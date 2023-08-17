"""Implementation of main client."""
import contextlib
import urllib.parse
from typing import Any, Self

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
        self.__session: aiohttp.ClientSession | None = None

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

    @contextlib.asynccontextmanager
    async def async_client(self):
        """Create a new async manager."""
        self.__session = aiohttp.ClientSession()
        try:
            yield self
        finally:
            await self.__session.close()
            self.__session = None

    async def _aget(
        self,
        url: str,
        param_kwargs: dict[str, Any] | None = None,
        query_kwargs: dict[str, Any] | None = None,
    ):
        if self.__session is None:
            raise RuntimeError(
                "Please create a session using the async with statement. See the README.MD file for more details."
            )
        url = utils.format_url(url, param_kwargs, query_kwargs)
        logger.debug(f"GETting from Fitbit WebAPI: {url}")
        async with self.__session.get(
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
                async with self.__session.get(
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
