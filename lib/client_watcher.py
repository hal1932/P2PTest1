# encoding: utf-8
import config
import http_request
import log

import threading
import functools
import time


class ClientWatcher(object):

    def __init__(self, clients, on_client_closed, polling_interval=30, retry_count=2):
        running_token = threading.Event()
        cancellation_token = threading.Event()

        thread = threading.Thread(
            target=functools.partial(
                ClientWatcher.__watch_thread,
                running_token=running_token,
                cancellation_token=cancellation_token,
                clients=clients,
                on_client_closed=on_client_closed,
                polling_interval=polling_interval,
                retry_count=retry_count),
        )
        thread.daemon = True

        self.__watch_thread = thread
        self.__running_token = running_token
        self.__cancel_token = cancellation_token

    def start(self):
        self.__cancel_token.clear()
        self.__watch_thread.start()
        return self

    def stop(self):
        self.__cancel_token.set()
        self.__watch_thread.join()

    def suspend(self):
        self.__running_token.clear()
        log.write('suspend watching clients keep alive')

    def resume(self):
        self.__running_token.set()
        log.write('resume watching clients keep alive')

    @staticmethod
    def __watch_thread(running_token, cancellation_token, clients, on_client_closed, polling_interval, retry_count):
        retry_cache = {}

        while not cancellation_token.is_set():

            if not running_token.is_set():
                running_token.wait()

            if len(clients) > 0:

                def _get_query_url(client):
                    return 'http://{}/{}'.format(client.address, config.QUERY_IS_CLIENT_ALIVE)

                urls = [_get_query_url(client) for client in clients]
                results = http_request.gets_sync(urls)

                # 通信に失敗した回数を数えておく
                client_dict = {_get_query_url(client): client for client in clients}
                for url, (status_code, _) in results.items():
                    client = client_dict[url]
                    if status_code != http_request.STATUS_OK:
                        log.write('client may be disconnected: {}'.format(url))
                        if client in retry_cache:
                            retry_cache[client] += 1
                        else:
                            retry_cache[client] = 1
                    else:
                        log.write('client is alive: {}'.format(url))
                        if url in retry_cache:
                            retry_cache[client] = 0

                # リトライ回数が retry_count を超えたら切断されたと判断する
                closed_clients = filter(
                    lambda client: retry_cache[client] > retry_count,
                    retry_cache)
                for client in closed_clients:
                    on_client_closed(client)
                    retry_cache.pop(client)

            time.sleep(1)
