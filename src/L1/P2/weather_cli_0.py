#!/usr/bin/env python3
"""
Weather Query Agent 拓展0
要求实现效果： 把API_KEY配置放在setting.json之类的文件，分离配置和源代码
文件包括：settings.json, config.py
"""

import argparse
import os
import sys
from datetime import datetime

from config import config # 引入配置config全局单例

import requests

API_KEY = config["API_KEY"]    # 1： 不再硬编码而是读取config：settings.json
BASE_URL = config["BASE_URL"]
LANG = config["LANG"]

def fetch_weather(city: str, units: str = "metrics") -> dict:
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units,
        "lang": "zh_cn" 
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()         #
        return resp.json()
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
    
    data = fetch_weather(city, args.unit)
    if args.format == "json":   
        print(data)
    else:
        unit_label = "m/s" if args.unit == "metrics" else "mph"
        print(parse_weather(data, unit_label))


if __name__ == "__main__":
    main()



