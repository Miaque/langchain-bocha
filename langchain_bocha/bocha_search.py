"""Bocha Search tools."""

from typing import Any, Dict, List, Literal, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field

from langchain_bocha._utilities import BochaSearchAPIWrapper


class BochaSearchInput(BaseModel):
    """Input for [BochaSearch]"""

    query: str = Field(description=("Search query to look up"))
    freshness: Optional[
        Literal["noLimit", "oneDay", "oneWeek", "oneMonth", "oneYear"]
    ] = Field(
        default="noLimit",
        description="""Limits results to content published within a specific timeframe.
        
        Options:
        - "noLimit": No time limit (default, recommended)
        - "oneDay": Within the last day
        - "oneWeek": Within the last week
        - "oneMonth": Within the last month
        - "oneYear": Within the last year
        
        Note: Using "noLimit" is recommended as the search algorithm 
        automatically handles time range optimization.
        """,  # noqa: E501
    )
    summary: Optional[bool] = Field(
        default=False,
        description="""Whether to include detailed text summaries for each result.
        
        Set to True to get comprehensive summaries of web page content.
        Default is False.
        """,  # noqa: E501
    )
    include: Optional[str] = Field(
        default=None,
        description="""Specify search scope to include only certain domains.
        
        Use pipe | or comma , to separate multiple domains (max 20).
        Can specify root domains or subdomains.
        
        Example: "qq.com|m.163.com" or "qq.com,m.163.com"
        """,  # noqa: E501
    )
    exclude: Optional[str] = Field(
        default=None,
        description="""Specify search scope to exclude certain domains.
        
        Use pipe | or comma , to separate multiple domains (max 20).
        Can specify root domains or subdomains.
        
        Example: "qq.com|m.163.com" or "qq.com,m.163.com"
        """,  # noqa: E501
    )


def _generate_suggestions(params: Dict[str, Any]) -> List[str]:
    """Generate helpful suggestions based on the failed search parameters."""
    suggestions = []

    freshness = params.get("freshness")
    include = params.get("include")
    exclude = params.get("exclude")

    if freshness and freshness != "noLimit":
        suggestions.append("Try using 'noLimit' for freshness parameter")
    if include:
        suggestions.append("Remove or broaden the 'include' domain restrictions")
    if exclude:
        suggestions.append("Remove the 'exclude' domain restrictions")
    if not suggestions:
        suggestions.append("Try a different search query")

    return suggestions


