# encoding: utf-8
import hostinfo


class NodeBase(object):

    @property
    def host(self): return self.__host

    @property
    def port(self): return self.__port

    @property
    def user(self): return self.__user

    @property
    def address(self): return '{}:{}'.format(self.host, self.port)

    def __init__(self, host=None, port=None, user=None):
        if host is None:
            self.__host = hostinfo.get_ipv4_address()
        else:
            self.__host = host

        self.__port = port

        if user is None:
            self.__user = hostinfo.get_user()
        else:
            self.__user = user

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
        }

    @staticmethod
    def from_dict(dic):
        return NodeBase(dic['host'], dic['port'], dic['user'])

    def update_port(self, port):
        self.__port = port
