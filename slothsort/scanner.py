"""Read-only filesystem scanning utilities."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileMetadata:
    """Metadata for an eligible direct child file."""

    filename: str
    extension: str
    size: int
    absolute_path: Path


def scan_directory(directory: str | Path) -> list[FileMetadata]:
    """Return metadata for eligible files directly inside ``directory``.

    The scan is non-recursive and does not modify the filesystem. Hidden files,
    directories, and symbolic links are excluded.
    """

    directory_path = Path(directory).expanduser().resolve()
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory_path}")
    if not directory_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")

    files: list[FileMetadata] = []
    for path in directory_path.iterdir():
        if path.name.startswith(".") or path.is_symlink() or not path.is_file():
            continue

        files.append(
            FileMetadata(
                filename=path.name,
                extension=path.suffix,
                size=path.stat().st_size,
                absolute_path=path.resolve(),
            )
        )

    return sorted(files, key=lambda file: file.filename)
