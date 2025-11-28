# duck_tool.py
from langchain.tools import BaseTool
from ddgs import DDGS

# 自建封装工具，继承基础工具类
class DuckDuckGoSearchTool(BaseTool):
    name: str = "duckduckgo_search"
    description: str = (
        "若维基返回‘页面不存在’或摘要少于 50 字，请立即使用本工具搜索: "
        "DuckDuckGo 即时搜索工具；当维基百科找不到条目或信息不足时，"
        "可用此工具获取全网最新摘要与链接。"
    )

    def _run(self, query: str) -> str:
        # 返回前 5 条标题+摘要+链接，拼接成一段文本
        with DDGS() as ddgs:
            result = list(ddgs.text(query, max_results=5))
        if not result:
            return "DuckDuckGo 也没检索到任何结果"
        pieces = []
        for i, r in enumerate(result, 1):
            pieces.append(f"{i}. {r['title']}\n{r['body']}\n{r['href']}")
        return "\n\n".join(pieces)
    
    async def _arun(self, query: str) -> str:
        # 简单异步包装，同步即可
        return self._run(query)
