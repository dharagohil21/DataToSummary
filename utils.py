from bs4 import BeautifulSoup
import os

def extractTextFromHtml(html):
    """Convert HTML content to plain text"""
    soup = BeautifulSoup(html, "html.parser")
    return soup.getText(separator="\n", strip=True)

def ensureDir(path):
    """Ensure that the given directory exists"""
    os.makedirs(path, exist_ok=True)