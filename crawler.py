from dotenv import load_dotenv

load_dotenv()

guardian_api_key = GUARDIAN_API_KEY

class ArticleURLFetcher:
    api_url = f"https://content.guardianapis.com/search?section=books&page-size=50&commentable=true&show-fields=shortUrl,commentable&show-tags=series,keyword&api-key={guardian_api_key}"
    def get_urls():
        r = requests.get(url)


