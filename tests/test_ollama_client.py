from unittest.mock import Mock, patch

import pytest
import requests

from slothsort.ollama_client import (
    OLLAMA_GENERATE_URL,
    OLLAMA_TAGS_URL,
    OllamaClient,
    OllamaConnectionError,
    OllamaResponseError,
    OllamaTimeoutError,
)


def ollama_tags_response() -> Mock:
    response = Mock()
    response.json.return_value = {"models": [{"name": "gemma3:1b"}]}
    return response


@patch("slothsort.ollama_client.requests.post")
@patch("slothsort.ollama_client.requests.get")
def test_generate_returns_json_and_uses_strict_format(
    mock_get: Mock, mock_post: Mock
) -> None:
    mock_get.return_value = ollama_tags_response()
    generated_response = Mock()
    generated_response.json.return_value = {"response": '{"category": "Documents"}'}
    mock_post.return_value = generated_response

    result = OllamaClient("gemma3:1b").generate("Classify this file")

    assert result == {"category": "Documents"}
    mock_get.assert_called_once_with(OLLAMA_TAGS_URL, timeout=30.0)
    mock_post.assert_called_once_with(
        OLLAMA_GENERATE_URL,
        json={
            "model": "gemma3:1b",
            "prompt": "Classify this file",
            "stream": False,
            "format": "json",
        },
        timeout=30.0,
    )


@patch("slothsort.ollama_client.requests.get")
def test_verify_service_raises_for_timeout(mock_get: Mock) -> None:
    mock_get.side_effect = requests.Timeout("timed out")

    with pytest.raises(OllamaTimeoutError, match="timed out"):
        OllamaClient("gemma3:1b").verify_service()


@patch("slothsort.ollama_client.requests.get")
def test_verify_service_raises_for_connection_error(mock_get: Mock) -> None:
    mock_get.side_effect = requests.ConnectionError("connection refused")

    with pytest.raises(OllamaConnectionError, match="Could not connect"):
        OllamaClient("gemma3:1b").verify_service()


@patch("slothsort.ollama_client.requests.get")
def test_verify_service_raises_for_invalid_json(mock_get: Mock) -> None:
    response = Mock()
    response.json.side_effect = requests.exceptions.JSONDecodeError(
        "invalid JSON", "", 0
    )
    mock_get.return_value = response

    with pytest.raises(OllamaResponseError, match="invalid JSON"):
        OllamaClient("gemma3:1b").verify_service()
