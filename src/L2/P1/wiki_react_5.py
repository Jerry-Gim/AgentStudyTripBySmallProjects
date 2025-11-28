#!/usr/bin/env python3
"""
Level 2 Project 1: wiki agent
ReAct Wikipedia Agent  (Stage-2 Project-1)
拓展 3: 本地可视化verbose记录
解决方案：继承重写一个记录并保存本地的callbackHandler
"""
import os
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from duck_tool import DuckDuckGoSearchTool

# 工具
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="zh"))
duck = DuckDuckGoSearchTool()
tools = [wiki, duck]

# 记忆
memory = ConversationBufferMemory(
    memory_key="chat_history",  # 必须与模板一致
    return_messages=True,
    k=5     # 最大保存五轮记忆
)

# 初始化自定义handler
from markdown_callback_handler import MarkdownCallbackHandler
md_handler = MarkdownCallbackHandler()

# LLM
llm = ChatOpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("ALI_API_KEY"),
    model="qwen-plus",
    temperature=0
)

# 修改模板
base_prompt = hub.pull("hwchase17/react")
modified_template = f"""
你是一个有帮助的助手，请用中文回答用户的问题。

对话历史:
{{chat_history}}

{base_prompt.template}
请用中文回答用户的问题。
"""

prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad", "chat_history"],
    template=modified_template,
)

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt) 

# 创建 executor，传入自定义callback_handler
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,  # executor设置 memory
    verbose=False,  # 关闭verbose控制台输出
    callbacks=[md_handler],     # 添加callback handler
    handle_parsing_errors=True,
)

def main():
    print("=== 带记忆的维基 + DuckDuckGo ReAct Agent ===")
    while True:
        query = input("\n问题> ").strip()
        if query.lower() == "q":
            break
        try:
            result = executor.invoke({"input": query})
            print(f"Answer: {result['output']}")
        except Exception as e:
            print(f"[Agent] 出错: {e}")
        finally:
            md_handler.save_to_file()

if __name__ == "__main__":
    main()
