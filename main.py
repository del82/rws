#!/usr/bin/env python

import os, json, codecs
import random
import webapp2
import wikipedia
import nltk.data
import jinja2
import logging

# directly access the default handler and set its format directly
#logging.getLogger().handlers[0].setFormatter(fr)

logger = logging.getLogger(__name__)

from itertools import takewhile

from google.appengine.ext import ndb

tokenizer = nltk.data.load('./english.pickle')


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Article(ndb.Model):
    """ an article """
    title = ndb.StringProperty(required = True, indexed=True)
    content = ndb.JsonProperty(compressed=True, indexed=False)
    sentence_list = ndb.JsonProperty(compressed=True, indexed=False)
    revision_id = ndb.IntegerProperty(indexed = False)
    access_count = ndb.IntegerProperty(indexed = True, default = 0)
    loaded = ndb.DateTimeProperty(indexed = True, auto_now_add=True)

def _smart_tokenize(text):

    sentences = tokenizer.tokenize(text)
    pred = lambda x: x != '== References ==' and x != '== External Links ==' and x != '== Bibliography =='
    return [s for s in list(takewhile(pred, sentences)) if not '==' in s]

class MainHandler(webapp2.RequestHandler):

    def _safe_random_page(self):
        logger.debug('Getting a safe random page')
        page_list = wikipedia.random(10)
        for title in page_list:
            try:
                logger.debug('Trying %s' % title)
                article = wikipedia.page(title)
                return article
            except wikipedia.exceptions.DisambiguationError:
                logger.info('Caught DisambiguationError')
                continue
        # if that doesn't work, barf.  In the future grab a cached page?
        raise wikipedia.exceptions.WikipediaException('too many disambiguation errors')


    def get(self):
        article = self._safe_random_page()
        local = Article(title         = unicode(article.title),
                        content       = article.content,
                        revision_id   = article.revision_id,
                        sentence_list = _smart_tokenize(article.content))
        local_key = local.put()
        #local = Article.query(Article.title == "Scott Colley").fetch(1)[0]
        template = JINJA_ENVIRONMENT.get_template('index.html')
        #self.response.write(article.summary)  # this exists.
        random_sentence = random.choice(local.sentence_list)
        self.response.write(template.render({'sentence' : unicode(random_sentence),
                                             'title' : unicode(article.title),
                                             'revision_id' : article.revision_id}))


class JSONHandler(MainHandler):
    def get(self):
        article = self._safe_random_page()
        local = Article(title         = unicode(article.title),
                        content       = article.content,
                        revision_id   = article.revision_id,
                        sentence_list = _smart_tokenize(article.content))
        local_key = local.put()
        random_sentence = random.choice(local.sentence_list)
        response = {'sentence' : random_sentence,
                    'link' : 'https://en.wikipedia.org/wiki/%s' % unicode(local.title)}
        self.response.content_type = 'text/json'
        self.response.write(json.dumps(response))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/api', JSONHandler)

], debug=True)

def error_404(request, response, error):
    response.set_status(404)
    response.write(open('static/404.html').read())

app.error_handlers[404] = error_404
#app.error_handlers[500] = lambda x, response, z: response.write(open('static/500.html').read())
#app.error_handlers[503] = lambda x, response, z: response.write(open('static/503.html').read())
