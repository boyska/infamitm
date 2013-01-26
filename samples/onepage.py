'''
This is a configuration sample.

This will make EVERY http request return the same resource, no  matter what
'''

from urlparse import urlsplit, urlunsplit

def preRequest(session):
    url = list(urlsplit(session.request.uri))
    url[1] = 'ifconfig.me' #netloc
    url[2] = '/host' #path
    session.request.uri = session.request.path = urlunsplit(url)
    session.request.setHost('ifconfig.me', 80)


Session.pre = preRequest
Session.post = None

