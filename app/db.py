from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

# Example: create indexes at startup
async def create_indexes():
    await db.users.create_index("email", unique=True)
    await db.policies.create_index([("owner_id", 1)])
    await db.claims.create_index([("policy_id", 1)])
