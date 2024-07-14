from datetime import datetime
from lib.base_scraper import BaseStrategy
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

        next_page = response.css('ul.a-pagination li.a-last a::attr(href)').get()
        if next_page is not None and pages_scraped < max_pages:
            logger.info(f"Following next page link: {next_page}")
            yield response.follow(next_page, self.parse, cb_kwargs={'max_pages': max_pages, 'pages_scraped': pages_scraped + 1})
        else:
            logger.info(f"Reached the maximum number of pages: {max_pages}")

class SaaSworthyStrategy(BaseStrategy):
    def __init__(self):
        self.pages_scraped = 0

    def parse(self, response, max_pages, pages_scraped=1):
        self.pages_scraped += 1
        logger.info(f"Scraping main page {pages_scraped} of {max_pages}")

        # Extract all category URLs
        categories = response.css('a::attr(href)').re(r'/list/[^"]+')
        logger.debug(f"Found categories: {categories}")
        for category_url in categories:
            yield response.follow(category_url, self.parse_category, cb_kwargs={'max_pages': max_pages, 'pages_scraped': 1})

    def parse_category(self, response, max_pages, pages_scraped):
        logger.info(f"Scraping category page: {response.url}")

        # Extract individual product listing URLs using regex
        product_urls = response.css('a::attr(href)').re(r'/product/[^"]+')
        logger.debug(f"Found product URLs: {product_urls}")
        for rank, product_url in enumerate(product_urls, start=1):
            yield response.follow(product_url, self.parse_listing, cb_kwargs={'rank': rank})

        # Handle pagination within the category
        if pages_scraped < max_pages:
            next_page = response.css('li.next a::attr(href)').get()
            if next_page is not None:
                logger.info(f"Following next page link in category: {next_page}")
                yield response.follow(next_page, self.parse_category, cb_kwargs={'max_pages': max_pages, 'pages_scraped': pages_scraped + 1})
        else:
            logger.info(f"Reached the maximum number of pages in category: {max_pages}")

    def parse_listing(self, response, rank):
        logger.info(f"Scraping listing page: {response.url}")

        item = {
            'ListingImageUrl1': response.css('img.b-r-3::attr(src)').get(),
            'ListingRating': response.css('span.rate_txt::text').re_first(r'([\d.]+)'),
            'ListingName': response.css('h1.banner-txt::text').get(),
            'ListingLink1': response.css('a[title="Visit Website"]::attr(href)').get(),
            'ListingDescription1': response.css('p.font-m.f-w-med.italic::text').get(),
            'ListingIconUrl': response.css('img.b-r-3::attr(src)').get(),
            'ListingImageUrl2': response.css('div.screenshot img::attr(src)').get(),
            'ListingUrl': response.url,
            'ListingReviewCount': response.css('span.rate_nmbr::text').re_first(r'(\d+) Ratings'),
            'ListingDescription2': response.css('div.desc-section p::text').get(),
            'ListingDescription3': response.css('div.desc-section p::text').getall(),
            'SellerHq': response.css('div.details-pg-sec-vendor span.d-block::text').get(),
            'ListingScrapeDate': datetime.now().isoformat(),
            'ListingRank': rank,
            'ListingLastUpdated': response.css('p.updtd_date::text').get(),
            'ListingSellerName': response.css('p.f-w-med a::text').get(),
        }

        logger.debug(f"Extracted item: {item}")

        if item['ListingName']:
            yield item
        else:
            logger.warning(f"Skipping incomplete item: {item}")

class MorrisonsDealsStrategy(BaseStrategy):
    def __init__(self):
        self.pages_scraped = 0
        self.seen_urls = set()

    def parse(self, response, max_pages, pages_scraped=1):
        self.pages_scraped += 1
        logger.info(f"Scraping main page {pages_scraped} of {max_pages}")

        # Extract all product data from the current page
        for product in response.css('li.fops-item'):
            item = {
                'ProductName': product.css('div.fop-description h4.fop-title span::text').get(),
                'PackSize': product.css('div.fop-description h4.fop-title span.fop-catch-weight-inline::text').get() or product.css('div.fop-description span.fop-catch-weight::text').get(),
                'CurrentPrice': product.css('div.price-group-wrapper span.fop-price::text').get(),
                'OriginalPrice': self.extract_original_price(product),
                'UnitPrice': product.css('div.price-group-wrapper span.fop-unit-price::text').get(),
                'Rating': self.extract_rating(product),
                'ImageUrl': product.css('div.fop-img-wrapper img.fop-img::attr(src)').get(),
                'OfferDetails': product.css('a.fop-row-promo span::text').get(),
                'ProductUrl': response.urljoin(product.css('div.fop-contentWrapper a::attr(href)').get()),
                'ScrapeDate': datetime.now().isoformat(),
                'url': response.url,
            }

            logger.debug(f"Extracted item: {item}")

            if item['ProductName'] and item['CurrentPrice']:
                yield item
            else:
                logger.warning(f"Skipping incomplete item: {item}")

        # Handle pagination within the main page
        if pages_scraped < max_pages:
            next_page = response.css('a.pagination-next::attr(href)').get()
            if next_page is not None:
                logger.info(f"Following next page link: {next_page}")
                yield response.follow(next_page, self.parse, cb_kwargs={'max_pages': max_pages, 'pages_scraped': pages_scraped + 1})
        else:
            logger.info(f"Reached the maximum number of pages: {max_pages}")

    def extract_original_price(self, product):
        price_str = product.css('div.price-group-wrapper').get()
        if price_str and 'Was' in price_str:
            try:
                return price_str.split('Was ')[1].split('<')[0]
            except IndexError:
                return None
        return None

    def extract_rating(self, product):
        rating_style = product.css('span.fop-rating-inner::attr(style)').get()
        if rating_style:
            try:
                return float(rating_style.split('width: ')[1].replace('%', '')) / 20
            except (IndexError, ValueError):
                return None
        return None