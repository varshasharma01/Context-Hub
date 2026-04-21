import streamlit as st
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="ContextHub", layout="wide")

#---
st.markdown("""
    <style>
    .main-header {
        background-color: #427d44;
        color: white;
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
    <style>
        /* Change the font size of the tab labels */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.5rem; 
            gap: 20px;
        }
        
        /* Optional: Change the height and padding of the tabs */
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            padding-top: 10px;
            padding-bottom: 10px;
            padding-right: 20px;
            padding-left: 20px;
        }
        
    </style>
    <div class="main-header">
        <h1> 🔍 Context Hub</h1>
    </div>
    """, unsafe_allow_html=True)


tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "About",
    "📄 Document", 
    "🖼️ Visual", 
    "🔗 Web Link", 
    "🎥 Video"
])

with tab0:
    st.markdown("""
            
            <h3 style='text-align: center; color: #427d44;'>Your Universal Multimodal Intelligence Hub</h3>
            <br>
        """, unsafe_allow_html=True)

        # 3-column layout for a "Features at a glance" look
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ⚡ Fast")
        st.write("Powered by **Gemini** inference for near-instant responses.")
        
    with col2:
        st.markdown("### 🧠 Smart")
        st.write("Uses **Nomic Embeddings** and **Pinecone** for deep context retrieval.")
        
    with col3:
        st.markdown("### 🔄 Versatile")
        st.write("Handles Documents, Images, Web Links, and Videos seamlessly.")

    st.markdown("---")

    st.markdown("## 📖 What is ContextHub?")
    st.write("""
        ContextHub is a state-of-the-art **RAG (Retrieval-Augmented Generation)** platform. 
        Instead of just talking to a general AI, you can give the AI your own specific data—be it a complex 
        PDF report, a website link, or even a video—and ask questions based on that specific content.
    """)

    with st.expander("🚀 How it works under the hood"):
        st.info("""
        1. **Ingest:** You upload a source (PDF, Image, Link, or Video).
        2. **Process:** The system chunks the data and uses **Nomic** to create vector embeddings.
        3. **Store:** These vectors are indexed in a **Pinecone** database.
        4. **Retrieve:** When you ask a question, we find the most relevant context.
        5. **Generate:** **Gemini** generates an accurate answer based ONLY on your data.
        """)

    st.markdown("---")
    st.markdown("""
            
            <h3 style='text-align: center; color: #427d44;'>🛠 How to use ContextHub?</h3>
            <br>
        """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>1. Select your Source</h4>
            <p>Choose between PDF, Image, Web, or Video tabs based on your needs.</p>
        </div><br>
        <div class="feature-card">
            <h4>2. Upload & Process</h4>
            <p>Click the process button to let Nomic & Gemini index your data.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>3. Ask Anything</h4>
            <p>Type your query in the chat box. The AI answers <b>only</b> based on your data.</p>
        </div><br>
        <div class="feature-card">
            <h4>4. Multi-Format Output</h4>
            <p>Get summaries, tables, or code extracted directly from your sources.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    st.caption("Developed by Varsha | Powered by Gemini, Pinecone & Nomic")
    
#########################################################################################################################

with tab1:
    st.header("PDF Analysis")

    # -------- SESSION STATE --------
    if "file_processed" not in st.session_state:
        st.session_state.file_processed = False

    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None

    col1, col2 = st.columns([1, 1], gap="large")

    # -------- LEFT SIDE (UPLOAD) --------
    with col1:
        st.subheader("Upload & Preview")

        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:

            #  KEY FIX: detect new file
            if st.session_state.uploaded_filename != uploaded_file.name:
                st.session_state.file_processed = False

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

                        response = requests.post(
                            "http://127.0.0.1:8000/upload",
                            files=files
                        )

                        if response.status_code == 200:
                            st.success(response.json()['message'])

                            # update state
                            st.session_state.file_processed = True
                            st.session_state.uploaded_filename = uploaded_file.name

                        else:
                            st.error(f"Backend Error: {response.text}")

                    except Exception as e:
                        st.error(f"Connection Error: {e}")

            else:
                st.success(f"File '{uploaded_file.name}' already processed")

        else:
            st.warning("Please select a PDF file first!")

    # -------- RIGHT SIDE (QUERY) --------
    with col2:
        st.subheader("Query Document")

        user_query = st.text_input("Type any question from the PDF...")

        ask_clicked = st.button("Ask pdf")

        if ask_clicked:

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

                            else:
                                st.error(f"Backend Error: {response.status_code}")

                        except Exception as e:
                            st.error(f"Connection Error: {e}")

                else:
                    st.warning("Please type a question first!")

            else:
                st.error(" Upload PDF first!")

#########################################################################################################################

with tab2:
    st.header("🖼️ Image Intelligence")

    # -------- SESSION STATE --------
    if "image_processed" not in st.session_state:
        st.session_state.image_processed = False

    if "uploaded_image_name" not in st.session_state:
        st.session_state.uploaded_image_name = None

    col1, col2 = st.columns([1,1], gap='large')

    # -------- LEFT SIDE (UPLOAD) --------
    with col1:
        uploaded_image = st.file_uploader(
            "Upload an image",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_image is not None:

            # show preview
            st.image(uploaded_image, caption="Uploaded Image", width="content")

            #  detect new image
            if st.session_state.uploaded_image_name != uploaded_image.name:
                st.session_state.image_processed = False

            if not st.session_state.image_processed:

                with st.spinner("Processing image..."):
                    try:
                        files = {
                            "file": (
                                uploaded_image.name,
                                uploaded_image.getvalue(),
                                "image/png"
                            )
                        }

                        response = requests.post(
                            "http://localhost:8000/process-image",
                            files=files
                        )

                        if response.status_code == 200:
                            st.session_state.image_processed = True
                            st.session_state.uploaded_image_name = uploaded_image.name
                            st.success("Image processed!")

                        else:
                            st.error("Backend error")

                    except Exception as e:
                        st.error(f"Error: {e}")

        else:
            st.info("Upload an image to begin")

    # -------- RIGHT SIDE (QUERY) --------
    with col2:
        query = st.text_input("Ask something about the image...")

        ask_clicked_image = st.button("Ask Image")

        if ask_clicked_image:

            if st.session_state.image_processed:

                if query:
                    with st.spinner("Analyzing with AI..."):
                        try:
                            response = requests.post(
                                "http://localhost:8000/query-image",
                                params={"query": query}
                            )

                            if response.status_code == 200:
                                st.write(response.json().get("answer"))

                            else:
                                st.error("Backend error")

                        except Exception as e:
                            st.error(f"Error: {e}")

                else:
                    st.warning("Enter a question")

            else:
                st.error("Upload image first!")

with tab3:
    st.header("🌐 URL Intelligence")

    # -------- SESSION STATE --------
    if "url_processed" not in st.session_state:
        st.session_state.url_processed = False

    if "current_url" not in st.session_state:
        st.session_state.current_url = None

    col1, col2 = st.columns([1,1], gap="large")

    # -------- LEFT (INPUT URL) --------
    with col1:
        url = st.text_input("Paste URL here")

        if url:

            # detect new URL
            if st.session_state.current_url != url:
                st.session_state.url_processed = False

            if not st.session_state.url_processed:

                with st.spinner("Fetching website..."):
                    try:
                        response = requests.post(
                            "http://localhost:8000/process-url",
                            params={"url": url}
                        )

                        if response.status_code == 200:
                            st.session_state.url_processed = True
                            st.session_state.current_url = url
                            st.success("URL processed!")

                        else:
                            st.error("Backend error")

                    except Exception as e:
                        st.error(f"Error: {e}")

        else:
            st.info("Enter a URL to begin")

    # -------- RIGHT (QUERY) --------
    with col2:
        query = st.text_input("Ask something about the website...")

        ask_clicked = st.button("Ask")

        if ask_clicked:

            if st.session_state.url_processed:

                if query:
                    with st.spinner("Analyzing..."):
                        try:
                            response = requests.post(
                                "http://localhost:8000/query-url",
                                params={"query": query}
                            )

                            if response.status_code == 200:
                                st.write(response.json().get("answer"))

                            else:
                                st.error("Backend error")

                        except Exception as e:
                            st.error(f"Error: {e}")

                else:
                    st.warning("Enter a question")

            else:
                st.error("Process URL first!")
                
                
# ##############################################################################################################
with tab4:
    st.header("🎥 YouTube Intelligence")

    # -------- SESSION STATE --------
    if "yt_processed" not in st.session_state:
        st.session_state.yt_processed = False

    if "yt_url" not in st.session_state:
        st.session_state.yt_url = None

    col1, col2 = st.columns([1,1], gap="large")

    # -------- LEFT (URL INPUT) --------
    with col1:
        yt_url = st.text_input("Paste YouTube URL")

        if yt_url:

            # detect new video
            if st.session_state.yt_url != yt_url:
                st.session_state.yt_processed = False

            if not st.session_state.yt_processed:

                with st.spinner("Processing YouTube video..."):
                    try:
                        response = requests.post(
                            "http://localhost:8000/process-youtube",
                            params={"url": yt_url}
                        )

                        if response.status_code == 200:
                            st.session_state.yt_processed = True
                            st.session_state.yt_url = yt_url
                            st.success("Video processed!")

                        else:
                            st.error("Backend error")

                    except Exception as e:
                        st.error(f"Error: {e}")

        else:
            st.info("Enter YouTube URL")

    # -------- RIGHT (QUERY) --------
    with col2:
        query = st.text_input("Ask something about the video...")

        ask_clicked = st.button("Ask")

        if ask_clicked:

            if st.session_state.yt_processed:

                if query:
                    with st.spinner("Thinking..."):
                        try:
                            response = requests.post(
                                "http://localhost:8000/query-youtube",
                                params={"query": query}
                            )

                            if response.status_code == 200:
                                st.write(response.json().get("answer"))

                            else:
                                st.error("Backend error")

                        except Exception as e:
                            st.error(f"Error: {e}")

                else:
                    st.warning("Enter a question")

            else:
                st.error("Process video first!")