from tortoise import Tortoise

async def init_db():
    await Tortoise.init(
        db_url="postgres://user:password@localhost:5432/monitorscape",
        modules={"models": ["src.models"]},
    )

async def close_db():
    await Tortoise.close_connections()
