
import streamlit as st
import fitz  # PyMuPDF
import json
import re
from collections import defaultdict

# Load Kois interpretation keys
@st.cache_data
def load_interpretation_keys():
    with open("kois_medical_key.json") as f_med, open("kois_dental_key.json") as f_dent:
        medical_key = json.load(f_med)
        dental_key = json.load(f_dent)
    return medical_key, dental_key

# Extract Q&A pairs from the Oryx PDF
def extract_question_responses_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    responses = defaultdict(dict)
    current_section = None
    for line in full_text.split("\n"):
        line = line.strip()
        if "Medical History" in line:
            current_section = "medical"
        elif "Dental History" in line:
            current_section = "dental"
        match = re.match(r"^(Q\d+)[\s:–-]+(.+)", line)
        if match and current_section:
            qnum, response = match.groups()
            responses[current_section][qnum.strip()] = response.strip()
    return responses

# Build GPT prompt
def build_prompt(patient_data, kois_keys):
    prompt = [
        "You are a Kois-trained dentist. Based on the patient’s medical and dental history, identify relevant clinical risks and summarize findings in four categories: systemic, periodontal, biomechanical, and functional. Reference the Kois Interpretation Guidelines for consistency.\n"
    ]
    for section in ['medical', 'dental']:
        prompt.append(f"\n### {section.upper()} HISTORY RESPONSES:")
        for q, ans in patient_data.get(section, {}).items():
            interp = kois_keys[section].get(q, {}).get("interpretation", "No guideline available.")
            prompt.append(f"- {q}: {ans} → {interp}")
    prompt.append("\n### Generate a summary organized under these headings: Systemic Risk, Periodontal Risk, Biomechanical Risk, Functional Risk. Highlight clinically significant findings, rationale, and any diagnostic flags.\n")
    return "\n".join(prompt)

# Streamlit UI
st.title("🦷 Kois Treatment Planning Assistant (MVP)")

uploaded_pdf = st.file_uploader("Upload Oryx Medical & Dental History PDF", type=["pdf"])
if uploaded_pdf:
    st.success("✅ PDF Uploaded Successfully.")
    medical_key, dental_key = load_interpretation_keys()
    patient_data = extract_question_responses_from_pdf(uploaded_pdf)

    st.subheader("📋 Extracted Responses")
    st.json(patient_data)

    gpt_prompt = build_prompt(patient_data, {"medical": medical_key, "dental": dental_key})

    st.subheader("🧠 GPT-4 Prompt")
    st.code(gpt_prompt, language="markdown")

    st.download_button("Download Prompt as .txt", gpt_prompt, file_name="kois_prompt.txt")

    st.info("You can paste this prompt into OpenAI GPT-4 or your custom AI agent for interpretation.")
