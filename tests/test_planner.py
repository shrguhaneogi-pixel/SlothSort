from pathlib import Path

import pytest

from slothsort.classifier import ClassificationResult
from slothsort.planner import plan_destination
from slothsort.scanner import FileMetadata


def make_file(tmp_path: Path, filename: str = "report.txt") -> FileMetadata:
    source = tmp_path / filename
    source.write_text("content")
    return FileMetadata(filename, source.suffix, source.stat().st_size, source)


def test_plan_destination_proposes_category_path_without_moving_file(
    tmp_path: Path,
) -> None:
    file = make_file(tmp_path)

    destination = plan_destination(
        file, ClassificationResult("Documents", 0.9), tmp_path
    )

    assert destination == tmp_path / "Documents" / "report.txt"
    assert file.absolute_path.exists()
    assert not destination.exists()


def test_plan_destination_uses_counter_when_destination_exists(tmp_path: Path) -> None:
    file = make_file(tmp_path)
    destination_dir = tmp_path / "Documents"
    destination_dir.mkdir()
    (destination_dir / "report.txt").write_text("existing")
    (destination_dir / "report_1.txt").write_text("existing")

    destination = plan_destination(
        file, ClassificationResult("Documents", 0.9), tmp_path
    )

    assert destination == destination_dir / "report_2.txt"
    assert (destination_dir / "report.txt").read_text() == "existing"


def test_plan_destination_rejects_path_traversal_filename(tmp_path: Path) -> None:
    file = FileMetadata("../outside.txt", ".txt", 0, tmp_path / "outside.txt")

    with pytest.raises(ValueError, match="Unsafe filename"):
        plan_destination(file, ClassificationResult("Other", 0.5), tmp_path)
