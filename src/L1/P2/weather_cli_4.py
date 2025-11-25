#!/usr/bin/env python3
"""
Weather Query Agent 拓展4
要求实现效果： 异常细分：
    - 城市名拼错 → 返回 404，提示“是否想输入 Beijing？”
    - API 配额超限 → 返回 401，提示“请检查 OWM_KEY”
    - 大小写不影响
文件包括：error_helper.py  统一翻译 OpenWeather 常见返回码，并做「城市名拼写建议」
比较统一用.lower()
如果 404，把服务器返回的「相近城市」或用本地常用城市列表模糊匹配提示给用户。
"""
import argparse
import os
import sys
from datetime import datetime

from config import config
from cache import get as cache_get, set as cache_set  
from forecast import fetch_forecast, format_forecast  
from ui import print_current, print_table  

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

def parse_weather(data: dict, unit_label: str) -> None:
    '''解析逻辑不变，但是打印之交给ui而不返回自己打印'''
    city = data["name"]
    weather = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    temp_max = data["main"]["temp_max"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    feel = '炎热' if temp > 30 else '舒适' if temp > 15 else '寒冷'
    print_current(city, weather, temp, temp_max, humidity, wind, unit_label, feel)

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

    if args.forecast:
        slots = fetch_forecast(city, args.unit)
        unit_label = "m/s" if args.unit == "metrics" else "mph"
        print(f"{city.lower()}:")
        print(format_forecast(slots, unit_label, True))
    else:
        data = fetch_weather(city, args.unit)
        if args.format == "json":   
            print(data)
        else:
            unit_label = "m/s" if args.unit == "metrics" else "mph"
            print(parse_weather(data, unit_label))


if __name__ == "__main__":
    main()



