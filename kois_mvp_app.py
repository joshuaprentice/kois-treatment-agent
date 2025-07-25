
import streamlit as st
import fitz  # PyMuPDF
import openai
import json
import re

# Load Kois keys
with open("kois_medical_key.json") as f:
    medical_key = json.load(f)

with open("kois_dental_key.json") as f:
    dental_key = json.load(f)

st.title("🦷 Kois Treatment Planning Assistant (MVP)")

uploaded_file = st.file_uploader("Upload Oryx Medical & Dental History PDF", type="pdf")

api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

if uploaded_file:
    st.success("✅ PDF Uploaded Successfully.")

    # Extract raw text from PDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    # STEP 1: Show raw PDF text
    with st.expander("🔍 Raw Extracted PDF Text"):
        st.text(text[:3000])  # Show first 3000 chars

    # Placeholder parsing
    medical_responses = {}
    dental_responses = {}

    # Display extracted content
    st.subheader("📋 Extracted Responses")
    st.json({ "Medical": medical_responses, "Dental": dental_responses })

    # Build prompt
    prompt = f"""
You are a Kois-trained dentist. Based on the patient’s medical and dental history, identify relevant clinical risks and summarize findings in four categories: systemic, periodontal, biomechanical, and functional. Reference the Kois Interpretation Guidelines for consistency.

### MEDICAL HISTORY RESPONSES:
{json.dumps(medical_responses, indent=2)}

### DENTAL HISTORY RESPONSES:
{json.dumps(dental_responses, indent=2)}

### Generate a summary organized under these headings: Systemic Risk, Periodontal Risk, Biomechanical Risk, Functional Risk. Highlight clinically significant findings, rationale, and any diagnostic flags.
"""
    st.subheader("🧠 GPT-4 Prompt")
    st.text_area("Prompt Preview", prompt, height=300)
