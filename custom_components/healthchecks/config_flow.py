"""Config flow for Healthchecks.io integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import API_URL, UnauthorizedError, check_api_key
from .const import CONF_API_URL, CONF_NAME, CONF_SLUG, CONF_TAG, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_API_URL, default=API_URL): cv.string,
        vol.Optional(CONF_SLUG): cv.string,
        vol.Optional(CONF_TAG): cv.string,
    }
)


class HealthchecksConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Healthchecks.io."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)
                await check_api_key(
                    session=session,
                    api_url=user_input.get(CONF_API_URL, API_URL),
                    api_key=user_input[CONF_API_KEY],
                )
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
            except UnauthorizedError:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
