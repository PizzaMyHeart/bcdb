from models import Base, Posts, Comments, Tags
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import Session
from extract import Extractor

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

Base.metadata.create_all(engine)

extractor = Extractor()
comments = extractor.get_comments()
comment_data = extractor.get_comment_data(comments)

with Session(engine) as session:
    data = comment_data[0]
    comment = Comments(body = data["body"])
    session.add_all([comment])
    session.commit()