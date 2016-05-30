# Stdlib imports
import json

# Third-party app imports
import urllib3
import requests
import dateutil.parser as parser
from pymongo import MongoClient
from newspaper import Article
from pattern.web import Newsfeed, plaintext
from pattern.db import date as datecalc
from pattern.vector import Model, Document, LEMMA
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Imports from app
from middleware.config import BASE_URL
from trends.utils.parser import timestamptext
from trends.internal.context import get_login_token, get_articles

# Removing requests warning
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# MongoDB setup
client = MongoClient(connect=False)
db = client.trends
articles_collection = db.articles

# Context Setup
base_url = BASE_URL


def get_article_text(url):
    mongo_article = articles_collection.find_one({'url': url})
    if mongo_article:
        return mongo_article['article']

    article = Article(url)
    article.download()
    article.parse()

    article_text = article.text.split('\n')
    article_text = ' '.join(article_text)

    data = {
        'article': article_text,
        'url': url,
    }

    articles_collection.insert_one(data)
    return article_text


def articles_to_trends(articles):
    news = {}
    for story in articles:
        if story['added_at']:
            article_text = get_article_text(story['url'])
            d, s = timestamptext(story['added_at'], article_text)

            # Each key in the news dictionary is a date: news is grouped per day.
            # Each value is a dictionary of id => story items.
            # We use hash(story['summary']) as a unique id to avoid duplicate
            # content.
            news.setdefault(d, {})[hash(s)] = s

    m = Model()
    for date, stories in news.items():
        s = stories.values()
        s = ' '.join(s).lower()
        # Each day of news is a single document.
        # By adding all documents to a model we can calculate tf-idf.
        m.append(Document(s, stemmer=LEMMA, exclude=[
                 'news', 'day'], name=date))

    for document in m:
        print document.name
        print document.keywords(top=10)


def process_articles():
    articles = get_articles(500)['results']
    articles_to_trends(articles)
