from .base_manager import BaseManager
from datetime import datetime
from typing import List, Dict, Optional, Any

class DeviceManager(BaseManager):
    def add_device(self, user_id: str, data: Dict[str, Any]) -> int:
        """添加设备"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO traffic_devices (device_type, location, installation_date, status)
                VALUES (?, ?, ?, '正常')
            """, (data['device_type'], data['location'], data['installation_date']))
            
            device_id = cursor.lastrowid
            conn.commit()
            conn.close()

            self.log_operation(user_id, "添加设备", 
                             f"新增{data['device_type']}设备于{data['location']}")
            return device_id

        except Exception as e:
            self.logger.error(f"添加设备失败: {str(e)}")
            raise

    class DeviceManager(BaseManager):
        """
        交通设备管理类
    
        功能:
        - 设备信息维护
        - 设备状态监控
        - 维护记录管理
    
        Traffic Device Management Class
    
        Features:
        - Device maintenance operations
        - Device status monitoring
        - Maintenance records management
        """
    
        def record_maintenance(self, user_id: str, data: Dict[str, Any]) -> int:
            """
            记录设备维护信息
    
            参数:
            user_id (str): 操作员ID
            data (Dict): {
                'device_id': 设备ID,
                'operation_type': 维护类型（维修/更换/校准）,
                'cost': 维护成本
            }
    
            返回:
            int: 新创建的维护记录ID
    
            异常:
            ValueError: 当维护类型无效时抛出
            SQLException: 数据库操作失败时抛出
    
            Record device maintenance information
    
            Args:
            user_id (str): Operator ID
            data (Dict): {
                'device_id': Device ID,
                'operation_type': Maintenance type (repair/replace/calibrate),
                'cost': Maintenance cost
            }
    
            Returns:
            int: New maintenance record ID
    
            Raises:
            ValueError: On invalid maintenance type
            SQLException: On database operation failure
            """
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO maintenance_records 
                    (device_id, maintenance_date, operation_type, cost)
                    VALUES (?, ?, ?, ?)
                """, (data['device_id'], datetime.now().date(), 
                     data['operation_type'], data['cost']))
                
                record_id = cursor.lastrowid
                conn.commit()
                conn.close()
    
                self.log_operation(user_id, "设备维护", 
                             f"设备ID {data['device_id']} 进行{data['operation_type']}")
                return record_id
    
            except Exception as e:
                self.logger.error(f"记录设备维护失败: {str(e)}")
                raise