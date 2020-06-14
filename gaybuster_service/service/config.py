import environs

env = environs.Env()

RABBITMQ_CONNECTION_URI: str = env("RABBITMQ_CONNECTION_URI")
N_WORKERS: int = env.int("N_WORKERS")
GENDER_REP = {0: "gay", 1: "straight"}
