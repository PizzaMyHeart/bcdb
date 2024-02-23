from sqlalchemy import create_engine, text
from datetime import datetime
from enum import Enum, auto
from sqlalchemy import Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class PostSource(Enum):
    GUARDIAN = auto()
    TORDOTCOM = auto()

class TagType(Enum):
    KEYWORD = auto()
    SERIES = auto()
    

class Posts(Base):
    __tablename__ = "posts"

    post_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    published_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    crawled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[Enum] = mapped_column(PostSource)
    num_comments: Mapped[int] = mapped_column(Integer)
    permalink: Mapped[str] = mapped_column(String)
    guardian_short_url: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return f"Post(id={self.id}, title={self.title})"

class Tags(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[Enum] = mapped_column(TagType, nullable=True)
    post_id: Mapped[int] = mapped_column()

class PostsTags(Base):
    __tablename__ = "posts_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.post_id"))
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.tag_id"))

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String)

class Comments(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

Base.metadata.create_all(engine)



"""
with Session(engine) as session:
    result = session.execute(text("CREATE TABLE post (post_id int, title str)"))
    print(result)

"""
