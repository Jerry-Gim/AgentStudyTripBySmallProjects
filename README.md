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