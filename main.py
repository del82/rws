#!/usr/bin/env python

import os
import random
import webapp2
import wikipedia
import nltk.data
import jinja2
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

class MainHandler(webapp2.RequestHandler):

    def get(self):
        article = wikipedia.page(wikipedia.random(1))
        local = Article(title         = article.title,
                        content       = article.content,
                        revision_id   = article.revision_id,
                        sentence_list = tokenizer.tokenize(article.content))
        local_key = local.put()
        #local = Article.query(Article.title == "Scott Colley").fetch(1)[0]
        template = JINJA_ENVIRONMENT.get_template('index.html')
        #self.response.write(article.summary)  # this exists.
        random_sentence = random.choice([ i for i in local.sentence_list if not '==' in i])
        self.response.write(template.render({'sentence' : random_sentence}))

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
