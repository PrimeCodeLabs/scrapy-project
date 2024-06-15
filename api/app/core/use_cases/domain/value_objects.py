# src/core/domain/value_objects.py
class URL:
    def __init__(self, url):
        self.url = url
        self.validate()

    def validate(self):
        if not self.url.startswith('http'):
            raise ValueError("Invalid URL")
