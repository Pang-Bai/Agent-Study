import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()#读取.env文件

class LLMs:
    def __init__(self, model : str = None, apiKey : str = None, url : str = None, timeout : int = None):
        #初始化，提供大模型的api_key, name, url
        if(model is None) : self.model = os.getenv("LLM_MODEL_ID")
        if(model is None) : apiKey = os.getenv("LLM_API_KEY")
        if(model is None) : url = os.getenv("LLM_BASE_URL")
        if(model is None) : timeout = int(os.getenv("LLM_TIMEOUT", 1200))

        if self.model == None or apiKey == None or url == None:
            raise ValueError("模型ID、API密钥和服务地址缺少, 可能没有在.env文件中定义, 或者.env文件路径问题")#强制中断
        
        self.client = OpenAI(api_key=apiKey, base_url=url, timeout=timeout) #模型需要支持openai调用,可以查阅模型的api文档，一般会提供可供openai使用的接口

    def think(self, messages : List[Dict[str, str]], temperature : float = 0) -> str:
        print(messages)
        print(f"正在调用{self.model}模型...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=65536,
                temperature=temperature,
                stream=True,
            )

            print("大模型响应成功")
            #流式输出
            response_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                response_content.append(content)
            print()  # 在流式输出结束后换行
            return "".join(response_content)
        
        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            return None

if __name__ == '__main__':
    try:
        llm_example = LLMs()
        exampleMessages = [
            {"role": "system", "content": "你是一个擅长写python代码的人"},
            {"role": "user", "content": "写一个快速排序算法"}
        ]

        print("---------------调用LLM ---------------")
        responseText = llm_example.think(exampleMessages)
        if responseText:
            print("\n\n---------------完整模型响应---------------")
            print(responseText)
    
    except ValueError as e:
        print(e)


