from .base_scraper import BaseStrategy
import logging

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
            
class BooksStrategy(BaseStrategy):
    def __init__(self):
        self.pages_scraped = 0

    def parse(self, response, max_pages, pages_scraped=1):
        for book in response.css('article.product_pod'):
            yield {
                'title': book.css('h3 a::attr(title)').get(),
                'price': book.css('div.product_price p.price_color::text').get(),
                'availability': book.css('div.product_price p.availability::text').get().strip(),
            }
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None and self.pages_scraped < max_pages:
            yield response.follow(next_page, self.parse, cb_kwargs={'max_pages': max_pages, 'pages_scraped': pages_scraped + 1})
        else:
            logger.info(f"Reached the maximum number of pages: {max_pages}")


class AmazonStrategy(BaseStrategy):
    def __init__(self):
        self.pages_scraped = 0

    def parse(self, response, max_pages, pages_scraped=1):
        self.pages_scraped += 1
        logger.info(f"Scraping page {pages_scraped} of {max_pages}")

        for product in response.css('div.s-main-slot div.s-result-item'):
            title = product.css('h2 a span::text').get()
            price_whole = product.css('span.a-price-whole::text').get()
            price_fraction = product.css('span.a-price-fraction::text').get()
            price = (price_whole or '') + (price_fraction or '')
            availability = product.css('span.a-declarative span::text').get()

            if title and price:
                yield {
                    'title': title,
                    'price': price,
                    'availability': availability,
                }
            else:
                logger.warning(f"Missing data for product: {product.extract()}")

        if pages_scraped < max_pages:
            next_page = response.css('ul.a-pagination li.a-last a::attr(href)').get()
            if next_page is not None:
                logger.info(f"Following next page link: {next_page}")
                yield response.follow(next_page, self.parse, cb_kwargs={'max_pages': max_pages, 'pages_scraped': pages_scraped + 1})
        else:
            logger.info(f"Reached the maximum number of pages: {max_pages}")