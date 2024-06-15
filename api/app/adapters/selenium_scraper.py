from selenium import webdriver

class SeleniumScraper:
    def __init__(self, driver_path):
        self.driver = webdriver.Chrome(executable_path=driver_path)

    def scrape(self, url):
        self.driver.get(url)
        data = []
        items = self.driver.find_elements_by_class_name('item')
        for item in items:
            title = item.find_element_by_tag_name('h2').text
            content = item.find_element_by_tag_name('p').text
            data.append({'title': title, 'content': content, 'source': url})
        return data
