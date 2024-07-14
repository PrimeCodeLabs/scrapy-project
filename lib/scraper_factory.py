import json
import logging
from urllib.parse import urlparse
from lib.scraping import ScrapyScraper
from lib.base_scraper import BaseScraper
from lib.strategy_service import StrategyService
from lib.scraping_strategies import (QuotesStrategy, BooksStrategy, AmazonStrategy, SaaSworthyStrategy, MorrisonsDealsStrategy)

logger = logging.getLogger(__name__)

class ScraperFactory:
    STRATEGY_MAP = {
        'quotes.toscrape.com': QuotesStrategy,
        'books.toscrape.com': BooksStrategy,
        'amazon.co.uk': AmazonStrategy,
        'saasworthy.com': SaaSworthyStrategy,
        'groceries.morrisons.com': MorrisonsDealsStrategy,
    }

    @classmethod
    def get_scraper(cls, url: str, file_path) -> BaseScraper:
        logger.info(f"Getting scraper for URL: {url}")
        hostname = urlparse(url).hostname
        logger.info(f"Getting scraper for hostname: {hostname}")
        strategy_class = cls.STRATEGY_MAP.get(hostname)
    
        if strategy_class:
            strategy_class = cls.STRATEGY_MAP.get(hostname)
            if not strategy_class:
                logger.error(f"No strategy class found for name: {hostname}")
                raise ValueError(f"No strategy class found for name: {hostname}")
            
            strategy_instance = strategy_class()
            logger.info(f"Found matching scraper for URL: {url} with strategy: {hostname}")
            return ScrapyScraper(strategy_instance, file_path)
        else:
            logger.info(f"No match for hostname {hostname}")

        logger.error(f"No scraper found for URL: {url}")
        raise ValueError(f"No scraper found for URL: {url}")
