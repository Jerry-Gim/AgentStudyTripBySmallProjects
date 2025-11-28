#!/usr/bin/env python3
"""
Level 2 Project 1: wiki agent
ReAct Wikipedia Agent  (Stage-2 Project-1)
LangChain + 维基百科工具，verbose 打印完整思维链
"""
import os
from langchain_openai import OpenAI # 专用于OpenAI
from langchain_openai import ChatOpenAI # 用于其他兼容OpenAI接口的api
from langchain import hub
from langchain.agents import initialize_agent, AgentType
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# 1. 组装工具：维基百科 API
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="en"))   
'''
# 2. 大模型“大脑”   OpenAI版本
llm = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    model="gpt-3.5-turbo-instruct"
)
'''

# 2. 大模型“大脑”   兼容OpenAI接口的其他大模型的api版本
llm = ChatOpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.getenv("ALI_API_KEY"),   # 百炼控制台申请
        model="qwen-plus",
        temperature=0
)

'''
# 2. 本地 Ollama
from langchain_community.llms import Ollama
llm = Ollama(model="qwen:7b", temperature=0)
'''


# 3. 拉去官方ReAct模板prompt，创建 ReAct Agent和Executor
prompt = hub.pull("hwchase17/react")    # 等价于之前的ZERO_SHOT_REACT_DESCRIPTION
agent = create_react_agent(
    llm=llm,
    tools=[wiki],
    prompt=prompt
)
executor = AgentExecutor(
    agent=agent,
    tools=[wiki],
    verbose=True,
    handle_parsing_errors=True
)

# 4. 交互 CLI
def main():
    print("=== ReAct维基回答 === （输入q退出）")
    while True:
        query = input("\n问题> ").strip()
        if query.lower() == "q":
            break
        try :
            result = executor.invoke({"input": query}) # 输入和返回都要求dict
            answer = result["output"]   # 获取dict里的output
            print(f"Answer: {answer}")
        except Exception as e:
            print(f"[Agent] 出错: {e} ({type(e).__name__} - {e.args})")

if __name__ == "__main__":
    main()