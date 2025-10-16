"""Example usage of langchain-bocha package."""
# ruff: noqa: T201

from langchain_bocha import BochaSearch, SearchResponse

# 设置 API 密钥
# import os
# os.environ["BOCHA_API_KEY"] = "your-api-key-here"

# 初始化博查搜索工具
bocha_tool = BochaSearch(
    count=10,
    freshness="noLimit",  # 推荐使用，让搜索算法自动优化
    summary=True,  # 获取详细摘要
)

# 执行搜索
if __name__ == "__main__":
    # 示例查询
    query = "人工智能最新进展"

    try:
        # 工具返回字典（JSON可序列化）
        result_dict = bocha_tool.invoke({"query": query})
        
        # 可以转换为结构化对象以获得类型安全
        result = SearchResponse(**result_dict)

        # 类型安全的访问
        print(f"查询: {result.query_context.original_query}")

        if result.web_pages:
            total = result.web_pages.total_estimated_matches
            print(f"找到约 {total:,} 个匹配结果")
            print(f"返回了 {len(result.web_pages.value)} 个结果\n")

            # 打印前3个结果
            for idx, page in enumerate(result.web_pages.value[:3], 1):
                print(f"{idx}. {page.name}")
                print(f"   URL: {page.url}")
                print(f"   摘要: {page.snippet[:100]}...")
                if page.summary:
                    print(f"   详细摘要: {page.summary[:150]}...")
                if page.site_name:
                    print(f"   来源: {page.site_name}")
                if page.date_published:
                    print(f"   发布时间: {page.date_published}")
                print()

        # 打印图片数量（如果有）
        if result.images and result.images.value:
            print(f"找到 {len(result.images.value)} 张相关图片")
            for idx, img in enumerate(result.images.value[:3], 1):
                img_name = img.name or "无标题"
                img_url = img.content_url or ""
                print(f"  {idx}. {img_name}: {img_url}")

    except Exception as e:
        print(f"错误: {e}")

    # 示例2: 直接使用字典
    print("\n" + "=" * 50)
    print("示例2: 直接使用字典访问")
    print("=" * 50 + "\n")

    try:
        result_dict = bocha_tool.invoke(
            {"query": "Python教程", "freshness": "oneWeek", "include": "python.org"}
        )

        # 字典访问方式
        if "webPages" in result_dict and result_dict["webPages"]:
            web_pages = result_dict["webPages"]
            print(f"找到 {len(web_pages.get('value', []))} 个结果")
            
            for idx, page in enumerate(web_pages.get("value", [])[:2], 1):
                print(f"{idx}. {page.get('name', '无标题')}")
                print(f"   URL: {page.get('url', '')}")
                print()

    except Exception as e:
        print(f"错误: {e}")

    # 示例3: 两种方式对比
    print("\n" + "=" * 50)
    print("示例3: 字典 vs 结构化对象")
    print("=" * 50 + "\n")

    try:
        result_dict = bocha_tool.invoke({"query": "博查AI"})

        # 方式1: 字典访问（直接使用）
        print("字典访问:")
        query_text = result_dict.get("queryContext", {}).get("originalQuery", "")
        print(f"  查询: {query_text}")
        
        # 方式2: 结构化对象访问（类型安全）
        print("\n结构化对象访问:")
        result = SearchResponse(**result_dict)
        print(f"  查询: {result.query_context.original_query}")
        print(f"  类型: {result.type}")
        
        if result.web_pages and result.web_pages.value:
            first_result = result.web_pages.value[0]
            print(f"  第一个结果: {first_result.name}")
            
            # IDE提供自动补全和类型检查
            if first_result.summary:
                print(f"  摘要长度: {len(first_result.summary)} 字符")

    except Exception as e:
        print(f"错误: {e}")
