import json
from datetime import datetime
from pprint import pprint
from typing import List

# If comments < 1, skip
# If comments == number of comments in database, skip
# else set up_to_date to False

# Query database for posts with up_to_date = False
# If there are posts with up_to_date = False,
# run the scraper on them to fetch comments

class Extractor:
    def __init__(self):
        pass

    def get_comments(self) -> list:
        """Return a list of just the comments from the original json object"""
        with open("./tests/raw/guardian_comments.json") as file:
            data = json.load(file)
            
            comments: list = data["discussion"]["comments"]
            return comments
        
    def filter(self, raw: list):
        """Return a subset of comment data"""
        return {
            "body": raw["body"],
            # Needs more recent Python, 3.8 not supported
            #"date": datetime.fromisoformat(raw["isoDateTime"]),
            "guardian_id": raw["id"],
            "permalink": raw["webUrl"],
            "author_name": raw["userProfile"]["displayName"],
            "responses": []
        }
            

    def get_comment_data(self, comments: list) -> List[dict]:
        """Apply the filter function to each comment and add list of responses if they exist.
        Apply the filter function to any comments that are responses.
        """
        data = []
        for x, comment in enumerate(comments):
            data.append(self.filter(comment))
            if "responses" in comment.keys():
                for y, response in enumerate(comment["responses"]):
                    data[x]["responses"].append(self.filter(response))
                    data[x]["responses"][y].update({"response_to": response["responseTo"]["commentId"]})
            """
        for comment in comments:
            body: str = comment["body"]
            date: datetime = comment["isoDateTime"]
            guardian_id: int = comment["id"]
            permalink: str = comment["webUrl"]
            if "responses" in comment.keys():
                responses: list = comment["responses"]
            else:
                responses: list = []
            data.append({"body": body, "date": date, "responses": responses})
            """
        return data
    

parser = Extractor()
comments = parser.get_comments()
data = parser.get_comment_data(comments)


