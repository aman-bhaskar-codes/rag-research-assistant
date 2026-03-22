import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Persistence Layer for User Profiles and Personalization.
    Stores traits, preferences, and adaptive behavior models.
    """

    def __init__(self, db):
        self.db = db

    async def update_preferences(self, user_id: str, key: str, value: Any):
        """
        Atomic update of user preferences JSONB.
        Merges new key-value into existing structure.
        """
        query = """
        INSERT INTO user_profiles (user_id, preferences)
        VALUES ($1, jsonb_build_object($2::text, $3::jsonb))
        ON CONFLICT (user_id)
        DO UPDATE SET preferences = 
            user_profiles.preferences || jsonb_build_object($2::text, $3::jsonb),
            updated_at = NOW()
        """
        # Ensure value is JSON strings for storage if it's not already
        import json
        json_value = json.dumps(value)
        
        await self.db.execute(query, user_id, key, json_value)
        logger.info(f"[USER REPO] Updated preference '{key}' for user {user_id}")

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves full user profile (preferences + traits).
        Decodes JSONB columns into Python dictionaries.
        """
        query = "SELECT preferences, traits FROM user_profiles WHERE user_id = $1"
        row = await self.db.fetchrow(query, user_id)
        
        if not row:
            return {"preferences": {}, "traits": {}}

        import json
        profile = dict(row)
        
        # Ensure JSONB fields are dictionaries
        for key in ["preferences", "traits"]:
            if isinstance(profile[key], str):
                profile[key] = json.loads(profile[key])
                
        return profile
