import os
import shutil
from datetime import datetime
from typing import List, Optional
import logging

class EvidenceManager:
    def __init__(self, evidence_dir: str = "evidence"):
        self.evidence_dir = evidence_dir
        self.logger = logging.getLogger(__name__)
        self._ensure_evidence_dir()
    
    def _ensure_evidence_dir(self):
        """确保证据存储目录存在"""
        os.makedirs(self.evidence_dir, exist_ok=True)
    
    def save_evidence(self, violation_id: int, file_path: str) -> str:
        """保存违章证据"""
        try:
            # 创建违章专属目录
            violation_dir = os.path.join(self.evidence_dir, str(violation_id))
            os.makedirs(violation_dir, exist_ok=True)
            
            # 生成目标文件名
            file_ext = os.path.splitext(file_path)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_name = f"evidence_{timestamp}{file_ext}"
            target_path = os.path.join(violation_dir, target_name)
            
            # 复制文件
            shutil.copy2(file_path, target_path)
            return target_path
            
        except Exception as e:
            self.logger.error(f"保存证据失败: {str(e)}")
            raise
    
    def get_evidence_files(self, violation_id: int) -> List[str]:
        """获取违章的所有证据文件"""
        violation_dir = os.path.join(self.evidence_dir, str(violation_id))
        if not os.path.exists(violation_dir):
            return []
        
        return [os.path.join(violation_dir, f) for f in os.listdir(violation_dir)]