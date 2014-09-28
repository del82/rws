#!/usr/bin/env python

import webapp2
import wikipedia
from google.appengine.ext import ndb

class Article(ndb.Model):
    """ an article """
    title = ndb.StringProperty(required = True, indexed=True)
    content = ndb.JsonProperty(compressed=True, indexed=False)
    sentence_list = ndb.JsonProperty(compressed=True, indexed=False)
    revision_id = ndb.IntegerProperty(indexed = False)

class MainHandler(webapp2.RequestHandler):

    def get(self):
        article = wikipedia.page(wikipedia.random(1))
        local = Article(title       = article.title,
                        content     = article.content,
                        revision_id = article.revision_id)
        local_key = local.put()
        self.response.write(article.content[:100])
        # query = Article.query(Article.title == "Ishu Patel").fetch(1)[0]
        # self.response.write(query.content[:100])



app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
