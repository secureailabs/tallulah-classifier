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

import dotenv
from aio_pika.abc import AbstractIncomingMessage
from models.common import PyObjectId
from models.email import Emails, EmailState
from utils.message_queue import RabbitMQWorkQueue
from utils.secrets import get_secret

from app.email_classifier import EmailClassifier


class EmailConsumer:
    def __init__(self):
        # read the environment variable form the .env file if available
        if dotenv.find_dotenv():
            dotenv.load_dotenv(dotenv.find_dotenv())

        self.rabbit_mq_connect_hostname = get_secret("rabbit_mq_host")
        self.rabbit_mq_connect_port = get_secret("rabbit_mq_port")  # 5672

        self.classifier = EmailClassifier()
        self.classifier.load("email_model.pkl")

    # Connect to rabbit mq and listen for messages
    async def on_email_receive(self, message: AbstractIncomingMessage) -> None:
        async with message.process(ignore_processed=True):
            # Read the message body
            email_id = PyObjectId(message.body.decode())

            # # Get the email from the database
            emails = await Emails.read(email_id=email_id)

            # tags = classifier.predict_email_tags(emails[0].subject + emails[0].body["content"])

            tags = self.classifier.predict_email_tags(emails[0].subject + emails[0].body["content"])

            # # Update the email with the tags
            await Emails.update(
                query_message_id=email_id,
                update_message_tags=[tags],
                update_message_state=EmailState.PROCESSED,
            )

            print(f"Message body is: {str(email_id)}")

    async def main(self):
        rabbit_mq_client = RabbitMQWorkQueue(
            url=f"{self.rabbit_mq_connect_hostname}:{self.rabbit_mq_connect_port}", queue_name="email_queue"
        )

        await rabbit_mq_client.connect()
        await rabbit_mq_client.consume_messages(self.on_email_receive)
        await rabbit_mq_client.disconnect()


if __name__ == "__main__":
    email_consumer = EmailConsumer()
    asyncio.run(email_consumer.main())
