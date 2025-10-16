"""Util that calls Bocha Search API.

In order to set this up, follow instructions at:
https://www.bocha.ai/
"""

import json
from typing import Any, Dict, Literal, Optional

import aiohttp
import requests
from langchain_core.utils import get_from_dict_or_env
from pydantic import BaseModel, ConfigDict, SecretStr, model_validator

from langchain_bocha.schemas import SearchResponse

BOCHA_API_URL: str = "https://api.bochaai.com"


class BochaSearchAPIWrapper(BaseModel):
    """Wrapper for Bocha Search API."""

    bocha_api_key: SecretStr
    api_base_url: Optional[str] = None

    model_config = ConfigDict(
        extra="forbid",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        """Validate that api key and endpoint exists in environment."""
        bocha_api_key = get_from_dict_or_env(values, "bocha_api_key", "BOCHA_API_KEY")
        values["bocha_api_key"] = bocha_api_key

        return values

    def raw_results(
        self,
        query: str,
        freshness: Optional[
            Literal["noLimit", "oneDay", "oneWeek", "oneMonth", "oneYear"]
        ] = None,
        summary: Optional[bool] = False,
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        count: Optional[int] = 10,
    ) -> SearchResponse:
        # Build request parameters
        params: Dict[str, Any] = {
            "query": query,
        }

        # Add optional parameters
        if freshness is not None:
            params["freshness"] = freshness
        if summary is not None:
            params["summary"] = summary
        if include is not None:
            params["include"] = include
        if exclude is not None:
            params["exclude"] = exclude
        if count is not None:
            params["count"] = count

        headers = {
            "Authorization": f"Bearer {self.bocha_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

        base_url = self.api_base_url or BOCHA_API_URL
        response = requests.post(
            f"{base_url}/v1/web-search",
            json=params,
            headers=headers,
        )

        if response.status_code != 200:
            try:
                error_data = response.json()
                error_message = error_data.get("msg", "Unknown error")
            except Exception:
                error_message = response.text or "Unknown error"
            raise ValueError(f"Error {response.status_code}: {error_message}")

        result = response.json()

        # Check if the API returned an error in the response body
        if result.get("code") != 200:
            error_message = result.get("msg", "Unknown error")
            raise ValueError(f"API Error: {error_message}")

        # Return structured response
        # Parse the data portion into a SearchResponse object
        data = result.get("data", {})
        return SearchResponse(**data)

    async def raw_results_async(
        self,
        query: str,
        freshness: Optional[
            Literal["noLimit", "oneDay", "oneWeek", "oneMonth", "oneYear"]
        ] = None,
        summary: Optional[bool] = False,
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        count: Optional[int] = 10,
    ) -> SearchResponse:
        """Get results from the Bocha Search API asynchronously."""

        # Function to perform the API call
        async def fetch() -> str:
            # Build request parameters
            params: Dict[str, Any] = {
                "query": query,
            }

            # Add optional parameters
            if freshness is not None:
                params["freshness"] = freshness
            if summary is not None:
                params["summary"] = summary
            if include is not None:
                params["include"] = include
            if exclude is not None:
                params["exclude"] = exclude
            if count is not None:
                params["count"] = count

            headers = {
                "Authorization": f"Bearer {self.bocha_api_key.get_secret_value()}",
                "Content-Type": "application/json",
            }

            base_url = self.api_base_url or BOCHA_API_URL
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/v1/web-search", json=params, headers=headers
                ) as res:
                    if res.status == 200:
                        data = await res.text()
                        return data
                    else:
                        error_text = await res.text()
                        raise Exception(f"Error {res.status}: {error_text}")

        results_json_str = await fetch()
        result = json.loads(results_json_str)

        # Check if the API returned an error in the response body
        if result.get("code") != 200:
            error_message = result.get("msg", "Unknown error")
            raise ValueError(f"API Error: {error_message}")

        # Return structured response
        # Parse the data portion into a SearchResponse object
        data = result.get("data", {})
        return SearchResponse(**data)
