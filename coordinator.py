"""DataUpdateCoordinator for the Healthchecks.io integration."""
from __future__ import annotations

from typing import NotRequired, TypedDict

import aiohttp
import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_SLUG, CONF_TAG, DOMAIN, LOGGER, SCAN_INTERVAL


class HealthchecksCheck(TypedDict):
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
    unique_key: NotRequired[str]
    last_duration: NotRequired[int]
    ping_url: NotRequired[str]
    update_url: NotRequired[str]
    pause_url: NotRequired[str]
    resume_url: NotRequired[str]
    channels: NotRequired[str]
    timeout: NotRequired[int]


def check_id(check: HealthchecksCheck) -> str:
    if "ping_url" in check:
        return check_uuid(check)
    elif "unique_key" in check:
        return check["unique_key"]
    else:
        return check["slug"]


def check_uuid(check: HealthchecksCheck) -> str:
    return check["ping_url"].split("/")[-1]


class HealthchecksDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, HealthchecksCheck]]
):
    """The Healthchecks.io Data Update Coordinator."""

    session: aiohttp.ClientSession
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.config_entry = entry
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, HealthchecksCheck]:
        async with async_timeout.timeout(10):
            headers = {}
            params = {}

            if api_key := self.config_entry.data.get(CONF_API_KEY):
                headers["X-Api-Key"] = api_key
            if slug := self.config_entry.data.get(CONF_SLUG):
                params["slug"] = slug
            if tag := self.config_entry.data.get(CONF_TAG):
                params["tag"] = tag

            response = await self.session.request(
                method="GET",
                url="https://healthchecks.io/api/v3/checks/",
                params=params,
                headers=headers,
            )

            if response.status == 401:
                raise ConfigEntryAuthFailed()

            response.raise_for_status()
            data = await response.json()

            checks: dict[str, HealthchecksCheck] = {}
            for check in data["checks"]:
                checks[check_id(check)] = check

            return checks
