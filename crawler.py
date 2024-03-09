from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

GUARDIAN_API_KEY = os.environ.get("GUARDIAN_API_KEY")

with open("./tests/raw/guardian_articles.json") as file:
    data = json.load(file)
results = data["response"]["results"]

def get_urls():
    data = []
    for result in results:
        data.append(
            {"post_permalink": result["webUrl"],
             "title": result["webTitle"],
             "published_date": datetime.fromisoformat(result["webPublicationDate"]),
             "guardian_short_url": result["fields"]["shortUrl"],
             })

    return data

print(get_urls()[0])
    

class ArticleURLFetcher:
    api_url = f"https://content.guardianapis.com/search?section=books&page-size=200&commentable=true&show-fields=shortUrl,commentable&show-tags=series,keyword&api-key={GUARDIAN_API_KEY}"
    def get_urls():
        #r = requests.get(url)
        pass

from models import Base, Posts, Comments, Tags, Users, PostSource
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)

Base.metadata.create_all(engine)


with Session(engine) as session:
    for result in get_urls():
        session.add(Posts(
            title=result["title"],
            published_date=result["published_date"],
            crawled_date=datetime.utcnow(),
            updated_date=datetime.utcnow(),
            permalink=result["post_permalink"],
            guardian_short_url=result["guardian_short_url"],
            source=PostSource.GUARDIAN
        ))
    session.commit()
    result = session.execute(select(Posts).where(Posts.title == "Five of the best recent books from Ukraine"))
    print(result.all())
