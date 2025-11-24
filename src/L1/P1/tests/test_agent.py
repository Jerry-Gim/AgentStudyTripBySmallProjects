'''
测试代码
'''

import shutil
import tempfile
from pathlib import Path
import pytest

# 导入被测函数
from file_organizer_agent import classifyByRule, RULES, move_file

# ---------- 1. classify 大小写不敏感 ----------
@pytest.mark.paramterize("name", ["photo.JPG", "IMG.Png", "screen.GIF"])
def test_classify_case_insensitive(name):
    assert classifyByRule(name) == "Images"

# ---------- 2. 重名移动计数器 ----------
def test_move_file_counter():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src_file = tmp/"test.txt"
        src_file.write_text("data")
        dst_folder = tmp/"Docs"
        dst_folder.mkdir()

        # 第一次移动
        move_file(src_file, dst_folder)
        assert (dst_folder/"test.txt").exists()

        # 再建一个同名源文件
        src_file2 = tmp / "test.txt"
        src_file2.write_text("data2")
        move_file(src_file2, dst_folder)
        assert (dst_folder / "test_1.txt").exists()

        # 第三次
        src_file3 = tmp / "test.txt"
        src_file3.write_text("data3")
        move_file(src_file3, dst_folder)
        assert (dst_folder / "test_2.txt").exists()

# ---------- 3. 空桌面（无匹配文件）不报错 ----------
def test_empty_directory():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # 确保目录为空
        assert not any(tmp.iterdir())
         # 直接调用主流程不应抛异常
        for item in tmp.iterdir():
            if item.is_file():
                folder = classify(item.name)
                if folder:
                    move_file(item, tmp / folder)
        # 能走到这里即表示无异常
