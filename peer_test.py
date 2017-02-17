# encoding: utf-8
import config

from lib import *

import time
import json


class PeerTest(peer_node.PeerNode):

    def __init__(self):
        super(PeerTest, self).__init__(config.PEER_CONFIG, self.__run_impl)

    def __run_impl(self, server):
        status, content = self.send_to_index_server('/clients', target='all')
        if status == http_request.STATUS_OK:
            for item in content:
                client = node.NodeBase.from_dict(item)
                print(client.address)

        status, content = self.send_to_index_server('/clients')
        if status == http_request.STATUS_OK:
            for item in content:
                client = node.NodeBase.from_dict(item)
                print(client.address)

        time.sleep(10)

        server.stop()


if __name__ == '__main__':
    PeerTest().run()
