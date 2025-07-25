
import streamlit as st
import fitz  # PyMuPDF
import re
import json
import openai

# Load Kois interpretation keys
with open("kois_medical_key.json") as f:
    med_key = json.load(f)

with open("kois_dental_key.json") as f:
    dent_key = json.load(f)

# Load the prompt template
with open("kois_prompt.txt") as f:
    prompt_template = f.read()

st.title("🦷 Kois Treatment Planning Assistant (MVP)")
st.write("**Upload Oryx Medical & Dental History PDF**")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

def extract_responses_from_text(text, key):
    responses = {}
    for q_num in key:
        pattern = rf"{q_num}[\.\)]\s*(.*?)\n"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            responses[q_num] = match.group(1).strip()
    return responses

if uploaded_file:
    st.success("✅ PDF Uploaded Successfully.")

    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
            with st.expander("🔍 Raw Extracted PDF Text"):
    st.text(text[:3000])  # Adjust character count as needed

    med_responses = extract_responses_from_text(text, med_key)
    dent_responses = extract_responses_from_text(text, dent_key)

    st.subheader("📋 Extracted Responses")
    st.json({**med_responses, **dent_responses})

    # Format prompt by replacing placeholders
    med_text = "\n".join([f"{k}: {v}" for k, v in med_responses.items()])
    dent_text = "\n".join([f"{k}: {v}" for k, v in dent_responses.items()])
    formatted_prompt = prompt_template.replace("### MEDICAL HISTORY RESPONSES:", f"### MEDICAL HISTORY RESPONSES:\n{med_text}")
    formatted_prompt = formatted_prompt.replace("### DENTAL HISTORY RESPONSES:", f"### DENTAL HISTORY RESPONSES:\n{dent_text}")

    st.subheader("🧠 GPT-4 Prompt")
    st.code(formatted_prompt, language="markdown")

    if api_key and st.button("🔍 Analyze with GPT-4"):
        try:
            openai.api_key = api_key
            with st.spinner("Contacting GPT-4..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": formatted_prompt}],
                    temperature=0.3,
                )
                result = response["choices"][0]["message"]["content"]
                st.subheader("🦷 GPT-4 Interpretation")
                st.markdown(result)
        except Exception as e:
            st.error(f"Error: {e}")
