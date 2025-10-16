# 结构化响应使用指南

## 📊 概览

`langchain-bocha` 工具返回标准的字典格式（JSON可序列化），但提供了 `SearchResponse` Pydantic 模型，你可以选择将字典转换为结构化对象以获得类型安全。

## 🔄 工作原理

1. **内部处理**: API响应被解析为 `SearchResponse` 对象进行验证
2. **返回格式**: 工具返回字典（`result.to_dict()`），确保 JSON 可序列化
3. **可选转换**: 你可以手动转换为 `SearchResponse` 对象以获得类型安全

## ✨ 核心优势

### 1. 兼容性
```python
from langchain_bocha import BochaSearch

tool = BochaSearch()
result_dict = tool.invoke({"query": "AI"})

# 返回字典，JSON可序列化，与LangChain完美兼容
# 可以在Agent中使用，无需担心序列化问题
```

### 2. 类型安全（可选）
```python
from langchain_bocha import BochaSearch, SearchResponse

tool = BochaSearch()
result_dict = tool.invoke({"query": "AI"})

# 转换为结构化对象
result = SearchResponse(**result_dict)

# IDE 提供完整的自动补全和类型检查
result.query_context.original_query  # ✅ 类型正确
result.web_pages.value[0].name      # ✅ 类型正确
```

### 3. 数据验证
```python
# 内部使用 Pydantic 自动验证所有字段
# 只有合法的API响应才会被返回
```

### 3. 清晰的文档
```python
# 每个字段都有类型提示
class WebPageValue(BaseModel):
    name: str                       # 必填字段
    url: str                        # 必填字段
    summary: Optional[str] = None   # 可选字段
```

## 📚 完整的数据结构

### SearchResponse
```python
class SearchResponse:
    type: str                                    # "_type" in API
    query_context: QueryContext                  # "queryContext" in API
    web_pages: Optional[WebSearchWebPages]       # "webPages" in API
    images: Optional[WebSearchImages]            # "images" in API
    videos: Optional[WebSearchVideos]            # "videos" in API
```

### WebSearchWebPages
```python
class WebSearchWebPages:
    web_search_url: Optional[str]
    total_estimated_matches: Optional[int]       # 总匹配数
    value: List[WebPageValue]                    # 搜索结果列表
    some_results_removed: Optional[bool]         # 是否过滤
```

### WebPageValue
```python
class WebPageValue:
    # 必填字段
    name: str                                    # 标题
    url: str                                     # URL
    snippet: str                                 # 摘要
    
    # 可选字段
    id: Optional[str]
    display_url: Optional[str]                   # 展示URL
    summary: Optional[str]                       # 详细摘要（summary=true时）
    site_name: Optional[str]                     # 网站名
    site_icon: Optional[str]                     # 网站图标
    date_published: Optional[str]                # 发布时间
    date_last_crawled: Optional[str]             # 爬取时间
    cached_page_url: Optional[str]               # 缓存URL
    language: Optional[str]                      # 语言
```

### ImageValue
```python
class ImageValue:
    content_url: Optional[str]                   # 图片URL
    thumbnail_url: Optional[str]                 # 缩略图URL
    name: Optional[str]                          # 标题
    width: Optional[int]                         # 宽度
    height: Optional[int]                        # 高度
    host_page_url: Optional[str]                 # 所在页面URL
```

## 💻 使用示例

### 基础使用（字典方式）
```python
from langchain_bocha import BochaSearch

tool = BochaSearch(count=5, summary=True)
result_dict = tool.invoke({"query": "人工智能"})

# 字典访问
query = result_dict["queryContext"]["originalQuery"]
print(f"查询: {query}")

# 访问网页结果
if "webPages" in result_dict and result_dict["webPages"]:
    web_pages = result_dict["webPages"]
    total = web_pages.get("totalEstimatedMatches", 0)
    print(f"找到约 {total:,} 个结果")
    
    for page in web_pages.get("value", []):
        print(f"标题: {page['name']}")
        print(f"URL: {page['url']}")
        print(f"摘要: {page['snippet']}")
```

### 类型安全使用（结构化对象）
```python
from langchain_bocha import BochaSearch, SearchResponse

tool = BochaSearch(count=5, summary=True)
result_dict = tool.invoke({"query": "人工智能"})

# 转换为结构化对象
result = SearchResponse(**result_dict)

# 类型安全的访问
print(f"查询: {result.query_context.original_query}")

# 访问网页结果
if result.web_pages:
    print(f"找到约 {result.web_pages.total_estimated_matches:,} 个结果")
    
    for page in result.web_pages.value:
        print(f"标题: {page.name}")
        print(f"URL: {page.url}")
        print(f"摘要: {page.snippet}")
        
        # 可选字段需要检查
        if page.summary:
            print(f"详细摘要: {page.summary}")
        if page.site_name:
            print(f"来源: {page.site_name}")
        if page.date_published:
            print(f"发布时间: {page.date_published}")
```

