"""The Healthchecks.io integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import Check, check_id, check_uuid
from .const import DOMAIN
from .coordinator import HealthchecksDataUpdateCoordinator

PLATFORMS = [
    # Platform.BINARY_SENSOR,
    Platform.SENSOR
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Healthchecks.io from a config entry."""

    coordinator = HealthchecksDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Healthchecks.oi config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        del hass.data[DOMAIN][entry.entry_id]
    return unload_ok


class HealthchecksEntity(CoordinatorEntity[HealthchecksDataUpdateCoordinator]):
    """Defines a Healthchecks.io base entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        coordinator: HealthchecksDataUpdateCoordinator,
        check: Check,
        description: EntityDescription,
    ) -> None:
        """Initialize a Healthchecks.io sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._id = check_id(check)
        self._attr_unique_id = f"{self._id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        check = self.coordinator.data[self._id]

        configuration_url: str | None = None
        if "ping_url" in check:
            uuid = check_uuid(check)
            configuration_url = f"https://healthchecks.io/checks/{uuid}/details/"

        return DeviceInfo(
            configuration_url=configuration_url,
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._id)},
            manufacturer="Healthchecks.io",
            name=check["name"],
        )
