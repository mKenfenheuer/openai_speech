"""Config flow for OpenAI text-to-speech custom component."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
import logging

from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.selector import selector
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_BASE_URL,
    CONF_API_KEY,
    CONF_TTS_MODEL,
    CONF_TTS_VOICE,
    CONF_TTS_SPEED,
    CONF_STT_MODEL,
    CONF_STT_DEFAULT_LANG,
    CONF_STT_TEMPERATURE,
    CONF_STT_PROMPT,
    DOMAIN,
    TTS_MODELS,
    TTS_VOICES,
    URL,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(user_input: dict):
    """Function to validate provided  data"""
    if len(user_input[CONF_API_KEY]) != 56:
        raise WrongAPIKey


class OpenAITTSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow ."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""

        data_schema = {
            vol.Required(CONF_BASE_URL, default=URL): str,
            vol.Required(CONF_API_KEY): str,
            vol.Optional(CONF_TTS_SPEED, default=1): float,
            CONF_TTS_MODEL: selector(
                {
                    "select": {
                        "options": TTS_MODELS,
                        "mode": "dropdown",
                        "sort": True,
                        "custom_value": False,
                    }
                }
            ),
            CONF_TTS_VOICE: selector(
                {
                    "select": {
                        "options": TTS_VOICES,
                        "mode": "dropdown",
                        "sort": True,
                        "custom_value": False,
                    }
                }
            ),
            vol.Required(CONF_STT_DEFAULT_LANG, default="en"): str,
            vol.Required(CONF_STT_MODEL, default="whisper-1"): str,
            vol.Optional(CONF_STT_PROMPT): str,
            vol.Optional(CONF_STT_TEMPERATURE): float,
        }

        errors = {}

        if user_input is not None:
            try:
                self._async_abort_entries_match(
                    {CONF_TTS_VOICE: user_input[CONF_TTS_VOICE]}
                )
                await validate_input(user_input)
                return self.async_create_entry(title="OpenAI Speech", data=user_input)
            except WrongAPIKey:
                _LOGGER.exception("Wrong or no API key provided.")
                errors[CONF_API_KEY] = "wrong_api_key"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unknown exception.")
                errors["base"] = "Unknown exception."

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema))


class WrongAPIKey(HomeAssistantError):
    """Error to indicate no or wrong API key."""
