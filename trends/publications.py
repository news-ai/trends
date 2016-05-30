# Stdlib imports
import datetime

# Third-party app imports
from pattern.web import Newsfeed, plaintext, HTTP404NotFound
from pattern.vector import Model, Document, LEMMA

# Imports from app
from trends.utils.parser import datetext
from trends.internal.context import get_publisherfeeds


# You need data from multiple days to make this particular function work
# So you need to download data from the current day and the previous days.
def feeds_to_trends(feeds):
    for url in feeds:
        url = url['feed_url']
        news = {}
        try:
            for story in Newsfeed().search(url, cached=False):
                d, s = datetext(story.date, story.description)

                # Each key in the news dictionary is a date: news is grouped per day.
                # Each value is a dictionary of id => story items.
                # We use hash(story.description) as a unique id to avoid duplicate
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
        except HTTP404NotFound:
            print url
            pass


def run_feeds_trend():
    feeds = get_publisherfeeds()['results']
    return feeds_to_trends(feeds)
