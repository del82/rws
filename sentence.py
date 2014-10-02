
import logging
import random
import re

from itertools import takewhile

import nltk.data
import wikipedia

from google.appengine.ext import ndb


logger = logging.getLogger(__name__)
tokenizer = nltk.data.load('./english.pickle')



class Article(ndb.Model):
    """ an article """
    title = ndb.StringProperty(required = True, indexed=False)
    #content = ndb.JsonProperty(compressed=True, indexed=False)
    sentence_list = ndb.JsonProperty(compressed=True, indexed=False)
    revision_id = ndb.IntegerProperty(indexed = False)
    access_count = ndb.IntegerProperty(indexed = True, default = 1)
    loaded = ndb.DateTimeProperty(indexed = True, auto_now_add=True)

def _smart_tokenize(text):
    blacklist = '|'.join(['References',  # if we see any of these sections, the article's over.
                          'External links',
                          'Bibliography',
                          'See also',
                          'Further reading',
                          'Notes',
                      ])
    stopper = re.compile('== *(%s) *==' % blacklist)
    sentences = tokenizer.tokenize(text)

    pred = lambda x: not bool(stopper.match(x))
    return [s for s in list(takewhile(pred, sentences)) if not '==' in s]


def _get_random_article():
    """ try to get a random article from wikipedia; return None on failure """
    try:
        title = wikipedia.random(1)
        logger.debug('Trying %s' % title)
        article = wikipedia.page(title)
        sentence_list = _smart_tokenize(article.content)
        local = Article(title         = unicode(article.title),
                        revision_id   = article.revision_id,
                        sentence_list = sentence_list)
        if len(sentence_list) > 5:  # save only long articles
            #random.shuffle(sentence_list) # pop off the front?
            local_key = local.put()
        return local
    except wikipedia.exceptions.DisambiguationError:
        logger.info('Caught DisambiguationError')
        return None
    except wikipedia.exceptions.HTTPTimeoutError:
        logger.info('Caught HTTPTimeoutError')
        return None


def _get_random_cached_article():
    queries = Article.query().order(Article.access_count).fetch(50)
    item = random.choice(queries)
    item.access_count += 1
    item.put()
    return item

def random_article():
    article = _get_random_article()
    if article == None:  # wikipedia article collection failed
        logger.warning("failed to get article from wikipedia")
        article = _get_random_cached_article()
    return article

def random_sentence():
    """ return a random sentence from a random article """
    article = random_article()
    random_sentence = random.choice(article.sentence_list)

    return {'sentence' : unicode(random_sentence),
            'title'    : unicode(article.title),
            'revision_id' : article.revision_id }
