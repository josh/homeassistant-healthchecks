"""Platform for sensor integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HealthchecksEntity
from .const import DOMAIN
from .coordinator import HealthchecksCheck


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Healthchecks.io sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        HealthchecksSensorEntity(
            coordinator=coordinator,
            check=check,
            description=description,
        )
        for check in coordinator.data.values()
        for description in SENSORS
    )


@dataclass
class HealthchecksSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[HealthchecksCheck], datetime | str | None]


@dataclass
class HealthchecksSensorEntityDescription(
    SensorEntityDescription, HealthchecksSensorEntityDescriptionMixin
):
    """Describes a Healthchecks.io sensor entity."""


class HealthchecksSensorEntity(HealthchecksEntity, SensorEntity):
    """Defines a Tailscale sensor."""

    entity_description: HealthchecksSensorEntityDescription

    @property
    def native_value(self) -> datetime | str | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data[self.unique_key])


SENSORS: tuple[HealthchecksSensorEntityDescription, ...] = (
    HealthchecksSensorEntityDescription(
        key="status",
        translation_key="status",
        icon="mdi:server",
        device_class=SensorDeviceClass.ENUM,
        options=["new", "up", "grace", "down", "paused"],
        value_fn=lambda check: check["status"],
    ),
    HealthchecksSensorEntityDescription(
        key="n_pings",
        translation_key="n_pings",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda check: check["n_pings"],
    ),
    HealthchecksSensorEntityDescription(
        key="last_ping",
        translation_key="last_ping",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda check: datetime.fromisoformat(check["last_ping"]),
    ),
    HealthchecksSensorEntityDescription(
        key="next_ping",
        translation_key="next_ping",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda check: datetime.fromisoformat(check["next_ping"]),
    ),
)
