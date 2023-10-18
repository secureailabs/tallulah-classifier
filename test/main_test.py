import asyncio
from typing import Dict
from uuid import uuid4

import dotenv
from aio_pika.abc import AbstractIncomingMessage
from email_test import read_emails

from app.email_dao_dict import EmailDaoDict
from app.main import EmailConsumer
from app.models.email import Email_Base
from app.utils.message_queue import RabbitMQWorkQueue


async def main():
    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())

    list_email = read_emails()
    email_dao = EmailDaoDict()
    message_queue = RabbitMQWorkQueue("amqp://guest:guest@localhost/", "test_queue_dummy")
    await message_queue.connect()

    for email in list_email:
        email_id = str(uuid4())
        email_dao.add(email_id, email)
        await message_queue.push_message(email_id)
    email_consumer = EmailConsumer(message_queue, email_dao)
    await email_consumer.main()


if __name__ == "__main__":
    asyncio.run(main())
