from LLM_Client import LLMs
EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决“当前步骤”，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对“当前步骤”的回答:
"""

class Executor:
    def __init__(self, llm_client : LLMs):
        self.llm_client = llm_client

    def execute(self, question : str, plan : list[str]) -> str:
        history = ""
        print("\n----------正在执行计划----------")

        for i , step in enumerate(plan):
            print(f"正在执行步骤{i+1}/{len(plan)}: {step}")
        
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question = question,
                plan = plan,
                history = history if history else "无",
                current_step = step
            )

            messages = [{"role" : "user", "content" : prompt}]

            response_text = self.llm_client.think(messages=messages) or ""

            history += f"步骤{i+1}: {step}\n结果：{response_text}\n\n"

            print(f"步骤{i+1}已完成，结果：{response_text}")

        final_answer = response_text
        return final_answer