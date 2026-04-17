import streamlit as st
import os
import io
import base64
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



# --- LAYOUT: TWO COLUMNS ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Upload & Preview")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", label_visibility="collapsed")
    
    if uploaded_file is not None:
        # Display PDF (Simple version)
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        # In a real RAG app, you'd process the PDF here
    else:
        # Placeholder to match your UI
        st.info("No PDF uploaded yet.")
    
    if st.button("Upload"):
        if uploaded_file is not None:
            with st.spinner("Analyzing with AI..."):
                try:
                    # Prepare the file to be sent as 'multipart/form-data'
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    
                    response = requests.post("http://127.0.0.1:8000/upload", files=files)
                    
                    if response.status_code == 200:
                        st.success(response.json()['message'])
                    else:
                        st.error(f"Backend Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please select a PDF file first!")
with col2:
    st.subheader("Query Document")
    user_query = st.text_input("Type any question from the PDF...", placeholder="e.g., What is the main conclusion?")
    
    if st.button("Ask"):
        
        if uploaded_file is not None: 
            if user_query:
                with st.spinner("Thinking..."):
                    try:
                        response = requests.post(f"http://127.0.0.1:8000/query", params={"query": user_query})
                        
                        if response.status_code == 200:
                            answer = response.json().get('answer', "No answer found.")
                            st.markdown("### Answer:")
                            st.write(answer)
                            
                            context = response.json().get('context', "No context")
                            st.markdown("### Context:")
                            st.write(context)
                        else:
                            st.error(f"Backend Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
            else:
                st.warning("Please type a question first!")
        else:
            
            st.error("❌ No file uploaded! Please upload a PDF to ask questions.")