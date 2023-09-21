"""Diagnostics support for Healthchecks.io."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from .const import CONF_NAME, DOMAIN
from .coordinator import HealthchecksDataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: HealthchecksDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    return list(coordinator.data.values())
