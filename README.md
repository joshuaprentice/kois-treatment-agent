# 🦷 Kois Treatment Planning Assistant (MVP)

This is a **Streamlit-based MVP** app that extracts patient history from an Oryx-generated PDF and summarizes dental risks following Kois Center guidelines.

---

## ✅ Features

- Upload Oryx Medical & Dental History PDFs
- Parse and extract relevant patient responses
- Automatically generate a prompt for GPT-4
- Output clinical risk summaries:
  - Systemic
  - Periodontal
  - Biomechanical
  - Functional

---

## 🛠️ Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/kois-treatment-agent.git
   cd kois-treatment-agent
   ```

2. **Install requirements**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your OpenAI API key**  
   Create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

4. **Run the app**
   ```bash
   streamlit run kois_mvp_app.py
   ```

---

## 📄 Example Input

Use the `Oryx-Prentice Dental.pdf` file exported from Oryx PMS. The app will read and format the content and create an interpretation-ready GPT-4 prompt.

---

## 🚧 Disclaimer

This app is for educational and prototyping purposes only. It does not replace clinical judgment or FDA-cleared tools.

---

## 📬 Contact

Created by **Dr. Joshua Prentice**  
Email: joshua.n.prentice@gmail.com
