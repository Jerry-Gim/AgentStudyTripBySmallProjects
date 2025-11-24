#!/user/bin/env python3

"""
桌面文件分类机器人  (Stage-1 Project-1)
拓展功能：用来打包成一个exe文件
用法示例:
    方案 A：拖放文件夹 → 自动整理
    按前面步骤生成 file_organizer_agent.exe（单文件控制台版）。
    把任意文件夹 拖到 exe 图标上 再松开。
    Windows 会把被拖目录的完整路径当作 sys.argv[1]，效果等价于
    file_organizer_agent.exe "D:\用户\Downloads"
    代码里 argparse 的 --path 默认 positional 就能吃到，无需改动。
    想默认“预览”再让用户确认，可在 bat 里加 --dry-run，见下。

    方案 B：同目录放一个“预览并整理.bat”
    把下面两行保存成 整理Downloads.bat（放 exe 同级）：
    bat
    复制
    @echo off
    echo ===== 预览模式 =====
    file_organizer_agent.exe --path "%USERPROFILE%\Downloads" --dry-run
    echo.
    echo 按任意键真正整理...
    pause >nul
    file_organizer_agent.exe --path "%USERPROFILE%\Downloads"
    pause
    用户双击 bat 即可：
    先看到预览 → 敲任意键 → 真正移动 → 窗口保留，方便检查。

    方案 C：快捷方式里写参数
    在 file_organizer_agent.exe 上右键 → 创建快捷方式。
    右键快捷方式 → 属性 → 目标，改成：
    "D:\工具\file_organizer_agent.exe" --path "D:\我的文档\桌面" --dry-run
    以后双击这个快捷方式就是“预览桌面”。

    例如：
    D:\我的工具\
        ├─ file_organizer_agent.exe
        └─ file_rules.yml          ← 放这里即可
"""

import os
import shutil
from pathlib import Path
from typing import Optional
import yaml
import argparse
import sys

# 不论打包还是源码，都指向“exe 或脚本”所在目录
BASE = Path(sys.executable).parent

RULES_FILE = BASE/"RULES.yml"

# ---- 1. 感知：从 YAML 加载规则 ----
def load_rules() -> dict[str, list[str]]:
    """返回{'Images':['.jpg', ...], ...}"""
    if not RULES_FILE.exists():
        print(f"[Agent] 找不到规则文件：{RULES_FILE.resolve()}")
        exit(1)
    with RULES_FILE.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    # 统一转小写，去掉空分类
    return {k : [ext.lower() for ext in v] for k, v in raw.items()}

RULES = load_rules()

def classifyByRule(fileName: str, moveOthers: bool=False) -> Optional[str]:
    """根据后缀返回目标文件夹名，不匹配返回None"""
    """支持 .tar.gz 等多级后缀"""
    path = Path(fileName)
    suffix = path.suffix.lower()
    suffix_chain = ''.join(path.suffixes[-2:]).lower()
    for folder, ext_list in RULES.items():
        for ext in ext_list:
            if suffix == ext or suffix_chain == ext:
                return folder
            else:
                if moveOthers:
                    return "Others"
    return None

# ---- 2. 决策+行动：移动文件或者计划预览 ----
def action(src: Path, dst_folder:Path, dry_run: bool = False) -> None:
    dst_folder.mkdir(exist_ok=True)
    dst = dst_folder/src.name
    # 重名处理
    counter = 1
    stem, suffix = src.stem, src.suffix
    while dst.exists():
        dst = dst_folder/f"{stem}_{counter}{suffix}"
        counter+=1
    # 捕获移动失败异常原因

    if dry_run:
        print(f"[预览] {src} -> {dst}")
        return

    try:
        shutil.move(str(src), str(dst))
        print(f"[Agent] 已移动: {src.name} → {dst_folder.name}/")
    except Exception as e:
        print(f"[Agent] 移动失败: {src.name} 原因: {e}")

# ---- 3. 主循环 ----
def main():
    parser = argparse.ArgumentParser(description="文件自动分类小助手")
    parser.add_argument(
        "--path",
        type=str,
        default="~/Desktop",
        help="要整理的目录，默认 ~/Desktop",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="开启后只打印预览，不真正移动文件",
    )
    parser.add_argument(
        "--move-others",
        action="store_true",
        help="开启后其他未被RULES.yml分类的文件类型会被放到Others"
    )
    args = parser.parse_args()
    target_dir = Path(args.path).expanduser().resolve()
    if not target_dir.is_dir():
        print(f"未找到目标目录 {target_dir}，程序退出")
        exit(1)
    
    print(f"[File Organiser Agent] {'[预览模式]' if args.dry_run else ''}开始扫描：{target_dir}")
    for item in target_dir.iterdir():
        if item.is_file():
            folder = classifyByRule(item.name, args.move_others)
            if folder:
                action(item, target_dir/folder, dry_run=args.dry_run)
    print("[Agent] 本轮整理完毕！")

if __name__ == "__main__":
    main()