import jinja2, wikipedia

from itertools import takewhile
import nltk.data
tokenizer = nltk.data.load('./english.pickle')

def _smart_tokenize(text):

    sentences = tokenizer.tokenize(text)
    pred = lambda x: x != '== References =='
    return [s for s in list(takewhile(pred, sentences)) if not '==' in s]


url_500 = "List_of_HTTP_status_codes#5xx_Server_Error"
internal_server_error = """500 Internal Server Error: A generic error message, given when an unexpected condition was encountered and no more specific message is suitable."""
service_unavailable = """503 Service Unavailable: The server is currently unavailable (because it is overloaded or down for maintenance). Generally, this is a temporary state."""


if __name__=='__main__':
    error_404 = {'title' : "HTTP_404"}
    wiki_404 = wikipedia.page(error_404['title'])
    error_404['sentence'] = _smart_tokenize(wiki_404.content)[0]

    template = jinja2.Template(open('index.html').read())
    page_404 = template.render(error_404)
    open('static/404.html','w').write(page_404)

    error_500 = {'title' : url_500, 'sentence': internal_server_error}
    error_503 = {'title' : url_500, 'sentence': service_unavailable}

    open('static/500.html', 'w').write(template.render(error_500))
    open('static/503.html', 'w').write(template.render(error_503))
