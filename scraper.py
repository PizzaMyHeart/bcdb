import requests
from bs4 import BeautifulSoup



class ArticleURLFetcher:
    api_url = f"https://content.guardianapis.com/search?section=books&page-size=50&commentable=true&show-fields=shortUrl,commentable&show-tags=series,keyword&api-key={guardian_api_key}"
    def get_urls():
        r = requests.get(url)


