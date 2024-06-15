# src/adapters/scraping/beautifulsoup_scraper.py
import requests
from bs4 import BeautifulSoup

class BeautifulSoupScraper:
    def scrape(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        data = []
        for item in soup.find_all('div', class_='item'):
            title = item.find('h2').get_text()
            content = item.find('p').get_text()
            data.append({'title': title, 'content': content, 'source': url})
        return data
