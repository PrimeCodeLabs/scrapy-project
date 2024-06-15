import logging
import signal
from pymongo import MongoClient
from scrapy import Request, Spider
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from app.adapters.base_scraper import BaseScraper
from app.services.strategy_service import StrategyService

logger = logging.getLogger(__name__)

class ScrapyScraper(BaseScraper):
    def __init__(self, strategy, repository):
        self.strategy = strategy
        self.repository = repository
        self.process = None  # Initialize process as None

    def scrape(self, url: str, max_pages: int):
        if not self.strategy:
            raise ValueError(f"No strategy found for URL: {url}")

        if self.process and self.process.crawling:
            self.process.stop()

        self.process = CrawlerProcess(settings={
            'LOG_LEVEL': 'INFO',  # Reduce log verbosity
        })

        def handle_sigint(signal, frame):
            logger.info("Received SIGINT, shutting down Scrapy process gracefully...")
            self.process.stop()

        signal.signal(signal.SIGINT, handle_sigint)

        print("Starting Scrapy process...")

        try:
            self.process.crawl(ScrapySpider, strategy=self.strategy, start_url=url, max_pages=max_pages, repository=self.repository)
            self.process.start()
        except Exception as e:
            print(e)
            logger.error(f"Error during Scrapy process: {str(e)}")
        finally:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            if reactor.running:
                reactor.stop()

        # Retrieve data from MongoDB
        logger.info(f"Retrieving data for URL: {url}")
        data = self.repository.get_data({'url': url}, {'_id': False})
        logger.debug(f"Retrieved data: {data}")

        return data
    
class ScrapySpider(Spider):
    name = "generic_spider"

    def __init__(self, strategy, start_url=None, max_pages=1, repository=None, *args, **kwargs):
        super(ScrapySpider, self).__init__(*args, **kwargs)
        self.strategy = strategy
        self.start_urls = [start_url]
        self.max_pages = max_pages
        self.repository = repository
        self.pages_scraped = 0

    def parse(self, response):
        self.pages_scraped += 1
        logger.info(f"Scraping page {self.pages_scraped} of {self.max_pages}")

        for result in self.strategy.parse(response, self.max_pages, self.pages_scraped):
            if isinstance(result, dict):
                result['url'] = self.start_urls[0]
                logger.debug(f"Saving item: {result}")
                yield result
                if self.repository:
                    self.repository.save_data(result)
            elif isinstance(result, Request):
                yield result
            else:
                logger.error(f"Unexpected result type: {type(result)}")