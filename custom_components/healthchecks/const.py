"""Constants for the Healthchecks.io integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Final

DOMAIN: Final = "healthchecks"

DEFAULT_API_URL = "https://healthchecks.io"

LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(minutes=1)

CONF_API_URL: Final = "api_url"
CONF_NAME: Final = "name"
CONF_TAG: Final = "tag"
CONF_SLUG: Final = "slug"
