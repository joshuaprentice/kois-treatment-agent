
import streamlit as st
import fitz  # PyMuPDF
import json
import os
from dotenv import load_dotenv
import openai
import re

st.set_page_config(page_title="🦷 Kois Treatment Planning Assistant (MVP)")

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_medical_dental_sections(text):
    """
    Extract responses to medical and dental questions from the PDF text
    by identifying headers and aggregating their respective sections.
    """
    cleaned_text = re.sub(r'\n+', '\n', text)

    med_match = re.search(r'Medical History\s*\|?\s*Summary(.*?)(Dental History|$)', cleaned_text, re.DOTALL | re.IGNORECASE)
    dent_match = re.search(r'Dental History\s*\|?\s*Summary(.*?)(Confirmation|$)', cleaned_text, re.DOTALL | re.IGNORECASE)

    med_text = med_match.group(1).strip() if med_match else ""
    dent_text = dent_match.group(1).strip() if dent_match else ""

    return {
        "Medical": med_text,
        "Dental": dent_text
    }

def main():
    st.title("🦷 Kois Treatment Planning Assistant (MVP)")
    uploaded_file = st.file_uploader("Upload Oryx Medical & Dental History PDF", type=["pdf"])

    if uploaded_file:
        st.success("✅ PDF Uploaded Successfully.")
        raw_text = extract_text_from_pdf(uploaded_file)

        with st.expander("🔍 Raw Extracted PDF Text"):
            st.text(raw_text)

        responses = extract_medical_dental_sections(raw_text)

        with st.expander("📋 Extracted Responses"):
            st.json(responses)

        prompt_template = """
You are a Kois-trained dentist. Based on the patient’s medical and dental history, identify relevant clinical risks and summarize findings in four categories: systemic, periodontal, biomechanical, and functional. Reference the Kois Interpretation Guidelines for consistency.

### MEDICAL HISTORY RESPONSES:
{medical}

### DENTAL HISTORY RESPONSES:
{dental}

### Generate a summary organized under these headings: Systemic Risk, Periodontal Risk, Biomechanical Risk, Functional Risk. Highlight clinically significant findings, rationale, and any diagnostic flags.
"""

        if responses["Medical"] or responses["Dental"]:
            prompt = prompt_template.format(
                medical=responses["Medical"],
                dental=responses["Dental"]
            )

            with st.expander("🧠 GPT-4 Prompt"):
                st.code(prompt)

if __name__ == "__main__":
    main()
