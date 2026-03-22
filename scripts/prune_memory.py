import asyncio
import logging
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from memory.config.db import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prune_memory")


async def prune_memory():
    """
    Production Memory Lifecycle Script.
    Archives low-value, old, or inactive memories to keep RAG search sharp.
    """
    db = get_db()
    
    logger.info("Starting memory pruning cycle...")
    
    # Strategy: Archive memories with low importance scoring AND low usage
    query = """
    UPDATE memory_entries
    SET is_archived = TRUE
    WHERE 
        is_archived = FALSE
        AND importance_score < 0.3
        AND access_count < 2
        AND created_at < NOW() - INTERVAL '30 days'
    """
    
    try:
        await db.execute(query)
        logger.info("Successfully archived stale memories.")
    except Exception as e:
        logger.error(f"Failed to prune memory: {e}")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(prune_memory())
