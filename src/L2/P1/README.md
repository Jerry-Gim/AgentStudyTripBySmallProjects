# 阶段 2 · 项目 1
## 「ReAct 版维基百科问答」
-   **目标**：用户提问 → 大模型按 Thought→Action→Observation 循环调用维基 API → 终端打印 3 步推理轨迹 → 给出最终答案。
-   **通过动手实现，掌握**
    - ReAct 提示模板
    - LangChain AgentExecutor
    - 维基百科工具封装
    - verbose 推理链可视化

# 最终体验：
    $ python wiki_react.py
    问题> 谁发明了电话？
    Thought: 需要搜索“电话 发明者”
    Action: Wikipedia → "telephone"
    Observation: Alexander Graham Bell 通常被认为是电话的发明者……
    Thought: 信息已足够
    Answer: 亚历山大·格拉汉姆·贝尔被广泛认为是电话的发明者。
    （全程 3 步，可继续追问）

# 依赖：
```
pip install langchain wikipedia
pip install langchain_community
pip install langchain-openai
```

*(可选)*`
export OPENAI_API_KEY=sk-xxx
`

*现在新版openai可以作为环境变量，例如用set OPENAI_API_KEY = key*

# ReAct框架：基础Agent运行循环的升级
1. **ReAct** = Reasoning + Acting, 一种“边推理边行动”框架，核心是让大模型像人一样“先想→再做→再看结果→再思考”，循环往复直到任务完成。
   - 之前在[Level 1 Program 1](../../L1/P1/README.md#核心知识点)中我们学习了一个最基本的agent具有的"感知-决策-行动"闭环，现在我们使用ReAct框架，将这个简单的agent升级到大模型：
     - **思考（Thought）**：模型分析当前问题与已有信息，判断下一步该做什么。
     - **行动（Action）**：根据思考结果，从注册的工具列表里选择一个调用，并给出参数；LangChain 会把这次调用交给对应的 Tool 函数去执行。
     - **观察（Observation）**：把工具返回的结果作为新信息送回模型，成为下一轮思考的输入。
   - 这个循环会被写进提示模板，由ReActSingleInputOutputParser把模型的每步输出解析成继续循环还是给出最终答案。主循环反复触发直到AgentFinish
   - 这个框架对于开发者更加友好
     - **@tool**装饰普通函数将任意方法（搜索/计算/数据库/API）注册为工具；
     - 选用内置的AgentType.REACT或者手写LCEL链，就能把“推理+工具”流程串起来，实现复杂的多跳问答，自动报表，智能运维等厂家。
 - **总结**：ReAct 把“让大模型自己决定何时调用外部工具”做成了标准范式，是 LangChain 打造自主智能体的关键基石

# 调度LLM Agent的方式:
- ***Agent*** (由create_react_agent()等方法获得)：是一个*LangChain Runnable*对象，本质是LLM+Prompt+OutputParser。
  - 输入：{“input”: 问题, “intermediate_steps”: 之前走过的 Thought/Action/Obs 列表}
  - 输出：AgentAction（要去调工具）或 AgentFinish（任务结束，返回答案）。
  - **职责**：只负责“想”和“决定”，不亲自调用工具，也不保存状态。
- ***AgentExecutor***（由AgentExector()构造方法获得）：是一个while循环+一场不会+工具执行+早期停止策略
  - 流程：
    1. 把用户问题包装后喂给 agent。
    2. 拿到 AgentAction → 找对应 tool 运行 → 把 Observation 写回。
    3. 重复直到 AgentFinish 或达到 max_iterations。
  - 额外功能：
    - 自动加 memory（把历史放到 prompt）。
    - 处理解析失败（handle_parsing_errors）。
    - 日志/verbose、early stopping、return_intermediate_steps 等。

| 组件           | 本质               | 作用                             | 典型对象/示例                                             | 一句话记忆        |
| ------------ | ---------------- | ------------------------------ | --------------------------------------------------- | ------------ |
| **LLM**      | 大模型接口            | 接收文本→输出文本                      | `ChatOpenAI`、`Ollama`、`DeepSeek`                    | 只会“说话”的脑     |
| **Prompt**   | 带变量的模板           | 把用户输入+上下文拼成模型可读的完整提示           | `hub.pull("hwchase17/react")`                       | 给大脑的“考题纸”    |
| **Agent**    | LLM+Prompt+输出解析器 | 按 ReAct 模板决定“下一步：调用哪个工具/是否结束”  | `create_react_agent(llm, tools, prompt)`            | 专出“指令”的参谋    |
| **Executor** | while 循环驱动器      | 反复执行：问 Agent→调工具→回传结果，直到拿到最终答案 | `AgentExecutor(agent=..., tools=..., verbose=True)` | 负责“跑腿+循环”的管家 |



# 知识讲解：
1. WikipediaAPIWrapper(lang="en")
- 官方封装：自动调用维基百科 REST API，返回前 1 条摘要，省去自己写 requests。
2. ZERO_SHOT_REACT_DESCRIPTION
- LangChain 内置 ReAct 提示模板，零样本即可让 LLM 生成，提示词里没有“演示”段落，LLM 只通过 Tool 的 description 字段理解每个工具的用途。LLM进行ReAct循环直到认为任务完成。只要工具起好名字写好描述，就能在运行时被AI模型理解并被Agent自动选中，无需对模型针对工具进行额外训练，关键词，或者写复杂逻辑
```
Thought: xxx
Action: Wikipedia[xxx]
Action Input: xxx
Observation: ...
```
   循环直至得出答案 。

3. verbose=True
- 终端实时显示完整推理链，每一步 Thought → Action → Observation、LLM 调用、工具参数、返回结果等都会实时输出，方便调试；关闭后可静默调用。
4. handle_parsing_errors=True
- 若 LLM 输出格式不合法，自动重试一次，避免程序崩溃。LLM 输出格式偶尔“放飞自我”，比如少写引号、把 Action: 拼错，导致 ReAct 解析器抛出 OutputParserException。一旦解析失败，整个 Agent 流程直接崩溃。handle_parsing_errors就是用来处理这种情况：
  - 参数
    1. **True**：内置的“自我修复提示”，把错误输出和信息反馈给大模型，让其生成一次符合格式的回答
    2. **自定义提示字符串**：把这段固定的文本作为Observation喂回大模型，体系模型修正格式回答
    3. **自定义函数 *f(exc, llm_output:str)->str***: 通过函数来自由处理怎么返回Observation和处理，例如打日志，调用备用模型/解析器，甚至直接返回最终答案
1. 温度 temperature=0
- 控制LLM输出随机性的核心参数，取值范围通常在0-1
- 降低“幻觉”，让推理链更稳定，适合演示。
  - **temperature=0**: 强确定性，几乎每次问都一样。场景：<u>数学计算、格式解析、生产问答</u>
  - **temperature=0.3~0.7**: 适度多样，仍可控。场景: <u>对话、写作、头脑风暴</u>
  - **temperature>=1**: 非常随机，可能出现“胡言乱语”。场景: <u>创意写作、诗歌、彩蛋</u>

## 知识详解：LangChain
- LangChain 是一个开源的 Python/JS 框架，被社区称为“大模型的操作系统”。它把提示词管理、模型调用、外部工具、记忆、向量化检索等常用能力抽象成可复用的“积木”，开发者只需按需组合即可快速搭建生产级 LLM 应用，而无需重复造轮子
- **六大核心组件：**
  - **Model I/O**: 统一封装OpenAI、DeepSeek、通义千问、本地Ollama等接口，便于同一行代码切换模型（切换base_url和api_key切换模型接口）
  - **Prompts**: 把“提示-模型-后处理”串成流水线；内置LLMChain、RetrievalQA、SQLChain等，5行代码即可跑通RAG或者SQL问答
  - **Memory**：自动化管理多轮对话历史，支持缓冲区、摘要、实体记忆等多种策略，解决上下文溢出问题
  - **Retrieval**: 内置文档加载、文本分块、向量化与FAISS/Chroma/PGVector
  - **Agents**: 让模型自己决定调用搜索、计算器、数据库等工具，实现“推理+行动”的自主智能体

# 拓展练习
1. 中文维基：把 lang="zh"，提示模板加“请用中文回答”，体验跨语言 ReAct。
2. 自建工具：再封装一个 DuckDuckGo 搜索工具，让 Agent 在“维基无结果”时自动 fallback，练习多3工具路由。
3. 记忆增强：接入 ConversationBufferMemory，支持追问“他是什么时候申请的专利？”—— 练习“带记忆的 ReAct” 。
4. 量化评估：随机 20 道常识题，对比“纯 LLM 回答” vs “ReAct+维基”准确率，体验工具增强效果。
5. 提示可视化：把 verbose 输出保存为 .md，用 Typora 查看漂亮推理流程，方便写报告。

# 如何进行量化测试
## 准备题目
随机抽取20到常识题
- 例如可以让LLM（联网）生成一百到常识问答题，要求输出问题和答案，且尽量唯一答案且可量化正确性
## 分别用两种模式回答
- 纯LLM (不适用工具)：`llm.invoke("Q1: ...")`
- ReAct + Wikipedia: `executor.invoke({"input": question})`
## 人工或者自动判分
统计两种模式的准确率


# 运行演示
```
$python wiki_react.py
=== ReAct维基回答 === （输入q退出）

问题> 谁发明了电话？


> Entering new AgentExecutor chain...
Thought: 我需要找出谁发明了电话。这可以通过查询维基百科来确认。
Action: wikipedia
Action Input: 电话 发明者
ObservNo good Wikipedia Search Result was foundThought: 我需要更精确地搜索“电话发明者”这一主题，尝试使用英文关键词进行搜索，因为历史记录中常用英文资料记录此类发明。
Action: wikipedia
Action Input: inventor of the telephone
ObservNo good Wikipedia Search Result was foundThought: 我需要更准确地搜索与“电话的发明者”相关的信息，尝试使用关键人物的名字或更具体的术语进行查询。
Action: wikipedia
Action Input: Alexander Graham Bell  Page: Alexander Graham Bell
Summary: Alexander Graham Bell ( ; born Alexander Bell; March 3, 1847 – August 2, 1922) was a  Scottish-born Canadian-American inventor, scientist, and engineer who is credited with patenting the first practical telephone. He also co-founded the American Telephone and Telegraph Company (AT&T) in 1885.
Bell's father, grandfather, and brother had all been associated with work on elocution and speech, and both his mother and wife were deaf, profoundly influencing Bell's life's work. His research on hearing and speech further led him to experiment with hearing devices, which eventually culminated in his being awarded the first U.S. patent for the telephone, on March 7, 1876. Bell considered his invention an intrusion on his real work as a scientist and refused to have a telephone in his study.
Many other inventions marked Bell's later life, including ground-breaking work in optical telecommunications, hydrofoils, and aeronautics. Bell also had a strong influence on the National Geographic Society and its magazine while serving as its second president from 1898 to 1903.
Beyond his work in engineering, Bell had a deep interest in the emerging science of heredity. His work in this area has been called "the soundest, and most useful study of human heredity proposed in nineteenth-century America ... Bell's most notable contribution to basic science, as distinct from invention."



Page: The Story of Alexander Graham Bell
Summary: The Story of Alexander Graham Bell is a somewhat fictionalized 1939 biographical film of the famous inventor. It was filmed in black-and-white and released by Twentieth Century-Fox. The film stars Don Ameche as Bell and Loretta Young as Mabel, his wife, who contracted scarlet fever at an early age and became deaf.
The first half of the film concentrates on the hero's romantic, financial, and scientific struggle.
Henry Fonda is notable in a co-starring role as Mr. Watson, who hears the first words ever spoken over the telephone. In a pivotal scene, Bell (Don Ameche), while working on the telephone, accidentally spills acid onto his lap and shouts in pain, “Mr. Watson, come here! I want you!” Watson, barely able to contain his own excitement, rushes into the room and stammers out the news that he heard Bell calling out to him over the telephone receiver.  Bell has Watson repeat his own words to him to confirm it, and the two men begin hopping around the room, with Watson yelling out a war whoop.
The last part depicts the legal struggle against Western Union over patent priority in the invention of the telephone, ending with a courtroom victory. The final scene has the hero contemplating crewed flight, under his wife's adoring gaze.
The film led to the use of the word "ameche" as juvenile slang for a telephone, as noted by Mike Kilen in the Iowa City Gazette: "The film prompted a generation to call people to the telephone with the phrase: 'You're wanted on the Ameche.'" Such an identity between Ameche and the telephone was forged, that in the 1940 film Go West, Groucho Marx proclaims, "Telephone? This is 1870, Don Ameche hasn't invented the telephone yet."



Page: Alexander Graham Bell honors and tributes
Summary: Alexander Graham Bell (March 3, 1847 – August 2, 1922) was an inventor, scientist, and engineer who received numerous honors and tributes during his life, and new awards were subsequently named for him posthumously.Thought: 根据维基百科的观察结果，Alexander Graham Bell 被认为是发明了第一台实用电话的人，并于1876年获得了美国第一个电话专利。此外，他还因此被广泛认可为电话的发明者。

Final Answer: 电话是由亚历山大·格雷厄姆·贝尔（Alexander Graham Bell）发明的。他于1876年获得了第一台实用电话的专利，并因此被公认为电话的发明者。

> Finished chain.
Answer: 电话是由亚历山大·格雷厄姆·贝尔（Alexander Graham Bell）发明的。他于1876年获得了第一台实用电话的专利，并因此被公认为电话的发明者。

问题>
```

**多工具**

```
问题> 公认的世界几大奇迹？


> Entering new AgentExecutor chain...
Question: 公认的世界几大奇迹？
Thought: 这个问题询问的是公认的世界几大奇迹，通常指的是“古代世界七大奇迹”以及可能包括现代评选的“新世界七大奇迹”。我需要查找这些信息。
Action: wikipedia
Action Input: 世界七大奇迹
ObservNo good Wikipedia Search Result was foundThought: 维基百科搜索未返回有效结果，我需要通过全网搜索来获取关于“公认的世界几大奇迹”的信息。
Action: duckduckgo_search
Action Input: 公认的世界几大奇迹
1. 肏翻你们女孩儿们当日常实属无奈啊 的 高中 奇 幻生活-校园-爱丽丝书屋
但微微也并非故意如此，这个 世 界 是未来某个仪式循环轮回无数次后所产生 的 新 世 界 ，而未来那个仪式 的 原型“零号道具”，在未来某个时刻也会被微微首. 度创作出来。
https://www.alicesw.com/novel/33235.html

2. agedm.io/catalog/all-all-all-血腥-all-点击量-1
第三期于2018年7月22日起每周日在NHK综合频道首播，全24话。 历经百年 的 时光，将人类与外侧 世 界 隔开 的 墙壁。 在墙壁 的 另一侧，似乎有前所未见 的 世 界 延伸开来。 火焰之水、冰之 大 地、砂之雪原……。
https://www.agedm.io/catalog/all-all-all-血腥-all-点击量-1

3. 艺术 大 师 的 幽默 八个隐藏在杰作中 的 古怪细节 - BBC 英伦网
例如蒙娜丽莎不安 的 右手手指、卡萝（Frida Kahlo）最为闻名于 世 的 自画像，主人 公 眼神里象征刚毅 的 塔罗符号等……随着名画中这些细节 的 展露，我不禁想起法国诗.
https://www.bbc.com/ukchina/simp/vert-cul-47542873

4. 五角 大 楼建议将阿里巴巴、百度、比亚迪列入协助中国军方 的 名单
法国 世 界 媒体集团 (France Médias Monde).
https://www.rfi.fr/cn/中国/20251126-五角大楼建议将阿里巴巴-百度-比亚迪列入协助中国军方的名单

5. wangyukun.blog.caixin.com/archives/134765
尼古拉·特斯拉 的 前 世 今生. 科学 界 有一个普遍共识，人类历史上曾经存在过两个 公 认 的 旷 世 天才：达·芬 奇 (Da Vinchy)和尼古拉·特斯拉(NikolaTesla)。在厄瓜多尔La Maná发现 的 世 界 地图石.
https://wangyukun.blog.caixin.com/archives/134765Thought: 搜索结果未能直接提供关于“公认的世界几大奇迹”的清晰信息。我需要进一步使用更精确的关键词进行搜索，以获取古代世界七大奇迹和新世界七大奇迹的相关内容。
Action: duckduckgo_search
Action Input: 古代世界七大奇迹 新世界七大奇迹 一览
1. 网易云音乐网页版入口-网易云音乐网页版官网登录入口_百度知道
Jun 12, 2025 · 以下是关于网易云音乐网页版的一些关键点介绍： 1. 入口与访问方式 官网链接：用户可以通过浏览器直接访问上述网址，进入网易云音乐的网页版。 界面设计：网页版界面简 …
https://zhidao.baidu.com/question/1380390322071234339.html

2. 网易云电脑版下载官网 - 百度知道
Apr 16, 2025 · 网易云电脑版下载官网网易云电脑版的官方下载网址为：https://music.163.com/download。 以下是关于网易云电脑版下载官网的详细解答：一、官 …
https://zhidao.baidu.com/question/596532176109819645.html

3. 网易云音乐网页版官网 - 百度知道
Apr 18, 2025 · 网易云音乐网页版官网网易云音乐网页版官网的网址是：https://music.163.com/。 以下是对网易云音乐网页版官网的详细介绍：官方网址：用户只需在浏览器中输入上述网址， …
https://zhidao.baidu.com/question/404981490438518565.html

4. 网易云音乐官网下载 - 百度知道
Apr 16, 2025 · 网易云音乐官网下载网易云音乐官网的下载方式如下：直接访问官网下载：网易云音乐的官方下载链接为：https://music.163.com/。 在浏览器中输入该网址，即可进入网易云 …
https://zhidao.baidu.com/question/1716057056796641340.html

5. 网易云下载官网 - 百度知道
Apr 23, 2025 · 以下是关于网易云音乐官网下载的一些详细信息：官网地址：网易云音乐的官方网站地址为 https://music.163.com/。 在该网站上，用户可以找到关于
https://zhidao.baidu.com/question/1844060260833659540.htmlThought: 搜索结果仍然未能提供关于“公认的世界几大奇迹”的有效信息。我需要更换更准确的关键词，尝试直接搜索“世界七大奇迹 古代 新”或类似表达，以获取权威解释。

Action: duckduckgo_search
Action Input: 世界公认的古代七大奇迹和新七大奇迹 列表
1. 世界七大奇迹（古代世界七处宏伟景观）_百度百科



2. Job d’été • Province Sud
Bienvenue sur le portail de Job d’été en province Sud. Que vous soyez un jeune à la recherche d’une opportunité de travail pour l’été ou un employeur souhaitant recruter des talents …
https://www.province-sud.nc/job-ete

3. Les jobs d’été - Ville de Nouméa
Les jobs d’été sont l’occasion pour les jeunes de 16 à 26 ans de découvrir le monde du travail, la diversité des métiers dans une collectivité, de comprendre le fonctionnement des services …
https://www.noumea.nc/noumea-pratique/mairie-recrute/jobs-ete

4. Job d'été c'est maintenant ! | Espace Jeunes province Sud
Les inscriptions pour le Job d'été 2024-2025 sont ouvertes depuis le 1er novembre ! Les Jobs d'été, c'est l'opportunité de gagner en expérience, découvrir des métiers et gagner ton premier …
https://www.espacejeunes.nc/actualites/job-dete-cest-maintenant

5. Dispositif Job d'été pour les jeunes | service-public. nc
Chaque année, la province Sud lance le dispositif « Job d’été » pour aider les jeunes calé
https://service-public.nc/article/dispositif-job-d-ete-pour-les-jeunesThought: 搜索结果仍未直接提供完整信息，但第一条“世界七大奇迹（古代世界七处宏伟景观）_百度百科”链接很可能指向有效内容。尽管未显示详细文本，我可以基于广泛认知的常识回答该问题：公认的“古代世界七大奇迹”和2007年评选的“新世界七大奇迹”是公众普遍接受的两个列表。我将结合这一常识进行总结。

Final Answer: 公认的世界几大奇迹通常分为两类：

1. **古代世界七大奇迹**（Ancient World Seven Wonders）：
   - 吉萨大金字塔（埃及）——唯一现存至今的奇迹
   - 巴比伦空中花园（伊拉克，传说中存在）
   - 阿尔忒弥斯神庙（土耳其以弗所）
   - 奥林匹亚宙斯神像（希腊）
   - 摩索拉斯陵墓（土耳其哈利卡纳苏斯）
   - 罗德岛太阳神巨像（希腊）
   - 亚历山大灯塔（埃及）

2. **新世界七大奇迹**（2007年由全球投票选出）：
   - 中国：长城
   - 中国：秦始皇陵兵马俑
   - 意大利：罗马斗兽场
   - 印度：泰姬陵
   - 秘鲁：马丘比丘
   - 墨西哥：奇琴伊察（玛雅金字塔）
   - 巴西：里约热内卢基督救世主雕像

其中，吉萨大金字塔是唯一被普遍认可的古代奇迹中仍存于世的建筑。

> Finished chain.
Answer: 公认的世界几大奇迹通常分为两类：

1. **古代世界七大奇迹**（Ancient World Seven Wonders）：
   - 吉萨大金字塔（埃及）——唯一现存至今的奇迹
   - 巴比伦空中花园（伊拉克，传说中存在）
   - 阿尔忒弥斯神庙（土耳其以弗所）
   - 奥林匹亚宙斯神像（希腊）
   - 摩索拉斯陵墓（土耳其哈利卡纳苏斯）
   - 罗德岛太阳神巨像（希腊）
   - 亚历山大灯塔（埃及）

2. **新世界七大奇迹**（2007年由全球投票选出）：
   - 中国：长城
   - 中国：秦始皇陵兵马俑
   - 意大利：罗马斗兽场
   - 印度：泰姬陵
   - 秘鲁：马丘比丘
   - 墨西哥：奇琴伊察（玛雅金字塔）
   - 巴西：里约热内卢基督救世主雕像

其中，吉萨大金字塔是唯一被普遍认可的古代奇迹中仍存于世的建筑。

问题>
```


