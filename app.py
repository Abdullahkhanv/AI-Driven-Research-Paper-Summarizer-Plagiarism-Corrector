import streamlit as st
import os
from groq import Groq
import PyPDF2
import re

# ---------------------------
# STREAMLIT CONFIG
# ---------------------------
st.set_page_config(page_title="AI Research Assistant", layout="wide")

st.title("📄 AI Research Paper Assistant")
st.markdown("### ✨ Summarize | Rewrite | Cite")

# ---------------------------
# API KEY HANDLING (FIXED)
# ---------------------------
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.warning("⚠️ Enter your Groq API Key")
    api_key = st.text_input("Enter GROQ API Key", type="password")

if not api_key:
    st.stop()

# Initialize client safely
client = Groq(api_key=api_key)

# ---------------------------
# PDF TEXT EXTRACTION
# ---------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    reader = PyPDF2.PdfReader(uploaded_file)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# ---------------------------
# SECTION SPLITTING
# ---------------------------
def split_sections(text):
    sections = {
        "Abstract": "",
        "Introduction": "",
        "Methodology": "",
        "Results": "",
        "Discussion": "",
        "Conclusion": ""
    }

    for sec in sections.keys():
        pattern = rf"{sec}(.*?)(?=\n[A-Z][a-z]+|\Z)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[sec] = match.group(1).strip()

    return sections

# ---------------------------
# LLM FUNCTION (SAFE)
# ---------------------------
def ask_llm(prompt):
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ---------------------------
# FEATURES
# ---------------------------
def summarize_section(text):
    prompt = f"Summarize this for students in bullet points:\n{text}"
    return ask_llm(prompt)

def rewrite_text(text):
    prompt = f"Rewrite this in plagiarism-free academic style:\n{text}"
    return ask_llm(prompt)

def generate_citation(text):
    prompt = f"Generate APA and MLA citation from:\n{text[:2000]}"
    return ask_llm(prompt)

# ---------------------------
# UI TABS
# ---------------------------
tab1, tab2, tab3 = st.tabs(["📤 Summary", "🔁 Rewrite", "📚 Citation"])

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)

    # -------- SUMMARY --------
    with tab1:
        st.subheader("📑 Summary")

        if st.button("Generate Summary"):
            sections = split_sections(text)

            for sec, content in sections.items():
                st.markdown(f"### {sec}")

                if content.strip():
                    with st.spinner("Processing..."):
                        summary = summarize_section(content[:1500])
                    st.write(summary)
                else:
                    st.info("Not found")

    # -------- REWRITE --------
    with tab2:
        st.subheader("🔁 Rewrite")

        input_text = st.text_area("Paste text (or leave empty to use PDF)")

        if st.button("Rewrite"):
            target = input_text if input_text else text[:1500]

            with st.spinner("Rewriting..."):
                result = rewrite_text(target)

            st.write(result)

    # -------- CITATION --------
    with tab3:
        st.subheader("📚 Citation")

        if st.button("Generate Citation"):
            with st.spinner("Generating..."):
                result = generate_citation(text)

            st.write(result)
