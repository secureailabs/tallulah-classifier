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

from app.email_classifier_tfid import EmailClassifierTfid
from app.email_dao_base import EmailDaoBase
from app.email_dao_mongo import EmailDaoMongo
from app.models.common import PyObjectId
from app.models.email import EmailState
from app.utils.message_queue import MessageQueueType, RabbitMQWorkQueue
from app.utils.secrets import get_secret


class EmailConsumer:
    def __init__(
        self,
        rabbit_mq_client: MessageQueueType,
        email_dao: EmailDaoBase,
    ):
        # read the environment variable form the .env file if available
        self.rabbit_mq_client = rabbit_mq_client
        self.email_dao = email_dao

        self.classifier = EmailClassifierTfid()
        self.classifier.load("email_model.pkl")

    # Connect to rabbit mq and listen for messages
    async def on_email_receive(self, message: AbstractIncomingMessage) -> None:
        async with message.process(ignore_processed=True):
            # Read the message body
            email_id = PyObjectId(message.body.decode())

            # # Get the email from the database
            emails = await self.email_dao.read(email_id=email_id)
            list_annotation = self.classifier.predict_email_tags(emails[0])
            # # Update the email with the tags
            await self.email_dao.update(
                query_message_id=email_id,
                update_message_state=EmailState.PROCESSED,
                update_message_annotations=list_annotation,
            )

            print(f"Message body is: {str(email_id)}")

    async def main(self):
        await self.rabbit_mq_client.connect()
        await self.rabbit_mq_client.consume_messages(self.on_email_receive)
        await self.rabbit_mq_client.disconnect()


if __name__ == "__main__":
    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())
    mongodb_connection_string = get_secret("mongo_connection_url")
    mongodb_database_name = get_secret("mongo_db_name")
    mongodb_collection_name = get_secret("mongodb_collection_name")
    email_dao = EmailDaoMongo(mongodb_connection_string, mongodb_database_name, mongodb_collection_name)

    rabbit_mq_connect_hostname = get_secret("rabbit_mq_hostname")
    rabbit_mq_connect_port = get_secret("rabbit_mq_port")  # 5672
    rabbit_mq_connect_queue_name = get_secret("rabbit_mq_queue_name")
    rabbit_mq_client = RabbitMQWorkQueue(
        url=f"{rabbit_mq_connect_hostname}:{rabbit_mq_connect_port}",
        queue_name=rabbit_mq_connect_queue_name,
    )

    email_consumer = EmailConsumer(rabbit_mq_client, email_dao)
    asyncio.run(email_consumer.main())
