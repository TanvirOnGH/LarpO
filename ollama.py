import requests
import json
from utils import get_cores
from config import ConfigReader


class OllamaClient:
    def __init__(self, config_filename="config.ini"):
        self.config_reader = ConfigReader(filename=config_filename)
        self.load_settings()

    def load_settings(self):
        self.protocol = self.config_reader.get_setting("Ollama", "protocol")
        self.url = self.config_reader.get_setting("Ollama", "url")
        self.port = self.config_reader.get_setting("Ollama", "port")
        self.post = self.config_reader.get_setting("Ollama", "post")

        self.model = self.config_reader.get_setting("Model", "name")
        self.seed = self.config_reader.get_setting("Model", "seed", as_type=int)
        self.temperature = self.config_reader.get_setting(
            "Model", "temperature", as_type=float
        )
        self.num_ctx = self.config_reader.get_setting("Model", "num_ctx", as_type=int)

        # It is recommended to set this value to the number of physical CPU cores
        # as opposed to the logical number of cores
        self.num_thread = self.config_reader.get_setting(
            "Model", "num_thread", as_type=int, default=get_cores(logical=False)
        )

    def model_response(self, prompt, stream=False, raw=False):
        url = f"{self.protocol}://{self.url}:{self.port}/api/{self.post}"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "raw": raw,
            # TODO: Implement all options
            "options": {
                "seed": self.seed,
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
                "num_thread": self.num_thread,
            },
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, data=json.dumps(data), headers=headers)
        parsed_response = json.loads(response.text)

        return parsed_response.get("response", "Error: No response found!")
