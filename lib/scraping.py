import logging
import signal
from scrapy import Request, Spider
from scrapy.crawler import CrawlerProcess
from lib.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class ScrapyScraper(BaseScraper):
    def __init__(self, strategy, output_file='output.csv'):
        self.strategy = strategy
        self.output_file = output_file
        self.process = None

    def scrape(self, url: str, max_pages: int):
        if not self.strategy:
            raise ValueError(f"No strategy found for URL: {url}")

        if self.process and self.process.crawling:
            self.process.stop()

        self.process = CrawlerProcess(settings={
            'FEEDS': {
                self.output_file: {
                    'format': 'csv',
                    'encoding': 'utf8',
                    'store_empty': False,
                    'fields': None,
                    'indent': 4,
                },
            },
            'LOG_LEVEL': 'INFO',
            # 'DOWNLOAD_DELAY': 3,  # Increased delay to reduce request rate
            'RANDOMIZE_DOWNLOAD_DELAY': True,
            # 'CONCURRENT_REQUESTS': 2,  # Fewer concurrent requests to reduce load
            'RETRY_TIMES': 10,  # Increased retry times
            'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
            'USER_AGENTS': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            ],
            'DOWNLOADER_MIDDLEWARES': {
                'lib.middlewares.RandomUserAgentMiddleware': 400,
                'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
                'scrapy.downloadermiddlewares.retry.RetryMiddleware': 543,
                'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
            },
            'ROTATING_PROXY_LIST': [
                    "http://138.68.60.8:8080",
                    "http://47.89.184.18:3128",
                    "http://91.189.177.188:3128",
                    "http://103.36.136.138:8090",
                    "http://221.140.235.236:5002",
                    "http://222.88.167.22:9002",
                    "http://60.12.168.114:9002",
                    "http://67.43.228.253:1217",
                    "http://12.186.205.123:80",
                    "http://198.160.7.15:80",
                    "http://103.89.233.226:82",
                    "http://78.28.152.113:80",
                    "http://103.168.38.246:80",
                    "http://116.63.129.202:6000",
                    "http://147.182.180.242:80",
                    "http://74.48.78.52:80",
                    "http://67.43.227.227:18213",
                    "http://198.49.68.80:80",
                    "http://120.194.4.157:82",
                    "http://72.10.164.178:29567",
                    "http://39.191.223.9:3128",
                    "http://89.116.34.113:80",
                    "http://50.231.0.43:4481",
                    "http://84.252.73.132:4444",
                    "http://185.199.53.73:80",
                    "http://45.9.75.76:4444",
            ],
        })

        def handle_sigint(signal, frame):
            logger.info("Received SIGINT, shutting down Scrapy process gracefully...")
            self.process.stop()

        signal.signal(signal.SIGINT, handle_sigint)

        print("Starting Scrapy process...")

        try:
            self.process.crawl(ScrapySpider, strategy=self.strategy, start_url=url, max_pages=max_pages)
            self.process.start()
        except Exception as e:
            logger.error(f"Error during Scrapy process: {str(e)}")
        finally:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
      
class ScrapySpider(Spider):
    name = "generic_spider"

    def __init__(self, strategy, start_url=None, max_pages=1, *args, **kwargs):
        super(ScrapySpider, self).__init__(*args, **kwargs)
        self.strategy = strategy
        self.start_urls = [start_url]
        self.max_pages = max_pages
        self.pages_scraped = 0

    def parse(self, response):
        self.pages_scraped += 1
        logger.info(f"Scraping page {self.pages_scraped} of {self.max_pages}")

        for result in self.strategy.parse(response, self.max_pages, self.pages_scraped):
            if isinstance(result, dict):
                result['url'] = self.start_urls[0]
                logger.debug(f"Extracted item: {result}")
                yield result
            elif isinstance(result, Request):
                yield result
            else:
                logger.error(f"Unexpected result type: {type(result)}")