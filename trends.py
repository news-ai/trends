# Stdlib imports
import urllib3
import json
import datetime

# Third-party app imports
import requests
import dateutil.parser as parser
from pattern.web import Newsfeed, plaintext, HTTP404NotFound
from pattern.db import date as datecalc
from pattern.vector import Model, Document, LEMMA
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Imports from app
from middleware.config import (
    CONTEXT_API_USERNAME,
    CONTEXT_API_PASSWORD,
)

# Removing requests warning
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Context Setup
base_url = 'https://context.newsai.org/api'


def articles_to_trends(articles):
    news = {}
    for story in articles:
        if story['added_at']:
            dt = datetime.datetime.fromtimestamp(
                story['added_at']).strftime('%Y-%m-%d')
            dt = parser.parse(dt)
            dt = dt.strftime("%Y-%m-%d")
            d = str(datecalc(dt, format='%Y-%m-%d'))
            s = plaintext(story['summary'])
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


def get_login_token():
    headers = {
        "content-type": "application/json",
        "accept": "application/json"
    }
    payload = {
        "username": CONTEXT_API_USERNAME,
        "password": CONTEXT_API_PASSWORD,
    }

    r = requests.post(base_url + "/jwt-token/",
                      headers=headers, data=json.dumps(payload), verify=False)
    data = json.loads(r.text)
    token = data.get('token')
    return token


def get_articles():
    token = get_login_token()
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": "Bearer " + token
    }

    r = requests.get(base_url + '/articles/?limit=200',
                     headers=headers, verify=False)
    return r.json()


def process_articles():
    articles = get_articles()['results']
    articles_to_trends(articles)

process_articles()
