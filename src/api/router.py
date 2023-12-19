from bson import ObjectId
from fastapi import APIRouter, status, Depends
from starlette.responses import Response

from models.booking import Booking, UpdateBooking
from models.client import Client, UpdateClient
from models.room import Room, UpdateRoom
from repository.mongo_repository import MongoRepository


router = APIRouter()


@router.post("/clients")
async def add_client(
    name: str,
    repository: MongoRepository = Depends(MongoRepository.get_instance),
):
    client = UpdateClient(name=name)
    client_id = await repository.create_client(client)
    return client_id
    # return name


@router.get("/clients/{client_id}", response_model=Client)
async def get_client_by_id(
    user_id: str, 
    repository: MongoRepository = Depends(MongoRepository.get_instance),
    # memcached_user_client: HashClient = Depends(get_memcached_user_client)
):
    if not ObjectId.is_valid(user_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    """
    user = memcached_user_client.get(user_id)
    if user is not None:
        print('using cached user data', flush=True)
        return user
    """

    user = await repository.get_client_by_id(user_id)
    if user is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    # memcached_user_client.add(user_id, user, int(os.getenv('MEMCACHED_MESSENGER_USER_EXPIRE')))
    
    return user

'''
@router.post("/rooms")
async def add_room(
    room: UpdateRoom,
    repository: MongoRepository = Depends(MongoRepository.get_instance),
):
    room_id = await repository.create_room(room)
    return room_id


@router.get("/rooms/{room_id}", response_model=Room)
async def get_room_by_id(
    room_id: str, 
    repository: MongoRepository = Depends(MongoRepository.get_instance),
    # memcached_rooms: HashClient = Depends(get_memcached_rooms),
):
    if not ObjectId.is_valid(room_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    """
    room = memcached_rooms.get(room_id)
    if room is not None:
        print('using cached room data', flush=True)
        return room
    """

    room = await repository.get_room_by_id(room_id)
    if room is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    # memcached_rooms.add(room_id, riim, int(os.getenv('MEMCACHED_MESSENGER_ROOM_EXPIRE')))
    
    return room


@router.post("/rooms/book_room")
async def book_room_by_id(
    booking: UpdateBooking,
    repository: MongoRepository = Depends(MongoRepository.get_instance),
):
    if not ObjectId.is_valid(booking.client_id) or not ObjectId.is_valid(booking.room_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    booking_id = await repository.book_room(booking)
    return booking_id


@router.post("/rooms/pay_booking")
async def pay_booking_by_id(
    booking_id: str,
    repository: MongoRepository = Depends(MongoRepository.get_instance),
):
    if not ObjectId.is_valid(booking_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    booking_id = await repository.pay_booking(booking_id)
    return booking_id
'''
