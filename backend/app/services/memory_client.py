class MemoryClient:

    def __init__(self):
        # temporary in-memory store
        self.store = {}

    async def get_recent_messages(
        self,
        user_id: str,
        session_id: str,
        limit: int = 5
    ):
        """
        Returns last N messages
        """

        if not user_id or not session_id:
            return []

        key = f"{user_id}:{session_id}"

        messages = self.store.get(key, [])

        return messages[-limit:]

    async def save_interaction(
        self,
        user_id: str,
        session_id: str,
        query: str,
        response: str
    ):
        """
        Save interaction in memory
        """

        if not user_id or not session_id:
            return

        key = f"{user_id}:{session_id}"

        if key not in self.store:
            self.store[key] = []

        self.store[key].append({
            "role": "user",
            "content": query
        })

        self.store[key].append({
            "role": "assistant",
            "content": response
        })