# 阶段 1 · 项目 1
## 「桌面文件分类机器人」
- 目标：双击即可运行，把 ~/Desktop 下的 3 类文件（图片、文档、压缩包）自动移进对应文件夹，从而第一次把“感知-决策-行动”的 Agent 闭环跑通。

## 核心知识点
1. 理解agent的"感知-决策-行动"闭环
2. 掌握文件系统API
3. 掌握规则匹配（python语法dictionary和list）
4. 学习脚本打包、pytest、schedule、pyyaml等知识

# 知识点拆解
1. #!/usr/bin/env python3
    - Shebang，Linux/Mac 可直接 ./file_organizer_agent.py 运行；Windows 双击 .py 会调用默认 Python 解释器。
2. import os / shutil / pathlib
    - pathlib.Path：面向对象的文件系统 API，比传统 os.path 更直观。
    - shutil.move：高级“移动+重命名”函数，跨盘时自动完成复制+删除。
3. RULES 字典
    - “规则匹配”核心——把“人类语义类别”映射到“机器可识别的后缀列表”。
    规则与代码分离，后续可改成 YAML/JSON，让非程序员也能改。
4. classify() 函数
    - 纯函数，无副效应，方便单元测试：

    `
    assert classify("a.JPG") == "Images"
    move_file() 
    mkdir(exist_ok=True)
    `：首次运行时自动创建文件夹，无需手工新建。
    重名检测循环：演示“防御式编程”，避免覆盖用户数据。
    print 日志：最简单的“可观测性”，后续可换成 logging 模块。


    跨平台获取桌面：
    `
    Path.home() / "Desktop"
    Win  → C:\Users\<user>\Desktop
    Mac  → /Users/<user>/Desktop
    Linux→ /home/<user>/Desktop
    `

    `if __name__ == "__main__"`
    Python 脚本入口惯例，允许未来把代码作为模块导入而不触发整理逻辑。

# 拓展
1. 把 RULES 外置到 rules.yaml，用 pyyaml 加载，体会“数据驱动”。
2. 用 argparse 支持命令行参数：
`
python file_organizer_agent.py --path ~/Downloads --dry-run
--dry-run 只打印计划而不真正移动，练习“决策预览”思维。
`
3. 打包成“双击”可执行文件：
`
pip install pyinstaller
pyinstaller -F -w file_organizer_agent.py
`
会在 dist/ 生成独立 .exe，给朋友也能运行。
4. 加入“定时感知”——用 schedule 每 10 分钟扫描一次，向“持续运行”的 Agent 演进。
5. 写 3 个单元测试（pytest）：
   - 测试 classify 对大小写不敏感
   - 测试重名移动后计数器正确
   - 测试空桌面不报错
  
  <u>注意： pytest需要在../src\L1\P1\ 目录中用python -m pytest ..运行</u>