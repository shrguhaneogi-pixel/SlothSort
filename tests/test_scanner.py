from pathlib import Path

from slothsort.scanner import FileMetadata, scan_directory


def test_scan_directory_returns_only_eligible_direct_files(tmp_path: Path) -> None:
    (tmp_path / "report.txt").write_text("report")
    (tmp_path / "photo.jpg").write_bytes(b"image data")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "ignored.txt").write_text("nested")
    (tmp_path / ".hidden.txt").write_text("hidden")

    scanned_files = scan_directory(tmp_path)

    assert scanned_files == [
        FileMetadata(
            filename="photo.jpg",
            extension=".jpg",
            size=10,
            absolute_path=(tmp_path / "photo.jpg").resolve(),
        ),
        FileMetadata(
            filename="report.txt",
            extension=".txt",
            size=6,
            absolute_path=(tmp_path / "report.txt").resolve(),
        ),
    ]
