"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HealthchecksEntity
from .const import DOMAIN, LOGGER


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Healthchecks.io switch based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    switches = []
    for check in coordinator.data.values():
        if "pause_url" in check:
            switch = HealthchecksPauseSwitchEntity(
                coordinator=coordinator,
                check=check,
                description=PAUSE_SWITCH,
            )
            switches.append(switch)

    async_add_entities(switches)


PAUSE_SWITCH = SwitchEntityDescription(
    key="paused",
    translation_key="paused",
    device_class=SwitchDeviceClass.SWITCH,
    entity_category=EntityCategory.DIAGNOSTIC,
    icon="mdi:pause-circle",
)


class HealthchecksPauseSwitchEntity(HealthchecksEntity, SwitchEntity):
    """Defines a Healthchecks.io pause/resume switch."""

    entity_description: SwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return the state of the switch."""
        check = self.coordinator.data.get(self._id)
        if not check:
            LOGGER.warning("Couldn't load switch for %s", self._id)
            return None
        return check["status"] == "paused"

    async def async_turn_on(self, **kwargs) -> None:
        """Pause check"""
        check = self.coordinator.data.get(self._id)
        if not check:
            LOGGER.warning("Couldn't load switch for %s", self._id)
            return
        await self.coordinator.pause_check(check)

    async def async_turn_off(self, **kwargs) -> None:
        """Resume check"""
        check = self.coordinator.data.get(self._id)
        if not check:
            LOGGER.warning("Couldn't load switch for %s", self._id)
            return
        await self.coordinator.resume_check(check)
