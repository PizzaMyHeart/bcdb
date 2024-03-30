import json
from datetime import datetime, UTC
from typing import List
from enum import Enum, auto
from models import ArticleSource
import requests
import os
from dotenv import load_dotenv




# If comments < 1, skip
# If comments == number of comments in database, skip
# else set up_to_date to False

# Query database for posts with up_to_date = False
# If there are posts with up_to_date = False,
# run the scraper on them to fetch comments



class RawDataType(Enum):
    ARTICLE = auto()
    COMMENT = auto()

class Extractor:
    def __init__(self, test=False):
        load_dotenv()

        self.GUARDIAN_API_KEY = os.environ.get("GUARDIAN_API_KEY")
        self.test = test
        self.api_url_guardian_articles = f"https://content.guardianapis.com/search?section=books&page-size=50&commentable=true&show-fields=shortUrl,commentable&show-tags=series,keyword&api-key={self.GUARDIAN_API_KEY}"

    def load_data(self, url, type: RawDataType) -> list:
        if self.test:
            with open(url) as file:
                data = json.load(file)
            return data
        else:
            pass
        
    def get_articles(self, url):
        data = self.load_data(url, RawDataType.ARTICLE)
        articles = data["response"]["results"]
        processed = self.filter_func(articles, self.articles_filter)
        for idx, article in enumerate(articles):
            tags = self.filter_func(article["tags"], self.tags_filter)
            #print(f"\n{idx}: {tags}\n")
            processed[idx]["tags"] = tags
            #print(processed[idx])
        return processed
    
    def articles_filter(self, raw: list):
        return {
            "title": raw["webTitle"],
            "published_date": datetime.fromisoformat(raw["webPublicationDate"]),
            "crawled_date": datetime.now(UTC),
            "updated_date": datetime.now(UTC),
            "permalink": raw["webUrl"],
            "guardian_short_url": raw["fields"]["shortUrl"],
            "source": ArticleSource.GUARDIAN
        }
    
    def tags_filter(self, raw: list):
        return {
            "name": raw["webTitle"],
            "permalink": raw["webUrl"]
        }
    
    def filter_func(self, items: list, func: callable) -> list:
        data = []
        for item in items:
            data.append(func(item))
        return data
    

    def comments_filter(self, raw: list):
        """Return a subset of comment data"""
        return {
            "body": raw["body"],
            "date": datetime.fromisoformat(raw["isoDateTime"]),
            "source_id": raw["id"], #guardian ID
            "permalink": raw["webUrl"],
            "author_name": raw["userProfile"]["displayName"],
            "responses": []
        }
            

    def get_comments(self, url) -> List[dict]:
        """Apply the filter function to each comment and add list of responses if they exist.
        Apply the filter function to any comments that are responses.
        """
        processed = []
        data = self.load_data(url, RawDataType.COMMENT)
        is_closed_for_comments = data["discussion"]["isClosedForComments"]
        num_comments = data["discussion"]["commentCount"]
        comments = data["discussion"]["comments"]
        for x, comment in enumerate(comments):
            filtered = self.comments_filter(comment)
            filtered["num_comments"] = num_comments
            filtered["is_closed_to_comments"] = is_closed_for_comments
            processed.append(filtered)
            if "responses" in comment.keys():
                for y, response in enumerate(comment["responses"]):
                    processed[x]["responses"].append(self.comments_filter(response))
                    processed[x]["responses"][y].update({"parent_guardian_id": response["responseTo"]["commentId"]})
        return processed
    


