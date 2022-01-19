import os
import random

from huey import RedisHuey

# This creates a Huey worker that uses Redis to store tasks in it
huey = RedisHuey(url=os.getenv('REDIS_URL'))


# @huey.task creates a function, which is marked as a background task. If it fails, Huey will try max. 5 times with a 5 second delay to successfully execute the task
@huey.task(retries=5, retry_delay=5)
def get_random_num():
    print("This is a task for producing a random number")
    num = random.randint(1, 3)
    print(f"The random number is {num}.")
    
    # If the random integer is exactly 1, the task is successfully executed, otherwise it fails
    if num == 1:
        return True
    
    else:
        raise Exception("There has been an error in the worker")