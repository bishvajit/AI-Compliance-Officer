# backend/main.py
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import faiss
import os
import re
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA

app = FastAPI()

# -----------------------------
# 1. Load Regulation Knowledge Base
# -----------------------------
regulations = """
GDPR Article 5: Personal data must be collected for specified, explicit purposes and not kept longer than necessary.
GDPR Article 25: Data protection must be implemented by design and by default.
DPDP Act Section 4: Personal data should not be processed without user consent.
"""

# Split & Embed Regulations
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
docs = splitter.split_text(regulations)

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(docs, embeddings)

qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    retriever=vectorstore.as_retriever()
)

# -----------------------------
# 2. Risk Detection Helper
# -----------------------------
def detect_pii(text: str) -> List[str]:
    risks = []
    if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text):
        risks.append("Email addresses detected (PII risk).")
    if re.search(r"\b\d{10}\b", text):
        risks.append("Phone numbers detected (PII risk).")
    if re.search(r"\b\d{12}\b", text):
        risks.append("Possible Aadhaar number detected (PII risk).")
    return risks

# -----------------------------
# 3. API Endpoints
# -----------------------------
class ComplianceReport(BaseModel):
    risks: List[str]
    compliance_analysis: str

@app.post("/analyze", response_model=ComplianceReport)
async def analyze_document(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    # Run PII detection
    risks = detect_pii(text)

    # Run Compliance Check with LLM
    query = f"Check this document for GDPR/DPDP violations:\n{text[:1000]}"
    compliance = qa_chain.run(query)

    return {"risks": risks, "compliance_analysis": compliance}
