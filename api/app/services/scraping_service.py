class ScrapingService:
    def __init__(self, scraper, repository):
        self.scraper = scraper
        self.repository = repository

    def scrape(self, url, max_results):
        return self.scraper.scrape(url, max_results)
