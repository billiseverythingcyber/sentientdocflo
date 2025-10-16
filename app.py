import io
from typing import List

import streamlit as st
import pdfplumber
from docx import Document

st.set_page_config(page_title="SentientDocFlo — Week 1", layout="wide")
st.title("📄 SentientDocFlo — Document Intelligence (Week 1)")
st.write("Upload a PDF or DOCX. We'll show the words inside. Baby steps!")

with st.sidebar:
st.header("Upload")
uploaded_files = st.file_uploader(
"Upload files", type=["pdf", "docx"], accept_multiple_files=True
)
export_all = st.checkbox("Enable per-file text download", value=True)


def read_pdf(file) -> str:
"""Extracts text from a PDF file-like object using pdfplumber."""
text_parts: List[str] = []
try:
with pdfplumber.open(file) as pdf:
for page in pdf.pages:
text_parts.append(page.extract_text() or "")
except Exception as e:
return f"[PDF read error] {e}"
return "
".join(text_parts).strip()


def read_docx(file) -> str:
"""Extracts text from a DOCX file-like object using python-docx."""
try:
doc = Document(file)
return "
".join(p.text for p in doc.paragraphs).strip()
except Exception as e:
return f"[DOCX read error] {e}"


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

st.text_area("Extracted Text", text, height=260, key=f"ta_{uf.name}")

if export_all and text and not text.startswith("["):
st.download_button(
label="Download extracted text (.txt)",
data=text.encode("utf-8"),
file_name=f"{uf.name.rsplit('.', 1)[0]}_text.txt",
mime="text/plain",
key=f"dl_{uf.name}",
)
else:
st.info("Tip: try a simple sample file; we’ll add smart extraction next week.")