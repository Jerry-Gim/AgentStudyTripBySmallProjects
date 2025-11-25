'''
fetch & parse / forecast 端点
返回 List[dict] 供主脚本格式化
'''

import requests
from config import config
from cache import get as cache_get, set as cache_set
from ui import print_table  # 接入ui扩展

URL = config["FORECAST_URL"]
CNT = config["FORECAST_CNT"]
TTL = config["CACHE_TTL"]

def fetch_forecast(city: str, units: str = "metric") -> list[dict]:
    hit = cache_get(city, units, TTL, True)
    if hit is not None:
        hit = hit["list"]
        print("[Agent] 命中预报缓存")
        return hit
    
    params = {
        "q": city,
        "appid": config["API_KEY"],
        "units": units,
        "lang": config["LANG"],
        "cnt": CNT * 2          # API 3h 步长，取 3 条即 9h 内
    }

    try:
        resp = requests.get(URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # 要前CNT条
        slots = data["list"][:CNT]
        cache_set(city, units, data, True)
        return slots
    except requests.exceptions.RequestException as e:
        print(f"[Agent] 预报接口错误: {e}")
        return []
    
def format_forecast(slots: list[dict], units_label: str, ui: bool = False) -> str:
    """把list[dict]拼成一行一行自然语言, 如果有支持rich且开启，则使用ui打印"""
    # 解析结构参考https://openweathermap.org/api/hourly-forecast#geo5
    if not ui:
        if not slots:
            return "（暂无预报数据）"
        lines = []
        for s in slots:
            ts = s["dt"]
            time_str = __import__("datetime").datetime.fromtimestamp(ts).strftime("%m%d-%H:%M")
            temp = s["main"]["temp"]
            desc = s["weather"][0]["description"]
            lines.append(f"{time_str}  {temp}℃ {desc}")
        return "\n".join(lines)
    else:
        """改成 rich 表格，不再拼接字符串"""
        if not slots:
            return "（暂无预报数据）"
        rows = []
        for s in slots:
            ts = s["dt"]
            time_str = __import__("datetime").datetime.fromtimestamp(ts).strftime("%m%d %H:%M")
            temp = s["main"]["temp"]
            desc = s["weather"][0]["description"]
            rows.append((time_str, f"{temp:.0f}", desc))
        print_table("未来天气预报", rows)
        return ""