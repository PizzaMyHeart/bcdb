from models import Base, Posts, Comments, Tags
from sqlalchemy import create_engine, Session
from parser import Parser

engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)

Base.metadata.create_all(engine)

parser = Parser()
comments = parser.get_comments()
comment_data = parser.get_comment_data(comments)

with Session(engine) as session:
    for 
