from LLM_Client import LLMs
from Action import ToolExecutor, search
import re

REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下：
{tools}

请严格按照以下格式进行回应：

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一：
- `{{tool_name}}[{{tool_input}}]`：调用一个可用工具。
- `Finish[最终答案]`：当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `Finish[最终答案]` 来输出最终答案。


现在，请开始解决以下问题：
Question: {question}
History: {history}
"""

class ReAct_Agent:
    #思考一下需要哪些东西，首先肯定是一个大模型接口，然后是工具
    def __init__(self, llm_client : LLMs, tool_executor: ToolExecutor, max_steps : int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []
    
    def run(self, question: str):
        self.history = []#记录历史记录
        cur_step = 0

        while cur_step < self.max_steps:
            cur_step += 1
            print(f"----------第{cur_step}步----------")

            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools = tools_desc,
                question = question,
                history = history_str
            )


            messages = [{"role" : "user", "content" : prompt}]
            response_text = self.llm_client.think(messages=messages)

            if not response_text:
                print("错误：大模型未能返回有效响应")
                break
            
            thougt, action = self._parse_output(response_text)#解析出思考与行动
            # print(action)
            if thougt:
                print(f"思考:{thougt}")
            
            if not action:
                print("警告：未能解析出有效的Action，流程终止")
                break

            if action.startswith("Finish"):
                final_answer = self._parse_action_input(action)
                print(f"最终结果:{final_answer}")
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:

                continue
            
            print(f"行动：{tool_name}[{tool_input}]")

            tool_function = self.tool_executor.getTool(tool_name)

            if not tool_function:
                observation = f"错误，未找到名未'{tool_name}'的工具。"
            else:
                observation = tool_function(tool_input)
            
            print(f"观察：{observation}")

            self.history.append(f"Action:{action}")
            self.history.append(f"Observation:{observation}")
        
        print("已达到最大步数，流程终止。")
        return None
    
    def _parse_output(self, text: str):
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)

        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None

        return thought, action
    
    def _parse_action(self, action_text: str):
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)

        return None, None
    
    def _parse_action_input(self, action_text: str):
        match = re.match(r"\w+\[(.*)\]", action_text, re.DOTALL)
        return match.group(1) if match else ""
    
if __name__ == "__main__":
    llm = LLMs()
    tool_executor = ToolExecutor()
    search_desc = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    tool_executor.registerTool("Search", search_desc, search)
    agent = ReAct_Agent(llm_client=llm, tool_executor=tool_executor)
    question = "上海最近的演唱会有哪些?"
    agent.run(question)
