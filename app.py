import io
from typing import List
import pandas as pd

import streamlit as st
import pdfplumber
from docx import Document

from src.extractors import load_rules, extract_fields

# ----------- CONFIG -----------

HIGH_VALUE_THRESHOLD = 5000
st.write("🚨 NEW VERSION LOADED 🚨")
st.set_page_config(
    page_title="SentientDocFLO",
    layout="wide"
)

# ----------- STYLE (FONT + COLORS) -----------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap');

/* Global Font */
html, body, [class*="css"] {
    font-family: 'Michroma', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #1e1b4b);
    color: #e2e8f0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #7c3aed, #38bdf8);
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

/* Metrics */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    padding: 12px;
    border-radius: 10px;
}

/* Spacing */
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ----------- HERO -----------

st.markdown("""
<div style="text-align:center;">
    <h1 style="
        font-family: 'Michroma', sans-serif;
        background: linear-gradient(90deg, #a78bfa, #38bdf8, #22d3ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
    ">
        SentientDocFLO
    </h1>

    <p style="color:#94a3b8; font-size:14px;">
        Intelligent Document Processing • Automated • Accurate • Scalable
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ----------- PIPELINE -----------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="font-family: 'Michroma', sans-serif;">
        <h3>📥 Input</h3>
        <p>PDF<br>DOCX<br>Multi-file Upload</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="font-family: 'Michroma', sans-serif;">
        <h3>🧠 Processing</h3>
        <p>
        Text Extraction<br>
        Classification<br>
        Field Detection<br>
        Validation
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="font-family: 'Michroma', sans-serif;">
        <h3>📤 Output</h3>
        <p>
        Structured Data<br>
        Alerts<br>
        CSV Export
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ----------- LOAD RULES -----------

invoice_rules = load_rules("rules/invoice_rules.yaml")
bank_rules = load_rules("rules/bank_statement_rules.yaml")

# ----------- DETECTION -----------

def detect_document_type(text: str) -> str:
    text_lower = text.lower()

    if "invoice" in text_lower:
        return "invoice"
    elif "account" in text_lower or "statement" in text_lower:
        return "bank_statement"
    else:
        return "unknown"

# ----------- EXTRACTION -----------

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

# ----------- VALIDATION -----------

def check_missing_fields(fields: dict):
    return [k for k, v in fields.items() if v in (None, "", "unknown")]

def flag_high_value(fields: dict):
    amount = fields.get("amount_due") or fields.get("balance")

    try:
        if amount:
            return float(amount) > HIGH_VALUE_THRESHOLD
    except:
        return False

    return False

# ----------- SIDEBAR -----------

with st.sidebar:
    st.title("Upload Documents")

    uploaded_files = st.file_uploader(
        "Upload PDF or DOCX",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

# ----------- MAIN -----------

results = []
total_missing = 0

if uploaded_files:

    with st.spinner("Processing..."):

        for uf in uploaded_files:
            st.markdown("---")
            st.subheader(f"{uf.name}")

            if uf.name.endswith(".pdf"):
                text = read_pdf(uf)
            else:
                text = read_docx(uf)

            st.text_area("Extracted Text", text, height=200)

            doc_type = detect_document_type(text)

            if doc_type == "invoice":
                fields = extract_fields(text, invoice_rules)
            elif doc_type == "bank_statement":
                fields = extract_fields(text, bank_rules)
            else:
                fields = {}

            fields["document_type"] = doc_type

            missing = check_missing_fields(fields)
            high_value = flag_high_value(fields)

            total_missing += len(missing)

            st.json(fields)

            if missing:
                st.warning(f"Missing: {missing}")

            if high_value:
                st.error("High Value Detected")

            row = {"file": uf.name}
            row.update(fields)
            row["missing"] = ", ".join(missing)
            row["high_value"] = high_value

            results.append(row)

# ----------- OUTPUT -----------

if results:
    st.markdown("---")
    st.markdown("## Output Dataset")

    df = pd.DataFrame(results)

    col1, col2, col3 = st.columns(3)

    col1.metric("Documents", len(results))
    col2.metric("Fields", df.shape[1])
    col3.metric("Missing", total_missing)

    st.dataframe(df)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "output.csv"
    )