from models import Articles, Comments
from extract import Extractor
from database import build_db, print_table, get_all_comments, update_num_comments, select_column, get_guardian_article_key, get_comment_thread

#url_comments = "https://discussion.theguardian.com/discussion-api/discussion//p/q3x8f?orderBy=oldest&pageSize=100"
url_comments = "./tests/raw/guardian_comments_grief.json"
url_articles = "./tests/raw/guardian_articles.json"

extractor = Extractor(test=True)
articles = extractor.get_articles(url_articles)
comments = extractor.get_comments(url_comments)


build_db(articles, comments)
update_num_comments()
short_urls = select_column(Articles, "guardian_short_url")
guardian_article_keys = [get_guardian_article_key(item) for item in short_urls]
print(guardian_article_keys)
#print_table(Articles)
#print_table(Comments)


#comments = get_all_comments(200)
#print(len(comments))
#[print(comment.body) for comment in comments]

def print_thread():
    thread = get_comment_thread(5)
    print(thread["thread"])
    print(f"{thread['num_replies']} replies")

