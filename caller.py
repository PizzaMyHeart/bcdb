import requests
import os
from models import Articles
from dotenv import load_dotenv
from extract import Extractor
from database import build_db, print_table, get_all_comments, get_tags, select_column, get_guardian_article_key, get_comment_thread
import json
import time
from custom_types import EntryAlreadyExists
from requests.exceptions import HTTPError
from http import HTTPStatus

load_dotenv()
GUARDIAN_API_KEY = os.environ.get("GUARDIAN_API_KEY")
extractor = Extractor()

retry_codes = [
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
]

class ArticleAPICaller():
    def __init__(self, test=False):
        self.current_page = 1
        self.total_pages = int()
        self.test = test

    def load_data(self, url) -> list:
        if self.test:
            with open(url) as file:
                data = json.load(file)
            return data
        else:
            self.paginate()


    def paginate_articles(self):
        try:
            print("Downloading articles...")
            self.current_page = 169
            data = self.make_request()
            articles = extractor.get_articles(data)
            build_db(articles)
            self.total_pages = data["response"]["pages"]
            while self.current_page <= self.total_pages:
                try:
                    print(f"Downloading page {self.current_page}")
                    time.sleep(1)
                    data = self.make_request()
                    articles = extractor.get_articles(data)
                    build_db(articles)
                    self.current_page += 1

                except EntryAlreadyExists as err:
                    print(f"Error: {err}")
                    continue
                except HTTPError as err:
                    print(f"HTTP error: {err}")
                    code = err.response.status_code
                    print(code)
                    if code in retry_codes:
                        time.sleep(1)
                        continue
                    raise
        except EntryAlreadyExists as err:
            print(err)
            pass
        except Exception as err:
            print(err)
            pass
        
    def paginate(self):
        try:
            data = self.make_request()
            articles = extractor.get_articles(data)
            build_db(articles)
            self.current_page = 2
            self.total_pages = data["response"]["pages"]
            #self.total_pages = 1
            max_requests = 60
            time_frame = 60
            sleep_time = time_frame / max_requests

            last_request_time = time.time()

            request_count = 0
            while self.current_page <= self.total_pages:
                try:
                    print(f"Request number {request_count}")
                    current_time = time.time()
                    if current_time - last_request_time < sleep_time:
                        time.sleep(sleep_time - (current_time - last_request_time))
                    data = self.make_request()
                    articles = extractor.get_articles(data)
                    build_db(articles)
                    self.current_page += 1
                    last_request_time = time.time()
                    request_count += 1

                    if request_count >= max_requests:
                        last_request_time = time.time()
                        request_count = 0

                except EntryAlreadyExists as err:
                    print(f"Error: {err}")
                    continue

        except Exception as err:
            print(err)
            pass



        
    def make_request(self):
        
        api_url = f"https://content.guardianapis.com/search?section=books&page-size=200&commentable=true&show-fields=shortUrl,commentable,commentCloseDate&show-tags=series,keyword&page={self.current_page}&api-key={GUARDIAN_API_KEY}"
        try:
            r = requests.get(api_url)
            r.raise_for_status()
            return r.json()
        except Exception as err:
            print(f"Error: {err}")
            pass



