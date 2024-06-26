"""Constants for OpenAI TTS custom component"""

DOMAIN = "openai_speech"
CONF_NAME = "name"
NAME = "Open AI Speech"
CONF_BASE_URL = "base_url"
CONF_API_KEY = "api_key"
CONF_TTS_MODEL = "tts_model"
CONF_TTS_VOICE = "tts_voice"
CONF_TTS_SPEED = "tts_speed"
TTS_SPEED = 1.0
CONF_STT_MODEL = "stt_model"
CONF_STT_DEFAULT_LANG = "stt_default_lang"
CONF_STT_TEMPERATURE = "stt_temperature"
CONF_STT_PROMPT = "stt_prompt"
STT_MODEL = "whisper-1"
STT_DEFAULT_LANG = "en-US"
STT_TEMPERATURE = 0
TTS_MODELS = ["tts-1", "tts-1-hd"]
TTS_VOICES = [
    {"value": "alloy", "label": "Alloy"},
    {"value": "echo", "label": "Echo"},
    {"value": "fable", "label": "Fable"},
    {"value": "onyx", "label": "Onyx"},
    {"value": "nova", "label": "Nova"},
    {"value": "shimmer", "label": "Shimmer"},
]
URL = "https://api.openai.com/v1"
