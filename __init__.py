"""The Healthchecks.io integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HealthchecksCheck, HealthchecksDataUpdateCoordinator

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
        check: HealthchecksCheck,
        description: EntityDescription,
    ) -> None:
        """Initialize a Healthchecks.io sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self.unique_key = check["unique_key"]  # or uuid
        slug = check["slug"].replace("-", "_")
        self._attr_unique_id = f"{slug}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        check = self.coordinator.data[self.unique_key]

        return DeviceInfo(
            configuration_url=f"https://healthchecks.io/checks/{check['unique_key']}/details/",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, check["unique_key"])},
            manufacturer="Healthchecks.io",
            name=check["name"],
        )
