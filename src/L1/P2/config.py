"""
读取外置 settings.json；若缺失/空 KEY 则提示用户。
"""

import json
import os
import sys
from pathlib import Path

def _base_dir() -> Path:
    """
    用于区分EXE运行路径搜索和Script调试搜索
    """
    # PyInstaller 运行时
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    # 正常python开发运行script
    return Path(__file__).resolve().parent

_CONFIG_FILE = _base_dir() / "settings.json"

def load_confg() -> dict:
    if not _CONFIG_FILE.exists():
        _write_default()
        print(f"[Config] 配置文件以生成： {_CONFIG_FILE}")
        print("[Config] 填入有效OpenWeatherMap Key在settings.json在运行")
        # sys.exit(1)

    try:
        with _CONFIG_FILE.open(encoding="utf-8") as f:
            cfg = json.load(f)
    except (json.JSONDecodeError, OSError):
        sys.exit("[Config] setting.json缺失或者格式错误，请检查！")
    
    if not cfg.get("API_KEY") or cfg["API_KEY"] == "YOUR_OPENWEATHER_API_KEY":
        sys.exit("[Config] API_KEY 未设置，请编辑 settings.json 后重试！")

    return cfg

def _write_default():
    default = {
        "API_KEY": "9e0385deee879b822b37bd37eb01c017",
        "BASE_URL": "https://api.openweathermap.org/data/2.5/weather",
        "CACHE_TTL": 600,
        "DEFAULT_CITY": "Beijing",
        "DEFAULT_UNITS": "metric",
        "LANG": "zh_cn"
    }
    with _CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(default, f, ensure_ascii=False, indent=2)

# 全局单例
config = load_confg()