import environs

env = environs.Env()

RABBITMQ_CONNECTION_URI: str = env("RABBITMQ_CONNECTION_URI")
