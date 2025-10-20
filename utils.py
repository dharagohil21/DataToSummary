from bs4 import BeautifulSoup
import os
import re
from pathlib import Path

def extractTextFromHtml(html):
    """Convert HTML content to plain text"""
    soup = BeautifulSoup(html, "html.parser")
    return soup.getText(separator="\n", strip=True)

def ensureDir(path):
    """Ensure that the given directory exists"""
    os.makedirs(path, exist_ok=True)

def clean_text(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip()

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200):
    """
    chunk_size ~ characters (or tokens if you convert)
    overlap ~ characters overlap between chunks
    returns list of chunk strings
    """
    text = clean_text(text)
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks