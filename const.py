"""Constants for the Healthchecks.io integration."""
import logging
from datetime import timedelta
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "healthchecks"
PLATFORMS = [Platform.SENSOR]

LOGGER = logging.getLogger(__package__)

COORDINATOR_UPDATE_INTERVAL = timedelta(minutes=5)
