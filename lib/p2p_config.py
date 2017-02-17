# encoding: utf-8
import random

AVAILABLE_PORT_BASE = 49152 + 100
AVAILABLE_CONTENT_PORT_MAX = 65535 - 100

TOPIC_REGISTER_CLIENT = 'libp2p_register_client'


def get_random_port():
    return random.randint(AVAILABLE_PORT_BASE, AVAILABLE_CONTENT_PORT_MAX)
