"""Safe, non-mutating destination planning."""

from pathlib import Path

from slothsort.classifier import ClassificationResult
from slothsort.scanner import FileMetadata


def _is_within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def plan_destination(
    file: FileMetadata, classification: ClassificationResult, root_dir: str | Path
) -> Path:
    """Return a non-overwriting destination path without moving any files."""

    root = Path(root_dir).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Root path is not a directory: {root}")

    filename = Path(file.filename)
    if filename.name != file.filename or filename.is_absolute():
        raise ValueError(f"Unsafe filename: {file.filename}")

    destination_dir = root / classification.category
    destination = destination_dir / filename
    if not _is_within_root(destination.resolve(strict=False), root):
        raise ValueError("Proposed destination escapes the root directory")

    if not destination.exists():
        return destination

    stem = filename.stem
    suffix = filename.suffix
    counter = 1
    while True:
        candidate = destination_dir / f"{stem}_{counter}{suffix}"
        if not _is_within_root(candidate.resolve(strict=False), root):
            raise ValueError("Proposed destination escapes the root directory")
        if not candidate.exists():
            return candidate
        counter += 1
