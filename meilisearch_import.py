import meilisearch
from dotenv import load_dotenv
import os
from database import select_all
from models import Articles, Comments
import time
from bs4 import BeautifulSoup

load_dotenv()

client = meilisearch.Client("http://127.0.0.1:7700", os.environ.get("MEILISEARCH_API_KEY"))
index_articles = client.index("articles")
index_comments = client.index("comments")

def row_to_dict(row):
    return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())

def unix_ts(datetime_obj):
    return time.mktime(datetime_obj.timetuple())

def remove_html_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def process_article_rows(rows):
    result = []
    for row in rows:
        result.append({
            "id": row.id,
            "title": row.title, 
            "published_date": unix_ts(row.published_date),
            "num_comments": row.num_comments,
            "permalink": row.permalink
            })
    return result

def process_comment_rows(rows):
    result = []
    for row in rows:        
        result.append({
            "id": row.id,
            "body": remove_html_tags(row.body),
            "date": unix_ts(row.date),
            "permalink": row.permalink,
            "author_name": row.author_name,
            "article_id": row.article_id
        })
    return result


#articles = process_article_rows(select_all(Articles))
comments = process_comment_rows(select_all(Comments))

print(len(comments))
#index_articles.add_documents(articles)
#index_comments.add_documents(comments)