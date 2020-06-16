import asyncio
import tenacity

import aio_pika

try:
    import ujson as json
except ImportError:
    import json

from loguru import logger

from .config import RABBITMQ_CONNECTION_URI
from .detection import *


async def get_rabbit_connection():
    while True:
        try:
            return await aio_pika.connect_robust(RABBITMQ_CONNECTION_URI)
        except ConnectionError:
            await asyncio.sleep(1)


@tenacity.retry(wait=5)
async def main():
    logger.info('Consuming events from "recognize_photos"')
    connection = await get_rabbit_connection()

    async with connection:
        channel = await connection.channel()

        queue = await channel.declare_queue("recognize_photos")
        vgg_face = get_vgg_face()
        classifier_model = get_classifier_model()
        face_detector = get_face_detector()

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                message: aio_pika.IncomingMessage
                try:
                    await process_photo(
                        channel,
                        message, vgg_face, classifier_model, face_detector
                    )
                except Exception:  # noqa
                    logger.exception('Image processing error')


async def process_photo(
    channel: aio_pika.Channel, message: aio_pika.IncomingMessage, vgg_face, classifier, face_detector
):
    async with message.process():
        task = json.loads(message.body)
        image, resizing_ratio = load_image(
            image_encoded=task.get("image"),
            image_url=task.get("image_url"),
        )

        result = process_image(image, face_detector, classifier, vgg_face, resizing_ratio)
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(result).encode('utf-8')),
            routing_key=task["response_queue"],
        )

        logger.info(
            f'Processed {task["response_queue"]} '
            f'from {"url" if task.get("url") is not None else "file"} '
            f'[resized by {round(resizing_ratio)}]'
        )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
