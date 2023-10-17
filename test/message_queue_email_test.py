import asyncio

from aio_pika.abc import AbstractIncomingMessage
from email_test import read_emails

from app.utils.message_queue import RabbitMQWorkQueue


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process(ignore_processed=True):
        await asyncio.sleep(message.body.count(b"."))
        email_id = str(message.body)
        print(f"     email_id body is: {email_id}")


async def main():
    mq = RabbitMQWorkQueue("amqp://guest:guest@localhost/", "test_queue_dummy")
    await mq.connect()
    list_email = read_emails()
    dict_email = {}
    for email in list_email:
        dict_email[email.body["id"]] = email
        await mq.push_message(list_email[0].body["id"])
    await mq.consume_messages(on_message)  # TODO this is blocking
    await mq.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
