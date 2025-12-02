#!/usr/bin/env python3
"""
Meeting Memory Agent  (Stage-2 Project-2)
功能: 录音→转写→切片→向量化→摘要→可追问
依赖: whisper / openai / chromadb / langchain
"""

import os
import sys

from langchain_openai import ChatOpenAI
import
import openai
from langchain.chains.conversational_retrieval import ConversationalRetrievalChain
from langchain.chains.retrieval_qa import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI

AUDIO_FILE = "meeting.wav"      # 1. 支持 wav/mp3/m4a
MODEL_SIZE = "base"         # whisper模型尺寸
API_KEY = os.getenv("ALI_API_KEY")

llm = ChatOpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("ALI_API_KEY"), 
    model="qwen-plus",
    temperature=0
)

# 1. 语音转文本
def transcribe(path: str) -> str:
    model = whisper.load_model(MODEL_SIZE)
    result = model.transcribe(path, language = "zh", word_timestamps=False)
    print(f"[Agent] 转写成功，时长 {result['segments'][-1]['end']:.0f}s")
    return result["text"]

# 2. 文本->切片->向量
def build_memory(text: str):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=50
    )
    docs = text_splitter.create_documents([text])   # 整段文本切片成tokens docs
    embeddings = OpenAIEmbeddings()     # 使用OpenAI训练好的embedding层模型
    vectordb = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")     # 使用docs调用embedding层模型获得向量，使用chroma_db方法生成向量数据库，永久储存在./chroma_db
    vectordb.persist()      # 向量数据库持久化
    return vectordb # 返回向量数据库

# 3. 生成3行摘要
def make_summary(vectordb) -> str:
    '''
    # 直接调用法
    qa = RetrievalQA.from_chat_tyoe(llm=llm, retriever=vectordb.as_retriever())
    summary = qa.run("用三句话总结这份会议纪要，每句包含关键结论或待办")
    '''

    # Runnable管道调用
    '''
    retriever.invoke()/.run()生成的是集合:
    [
        Document(
            page_content="深圳属于亚热带季风气候，夏季炎热多雨，冬季温暖少雨。",
            metadata={"source": "climate_info.txt", "page": 2}
        ),
        Document(
            page_content="全年平均气温在22℃左右，湿度较大。",
            metadata={"source": "climate_info.txt", "page": 3}
        )
    ]
    其中page_content：文档的正文内容（字符串）；metadata：字典，包含来源、页码、文件名、向量库中的 ID 等信息
    之后将这个文档传给LLM作为上下文
    '''
    retriever = vectordb.as_retriever()
    qa = retriever | llm        #  Runnable 管道：retriever 输出文档 → llm 生成答案
    summary = qa.invoke("用三句话总结这份会议纪要，每句包含关键结论或待办")
    return summary

# 4. 进入追问循环
def chat_mode(vectordb):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    crc = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectordb.as_retriever(),
        memory=memory
    )
    print("\n【4】进入追问模式（输入 q 退出）")
    while True:
        q = input("> ").strip()
        if q.lower() == q:
            break
        ans = crc({"question": q})["answer"]
        print("Answer: ", ans)

# 5. 主函数
def main():
    if not os.path.exists(AUDIO_FILE):
        print(f"请把录音文件命名为 {AUDIO_FILE} 后重试")
        sys.exit(1)
    print("【1】上传录音:", AUDIO_FILE)
    print("【2】正在转写...")
    text = transcribe(AUDIO_FILE)
    print("【3】生成摘要...")
    vectordb = build_memory(text)
    summary = make_summary(vectordb)
    print(summary)
    chat_mode(vectordb)

if __name__ == "__main__":
    main()