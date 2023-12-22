import datetime
import os
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from utils.elasticsearch_utils import get_elasticsearch_client
from models.booking import Booking, UpdateBooking
from models.client import Client, UpdateClient
from models.room import Room, UpdateRoom

elasticsearch_client: AsyncElasticsearch = None

class ElasticSearchRepository:
    def __init__(self):
        self._elasticsearch_index_client = os.getenv('ELASTICSEARCH_INDEX_CLIENT')
        self._elasticsearch_index_room = os.getenv('ELASTICSEARCH_INDEX_ROOM')
        self._elasticsearch_index_booking = os.getenv('ELASTICSEARCH_INDEX_CLIENT')

    async def create_client(self, client_id: str, client: UpdateClient):
        await self._elasticsearch_client.create(index=self._elasticsearch_index_client, id=client_id, document=dict(client))

    async def create_booking(self, booking_id: str, booking: UpdateBooking):
        await self._elasticsearch_client.create(index=self._elasticsearch_index_booking, id=booking_id, document=dict(booking))

    async def create_room(self, room_id: str, room: UpdateRoom):
        await self._elasticsearch_client.create(index=self._elasticsearch_index_room, id=room_id, document=dict(room))
    
    async def update_client(self, client_id: str, client: UpdateClient):
        await self._elasticsearch_client.update(index=self._elasticsearch_index_client, id=client_id, document=dict(client))

    async def update_booking(self, booking_id: str, booking: UpdateBooking):
        await self._elasticsearch_client.update(index=self._elasticsearch_index_booking, id=booking_id, document=dict(booking))

    async def update_room(self, room_id: str, room: UpdateRoom):
        await self._elasticsearch_client.update(index=self._elasticsearch_index_room, id=room_id, document=dict(room))
    
    async def delete_client(self, client_id: str, client: UpdateClient):
        await self._elasticsearch_client.update(index=self._elasticsearch_index_client, id=client_id)

    async def delete_booking(self, booking_id: str, booking: UpdateBooking):
        await self._elasticsearch_client.update(index=self._elasticsearch_index_booking, id=booking_id)

    async def delete_room(self, room_id: str, room: UpdateRoom):
        await self._elasticsearch_client.update(index=self._elasticsearch_index_room, id=room_id)

    async def find_booking_by_query(self, query) -> list:
        response = await self._elasticsearch_client.search(index=self._elasticsearch_index, query=query,
                                                           filter_path=['hits.hits._id', 'hits.hits._source'])
        if 'hits' not in response.body:
            return []
        result = response.body['hits']['hits']
        booking = list(map(lambda reservation:
                                Booking(id=reservation['_id'],
                                                client_id=reservation['_source']['client_id'],
                                                room_id=reservation['_source']['room_id'],
                                                start_dt=reservation['_source']['start_dt'],
                                                end_dt=reservation['_source']['end_dt'],
                                                booking_status=reservation['_source']['booking_status']), result))
        return booking
    
    async def find_booking_by_client_id(self, client_id: str) -> list:
        query = {
            "match": {
                "client_id": client_id
            }
        }
        booking = await self.find_booking_by_query(query)
        return booking

    async def find_booking_by_booking_date(self, booking_date: datetime) -> list:
        query = {
            "match": {
                "booking_date": booking_date
            }
        }
        booking = await self.find_booking_by_query(query)
        return booking
    
    async def find_booking_by_range(self, left_date: datetime, right_date: datetime) -> list:
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
        response = await self._elasticsearch_client.search(index=self._elasticsearch_index, query=query,
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
    
    
    
    async def find_rooms_by_address(self, query: str):
        query = {
            "bool": {
                "must": [
                    {"match": {"address": query}},
                ]
            }
        }
        rooms = await self.find_rooms_by_query(query)
        return rooms

    async def find_rooms_by_country(self, query: str):
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


    @staticmethod
    def get_instance():
        return ElasticSearchRepository()
