# encoding: utf-8
from lib import *


class IndexServer(node.NodeBase):

    def __init__(self):
        super(IndexServer, self).__init__(port=config.get_random_port())

        self.__client_pool = client_pool.ClientPool(self.host, self.port)

        self.__query_server = query_server.QueryServer(
            self.port, self.__client_pool.clients)

        self.__clients_watcher = client_watcher.ClientWatcher(
            self.__client_pool.clients, self.__client_pool.remove)

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


if __name__ == '__main__':
    IndexServer().run()
