from tortoise import fields
from tortoise.models import Model
from uuid import uuid4


class User(Model):
    id: int = fields.IntField(pk=True)

    user_id: int = fields.IntField(required=True)
    usages: int = fields.IntField(default=3)


class Token(Model):
    id: int = fields.IntField(pk=True)

    token = fields.UUIDField(default=uuid4)
    usages = fields.IntField(default=10)
