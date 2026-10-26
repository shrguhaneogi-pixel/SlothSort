import streamlit as st


st.set_page_config(page_title="SlothSort", page_icon="📁")

st.title("SlothSort")
st.write("Organize your files locally with AI assistance.")
st.info(
    "Privacy first: your files stay on this device and are not uploaded to a "
    "third-party service."
)
st.subheader("Nothing to organize yet")
st.write("Choose a folder in a future step to begin organizing your files.")
