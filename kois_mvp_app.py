
import streamlit as st
import fitz  # PyMuPDF
import json
import os
from typing import Tuple
from dotenv import load_dotenv
import openai

load_dotenv()

# Load interpretation keys
def load_keys():
    with open("kois_medical_key.json") as f:
        medical_key = json.load(f)
    with open("kois_dental_key.json") as f:
        dental_key = json.load(f)
    return medical_key, dental_key

# Extract text from uploaded PDF
def extract_text_from_pdf(pdf_file) -> str:
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Parse the PDF text to extract question-answer pairs
def parse_responses(text: str, medical_key: dict, dental_key: dict) -> Tuple[dict, dict]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    medical_data = {}
    dental_data = {}

    for key, label in medical_key.items():
        for line in lines:
            if label.lower() in line.lower():
                response_index = lines.index(line) + 1
                if response_index < len(lines):
                    medical_data[label] = lines[response_index]
                break

    for key, label in dental_key.items():
        for line in lines:
            if label.lower() in line.lower():
                response_index = lines.index(line) + 1
                if response_index < len(lines):
                    dental_data[label] = lines[response_index]
                break

    return medical_data, dental_data

# Construct GPT-4 prompt
def build_prompt(medical: dict, dental: dict) -> str:
    prompt = """You are a Kois-trained dentist. Based on the patient’s medical and dental history, identify relevant clinical risks and summarize findings in four categories: systemic, periodontal, biomechanical, and functional. Reference the Kois Interpretation Guidelines for consistency.

### MEDICAL HISTORY RESPONSES:
"""
    for k, v in medical.items():
        prompt += f"- {k}: {v}\n"

    prompt += "\n### DENTAL HISTORY RESPONSES:\n"
    for k, v in dental.items():
        prompt += f"- {k}: {v}\n"

    prompt += """

### Generate a summary organized under these headings: Systemic Risk, Periodontal Risk, Biomechanical Risk, Functional Risk. Highlight clinically significant findings, rationale, and any diagnostic flags.
"""
    return prompt

# Streamlit UI
def main():
    st.title("🦷 Kois Treatment Planning Assistant (MVP)")
    st.subheader("Upload Oryx Medical & Dental History PDF")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

    if uploaded_file:
        st.success("✅ PDF Uploaded Successfully.")
        raw_text = extract_text_from_pdf(uploaded_file)
        st.markdown("### 🔍 Raw Extracted PDF Text")
        st.text(raw_text[:3000])  # show a portion

        medical_key, dental_key = load_keys()
        medical, dental = parse_responses(raw_text, medical_key, dental_key)

        st.markdown("### 📋 Extracted Responses")
        st.json({"Medical": medical, "Dental": dental})

        prompt = build_prompt(medical, dental)

        st.markdown("### 🧠 GPT-4 Prompt")
        st.text_area("Prompt Preview", prompt, height=400)

        if st.button("Run GPT-4"):
            if not api_key:
                st.error("Please enter your OpenAI API key.")
                return

            openai.api_key = api_key
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a Kois-trained dentist."},
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response.choices[0].message.content
                st.markdown("### 🧾 GPT-4 Output")
                st.text_area("Interpretation", result, height=500)
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
