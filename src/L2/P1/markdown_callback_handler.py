'''
    LangChain 的 verbose 输出本质是 CallbackHandler 机制，
默认用 StdOutCallbackHandler 打印到控制台
    可以自定义一个 CallbackHandler，捕获 on_agent_action、on_tool_start、
on_tool_end、on_chain_end 等事件，用时间戳组织为结构化日志
    运行结束后，将日志按 markdown 格式写入文件，支持可视化、归档、复盘。
'''
import os
import time
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage

# 继承基础的BaseCallbackHandler，重写方法
class MarkdownCallbackHandler(BaseCallbackHandler):
    def __init__(self, output_path: str = "agent_log.md"):
        self.output_path = output_path
        self.logs: List[str] = []

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        log = f"\n### 🤖 Agent Action ({time.strftime('%H:%M:%S')})\n- **Tool:** {action.tool}\n- **Input:** {action.tool_input}\n"
        self.logs.append(log)

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        tool_name = serialized.get("name", "Unknown")
        log = f"\n### 🔧 Tool Start ({time.strftime('%H:%M:%S')})\n- **Tool:** {tool_name}\n- **Input:** {input_str}\n"
        self.logs.append(log)

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        log = f"\n### ✅ Tool End ({time.strftime('%H:%M:%S')})\n- **Output:** {output}\n"
        self.logs.append(log)

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        log = f"\n### 🏁 Chain End ({time.strftime('%H:%M:%S')})\n- **Final Output:** {outputs.get('output', '')}\n"
        self.logs.append(log)

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        log = f"\n### 🏁 Agent Finish ({time.strftime('%H:%M:%S')})\n- **Return:** {finish.return_values}\n"
        self.logs.append(log)

    def save_to_file(self):
        with open(self.output_path, "a", encoding="utf-8") as f:
            f.write("# 🤖 Agent Execution Log\n\n")
            f.writelines(self.logs)
        print(f"✅ Log saved to {self.output_path}")
