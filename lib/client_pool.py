# encoding: utf-8
import p2p_config
import node
import messaging
import http_request
import log
import util
import query

import threading
import functools
import json


class ClientPool(object):

    @property
    def clients(self):
        return self.__clients

    def __init__(self, config, host, port):
        self.__config = config
        self.__host = host
        self.__port = port

        self.__clients = []
        self.__clients_lock = threading.Lock()
        self.__on_added_client = None
        self.__on_removed_client = None

    def set_connection_event(self, on_added_client, on_removed_client):
        self.__on_added_client = on_added_client
        self.__on_removed_client = on_removed_client

    def run(self):
        messaging.create_subscriber(
            self.__config.nsqd_config,
            p2p_config.TOPIC_REGISTER_CLIENT,
            channel='channel0',
            on_received_message=functools.partial(
                self.__on_received_registration_request,
                instance=self),
        )

        messaging.run()

    def remove(self, client):
        log.write('client is disconnected: {}'.format(client.address))
        with self.__clients_lock:
            self.__clients.remove(client)

            if self.__on_removed_client is not None:
                self.__on_removed_client(self.clients)

    @staticmethod
    def __on_received_registration_request(message, instance):
        data = json.loads(message)
        new_client = node.NodeBase(**data)

        error = instance.__test_register_client(new_client)
        if error is None:
            error = instance.__send_register_notification(new_client)

        if error is None:
            error = instance.__register_client(new_client)

        if error is None:
            return

        instance.__send_error(new_client, error)

    def __test_register_client(self, new_client):
        new_address = new_client.address

        if util.exists(self.__clients, lambda x: x.address == new_address):
            return 'duplicated client address: {}'.format(new_address)

        if self.__config.max_peer_count is not None:
            if len(self.__clients) >= self.__config.max_peer_count:
                return 'exceeding max peer count {}'.format(self.__config.max_peer_count)

        return None

    def __send_register_notification(self, new_client):
        url = 'http://{}/{}/{}'.format(
            new_client.address, query.REGISTER_CLIENT, query.SUCCESS)

        data = {
            'host': self.__host,
            'port': self.__port,
        }

        try:
            code, _ = http_request.get_sync(url, params=data)
            if code != http_request.STATUS_OK:
                return 'failed to notifying registeration completion to client: {}'.format(url)
        except http_request.ConnectionError as e:
            log.warning(e)

        return None

    def __register_client(self, new_client):
        with self.__clients_lock:
            self.__clients.append(new_client)

            if self.__on_added_client is not None:
                self.__on_added_client(self.clients)

        log.write('accept new client: {}'.format(new_client.address))
        return None

    def __send_error(self, client, msg):
        url = 'http://{}/{}/{}?message={}'.format(
            client.address, query.REGISTER_CLIENT, query.ERROR, msg)
        http_request.get_sync(url, ignore_error=True)