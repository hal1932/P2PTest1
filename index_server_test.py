# encoding: utf-8
import config

from lib import *


class IndexServerTest(index_server_node.IndexServerNode):

    def __init__(self):
        super(IndexServerTest, self).__init__(config.SERVER_CONFIG, self.__process_query)

    def __process_query(self, paths, params, handler):
        if paths[0] == 'clients':
            if 'target' in params:
                if params['target'][0] == 'all':
                    self.__send_all_clients(handler)
            else:
                self.__send_clients(handler, params['sender'][0])
        else:
            handler.send_response(http_request.STATUS_NOT_FOUND)
            handler.end_headers()

    def __send_clients(self, handler, sender_address):
        content = [client.to_dict() for client in self.clients if client.address != sender_address]
        self.write_response(handler, http_request.STATUS_OK, content)

    def __send_all_clients(self, handler):
        content = [client.to_dict() for client in self.clients]
        self.write_response(handler, http_request.STATUS_OK, content)


if __name__ == '__main__':
    IndexServerTest().run()
