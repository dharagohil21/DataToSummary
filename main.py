from confluenceData import ConfluenceCrawler
from summarization import summarization
from config import START_PAGE_ID, OUTPUT_DIR
#from summarize import summarize
import os

if __name__ == "__main__":
    print("Starting python code...\n")
    crawler = ConfluenceCrawler()
    print("Starting crawl...\n")
    crawler.crawlPage(START_PAGE_ID)
    print("\nCrawl complete!")
    print("Starting summarization...\n")
    try:
        files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".txt")]
    except FileNotFoundError:
        print(f"Output directory not found: {OUTPUT_DIR}")
        exit(1)

    if not files:
        print(f"No .txt files found in {OUTPUT_DIR}. Nothing to summarize.")
        exit(0)
        
    print(f"Found {len(files)} .txt file(s). Starting summarization...\n")
    for filename in files:
        filepath = os.path.join(OUTPUT_DIR, filename)
        print(f"Summarizing file: {filepath}")
        #summary = summarize.summarize_file(filepath)
        summary = summarization.summarize_file(filepath)
        print("Summarization complete!\n")
        print(f"Summary:\n {summary}")
    
