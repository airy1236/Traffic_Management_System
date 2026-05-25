from .base_manager import BaseManager
import re
from datetime import datetime
from typing import List, Dict, Optional, Any

class VehicleManager(BaseManager):
    """
    车辆信息管理类

    功能:
    - 车辆信息增删改查
    - 车牌格式验证
    - 数据库操作事务管理

    Vehicle Management Class

    Features:
    - CRUD operations for vehicle records
    - License plate validation
    - Database transaction management
    """

    def update_vehicle(self, user_id: str, vehicle_id: int, data: Dict[str, Any]) -> bool:
        """更新车辆信息"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE vehicles SET
                    license_plate = ?,
                    vehicle_type = ?,
                    owner = ?,
                    registration_date = ?
                WHERE vehicle_id = ?
            """, (
                data['license_plate'],
                data['vehicle_type'],
                data['owner'],
                data['registration_date'],
                vehicle_id
            ))
            conn.commit()
            conn.close()
            self.log_operation(user_id, "更新车辆", f"更新车辆ID {vehicle_id}")
            return True
        except Exception as e:
            self.logger.error(f"更新车辆失败: {str(e)}")
            raise

    def add_vehicle(self, user_id: str, data: Dict[str, Any]) -> int:
        """
        添加车辆记录

        参数:
        user_id (str): 操作员ID
        data (Dict): {
            'license_plate': 车牌号（需通过格式验证）,
            'vehicle_type': 车辆类型（参见数据字典）,
            'owner': 车主姓名,
            'registration_date': 注册日期（YYYY-MM-DD）
        }

        返回:
        int: 新创建记录的vehicle_id

        异常:
        ValueError: 当车牌格式无效时抛出
        SQLException: 数据库操作失败时抛出

        Add new vehicle record

        Args:
        user_id (str): Operator ID
        data (Dict): {
            'license_plate': License plate (valid format required),
            'vehicle_type': Vehicle type (see data dict),
            'owner': Owner name,
            'registration_date': Registration date (YYYY-MM-DD)
        }

        Returns:
        int: Newly created vehicle_id

        Raises:
        ValueError: On invalid license plate format
        SQLException: On database operation failure
        """
        try:
            if not self.validate_license_plate(data['license_plate']):
                raise ValueError("无效的车牌号格式")

            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vehicles (license_plate, vehicle_type, owner, registration_date)
                VALUES (?, ?, ?, ?)
            """, (data['license_plate'], data['vehicle_type'], 
                 data['owner'], data['registration_date']))
            
            vehicle_id = cursor.lastrowid
            conn.commit()
            conn.close()

            self.log_operation(user_id, "添加车辆", f"新增车辆 {data['license_plate']}")
            return vehicle_id

        except Exception as e:
            self.logger.error(f"添加车辆失败: {str(e)}")
            raise

    def get_vehicle(self, vehicle_id: int) -> Optional[Dict]:
        """获取车辆信息"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vehicle_id, license_plate, vehicle_type, owner, registration_date
                FROM vehicles WHERE vehicle_id = ?
            """, (vehicle_id,))
            
            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    "vehicle_id": result[0],
                    "license_plate": result[1],
                    "vehicle_type": result[2],
                    "owner": result[3],
                    "registration_date": result[4]
                }
            return None

        except Exception as e:
            self.logger.error(f"获取车辆信息失败: {str(e)}")
            raise

    def update_vehicle(self, user_id: str, vehicle_id: int, data: Dict[str, Any]) -> bool:
        """更新车辆信息"""
        try:
            if 'license_plate' in data and not self.validate_license_plate(data['license_plate']):
                raise ValueError("无效的车牌号格式")

            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            update_fields = []
            values = []
            for key, value in data.items():
                if key in ['license_plate', 'vehicle_type', 'owner', 'registration_date']:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            values.append(vehicle_id)
            update_sql = "UPDATE vehicles SET " + ", ".join(update_fields) + " WHERE vehicle_id = ?"
            
            cursor.execute(update_sql, values)
            conn.commit()
            conn.close()

            self.log_operation(user_id, "更新车辆", f"更新车辆ID {vehicle_id}")
            return True

        except Exception as e:
            self.logger.error(f"更新车辆信息失败: {str(e)}")
            raise

    def delete_vehicle(self, user_id: str, vehicle_id: int) -> bool:
        """删除车辆"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 检查是否存在关联的违章记录
            cursor.execute("SELECT COUNT(*) FROM violations WHERE vehicle_id = ?", (vehicle_id,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("存在关联的违章记录，无法删除")

            cursor.execute("DELETE FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
            conn.commit()
            conn.close()

            self.log_operation(user_id, "删除车辆", f"删除车辆ID {vehicle_id}")
            return True

        except Exception as e:
            self.logger.error(f"删除车辆失败: {str(e)}")
            raise

    def search_vehicles(self, criteria: Dict[str, Any]) -> List[Dict]:
        """搜索车辆"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM vehicles WHERE 1=1"
            params = []
            
            if 'license_plate' in criteria:
                query += " AND license_plate LIKE ?"
                params.append(f"%{criteria['license_plate']}%")
            
            if 'vehicle_type' in criteria:
                query += " AND vehicle_type = ?"
                params.append(criteria['vehicle_type'])
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            vehicles = []
            for row in results:
                vehicles.append({
                    "vehicle_id": row[0],
                    "license_plate": row[1],
                    "vehicle_type": row[2],
                    "owner": row[3],
                    "registration_date": row[4]
                })
            return vehicles

        except Exception as e:
            self.logger.error(f"搜索车辆失败: {str(e)}")
            raise

"""
车辆信息管理模块

包含车辆的增删改查、车牌验证等核心业务逻辑
对应数据表: vehicles (vehicle_id, license_plate, vehicle_type, owner, registration_date)

Vehicle Management Module

Handles CRUD operations and license validation for vehicles
Related DB Table: vehicles (see data_schema.md#vehicles)
"""