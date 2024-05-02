"""
Support for Whisper API STT.
"""

from typing import AsyncIterable
import aiohttp
import os
import tempfile
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.tts import CONF_LANG
from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    SpeechToTextEntity,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
)

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
import wave
import io

from .const import (
    CONF_API_KEY,
    CONF_NAME,
    CONF_STT_MODEL,
    CONF_STT_DEFAULT_LANG,
    CONF_STT_TEMPERATURE,
    CONF_STT_PROMPT,
    CONF_BASE_URL,
    NAME,
    STT_MODEL,
    STT_DEFAULT_LANG,
    URL,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenAI Text-to-speech platform via config entry."""
    engine = OpenAISTTProvider(
        hass,
        config_entry.data.get(CONF_API_KEY),
        config_entry.data.get(CONF_STT_DEFAULT_LANG, STT_DEFAULT_LANG),
        config_entry.data.get(CONF_STT_MODEL, STT_MODEL),
        config_entry.data.get(CONF_BASE_URL, URL),
        config_entry.data.get(CONF_STT_PROMPT, None),
        config_entry.data.get(CONF_STT_TEMPERATURE, 0),
        config_entry.data.get(CONF_NAME, NAME),
    )
    async_add_entities([engine])


class OpenAISTTProvider(SpeechToTextEntity):
    """The Whisper API STT provider."""

    def __init__(self, hass, api_key, lang, model, url, prompt, temperature, name):
        """Initialize Whisper API STT provider."""
        self.hass = hass
        self._api_key = api_key
        self._language = lang
        self._model = model
        self._url = url
        self._prompt = prompt
        self._temperature = temperature
        self._name = name
        self._attr_name = f"{self._name} Speech-to-Text Service"

    @property
    def device_info(self):
        return {
            "identifiers": {self._name},
            "name": f"{self._name} Speech Services",
            "manufacturer": "OpenAI",
        }

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return self._language.split(",")[0]

    @property
    def supported_languages(self) -> list[str]:
        """Return the list of supported languages."""
        return self._language.split(",")

    @property
    def supported_formats(self) -> list[AudioFormats]:
        """Return a list of supported formats."""
        return [AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        """Return a list of supported codecs."""
        return [AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        """Return a list of supported bitrates."""
        return [AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        """Return a list of supported samplerates."""
        return [AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        """Return a list of supported channels."""
        return [AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> SpeechResult:
        data = b""
        async for chunk in stream:
            data += chunk

        if not data:
            return SpeechResult("", SpeechResultState.ERROR)

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                with wave.open(temp_file, "wb") as wav_file:
                    wav_file.setnchannels(metadata.channel)
                    wav_file.setsampwidth(2)  # 2 bytes per sample
                    wav_file.setframerate(metadata.sample_rate)
                    wav_file.writeframes(data)
                temp_file_path = temp_file.name

            url = self._url or URL

            url = url + "/audio/transcriptions"

            headers = {
                "Authorization": f"Bearer {self._api_key}",
            }

            file_to_send = open(temp_file_path, "rb")
            form = aiohttp.FormData()
            form.add_field(
                "file", file_to_send, filename="audio.wav", content_type="audio/wav"
            )
            form.add_field("language", self._language)
            form.add_field("model", self._model)

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form, headers=headers) as response:
                    if response.status == 200:
                        json_response = await response.json()
                        return SpeechResult(
                            json_response["text"], SpeechResultState.SUCCESS
                        )
                    else:
                        text = await response.text()
                        return SpeechResult("", SpeechResultState.ERROR)
        except Exception as e:
            return SpeechResult("", SpeechResultState.ERROR)
        finally:
            if "file_to_send" in locals():
                file_to_send.close()
            if temp_file_path:
                os.remove(temp_file_path)
