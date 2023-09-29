"""The Healthchecks.io integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.service import async_extract_entity_ids
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import Check, check_details_url, check_id
from .const import DOMAIN, LOGGER
from .coordinator import HealthchecksDataUpdateCoordinator

PLATFORMS = [
    # Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Healthchecks.io from a config entry."""

    coordinator = HealthchecksDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    @callback
    async def ping(service_call: ServiceCall) -> None:
        entity_ids = await async_extract_entity_ids(hass, service_call)
        for entity_id in entity_ids:
            await ping_entity_id(hass, entity_id)

    hass.services.async_register(DOMAIN, "ping", ping)

    return True


async def ping_entity_id(hass: HomeAssistant, entity_id: str) -> None:
    er = entity_registry.async_get(hass)
    entity = er.async_get(entity_id)
    if not entity:
        LOGGER.warning("entity_id not found: %s", entity_id)
        return

    coordinator = hass.data[DOMAIN].get(entity.config_entry_id)
    if not coordinator:
        LOGGER.warning(
            "missing coordinator for config_entry_id: %s", entity.config_entry_id
        )
        return

    dr = device_registry.async_get(hass)
    device = dr.async_get(entity.device_id)
    if not device:
        LOGGER.warning("device_id not found: %s", entity.device_id)
        return

    identifier = list(device.identifiers)[0]
    domain, id = identifier
    assert domain == DOMAIN

    LOGGER.debug("Found entity_id (%s) -> check uuid (%s)", entity_id, id)
    check = coordinator.data[id]
    await coordinator.ping_check(check)


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
        if "update_url" in check:
            configuration_url = check_details_url(check)

        return DeviceInfo(
            configuration_url=configuration_url,
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._id)},
            manufacturer="Healthchecks.io",
            name=check["name"],
        )
