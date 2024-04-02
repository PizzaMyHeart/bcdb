from datetime import datetime
import enum
#from enum import Enum, auto
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class ArticleSource(enum.Enum):
    GUARDIAN = enum.auto()
    TORDOTCOM = enum.auto()

class TagType(enum.Enum):
    KEYWORD = enum.auto()
    SERIES = enum.auto()
    

class Articles(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    published_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    crawled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    comment_close_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True) # Some earlier results don't have this field
    source: Mapped[ArticleSource]
    is_closed_for_comments: Mapped[bool] = mapped_column(default=False) # Use this as a proxy for "up to date"; probs rename this
    num_comments: Mapped[int] = mapped_column(Integer, nullable=True)
    permalink: Mapped[str] = mapped_column(String)
    guardian_short_url: Mapped[str] = mapped_column(String, nullable=True)

class Tags(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    permalink: Mapped[str] = mapped_column(String)

class ArticlesTags(Base):
    __tablename__ = "articles_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("articles.id"))
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"))

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String)

class Comments(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guardian_id: Mapped[int] = mapped_column(Integer, unique=True)
    body: Mapped[str] = mapped_column(String)
    permalink: Mapped[str] = mapped_column(String)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    author_name: Mapped[str] = mapped_column(String)
    parent_guardian_id: Mapped[int] = mapped_column(Integer, ForeignKey("comments.guardian_id"), nullable=True)
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("articles.id"))


