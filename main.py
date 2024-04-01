from database import get_comment_thread
from caller import ArticleAPICaller
#url_comments = "https://discussion.theguardian.com/discussion-api/discussion//p/q3x8f?orderBy=oldest&pageSize=100"
url_comments = "./tests/raw/guardian_comments_grief.json"
url_articles = "./tests/raw/guardian_articles.json"
"""
extractor = Extractor(test=True)
articles = extractor.get_articles(url_articles)
comments = extractor.get_comments(url_comments)


build_db(articles)
"""
caller = ArticleAPICaller()
caller.paginate_articles()
#caller.paginate_comments()

#guardian_article_keys_and_row_id()

#update_num_comments()
#short_urls = select_column(Articles, "guardian_short_url")
#guardian_article_keys = [get_guardian_article_key(item) for item in short_urls]
#get_tags()
#print(guardian_article_keys)
#print_table(Articles)
#print_table(Comments)


#comments = get_all_comments(200)
#print(len(comments))
#[print(comment.body) for comment in comments]

def print_thread():
    thread = get_comment_thread(5)
    print(thread["thread"])
    print(f"{thread['num_replies']} replies")

