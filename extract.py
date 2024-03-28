import json
from datetime import datetime
from typing import List
from enum import Enum, auto
from models import PostSource

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
    def __init__(self):
        pass

    def load_data(self, url, type: RawDataType) -> list:
        with open(url) as file:
            data = json.load(file)
        return data
        
    def articles_filter(self, raw: list):
        return {
            "title": raw["webTitle"],
            "published_date": datetime.fromisoformat(raw["webPublicationDate"]),
            "crawled_date": datetime.utcnow(),
            "updated_date": datetime.utcnow(),
            "permalink": raw["webUrl"],
            "guardian_short_url": raw["fields"]["shortUrl"],
            "source": PostSource.GUARDIAN
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
    
    def get_articles(self, url):
        data = self.load_data(url, RawDataType.ARTICLE)
        articles = data["response"]["results"]
        #print(articles)
        return self.filter_func(articles, self.articles_filter)

    """
    def get_articles(self, url):
        article_data = []
        tag_data = []
        articles = self.load_data(url, RawDataType.ARTICLE)
        for article in articles:
            article_data.append(self.articles_filter(article))
            for tag in article["tags"]:
                tag_data.append(self.tags_filter(tag))

        return article_data, tag_data
    """

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
        num_comments = data["discussion"]["commentCount"]
        print(num_comments)
        comments = data["discussion"]["comments"]
        for x, comment in enumerate(comments):
            processed.append(self.comments_filter(comment))
            if "responses" in comment.keys():
                for y, response in enumerate(comment["responses"]):
                    processed[x]["responses"].append(self.comments_filter(response))
                    processed[x]["responses"][y].update({"parent_guardian_id": response["responseTo"]["commentId"]})
 
        return processed
    


