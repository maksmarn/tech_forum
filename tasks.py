import os
import requests
import json

from huey import RedisHuey

# This creates a Huey worker that uses Redis to store tasks in it
huey = RedisHuey(url=os.getenv('REDIS_URL'))


# @huey.task creates a function, which is marked as a background task. If it fails, Huey will try max. 10 times with a 10 second delay to successfully execute the task
@huey.task(retries=10, retry_delay=10)
def send_email_task(receiver_email, subject, text):
    sender_email = os.getenv("MY_SENDER_EMAIL")  # Your website's official email address
    api_key = os.getenv('SENDGRID_API_KEY')

    if sender_email and api_key:
        url = "https://api.sendgrid.com/v3/mail/send"

        data = {"personalizations": [{
                    "to": [{"email": receiver_email}],
                    "subject": subject
                }],

                "from": {"email": sender_email},

                "content": [{
                    "type": "text/plain",
                    "value": text
                }]
        }

        headers = {
            'authorization': "Bearer {0}".format(api_key),
            'content-type': "application/json"
        }

        response = requests.request("POST", url=url, data=json.dumps(data), headers=headers)

        print("Sent to SendGrid")
        print(response.text)
    else:
        print("No env vars or no email address")
        print("The email wasn't sent.")
        print(f"If it were, this would have been the subject: {subject}.")
        print(f"And this would have been the text: {text}.")
        print(f"It would have been sent to: {receiver_email}.")