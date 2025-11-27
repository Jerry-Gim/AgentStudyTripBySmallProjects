# 阶段1 项目3 （未完工，代码示例暂未跑通，需要后续重新思考。当前代码可以跳过，查看知识点）
## 语言闹钟提醒小助手
    目标： 在终端使用 `python voice_alarm_agent.py 30min` 就能触发后台倒计时，30分钟后自动语音播报“时间到，该休息啦”

## 涉及知识
1. 离线语音合成：pyttsx3库
2. 定时调度，非阻塞轮询：schedule库（在L1P1的桌面整理小助手中的拓展有涉及）
3. 并发
4. 正则解析自然语言时间
5. 命令行参数与退出

## 最终效果

    # 立即试用
    $ python voice_alarm_agent.py 3min
    [Agent] 闹钟已设定 → 03:00 后提醒
    ...3 分钟后...
    🔊 时间到，该休息啦！

    # 支持自然语言
    $ python voice_alarm_agent.py "1 hour 20 min"
    [Agent] 闹钟已设定 → 80:00 后提醒

    # 查看帮助
    $ python voice_alarm_agent.py --help
    usage: voice_alarm_agent.py [-h] [--msg MSG] time

    语音闹钟 Agent（支持 10s/3min/1h20m 等写法）

    positional arguments:
    time        倒计时，例：30s  5min  1h  2h30m
    optional arguments:
    -h, --help  show this help message and exit
    --msg MSG   自定义提醒文本

## 额外环境依赖
- pyttsx3, schedule

# 知识点解析：
1. pyttsx3.init()
    - 离线 TTS 引擎，跨平台（Win/Mac/Linux），不依赖网络，适合入门。
2. engine.runAndWait()
    - 阻塞直到读完，避免程序提前退出导致没声音。
3. 正则 (?P<hour>\d+h)?
    - 命名捕获组让解析逻辑一目了然，练习“从自然语言抽取结构化数据”。
    - 例如，(?P<hour>\d+h)：匹配一个或多个数字后跟 h，表示小时。
    - 每个组（括号内）后面的?表示这些部分是可选的（0次或者一次）
    - 标志 re.I代表囫囵大小写，因此对s/min/h的大小写不敏感
    - 例子voice_alarm_agent.py中使用了(?P<sec\>\d+s)?(?P<min\>\d+min)?(?P<hour\>\d+h)?作为正则：
      - 它强制顺序：顺序必须是秒分时，可以少但是不能颠倒顺序否则不能正确匹配
    - Match.groupdict()会获得每个捕获组字符串对应捕获的字符串，例如3h捕获的<hour\>为 {hour: 3}
4. schedule.every().day.at(...)
    - schedule 库仅支持“时刻”触发，因此先把“倒计时”换算成“绝对时刻”，再每秒轮询 run_pending()——经典“非阻塞定时器”模式。
5. KeyboardInterrupt
    - 捕获 Ctrl-C 实现“用户随时取消”，演示优雅退出。
6. argparse 位置参数
    - 让用户直接写 python voice_alarm_agent.py 30s，无需 -c 选项，更符合直觉。
  
# Python知识点：手动异常处理
- Python 的异常机制围绕“抛出 → 捕获 → 处理”展开，核心关键字只有 5 组：
    - try、except、else、finally、raise。
- 除此之外，还有几个配套但不是关键字的辅助工具：assert 语句、自定义异常类、异常链（from）、with…raise…from 等
### 5个核心关键字：
1. **try**: 划定“可能出错的代码块”。
2. **except <异常类> [as 变量]**: 捕获并处理；可多重、可元组、可省略异常类（捕获 BaseException）。
3. **else**: 当 try 块没有发生任何异常时执行；常用于“成功后的后续动作”，避免把大量代码塞进 try。
4. **finally**: 无论是否异常都会执行；常用于释放锁、关闭文件、回滚事务等“清理”逻辑。
即使有 return / break / 异常，finally 也会在跳出前运行。
5. **raise <异常实例> [from <原异常>]**: 手动抛出异常；from 用于链式异常（PEP 3134）。
6. ****特殊：with***：*上下文管理器里的 exit 收到异常时会拿到 (exc_type, exc_val, exc_tb)
返回 True 代表“我把异常吞掉了”，with 外不会继续抛。*


# 额外扩展：
1. 循环闹钟：支持“每 45 分钟提醒一次坐直”，用 schedule.every(45).minutes.do(job)。
2. 多语言播报：检测系统语言，中文用 pyttsx3，英文换 gTTS 在线接口，练习“条件驱动工具选择”。
3. 语音确认：倒计时开始时先用语音复述“将在 30 分钟后提醒你”，练习“语音输入-确认”闭环。
4. GUI 版本：用 tkinter 做一个输入框+按钮，把核心逻辑封装成 start_alarm(seconds, msg)，体会 “逻辑与界面分离”。
5. 日志持久化：把每次闹钟记录写进 ~/.alarm_log.csv（时间、文案），练习“最小化数据沉淀”。