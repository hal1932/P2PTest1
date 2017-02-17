# encoding: utf-8
import http_server
import functools
import json


class QueryServer(object):

    def __init__(self, port, on_received_query):
        self.__on_received_query = on_received_query

        def _on_query_from_clients(handler, instance):
            paths, params = handler.parse_url()
            instance.__on_received_query(paths=paths, params=params, handler=handler)

        callbacks = {
            'get': functools.partial(_on_query_from_clients, instance=self),
        }
        self.__server = http_server.HttpServer(port, callbacks)

    def start(self):
        self.__server.start()

    def stop(self):
        self.__server.stop()

    def write_response(self, handler, status, content):
        handler.send_response(status)
        handler.end_headers()
        handler.wfile.write(json.dumps(content))
