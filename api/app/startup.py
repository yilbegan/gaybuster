from .main import app
from .config import RABBITMQ_CONNECTION_URI
from .rabbitmq import rabbit_plugin


@app.on_event("startup")
async def init_rabbit():
    await rabbit_plugin.init_app(app, connection_uri=RABBITMQ_CONNECTION_URI)
    await rabbit_plugin.init()


@app.on_event("shutdown")
async def close_rabbit():
    await rabbit_plugin.close()
