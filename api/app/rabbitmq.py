import asyncio
import typing

import aio_pika
import fastapi
from starlette import requests


class RabbitPlugin:
    connection_uri: str = None
    rabbit: typing.Optional[aio_pika.RobustConnection] = None

    async def init_app(self, app: fastapi.FastAPI, connection_uri: str):
        self.connection_uri = connection_uri
        app.state.RABBIT = self
        self.rabbit = None

    async def init(self, retries: int = 40):
        for i in range(retries):
            try:
                self.rabbit = await aio_pika.connect_robust(self.connection_uri)
                return
            except ConnectionError:
                await asyncio.sleep(1)
        raise TimeoutError

    async def close(self):
        if self.rabbit is not None:
            await self.rabbit.close()
            self.rabbit = None

    async def __call__(self):
        if self.rabbit is None:
            raise NotImplementedError("RabbitMQ is not initialized")
        return self.rabbit


rabbit_plugin = RabbitPlugin()


async def depends_rabbit(request: requests.Request) -> aio_pika.RobustConnection:
    return await request.app.state.RABBIT()
