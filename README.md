# SlothSort

SlothSort is a local-AI file organizer built around the **Slow and Steady**
principle: inspect a small, safe set of files, review every proposed move, and
only execute the moves that you explicitly approve.

The application uses Streamlit for the review interface and a locally running
Ollama Gemma model for filename-based classification. It never automatically
organizes a directory without showing the proposed destinations first.

## Project Description

SlothSort currently provides this workflow:

1. Enter a directory path in the Streamlit interface.
2. Scan only eligible direct child files.
3. Ask the local Gemma model to classify each filename and extension.
4. Review the proposed category and destination in an editable approval table.
5. Approve individual rows and execute only those approved moves.

The supported categories are:

- Work
- Finance
- Documents
- Images
- Media
- Archives
- Other

The scanner and planner are read-only. File changes happen only after the
`Execute Move` action and are guarded against overwriting existing files and
moving symlinked or out-of-root paths.

## Prerequisites

- Python 3.10 or newer
- Ollama installed and available on the local machine
- The `gemma3:1b` Ollama model

The code uses Python's `pathlib` and type-union syntax, so Python 3.10 or newer
is required. Ollama must expose its local API at
`http://localhost:11434`.

## Installation

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull gemma3:1b
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Confirm that Ollama is running and that the model is installed:

```bash
curl http://localhost:11434/api/tags
```

The response should include a model named `gemma3:1b`.

## Usage

Start the Streamlit application:

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually
`http://localhost:8501`.

### Review and execute a plan

1. Enter the absolute or relative path of the directory to scan.
2. Select **Scan and classify**.
3. Review the **Original Name**, **Proposed Category**, and
   **Proposed Destination** columns.
4. Select **Approve** only for the rows you want to move.
5. Select **Execute Move**.

If the directory is invalid, the app displays an **Invalid Directory** error.
If Ollama cannot be reached, the configured model is not installed, or the
local response is invalid, the app displays a **Model Unavailable** error.

The application keeps the current review metadata in Streamlit session state
so ordinary UI interactions do not trigger a new scan or classification.

## Privacy & Offline Guarantee

SlothSort is designed to run locally:

- Files are scanned and moved on the local machine.
- Only filenames and extensions are sent to the local Ollama service for
  classification; file contents are never read or uploaded.
- The Ollama client uses only `http://localhost:11434` for model requests.
- No cloud AI provider, remote storage service, or external upload endpoint is
  configured by this project.
- The application does not send file data off the machine.

Keep Ollama bound to the local host if you require the strongest offline
boundary, and do not replace the configured local endpoint with a remote
service.

## Safety Model

- Scanning is non-recursive and read-only.
- Hidden files, directories, and symbolic links are excluded from scans.
- Model categories are constrained to the application allowlist.
- Invalid model categories become `Other`.
- Proposed destinations are checked to remain under the selected root.
- Existing destinations are given a counter-based alternative during planning.
- Execution rechecks source existence, symlink status, root containment, and
  destination collisions immediately before moving.
- Existing files are never overwritten.

## Testing

Run the complete test suite with:

```bash
pytest
```

The tests cover scanning, model-client error handling, classification
validation, destination planning, collision protection, and symlink rejection.

## Current Limitations

- Only direct child files are scanned; nested directories are not traversed.
- Directories, hidden files, and symbolic links are not eligible for scanning.
- Classification uses only the filename and extension; file contents are not
  analyzed.
- The model must be installed locally as `gemma3:1b`; there is no model
  download flow in the application.
- The category set is fixed in `slothsort/config.py`.
- There is no native folder-picker component; a path must be entered manually.
- There is no undo operation, move history, dry-run export, or recovery
  workflow after a successful move.
- The UI has been tested in the project's Linux development environment.
  Windows and macOS behavior, including filesystem-specific permissions and
  symlink behavior, has not been validated.
- Concurrent changes to a directory by other applications can still cause an
  individual move to fail; failed and skipped moves are reported rather than
  retried.
- The project currently has no packaging metadata or installed console
  command; run the app from the repository root.

## Repository Layout

```text
.
├── app.py
├── requirements.txt
├── slothsort/
│   ├── classifier.py
│   ├── config.py
│   ├── executor.py
│   ├── ollama_client.py
│   ├── planner.py
│   └── scanner.py
└── tests/
    ├── test_classifier.py
    ├── test_executor.py
    ├── test_ollama_client.py
    ├── test_planner.py
    └── test_scanner.py
```