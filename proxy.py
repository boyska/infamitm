#!/usr/bin/python
"""A basic transparent HTTP proxy"""

__license__= """
Copyright (c) 2012 Erik Johansson <erik@ejohansson.se>
 
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA

"""

from twisted.web import http
from twisted.internet import reactor, protocol
from twisted.python import log
from urlparse import urlsplit, urlunsplit
import re
import sys
import time
import signal

log.startLogging(sys.stdout)

class ProxyClient(http.HTTPClient):
    """ The proxy client connects to the real server, fetches the resource and
    sends it back to the original client, possibly in a slightly different
    form.
    """

    def __init__(self, method, uri, postData, headers, session):
        self.method = method
        self.uri = uri
        self.postData = postData
        self.headers = headers
        self.session = session
        self.contentLength = None

    def sendRequest(self):
        log.msg("Sending request: %s %s" % (self.method, self.uri))
        self.sendCommand(self.method, self.uri)

    def sendHeaders(self):
        for key, values in self.headers:
            if key.lower() == 'connection':
                values = ['close']
            elif key.lower() == 'keep-alive':
                next

            for value in values:
                self.sendHeader(key, value)
        self.endHeaders()

    def sendPostData(self):
        log.msg("Sending POST data")
        self.transport.write(self.postData)

    def connectionMade(self):
        log.msg("HTTP connection made")
        self.sendRequest()
        self.sendHeaders()
        if self.method == 'POST':
            self.sendPostData()

    def handleStatus(self, version, code, message):
        log.msg("Got server response: %s %s %s" % (version, code, message))
        self.session.request.setResponseCode(int(code), message)

    def handleHeader(self, key, value):
        if key.lower() == 'content-length':
            self.contentLength = value
        else:
            self.session.request.responseHeaders.addRawHeader(key, value)

    def handleResponse(self, data):
        data = self.session.postResponse(data)

        self.session.request.setHeader('Content-Length', len(data))

        self.session.request.write(data)

        self.session.request.finish()
        self.transport.loseConnection()

class ProxyClientFactory(protocol.ClientFactory):
    def __init__(self, method, uri, postData, headers, session):
        self.protocol = ProxyClient
        self.method = method
        self.uri = uri
        self.postData = postData
        self.headers = headers
        self.session = session

    def buildProtocol(self, addr):
        return self.protocol(self.method, self.uri, self.postData,
                             self.headers, self.session)

    def clientConnectionFailed(self, connector, reason):
        log.err("Server connection failed: %s" % reason)
        self.session.setResponseCode(504)
        self.session.finish()
 
class ProxyRequest(http.Request):
    def __init__(self, channel, queued, reactor=reactor):
        http.Request.__init__(self, channel, queued)
        self.reactor = reactor

    def process(self):
        log.msg('PROCESS: %s' % id(self))
        log.msg('URI:%s PATH %s' % (self.uri, self.path + str(self.args)))
        log.msg('Request:\n\t%s' % '\n\t'.join(
                ('%s\t%s' % (x[0],';'.join(x[1])) for x in
                self.requestHeaders.getAllRawHeaders())
            )
        )
        session = Session(self)

        session.preRequest()
        host = self.getHeader('host')
        if not host:
            log.err("No host header given")
            self.setResponseCode(400)
            self.finish()
            return

        port = 80
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        self.setHost(host, port)

        log.msg('URI:%s PATH %s' % (self.uri, self.path + str(self.args)))
        log.msg('Request:\n\t%s' % '\n\t'.join(
                ('%s\t%s' % (x[0],';'.join(x[1])) for x in
                self.requestHeaders.getAllRawHeaders())
            )
        )

        self.content.seek(0, 0)
        postData = self.content.read()
        factory = ProxyClientFactory(self.method, self.uri, postData,
                                     self.requestHeaders.getAllRawHeaders(),
                                     session)
        self.reactor.connectTCP(host, port, factory)

    def processResponse(self, data):
        data = data.upper()
        return data

class TransparentProxy(http.HTTPChannel):
    requestFactory = ProxyRequest
 
class ProxyFactory(http.HTTPFactory):
    protocol = TransparentProxy


class Session(object):
    pre = None
    post = None
    def __init__(self, request):
        self.pre = self.__class__.pre
        self.post = self.__class__.post
        self.request = request

    def preRequest(self):
        if self.pre is not None:
            return self.pre(self)
    def postResponse(self, data):
        if self.post is not None:
            return self.post(self, data)
        return data


if __name__ == '__main__':
    configpath = sys.argv[1]
    def load_config():
        log.msg('Reloaded config: %s' % configpath)
        execfile(configpath)
    load_config()
    signal.signal(signal.SIGHUP, lambda sig,stack: load_config())

    reactor.listenTCP(8080, ProxyFactory())
    reactor.run()
