
import logging
import random

from itertools import takewhile

import nltk.data

from google.appengine.ext import ndb


logger = logging.getLogger(__name__)
tokenizer = nltk.data.load('./english.pickle')


def _smart_tokenize(text):
    blacklist = ['== References ==',
                 '== External Links ==',
                 '== Bibliography ==',
                 '== See also ==',
             ]
    sentences = tokenizer.tokenize(text)

    pred = lambda x: x not in blacklist
    return [s for s in list(takewhile(pred, sentences)) if not '==' in s]


class Article(ndb.Model):
    """ an article """
    title = ndb.StringProperty(required = True, indexed=False)
    content = ndb.JsonProperty(compressed=True, indexed=False)
    sentence_list = ndb.JsonProperty(compressed=True, indexed=False)
    revision_id = ndb.IntegerProperty(indexed = False)
    access_count = ndb.IntegerProperty(indexed = True, default = 0)
    loaded = ndb.DateTimeProperty(indexed = True, auto_now_add=True)
