# encoding: utf-8
import config

from lib import *

import time


class PeerTest(peer_node.PeerNode):

    def __init__(self):
        super(PeerTest, self).__init__(config.PEER_CONFIG, self.__run_impl)

    def __run_impl(self, server):
        response = self.send_to_index_server('/clients', target='all')
        print(response)

        response = self.send_to_index_server('/clients')
        print(response)

        time.sleep(3)

        server.stop()


if __name__ == '__main__':
    PeerTest().run()
