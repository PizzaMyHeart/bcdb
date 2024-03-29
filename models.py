from sqlalchemy import create_engine, text
from datetime import datetime
import enum
#from enum import Enum, auto
from sqlalchemy import Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Session, relationship
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class PostSource(enum.Enum):
    GUARDIAN = enum.auto()
    TORDOTCOM = enum.auto()

class TagType(enum.Enum):
    KEYWORD = enum.auto()
    SERIES = enum.auto()
    

class Articles(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    published_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    crawled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[PostSource]
    num_comments: Mapped[int] = mapped_column(Integer, nullable=True)
    permalink: Mapped[str] = mapped_column(String)
    guardian_short_url: Mapped[str] = mapped_column(String, nullable=True)

class Tags(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[TagType]
    permalink: Mapped[str] = mapped_column(String)
    post_id: Mapped[int] = mapped_column()

class PostsTags(Base):
    __tablename__ = "posts_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"))
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.tag_id"))

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String)

class Comments(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    body: Mapped[str] = mapped_column(String)
    permalink: Mapped[str] = mapped_column(String)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    author_name: Mapped[str] = mapped_column(String)
    source_id: Mapped[str] = mapped_column(String)
    parent_guardian_id: Mapped[int] = mapped_column(Integer, nullable=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("comments.id"), nullable=True)


