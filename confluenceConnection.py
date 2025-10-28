import requests, re
from bs4 import BeautifulSoup, Tag
from requests.auth import HTTPBasicAuth
from config import BASE_URL, EMAIL, API_TOKEN
from utils import extractTextFromHtml

class ConfluenceClient:
    def __init__(self):
        self.auth = HTTPBasicAuth(EMAIL, API_TOKEN)
        self.headers = {"Accept": "application/json"}

    def getPage(self, page_id):
        """Fetch a specific Confluence page by ID"""
        url = f"{BASE_URL}/rest/api/content/{page_id}"
        params = {"expand": "body.storage,version,ancestors,children.page"}
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()
        return response.json()
    
    # def extract_section(self, data, section_name: str) -> str:
    #     storage = data["body"]["storage"]["value"] 

    #     if not storage:
    #         raise SystemExit("No storage body found for that page (check PAGE_ID and permissions).")

    #     # Parse storage format and find the excerpt macro
    #     soup = BeautifulSoup(storage, "xml")  # storage is XML-like
    #     excerpt = soup.find_all("ac:structured-macro", {"ac:name": "excerpt"})

    #     if not excerpt:
    #         raise SystemExit("No Excerpt macro found on page.")
        
    #     target_excerpt = None
    #     for ex in excerpt:
    #         param = ex.find("ac:parameter", {"ac:name": "name"})
    #         name_value = param.get_text(strip=True) if param else ""
    #         if name_value.lower() == section_name.lower():
    #             target_excerpt = ex
    #             break

    #     if not target_excerpt:
    #         raise SystemExit(f"No excerpt named '{section_name}' found.")

    #     # --- STEP 4: Extract the body of that excerpt ---
    #     body = target_excerpt.find("ac:rich-text-body")
    #     section_html = "".join(str(child) for child in body.contents)
    #     text = extractTextFromHtml(section_html)
    #     return text 


    def extract_section(self, html: str, section_name: str) -> str:
        """Finds the text under a given heading (e.g., Skills, Education)."""
        soup = BeautifulSoup(html, "html.parser")
        #section_pattern = re.compile(rf"\b{re.escape(section_name)}\b", re.I)
        heading = None
        for level in range(1, 7):
            found = soup.find_all(f"h{level}")
            for h in found:
                if  section_name.lower() in h.get_text(strip=True).lower():
                    heading = h
                    heading_level = level
                    break
            if heading:
                break

        if not heading:
            raise SystemExit(f"Heading '{section_name}' not found on the page.")

        # Collect the heading and all following siblings until the next heading of same or higher level
        collected = [str(heading)]
        for sib in heading.next_siblings:
            # skip strings that are just whitespace/newline
            if isinstance(sib, str) and not sib.strip():
                continue
            # If sibling is a Tag and is heading of same or higher level, stop.
            if getattr(sib, "name", None) and sib.name.startswith("h"):
                try:
                    lvl = int(sib.name[1])
                except Exception:
                    lvl = 100
                if lvl <= heading_level:
                    break
            collected.append(str(sib))

        section_html = "\n".join(collected)
        text = extractTextFromHtml(section_html)
        return text