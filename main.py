#!/usr/bin/env python



import os, json, codecs
import random
import webapp2
import wikipedia
import nltk.data
import jinja2
import logging

import sentence

# directly access the default handler and set its format directly
#logging.getLogger().handlers[0].setFormatter(fr)

logger = logging.getLogger(__name__)

from google.appengine.ext import ndb



JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainHandler(webapp2.RequestHandler):

    def get(self):
        random_sentence = sentence.random_sentence()
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(random_sentence))


class JSONHandler(MainHandler):
    def get(self):
        random_sentence = sentence.random_sentence()
        random_sentence['source'] =  'https://en.wikipedia.org/wiki/%s' % random_sentence['title']
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
