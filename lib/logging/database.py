import logging
import pymongo
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MongoLogger:
    _instance = None
    _client = None
    _db = None

    @classmethod
    def initialize(
        cls,
        connection_string: str = "mongodb://localhost:27017/",
        db_name: str = "catan",
    ) -> "MongoLogger":
        if not cls._instance:
            cls._instance = cls()
            try:
                cls._client = pymongo.MongoClient(connection_string)
                cls._db = cls._client[db_name]
                logger.info("MongoDB connection established")
            except Exception as e:
                logger.error(f"Could not connect to MongoDB: {e}")
                cls._client = None
                cls._db = None
        return cls._instance

    @classmethod
    def log(cls, collection_name: str, data: Dict[str, Any]) -> None:
        if cls._db is None:
            logger.error(f"MongoDB not connected. Falling back to logging only: {data}")
            return

        try:
            collection = cls._db[collection_name]
            log_entry = {"timestamp": datetime.now(), **data}

            collection.insert_one(log_entry)

        except Exception as e:
            logger.error(f"Failed to log to MongoDB: {e}")


# Example usage in the original code would become:
"""
MongoLogger.initialize()
for action in actions:
    MongoLogger.log("action_logs", {
        "player_id": self.player.id,
        "action_type": str(action.action_type),
        "cost": action.cost,
        "reward": action.reward,
        "priority": action.priority,
        "player_state": self.get_state()
    })
"""
