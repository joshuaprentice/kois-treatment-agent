
import streamlit as st
import fitz  # PyMuPDF
import openai
import os

st.set_page_config(page_title="🦷 Kois Treatment Planning Assistant (MVP)")

st.title("🦷 Kois Treatment Planning Assistant (MVP)")
st.markdown("Upload Oryx Medical & Dental History PDF")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

if uploaded_file:
    st.success("✅ PDF Uploaded Successfully.")
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    st.subheader("🔍 Raw Extracted PDF Text")
    with st.expander("Click to view"):
        st.text(full_text)

    # Placeholder dictionary for extracted values
    responses = {
        "Medical": {},
        "Dental": {}
    }

    st.subheader("📋 Extracted Responses")
    st.json(responses)

    if api_key:
        if st.button("🧠 Generate Summary"):
            openai.api_key = api_key
            prompt = f'''
You are a Kois-trained dentist. Based on the patient’s medical and dental history, identify relevant clinical risks and summarize findings in four categories: systemic, periodontal, biomechanical, and functional. Reference the Kois Interpretation Guidelines for consistency.

### MEDICAL HISTORY RESPONSES:
{responses["Medical"]}

### DENTAL HISTORY RESPONSES:
{responses["Dental"]}

### Generate a summary organized under these headings: Systemic Risk, Periodontal Risk, Biomechanical Risk, Functional Risk. Highlight clinically significant findings, rationale, and any diagnostic flags.
            '''.strip()

            with st.spinner("Processing with GPT-4..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a Kois-trained dentist."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2
                    )
                    st.success("✅ Summary generated successfully!")
                    st.subheader("🧾 GPT-4 Summary")
                    st.write(response.choices[0].message["content"])
                except Exception as e:
                    st.error(f"❌ Error from OpenAI: {e}")
    else:
        st.warning("⚠️ Please enter your OpenAI API key to generate the summary.")
else:
    st.info("📄 Awaiting PDF upload.")
