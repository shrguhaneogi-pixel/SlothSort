"""HTTP adapter for the local Ollama generate API."""

import json
from json import JSONDecodeError
from typing import Any

import requests


OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"


class OllamaClientError(RuntimeError):
    """Base error for local Ollama client failures."""


class OllamaConnectionError(OllamaClientError):
    """Raised when the local Ollama service cannot be reached."""


class OllamaTimeoutError(OllamaClientError):
    """Raised when Ollama does not respond before the timeout."""


class OllamaResponseError(OllamaClientError):
    """Raised when Ollama returns an invalid or unsuccessful response."""


class OllamaClient:
    """Small, strict client for local Ollama model inference."""

    def __init__(self, model: str, timeout: float = 30.0) -> None:
        if not model:
            raise ValueError("An Ollama model name is required")
        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero")

        self.model = model
        self.timeout = timeout

    def verify_service(self) -> list[dict[str, Any]]:
        """Verify Ollama is reachable and return its installed model tags."""

        try:
            response = requests.get(OLLAMA_TAGS_URL, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.ConnectionError as error:
            raise OllamaConnectionError(
                "Could not connect to Ollama at http://localhost:11434"
            ) from error
        except requests.Timeout as error:
            raise OllamaTimeoutError("Ollama service check timed out") from error
        except JSONDecodeError as error:
            raise OllamaResponseError(
                "Ollama returned invalid JSON while listing models"
            ) from error
        except requests.RequestException as error:
            raise OllamaResponseError(
                f"Ollama service check failed: {error}"
            ) from error

        models = payload.get("models")
        if not isinstance(models, list):
            raise OllamaResponseError(
                "Ollama model listing did not contain a valid models list"
            )
        return models

    def check_model_installed(self) -> bool:
        """Return whether the configured model is installed locally."""

        models = self.verify_service()
        return any(
            isinstance(model, dict)
            and model.get("name") == self.model
            for model in models
        )

    def generate(self, prompt: str) -> dict[str, Any]:
        """Generate and decode a JSON response from the configured model."""

        if not prompt:
            raise ValueError("A prompt is required")
        if not self.check_model_installed():
            raise OllamaResponseError(
                f"Ollama model is not installed: {self.model}"
            )

        try:
            response = requests.post(
                OLLAMA_GENERATE_URL,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            generated_content = payload["response"]
            result = json.loads(generated_content)
        except requests.ConnectionError as error:
            raise OllamaConnectionError(
                "Could not connect to Ollama at http://localhost:11434"
            ) from error
        except requests.Timeout as error:
            raise OllamaTimeoutError("Ollama generation timed out") from error
        except JSONDecodeError as error:
            raise OllamaResponseError(
                "Ollama returned invalid JSON for the generated response"
            ) from error
        except (KeyError, TypeError) as error:
            raise OllamaResponseError(
                "Ollama response did not contain a JSON response field"
            ) from error
        except requests.RequestException as error:
            raise OllamaResponseError(
                f"Ollama generation failed: {error}"
            ) from error

        if not isinstance(result, dict):
            raise OllamaResponseError("Generated response must be a JSON object")
        return result
