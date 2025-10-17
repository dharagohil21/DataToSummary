from confluenceData import ConfluenceCrawler
from config import START_PAGE_ID

if __name__ == "__main__":
    print("Starting python code...\n")
    crawler = ConfluenceCrawler()
    print("Starting crawl...\n")
    crawler.crawlPage(START_PAGE_ID)
    print("\nCrawl complete!")