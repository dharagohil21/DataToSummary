from confluenceConnection import ConfluenceClient
from utils import extractTextFromHtml
import pandas as pd
import os
from config import OUTPUT_DIR

class ConfluenceCrawler:
    def __init__(self):
        self.client = ConfluenceClient()
        self.visited = set()

    def crawlPage(self, pageId, depth=0):
        """Recursively crawl a Confluence page and its children"""
        if pageId in self.visited:
            return
        self.visited.add(pageId)

        pageData = self.client.getPage(pageId)
        title = pageData.get("title")
        bodyHtml = pageData.get("body", {}).get("storage", {}).get("value", "")
        print("  " * depth + f"📄 {title}")
        print("Extracting text from page:", title)
        bodyText = extractTextFromHtml(bodyHtml)
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filePath = os.path.join(OUTPUT_DIR, f"{title}.txt")
        
        with open(filePath, "w", encoding="utf-8") as f:
            f.write(bodyText)
            
        print(f"✅ Page '{title}' saved to:\n - {filePath}")

        children = pageData.get("children", {}).get("page", {}).get("results", [])
        for child in children:
            childId = child["id"]
            self.crawlPage(childId, depth + 1)
     