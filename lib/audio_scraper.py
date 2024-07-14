from datetime import datetime
from lib.base_scraper import BaseStrategy
import logging
import requests
from pydub import AudioSegment
import speech_recognition as sr
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class PodcastScraperStrategy(BaseStrategy):
    def __init__(self):
        self.pages_scraped = 0

    def parse(self, response, max_pages, pages_scraped=1):
        for podcast in response.css('div.podcast'):
            item = {
                'title': podcast.css('h2.title::text').get(),
                'author': podcast.css('span.author::text').get(),
                'date': podcast.css('span.date::text').get(),
                'audio_url': podcast.css('audio::attr(src)').get(),
            }
            if item['audio_url']:
                yield self.download_and_transcribe(item)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None and pages_scraped < max_pages:
            self.pages_scraped += 1
            yield response.follow(next_page, self.parse, cb_kwargs={'max_pages': max_pages, 'pages_scraped': pages_scraped + 1})
        else:
            logger.info(f"Reached the maximum number of pages: {max_pages}")

    def download_and_transcribe(self, item):
        # Download audio file
        audio_response = requests.get(item['audio_url'])
        audio_filename = f"{item['title'].replace(' ', '_')}.mp3"
        with open(audio_filename, 'wb') as f:
            f.write(audio_response.content)

        # Convert audio to WAV format
        audio = AudioSegment.from_mp3(audio_filename)
        wav_filename = audio_filename.replace('.mp3', '.wav')
        audio.export(wav_filename, format='wav')

        # Transcribe audio file
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_filename) as source:
            audio_data = source.record(source)
            try:
                transcription = recognizer.recognize_google(audio_data)
                item['transcription'] = transcription
                item['scraped_date'] = datetime.now().isoformat()
                return item
            except sr.UnknownValueError:
                logger.error(f"Could not transcribe audio for {item['title']}")
            except sr.RequestError as e:
                logger.error(f"Error with the transcription service: {e}")

        return None

    def parse_transcription(self, transcription):
        # Placeholder for NLP tasks like extracting key phrases, sentiment analysis, etc.
        # Use libraries like spaCy, NLTK, or TextBlob
        pass
