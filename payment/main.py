from ctypes import cast
from itertools import product
from starlette.requests import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from decouple import config
from unipath import Path
import requests


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

@app.post('/orders')
async def create(request: Request): #id, quantity
    body = await request.json()

    req = requests.get('http://localhost:8000/products/%s' % body['id'])
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2*product['price'],
        total= 1.2*product['price'],
        quantity=body['id'],
        status='pending'
    )

    order.save()

    order_completed(order)

    return order

#Function to change the Order status by default
def order_completed(order: Order):
    order.status = 'completed'
    order.save()


    #Just for test the data retrived form the inventory microservice
    #return req.json()



