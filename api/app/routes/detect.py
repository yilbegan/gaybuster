import aio_pika
import asyncio
import base64
import uuid
import ujson

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from starlette import status
from .models import DetectionResponse
from ..rabbitmq import depends_rabbit

router = APIRouter()
TIMEOUT = 40


@router.post('/', response_model=DetectionResponse)
async def detect_gay(
    photo: UploadFile = File(None),
    rabbit: aio_pika.RobustConnection = Depends(depends_rabbit),
):

    channel = await rabbit.channel()
    await channel.declare_queue("process_photos")

    response_queue = f"processing_result.{uuid.uuid4().hex}"
    queue = await channel.declare_queue(response_queue, auto_delete=True)

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=ujson.dumps(
                {
                    "image": base64.urlsafe_b64encode(await photo.read()).decode('utf-8'),
                    "response_queue": response_queue,
                }
            ).encode("utf-8")
        ),
        routing_key="recognize_photos",
    )

    for i in range(TIMEOUT * 2):
        answer = await queue.get(no_ack=True, fail=False)
        if answer is not None:
            break
        await asyncio.sleep(0.5)

    else:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Gay Detection worker was not send response. Try again later."
        )

    data = ujson.loads(answer.body.decode("utf-8"))
    return DetectionResponse(count=len(data), faces=data)
