
import streamlit as st
import json
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_pdf(pdf_file):
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

def load_json_key(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def parse_responses(text, medical_key, dental_key):
    medical_responses = {}
    dental_responses = {}

    # Split based on likely medical/dental headers
    medical_section = ""
    dental_section = ""
    if "Medical History | Summary" in text:
        medical_section = text.split("Medical History | Summary")[1]
    if "Dental History | Summary" in text:
        dental_section = text.split("Dental History | Summary")[1]

    def extract_qas(section_text):
        lines = section_text.split("
")
        qa_pairs = {}
        question = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.endswith("?") or line.endswith(":"):
                question = line.rstrip(":").strip()
            elif question:
                qa_pairs[question] = line
                question = ""
        return qa_pairs

    medical_responses = extract_qas(medical_section)
    dental_responses = extract_qas(dental_section)

    return medical_responses, dental_responses

    medical_responses = {}
    dental_responses = {}

    all_keys = [(label.lower(), "Medical", label) for label in medical_key] + \
               [(label.lower(), "Dental", label) for label in dental_key]

    for i, line in enumerate(lines):
        for norm_label, category, original_label in all_keys:
            if norm_label in line.lower():
                try:
                    response = lines[i + 1].strip()
                    if category == "Medical":
                        medical_responses[original_label] = response
                    else:
                        dental_responses[original_label] = response
                except IndexError:
                    continue
    return medical_responses, dental_responses

def main():
    st.title("🦷 Kois Treatment Planning Assistant (MVP)")
    st.write("Upload Oryx Medical & Dental History PDF")

    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

    if uploaded_file:
        st.success("✅ PDF Uploaded Successfully.")

        raw_text = extract_text_from_pdf(uploaded_file)
        st.subheader("🔍 Raw Extracted PDF Text")
        st.text(raw_text[:3000])

        medical_key = load_json_key("kois_medical_key.json")
        dental_key = load_json_key("kois_dental_key.json")

        try:
            medical, dental = parse_responses(raw_text, medical_key, dental_key)
        except AttributeError as e:
            st.error(f"Parsing error: {str(e)}")
            medical, dental = {}, {}

        st.subheader("📋 Extracted Responses")
        st.json({"Medical": medical, "Dental": dental})

        if api_key:
            system_prompt = open("kois_prompt.txt").read()

            full_prompt = f"""{system_prompt}

### MEDICAL HISTORY RESPONSES:
{json.dumps(medical, indent=2)}

### DENTAL HISTORY RESPONSES:
{json.dumps(dental, indent=2)}

### Generate a summary organized under these headings: Systemic Risk, Periodontal Risk, Biomechanical Risk, Functional Risk. Highlight clinically significant findings, rationale, and any diagnostic flags."""

            st.subheader("🧠 GPT-4 Prompt")
            st.text_area("Prompt Preview", value=full_prompt, height=500)
        else:
            st.warning("Please enter your OpenAI API key to generate a summary.")

if __name__ == "__main__":
    main()
