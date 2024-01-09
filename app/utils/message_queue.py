import abc
import asyncio
from typing import Callable

from aio_pika import DeliveryMode, Message, connect_robust


class MessageQueueType(abc.ABC):
    @abc.abstractmethod
    def connect(self):
        raise NotImplementedError

    @abc.abstractmethod
    def push_message(self, message):
        raise NotImplementedError

    @abc.abstractmethod
    def consume_messages(self, on_message: Callable):
        raise NotImplementedError

    @abc.abstractmethod
    def disconnect(self):
        raise NotImplementedError


class RabbitMQWorkQueue(MessageQueueType):
    def __init__(self, url: str, queue_name: str):
        self.url = url
        self.queue_name = queue_name
        self.is_initialized = False

    async def connect(self):
        print(f"Connecting to rabbitmq on {self.url}...")
        self.connection = await connect_robust(self.url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name, durable=True)
        self.is_initialized = True

    async def push_message(self, message: str):
        if not self.is_initialized:
            raise Exception("Not initialized")

        await self.channel.default_exchange.publish(
            Message(message.encode(), delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=self.queue.name,
        )

    async def consume_messages(self, on_message: Callable):
        if not self.is_initialized:
            raise Exception("Not initialized")

        await self.channel.set_qos(prefetch_count=1)

        await self.queue.consume(on_message)

        print(" [*] Waiting for messages. To exit press CTRL+C")
        await asyncio.Future()

    async def disconnect(self):
        if not self.is_initialized:
            raise Exception("Not initialized")

        await self.connection.close()
