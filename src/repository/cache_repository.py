import os
import sys
from datetime import datetime

from pymemcache import HashClient

from utils.cache_utils import JsonSerializer


memcached_clients_client: HashClient = None
memcached_rooms_client: HashClient = None
memcached_bookings_client: HashClient = None


def connect_memcached():
    global memcached_clients_client
    global memcached_rooms_client
    global memcached_bookings_client

    memcached_clients_uri = os.getenv('MEMCACHED_CLIENTS_URI')
    memcached_rooms_uri = os.getenv('MEMCACHED_ROOMS_URI')
    memcached_bookings_uri = os.getenv('MEMCACHED_BOOKINGS_URI')

    memcached_uris = [memcached_clients_uri,
                      memcached_rooms_uri,
                      memcached_bookings_uri,]

    memcached_clients = [None for _ in range(len(memcached_uris))]

    for i, memcached_uri in enumerate(memcached_uris):
        try:
            memcached_clients[i] = HashClient(memcached_uri.split(','), serde=JsonSerializer())
            print(f'Connected to memcached with uri {memcached_uri}', flush=True)
        except Exception as ex:
            print(f'Cant connect to user memcached: {ex}', flush=True)

    map_client_array(memcached_clients)


def close_memcached_connect():
    global memcached_clients_client
    global memcached_rooms_client
    global memcached_bookings_client

    memcached_clients = [memcached_clients_client,
                         memcached_rooms_client,
                         memcached_bookings_client]

    for memcached_client in memcached_clients:
        if memcached_client is not None:
            memcached_client.close()


def map_client_array(memcached_clients):
    global memcached_clients_client
    global memcached_rooms_client
    global memcached_bookings_client

    memcached_clients_client = memcached_clients[0]
    memcached_rooms_client = memcached_clients[1]
    memcached_bookings_client = memcached_clients[2]


def get_memcached_clients_client():
    return memcached_clients_client


def get_memcached_rooms_client():
    return memcached_rooms_client


def get_memcached_bookings_client():
    return memcached_bookings_client
