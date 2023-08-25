"""Implementation of main client."""
from typing import Any

import aiohttp
import requests

try:
    from loguru import logger
except ModuleNotFoundError:
    import logging

    logger = logging.getLogger()

from fitbit_web import api, auth, utils

TIMEOUT: float = 2


class Client(api.FitbitWebApi):
    """Fitbit WebAPI client."""

    def __init__(self, tokens: auth.AuthTokens) -> None:
        """Create a client using the given auth tokens."""
        self.__tokens = tokens


    def _get(
        self,
        url: str,
        param_kwargs: dict[str, Any] | None = None,
        query_kwargs: dict[str, Any] | None = None,
    ):
        url = utils.format_url(url, param_kwargs, query_kwargs)
        logger.debug(f"GETting from Fitbit WebAPI: {url}")
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {self.__tokens.access_token}",
                "Accept": "application/json",
            },
            timeout=TIMEOUT,
        )
        logger.debug(f"Got status code {response.status_code}")
        if response.status_code == 401:
            logger.debug(f"Refreshing token...")
            self.__tokens = self.__tokens.refresh()
            logger.debug(f"GETting from Fitbit WebAPI: {url}")
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {self.__tokens.access_token}",
                    "Accept": "application/json",
                },
                timeout=TIMEOUT,
            )

        if response.status_code != 200:
            raise Exception(response.text)
        return response.json()

    async def _aget(
        self,
        url: str,
        param_kwargs: dict[str, Any] | None = None,
        query_kwargs: dict[str, Any] | None = None,
    ):

        url = utils.format_url(url, param_kwargs, query_kwargs)
        logger.debug(f"GETting from Fitbit WebAPI: {url}")
        async with aiohttp.ClientSession() as session:
            
            async with session.get(
                url,
                headers={
                    "Authorization": f"Bearer {self.__tokens.access_token}",
                    "Accept": "application/json",
                },
                timeout=TIMEOUT,
            ) as response:
                logger.debug(f"Got status code {response.status}")
                if response.status == 401:
                    logger.debug(f"Refreshing token...")
                    self.__tokens = self.__tokens.refresh()
                    logger.debug(f"GETting from Fitbit WebAPI: {url}")
                    async with session.get(
                        url,
                        headers={
                            "Authorization": f"Bearer {self.__tokens.access_token}",
                            "Accept": "application/json",
                        },
                        timeout=TIMEOUT,
                    ) as response:
                        if response.status != 200:
                            raise Exception(response.text)
                        else:
                            return await response.json()
                return await response.json()
