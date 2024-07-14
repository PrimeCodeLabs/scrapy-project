class ScrapingService:
    def __init__(self, scraper):
        self.scraper = scraper

    def scrape(self, url, max_results):
        return self.scraper.scrape(url, max_results)
