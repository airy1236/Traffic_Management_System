from .base_manager import BaseManager
from typing import List, Dict, Optional,Any

class RoadManager(BaseManager):
    def add_road(self, user_id: str, data: Dict[str, Any]) -> int:
        """添加道路"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO roads (road_name, start_point, end_point, speed_limit, status)
                VALUES (?, ?, ?, ?, ?)
            """, (data['road_name'], data['start_point'], 
                 data['end_point'], data['speed_limit'], '畅通'))
            
            road_id = cursor.lastrowid
            conn.commit()
            conn.close()

            self.log_operation(user_id, "添加道路", f"新增道路 {data['road_name']}")
            return road_id

        except Exception as e:
            self.logger.error(f"添加道路失败: {str(e)}")
            raise

    def update_road_status(self, user_id: str, road_id: int, status: str) -> bool:
        """更新道路状态"""
        try:
            if status not in ['畅通', '拥堵', '施工', '关闭']:
                raise ValueError("无效的道路状态")

            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE roads SET status = ?
                WHERE road_id = ?
            """, (status, road_id))
            
            conn.commit()
            conn.close()

            self.log_operation(user_id, "更新道路状态", 
                             f"道路ID {road_id} 状态更新为 {status}")
            return True

        except Exception as e:
            self.logger.error(f"更新道路状态失败: {str(e)}")
            raise