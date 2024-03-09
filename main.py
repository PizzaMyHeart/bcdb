from models import Base, Posts, Comments, Tags
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from extract import Extractor

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

Base.metadata.create_all(engine)

extractor = Extractor()
comments = extractor.get_comments()
comment_data = extractor.get_comment_data(comments)

def insert_comment_data(comment_data):
    to_insert = []
    with Session(engine) as session:
        for item in comment_data:
            to_insert.append(Comments(body = item["body"], author_name = item["author_name"]))
        session.add_all(to_insert)
        session.commit()

def get_comment_data():
    comments_all = session.scalars(select(Comments))
    for row in comments_all:
        print(row.author_name)
    return comments_all

with Session(engine) as session:
    insert_comment_data(comment_data)
    get_comment_data()
    