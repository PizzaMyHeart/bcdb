from sqlalchemy import create_engine, select, update, URL
from sqlalchemy.orm import Session
from models import Base, Articles, Comments
import re
import os
from dotenv import load_dotenv

def specify_engine(type="test"):
    if type == "test":
        engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    elif type == "postgres":
        load_dotenv()
        POSTGRES_USER = os.environ.get("POSTGRES_USER")
        POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
        postgres_url = URL.create(
            "postgresql+psycopg2",
            username=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host="localhost",
            database="bcdb"
        )
        engine = create_engine(postgres_url, echo=False)
    Base.metadata.create_all(engine)
    return engine

engine = specify_engine(type="postgres")

def make_article_row(articles):
    #print(Articles(**articles))
    return Articles(**articles)

def insert_article_data(article_data):
    """Returns the row id (used as foreign key for comments)."""
    with Session(engine) as session:
        existing_articles = select_column(Articles, "permalink")
        for item in article_data:
            if item["permalink"] in existing_articles:
                continue
            article_row = make_article_row(item)
            session.add(article_row)
        session.commit()
        return article_row.id

def make_comment_row(comment: dict, article_id: int, parent_id = None):
    # Use a subset of the dict without the responses list
    # but keep the list in the original dict to build adjacency list.
    #comment = {k: v for k, v in comment.items() if k not in ("responses",)}
    comment_table_columns = ("body, date, source, permalink, source_id, author_name")
    comment = {k:v for k, v in comment.items() if k in comment_table_columns}
    # Use article id as foreign key
    comment["article_id"] = article_id
    return Comments(**comment, parent_id = parent_id)

def insert_comment_data(comment_data, article_id):
    with Session(engine) as session:
        for item in comment_data:
            comment_row = make_comment_row(item, article_id)
            session.add(comment_row)
            session.flush()
            if len(item["responses"]) > 0:
                for response in item["responses"]:
                    session.add(make_comment_row(response, article_id, parent_id=comment_row.id))
        session.commit()
        
def get_guardian_article_key(url):
    pattern = r"p/.*"
    return re.search(pattern, url).group(0)

def select_all(table):
    with Session(engine) as session:
        rows = session.query(table).all()
        return rows
    
def select_column(table, column) -> list:
    with Session(engine) as session:
        rows = session.execute(select(getattr(table, column)))
        return [row[0] for row in rows]

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
    
def get_all_comments(article_id):
    with Session(engine) as session:
        stmt = select(Comments).where(Comments.article_id == article_id)
        rows = session.execute(stmt)
        return rows.scalars().all()

def update_num_comments():
    with Session(engine) as session:
        rows = session.execute(select(Articles.id))
        article_ids = [row[0] for row in rows]
        for article_id in article_ids:
            num_comments = len(get_all_comments(article_id))
            session.execute(update(Articles).where(Articles.id == 1).values(num_comments=num_comments))
            session.commit()
    
def print_one_article(article_id):
    with Session(engine) as session:
        rows = session.execute(select(Articles).where(Articles.id == article_id)).all()
        print(vars(rows[0][0]))

def print_table(table):
    """Utility function to print all rows of a table."""
    for row in select_all(table):
        print(vars(row))
   
def build_db(articles, comments):
    article_id = insert_article_data(articles)
    insert_comment_data(comments, article_id)