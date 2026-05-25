from typing import Dict, List, Optional
from datetime import datetime
import logging
from database import DatabaseManager
from .violation_types import ViolationType, VIOLATION_RULES
from .evidence_manager import EvidenceManager
from manage.driver_manager import DriverManager

class ViolationProcessor:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.evidence_mgr = EvidenceManager()
        self.driver_mgr = DriverManager(db)
        self.logger = logging.getLogger(__name__)
    
    def record_violation(self, user_id: str, data: Dict) -> int:
        """记录新的违章"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 插入违章记录
            cursor.execute("""
                INSERT INTO violations 
                (vehicle_id, driver_id, violation_time, location, violation_type, status)
                VALUES (?, ?, ?, ?, ?, '未处理')
            """, (
                data['vehicle_id'],
                data['driver_id'],
                data['violation_time'],
                data['location'],
                data['violation_type']
            ))
            
            violation_id = cursor.lastrowid
            
            # 保存证据文件（如果有）
            if 'evidence_file' in data:
                self.evidence_mgr.save_evidence(violation_id, data['evidence_file'])
            
            conn.commit()
            conn.close()
            
            self.db.add_log(user_id, "记录违章", 
                           f"车辆ID {data['vehicle_id']} 在 {data['location']} 发生违章")
            return violation_id
            
        except Exception as e:
            self.logger.error(f"记录违章失败: {str(e)}")
            raise
    
    def process_violation(self, user_id: str, violation_id: int, action: str) -> bool:
        """处理违章"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 获取违章信息
            cursor.execute("""
                SELECT driver_id, violation_type, status
                FROM violations
                WHERE violation_id = ?
            """, (violation_id,))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError("违章记录不存在")
                
            driver_id, violation_type, status = result
            
            if status != '未处理':
                raise ValueError(f"违章状态({status})不允许处理")
            
            # 获取处罚规则
            rule = VIOLATION_RULES[ViolationType(violation_type)]
            
            # 扣除驾驶员分数
            if rule.points > 0:
                self.driver_mgr.update_score(user_id, driver_id, -rule.points)
            
            # 更新违章状态
            cursor.execute("""
                UPDATE violations
                SET status = ?
                WHERE violation_id = ?
            """, (action, violation_id))
            
            conn.commit()
            conn.close()
            
            self.db.add_log(user_id, "处理违章", 
                           f"违章ID {violation_id} 处理完成，状态更新为 {action}")
            return True
            
        except Exception as e:
            self.logger.error(f"处理违章失败: {str(e)}")
            raise
    
    def get_violation_details(self, violation_id: int) -> Optional[Dict]:
        """获取违章详细信息"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT v.*, 
                       veh.license_plate,
                       d.name as driver_name,
                       d.license_number
                FROM violations v
                JOIN vehicles veh ON v.vehicle_id = veh.vehicle_id
                JOIN drivers d ON v.driver_id = d.driver_id
                WHERE v.violation_id = ?
            """, (violation_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
                
            # 获取证据文件
            evidence_files = self.evidence_mgr.get_evidence_files(violation_id)
            
            # 构建详细信息
            violation_info = {
                "violation_id": result[0],
                "vehicle_id": result[1],
                "driver_id": result[2],
                "violation_time": result[3],
                "location": result[4],
                "violation_type": result[5],
                "status": result[6],
                "license_plate": result[7],
                "driver_name": result[8],
                "license_number": result[9],
                "evidence_files": evidence_files,
                "punishment_rule": VIOLATION_RULES[ViolationType(result[5])].__dict__
            }
            
            return violation_info
            
        except Exception as e:
            self.logger.error(f"获取违章详情失败: {str(e)}")
            raise
    
    def search_violations(self, criteria: Dict) -> List[Dict]:
        """搜索违章记录"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT v.*, veh.license_plate, d.name
                FROM violations v
                JOIN vehicles veh ON v.vehicle_id = veh.vehicle_id
                JOIN drivers d ON v.driver_id = d.driver_id
                WHERE 1=1
            """
            params = []
            
            if 'license_plate' in criteria:
                query += " AND veh.license_plate LIKE ?"
                params.append(f"%{criteria['license_plate']}%")
            
            if 'driver_name' in criteria:
                query += " AND d.name LIKE ?"
                params.append(f"%{criteria['driver_name']}%")
            
            if 'start_date' in criteria:
                query += " AND v.violation_time >= ?"
                params.append(criteria['start_date'])
            
            if 'end_date' in criteria:
                query += " AND v.violation_time <= ?"
                params.append(criteria['end_date'])
            
            if 'status' in criteria:
                query += " AND v.status = ?"
                params.append(criteria['status'])
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            violations = []
            for row in results:
                violations.append({
                    "violation_id": row[0],
                    "vehicle_id": row[1],
                    "driver_id": row[2],
                    "violation_time": row[3],
                    "location": row[4],
                    "violation_type": row[5],
                    "status": row[6],
                    "license_plate": row[7],
                    "driver_name": row[8]
                })
            
            return violations
            
        except Exception as e:
            self.logger.error(f"搜索违章记录失败: {str(e)}")
            raise