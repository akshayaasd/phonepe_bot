import redis
import pickle
from typing import Any, Dict, Optional
from gnani_sdk.logging import setup_logger
from gnani_sdk.config_parser import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB_NUMBER
)

# Setup logger
logger = setup_logger("redis_utils")

class RedisDB:
    def __init__(self):
        try:
            self._redis_conn = redis.StrictRedis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB_NUMBER
            )
            # Test the connection with a ping
            if self._redis_conn.ping():
                logger.info("Successfully Connected to the Redis Database!")
            else:
                logger.error("Unable to connect to Redis Database!")
                self._redis_conn = None
        except redis.ConnectionError as e:
            logger.exception(f"Failed to connect to Redis Database: {e}")
            self._redis_conn = None
        except Exception as e:
            logger.exception(f"Error connecting to Redis Database: {e}")
            self._redis_conn = None

    def redis_get_value(self, key: str) -> Optional[str]:
        """Get string value for a key from redis.
        Args:
            key (str): Key to fetch
        Returns:
            str: Value corresponding to the key
        """
        try:
            value = self._redis_conn.get(key)
            return value.decode('utf-8') if value is not None else None
        except Exception as e:
            logger.exception(f"Unable to get value for key {key}: {e}")
            return None

    def redis_get_dict_value(self, key: str) -> Optional[Dict]:
        """Get dictionary value for a key from redis.
        Args:
            key (str): Key to fetch
        Returns:
            dict: Dictionary value corresponding to the key
        """
        try:
            value = self._redis_conn.get(key)
            return pickle.loads(value) if value is not None else None
        except Exception as e:
            logger.exception(f"Unable to get dict value for key {key}: {e}")
            return None

    def redis_set_value(self, key: str, value: str) -> Optional[bool]:
        """Set a string value for a key in redis.
        Args:
            key (str): Key to set
            value (str): Value to set
        Returns:
            bool: True if successful
        """
        try:
            return self._redis_conn.set(key, value)
        except Exception as e:
            logger.exception(f"Unable to set value for key {key}: {e}")
            return None

    def redis_set_dict_value(self, key: str, value: Dict) -> Optional[bool]:
        """Set a dictionary value for a key in redis.
        Args:
            key (str): Key to set
            value (dict): Dictionary value to set
        Returns:
            bool: True if successful
        """
        try:
            return self._redis_conn.set(key, pickle.dumps(value))
        except Exception as e:
            logger.exception(f"Unable to set dict value for key {key}: {e}")
            return None

    def redis_set_dict_value_and_expiry(self, key: str, value: Dict, expiry: int) -> Optional[bool]:
        """Set a dictionary value with expiry for a key in redis.
        Args:
            key (str): Key to set
            value (dict): Dictionary value to set
            expiry (int): Expiry time in seconds
        Returns:
            bool: True if successful
        """
        try:
            return self._redis_conn.set(key, pickle.dumps(value), ex=expiry)
        except Exception as e:
            logger.exception(f"Unable to set dict value with expiry for key {key}: {e}")
            return None

    def redis_set_value_and_expiry(self, key: str, value: str, expiry: int) -> Optional[bool]:
        """Set a string value with expiry for a key in redis.
        Args:
            key (str): Key to set
            value (str): Value to set
            expiry (int): Expiry time in seconds
        Returns:
            bool: True if successful
        """
        try:
            return self._redis_conn.set(key, value, ex=expiry)
        except Exception as e:
            logger.exception(f"Unable to set value with expiry for key {key}: {e}")
            return None

    def redis_delete_value(self, key: str) -> Optional[int]:
        """Delete a key from redis.
        Args:
            key (str): Key to delete
        Returns:
            int: 0 or 1 based on whether key was deleted
        """
        try:
            return self._redis_conn.delete(key)
        except Exception as e:
            logger.exception(f"Unable to delete key {key}: {e}")
            return None

    def redis_key_exists(self, key: str) -> bool:
        """Check if a key exists in redis.
        Args:
            key (str): Key to check
        Returns:
            bool: True if key exists
        """
        try:
            return bool(self._redis_conn.exists(key))
        except Exception as e:
            logger.exception(f"Unable to check existence of key {key}: {e}")
            return False

