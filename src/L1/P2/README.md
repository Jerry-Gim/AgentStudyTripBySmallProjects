# 阶段 1 · 项目 2
## 「天气查询小助手 CLI」
目标：在终端输入城市名，立刻返回一段人类可读的实时天气文本

## 核心知识点
1. 加强对AI agent的核心概念（感知、决策、行动）的理解
2. HTTP请求接口
3. JSON解析方法
4. 命令行参数 (在上一单元的拓展练习中也有使用)
5. 异常处理

## 最终效果
    `
    $ python weather_cli.py Beijing
    北京  今天 晴  26℃↑33℃  湿度55%  风速3m/s  体感炎热，注意防晒。

    $ python weather_cli.py --help
    usage: weather_cli.py [-c CITY] [-f {json,text}] [--unit {metric,imperial}]

    可选参数：
    -c, --city          城市名(中英文均可，默认自动检测本机IP城市)
    -f, --format        输出格式  text|json  默认text
    --unit              单位制    metric|imperial  默认metric
    `

# 知识点解析
## 1. Python requests库：
    GET方法：requests.get(url, params=None, **kwargs)
        用于向服务器请求数据，不会修改服务器资源。传递的是URL查询字符串，请求在URL后面，收URL长度限制（2kb-8kb）。多次请求结果一致（幂等性）
        常用参数：
            · url：请求地址（必填）
            · params：查询参数（字典或字符串），会附加在 URL 后面
            · headers：请求头（字典）
            · timeout：超时时间（秒）
        实例：
            import requests
            response = requests.get(
                'https://httpbin.org/get',
                params={'key1': 'value1', 'key2': 'value2'},
                headers={'User-Agent': 'my-app'}
            )

            print(response.status_code)
            print(response.json())
    
    POST方法：
        用于向服务器提交数据，可能会修改服务器资源。传递的是请求体，参数在请求体（data或json）相对安全，无明确长度限制。多次请求结果可能不同
        常用参数：
            · url：请求地址（必填）
            · data：表单数据（字典、元组列表、字节等）
            · json：JSON 数据（字典），会自动序列化为 JSON 字符串，并设置 Content-Type: application/json
            · headers：请求头（字典）

        实例：
            import requests
            response = requests.post(
                'https://httpbin.org/post',
                json={'username': 'alice', 'password': '123456'},
                headers={'User-Agent': 'my-app'}
            )

            print(response.status_code)
            print(response.json())

    * 总是检查 response.status_code 和 response.raise_for_status() 来处理异常。
    
    返回为Response对象，类型为requests.models.Response，包含：
        | 属性/方法                      | 说明                                           |
        | ----------------------------- | ---------------------------------------------- |
        | `response.status_code`        | HTTP 状态码（如 200、404、500）                  |
        | `response.text`               | 响应体的字符串形式（自动解码）                    |
        | `response.content`            | 响应体的字节形式（原始二进制数据）                |
        | `response.json()`             | 将响应体解析为 JSON（返回字典或列表）             |
        | `response.headers`            | 响应头（字典-like 对象）                         |
        | `response.url`                | 最终请求的 URL（可能因重定向而改变）              |
        | `response.encoding`           | 响应的编码方式（如 utf-8）                       |
        | `response.cookies`            | 响应中的 cookie（RequestsCookieJar 对象）       |
        | `response.raise_for_status()` | 如果状态码是 4xx 或 5xx，会抛出 `HTTPError` 异常 |

    实例：
        import requests
        response = requests.get('https://httpbin.org/json')
        print(type(response))  # <class 'requests.models.Response'>
        print(response.status_code)  # 200
        print(response.headers['Content-Type'])  # application/json
        print(response.json())  # 解析为字典

# 代码解释
1. os.getenv("OWM_KEY")
    第一次接触“配置与代码分离”：把 export OWM_KEY=你的key 写入 ~/.bashrc，避免硬编码泄露。
2. requests.get(..., timeout=10)
    网络 I/O 必须加超时，防止终端卡死；raise_for_status() 一键把 4xx/5xx 转成 HTTPError，简化异常分支。
3. argparse
    自动生成 -h/--help
    choices= 限制枚举值，用户输错立即提示
    默认参数机制让脚本“零配置”也能跑。
4. sys.exit(2)
    遵循 UNIX 惯例：exit 0 成功，2 命令行参数错误，1 通用异常，方便后续 Shell 脚本调用。
5. IP 自动定位
    演示“链式 API”思想：先问 IP-API 拿城市 → 再调天气 API，练习二次 HTTP 调用。
6. 体感温度规则
    极简“业务规则”示例，告诉你不是一切都要大模型，普通 if-else 也能完成“决策”。

# 拓展练习
0. API_KEY放在另一个配置文件中
1. 把输出缓存 10 分钟：用 ~/.weather_cache.json + 文件时间戳，练习“本地缓存”降低 API 调用。
2. 支持“未来 3 小时预报”：切换端点 /forecast，练习解析嵌套列表 JSON。
3. 彩色输出：安装 rich，把温度用红/蓝高亮，练习 CLI 可视化。
4. 异常细分：
    - 城市名拼错 → 返回 404，提示“是否想输入 Beijing？”
    - API 配额超限 → 返回 401，提示“请检查 OWM_KEY”
5. 打包为独立可执行文件：
   `
    pyinstaller weather_cli_4.spec      # 纯单个exe文件无dll
    或者
    pyinstaller -D -n weather_cli weather_cli.spec   # 带dll文件
    `
    生成的 weather_cli.exe 可放到任意 Windows 电脑双击使用。
  * weather_cli_4.spec为跨平台的打包配置文件
  * 注意区分打包EXE情况下和script情况下寻找json的路径区分

为了保护key安全，可以将settings.json放到.gitignore中