import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

import click
import logging
from app.adapters.scraping import ScrapyScraper
from app.core.repositories.mongo_repository import MongoStrategyRepository
from app.core.repositories.csv_repository import CsvRepository
from app.adapters.scraper_factory import ScraperFactory
from app.services.scraping_service import ScrapingService
from app.services.strategy_service import StrategyService
from app.core.use_cases.manage_strategies_use_case import ManageStrategiesUseCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo_strategy_repo = MongoStrategyRepository(os.getenv('MONGO_URI'), 'scraping_db')
strategy_service = StrategyService(mongo_strategy_repo)




@click.group()
def cli():
    """CLI for the Scraping Application."""
    pass

@cli.command()
@click.argument('url')
@click.option('--max_pages', default=1, help='The maximum number of pages to scrape.')
@click.option('--file_path', default="./output", help='The path of the file with scraped data.')
def scrape(url, max_pages, file_path):
    """Scrape the given URL."""
    repository = CsvRepository(file_path)
    scraper = ScraperFactory.get_scraper(url, ManageStrategiesUseCase(mongo_strategy_repo), repository)
    scraping_service = ScrapingService(scraper, repository)
    
    try:
        data = scraping_service.scrape(url, max_pages)
        click.echo(f"Scraping successful. Retrieved data: {data}")
    except ValueError as e:
        logger.error(e)
        click.echo(f"Error: {e}")

if __name__ == "__main__":
    cli()
