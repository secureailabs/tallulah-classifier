import asyncio
from typing import Dict
from uuid import uuid4

import dotenv

from app.email_dao_dict import EmailDaoDict
from app.email_dao_mongo import EmailDaoMongo
from app.main import EmailConsumer
from app.utils.message_queue import RabbitMQWorkQueue


async def main():
    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())

    email_dao = EmailDaoMongo("mongodb://127.0.0.1:27017", "tallulah", "emails_temp")
    message_queue = RabbitMQWorkQueue("amqp://guest:guest@localhost/", "test_queue_dummy")
    await message_queue.connect()

    for email in await email_dao.read_all():
        email_id = await email_dao.create(email)
        await message_queue.push_message(str(email_id))
    email_consumer = EmailConsumer(message_queue, email_dao)
    await email_consumer.main()


if __name__ == "__main__":
    asyncio.run(main())
