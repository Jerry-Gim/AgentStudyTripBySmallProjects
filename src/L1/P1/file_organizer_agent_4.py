#!/user/bin/env python3

"""
桌面文件分类机器人  (Stage-1 Project-1)
拓展功能：利用schedule变成持续运行的agent，每个五分钟运行一次检查，每十分钟运行一次整理
用法示例:
    # 每 10 分钟真正整理桌面
    python file_organizer_agent.py

    # 每 5 分钟仅预览 Downloads
    python file_organizer_agent.py --path ~/Downloads --interval 5 --dry-run

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
import schedule, time

# 不论打包还是源码，都指向“exe 或脚本”所在目录
# 如果不打包应该是__file__
BASE = Path(__file__).parent

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
def job(target_dir: Path, dry_run:bool):
    """一次完整扫描-整理任务"""
    print(f"[Agent] {time.strftime('%Y-%m-%d %H:%M:%S')} 定时扫描 → {target_dir}")
    for item in target_dir.iterdir():
        if item.is_file():
            folder = classifyByRule(item.name)
            if folder:
                action(item, target_dir / folder, dry_run=dry_run)
    print("[Agent] 本轮整理完毕！")

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
        "--interval",
        type=int,
        default=10,
        help="定时扫描间隔（分钟），默认10"
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
    # 开始立即执行一次
    job(target_dir, args.dry_run)
    # 之后进入定时循环
    schedule.every(args.interval).minutes.do(job, target_dir, args.dry_run)
    print(f"[Agent] 已启动定时任务，每{args.interval}分钟扫描一次，Ctrl+C退出")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Agent] 用户中断退出")
    

if __name__ == "__main__":
    main()