"""Healthchecks.io integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "healthchecks"


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""
    hass.data[DOMAIN] = {"temperature": 42}
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)
    return True
