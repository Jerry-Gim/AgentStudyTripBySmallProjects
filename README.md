# AgentStudyTripBySmallProjects

# 环境导出
## Conda部分
conda activate your_env
conda env export --no-builds > env-conda.yml
## pip部分
pip freeze > env-pip.txt

# 环境恢复
## conda部分（新建空环境）
conda env create -f env-conda.yml -n restored_env
conda activate restored_env
## pip部分（新建空环境）
conda activate restored_env
## conda部分（后续更新）
conda env update -f environment.yml --prune
## pip部分（后续更新）
python -m pip install -r requirements-pip.txt


# 知识重点
1. [Python Request库](/AgentStudyTripBySmallProjects/src/L1/P2/README.md#1-python-requests库)
2. [Python 手动异常处理](/AgentStudyTripBySmallProjects/src/L1/P3/README.md#python知识点手动异常处理)
3. [ReAct框架和调度LLM的方法以及LangChain](/AgentStudyTripBySmallProjects/src/L2/P1/README.md#react框架基础agent运行循环的升级)
4. [向量知识库与Embedding](/AgentStudyTripBySmallProjects/src/L2/P2/README.md#向量数据库vector-database用于存储索引和检索高维向量这些向量通常来自文本图像音频等非结构化数据的-embedding嵌入)