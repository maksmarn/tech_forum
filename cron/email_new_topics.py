import datetime

from models.settings import db
from models.topic import Topic
from models.user import User
from utils.email_helper import send_email


def new_topics_email():
    print("Cron job: New topics daily email")
    
    # This finds all of the topics created in the last 24 hours
    yesterdays_topics = db.query(Topic).filter(Topic.created > (datetime.datetime.now() - datetime.timedelta(days=1))).all()
    
    print(yesterdays_topics)
    
    # If there are no topics, the task is finished without sending an email
    if not yesterdays_topics:
        print("There haven't been any new topics, so there's no need to send an email.")
    else:
        # Create an email message
        message = "Topics of the last day:\n"
        
        for topic in yesterdays_topics:
            message += f"- {topic.title}\n"
            
        print(message)
        
        users = db.query(User).all()
        
        for user in users:
            if user.email_address:
                send_email(receiver_email=user.email_address, subject="The topics of the last day at Sigma Tech Forum", text=message)
                
                
if __name__ == '__main__':
    new_topics_email()
