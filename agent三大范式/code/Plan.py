from LLM_Client import LLMs
import ast

PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

class Planner:
    def __init__(self, llm_client : LLMs):
        self.llm_client = llm_client
    
    def plan(self, question : str)->list[str]:
        prompt = PLANNER_PROMPT_TEMPLATE.format(question = question)

        messages = [{"role" : "user", "content" : prompt}]

        print("----------正在生成计划----------")

        response_text = self.llm_client.think(messages=messages) or ""


        print("计划已生成：\n{response_text}")

        try:
            plan_str = response_text.split("```python")[1].split("```")[0].strip()

            plan = ast.literal_eval(plan_str)

            return plan if isinstance(plan, list) else []
        except(ValueError, SyntaxError, IndexError) as e:
            print(f"解析计划时出错：{e}")
            print(f"原始响应：{response_text}")
            return []
        except Exception as e:
            print("解析计划时发生未知错误：{e}")
            return []