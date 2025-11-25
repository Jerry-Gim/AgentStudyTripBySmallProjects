#!/usr/bin/env python3
"""
Weather Query Agent  (Stage-1 Project-2)
依赖: 仅 requests  (pip install requests 或者 conda install requests)
接口: OpenWeatherMap 免费层  https://openweathermap.org/current
      无需登录即可申请 APP_KEY（每分钟 60 次够用）
"""

import argparse
import os
import sys
from datetime import datetime

import requests

API_KEY = os.getenv("OWM_KEY") or "9e0385deee879b822b37bd37eb01c017"    # 1： 硬编码key可作为环境变量隐藏敏感信息
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# 2：封装“感知”部分：真正发HTTP拿原始JSON
def fetch_weather(city: str, units: str = "metrics") -> dict:
    # 网络请求参数，参考OpenWeatherMap的官网
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units,
        "lang": "zh_cn" 
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()         # 3：HTTP异常自动抛
        return resp.json()
    except requests.exceptions.RequestException as e:
        # 4: 网络层异常提示
        print(f"[Agent] 网络错误：{e}")
        sys.exit(2)

# 5. 封装“决策+行动”：把JSON翻译成自然语言
def parse_weather(data: dict, unit_label: str) -> str:
    # OWM的响应体JSON的解析，格式参考OWM官网
    city = data["name"]
    weather = data["weather"][0]["description"]     # 多云/晴
    temp = data["main"]["temp"]
    temp_max = data["main"]["temp_max"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]

    return (f"{city} 今天 {weather} "
            f"{temp}度，最高{temp_max}度 "
            f"湿度{humidity}%，风速{wind} {unit_label} "
            f"体感{'炎热' if temp>30 else '舒适' if temp>15 else '寒冷'}")

# CLI入口：argparse解析启动参数
def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="weather_cli",
        description="实时天气查询小助手"
    )
    p.add_argument("-c", "--city", default="auto",
                   help="查询城市名，如Beijing；默认auto为根据IP自动定位")
    p.add_argument("-f", "--format", choices=["text", "json"], default="text",
                   help="输出格式，默认text")
    p.add_argument("--unit", choices=["metric", "imperial"], default="metric",
                   help="单位 metric=摄氏度/imperial=华氏度")
    
    return p

def main(argv = None):
    parser = make_parser()
    args = parser.parse_args(argv)

    # 自动定位: 调用IP-API免费接口
    if args.city == "auto":
        try:
            ip_info = requests.get("http://ip-api.com/json/?fields=city",
                                   timeout=5).json()
            city = ip_info["city"]
        except Exception:
            city = "Beijing"    # 无法检测的预设情况
    else:
        city = args.city
    
    data = fetch_weather(city, args.unit)
    if args.format == "json":   # 调试用
        print(data)
    else:
        unit_label = "m/s" if args.unit == "metrics" else "mph"
        print(parse_weather(data, unit_label))


if __name__ == "__main__":
    main()



