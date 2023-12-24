from bson import ObjectId
from fastapi import APIRouter, status, Depends
import os
from pymemcache import HashClient
from typing import Optional
from starlette.responses import Response

from models.booking import Booking, UpdateBooking
from models.client import Client, UpdateClient
from models.room import Room, UpdateRoom
from repository.mongo_repository import MongoRepository
from repository.elasticsearch_repository import ElasticSearchRepository
from repository.cache_repository import get_memcached_clients_client, get_memcached_rooms_client, get_memcached_bookings_client


router = APIRouter()


@router.post("/clients")
async def add_client(
    name: str,
    repository: MongoRepository = Depends(MongoRepository.get_instance),
    search: ElasticSearchRepository = Depends(ElasticSearchRepository.get_instance)
):
    client = UpdateClient(name=name)
    existed_client = await repository.get_client_by_name(name)
    if existed_client is not None:
        print(f'Client with name {name} already exists', flush=True)
        print(f'Existed_client {existed_client}', flush=True)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    client_id = await repository.create_client(client)
    await search.create_client(client_id, client)
    return client_id


@router.get("/clients/{client_id}", response_model=Client)
async def get_client_by_id(
    client_id: str, 
    repository: MongoRepository = Depends(MongoRepository.get_instance),
    memcached_clients_client: HashClient = Depends(get_memcached_clients_client)
):
    if not ObjectId.is_valid(client_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


    client = memcached_clients_client.get(client_id)
    if client is not None:
        print('using cached client data', flush=True)
        return client


    client = await repository.get_client_by_id(client_id)
    if client is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    memcached_clients_client.add(client_id, client, int(os.getenv('MEMCACHED_CLIENTS_EXPIRE')))
    
    return client


@router.post("/rooms")
async def add_room(
    name: str,
    city: str,
    country: str,
    address: str,
    description: str,
    repository: MongoRepository = Depends(MongoRepository.get_instance),
    search: ElasticSearchRepository = Depends(ElasticSearchRepository.get_instance)
):
    room = UpdateRoom(name=name, city=city, country=country, address=address, description=description)
    room_id = await repository.create_room(room)
    await search.create_room(room_id, room)
    return room_id


@router.get("/rooms/{room_id}", response_model=Room)
async def get_room_by_id(
    room_id: str, 
    repository: MongoRepository = Depends(MongoRepository.get_instance),
    memcached_rooms_client: HashClient = Depends(get_memcached_rooms_client),
):
    if not ObjectId.is_valid(room_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    room = memcached_rooms_client.get(room_id)
    if room is not None:
        print('using cached room data', flush=True)
        return room

    room = await repository.get_room_by_id(room_id)
    if room is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    memcached_rooms_client.add(room_id, room, int(os.getenv('MEMCACHED_ROOMS_EXPIRE')))
    
    return room


@router.post("/bookings/book_room")
async def book_room_by_id(
    client_id: str,
    room_id: str,
    is_paid: bool,
    start_dt: str,
    end_dt: str,
    repository: MongoRepository = Depends(MongoRepository.get_instance),
    search: ElasticSearchRepository = Depends(ElasticSearchRepository.get_instance)
):
    if not ObjectId.is_valid(client_id) or not ObjectId.is_valid(room_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    client = await repository.get_client_by_id(client_id)
    if client is None:
        print(f'Client with id {client_id} do not exist', flush=True)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    room = await repository.get_room_by_id(room_id)
    if room is None:
        print(f'Room with id {room_id} do not exist', flush=True)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
        
    if not await search.check_booking_dates(room_id, start_dt, end_dt):
        print(f'Room with id {room_id} is already booked in this dates', flush=True)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    booking = UpdateBooking(client_id=client_id, room_id=room_id, is_paid=is_paid, start_dt=start_dt, end_dt=end_dt)
    booking_id = await repository.book_room(booking)
    await search.create_booking(booking_id, booking)
    return booking_id


@router.post("/bookings/pay_booking")
async def pay_booking_by_id(
    booking_id: str,
    repository: MongoRepository = Depends(MongoRepository.get_instance),
    search: ElasticSearchRepository = Depends(ElasticSearchRepository.get_instance),
    memcached_bookings_client: HashClient = Depends(get_memcached_bookings_client),
):
    if not ObjectId.is_valid(booking_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    booking = await repository.get_booking_by_id(booking_id)
    if booking is None:
        print(f'Booking with id {booking_id} do not exist', flush=True)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    paid_booking = await repository.pay_booking(booking_id)
    if paid_booking is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    memcached_bookings_client.delete(booking_id)
    memcached_bookings_client.add(booking_id, paid_booking, int(os.getenv('MEMCACHED_BOOKINGS_EXPIRE')))
    return paid_booking


@router.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking_by_id(
    booking_id: str, 
    repository: MongoRepository = Depends(MongoRepository.get_instance),
    memcached_bookings_client: HashClient = Depends(get_memcached_bookings_client),
):
    if not ObjectId.is_valid(booking_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    booking = memcached_bookings_client.get(booking_id)
    if booking is not None:
        print('using cached booking data', flush=True)
        return booking

    booking = await repository.get_booking_by_id(booking_id)
    if booking is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    memcached_bookings_client.add(booking_id, booking, int(os.getenv('MEMCACHED_BOOKINGS_EXPIRE')))
    
    return booking


@router.get("/country/{country_name}")
async def find_by_country(country_name: str,
                                       search: ElasticSearchRepository = Depends(ElasticSearchRepository.get_instance)):
    rooms = await search.find_by_country(country_name)
    if rooms is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return {"rooms": rooms}


@router.get("/city/{city_name}")
async def find_by_city(city_name: str,
                                       search: ElasticSearchRepository = Depends(ElasticSearchRepository.get_instance)):
    rooms = await search.find_by_city(city_name)
    if rooms is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return {"rooms": rooms}


@router.get("/room_name/{room_name}")
async def find_by_name(room_name: str,
                                       search: ElasticSearchRepository = Depends(ElasticSearchRepository.get_instance)):
    rooms = await search.find_by_name(room_name)
    if rooms is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return {"rooms": rooms}


@router.get("/address/{address}")
async def find_by_address(address: str,
                                       search: ElasticSearchRepository = Depends(ElasticSearchRepository.get_instance)):
    rooms = await search.find_by_address(address)
    if rooms is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return {"rooms": rooms}
