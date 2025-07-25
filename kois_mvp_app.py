
import streamlit as st
import fitz  # PyMuPDF
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Load interpretation keys
def load_key(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

# Parse extracted text using interpretation keys
def parse_responses(text, medical_key, dental_key):
    medical = {}
    dental = {}
    lines = text.split('\n')
    for line in lines:
        for label, hint in medical_key.items():
            if hint.lower() in line.lower():
                medical[label] = line.strip()
        for label, hint in dental_key.items():
            if hint.lower() in line.lower():
                dental[label] = line.strip()
    return medical, dental

# Prompt creation function
def create_prompt(medical, dental):
    return f"""You are a Kois-trained dentist. Based on the patient’s medical and dental history, identify relevant clinical risks and summarize findings in four categories: systemic, periodontal, biomechanical, and functional. Reference the Kois Interpretation Guidelines for consistency.

### MEDICAL HISTORY RESPONSES:
{json.dumps(medical, indent=2)}

### DENTAL HISTORY RESPONSES:
{json.dumps(dental, indent=2)}

### Generate a summary organized under these headings: Systemic Risk, Periodontal Risk, Biomechanical Risk, Functional Risk. Highlight clinically significant findings, rationale, and any diagnostic flags.
"""

# Streamlit App
def main():
    st.title("🦷 Kois Treatment Planning Assistant (MVP)")
    st.markdown("Upload Oryx Medical & Dental History PDF")

    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

    if pdf_file:
        st.success("✅ PDF Uploaded Successfully.")
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        raw_text = ""
        for page in doc:
            raw_text += page.get_text()

        st.markdown("### 🔍 Raw Extracted PDF Text")
        st.text_area("Raw PDF Text", raw_text, height=300)

        # Load keys
        medical_key = load_key("kois_medical_key.json")
        dental_key = load_key("kois_dental_key.json")

        medical, dental = parse_responses(raw_text, medical_key, dental_key)

        st.markdown("### 📋 Extracted Responses")
        st.json({"Medical": medical, "Dental": dental})

        if api_key:
            st.markdown("### 🧠 GPT-4 Prompt")
            prompt = create_prompt(medical, dental)
            st.text_area("Prompt Preview", prompt, height=300)

            if st.button("🧪 Generate Treatment Summary"):
                openai.api_key = api_key
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a Kois-trained dental treatment planning assistant."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    result = response['choices'][0]['message']['content']
                    st.markdown("### ✅ Summary")
                    st.write(result)
                except Exception as e:
                    st.error(f"❌ Error generating summary: {str(e)}")

if __name__ == "__main__":
    main()
