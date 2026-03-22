class MessageRepository:
    def __init__(self, db):
        self.db = db

    async def get_recent_messages(self, conversation_id: str, limit: int):
        query = """
        SELECT role, content
        FROM messages
        WHERE conversation_id = $1
        ORDER BY created_at DESC
        LIMIT $2
        """
        rows = await self.db.fetch(query, conversation_id, limit)

        # return in chronological order
        return list(reversed([dict(r) for r in rows]))

    async def insert_message(self, conversation_id: str, role: str, content: str, metadata=None):
        query = """
        INSERT INTO messages (conversation_id, role, content, metadata)
        VALUES ($1, $2, $3, $4)
        """
        await self.db.execute(query, conversation_id, role, content, metadata)