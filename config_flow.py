"""Config flow for Healthchecks.io integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_NAME, CONF_SLUG, CONF_TAG, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
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
            session = async_get_clientsession(self.hass)
            response = await session.request(
                method="GET",
                url="https://healthchecks.io/api/v3/checks/",
                headers={"X-Api-Key": user_input[CONF_API_KEY]},
            )
            if response.status == 200:
                await self.async_set_unique_id(user_input[CONF_NAME])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
            elif response.status == 401:
                errors["base"] = "invalid_auth"
            else:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            description_placeholders={
                "authkeys_url": "https://healthchecks.io/accounts/profile/"
            },
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
