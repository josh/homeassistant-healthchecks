"""Platform for sensor integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import Check, ChecksDataUpdateCoordinator

CONF_SLUG = "slug"
CONF_TAG = "tag"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional("slug"): cv.string,
        vol.Optional("tag"): vol.Any(cv.string, vol.All(cv.ensure_list, [cv.string])),
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up an integration platform async."""

    # if discovery_info is None:
    #     return

    api_key = config[CONF_API_KEY]
    tag = config.get("tag", None)
    slug = config.get("slug", None)

    coordinator = ChecksDataUpdateCoordinator(hass, api_key=api_key, slug=slug, tag=tag)
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for check in coordinator.data:
        sensors.append(CheckStatusSensor(coordinator, check))

    async_add_entities(sensors, update_before_add=True)


async def async_setup_entry(
    self,
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up an integration platform from a config entry."""
    pass


class CheckStatusSensor(CoordinatorEntity[ChecksDataUpdateCoordinator], SensorEntity):
    _attr_attribution = "Data provided by Healthchecks.io"
    _attr_has_entity_name = True

    _attr_icon = "mdi:server"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["new", "up", "grace", "down", "paused"]
    _attr_device_info = DeviceInfo(
        identifiers={"healthchecks"},
        name="Healtchecks",
    )

    def __init__(self, coordinator: ChecksDataUpdateCoordinator, check: Check) -> None:
        super().__init__(coordinator)
        self._unique_key = check["unique_key"]
        self._attr_unique_id = self._unique_key
        self._update_check(check)

    @callback
    def _handle_coordinator_update(self) -> None:
        for check in self.coordinator.data:
            if check["unique_key"] == self._unique_key:
                self._update_check(check)
        self.async_write_ha_state()

    def _update_check(self, check: Check) -> None:
        self._attr_name = check["name"]
        self._attr_native_value = check["status"]
        self._attr_extra_state_attributes = {
            "name": check["name"],
            "slug": check["slug"],
            "tags": check["tags"],
            "desc": check["desc"],
            "grace": check["grace"],
            "n_pings": check["n_pings"],
            "last_ping": check["last_ping"],
            "next_ping": check["next_ping"],
            "unique_key": check["unique_key"],
        }
