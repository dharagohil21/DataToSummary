from confluenceConnection import ConfluenceClient

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
        body_html = pageData.get("body", {}).get("storage", {}).get("value", "")
        print("  " * depth + f"📄 {title}")

        # Save or process data (store in DB, file, etc.)
        # Example: save to a dictionary or JSON

        children = pageData.get("children", {}).get("page", {}).get("results", [])
        for child in children:
            childId = child["id"]
            self.crawl_page(childId, depth + 1)