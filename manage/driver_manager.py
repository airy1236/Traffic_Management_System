from .base_manager import BaseManager
from datetime import datetime
from typing import List, Dict, Optional,Any

class DriverManager(BaseManager):
    def validate_license_number(self, license_number: str) -> bool:
        """验证驾驶证号格式合法性
        Args:
            license_number: 待验证的驾驶证号
        Returns:
            符合18位数字格式返回True，否则False
        """
        return len(license_number) == 18 and license_number.isdigit()

    def update_driver(self, user_id: str, driver_id: int, data: Dict[str, Any]) -> bool:
        """更新驾驶员信息"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE drivers SET
                    name = ?,
                    license_number = ?,
                    contact_phone = ?,
                    valid_until = ?
                WHERE driver_id = ?
            """, (
                data['name'],
                data['license_number'],
                data['contact_phone'],
                data['valid_until'],
                driver_id
            ))
            conn.commit()
            conn.close()
            self.log_operation(user_id, "更新驾驶员", f"更新驾驶员ID {driver_id}")
            return True
        except Exception as e:
            self.logger.error(f"更新驾驶员失败: {str(e)}")
            raise

    def add_driver(self, user_id: str, data: Dict[str, Any]) -> int:
        """添加新驾驶员记录
        Args:
            user_id: 操作人ID（用于日志记录）
            data: 包含驾驶员信息的字典，应有以下键：
                - name: 姓名
                - license_number: 驾驶证号
                - contact_phone: 联系电话
                - valid_until: 有效期
        Returns:
            新插入记录的driver_id
        Throws:
            ValueError: 驾驶证号格式无效时抛出
        """

        try:
            if not self.validate_license_number(data['license_number']):
                raise ValueError("无效的驾驶证号")

            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO drivers (name, license_number, contact_phone, valid_until, current_score)
                VALUES (?, ?, ?, ?, 12)
            """, (data['name'], data['license_number'], 
                 data['contact_phone'], data['valid_until']))
            
            driver_id = cursor.lastrowid
            conn.commit()
            conn.close()

            self.log_operation(user_id, "添加驾驶员", f"新增驾驶员 {data['name']}")
            return driver_id

        except Exception as e:
            self.logger.error(f"添加驾驶员失败: {str(e)}")
            raise

    def update_score(self, user_id: str, driver_id: int, points_change: int) -> bool:
        """更新驾驶员积分
        Args:
            user_id: 操作人ID
            driver_id: 目标驾驶员ID
            points_change: 分数变化值（正为加分，负为扣分）
        Returns:
            更新成功返回True
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT current_score FROM drivers WHERE driver_id = ?", (driver_id,))
            current_score = cursor.fetchone()[0]
            new_score = max(0, min(12, current_score + points_change))
            
            cursor.execute("""
                UPDATE drivers SET current_score = ?
                WHERE driver_id = ?
            """, (new_score, driver_id))
            
            conn.commit()
            conn.close()

            self.log_operation(user_id, "更新积分", 
                             f"驾驶员ID {driver_id} 积分变更 {points_change}")
            return True

        except Exception as e:
            self.logger.error(f"更新驾驶员积分失败: {str(e)}")
            raise