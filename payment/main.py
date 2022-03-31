from ctypes import cast
from itertools import product
from starlette.requests import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks  #using for asyncronuos task in order to avoid
from decouple import config
from redis_om import get_redis_connection, HashModel
from unipath import Path
import requests, time


BASE_DIR = Path(__file__).parent

HOST = config('HOST')
PORT = config('PORT')
PASSWORD = config('PASSWORD')
DECODE_RESPONSES = config("DECODE_RESPONSES")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

#This should be a different DB (mongdb or mysql) for this tutorial was used the same
redis = get_redis_connection(
    host=config('HOST', cast=str),
    port=config('PORT', cast=int),
    password=config('PASSWORD', cast=str),
    decode_responses=config("DECODE_RESPONSES", cast=bool)
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str #peding, compleated or refunded

    class Meta:
        database: redis


@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)

@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks): #id, quantity

    body = await request.json()

    req = requests.get('http://127.0.0.1:8000/products/%s' % body['id'])

    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2*product['price'],
        total=1.2*product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save()

    background_tasks.add_task(order_completed, order)

    return order

     #Just for test the data retrived form the inventory microservice
    #return req.json()

#Function to change the Order status by default
def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()

    redis.xadd('order_completed', order.dict(), '*') #using Redis streams


## if a Error :redis.exceptions.ConnectionError: Error 61 connecting to localhost:6379. Connection refused. happens porceed to install redis and run redis-server

   



