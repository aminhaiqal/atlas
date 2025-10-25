import os
from tortoise import Tortoise
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")


async def init_db():
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["src.models"]},
    )


async def close_db():
    await Tortoise.close_connections()
