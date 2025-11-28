# 阶段 2 · 项目 2
## 带记忆的会议记录助手
目标：上传一段 5 分钟会议录音 → 自动输出 3 行摘要 → 支持后续追问“谁负责预算？”→ 助手能准确回答，实现“语音转写 + 向量记忆 + 多轮追问”完整闭环。

# 涉及技术要点：
1. 录音文件：Whisper API 转写（speaker-diarization 可选）
2. 文字切片： OpenAI Embedding
3. Chroma向量库存储（=长期记忆）
4. 大模型生成摘要 & 回答追问： LangChain RetrievalQA + ConversationBufferMemory 


