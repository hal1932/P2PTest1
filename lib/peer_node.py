# encoding: utf-8
import p2p_config
import node
import http_server
import http_request
import messaging
import query
import log

import random
import functools
import json
import threading


class PeerConfig(object):

    @property
    def nsqd_config(self):
        return self.__nsqd_config

    def __init__(self, nsqd_config):
        self.__nsqd_config = nsqd_config


class PeerNode(node.NodeBase):

    def __init__(self, config, run_impl):
        super(PeerNode, self).__init__()
        self.__config = config
        self.__run_impl = run_impl
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

        self.__run_impl(server=server)

    def send_to_index_server(self, function, **params):
        url = '{}{}'.format(self.__server_http_address, function)
        params['sender'] = self.address
        return http_request.get_sync(url, params)

    def __set_server_address(self, host, port):
        self.__server_http_address = 'http://{}:{}'.format(host, port)

    def __register_as_client(self):
        data = {
            'host': self.host,
            'port': random.randint(p2p_config.AVAILABLE_PORT_BASE, p2p_config.AVAILABLE_CONTENT_PORT_MAX),
            'user': self.user,
        }
        if not messaging.publish_once_sync(self.__config.nsqd_config, p2p_config.TOPIC_REGISTER_CLIENT, data):
            log.error_exit(1, 'failed to request the registration as a client')

        log.write('send registration request: {}:{} {}'.format(
            data['host'], data['port'], data['user']))
        return data['port']

    @staticmethod
    def __on_request_get(handler, instance):
        paths, params = handler.parse_url()

        if paths[0] == query.REGISTER_CLIENT:
            if paths[1] == query.SUCCESS:
                log.write('participate in the topology')
            else:
                error = params['message']
                log.error_exit(1, 'failed to participate in the topology: {}'.format(error))

            handler.send_response(http_request.STATUS_OK)
            handler.end_headers()

            instance.__set_server_address(params['host'][0], params['port'][0])
            instance.__connection_start.set()

        elif paths[0] == query.IS_CLIENT_ALIVE:
            handler.send_response(http_request.STATUS_OK)
            handler.end_headers()
