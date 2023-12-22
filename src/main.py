from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from api.router import router
from repository.mongo_repository import connect_and_init_mongo, close_mongo_connect
from utils.elasticsearch_utils import connect_and_init_elasticsearch, close_elasticsearch_connect
from repository.cache_repository import connect_memcached, close_memcached_connect


async def startup():
    await connect_and_init_mongo()
    await connect_and_init_elasticsearch()
    connect_memcached()


async def shutdown():
    await close_mongo_connect()
    await close_elasticsearch_connect()
    close_memcached_connect()


load_dotenv()

app = FastAPI()

app.include_router(router, prefix="/airbnb")
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
