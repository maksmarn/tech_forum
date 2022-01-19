import os
from tasks import send_email_task


def send_email(receiver_email, subject, text):
    
    # If the app is running on heroku, we call the send_email_task
    if os.getenv('REDIS_URL'):
        send_email_task(receiver_email, subject, text)
        
    
    else:
        print("We on the localhost, so the email is not for real.")
        print("---------------PRETEND EMAIL BELOW----------------")
        print(f"Email recipient: {receiver_email}")
        print(f"Subject: {subject}")
        print(f"Text: {text}")
        print("---------------END OF PRETEND EMAIL---------------")
