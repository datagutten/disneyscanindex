import re
import urllib.parse

import requests
from django.conf import settings


def replace_slash(code):
    return re.sub(r'([a-z]+)/(.+)', r'\1-\2', code)


def replace_dash(code):
    return re.sub(r'([a-z]+)-(.+)', r'\1/\2', code)


def api_request(model, key):
    api_url = settings.INDUCKS_API
    url = '%s%s/%s' % (api_url, model, replace_slash(key))
    response = requests.get(url)
    response.raise_for_status()
    if response.status_code != 200:
        return
    return response.json()


def api_request_single(model, **kwargs) -> dict:
    query = urllib.parse.urlencode(kwargs)
    api_url = settings.INDUCKS_API
    url = '%s%s?%s' % (api_url, model, query)
    response = requests.get(url)
    response.raise_for_status()
    if response.status_code != 200:
        return
    data = response.json()
    if data['count'] == 0:
        raise RuntimeError('No element found for query %s' % query)
    if data['count'] > 1:
        raise RuntimeError('More than 1 element found for query %s' % query)
    return data['results'][0]
