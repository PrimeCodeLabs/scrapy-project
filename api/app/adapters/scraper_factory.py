import json
import logging
from urllib.parse import urlparse
from app.adapters.scraping import ScrapyScraper
from app.adapters.base_scraper import BaseScraper
from app.services.strategy_service import StrategyService
from app.adapters.scraping_strategies import QuotesStrategy, BooksStrategy, AmazonStrategy

logger = logging.getLogger(__name__)

class ScraperFactory:
    STRATEGY_MAP = {
        'quotes.toscrape.com': QuotesStrategy,
        'books.toscrape.com': BooksStrategy,
        'amazon.co.uk': AmazonStrategy
    }

    @classmethod
    def get_scraper(cls, url: str, strategy_service: StrategyService, repo) -> BaseScraper:
        logger.info(f"Getting scraper for URL: {url}")
        hostname = urlparse(url).hostname
        config = strategy_service.get_strategy(hostname)

        if not config:
            logger.error(f"No scraper found for URL: {url}")
            raise ValueError(f"No scraper found for URL: {url}")
        
        logger.info(f"Loaded strategy: {config}")
        logger.info(f"Hostname extracted: {hostname}")

        website = config.get("website")
        logger.info(f"Checking scraper for website {website} with pattern {website}")
        if website == hostname:
            strategy_class = cls.STRATEGY_MAP.get(hostname)
            if not strategy_class:
                logger.error(f"No strategy class found for name: {hostname}")
                raise ValueError(f"No strategy class found for name: {hostname}")
            
            strategy_instance = strategy_class()
            logger.info(f"Found matching scraper for URL: {url} with strategy: {hostname}")
            return ScrapyScraper(strategy_instance, repo)
        else:
            logger.info(f"No match for pattern {website} in hostname {hostname}")

        logger.error(f"No scraper found for URL: {url}")
        raise ValueError(f"No scraper found for URL: {url}")
