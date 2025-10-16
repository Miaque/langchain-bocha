# 🦜️🔗 LangChain Bocha

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

这个包包含了 LangChain 与[博查搜索（Bocha Search）](https://www.bocha.ai/)的集成

```bash
pip install -U langchain-bocha
```

---

## 安装

```bash
pip install -U langchain-bocha
```

### 凭证

我们需要设置博查 API 密钥。您可以通过访问[博查AI开放平台](https://open.bochaai.com)并创建账户来获取 API 密钥。

```python
import getpass
import os

if not os.environ.get("BOCHA_API_KEY"):
    os.environ["BOCHA_API_KEY"] = getpass.getpass("Bocha API key:\n")
```

## Bocha Search

这里我们展示如何实例化博查搜索工具。该工具接受各种参数来自定义搜索。实例化后，我们使用简单的查询调用该工具。该工具允许您使用博查的 Web Search API 端点完成搜索查询。

### 🎯 结构化响应

`BochaSearch` 工具返回标准的字典格式（JSON可序列化），但你可以选择将其转换为结构化的 `SearchResponse` 对象以获得类型安全：

**选项1: 直接使用字典**（推荐用于Agent集成）
```python
from langchain_bocha import BochaSearch

tool = BochaSearch()
result_dict = tool.invoke({"query": "人工智能"})

# 字典访问
query = result_dict["queryContext"]["originalQuery"]
pages = result_dict["webPages"]["value"]
```

**选项2: 转换为结构化对象**（推荐用于类型安全）
```python
from langchain_bocha import BochaSearch, SearchResponse

tool = BochaSearch()
result_dict = tool.invoke({"query": "人工智能"})

# 转换为结构化对象以获得类型安全
result = SearchResponse(**result_dict)

# 类型安全的访问，IDE自动补全
print(result.query_context.original_query)  # "人工智能"
print(result.web_pages.total_estimated_matches)  # 1234567

# 遍历结果
for page in result.web_pages.value:
    print(f"{page.name}: {page.url}")
    if page.summary:
        print(f"摘要: {page.summary}")
```

**结构化对象的优势**:
- ✅ **类型安全**: IDE 自动补全和类型检查
- ✅ **数据验证**: Pydantic 自动验证所有字段
- ✅ **更好的文档**: 每个字段都有清晰的类型和描述
- ✅ **易于使用**: 使用 `.` 访问属性而不是字典键

### 实例化

工具在实例化期间接受各种参数：

- `count` (可选, int): 返回的最大搜索结果数量，范围 1-50。默认为 10。
- `freshness` (可选, str): 搜索时间范围。默认为 "noLimit" (推荐)。
  - `"noLimit"`: 不限时间（推荐，搜索算法会自动优化）
  - `"oneDay"`: 一天内
  - `"oneWeek"`: 一周内
  - `"oneMonth"`: 一个月内
  - `"oneYear"`: 一年内
- `summary` (可选, bool): 是否为每个结果返回详细的文本摘要。默认为 False。
- `include` (可选, str): 指定搜索的网站范围，多个域名使用 `|` 或 `,` 分隔，最多20个。
- `exclude` (可选, str): 排除搜索的网站范围，多个域名使用 `|` 或 `,` 分隔，最多20个。

有关可用参数的全面概述，请参考[博查 Web Search API 文档](https://bocha-ai.feishu.cn/wiki/RXEOw02rFiwzGSkd9mUcqoeAnNK)

```python
from langchain_bocha import BochaSearch

tool = BochaSearch(
    count=10,
    freshness="noLimit",  # 推荐使用，让搜索算法自动优化
    summary=True,  # 获取详细摘要
    # include="example.com|another.com",  # 可选：限制搜索域名
    # exclude="exclude.com",  # 可选：排除某些域名
)
```

### 直接使用参数调用

博查搜索工具在调用期间接受以下参数：

- `query` (必需): 自然语言搜索查询
- 以下参数也可以在调用期间设置：`freshness`、`summary`、`include`、`exclude`

注意：如果您在实例化期间设置了参数，该值将持久化并覆盖调用期间传递的值。

```python
# 基本查询
tool.invoke({"query": "博查搜索的最新功能是什么"})

# 带时间范围的查询
tool.invoke({
    "query": "人工智能最新进展", 
    "freshness": "oneWeek",
    "summary": True
})

# 限制搜索域名
tool.invoke({
    "query": "Python教程",
    "include": "python.org|docs.python.org"
})
```

输出：

```python
{
    "_type": "SearchResponse",
    "queryContext": {
        "originalQuery": "博查搜索的最新功能是什么"
    },
    "webPages": {
        "webSearchUrl": "",
        "totalEstimatedMatches": 1234567,
        "value": [
            {
                "id": null,
                "name": "博查AI开放平台",
                "url": "https://open.bochaai.com",
                "displayUrl": "https://open.bochaai.com",
                "snippet": "博查AI开放平台是杭州博查搜索科技...",
                "summary": "博查AI开放平台提供AI搜索、Web搜索、AI Agent等服务...",
                "siteName": "open.bochaai.com",
                "siteIcon": "https://th.bochaai.com/favicon?domain_url=...",
                "datePublished": "2024-07-22T00:00:00+08:00",
                "dateLastCrawled": "2024-07-22T00:00:00Z",
                "cachedPageUrl": null,
                "language": "zh"
            },
            ...
        ],
        "someResultsRemoved": false
    },
    "images": {
        "value": [
            {
                "contentUrl": "https://...",
                "thumbnailUrl": "https://...",
                "name": "图片标题"
            },
            ...
        ]
    }
}
```

### Agent 工具调用

我们可以通过将工具绑定到 agent 来直接使用我们的工具与 agent executor。这使 agent 能够动态设置博查搜索工具的可用参数。

```python
# !pip install -qU langchain langchain-openai langchain-bocha
from typing import Any, Dict, Optional
import datetime

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_bocha import BochaSearch
from langchain.schema import HumanMessage, SystemMessage

# 初始化 LLM
llm = init_chat_model(model="gpt-4o", model_provider="openai", temperature=0)

# 初始化博查搜索工具
bocha_search_tool = BochaSearch(
    count=5,
    summary=True,  # 获取详细摘要，更适合AI使用
)

# 设置包含 'agent_scratchpad' 的 Prompt
today = datetime.datetime.today().strftime("%D")
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""你是一个有用的研究助手，你将被给予一个查询，你需要
    在网络上搜索最相关的信息。今天的日期是 {today}。"""),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # 工具调用所需
])

# 创建一个可以使用工具的 agent
agent = create_openai_tools_agent(
    llm=llm,
    tools=[bocha_search_tool],
    prompt=prompt
)

# 创建 Agent Executor 来处理工具执行
agent_executor = AgentExecutor(agent=agent, tools=[bocha_search_tool], verbose=True)

user_input = "请告诉我最近一周关于人工智能的重要新闻"

# 正确构造输入为字典
response = agent_executor.invoke({"messages": [HumanMessage(content=user_input)]})
```

## 特性

- **全网搜索**：从全网搜索任何网页信息和网页链接
- **准确摘要**：结果准确、摘要完整，更适合 AI 使用
- **时间范围过滤**：可配置搜索时间范围（推荐使用 noLimit 让算法自动优化）
- **图片搜索**：API 自动返回相关图片
- **详细摘要**：可选择是否显示详细文本摘要（summary 参数）
- **域名过滤**：支持包含或排除特定域名
- **Bing 兼容格式**：响应格式兼容 Bing Search API

## API 参数说明

### freshness (时间范围)

```python
# 推荐使用 noLimit，让搜索算法自动优化
tool = BochaSearch(freshness="noLimit")

# 其他选项
tool = BochaSearch(freshness="oneDay")    # 一天内
tool = BochaSearch(freshness="oneWeek")   # 一周内
tool = BochaSearch(freshness="oneMonth")  # 一个月内
tool = BochaSearch(freshness="oneYear")   # 一年内
```

### summary (文本摘要)

```python
# 默认不返回摘要
tool = BochaSearch(summary=False)

# 返回详细摘要，更适合AI使用
tool = BochaSearch(summary=True)
```

### include / exclude (域名过滤)

```python
# 只搜索特定域名
tool = BochaSearch(include="python.org|stackoverflow.com")

# 排除特定域名
tool = BochaSearch(exclude="example.com|spam.com")

# 可以同时使用
tool = BochaSearch(
    include="edu|gov",  # 只搜索教育和政府网站
    exclude="ads.com"   # 但排除广告网站
)
```

## API 文档

更多详细信息，请访问：
- [Web Search API 文档](https://bocha-ai.feishu.cn/wiki/RXEOw02rFiwzGSkd9mUcqoeAnNK)
- [在 LangChain 中使用博查搜索API](https://bocha-ai.feishu.cn/wiki/XXCsw2Dyjiny8OkJl0KcWjyOnDb)
- [博查AI开放平台](https://open.bochaai.com)

## 响应格式

博查 API 的响应格式兼容 Bing Search API，包括：

- **网页结果**：包括 name、url、snippet、summary、siteName、siteIcon、datePublished 等信息
- **图片结果**：包括 contentUrl、thumbnailUrl、name 等信息

## 许可证

本项目采用 MIT 许可证。
