import streamlit as st
import os
from groq import Groq
import PyPDF2
import re

# ---------------------------
# SETUP GROQ CLIENT
# ---------------------------
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

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
# GROQ LLM FUNCTION
# ---------------------------
def ask_llm(prompt):
    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content

# ---------------------------
# SUMMARIZATION
# ---------------------------
def summarize_section(text):
    prompt = f"""
    Summarize the following research section in bullet points for undergraduate students:

    {text}
    """
    return ask_llm(prompt)

# ---------------------------
# REWRITING (PLAGIARISM FREE)
# ---------------------------
def rewrite_text(text):
    prompt = f"""
    Rewrite the following text in a plagiarism-free academic style.
    Keep the meaning same but change wording completely:

    {text}
    """
    return ask_llm(prompt)

# ---------------------------
# CITATION GENERATION
# ---------------------------
def generate_citation(text):
    prompt = f"""
    Extract details and generate APA and MLA citation from this research paper:

    {text[:2000]}
    """
    return ask_llm(prompt)

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="AI Research Assistant", layout="wide")

st.title("📄 AI Research Paper Assistant")
st.markdown("### ✨ Summarize | Rewrite | Cite — Smart Academic Tool")

# Tabs (GenZ + HCI style)
tab1, tab2, tab3 = st.tabs(["📤 Upload & Summary", "🔁 Rewrite", "📚 Citation"])

uploaded_file = st.file_uploader("Upload Research Paper (PDF)", type=["pdf"])

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)

    # ---------------------------
    # TAB 1: SUMMARY
    # ---------------------------
    with tab1:
        st.subheader("📑 Section-wise Summary")

        if st.button("⚡ Generate Summary"):
            sections = split_sections(text)

            for sec, content in sections.items():
                if content.strip():
                    st.markdown(f"### {sec}")
                    with st.spinner(f"Summarizing {sec}..."):
                        summary = summarize_section(content[:2000])
                    st.write(summary)
                else:
                    st.markdown(f"### {sec}")
                    st.info("Not found in document")

    # ---------------------------
    # TAB 2: REWRITE
    # ---------------------------
    with tab2:
        st.subheader("🔁 Plagiarism-Free Rewriting")

        input_text = st.text_area("Paste text to rewrite OR use full paper below:")

        if st.button("✨ Rewrite Text"):
            target_text = input_text if input_text else text[:2000]

            with st.spinner("Rewriting..."):
                rewritten = rewrite_text(target_text)

            st.success("Done!")
            st.write(rewritten)

    # ---------------------------
    # TAB 3: CITATION
    # ---------------------------
    with tab3:
        st.subheader("📚 Generate Citation")

        if st.button("📌 Generate APA & MLA Citation"):
            with st.spinner("Generating citation..."):
                citation = generate_citation(text)

            st.success("Citation Ready!")
            st.write(citation)
