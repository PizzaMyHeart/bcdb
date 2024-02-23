import json
from datetime import datetime
from pprint import pprint

# If comments < 1, skip
# If comments == number of comments in database, skip
# else set up_to_date to False

# Query database for posts with up_to_date = False
# If there are posts with up_to_date = False,
# run the scraper on them to fetch comments

class Parser:
    def __init__(self):
        pass

    def get_comments(self) -> list:
        with open("./tests/guardian_comments.json") as file:
            data = json.load(file)
            
            comments: list = data["discussion"]["comments"]
            return comments
        
    def filter(self, raw: list):
        return {
            "body": raw["body"],
            "date": raw["isoDateTime"],
            "guardian_id": raw["id"],
            "permalink": raw["webUrl"],
            "responses": []
        }
            

    def get_comment_data(self, comments: list) -> list[dict]:
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
    

parser = Parser()
comments = parser.get_comments()
data = parser.get_comment_data(comments)
pprint(data[2])


