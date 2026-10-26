import streamlit as st

from slothsort.classifier import classify_file
from slothsort.config import DEFAULT_MODEL
from slothsort.executor import ApprovedMove, execute_plan
from slothsort.ollama_client import OllamaClient, OllamaClientError
from slothsort.planner import plan_destination
from slothsort.scanner import scan_directory


st.set_page_config(page_title="SlothSort", page_icon="📁")

st.title("SlothSort")
st.write("Review AI-proposed file organization before anything is moved.")
st.info(
    "Privacy first: your files stay on this device and are not uploaded to a "
    "third-party service."
)

folder_path = st.text_input(
    "Folder to scan",
    placeholder="/path/to/folder",
)

if "review_rows" not in st.session_state:
    st.session_state.review_rows = []
if "review_moves" not in st.session_state:
    st.session_state.review_moves = []

if st.button("Scan and classify"):
    try:
        scanned_files = scan_directory(folder_path)
        ollama_client = OllamaClient(DEFAULT_MODEL)
        review_rows = []
        review_moves = []
        for file in scanned_files:
            classification = classify_file(file, ollama_client)
            destination = plan_destination(
                file, classification, folder_path
            )
            review_rows.append(
                {
                    "Original Name": file.filename,
                    "Proposed Category": classification.category,
                    "Approve": False,
                    "Proposed Destination": str(destination),
                }
            )
            review_moves.append(
                ApprovedMove(
                    source=file.absolute_path,
                    destination=destination,
                    root_dir=folder_path,
                )
            )
        st.session_state.review_rows = review_rows
        st.session_state.review_moves = review_moves
    except (FileNotFoundError, NotADirectoryError) as error:
        st.session_state.review_rows = []
        st.session_state.review_moves = []
        st.error(f"Invalid Directory: {error}")
    except OllamaClientError as error:
        st.session_state.review_rows = []
        st.session_state.review_moves = []
        st.error(f"Model Unavailable: {error}")

if st.session_state.review_rows:
    st.subheader("Review proposed moves")
    st.session_state.review_rows = st.data_editor(
        st.session_state.review_rows,
        column_config={
            "Original Name": st.column_config.TextColumn(disabled=True),
            "Proposed Category": st.column_config.TextColumn(disabled=True),
            "Approve": st.column_config.CheckboxColumn(
                "Approve",
                help="Approve this proposed move for a future execution step.",
            ),
            "Proposed Destination": st.column_config.TextColumn(disabled=True),
        },
        disabled=["Original Name", "Proposed Category", "Proposed Destination"],
        hide_index=True,
        key="review_table",
    )
else:
    st.subheader("Nothing to review yet")
    st.write("Enter a folder path and scan it to generate proposed moves.")

if st.button("Execute Move", disabled=not st.session_state.review_rows):
    approved_moves = [
        st.session_state.review_moves[index]
        for index, row in enumerate(st.session_state.review_rows)
        if row["Approve"]
    ]
    if not approved_moves:
        st.warning("No proposed moves were approved.")
    else:
        result = execute_plan(approved_moves)
        if result["success"]:
            st.success(f"Moved {len(result['success'])} file(s).")
        if result["skipped"]:
            st.warning(f"Skipped {len(result['skipped'])} file(s).")
        if result["failed"]:
            st.warning(f"Failed to move {len(result['failed'])} file(s).")
