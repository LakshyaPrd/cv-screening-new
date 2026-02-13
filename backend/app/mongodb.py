"""
MongoDB connection module using Motor (async driver).
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None


async def connect_mongodb():
    """Initialize MongoDB connection."""
    global _client, _db
    try:
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
        _db = _client[settings.MONGODB_DB_NAME]
        # Verify connection
        await _client.admin.command("ping")
        logger.info(f"MongoDB connected: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise


async def close_mongodb():
    """Close MongoDB connection."""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")


def get_mongodb() -> AsyncIOMotorDatabase:
    """Dependency to get MongoDB database instance."""
    if _db is None:
        raise RuntimeError("MongoDB not initialized. Call connect_mongodb() first.")
    return _db
