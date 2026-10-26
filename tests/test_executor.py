from pathlib import Path

from slothsort.executor import ApprovedMove, execute_plan


def test_execute_plan_moves_approved_file(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    destination = tmp_path / "Documents" / "source.txt"
    source.write_text("content")

    result = execute_plan([ApprovedMove(source, destination, tmp_path)])

    assert result == {
        "success": [f"{source} -> {destination}"],
        "failed": [],
        "skipped": [],
    }
    assert destination.read_text() == "content"
    assert not source.exists()


def test_execute_plan_skips_existing_destination_without_overwriting(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.txt"
    destination = tmp_path / "Documents" / "source.txt"
    source.write_text("new content")
    destination.parent.mkdir()
    destination.write_text("original content")

    result = execute_plan([ApprovedMove(source, destination, tmp_path)])

    assert result["success"] == []
    assert result["skipped"] == [f"{source} -> {destination}"]
    assert destination.read_text() == "original content"
    assert source.read_text() == "new content"


def test_execute_plan_rejects_symlink_source(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    source = tmp_path / "link.txt"
    destination = tmp_path / "Documents" / "link.txt"
    target.write_text("target")
    source.symlink_to(target)

    result = execute_plan([ApprovedMove(source, destination, tmp_path)])

    assert result["success"] == []
    assert result["skipped"] == [f"{source} -> {destination}"]
    assert source.is_symlink()
    assert not destination.exists()


def test_execute_plan_rejects_symlinked_destination_directory(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.txt"
    outside = tmp_path / "outside"
    destination_dir = tmp_path / "Documents"
    destination = destination_dir / "source.txt"
    source.write_text("content")
    outside.mkdir()
    destination_dir.symlink_to(outside, target_is_directory=True)

    result = execute_plan([ApprovedMove(source, destination, tmp_path)])

    assert result["success"] == []
    assert result["skipped"] == [f"{source} -> {destination}"]
    assert source.exists()
    assert not (outside / "source.txt").exists()
