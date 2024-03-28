from models import Articles
from extract import Extractor
from database import insert_article_data, insert_comment_data, select_all

#url_comments = "https://discussion.theguardian.com/discussion-api/discussion//p/q3x8f?orderBy=oldest&pageSize=100"
url_comments = "./tests/raw/guardian_comments_grief.json"
url_articles = "./tests/raw/guardian_articles.json"

extractor = Extractor()
comments = extractor.get_comments(url_comments)
articles = extractor.get_articles(url_articles)


insert_article_data(articles)
insert_comment_data(comments)

for row in select_all(Articles):
    print(vars(row))
    

"""
thread = get_comment_thread(5)
print(thread["thread"])
print(f"{thread['num_replies']} replies")
"""
