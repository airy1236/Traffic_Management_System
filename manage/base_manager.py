from typing import List, Dict, Any, Optional
from database import DatabaseManager
import logging

class BaseManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    def log_operation(self, user_id: str, action: str, detail: str):
        """记录操作日志"""
        self.db.add_log(user_id, action, detail)