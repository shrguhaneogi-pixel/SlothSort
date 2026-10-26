"""Safety checks and execution for approved file moves."""

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ApprovedMove:
    """A source and destination approved for execution."""

    source: Path
    destination: Path
    root_dir: Path


def _move_from_item(item: ApprovedMove | Mapping[str, object]) -> ApprovedMove:
    if isinstance(item, ApprovedMove):
        return item
    try:
        source = item["source"]
        destination = item["destination"]
        root_dir = item["root_dir"]
    except KeyError as error:
        raise ValueError(f"Move is missing {error.args[0]}") from error
    if not isinstance(source, (str, Path)) or not isinstance(
        destination, (str, Path)
    ) or not isinstance(root_dir, (str, Path)):
        raise ValueError("Move paths must be strings or pathlib.Path objects")
    return ApprovedMove(Path(source), Path(destination), Path(root_dir))


def _label(move: ApprovedMove) -> str:
    return f"{move.source} -> {move.destination}"


def _is_within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _has_symlink_component(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    current = root
    for part in relative_parts:
        current /= part
        if current.is_symlink():
            return True
    return False


def execute_plan(
    approved_moves: Sequence[ApprovedMove | Mapping[str, object]],
) -> dict[str, list[str]]:
    """Execute approved moves with last-moment overwrite and symlink checks."""

    summary: dict[str, list[str]] = {
        "success": [],
        "failed": [],
        "skipped": [],
    }

    for item in approved_moves:
        try:
            move = _move_from_item(item)
        except ValueError as error:
            summary["failed"].append(str(error))
            logger.error("Invalid approved move: %s", error)
            continue

        source = move.source
        destination = move.destination
        label = _label(move)
        root = move.root_dir.expanduser().resolve()

        if not root.is_dir():
            summary["failed"].append(label)
            logger.error("Move root is not a directory: %s", root)
            continue
        source_resolved = source.expanduser().resolve(strict=False)
        destination_resolved = destination.expanduser().resolve(strict=False)
        if not _is_within_root(source_resolved, root) or not _is_within_root(
            destination_resolved, root
        ):
            summary["failed"].append(label)
            logger.error("Move path escapes root: %s", label)
            continue
        if _has_symlink_component(source, root) or _has_symlink_component(
            destination, root
        ):
            summary["skipped"].append(label)
            logger.error("Move path contains a symlink component: %s", label)
            continue
        if not source.exists():
            summary["failed"].append(label)
            logger.error("Source does not exist: %s", source)
            continue
        if source.is_symlink():
            summary["skipped"].append(label)
            logger.error("Refusing to move symlink source: %s", source)
            continue
        if destination.exists():
            summary["skipped"].append(label)
            logger.error("Destination collision; skipping move: %s", destination)
            continue

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            source_resolved = source.expanduser().resolve(strict=False)
            destination_resolved = destination.expanduser().resolve(strict=False)
            if (
                not _is_within_root(source_resolved, root)
                or not _is_within_root(destination_resolved, root)
                or _has_symlink_component(source, root)
                or _has_symlink_component(destination, root)
            ):
                summary["skipped"].append(label)
                logger.error("Move path changed or became unsafe: %s", label)
                continue
            if not source.exists():
                summary["failed"].append(label)
                logger.error("Source disappeared before move: %s", source)
                continue
            if source.is_symlink():
                summary["skipped"].append(label)
                logger.error("Source became a symlink before move: %s", source)
                continue
            if destination.exists():
                summary["skipped"].append(label)
                logger.error(
                    "Destination collision after directory creation; skipping: %s",
                    destination,
                )
                continue
            shutil.move(str(source), str(destination))
        except OSError as error:
            summary["failed"].append(f"{label}: {error}")
            logger.error("Move failed for %s: %s", label, error)
            continue

        summary["success"].append(label)

    return summary
