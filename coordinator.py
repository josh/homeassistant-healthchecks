"""DataUpdateCoordinator for the Healthchecks.io integration."""
from __future__ import annotations

from datetime import timedelta
from typing import TypedDict

import aiohttp
import async_timeout
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER


class Check(TypedDict):
    name: str
    slug: str
    tags: str
    desc: str
    grace: int
    n_pings: int
    status: str
    started: bool
    last_ping: str
    next_ping: str
    manual_resume: bool
    methods: str
    start_kw: str
    success_kw: str
    failure_kw: str
    filter_subject: bool
    filter_body: bool
    unique_key: str
    timeout: int


class ChecksDataUpdateCoordinator(DataUpdateCoordinator[list[Check]]):
    """Data update coordinator for Healthchecks.io."""

    _session: aiohttp.ClientSession
    _api_key: str
    _slug: str | None
    _tag: str | list[str] | None

    def __init__(
        self,
        hass,
        api_key: str,
        slug: str | None = None,
        tag: str | list[str] | None = None,
    ):
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=300),
        )
        self._session = async_get_clientsession(hass)
        self._api_key = api_key
        self._slug = slug
        self._tag = tag

    async def _async_update_data(self) -> list[Check]:
        async with async_timeout.timeout(10):
            params = {}
            if self._slug:
                params["slug"] = self._slug
            if self._tag:
                params["tag"] = self._tag
            response = await self._session.request(
                method="GET",
                url="https://healthchecks.io/api/v3/checks/",
                params=params,
                headers={"X-Api-Key": self._api_key},
            )
            # TODO: Handle 401 Unauthorized
            # homeassistant.exceptions.ConfigEntryAuthFailed
            response.raise_for_status()
            data = await response.json()
            assert isinstance(data, dict)
            return data["checks"]
