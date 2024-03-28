from models import Articles, Comments
from extract import Extractor
from database import build_db, print_table, get_all_comments, update_num_comments, print_one_article

#url_comments = "https://discussion.theguardian.com/discussion-api/discussion//p/q3x8f?orderBy=oldest&pageSize=100"
url_comments = "./tests/raw/guardian_comments_grief.json"
url_articles = "./tests/raw/guardian_articles.json"

extractor = Extractor()
comments = extractor.get_comments(url_comments)
articles = extractor.get_articles(url_articles)


build_db(articles, comments)
update_num_comments()
print_one_article(1)
#print_table(Articles)
#print_table(Comments)


#comments = get_all_comments(200)
#print(len(comments))
#[print(comment.body) for comment in comments]


"""
thread = get_comment_thread(5)
print(thread["thread"])
print(f"{thread['num_replies']} replies")
"""
