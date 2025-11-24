#!/user/bin/env python3

"""
桌面文件分类机器人  (Stage-1 Project-1)
运行方式:
    python file_organizer_agent.py
效果:
    把 ~/Desktop 里的
      图片 →  ~/Desktop/Images/
      文档 →  ~/Desktop/Documents/
      压缩包 → ~/Desktop/Archives/
    已存在文件自动跳过，重名文件自动加序号
"""

import os
import shutil
from pathlib import Path
from typing import Optional

# ---- 1. 感知：定义“要管哪些文件” ----
RULES = {
    "Images":  [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Documents": [".pdf", ".docx", ".txt", ".pptx"],
    "Archievs": [".zip", ".rar", ".7z", ".tar.gz"]
}

def classifyByRule(fileName: str) -> Optional[str]:
    """根据后缀返回目标文件夹名，不匹配返回None"""
    """支持 .tar.gz 等多级后缀"""
    path = Path(fileName)
    suffix = path.suffix.lower()
    suffix_chain = ''.join(path.suffixes[-2:]).lower()
    for folder, ext_list in RULES.items():
        for ext in ext_list:
            if suffix == ext or suffix_chain == ext:
                return folder
    return None

# ---- 2. 决策+行动：移动文件 ----
def move_file(src: Path, dst_folder:Path)->None:
    dst_folder.mkdir(exist_ok=True)
    dst = dst_folder/src.name
    # 重名处理
    counter = 1
    stem, suffix = src.stem, src.suffix
    while dst.exists():
        dst = dst_folder/f"{stem}_{counter}{suffix}"
        counter+=1
    # 捕获移动失败异常原因
    try:
        shutil.move(str(src), str(dst))
        print(f"[Agent] 已移动: {src.name} → {dst_folder.name}/")
    except Exception as e:
        print(f"[Agent] 移动失败: {src.name} 原因: {e}")

# ---- 3. 主循环 ----
def main():
    desktop = Path.home()/"Desktop"
    if not desktop.is_dir():
        print(f"未找到桌面目录，程序退出")
        return
    print("File Organiser Agent 已启动，监听桌面.......")
    for item in desktop.iterdir():
        if item.is_file():
            folder = classifyByRule(item.name)
            if folder:
                move_file(item, desktop/folder)
    print("本轮整理完毕！")

if __name__ == "__main__":
    main()