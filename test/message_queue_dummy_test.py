import asyncio

from aio_pika.abc import AbstractIncomingMessage

from app.utils.message_queue import RabbitMQWorkQueue


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process(ignore_processed=True):
        await asyncio.sleep(message.body.count(b"."))
        print(f"     Message body is: {message.body!r}")


async def main():
    mq = RabbitMQWorkQueue("amqp://guest:guest@localhost/", "test_queue_dummy")
    await mq.connect()
    await mq.push_message("Hello World! Work Queue 1")
    await mq.push_message("Hello World! Work Queue 2")
    await mq.consume_messages(on_message)  # TODO this is blocking
    await mq.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
