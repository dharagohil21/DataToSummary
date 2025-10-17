
import requests
from requests.auth import HTTPBasicAuth
from config import BASE_URL, EMAIL, API_TOKEN

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

    """
    def get_space_pages(self, space_key, limit=50, start=0):
        ""Fetch all pages from a given space (paginated)""
        url = f"{BASE_URL}/rest/api/content"
        params = {
            "spaceKey": space_key,
            "limit": limit,
            "start": start,
            "expand": "body.storage,version"
        }
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()
        return response.json()
    """