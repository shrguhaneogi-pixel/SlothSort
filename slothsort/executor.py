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


def _move_from_item(item: ApprovedMove | Mapping[str, object]) -> ApprovedMove:
    if isinstance(item, ApprovedMove):
        return item
    try:
        source = item["source"]
        destination = item["destination"]
    except KeyError as error:
        raise ValueError(f"Move is missing {error.args[0]}") from error
    if not isinstance(source, (str, Path)) or not isinstance(
        destination, (str, Path)
    ):
        raise ValueError("Move source and destination must be paths")
    return ApprovedMove(Path(source), Path(destination))


def _label(move: ApprovedMove) -> str:
    return f"{move.source} -> {move.destination}"


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
