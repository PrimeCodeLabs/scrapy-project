import click
import logging
from lib.scraper_factory import ScraperFactory
from lib.scraping_service import ScrapingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    logger.info(f"Scraping URL: {url}")
    scraper = ScraperFactory.get_scraper(url, file_path)
    scraping_service = ScrapingService(scraper)
    
    try:
        data = scraping_service.scrape(url, max_pages)
        click.echo(f"Scraping successful. Retrieved data: {data}")
    except ValueError as e:
        logger.error(e)
        click.echo(f"Error: {e}")

if __name__ == "__main__":
    cli()
