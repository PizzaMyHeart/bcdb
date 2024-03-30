import requests
import os
from dotenv import load_dotenv

load_dotenv()
GUARDIAN_API_KEY = os.environ.get("GUARDIAN_API_KEY")

def call_api_article():
    api_url = f"https://content.guardianapis.com/search?section=books&page-size=200&commentable=true&show-fields=shortUrl,commentable,commentCloseDate&show-tags=series,keyword&api-key={GUARDIAN_API_KEY}"
    r = requests.get(api_url)


