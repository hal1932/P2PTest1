# encoding: utf-8

import http_server
import http_request
import functools
import json


class QueryServer(object):

    def __init__(self, port, clients):
        self.__clients = clients

        callbacks = {
            'get': functools.partial(QueryServer.__on_query_from_clients, instance=self),
        }
        self.__server = http_server.HttpServer(port, callbacks)

    def start(self):
        self.__server.start()

    def stop(self):
        self.__server.stop()

    @staticmethod
    def __on_query_from_clients(handler, instance):
        paths, params = handler.parse_url()

        if paths[0] == 'clients':
            if 'target' in params:
                if params['target'][0] == 'all':
                    instance.__send_all_clients(handler)
            else:
                instance.__send_clients(handler, params['sender'][0])
        else:
            handler.send_response(http_request.STATUS_NOT_FOUND)
            handler.end_headers()

    def __send_clients(self, handler, sender_address):
        content = [client.to_dict() for client in self.__clients if client.address != sender_address]
        self.__write_response(handler, http_request.STATUS_OK, content)

    def __send_all_clients(self, handler):
        content = [client.to_dict() for client in self.__clients]
        self.__write_response(handler, http_request.STATUS_OK, content)

    def __write_response(self, handler, status, content):
        handler.send_response(status)
        handler.end_headers()
        handler.wfile.write(json.dumps(content))