class BochaSearch(BaseTool):  # type: ignore[override]
    """Tool that queries the Bocha Search API and gets back json.

    Setup:
        Install ``langchain-bocha`` and set environment variable ``BOCHA_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-bocha
            export BOCHA_API_KEY="your-api-key"

    Instantiate:

        .. code-block:: python
            from langchain_bocha import BochaSearch

            tool = BochaSearch(
                count=10,
                freshness="noLimit",
                summary=False,
            )

    Invoke directly with args:

        .. code-block:: python

            tool.invoke({"query": "博查搜索的最新功能是什么"})

        .. code-block:: json

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
                            "summary": "博查AI开放平台提供AI搜索、Web搜索...",
                            "siteName": "open.bochaai.com",
                            "siteIcon": "https://th.bochaai.com/favicon?domain_url=...",
                            "datePublished": "2024-01-15T10:30:00+08:00",
                            "dateLastCrawled": "2024-01-15T10:30:00Z"
                        }
                    ]
                }
            }

    """  # noqa: E501

    name: str = "bocha_search"
    description: str = (
        "A search engine optimized for comprehensive, accurate, "
        "and trusted results from Bocha AI. "
        "Useful for when you need to answer questions about current events "
        "or search the web. "
        "It retrieves URLs, snippets, and detailed summaries of web pages. "
        "Supports time range filters, domain filtering, and image search "
        "for real-time, accurate results. Input should be a search query."
    )

    args_schema: Type[BaseModel] = BochaSearchInput
    handle_tool_error: bool = True

    freshness: Optional[
        Literal["noLimit", "oneDay", "oneWeek", "oneMonth", "oneYear"]
    ] = None
    """The time range to filter results. 
    Options: noLimit, oneDay, oneWeek, oneMonth, oneYear
    
    Default is noLimit (recommended).
    """

    summary: Optional[bool] = None
    """Whether to include detailed text summaries for each result.
    
    Default is False.
    """

    include: Optional[str] = None
    """Specify domains to include in search. Multiple domains separated by | or ,
    
    Default is None (no restriction).
    """

    exclude: Optional[str] = None
    """Specify domains to exclude from search. Multiple domains separated by | or ,
    
    Default is None (no exclusion).
    """

    count: Optional[int] = None
    """Max search results to return. Range: 1-50
    
    Default is 10.
    """

    api_wrapper: BochaSearchAPIWrapper = Field(default_factory=BochaSearchAPIWrapper)  # type: ignore[arg-type]

    def __init__(self, **kwargs: Any) -> None:
        # Create api_wrapper with bocha_api_key and api_base_url if provided
        if "bocha_api_key" in kwargs or "api_base_url" in kwargs:
            wrapper_kwargs = {}
            if "bocha_api_key" in kwargs:
                wrapper_kwargs["bocha_api_key"] = kwargs["bocha_api_key"]
            if "api_base_url" in kwargs:
                wrapper_kwargs["api_base_url"] = kwargs["api_base_url"]
            kwargs["api_wrapper"] = BochaSearchAPIWrapper(**wrapper_kwargs)

        super().__init__(**kwargs)

    def _run(
        self,
        query: str,
        count: Optional[int] = None,
        freshness: Optional[
            Literal["noLimit", "oneDay", "oneWeek", "oneMonth", "oneYear"]
        ] = None,
        summary: Optional[bool] = None,
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Execute a search query using the Bocha Search API.

        Returns:
            Dict[str, Any]: Search response dictionary with the following structure:
                - type: Response type ("SearchResponse")
                - query_context: QueryContext with original_query
                - web_pages: WebSearchWebPages containing:
                    - total_estimated_matches: Total number of matches
                    - value: List[WebPageValue] with search results
                    - some_results_removed: Whether results were filtered
                - images: WebSearchImages (if available)
                - videos: WebSearchVideos (if available)
        """
        try:
            # Execute search with parameters directly
            raw_results = self.api_wrapper.raw_results(
                query=query,
                count=self.count if self.count is not None else count,
                freshness=self.freshness if self.freshness else freshness,
                summary=self.summary if self.summary is not None else summary,
                include=self.include if self.include else include,
                exclude=self.exclude if self.exclude else exclude,
            )

            # Check if results are empty and raise a specific exception
            if not raw_results.web_pages or not raw_results.web_pages.value:
                search_params = {
                    "freshness": freshness or self.freshness,
                    "include": include or self.include,
                    "exclude": exclude or self.exclude,
                }
                suggestions = _generate_suggestions(search_params)

                # Construct a detailed message for the agent
                error_message = (
                    f"No search results found for '{query}'. "
                    f"Suggestions: {', '.join(suggestions)}. "
                    "Try modifying your search parameters with "
                    "one of these approaches."
                )
                raise ToolException(error_message)

            # Convert to dict for JSON serialization (LangChain requirement)
            return raw_results.to_dict()
        except ToolException:
            # Re-raise tool exceptions
            raise
        except Exception as e:
            return {"error": str(e)}

    async def _arun(
        self,
        query: str,
        count: Optional[int] = None,
        freshness: Optional[
            Literal["noLimit", "oneDay", "oneWeek", "oneMonth", "oneYear"]
        ] = None,
        summary: Optional[bool] = None,
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Use the tool asynchronously."""
        try:
            raw_results = await self.api_wrapper.raw_results_async(
                query=query,
                count=self.count if self.count is not None else count,
                freshness=self.freshness if self.freshness else freshness,
                summary=self.summary if self.summary is not None else summary,
                include=self.include if self.include else include,
                exclude=self.exclude if self.exclude else exclude,
            )

            # Check if results are empty and raise a specific exception
            if not raw_results.web_pages or not raw_results.web_pages.value:
                search_params = {
                    "freshness": freshness or self.freshness,
                    "include": include or self.include,
                    "exclude": exclude or self.exclude,
                }
                suggestions = _generate_suggestions(search_params)

                # Construct a detailed message for the agent
                error_message = (
                    f"No search results found for '{query}'. "
                    f"Suggestions: {', '.join(suggestions)}. "
                    "Try modifying your search parameters with "
                    "one of these approaches."
                )
                raise ToolException(error_message)

            # Convert to dict for JSON serialization (LangChain requirement)
            return raw_results.to_dict()
        except ToolException:
            # Re-raise tool exceptions
            raise
        except Exception as e:
            return {"error": str(e)}
