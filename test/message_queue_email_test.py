import asyncio
from typing import Dict

from aio_pika.abc import AbstractIncomingMessage

from app.email_dao_mongo import EmailDaoMongo
from app.models.email import Email_Base
from app.utils.message_queue import RabbitMQWorkQueue

dict_email: Dict[str, Email_Base] = {}


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process(ignore_processed=True):
        await asyncio.sleep(message.body.count(b"."))
        email_id = message.body.decode()
        print(f"     email_id  is: {email_id}")
        email = dict_email[email_id]
        if not email.body:
            print(f"     email not found for id: {email_id}")
            return
        print(f"     email body is: {email.body['content']!r}")


async def main():
    email_dao = EmailDaoMongo("emails_temp")
    mq = RabbitMQWorkQueue("amqp://guest:guest@localhost/", "test_queue_dummy")
    await mq.connect()
    list_email = await email_dao.read_all()

    for email in list_email:
        if not email.body:
            print(f"     email not found for id: {email.id}")
            continue
        dict_email[email.body["id"]] = email
        await mq.push_message(email.body["id"])
    await mq.consume_messages(on_message)  # TODO this is blocking
    await mq.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
