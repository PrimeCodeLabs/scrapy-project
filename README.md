# Scrapy Web Scraping Project

This project is designed to scrape data from various websites using Scrapy and custom scraping strategies. It includes a generic spider that can handle different strategies and repositories for storing scraped data.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Custom Strategies](#custom-strategies)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/PrimeCodeLabs/scrapy-project.git
cd scrapy-project
```

2. **Create a virtual environment and activate it:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install the required dependencies:**

```bash
pip install -r requirements.txt
```

## Usage

To start scraping a website, you need to define the scraping strategy and the repository for storing the data.

### Example Command

```python
from lib.scraping import ScrapyScraper
from lib.scraping_strategies import QuotesStrategy
from lib.scraping_service import StrategyService

url = 'https://quotes.toscrape.com'
strategy = QuotesStrategy()
scraper = ScrapyScraper(strategy, output_file='output.csv')
data = scraper.scrape(url, max_pages=5)

print(data)
```

## Project Structure

- **cli.py**: Entry point for command-line interactions.
- **docker-compose.yml**: Docker configuration file.
- **lib/base_scraper.py**: Base class for scrapers.
- **lib/scraper_factory.py**: Factory for creating scrapers.
- **lib/scraping.py**: Contains the `ScrapyScraper` class and the `ScrapySpider` class.
- **lib/scraping_service.py**: Service for managing scraping tasks.
- **lib/scraping_strategies.py**: Contains the custom scraping strategies.
- **lib/strategy_service.py**: Service for retrieving the appropriate scraping strategy.
- **requirements.txt**: List of required dependencies.
- **saasworthy.csv**: Output file for scraped data.

## Custom Strategies

You can define custom strategies for different websites by inheriting from `BaseStrategy` and implementing the `parse` method.

### Example Strategy

```python
import logging
from lib.base_scraper import BaseStrategy

logger = logging.getLogger(__name__)

class QuotesStrategy(BaseStrategy):
    def __init__(self):
        self.pages_scraped = 0

    def parse(self, response, max_pages, pages_scraped=1):
        for quote in response.css('div.quote'):
            item = {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }
            if item['text'] and item['author']:
                yield item
            else:
                logger.warning(f"Skipping incomplete item: {item}")

        next_page = response.css('li.next a::attr(href)').get()
        logger.info("Next page is not None")
        logger.info(next_page)
        if next_page is not None and pages_scraped < max_pages:
            self.pages_scraped += 1
            yield response.follow(next_page, self.parse, cb_kwargs={'max_pages': max_pages, 'pages_scraped': pages_scraped})
        else:
            logger.info(f"Reached the maximum number of pages: {max_pages}")
```

## Error Handling

The project includes basic error handling to manage common issues during scraping. Errors and warnings are logged using Python's `logging` module.

### Common Errors

- **TypeError**: Ensure the `parse` method yields dictionaries for items and `Request` objects for follow requests.
- **Connection Errors**: Ensure you have a stable internet connection and the target website is accessible.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
