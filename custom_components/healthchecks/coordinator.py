"""DataUpdateCoordinator for the Healthchecks.io integration."""
from __future__ import annotations

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import (
    Check,
    UnauthorizedError,
    check_id,
    list_checks,
    pause_check,
    resume_check,
)
from .config_flow import ConfigEntityData
from .const import DOMAIN, LOGGER, SCAN_INTERVAL


class HealthchecksDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Check]]):
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

    async def _async_update_data(self) -> dict[str, Check]:
        try:
            data: ConfigEntityData = self.config_entry.data
            checks = await list_checks(
                session=self.session,
                api_url=data["api_url"],
                api_key=data["api_key"],
                slug=data.get("slug"),
                tag=data.get("tag"),
            )
            return {check_id(c): c for c in checks}
        except UnauthorizedError:
            raise ConfigEntryAuthFailed()

    async def pause_check(self, check: Check) -> None:
        if "pause_url" not in check:
            raise ConfigEntryAuthFailed()

        data: ConfigEntityData = self.config_entry.data
        await pause_check(
            session=self.session,
            check=check,
            api_key=data["api_key"],
        )
        await self.async_refresh()

    async def resume_check(self, check: Check) -> None:
        if "resume_url" not in check:
            raise ConfigEntryAuthFailed()

        data: ConfigEntityData = self.config_entry.data
        await resume_check(
            session=self.session,
            check=check,
            api_key=data["api_key"],
        )
        await self.async_refresh()
