from abc import ABC, abstractmethod
import scrapy

class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, url: str):
        pass

class BaseStrategy(ABC):
    @abstractmethod
    def parse(self, response):
        pass

class ScrapySpider(scrapy.Spider):
    name = "generic_spider"

    def __init__(self, strategy: BaseStrategy, start_url=None, *args, **kwargs):
        super(ScrapySpider, self).__init__(*args, **kwargs)
        self.strategy = strategy
        self.start_urls = [start_url]

    def parse(self, response):
        yield from self.strategy.parse(response)
