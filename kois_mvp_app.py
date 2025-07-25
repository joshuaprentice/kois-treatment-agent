import streamlit as st
from dotenv import load_dotenv
import os
import openai
import PyPDF2

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def parse_responses(text, medical_key, dental_key):
    sections = text.split(dental_key)
    medical_text = sections[0].split(medical_key)[-1]
    dental_text = sections[1] if len(sections) > 1 else ""

    def extract_section(section_text):
        lines = section_text.split("\n")
        responses = {}
        for line in lines:
            for label in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
                if label.lower() in line.lower():
                    responses[label] = line.strip()
        return responses

    return extract_section(medical_text), extract_section(dental_text)

def main():
    st.title("🦷 Kois Treatment Planning Assistant (MVP)")

    pdf_file = st.file_uploader("Upload Oryx Medical & Dental History PDF", type=["pdf"])
    openai_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

    if pdf_file and openai_key:
        st.success("✅ PDF Uploaded Successfully.")
        raw_text = extract_text_from_pdf(pdf_file)
        st.subheader("🔍 Raw Extracted PDF Text")
        st.text_area("PDF Content", raw_text, height=300)

        medical_key = "Medical History | Summary"
        dental_key = "Dental History | Summary"

        try:
            medical, dental = parse_responses(raw_text, medical_key, dental_key)
            st.subheader("📋 Extracted Responses")
            st.json({"Medical": medical, "Dental": dental})

            if st.button("🧠 Generate Kois Risk Summary"):
                prompt = f'''
You are a Kois-trained dentist. Based on the patient’s medical and dental history, identify relevant clinical risks and summarize findings in four categories: systemic, periodontal, biomechanical, and functional. Reference the Kois Interpretation Guidelines for consistency.

### MEDICAL HISTORY RESPONSES:
{medical}

### DENTAL HISTORY RESPONSES:
{dental}

### Generate a summary organized under these headings: Systemic Risk, Periodontal Risk, Biomechanical Risk, Functional Risk. Highlight clinically significant findings, rationale, and any diagnostic flags.
'''
                with st.spinner("Analyzing..."):
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    summary = response.choices[0].message.content
                    st.markdown("### 📝 Kois Risk Summary")
                    st.write(summary)
        except Exception as e:
            st.error(f"Error during processing: {e}")

if __name__ == "__main__":
    main()