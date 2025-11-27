#!/usr/bin/env python3
"""
Voice Alarm Agent  (Stage-1 Project-3)
依赖: pyttsx3 + schedule
安装:
    pip install pyttsx3 schedule
"""
import argparse
import re
import sys
import time
from datetime import datetime, timedelta

import pyttsx3
import schedule

# ===== 1. 语音合成封装 =====
def init_tts() -> pyttsx3.Engine:
    engine = pyttsx3.init()
    engine.setProperty("rate", 180) # 语速
    return engine

def speak(text: str) -> None:
    engine = init_tts()
    engine.say(text)
    engine.runAndWait()

# ===== 2. 时间解析：把“1h 20min”→秒=====
TIME_RE = re.compile(r"(?P<sec>\d+s)?(?P<min>\d+min)?(?P<hour>\d+h)?", re.I)
def parse_human_time(s: str) -> int:
    s = s.replace(" ", "").lower()
    total = 0
    for match in TIME_RE.finditer(s):
        d = match.groupdict()
        if d["hour"]:
            total += int(d["hour"][:-1]*3600) # 到最后一位（不包括），排除掉捕获关键字'h'
        if d["min"]:
            total += int(d["min"][:-3]) * 60  # 到倒数第三位（不包括），排除掉捕获关键字'min'
        if d["sec"]:
            total += int(d["sec"][:-1]) # 到最后一位（不包括），排除掉捕获关键字's'
    if total == 0:
        raise ValueError("无法解析时间，例如：30s 5min 2h30min")
    return total

# ===== 3. 倒计时逻辑 =====
def schedule_alarm(seconds: int, msg: str) -> None:
    def job():
        print("\n🔊 ", msg)
        #speak(msg)      # 请到有扬声设备的环境尝试，否则可以注释
    
    # schedule库只支持“时刻”触发，因此计算目标时刻
    trigger_at = datetime.now() + timedelta(seconds=seconds)
    # 定时调度job任务，day的输入格式为HH:MM:SS，所以把时间strftime成%H:%M:%S
    # hour类schedule为MM:SS, minute为:SS
    schedule.every().day.at(trigger_at.strftime("%H:%M:%S")).do(job)

    # 非阻塞轮询
    print(f"[Agent] 闹钟已设定 -> {seconds//60:02d}: {seconds%60:02d} 后提醒")
    try:
        while datetime.now() < trigger_at:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Agent] 用户输入中断，闹钟取消")
        sys.exit(1)

# ===== 4. CLI =====
def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="语音闹钟小助手")
    p.add_argument("time", default="30s" ,help="倒计时长，例如30s 5min 1h 2h30m")
    p.add_argument("--msg", default="时间到啦！", help="自定义提醒文本")
    return p

def main(argv = None):
    args = make_parser().parse_args(argv)
    try:
        seconds = parse_human_time(args.time)
    except ValueError as e:
        print(f"[agent] Value Error: {e}")
        sys.exit(2)
    schedule_alarm(seconds, args.msg)

if __name__ == "_main":
    main()