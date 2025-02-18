import requests
import logging
import warnings

_LOGGER = logging.getLogger(__name__)

class WebServiceClient:
    def __init__(self, base_url, verify_ssl=True):
        """
        Инициализация клиента.
        
        :param base_url: Базовый URL веб-сервиса (например, "https://example.com/api")
        """
        self.base_url = base_url
        self.verify_ssl = verify_ssl

        if not verify_ssl:
            # Отключение предупреждений о непроверенных сертификатах
            warnings.filterwarnings("ignore", message="Unverified HTTPS request")
        
    def send_get_request(self, endpoint, params=None):
        """
        Отправка GET-запроса к указанному эндпоинту и получение WAV-файла как bytes.
        
        :param endpoint: Конечная точка (endpoint) API (например, "/generate_wav")
        :param params: Параметры запроса (например, {"text": "Hello, world!"})
        :return: Tuple (mime_type, content) где mime_type - тип контента, content - байты WAV-файла
        """
        _LOGGER.debug("send_get_request received with endpoint: '%s', params: '%s'", endpoint, params)
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params, verify=self.verify_ssl)
            
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "application/octet-stream")
                if "audio/wav" in content_type or "audio/x-wav" in content_type:
                    return "wav", response.content 
                else:
                    raise Exception(f"Unexpected content type: {content_type}")
            else:
                raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred while sending the request: {e}")

