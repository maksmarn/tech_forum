import os
import uuid
import smartninja_redis

redis = smartninja_redis.from_url(os.environ.get("REDIS_URL"))


def create_csrf_token(username):
    csrf_token = str(uuid.uuid4())
    redis.set(name=csrf_token, value=username)
    
    return csrf_token


def validate_csrf(csrf, username):
    # CSRF from redis
    redis_csrf_username = redis.get(name=csrf)
    
    # If the CSRF token is found in a cache
    if redis_csrf_username:
        csrf_username = redis_csrf_username.decode()
        # True if they match, false otherwise
        return username == csrf_username
    
    else:
        return False
