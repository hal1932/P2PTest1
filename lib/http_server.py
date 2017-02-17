# encoding: utf-8

import BaseHTTPServer
import SocketServer
import threading
import urlparse


class _RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def parse_url(self):
        params = urlparse.urlparse(self.path)
        return params.path.lstrip('/').split('/'), urlparse.parse_qs(params.query)

    def do_GET(self):
        self.__do_request('get')

    def do_POST(self):
        self.__do_request('post')

    def __do_request(self, method):
        if method in self.server.arguments:
            self.server.arguments[method](handler=self)


class HttpServer(object):

    def __init__(self, port, on_request={}):
        server = SocketServer.ThreadingTCPServer(('', port), _RequestHandler)
        server.arguments = on_request

        serve_thread = threading.Thread(target=server.serve_forever)
        serve_thread.daemon = True

        self.__server = server
        self.__serve_thread = serve_thread

    def start(self):
        self.__serve_thread.start()
        return self

    def stop(self):
        self.__server.shutdown()
        self.__server.server_close()
        self.__serve_thread.join()
