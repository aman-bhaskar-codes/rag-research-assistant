class ConversationRepository:
    def __init__(self, db):
        self.db = db

    async def ensure_exists(self, conversation_id: str, user_id: str):
        query = """
        INSERT INTO conversations (id, user_id)
        VALUES ($1, $2)
        ON CONFLICT (id) DO NOTHING
        """
        await self.db.execute(query, conversation_id, user_id)