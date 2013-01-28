'''
An example of infamitm configuration

ALL pages are uppercased, except the request to google.*.
Those are "moved" to ifconfig.me (ie: google.com/host will output your
hostname) AND the output is not capitalized, but the dots are stripped
'''
def preRequest(session):
    url = list(urlsplit(session.request.uri))
    if(url[1].startswith('google.')):
        url[1] = 'ifconfig.me' #netloc
        session.request.uri = session.request.path = urlunsplit(url)
        session.request.setHost('ifconfig.me', 80)

# change the "post" function!
        def strip_dots(session, data):
            return data.replace('.', '')
        session.post = strip_dots

def postResponse(session, data):
    '''without any good reason, any page is capitalized'''
    return data.upper()


Session.pre = preRequest
Session.post = postResponse

