from unittest.mock import Mock

from slothsort.classifier import ClassificationResult, classify_file
from slothsort.scanner import FileMetadata


def test_classify_file_builds_prompt_and_validates_response() -> None:
    client = Mock()
    client.generate.return_value = {"category": "Images", "confidence": 0.85}
    file = FileMetadata("holiday.jpg", ".jpg", 10, "/tmp/holiday.jpg")

    result = classify_file(file, client)

    assert result == ClassificationResult("Images", 0.85)
    prompt = client.generate.call_args.args[0]
    assert "holiday.jpg" in prompt
    assert ".jpg" in prompt
    assert "Return only a JSON object" in prompt


def test_classify_file_defaults_invalid_category_and_confidence() -> None:
    client = Mock()
    client.generate.return_value = {"category": "Outside", "confidence": 2}
    file = FileMetadata("notes.txt", ".txt", 10, "/tmp/notes.txt")

    assert classify_file(file, client) == ClassificationResult("Other", 0.0)
