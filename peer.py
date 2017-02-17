# encoding: utf-8
from lib import *

import random
import functools
import json
import threading


class Peer(node.NodeBase):

    def __init__(self):
        super(Peer, self).__init__()
        self.__server_http_address = None
        self.__connection_start = threading.Event()

    def run(self):
        local_port = self.__register_as_client()
        self.update_port(local_port)

        callbacks = {
            'get': functools.partial(self.__on_request_get, instance=self),
        }
        server = http_server.HttpServer(local_port, callbacks).start()
        log.write('start as a server at port {}'.format(local_port))

        self.__connection_start.wait()
        log.write('start connection to {}'.format(self.__server_http_address))

        response = self.__send_to_index_server('/clients', target='all')
        print(response)

        response = self.__send_to_index_server('/clients')
        print(response)

        import time
        time.sleep(3)

        server.stop()

    def __send_to_index_server(self, function, **params):
        print(params)
        url = '{}{}'.format(self.__server_http_address, function)
        params['sender'] = self.address
        return http_request.get_sync(url, params)

    def __set_server_address(self, host, port):
        self.__server_http_address = 'http://{}:{}'.format(host, port)

    def __register_as_client(self):
        data = {
            'host': self.host,
            'port': random.randint(config.AVAILABLE_PORT_BASE, config.AVAILABLE_CONTENT_PORT_MAX),
            'user': self.user,
        }
        if not messaging.publish_once_sync(config.TOPIC_REGISTER_CLIENT, data):
            log.error_exit(1, 'failed to request the registration as a client')

        log.write('send registration request: {}:{} {}'.format(
            data['host'], data['port'], data['user']))
        return data['port']

    @staticmethod
    def __on_request_get(handler, instance):
        paths, params = handler.parse_url()

        if paths[0] == config.QUERY_REGISTER_CLIENT:
            if paths[1] == config.QUERY_SUCCESS:
                log.write('participate in the topology')
            else:
                error = json.loads(paths[2])
                log.error_exit(1, 'failed to participate in the topology: {}'.format(error))

            handler.send_response(http_request.STATUS_OK)
            handler.end_headers()

            instance.__set_server_address(params['host'][0], params['port'][0])
            instance.__connection_start.set()

        elif paths[0] == config.QUERY_IS_CLIENT_ALIVE:
            handler.send_response(http_request.STATUS_OK)
            handler.end_headers()


if __name__ == '__main__':
    Peer().run()
