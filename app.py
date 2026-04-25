import io
from typing import List
import pandas as pd

import streamlit as st
import pdfplumber
from docx import Document

from src.extractors import load_rules, extract_fields

# ----------- CONFIG -----------

RULES_PATH = "rules/invoice_rules.yaml"

st.set_page_config(page_title="SentientDocFlo — Week 2", layout="wide")
st.title("📄 SentientDocFlo — Document Intelligence (Week 2)")
st.write("Upload files → Extract text → Detect structured fields → Export CSV")

# ----------- LOAD RULES -----------

rules = load_rules(RULES_PATH)

# ----------- SIDEBAR -----------

with st.sidebar:
    st.header("Upload")
    uploaded_files = st.file_uploader(
        "Upload files", type=["pdf", "docx"], accept_multiple_files=True
    )
    export_all = st.checkbox("Enable per-file text download", value=True)

# ----------- TEXT EXTRACTION -----------

def read_pdf(file) -> str:
    text_parts: List[str] = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
    except Exception as e:
        return f"[PDF read error] {e}"

    return "\n".join(text_parts).strip()


def read_docx(file) -> str:
    try:
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        return f"[DOCX read error] {e}"

# ----------- MAIN -----------

results = []

if uploaded_files:
    for uf in uploaded_files:
        st.markdown("---")
        st.subheader(f"Preview: {uf.name}")

        if uf.name.lower().endswith(".pdf"):
            text = read_pdf(uf)
        else:
            text = read_docx(uf)

        if not text:
            text = "(no selectable text found)"

        st.text_area("Extracted Text", text, height=200, key=f"ta_{uf.name}")

        # ----------- FIELD EXTRACTION -----------

        fields = extract_fields(text, rules)

        st.subheader("🔎 Detected Fields")
        st.json(fields)

        # ----------- SAVE RESULT -----------

        row = {"file_name": uf.name}
        row.update(fields)
        results.append(row)

        # ----------- DOWNLOAD TEXT -----------

        if export_all and text and not text.startswith("["):
            st.download_button(
                label="Download extracted text (.txt)",
                data=text.encode("utf-8"),
                file_name=f"{uf.name.rsplit('.', 1)[0]}_text.txt",
                mime="text/plain",
                key=f"dl_{uf.name}",
            )

# ----------- CSV OUTPUT -----------

if results:
    st.markdown("## 📊 Summary Table")
    df = pd.DataFrame(results)
    st.dataframe(df)

    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="extracted_data.csv",
        mime="text/csv",
    )