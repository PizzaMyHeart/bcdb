from models import Base, Posts, Comments, Tags, CommentsHierarchy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from extract import Extractor
from pprint import pprint

engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)

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
            if len(item["responses"]) > 0:
                for response in item["responses"]:
                    session.add(make_comment_row(response, parent_id=comment_row.id))
        session.commit()

def get_comment_data():
    comments = session.scalars(select(Comments)).all()
    return comments

def get_comment_thread(comment_id):
    subquery_one = select(Comments).where(Comments.id == comment_id).cte(recursive=True)
    subquery_two = select(Comments).join(subquery_one, Comments.parent_id == subquery_one.c.id)
    num_replies = session.query(subquery_two.subquery()).count()
    recursive_query = subquery_one.union(subquery_two)
    thread = session.query(recursive_query).all()
    return {"thread": thread, "num_replies": num_replies}

with Session(engine) as session:
    insert_comment_data(comment_data[:5])
    
    thread = get_comment_thread(5)
    pprint(thread["thread"])
    print(f"{thread['num_replies']} replies")
    