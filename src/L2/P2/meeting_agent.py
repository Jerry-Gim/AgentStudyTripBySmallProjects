#!/usr/bin/env python3
"""
Meeting Memory Agent  (Stage-2 Project-2)
功能: 录音→转写→切片→向量化→摘要→可追问
依赖: whisper / openai / chromadb / langchain
"""

import os
import sys
import whisper
import openai
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI

AUDIO_FILE = "meeting.wav"      # 1. 支持 wav/mp3/m4a
MODEL_SIZE = "base"         # whisper模型尺寸
API_KEY = os.getenv("ALI_API_KEY")

# 1. 语音转文本
def transcribe(path: str) -> str:
    model = whisper.load_model(MODEL_SIZE)
    result = model.transcribe(path, language = "zh", word_timestamps=False)
    print(f"[Agent] 转写成功，时长 {result["segments"][-1]['end']:.0f}s")
    return result["text"]

# 2. 文本->切片-向量