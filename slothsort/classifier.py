"""File classification using the local Ollama client."""

from dataclasses import dataclass
from typing import Protocol

from slothsort.config import ALLOWED_CATEGORIES
from slothsort.scanner import FileMetadata


class InferenceClient(Protocol):
    """Interface required by the classifier for model inference."""

    def generate(self, prompt: str) -> dict[str, object]:
        ...


@dataclass(frozen=True)
class ClassificationResult:
    """Validated classification returned by the model."""

    category: str
    confidence: float


def build_classification_prompt(file: FileMetadata) -> str:
    """Build a constrained prompt for one file."""

    categories = ", ".join(ALLOWED_CATEGORIES)
    return (
        "Classify this file using only its filename and extension.\n"
        f"Filename: {file.filename}\n"
        f"Extension: {file.extension or '(none)'}\n"
        f"Allowed categories: {categories}\n\n"
        "Return only a JSON object with exactly these keys:\n"
        '- "category": one allowed category\n'
        '- "confidence": a number from 0.0 to 1.0'
    )


def classify_file(
    file: FileMetadata, inference_client: InferenceClient
) -> ClassificationResult:
    """Classify a file and validate the model response."""

    response = inference_client.generate(build_classification_prompt(file))
    category = response.get("category")
    if not isinstance(category, str) or category not in ALLOWED_CATEGORIES:
        category = "Other"

    confidence = response.get("confidence")
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        confidence = 0.0

    return ClassificationResult(category=category, confidence=float(confidence))
