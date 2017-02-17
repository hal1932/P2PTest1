# encoding: utf-8
import p2p_config
import node
import client_pool
import query_server
import client_watcher


class IndexServerConfig(object):

    @property
    def nsqd_config(self):
        return self.__nsqd_config

    @property
    def peer_ping_timeout(self):
        return self.__peer_ping_timeout

    @property
    def max_peer_count(self):
        return self.__max_peer_count

    def __init__(self, nsqd_config, peer_ping_timeout, max_peer_count):
        self.__nsqd_config = nsqd_config
        self.__peer_ping_timeout = peer_ping_timeout
        self.__max_peer_count = max_peer_count


class IndexServerNode(node.NodeBase):

    @property
    def clients(self):
        return self.__client_pool.clients

    def __init__(self, config, on_received_query):
        super(IndexServerNode, self).__init__(port=p2p_config.get_random_port())

        self.__client_pool = client_pool.ClientPool(config, self.host, self.port)
        self.__query_server = query_server.QueryServer(self.port, on_received_query)
        self.__clients_watcher = client_watcher.ClientWatcher(self.clients, self.__client_pool.remove)

        def _on_added_client(clients):
            # 0から1になったら監視を再開
            # ClientPool内でロックかけてるから一気に2になったりはしない
            if len(clients) == 1:
                self.__clients_watcher.resume()

        def _on_removed_client(clients):
            # 0になったら監視を一時停止
            if len(clients) == 0:
                self.__clients_watcher.suspend()

        self.__client_pool.set_connection_event(_on_added_client, _on_removed_client)
        self.__clients_watcher.suspend()

    def run(self):
        self.__clients_watcher.start()
        self.__query_server.start()

        self.__client_pool.run()

    def write_response(self, handler, status, content):
        self.__query_server.write_response(handler, status, content)
