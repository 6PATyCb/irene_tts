import logging
from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import generate_entity_id
from .const import CONF_URL, DOMAIN, UNIQUE_ID
from homeassistant.exceptions import MaxLengthExceeded

_LOGGER = logging.getLogger(__name__)

from .web_service_client import WebServiceClient  

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Irene Text-to-speech platform via config entry."""
    base_url = config_entry.data[CONF_URL]
    client = WebServiceClient(base_url, verify_ssl=False)

    async_add_entities([CustomTTSEntity(hass, config_entry, client)])


class CustomTTSEntity(TextToSpeechEntity):
    """The custom TTS entity using your WebServiceClient."""
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass, config, client):
        """Initialize TTS entity."""
        self.hass = hass
        self._client = client
        self._config = config
        self._attr_unique_id = config.data.get(UNIQUE_ID)
        self.entity_id = generate_entity_id("tts.custom_tts_{}", self._attr_unique_id, hass=hass)

    @property
    def default_language(self):
        """Return the default language."""
        return "ru"

    @property
    def supported_languages(self):
        """Return the list of supported languages."""
        return ["en", "ru"]

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "model": "IreneTTS_inner_odel",
            "manufacturer": "IreneTTS"
        }

    @property
    def name(self):
        """Return name of entity."""
        return f"{self._config.data[UNIQUE_ID]}"

    def get_tts_audio(self, message, language, options=None):
        """
        Convert a given text to speech and return it as bytes.

        :param message: Текст для преобразования в речь
        :param language: Язык
        :param options: Дополнительные параметры
        :return: Tuple (mime_type, content) или None, если произошла ошибка
        """
        _LOGGER.debug("TTS request received with message: '%s', language: '%s', options: '%s'", message, language, options)
        try:
            if len(message) > 4096:
                raise MaxLengthExceeded

            # Подготовка параметров для GET-запроса
            params = {
                "text": message,
                "language": language,
                "options": options or {}
            }
            _LOGGER.debug("Parameters prepared for TTS request: %s", params)

            # Вызов метода клиента для получения WAV-файла
            mime_type, audio_content = self._client.send_get_request("/api/tts", params=params)

            if audio_content:
                _LOGGER.debug("TTS request successful. Received audio content with MIME type: %s", mime_type)
                return mime_type, audio_content  # Возвращаем MIME-тип и байты аудиофайла
            else:
                _LOGGER.error("No audio content received from the server.")
                return None, None

        except MaxLengthExceeded:
            _LOGGER.error("Maximum length of the message exceeded")
        except Exception as e:
            _LOGGER.error("Unknown Error: %s", e)
        return None, None