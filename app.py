import streamlit as st

from slothsort.classifier import classify_file
from slothsort.config import DEFAULT_MODEL
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

if st.button("Scan and classify"):
    try:
        scanned_files = scan_directory(folder_path)
        ollama_client = OllamaClient(DEFAULT_MODEL)
        review_rows = []
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
        st.session_state.review_rows = review_rows
    except (FileNotFoundError, NotADirectoryError) as error:
        st.session_state.review_rows = []
        st.error(f"Invalid Directory: {error}")
    except OllamaClientError as error:
        st.session_state.review_rows = []
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

st.button("Execute Move", disabled=True)
