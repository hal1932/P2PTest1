# encoding: utf-8
from lib import *

_NSQD_CONFIG = messaging.NsqdConfig(
    http_address='127.0.0.1:4151',
    tcp_addresses=['127.0.0.1:4150', ],
)

SERVER_CONFIG = index_server_node.IndexServerConfig(
    nsqd_config=_NSQD_CONFIG,
    peer_ping_timeout=5,
    max_peer_count=None,
)

PEER_CONFIG = peer_node.PeerConfig(
    nsqd_config=_NSQD_CONFIG,
)
