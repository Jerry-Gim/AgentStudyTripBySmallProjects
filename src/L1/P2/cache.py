'''
本地文件cache缓存(weather_cli_1.py)
目标：把输出缓存 10 分钟：用 ~/.weather_cache.json + 文件时间戳，练习“本地缓存”降低 API 调用。
key: "city|units"
'''

import json
import os
import time
from typing import Dict, Optional

CACHE_FILE = os.path.expanduser("~/.weather_cache.json")

def _now() -> int:
    return int(time.time())

def _load() ->Dict[str, dict]:
    '''返回整个缓存dict，文件不存在则返回空dict'''
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("cache file error")
        return {}
    
def _save(db: Dict[str, dict]) -> None:
    '''原子写入：先写临时文件再rename'''
    tmp = CACHE_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CACHE_FILE)
    except OSError:
        pass

def get(city: str, units: str, ttl: int, fc: bool = False) -> Optional[dict]:
    '''缓存命中且未过期返回data，否则None'''
    db = _load()
    key = f"{city.lower()}|{units}" if not fc else f"fc|{city.lower()}|{units}"
    item = db.get(key)
    if not item:
        return None
    if _now() - item["ts"] > ttl:
        return None
    return item["data"]

def set(city: str, units: str, data: dict, fc: bool = False) -> None:
    '''写入/覆盖缓存'''
    db = _load()
    key = f"{city.lower()}|{units}" if not fc else f"fc|{city.lower()}|{units}"
    db[key] = {
        "ts": _now(),
        "data": data
    }
    _save(db)