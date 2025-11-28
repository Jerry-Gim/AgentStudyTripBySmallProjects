#!/usr/bin/env python3
"""
Level 2 Project 1: wiki agent
ReAct Wikipedia Agent  (Stage-2 Project-1)
拓展1和2：添加自封装工具duckduckgoserach来实现多工具路由与fallback——当维基无结果或页面缺失时，Agent 自动调用 DuckDuckGo 进行全网搜索
"""
import os
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import initialize_agent, AgentType
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from duck_tool import DuckDuckGoSearchTool  # 引入自建工具

wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="zh"))    # 拓展1：设置wiki语言 
duck = DuckDuckGoSearchTool()   # 申明并初始化自建工具的封装类
tools = [wiki, duck]    # 工具方法的集合

llm = ChatOpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.getenv("ALI_API_KEY"), 
        model="qwen-plus",
        temperature=0
)

prompt = hub.pull("hwchase17/react")   
prompt.template += "\n请用中文回答用户的问题。"  # 拓展1：模板拼接添加强制中文的提示模板
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=15  # 设置最大ReAct循环，防止无限循环卡死
)

def main():
    print("===  维基 + DuckDuckGo 双工具 ReAct === （输入q退出）")
    while True:
        query = input("\n问题> ").strip()
        if query.lower() == "q":
            break
        try :
            result = executor.invoke({"input": query}) 
            answer = result["output"]
            print(f"Answer: {answer}")
        except Exception as e:
            print(f"[Agent] 出错: {e} ({type(e).__name__} - {e.args})")

if __name__ == "__main__":
    main()