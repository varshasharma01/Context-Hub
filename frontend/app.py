import streamlit as st
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Context Hub", layout="wide")

#---
st.markdown("""
    <style>
    .main-header {
        background-color: #d6d2a9;
        color: blue;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
    }
    .stButton>button {
        background-color: #016401;
        color: white;
        width: 100%;
    }
    </style>
    <div class="main-header">
        <h1>📄 Context Hub</h1>
    </div>
    """, unsafe_allow_html=True)


# Initialize state
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Upload & Preview")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", label_visibility="collapsed")

    if uploaded_file is not None:

        #Only process ONCE
        if not st.session_state.file_processed:

            with st.spinner("Analyzing with AI..."):
                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    }

                    response = requests.post("http://127.0.0.1:8000/upload", files=files)

                    if response.status_code == 200:
                        st.success(response.json()['message'])

                        #  mark as processed
                        st.session_state.file_processed = True
                        st.session_state.uploaded_filename = uploaded_file.name

                    else:
                        st.error(f"Backend Error: {response.text}")

                except Exception as e:
                    st.error(f"Connection Error: {e}")

        else:
            #  Show already uploaded
            st.success(f"File '{st.session_state.uploaded_filename}' already processed")

    else:
        st.warning("Please select a PDF file first!")


with col2:
    st.subheader("Query Document")

    user_query = st.text_input("Type any question from the PDF...")

    if st.button("Ask"):

        if st.session_state.file_processed:

            if user_query:
                with st.spinner("Thinking..."):
                    try:
                        response = requests.post(
                            "http://127.0.0.1:8000/query",
                            params={"query": user_query}
                        )

                        if response.status_code == 200:
                            data = response.json()

                            st.markdown("### Answer:")
                            st.write(data.get("answer"))

                            st.markdown("### Context:")
                            st.write(data.get("context"))

                        else:
                            st.error(f"Backend Error: {response.status_code}")

                    except Exception as e:
                        st.error(f"Connection Error: {e}")

            else:
                st.warning("Please type a question first!")

        else:
            st.error(" Upload PDF first!")