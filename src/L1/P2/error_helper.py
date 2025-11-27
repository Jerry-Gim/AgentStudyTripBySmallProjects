"""
OpenWeather 返回码 -> 人类话 + 纠错建议
"""
import requests
from typing import Optional
from difflib import get_close_matches

# 常用城市白名单
TOP_CITIES = ["Beijing", "Shanghai", "Guangzhou", "Shenzhen",
              "Hangzhou", "Chengdu", "Wuhan", "Xi'an", "Nanjing", "Tianjin"]

def suggest_city(wrong: str) -> Optional[str]:
    """简单模糊匹配：首字母相同或编辑距离<=2 即认为可能"""
    wrong = wrong.lower()
    # 模糊匹配
    match = get_close_matches(wrong, [c.lower() for c in TOP_CITIES], n=1, cutoff=0.6)
    if match:
        # 把首字母大写拼回去
        return next(c for c in TOP_CITIES if c.lower() == match[0])
    return None
    
def explain_exception(status_code: int, text: str, city: str) -> str:
    """把HTTP状态码+返回体解释为用户看得懂的话"""
    if status_code == 404:
        maybe = suggest_city(city)
        tip = f'是否想输入 "{maybe}" ？' if maybe else "请检查城市名拼写。"
        return f"ERROR 404: 城市名拼错或不在支持列表（{tip}）"
    elif status_code == 401:
        return "ERROR 401: API配额超限或者KEY无效，请检查settings.json里的OWM_KEY是否正确。"
    elif status_code == 429:
        return "ERROR 429: 调用频率超限，请稍后再试。"
    else:
        return f"服务异常（HTTPS{status_code}）： {text[:100]}"