### 图片结果
```python
if result.images and result.images.value:
    print(f"找到 {len(result.images.value)} 张图片")
    
    for img in result.images.value:
        if img.content_url:
            print(f"图片: {img.name}")
            print(f"URL: {img.content_url}")
            print(f"尺寸: {img.width}x{img.height}")
```

### 转换为字典
```python
# 如果需要字典格式（例如用于JSON序列化）
result_dict = result.to_dict()

# 使用原始API字段名
assert "_type" in result_dict
assert "queryContext" in result_dict
assert "webPages" in result_dict
```

### 与Agent集成
```python
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_bocha import BochaSearch, SearchResponse

llm = ChatOpenAI(model="gpt-4o")
tool = BochaSearch()

# Agent会自动处理结构化响应
agent_executor = AgentExecutor(
    agent=create_openai_tools_agent(llm, [tool], prompt),
    tools=[tool]
)

response = agent_executor.invoke({"messages": [...]})
```

## 🔄 字段名映射

Pydantic使用Python命名规范（snake_case），但可以无缝映射到API字段名（camelCase）：

| Python 属性 | API 字段名 |
|------------|------------|
| `type` | `_type` |
| `query_context` | `queryContext` |
| `original_query` | `originalQuery` |
| `web_pages` | `webPages` |
| `total_estimated_matches` | `totalEstimatedMatches` |
| `display_url` | `displayUrl` |
| `site_name` | `siteName` |
| `site_icon` | `siteIcon` |
| `date_published` | `datePublished` |
| `date_last_crawled` | `dateLastCrawled` |
| `content_url` | `contentUrl` |
| `thumbnail_url` | `thumbnailUrl` |

## 🎓 最佳实践

### 1. 使用类型注解
```python
result: SearchResponse = tool.invoke({"query": "..."})
```

### 2. 检查可选字段
```python
if result.web_pages and result.web_pages.value:
    for page in result.web_pages.value:
        if page.summary:  # 检查可选字段
            print(page.summary)
```

### 3. 利用IDE自动补全
```python
# 输入 result. 后，IDE会显示所有可用属性
result.web_pages.value[0].  # 显示WebPageValue的所有字段
```

### 4. 错误处理
```python
try:
    result = tool.invoke({"query": "..."})
    if result.web_pages:
        print(f"找到 {len(result.web_pages.value)} 个结果")
except Exception as e:
    print(f"搜索失败: {e}")
```

## 🔧 迁移指南

工具现在返回字典格式，与博查API的响应结构一致。

### 字典访问（推荐）
```python
from langchain_bocha import BochaSearch

tool = BochaSearch()
result_dict = tool.invoke({"query": "..."})

# 使用博查API的字段名
query = result_dict["queryContext"]["originalQuery"]
if "webPages" in result_dict:
    for page in result_dict["webPages"]["value"]:
        print(page["name"])  # 标题
        print(page["url"])   # URL
```

### 类型安全访问（可选）
```python
from langchain_bocha import BochaSearch, SearchResponse

tool = BochaSearch()
result_dict = tool.invoke({"query": "..."})

# 转换为结构化对象
result = SearchResponse(**result_dict)

# 使用Python风格的属性名
query = result.query_context.original_query
if result.web_pages:
    for page in result.web_pages.value:
        print(page.name)  # 类型安全，IDE自动补全
```

## 📦 导出的类型

所有类型都可以从主包导入：

```python
from langchain_bocha import (
    BochaSearch,           # 主工具类
    SearchResponse,        # 搜索响应
    WebPageValue,          # 网页结果
    WebSearchWebPages,     # 网页结果集合
    ImageValue,            # 图片结果
    VideoValue,            # 视频结果
    WebSearchImages,       # 图片结果集合
    WebSearchVideos,       # 视频结果集合
    QueryContext,          # 查询上下文
)
```

## 🚀 性能

结构化响应不会影响性能：

- ✅ Pydantic v2 使用 Rust 实现，解析速度极快
- ✅ 验证发生在对象创建时，访问属性无额外开销
- ✅ 内存占用与字典相当

## 🐛 调试技巧

```python
# 打印完整的响应结构
print(result.model_dump_json(indent=2))

# 查看所有字段
print(result.model_fields.keys())

# 转换为字典以便检查
result_dict = result.to_dict()
import json
print(json.dumps(result_dict, indent=2, ensure_ascii=False))
```

