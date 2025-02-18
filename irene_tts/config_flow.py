"""Config flow for Irene text-to-speech custom component."""
from __future__ import annotations
from typing import Any
import voluptuous as vol
import logging
from urllib.parse import urlparse

from homeassistant import data_entry_flow
from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.selector import selector
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_URL, DOMAIN, UNIQUE_ID

_LOGGER = logging.getLogger(__name__)

def generate_unique_id(user_input: dict) -> str:
    """Generate a unique id from user input."""
    parsed_url = urlparse(user_input[CONF_URL])
    parsed_port = 0
    if parsed_url.port is not None:
        parsed_port = parsed_url.port
    elif parsed_url.scheme == 'https':
        parsed_port = 443
    elif parsed_url.scheme == 'http':
        parsed_port = 80 
    return f"{parsed_url.hostname}_{parsed_port}"

async def validate_user_input(user_input: dict):
    """Validate user input fields."""

class IreneTTSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Irene TTS."""
    VERSION = 1
    data_schema = vol.Schema({
        vol.Optional(CONF_URL, default="https://192.168.133.252:5003"): str,
    })

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                await validate_user_input(user_input)
                unique_id = generate_unique_id(user_input)
                user_input[UNIQUE_ID] = unique_id
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"Irene TTS ({unique_id})", data=user_input)
            except data_entry_flow.AbortFlow:
                return self.async_abort(reason="already_configured")
            except HomeAssistantError as e:
                _LOGGER.exception(str(e))
                errors["base"] = str(e)
            except ValueError as e:
                _LOGGER.exception(str(e))
                errors["base"] = str(e)
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception(str(e))
                errors["base"] = "unknown_error"
        return self.async_show_form(step_id="user", data_schema=self.data_schema, errors=errors, description_placeholders=user_input)
