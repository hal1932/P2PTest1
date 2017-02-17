# encoding: utf-8
import p2p_config
import http_request
import log

import nsq
import json
import functools


class NsqdConfig(object):

    @property
    def http_address(self):
        return self.__http_address

    @property
    def tcp_addresses(self):
        return self.__tcp_addresses

    def __init__(self, http_address, tcp_addresses):
        self.__http_address = http_address
        self.__tcp_addresses = tcp_addresses


def publish_once_sync(nsqd_config, topic, data):
    url = 'http://{}/pub?topic={}'.format(nsqd_config.http_address, topic)
    json_data = json.dumps(data)

    code, content = http_request.post_sync(url, json_data)
    if code == 200 and content == 'OK':
        return True
    else:
        log.warning('{}: failed to http post, {}, {}'.format(__file__, code, content))
        return False


def create_subscriber(nsqd_config, topic, channel, on_received_message):
    def _message_handler(message, callback):
        message.enable_async()
        data = message.body
        message.finish()
        callback(data)

    return nsq.Reader(
        topic=topic,
        channel=channel,
        message_handler=functools.partial(_message_handler, callback=on_received_message),
        nsqd_tcp_addresses=nsqd_config.tcp_addresses,
    )


def run():
    nsq.run()


def start():
    raise NotImplementedError()

def stop():
    raise NotImplementedError()
