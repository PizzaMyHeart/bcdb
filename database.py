from sqlalchemy import create_engine, select, update, URL
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Base, Articles, Comments, Tags, ArticlesTags
import re
import os
import sys
import traceback
from dotenv import load_dotenv
from custom_types import EntryAlreadyExists
#from sqlalchemy.dialects.postgresql import insert   # for INSERT ... ON CONFLICT

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

def get_tags():
    tags = select_column(Tags, "name")
    tags = set(tags)
    print(tags)
    return tags


def make_article_row(article):
    article_table_columns = ("title", "published_date", "crawled_date", "comment_close_date", "source", "is_closed_for_comments", "num_comments", "permalink", "guardian_short_url")
    article = truncate_keys(article, article_table_columns)
    return Articles(**article)

def make_tags_row(tag):
    return Tags(**tag)

def make_articlestags_row(article_id, tag_id):
    return ArticlesTags(article_id=article_id, tag_id=tag_id)

def check_existing_entries(permalink, existing):
    if permalink in existing:
        raise EntryAlreadyExists
    
def update_closed_to_comments_to_true(article_id):
    with Session(engine) as session:
        session.execute(update(Articles).where(Articles.id == article_id).values(is_closed_for_comments = True))
        session.commit()

def insert_article_data(article_data):
    """Inserts rows in the Articles, Tags and ArticlesTags tables."""
    with Session(engine) as session:
        existing_articles = select_column(Articles, "permalink")
        for item in article_data:
            try:
                check_existing_entries(item["permalink"], existing_articles)
                article_row = make_article_row(item)
                session.add(article_row)
                session.commit() # Commit to get row id
            except EntryAlreadyExists:
                session.commit()
                continue
            tag_rows = item["tags"]
            #print(f"tag_rows: {tag_rows}")
            existing_tags = select_column(Tags, "permalink")
            for item in tag_rows:
                try:
                    permalink = item["permalink"]
                    #print(f"permalink: {permalink}\n\n")
                    # Don't do this; this means each tag will only be inserted once
                    # i.e. one tag belongs to only one article
                    #check_existing_entries(permalink, existing_tags)
                    if permalink in existing_tags:
                        # If tag already exists then re-use the same tag id for the junction table
                        tag_id = session.execute(select(Tags.id).where(Tags.permalink == permalink)).all()[0][0]
                        #print(tag_id)
                    else:
                        tag_row = make_tags_row(item)
                        session.add(tag_row)
                        session.commit() # Commit to get row id
                        tag_id = tag_row.id
                    session.add(make_articlestags_row(article_row.id, tag_id))
                    session.commit()
                except EntryAlreadyExists:
                    session.commit()
                    continue
        session.commit()

def truncate_keys(data: dict, keys: tuple) -> dict:
    """Return a smaller dict containing a subset of keys"""
    data = {k:v for k, v in data.items() if k in keys}
    return data

def make_comment_row(comment: dict, article_id: int, parent_guardian_id = None):
    # Use a subset of the dict without the responses list
    # but keep the list in the original dict to build adjacency list.
    #comment = {k: v for k, v in comment.items() if k not in ("responses",)}
    comment_table_columns = ("body, date, source, permalink, guardian_id, author_name")
    comment = truncate_keys(comment, comment_table_columns)
    # Use article id as foreign key
    comment["article_id"] = article_id
    return Comments(**comment, parent_guardian_id = parent_guardian_id)

def insert_comment_data(comment_data, article_id):
    with Session(engine) as session:
        existing_comments = select_column(Comments, "permalink")
        for item in comment_data:
            try:
                check_existing_entries(item["permalink"], existing_comments)
                comment_row = make_comment_row(item, article_id)
                session.add(comment_row)
                session.flush()
                if len(item["responses"]) > 0:
                    for response in item["responses"]:
                        #print(response.keys())
                        permalink = response["permalink"]
                        parent_guardian_id = response["parent_guardian_id"]
                        guardian_id = response["guardian_id"]
                        author = response["author_name"]
                        body = response["body"]
                        #print(permalink)
                        #print(f"guardian_id: {guardian_id} ({author})-- parent_guardian_id: {parent_guardian_id}")
                        check_existing_entries(response["permalink"], existing_comments)
                        #row_to_insert = make_comment_row(response, article_id, parent_guardian_id=response["parent_guardian_id"])
                        #entries = response
                        #del entries["responses"]
                        #entries["article_id"] = article_id
                        #stmt = insert(Comments).values(entries).on_conflict_do_nothing()
                        #session.execute(stmt)
                        try:
                            session.add(make_comment_row(response, article_id, parent_guardian_id=response["parent_guardian_id"]))
                            session.commit()
                        except IntegrityError as e:
                            session.rollback()
                            print(e)
                            #traceback.print_exc(file=sys.stdout)
            except EntryAlreadyExists as err:
                print("comment already exists")
                continue
        session.commit()
        
def guardian_article_key_filter(url: str):
    pattern = r"/p/.*"
    return re.search(pattern, url).group(0)

def article_metadata() -> list:
    """Returns a list of tuples of article key, row id, comment_closed_date, is_closed_for_comments"""
    with Session(engine) as session:
        result = []
        rows = session.execute(select(
            Articles.guardian_short_url, 
            Articles.id, 
            Articles.comment_close_date, 
            Articles.is_closed_for_comments)
            .where(Articles.is_closed_for_comments == False)
            )
        for row in rows:
            result.append((guardian_article_key_filter(row[0]), row[1], row[2], row[3]))
        return result
    

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
    """
    This SQL query updates the articles.num_comments with the comment count:

    WITH counts AS (SELECT article_id, COUNT(*) AS row_count FROM comments GROUP BY article_id) UPDATE articles SET num_comments = counts.row_count FROM counts WHERE articles.id = counts.article_id AND articles.is_closed_for_comments=True;
    """
    
def print_one_article(article_id):
    with Session(engine) as session:
        rows = session.execute(select(Articles).where(Articles.id == article_id)).all()
        print(vars(rows[0][0]))

def print_table(table):
    """Utility function to print all rows of a table."""
    for row in select_all(table):
        print(vars(row))
   

    #article_id = insert_article_data(articles)
    #insert_comment_data(comments, article_id)