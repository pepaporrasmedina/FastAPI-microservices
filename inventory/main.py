from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel

app = FastAPI()


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


