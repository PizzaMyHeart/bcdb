import requests
import os
from dotenv import load_dotenv
from extract import Extractor
from database import insert_article_data, insert_comment_data, article_metadata, update_closed_to_comments_to_true
import json
import time
from custom_types import EntryAlreadyExists
from requests.exceptions import HTTPError
from http import HTTPStatus
from datetime import datetime, UTC
import traceback, sys

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

    def url_article(self):
        url = f"https://content.guardianapis.com/search?section=books&page-size=200&commentable=true&show-fields=shortUrl,commentable,commentCloseDate&show-tags=series,keyword&page={self.current_page}&api-key={GUARDIAN_API_KEY}"
        return url
    
    def url_comments(self, guardian_article_key):
        url = f"https://discussion.theguardian.com/discussion-api/discussion/{guardian_article_key}?orderBy=oldest&pageSize=100&page={self.current_page}"
        return url
    
    def paginate_comments(self):
        print("Downloading comments...")
        
        # Get list of guardian article keys:
        article_data = article_metadata()
        print(f"{len(article_data)} articles to process")
        for item in article_data:
            guardian_article_key = item[0]
            article_id = item[1]
            comment_closed_date = item[2]
            is_closed_for_comments = item[3]
            self.current_page = 1 # reset
            if datetime.now(UTC) < comment_closed_date:
                print("Comments still open. Skipping...")
                continue
            if is_closed_for_comments:
                print("All comments already in database. Skipping...")
                continue
            try:
                data = self.make_request(self.url_comments(guardian_article_key))
                comments = extractor.get_comments(data)
                self.total_pages = data["pages"]
                insert_comment_data(comments, article_id)
                request_counter = 2
                while self.current_page <= self.total_pages:
                    print(f"Request number {request_counter}")
                    print(f"total pages: {self.total_pages}")
                    print(f"current page: {self.current_page}")
                    try:
                        print(f"Downloading page {self.current_page}")
                        time.sleep(1)
                        data = self.make_request(self.url_comments(guardian_article_key))
                        comments = extractor.get_comments(data)
                        insert_comment_data(comments, article_id)
                        if self.current_page == self.total_pages:
                            print("locking article")
                            update_closed_to_comments_to_true(article_id)
                        self.current_page += 1
                        request_counter += 1
                    except EntryAlreadyExists as err:
                        print(f"comments error: {err}")
                        continue
                    except HTTPError as err:
                        print(f"HTTP error: {err}")
                        code = err.response.status_code
                        print(code)
                        if code in retry_codes:
                            time.sleep(1)   
                            continue
                        if code == HTTPStatus.NOT_FOUND:
                            continue
                        raise
            except Exception as err:
                traceback.print_exc(file=sys.stdout)
                sys.exit(0)
                pass
                
    
    def paginate_articles(self):
        try:
            print("Downloading articles...")
            #self.current_page = 169
            data = self.make_request(self.url_article())
            articles = extractor.get_articles(data)
            insert_article_data(articles)
            self.total_pages = data["response"]["pages"]
            #self.total_pages = 2
            while self.current_page <= self.total_pages:
                try:
                    print(f"Downloading page {self.current_page}")
                    time.sleep(1)
                    data = self.make_request(self.url_article())
                    articles = extractor.get_articles(data)
                    insert_article_data(articles)
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
    """
    def paginate(self):
        try:
            data = self.make_request()
            articles = extractor.get_articles(data)
            build_db(articles)
            #self.current_page = 2
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

"""

        
    def make_request(self, url):
        try:
            r = requests.get(url)
            r.raise_for_status()
            return r.json()
        except Exception as err:
            print(f"Error: {err}")
            pass



