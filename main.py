from models import Base, Posts, Comments, Tags, CommentsHierarchy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from extract import Extractor

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

Base.metadata.create_all(engine)

extractor = Extractor()
comments = extractor.get_comments()
comment_data = extractor.get_comment_data(comments)

def make_comment_row(comment: dict, parent_id = None):
    return Comments(
        body = comment["body"], 
        date = comment["date"], 
        author_name = comment["author_name"], 
        source_id = comment["source_id"],
        parent_id = parent_id
        )

def make_comment_closure_row(parent_id, child_id, depth):
    return CommentsHierarchy(parent_id = parent_id, child_id = child_id, depth = depth)

def insert_comment_data(comment_data):
    with Session(engine) as session:
        for item in comment_data:
            comment_row = make_comment_row(item)
            session.add(comment_row)
            session.flush()
            print(comment_row.author_name)
            if len(item["responses"]) > 0:
                for response in item["responses"]:
                    session.add(make_comment_row(response, parent_id=comment_row.id))
        session.commit()

def get_comment_data():
    comments_all = session.scalars(select(Comments))
    #print(comments_all.first().author_name)
    return comments_all

with Session(engine) as session:
    insert_comment_data(comment_data[:3])
    get_comment_data()
    