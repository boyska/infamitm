def preRequest(session):
    url = list(urlsplit(session.request.uri))
    if(url[1].startswith('google.')):
        url[1] = 'ifconfig.me' #netloc
        session.request.uri = session.request.path = urlunsplit(url)
        session.request.setHost('ifconfig.me', 80)
        def strip_dots(session, data):
            return data.replace('.', '')
        session.post = strip_dots

def postResponse(session, data):
    return data.upper()


Session.pre = preRequest
Session.post = postResponse

