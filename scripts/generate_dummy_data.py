"""Generate empty files for a SlothSort demonstration."""

from pathlib import Path


DEMO_FOLDER = Path(__file__).resolve().parents[1] / "tests" / "demo_folder"
DEMO_FILES = (
    "meeting_notes.txt",
    "tax_return.pdf",
    "family_photo.jpg",
    "vacation_clip.mp4",
    "project_backup.zip",
    "budget_spreadsheet.xlsx",
    "podcast_episode.mp3",
    "scan_document.png",
    "presentation.pptx",
    "readme.md",
)


def main() -> None:
    DEMO_FOLDER.mkdir(parents=True, exist_ok=True)
    for filename in DEMO_FILES:
        (DEMO_FOLDER / filename).touch()
    print(f"Generated {len(DEMO_FILES)} demo files in {DEMO_FOLDER}")


if __name__ == "__main__":
    main()
