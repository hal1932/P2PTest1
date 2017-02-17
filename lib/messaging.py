# encoding: utf-8
import config
import http_request
import log

import nsq
import json
import functools


def publish_once_sync(topic, data):
    url = 'http://{}/pub?topic={}'.format(config.NSQD_HTTP_ADDRESS, topic)
    json_data = json.dumps(data)

    code, content = http_request.post_sync(url, json_data)
    if code == 200 and content == 'OK':
        return True
    else:
        log.warning('{}: failed to http post, {}, {}'.format(__file__, code, content))
        return False


def create_subscriber(topic, channel, on_received_message):
    def _message_handler(message, callback):
        message.enable_async()
        data = message.body
        message.finish()
        callback(data)

    return nsq.Reader(
        topic=topic,
        channel=channel,
        message_handler=functools.partial(_message_handler, callback=on_received_message),
        nsqd_tcp_addresses=config.NSQD_TCP_ADDRESSES,
    )


def run():
    nsq.run()


def start():
    raise NotImplementedError()

def stop():
    raise NotImplementedError()
