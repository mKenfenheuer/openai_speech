"""
Setting up TTS entity.
"""

import re
import logging
from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import (
    CONF_API_KEY,
    CONF_NAME,
    CONF_TTS_MODEL,
    CONF_TTS_SPEED,
    CONF_TTS_VOICE,
    DOMAIN,
    CONF_BASE_URL,
    NAME,
)
from .openaitts_engine import OpenAITTSEngine
from homeassistant.exceptions import MaxLengthExceeded

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenAI Text-to-speech platform via config entry."""
    engine = OpenAITTSEngine(
        config_entry.data[CONF_API_KEY],
        config_entry.data[CONF_TTS_VOICE],
        config_entry.data[CONF_TTS_MODEL],
        config_entry.data[CONF_TTS_SPEED],
        config_entry.data[CONF_BASE_URL],
    )
    async_add_entities([OpenAITTSEntity(hass, config_entry, engine)])


class OpenAITTSEntity(TextToSpeechEntity):
    """The OpenAI TTS entity."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def generate_entity_id(self, line: str):
        return re.sub(r"[^a-zA-Z0-9]+", "_", line).lower()

    def __init__(self, hass, config, engine):
        """Initialize TTS entity."""
        self.hass = hass
        self._engine = engine
        self._config = config
        self._name = self._config.data.get(CONF_NAME, NAME)
        self._attr_name = f"{self._name} Text-to-Speech Service"
        self._attr_unique_id = self.generate_entity_id(
            f"{self._name} Text-to-Speech Service"
        )

    @property
    def default_language(self):
        """Return the default language."""
        return "en"

    @property
    def supported_languages(self):
        """Return the list of supported languages."""
        return self._engine.get_supported_langs()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.generate_entity_id(self._name))},
            "name": f"{self._name} Services",
            "manufacturer": "OpenAI",
        }

    def get_tts_audio(self, message, language, options=None):
        """Convert a given text to speech and return it as bytes."""

        try:
            if len(message) > 4096:
                raise MaxLengthExceeded

            speech = self._engine.get_tts(message)

            # The response should contain the audio file content
            return "mp3", speech.content

        except MaxLengthExceeded:
            _LOGGER.error("Maximum length of the message exceeded")

        except Exception as e:
            _LOGGER.error("Unknown Error: %s", e)

        return None, None
