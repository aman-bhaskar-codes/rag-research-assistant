import os
import asyncpg
import logging
from typing import List, Optional, Any

logger = logging.getLogger(__name__)


class Database:
    """
    Asynchronous connection pool for PostgreSQL.
    """
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        if not self._pool:
            try:
                self._pool = await asyncpg.create_pool(self.dsn)
                logger.info("Connected to PostgreSQL pool.")
            except Exception as e:
                logger.error(f"Failed to create Postgres pool: {e}")
                raise

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        if not self._pool:
            await self.connect()
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        if not self._pool:
            await self.connect()
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query: str, *args):
        if not self._pool:
            await self.connect()
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def close(self):
        if self._pool:
            await self._pool.close()
            logger.info("PostgreSQL pool closed.")


# Singleton instance for the memory layer
_db: Optional[Database] = None


def get_db() -> Database:
    global _db
    if _db is None:
        # Resolve root .env path
        from dotenv import load_dotenv
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        load_dotenv(os.path.join(root_dir, ".env"))

        dsn = os.getenv("DATABASE_URL")
        
        # If DSN is clearly a placeholder or missing, try common dev defaults
        if not dsn or "user:password" in dsn:
            # Try current user on localhost
            import getpass
            user = getpass.getuser()
            dsn = f"postgresql://{user}@localhost:5432/rag_assistant"
            logger.info(f"Using default dev DSN: {dsn}")
        
        # 🔥 asyncpg doesn't like 'postgresql+asyncpg://'
        if dsn and "+asyncpg" in dsn:
            dsn = dsn.replace("+asyncpg", "")
            
        _db = Database(dsn)
    return _db
