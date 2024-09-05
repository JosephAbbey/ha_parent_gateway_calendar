"""Config flow for Parent Gateway Calendar."""

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow

from .const import CONF_PARENT_GATEWAY_DOMAIN, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ParentGatewayCalendarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Parent Gateway Calendar."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(
                title="Parent Gateway Calendar",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PARENT_GATEWAY_DOMAIN): str,
                }
            ),
            errors=_errors,
        )
