"""Pydantic schemas for Bocha Search API responses."""

from typing import List, Optional

from pydantic import BaseModel, Field


class WebPageValue(BaseModel):
    """单个网页搜索结果。"""

    id: Optional[str] = None
    name: str = Field(..., description="网页标题")
    url: str = Field(..., description="网页URL")
    display_url: Optional[str] = Field(
        None, alias="displayUrl", description="展示用URL（URL解码后格式）"
    )
    snippet: str = Field(..., description="网页内容简短描述")
    summary: Optional[str] = Field(
        None, description="网页内容详细摘要（当summary=true时）"
    )
    site_name: Optional[str] = Field(None, alias="siteName", description="网站名称")
    site_icon: Optional[str] = Field(None, alias="siteIcon", description="网站图标URL")
    date_published: Optional[str] = Field(
        None, alias="datePublished", description="发布时间（UTC+8）"
    )
    date_last_crawled: Optional[str] = Field(
        None, alias="dateLastCrawled", description="最后爬取时间"
    )
    cached_page_url: Optional[str] = Field(
        None, alias="cachedPageUrl", description="缓存页面URL"
    )
    language: Optional[str] = Field(None, description="网页语言")
    is_family_friendly: Optional[bool] = Field(None, alias="isFamilyFriendly")
    is_navigational: Optional[bool] = Field(None, alias="isNavigational")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True  # 允许使用原始字段名和别名


class WebSearchWebPages(BaseModel):
    """网页搜索结果集合。"""

    web_search_url: Optional[str] = Field(None, alias="webSearchUrl")
    total_estimated_matches: Optional[int] = Field(
        None, alias="totalEstimatedMatches", description="估计的匹配总数"
    )
    value: List[WebPageValue] = Field(default_factory=list, description="网页结果列表")
    some_results_removed: Optional[bool] = Field(
        None, alias="someResultsRemoved", description="是否有结果被安全过滤"
    )

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class ImageValue(BaseModel):
    """单个图片搜索结果。"""

    content_url: Optional[str] = Field(None, alias="contentUrl", description="图片URL")
    thumbnail_url: Optional[str] = Field(
        None, alias="thumbnailUrl", description="缩略图URL"
    )
    name: Optional[str] = Field(None, description="图片标题")
    width: Optional[int] = Field(None, description="图片宽度")
    height: Optional[int] = Field(None, description="图片高度")
    host_page_url: Optional[str] = Field(
        None, alias="hostPageUrl", description="图片所在页面URL"
    )

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class WebSearchImages(BaseModel):
    """图片搜索结果集合。"""

    value: List[ImageValue] = Field(default_factory=list, description="图片结果列表")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class VideoValue(BaseModel):
    """单个视频搜索结果。"""

    content_url: Optional[str] = Field(None, alias="contentUrl", description="视频URL")
    name: Optional[str] = Field(None, description="视频标题")
    description: Optional[str] = Field(None, description="视频描述")
    thumbnail_url: Optional[str] = Field(
        None, alias="thumbnailUrl", description="缩略图URL"
    )
    duration: Optional[str] = Field(None, description="视频时长")
    host_page_url: Optional[str] = Field(
        None, alias="hostPageUrl", description="视频所在页面URL"
    )

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class WebSearchVideos(BaseModel):
    """视频搜索结果集合。"""

    value: List[VideoValue] = Field(default_factory=list, description="视频结果列表")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class QueryContext(BaseModel):
    """查询上下文。"""

    original_query: str = Field(..., alias="originalQuery", description="原始搜索查询")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class SearchResponse(BaseModel):
    """完整的搜索响应结构。

    这是博查 Web Search API 的完整响应格式。
    """

    type: str = Field(
        ..., alias="_type", description="响应类型，通常为'SearchResponse'"
    )
    query_context: QueryContext = Field(
        ..., alias="queryContext", description="查询上下文"
    )
    web_pages: Optional[WebSearchWebPages] = Field(
        None, alias="webPages", description="网页搜索结果"
    )
    images: Optional[WebSearchImages] = Field(None, description="图片搜索结果")
    videos: Optional[WebSearchVideos] = Field(None, description="视频搜索结果")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True

    def to_dict(self) -> dict:
        """转换为字典格式（使用原始API字段名）。"""
        return self.model_dump(by_alias=True, exclude_none=False)
