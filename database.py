from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Base, Articles, Comments

engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)

Base.metadata.create_all(engine)

def make_article_row(articles):
    #print(Articles(**articles))
    return Articles(**articles)

def insert_article_data(article_data):
    with Session(engine) as session:
        for item in article_data:
            article_row = make_article_row(item)
            session.add(article_row)
        session.commit()

def make_comment_row(comment: dict, parent_id = None):
    # Use a subset of the dict without the responses list
    # but keep the list in the original dict to build adjacency list.
    #comment = {k: v for k, v in comment.items() if k not in ("responses",)}
    comment_table_columns = ("body, date, source, permalink, source_id, author_name")
    comment = {k:v for k, v in comment.items() if k in comment_table_columns}
    return Comments(**comment, parent_id = parent_id)
    """
    return Comments(
        body = comment["body"], 
        date = comment["date"], 
        author_name = comment["author_name"], 
        source_id = comment["source_id"],
        parent_id = parent_id
        )
        """

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

def select_all(table):
    with Session(engine) as session:
        rows = session.query(table).all()
        return rows

def get_comment_thread(comment_id):
    """Recursive CTE query to get a comment and its descendants.
    Returns rows from the comments table and the number of replies."""
    subquery_one = select(Comments).where(Comments.id == comment_id).cte(recursive=True)
    subquery_two = select(Comments).join(subquery_one, Comments.parent_id == subquery_one.c.id)
    with Session(engine) as session:
        num_replies = session.query(subquery_two.subquery()).count()
        recursive_query = subquery_one.union(subquery_two)
        thread = session.query(recursive_query).all()
        return {"thread": thread, "num_replies": num_replies}