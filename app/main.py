# -------------------------------------------------------------------------------
# Tallulah
# main.py
# -------------------------------------------------------------------------------
"""The main entrypoint of the Tallulah classifier"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Array Insights, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Array Insights, Inc.
# -------------------------------------------------------------------------------

import asyncio

import cloudpickle as cpkl
import dotenv
from aio_pika.abc import AbstractIncomingMessage
from models.common import PyObjectId
from models.email import Emails, EmailState
from utils.message_queue import MessageQueueClient, RabbitMQWorkQueue
from utils.secrets import get_secret

# read the environment variable form the .env file
dotenv.load_dotenv(dotenv.find_dotenv())


class EmailClassifier:
    """The email classifier"""

    def __init__(self, model_path: str):
        f = open(model_path, "rb")
        self.model = cpkl.load(f)

    def predict_email_tags(self, message: str) -> str:
        """Predict the tags of an email"""
        # combine the subject and body of each email together and pass it in as text input; You can pass an array of emails
        result = self.model.predict([message])
        print(result[0])
        return result[0]


# classifier = EmailClassifier("email_model.pkl")


# Connect to rabbit mq and listen for messages
async def on_email_receive(message: AbstractIncomingMessage) -> None:
    async with message.process(ignore_processed=True):
        # Read the message body
        email_id = PyObjectId(message.body.decode())

        # # Get the email from the database
        emails = await Emails.read(email_id=email_id)

        # tags = classifier.predict_email_tags(emails[0].subject + emails[0].body["content"])
        tags = "test"

        # # Update the email with the tags
        await Emails.update(
            query_message_id=email_id,
            update_message_tags=[tags],
            update_message_state=EmailState.PROCESSED,
        )

        print(f"Message body is: {str(email_id)}")


async def main():
    rabbit_mq_connect_url = get_secret("rabbit_mq_host")
    rabbit_mq_client = MessageQueueClient(RabbitMQWorkQueue(url=f"{rabbit_mq_connect_url}:5672"))
    await rabbit_mq_client.connect()
    await rabbit_mq_client.consume_messages(on_email_receive)
    await rabbit_mq_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
