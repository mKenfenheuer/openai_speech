"""Config flow for OpenAI speech custom component."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
import logging

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    selector,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.typing import UNDEFINED

from .const import (
    CONF_NAME,
    NAME,
    CONF_BASE_URL,
    CONF_API_KEY,
    CONF_TTS_MODEL,
    CONF_TTS_VOICE,
    CONF_TTS_SPEED,
    TTS_SPEED,
    CONF_STT_MODEL,
    CONF_STT_DEFAULT_LANG,
    CONF_STT_TEMPERATURE,
    CONF_STT_PROMPT,
    STT_DEFAULT_LANG,
    STT_MODEL,
    STT_TEMPERATURE,
    DOMAIN,
    TTS_MODELS,
    TTS_VOICES,
    URL,
)

_LOGGER = logging.getLogger(__name__)


class OpenAITTSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow ."""

    VERSION = 1

    def generate_schema(self):
        """Geneate Schema."""
        return {
            vol.Required(CONF_NAME, default=NAME): str,
            vol.Required(CONF_BASE_URL, default=URL): str,
            vol.Required(CONF_API_KEY): str,
            vol.Optional(CONF_TTS_SPEED, default=TTS_SPEED): vol.All(
                vol.Coerce(float), vol.Range(min=0, min_included=False)
            ),
            vol.Required(CONF_TTS_MODEL, default=TTS_MODELS[0]): SelectSelector(
                SelectSelectorConfig(
                    options=TTS_MODELS,
                    mode=SelectSelectorMode.DROPDOWN,
                    sort=True,
                    custom_value=True,
                )
            ),
            vol.Required(CONF_TTS_VOICE, default=TTS_VOICES[0]): SelectSelector(
                SelectSelectorConfig(
                    options=TTS_VOICES,
                    mode=SelectSelectorMode.DROPDOWN,
                    sort=True,
                    custom_value=True,
                )
            ),
            vol.Required(CONF_STT_DEFAULT_LANG, default=STT_DEFAULT_LANG): str,
            vol.Required(CONF_STT_MODEL, default=STT_MODEL): str,
            vol.Optional(CONF_STT_PROMPT): str,
            vol.Optional(CONF_STT_TEMPERATURE, default=STT_TEMPERATURE): vol.Coerce(
                float
            ),
        }

    def generate_schema(self, config_entry: ConfigEntry):
        """Geneate Schema."""

        data_schema = {
            vol.Required(
                CONF_NAME, default=config_entry.data.get(CONF_NAME, NAME)
            ): str,
            vol.Required(
                CONF_BASE_URL, default=config_entry.data.get(CONF_BASE_URL, URL)
            ): str,
            vol.Required(
                CONF_API_KEY,
                default=config_entry.data.get(CONF_API_KEY, UNDEFINED),
            ): str,
            vol.Optional(
                CONF_TTS_SPEED,
                default=config_entry.data.get(CONF_TTS_SPEED, TTS_SPEED),
            ): vol.All(vol.Coerce(float), vol.Range(min=0, min_included=False)),
            vol.Required(
                CONF_TTS_MODEL,
                default=config_entry.data.get(CONF_TTS_MODEL, TTS_MODELS[0]),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=TTS_MODELS,
                    mode=SelectSelectorMode.DROPDOWN,
                    sort=True,
                    custom_value=True,
                )
            ),
            vol.Required(
                CONF_TTS_VOICE,
                default=config_entry.data.get(
                    CONF_TTS_VOICE, TTS_VOICES[0].get("value")
                ),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=TTS_VOICES,
                    mode=SelectSelectorMode.DROPDOWN,
                    sort=True,
                    custom_value=True,
                )
            ),
            vol.Required(
                CONF_STT_DEFAULT_LANG,
                default=config_entry.data.get(CONF_STT_DEFAULT_LANG, STT_DEFAULT_LANG),
            ): str,
            vol.Required(
                CONF_STT_MODEL,
                default=config_entry.data.get(CONF_STT_MODEL, STT_MODEL),
            ): str,
        }

        if config_entry.data.get(CONF_STT_PROMPT, None) is None:
            data_schema[vol.Optional(CONF_STT_PROMPT)] = str
        else:
            data_schema[
                vol.Optional(
                    CONF_STT_PROMPT,
                    default=config_entry.data.get(CONF_STT_PROMPT, None),
                )
            ] = str

        if config_entry.data.get(CONF_STT_TEMPERATURE, None) is None:
            data_schema[vol.Optional(CONF_STT_TEMPERATURE, default=STT_TEMPERATURE)] = (
                vol.Coerce(float)
            )
        else:
            data_schema[
                vol.Optional(
                    CONF_STT_TEMPERATURE,
                    default=config_entry.data.get(CONF_STT_TEMPERATURE, None),
                )
            ] = vol.Coerce(float)

        return data_schema

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        config = self.hass.config_entries.async_get_entry(self.context["entry_id"])

        data_schema = self.generate_schema(config)

        errors = {}

        if user_input is not None:
            try:
                self.hass.config_entries.async_update_entry(
                    entry=config, data=user_input
                )
                await self.hass.config_entries.async_reload(config.entry_id)
                return self.async_abort(reason="reconfigure_successful")
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unknown exception.")
                errors["base"] = "Unknown exception."

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(data_schema),
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""

        errors = {}

        data_schema = self.generate_schema()

        if user_input is not None:
            try:
                self._async_abort_entries_match(
                    {CONF_TTS_VOICE: user_input[CONF_TTS_VOICE]}
                )
                return self.async_create_entry(
                    id="openai_speech", title="OpenAI Speech", data=user_input
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unknown exception.")
                errors["base"] = "Unknown exception."

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema))


class WrongAPIKey(HomeAssistantError):
    """Error to indicate no or wrong API key."""
