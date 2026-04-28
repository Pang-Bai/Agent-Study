from LLM_Client import LLMs
from Plan import Planner
from Executor import Executor

class Plan_and_Solve:
    def __init__(self, llm_client : LLMs):
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)
    
    def run(self, question : str):
        print("\n----------开始处理问题----------\n问题：{question}")

        plan = self.planner.plan(question)

        if not plan:
            print("\n----------任务终止----------\n无法生成有效的行动计划")
            return
        
        final_answer = self.executor.execute(question, plan)
        print(f"----------任务完成----------\n最终结果：{final_answer}")

if __name__ == "__main__":
    llm_client = LLMs()
    plan_and_solve = Plan_and_Solve(llm_client)
    question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
    plan_and_solve.run(question)