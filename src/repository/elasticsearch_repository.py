import os
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from models.booking import Booking, UpdateBooking
from models.client import Client, UpdateClient
from models.room import Room, UpdateRoom

elasticsearch_client: AsyncElasticsearch = None


def get_elasticsearch_client() -> AsyncElasticsearch:
    return elasticsearch_client


async def connect_and_init_elasticsearch():
    global elasticsearch_client
    elasticsearch_uri = os.getenv('ELASTICSEARCH_URI')
    try:
        elasticsearch_client = AsyncElasticsearch(elasticsearch_uri.split(','))
        await elasticsearch_client.info()
        print(f'Connected to elasticsearch with uri {elasticsearch_uri}')
    except Exception as ex:
        print(f'Cant connect to elasticsearch: {ex}')


async def close_elasticsearch_connect():
    global elasticsearch_client
    if elasticsearch_client is None:
        return
    await elasticsearch_client.close()

class ElasticSearchRepository:
    def __init__(self):
        self._elasticsearch_index_client = os.getenv('ELASTICSEARCH_INDEX_CLIENT')
        self._elasticsearch_index_room = os.getenv('ELASTICSEARCH_INDEX_ROOM')
        self._elasticsearch_index_booking = os.getenv('ELASTICSEARCH_INDEX_BOOKING')

    async def create_client(self, client_id: str, client: UpdateClient):
        await elasticsearch_client.create(index=self._elasticsearch_index_client, id=client_id, document=dict(client))

    async def create_booking(self, booking_id: str, booking: UpdateBooking):
        await elasticsearch_client.create(index=self._elasticsearch_index_booking, id=booking_id, document=dict(booking))

    async def create_room(self, room_id: str, room: UpdateRoom):
        await elasticsearch_client.create(index=self._elasticsearch_index_room, id=room_id, document=dict(room))
    
    async def update_client(self, client_id: str, client: UpdateClient):
        await elasticsearch_client.update(index=self._elasticsearch_index_client, id=client_id, document=dict(client))

    async def update_booking(self, booking_id: str, booking: UpdateBooking):
        await elasticsearch_client.update(index=self._elasticsearch_index_booking, id=booking_id, document=dict(booking))

    async def update_room(self, room_id: str, room: UpdateRoom):
        await elasticsearch_client.update(index=self._elasticsearch_index_room, id=room_id, document=dict(room))
    
    async def delete_client(self, client_id: str, client: UpdateClient):
        await elasticsearch_client.update(index=self._elasticsearch_index_client, id=client_id)

    async def delete_booking(self, booking_id: str, booking: UpdateBooking):
        await elasticsearch_client.update(index=self._elasticsearch_index_booking, id=booking_id)

    async def delete_room(self, room_id: str, room: UpdateRoom):
        await elasticsearch_client.update(index=self._elasticsearch_index_room, id=room_id)

    async def find_booking_by_query(self, query) -> list:
        response = await elasticsearch_client.search(index=self._elasticsearch_index_booking, query=query,
                                                           filter_path=['hits.hits._id', 'hits.hits._source'])
        if 'hits' not in response.body:
            return []
        result = response.body['hits']['hits']
        booking = list(map(lambda booking:
                                Booking(id=booking['_id'],
                                                client_id=booking['_source']['client_id'],
                                                room_id=booking['_source']['room_id'],
                                                start_dt=booking['_source']['start_dt'],
                                                end_dt=booking['_source']['end_dt'],
                                                is_paid=booking['_source']['is_paid']), result))
        return booking
    
    async def find_booking_by_client_id(self, client_id: str) -> list:
        query = {
            "match": {
                "client_id": client_id
            }
        }
        booking = await self.find_booking_by_query(query)
        return booking

    async def find_booking_by_booking_date(self, booking_date: str) -> list:
        query = {
            "match": {
                "booking_date": booking_date
            }
        }
        booking = await self.find_booking_by_query(query)
        return booking
    
    async def find_booking_by_range(self, left_date: str, right_date: str) -> list:
        query = {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "start_dt": {
                                "gte": left_date,
                                "lte": right_date,
                            }
                        }
                    },
                    {
                        "range": {
                            "end_dt": {
                                "gte": left_date,
                                "lte": right_date,
                            }
                        }
                    },
                ]
            }
        }
        booking = await self.find_booking_by_query(query)
        return booking
    
    
    async def find_booking_by_room_id(self, room_id: str) -> list:
        query = {
            "match": {
                "room_id": room_id
            }
        }
        booking = await self.find_booking_by_query(query)
        return booking


    async def find_rooms_by_query(self, query) -> list:
        response = await elasticsearch_client.search(index=self._elasticsearch_index_room, query=query,
                                                           filter_path=['hits.hits._id', 'hits.hits._source'])
        if 'hits' not in response.body:
            return []
        result = response.body['hits']['hits']
        rooms = list(map(lambda room:
                         Room(id=room['_id'],
                                    description=room['_source']['description'],
                                    country=room['_source']['country'],
                                    city=room['_source']['city'],
                                    name=room['_source']['name'],
                                    address=room['_source']['address']
                                    ), result))
        return rooms    
    
    
    
    async def find_by_address(self, query: str):
        query = {
            "bool": {
                "must": [
                    {"match": {"address": query}},
                ]
            }
        }
        rooms = await self.find_rooms_by_query(query)
        return rooms

    async def find_by_country(self, query: str):
        query = {
            "bool": {
                "must": [
                    {"match": {"country": query}},
                ]
            }
        }
        rooms = await self.find_rooms_by_query(query)
        return rooms

    async def find_by_city(self, query: str):
        query = {
            "bool": {
                "must": [
                    {"match": {"city": query}},
                ]
            }
        }
        rooms = await self.find_rooms_by_query(query)
        return rooms

    async def find_by_name(self, query: str):
        query = {
            "bool": {
                "must": [
                    {"match": {"name": query}},
                ]
            }
        }
        rooms = await self.find_rooms_by_query(query)
        return rooms

    async def check_booking_dates(self, room_id: str, start_dt: str, end_dt: str) -> bool:
        index_exist = await elasticsearch_client.indices.exists(index=self._elasticsearch_index_booking)
        if not index_exist:
            return True
        query_start = {
            "bool": {
                "filter": [
                    {"match": {"room_id": room_id}},
                    {
                        "range": {
                            "start_dt": {
                                "gte": start_dt,
                                "lte": end_dt,
                            }
                        }
                    }
                ]
            }
        }
        booking_start = await self.find_booking_by_query(query_start)
        query_end = {
            "bool": {
                "filter": [
                    {"match": {"room_id": room_id}},
                    {
                        "range": {
                            "end_dt": {
                                "gte": start_dt,
                                "lte": end_dt,
                            }
                        }
                    }
                ]
            }
        }
        booking_end = await self.find_booking_by_query(query_end)
        print(booking_end)
        if (len(booking_start) + len(booking_end)) == 0:
            return True
        else:
            return False

    @staticmethod
    def get_instance():
        return ElasticSearchRepository()
