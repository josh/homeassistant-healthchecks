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
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HealthchecksEntity
from .api import STATUSES, Check
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Healthchecks.io sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service("ping", {}, "ping")

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

    value_fn: Callable[[Check], datetime | str | None]


@dataclass
class HealthchecksSensorEntityDescription(
    SensorEntityDescription, HealthchecksSensorEntityDescriptionMixin
):
    """Describes a Healthchecks.io sensor entity."""


class HealthchecksSensorEntity(HealthchecksEntity, SensorEntity):
    """Defines a Healthchecks.io sensor."""

    entity_description: HealthchecksSensorEntityDescription

    @property
    def native_value(self) -> datetime | str | None:
        """Return the state of the sensor."""
        check: Check = self.coordinator.data[self._id]
        return self.entity_description.value_fn(check)

    async def ping(self):
        check: Check = self.coordinator.data[self._id]
        await self.coordinator.ping_check(check)


SENSORS: tuple[HealthchecksSensorEntityDescription, ...] = (
    HealthchecksSensorEntityDescription(
        key="status",
        translation_key="status",
        icon="mdi:server",
        device_class=SensorDeviceClass.ENUM,
        options=STATUSES,
        value_fn=lambda check: check["status"],
    ),
    HealthchecksSensorEntityDescription(
        key="timeout",
        translation_key="timeout",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda check: check.get("timeout"),
    ),
    HealthchecksSensorEntityDescription(
        key="grace",
        translation_key="grace",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda check: check["grace"],
    ),
    HealthchecksSensorEntityDescription(
        key="n_pings",
        translation_key="n_pings",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement="pings",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda check: check["n_pings"],
    ),
    HealthchecksSensorEntityDescription(
        key="last_ping",
        translation_key="last_ping",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda check: _parse_timestamp(check["last_ping"]),
    ),
    HealthchecksSensorEntityDescription(
        key="next_ping",
        translation_key="next_ping",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda check: _parse_timestamp(check["next_ping"]),
    ),
    HealthchecksSensorEntityDescription(
        key="last_duration",
        translation_key="last_duration",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda check: check.get("last_duration"),
    ),
)


def _parse_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value)
