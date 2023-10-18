import asyncio
from typing import Dict

from aio_pika.abc import AbstractIncomingMessage
from email_test import read_emails

from app.models.email import Email_Base
from app.utils.message_queue import RabbitMQWorkQueue

dict_email: Dict[str, Email_Base] = {}


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process(ignore_processed=True):
        await asyncio.sleep(message.body.count(b"."))
        email_id = message.body.decode()
        print(f"     email_id  is: {email_id}")
        email = dict_email[email_id]
        print(f"     email body is: {email.body['content']!r}")


async def main():
    mq = RabbitMQWorkQueue("amqp://guest:guest@localhost/", "test_queue_dummy")
    await mq.connect()
    list_email = read_emails()

    for email in list_email:
        dict_email[email.body["id"]] = email
        await mq.push_message(email.body["id"])
    await mq.consume_messages(on_message)  # TODO this is blocking
    await mq.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
