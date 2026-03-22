import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PersonalizationService:
    """
    Intelligence Layer for User Personalization.
    Extracts and manages user traits and preferences to tailor AI behavior.
    """

    def __init__(self, user_repo):
        self.user_repo = user_repo

    async def learn_preference(self, user_id: str, key: str, value: Any):
        """
        Persists a learned preference (e.g., 'programming_language': 'Python').
        """
        await self.user_repo.update_preferences(user_id, key, value)

    async def get_user_context(self, user_id: str) -> str:
        """
        Constructs a behavioral context string for the LLM prompt.
        """
        profile = await self.user_repo.get_profile(user_id)
        prefs = profile.get("preferences", {})
        
        if not prefs:
            return ""
            
        context_parts = []
        for k, v in prefs.items():
            context_parts.append(f"- User {k.replace('_', ' ')}: {v}")
            
        return "\n".join(context_parts)
