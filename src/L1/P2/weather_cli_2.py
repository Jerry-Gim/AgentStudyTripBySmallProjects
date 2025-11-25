#!/usr/bin/env python3
"""
Weather Query Agent 拓展2
要求实现效果： 支持“未来 3 小时预报”：切换端点 /forecast，练习解析嵌套列表 JSON。
文件包括：forecast.py

缓存文件位置 "~/.weather_cache.json"
示例：
    {
        "fc|shanghai|metric": {
            "ts": 1700001234,
            "data": { ... }
        }
    }
"""
import argparse
import os
import sys
from datetime import datetime

from config import config
from cache import get as cache_get, set as cache_set  
from forecast import fetch_forecast, format_forecast    # 1. 导入预测获取和解析模块

import requests

API_KEY = config["API_KEY"]
BASE_URL = config["BASE_URL"]
LANG = config["LANG"]
CACHE_TTL = config["CACHE_TTL"]

def fetch_weather(city: str, units: str = "metrics") -> dict:
    hit = cache_get(city, units, CACHE_TTL)
    if hit is not None:
        print(f'[Agent] 命中本地缓存（10分钟以内')
        return hit
    
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units,
        "lang": "zh_cn" 
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()      
        data = resp.json()
        cache_set(city, units, data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"[Agent] 网络错误：{e}")
        sys.exit(2)

def parse_weather(data: dict, unit_label: str) -> str:
    city = data["name"]
    weather = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    temp_max = data["main"]["temp_max"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]

    return (f"{city} 今天 {weather} "
            f"{temp}度，最高{temp_max}度 "
            f"湿度{humidity}%，风速{wind} {unit_label} "
            f"体感{'炎热' if temp>30 else '舒适' if temp>15 else '寒冷'}")

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="weather_cli",
        description="实时天气查询小助手"
    )
    p.add_argument("-c", "--city", default="auto",
                   help="查询城市名，如Beijing；默认auto为根据IP自动定位")
    p.add_argument("-f", "--format", choices=["text", "json"], default="text",
                   help="输出格式，默认text")
    p.add_argument("--unit", choices=["metric", "imperial"], default=config["DEFAULT_UNITS"],
                   help="单位 metric=摄氏度/imperial=华氏度")
    
    return p

def main(argv = None):
    parser = make_parser()
    # 2. 新增互斥组：默认current，可加--forecast
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--forecast", action="store_true", help="输出预测模式，预测未来3小时三次")
    args = parser.parse_args(argv)

    if args.city == "auto":
        try:
            ip_info = requests.get("http://ip-api.com/json/?fields=city",
                                   timeout=5).json()
            city = ip_info["city"]
        except Exception:
            city = config["DEFAULT_CITY"]   
    else:
        city = args.city

    # 3. 分支预测模式
    if args.forecast:
        slots = fetch_forecast(city, args.unit)
        unit_label = "m/s" if args.unit == "metrics" else "mph"
        print(format_forecast(slots, unit_label))
    else:
        data = fetch_weather(city, args.unit)
        if args.format == "json":   
            print(data)
        else:
            unit_label = "m/s" if args.unit == "metrics" else "mph"
            print(parse_weather(data, unit_label))


if __name__ == "__main__":
    main()



