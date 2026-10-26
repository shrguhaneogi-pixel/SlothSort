<pre>
        .-""""-.
       /  .--.  \      🦥  slow sorting, steady results
      /  /    \  \
      | | 0  0 | |      [ messy files ]  ->  [ calm folders ]
      | |  __  | |
       \ \____/ /
        '.___.'
          /|\
       __/ | \__
</pre>

# SlothSort

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/Ollama-local%20inference-black)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **SlothSort uses local AI to turn your messy Downloads folder into an organized workspace, without uploading your private files.**

## 🦥 Slow and Steady

SlothSort is built for the DEV Community **Slow and Steady** theme: let a
local open-weight model do the tedious sorting work while you stay relaxed,
private, and in control. It rewards laziness without outsourcing your data:
Gemma runs through Ollama on your machine, SlothSort proposes a plan, and you
approve only the moves you actually want.

The app is deliberately cautious. It scans direct child files, classifies
filename and extension metadata, shows a review table, and waits for an
explicit approval before moving anything.

## 🎬 Interactive Demo

![SlothSort Demo](link-to-gif.gif)

_Demo placeholder: replace `link-to-gif.gif` with a recording of a cluttered
folder becoming an organized workspace._

## ✨ Key Features

- [x] **Local AI** — classify files with a locally running Gemma model through Ollama.
- [x] **Zero Data Leakage by Design** — only filenames and extensions reach the local Ollama endpoint; file contents are never read.
- [x] **Human-in-the-Loop Approval** — every proposed move is visible and individually approvable.
- [x] **Overwrite Protection** — existing destinations are skipped at execution time and planned collisions receive counter-suffixed names.
- [x] **Path Safety** — proposed destinations are constrained to the selected root.
- [x] **Symlink Protection** — symlinks are excluded during scanning and rejected during execution.
- [x] **Slow, Focused Scanning** — only direct child files are considered; no recursive surprise sweep.
- [x] **Tested Safety Layer** — scanner, classifier, planner, Ollama adapter, and executor have automated tests.

## 🚀 Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/shrguhaneogi-pixel/SlothSort.git
cd SlothSort
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. Install the local Gemma model

Install and start [Ollama](https://ollama.com/) if it is not already
available, then pull the configured model:

```bash
ollama pull gemma3:1b
curl http://localhost:11434/api/tags
```

The tags response should include `gemma3:1b`. SlothSort expects Ollama at
`http://localhost:11434`.

### 4. Run SlothSort

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, usually
`http://localhost:8501`.

## 🧭 How to Use It

1. Type the path to a directory, such as a Downloads folder.
2. Select **Scan and classify**.
3. Review each **Original Name**, **Proposed Category**, and
   **Proposed Destination**.
4. Tick **Approve** only for the files you want to organize.
5. Select **Execute Move**.

Supported categories are `Work`, `Finance`, `Documents`, `Images`, `Media`,
`Archives`, and `Other`.

## 🧱 Under the Hood

<details>
<summary><strong>Open the architecture walkthrough</strong></summary>

```text
User enters folder
        |
        v
Scanner -> direct files only, no recursion, no hidden files, no symlinks
        |
        v
Classifier -> filename + extension -> local Ollama/Gemma JSON
        |
        v
Planner -> allowlisted category + root-safe, collision-aware destination
        |
        v
Streamlit review table -> user checks Approve
        |
        v
Executor -> revalidates source/symlink/destination immediately before move
```

| Layer | Responsibility | Safety boundary |
| --- | --- | --- |
| `slothsort/scanner.py` | Discover eligible direct child files | Read-only; excludes hidden files, directories, and symlinks |
| `slothsort/classifier.py` | Validate local model categories and confidence | Invalid categories fall back to `Other` |
| `slothsort/planner.py` | Propose category destinations | Resolves and checks root containment; avoids planned collisions |
| `slothsort/ollama_client.py` | Talk to the local Ollama API | Fixed to `localhost`; requests JSON output |
| `slothsort/executor.py` | Perform approved moves | Rechecks paths, symlinks, and collisions before moving |
| `app.py` | Present review and approval UI | Does not call the executor until approval is explicit |

</details>

## 🔒 Safety & Privacy Guarantee

SlothSort is local-first:

- It never sends file contents to an AI service.
- It sends only filename and extension metadata to Ollama on
  `http://localhost:11434`.
- It has no cloud AI, analytics, telemetry, or upload endpoint.
- It never executes a move during scanning, classification, or planning.
- It only calls the executor after the user checks **Approve** and clicks
  **Execute Move**.
- It never intentionally overwrites an existing destination.
- It rejects symlink sources and symlink path components.

Keep Ollama bound to localhost for the stated offline boundary. A user who
changes the endpoint or exposes Ollama beyond the local machine changes that
deployment's privacy properties.

## 🧪 Testing

Run the complete test suite:

```bash
pytest
```

The suite covers:

- Direct-child scanner filtering
- Ollama success, timeout, connection, and malformed JSON handling
- Classification allowlist validation
- Planner path traversal and collision behavior
- Executor moves, overwrite prevention, and symlink rejection

## <details>
<summary><strong>Troubleshooting</strong></summary>

### `Model Unavailable`

Check that Ollama is running and that the configured model is installed:

```bash
curl http://localhost:11434/api/tags
ollama pull gemma3:1b
```

### `Invalid Directory`

Enter an existing directory path. SlothSort does not create or select folders
for you, and it does not recursively search parent directories.

### No files appear

The scanner intentionally ignores hidden files, directories, symbolic links,
and files below nested directories. It considers only direct child files.

</details>

<details>
<summary><strong>Advanced Configuration</strong></summary>

The default model and categories are defined in
[`slothsort/config.py`](slothsort/config.py):

```python
DEFAULT_MODEL = "gemma3:1b"
ALLOWED_CATEGORIES = [
    "Work",
    "Finance",
    "Documents",
    "Images",
    "Media",
    "Archives",
    "Other",
]
```

The Ollama endpoint is intentionally fixed to
`http://localhost:11434` in [`slothsort/ollama_client.py`](slothsort/ollama_client.py);
there is no remote endpoint configuration in this project.

</details>

## 🧰 Tech Stack

| Tool | Why it is here |
| --- | --- |
| **Python** | Small, readable filesystem and safety primitives with `pathlib` |
| **Streamlit** | A fast local review UI with standard, judge-friendly controls |
| **Ollama** | A local inference runtime with no required cloud account |
| **Gemma 3 1B** | A compact open-weight model suitable for local filename classification |
| **Requests** | A minimal HTTP adapter for Ollama's localhost API |

## ⚠️ Current Limitations

- Only direct child files are scanned; nested directories are not traversed.
- Hidden files, directories, and symbolic links are excluded.
- Classification uses only filename and extension, not file contents.
- `gemma3:1b` must be installed locally; the app does not download models.
- Categories are fixed in `slothsort/config.py`.
- Paths are entered manually; there is no native folder-picker component.
- There is no undo history, dry-run export, or recovery workflow after a move.
- The project has been tested in a Linux development environment; Windows and
  macOS filesystem behavior is not validated.
- Concurrent filesystem changes can still cause an individual move to fail or
  be skipped; the app reports the result rather than retrying.

## 📁 Repository Layout

```text
.
├── app.py
├── requirements.txt
├── LICENSE
├── scripts/
│   └── generate_dummy_data.py
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

## 🏷️ Suggested Repository Topics

`hackathon` · `dev-community` · `local-ai` · `gemma` · `streamlit` · `python` ·
`automation` · `privacy`

## 📌 Submission Checklist

- [ ] Add a real demo GIF or before/after screenshots in place of the demo placeholder.
- [ ] Add the suggested topics in the GitHub repository settings.
- [ ] Create a GitHub Project board with **To Do**, **In Progress**, and **Done**.
- [ ] Open issues for the MVP features and any known bugs.
- [x] Include an MIT license.
- [x] Preserve the incremental implementation history.

## License

SlothSort is released under the [MIT License](LICENSE).
