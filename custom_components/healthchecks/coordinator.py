"""DataUpdateCoordinator for the Healthchecks.io integration."""
from __future__ import annotations

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import Check, UnauthorizedError, check_id, list_checks
from .const import CONF_SLUG, CONF_TAG, DOMAIN, LOGGER, SCAN_INTERVAL


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
            checks = await list_checks(
                session=self.session,
                api_key=self.config_entry.data[CONF_API_KEY],
                slug=self.config_entry.data.get(CONF_SLUG),
                tag=self.config_entry.data.get(CONF_TAG),
            )
            return {check_id(c): c for c in checks}
        except UnauthorizedError:
            raise ConfigEntryAuthFailed()
