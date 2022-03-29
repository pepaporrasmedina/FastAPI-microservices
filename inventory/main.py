from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="redis-13289.c52.us-east-1-4.ec2.cloud.redislabs.com",
    port=13289,
    password="nvzAKvSgwYYNbv17slBby8MMIH0JOi6q",
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity_available: int

    class Meta:
        database = redis

@app.get('/products')
def all():
    return Product.all_pks()


