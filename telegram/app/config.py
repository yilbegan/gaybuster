from environs import Env
from typing import Optional

env = Env()

TELEGRAM_TOKEN: str = env.str("TELEGRAM_TOKEN")
GAYBUSTER_API_URL: str = env.str("GAYBUSTER_API_URL", default="http://localhost/detect/")
MAX_WORKERS: int = env.int("MAX_WORKERS", default=1)
PROXY_URL: Optional[str] = env.str("PROXY_URL", default=None)
