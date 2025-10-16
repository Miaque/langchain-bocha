import json

from langchain_bocha import BochaSearch


def test_search():
    search = BochaSearch()
    result = search.invoke({"query": "今天厦门的天气怎么样?"})
    print(json.dumps(result, ensure_ascii=False))
