# Stdlib imports
import json

# Third-party app imports
import urllib3
import requests
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


def get_publisherfeeds():
    token = get_login_token()
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": "Bearer " + token
    }

    r = requests.get(base_url + "/publisherfeeds/?limit=1000",
                     headers=headers, verify=False)

    return r.json()
