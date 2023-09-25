"""Constants for the Healthchecks.io integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Final

DOMAIN: Final = "healthchecks"

LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(minutes=1)

CONF_NAME: Final = "name"
CONF_TAG: Final = "tag"
CONF_SLUG: Final = "slug"
