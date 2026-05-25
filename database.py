import sqlite3
import threading
from typing import Dict, List, Any
import logging

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = "transport.db"):
        if not hasattr(self, 'initialized'):
            self.db_path = db_path
            self._lock = threading.Lock()
            self.logger = logging.getLogger(__name__)
            self.init_database()
            self.initialized = True
    
    def get_connection(self):
        """
        获取数据库连接对象
        
        返回:
            sqlite3.Connection: 数据库连接实例
        
        异常:
            sqlite3.Error: 数据库连接失败时抛出异常
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            self.logger.error(f"获取数据库连接失败: {e}")
            raise

    def init_database(self):
        """
        初始化数据库表结构和索引
        包含以下表：
        - 车辆(vehicles)
        - 驾驶员(drivers) 
        - 道路(roads)
        - 违章(violations)
        - 交通设备(traffic_devices)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            """
            创建车辆信息表
            Fields:
            - vehicle_id: 自增主键
            - license_plate: 唯一车牌号
            - vehicle_type: 车辆类型枚举（客车/货车/特种车辆/其他）
            - owner: 车辆所有人
            - registration_date: 注册日期
            
            Constraints:
            - 车牌号唯一约束
            - 车辆类型检查约束
            """
            # 创建vehicles表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate TEXT UNIQUE NOT NULL,
                vehicle_type TEXT CHECK(vehicle_type IN ('客车','货车','特种车辆','其他')),
                owner TEXT NOT NULL,
                registration_date DATE NOT NULL
            )
            """)

            """
            创建驾驶员信息表
            Fields:
            - driver_id: 自增主键 
            - license_number: 唯一驾驶证号 
            - valid_until: 有效期 
            - current_score: 当前积分（0-12）
            
            Constraints:
            - 驾驶证号唯一约束
            - 积分范围检查
            - 默认12分
            """
            # 创建drivers表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS drivers (
                driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                license_number TEXT UNIQUE NOT NULL,
                contact_phone TEXT,
                valid_until DATE NOT NULL,
                current_score INTEGER DEFAULT 12 CHECK(current_score >= 0 AND current_score <= 12)
            )
            """)

            """
            创建道路信息表
            Fields:
            - road_id: 自增主键
            - speed_limit: 限速值
            - status: 道路状态枚举 
            
            Constraints:
            - 状态枚举检查（畅通/拥堵/施工/关闭）
            - 起终点非空约束
            """
            # 创建roads表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS roads (
                road_id INTEGER PRIMARY KEY AUTOINCREMENT,
                road_name TEXT NOT NULL,
                start_point TEXT NOT NULL,
                end_point TEXT NOT NULL,
                speed_limit INTEGER NOT NULL,
                status TEXT CHECK(status IN ('畅通','拥堵','施工','关闭'))
            )
            """)

            """
            创建违章记录表
            Fields:
            - violation_time: 违章时间
            - location: 违章地点
            - violation_type: 违章类型
            - status: 处理状态（未处理/已处理/申诉中）
            
            Foreign Keys:
            - 关联车辆表(vehicle_id) 
            - 关联驾驶员表(driver_id)
            
            Indexes:
            - 违章时间索引(idx_violation_time) 
            - 违章地点索引(idx_violation_location) 
            """
            # 创建violations表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations (
                violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                driver_id INTEGER,
                violation_time DATETIME NOT NULL,
                location TEXT NOT NULL,
                violation_type TEXT NOT NULL,
                status TEXT CHECK(status IN ('未处理','已处理','申诉中')),
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
                FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
            )
            """)

            """
            创建交通设备表
            Fields:
            - device_type: 设备类型枚举（摄像头/信号灯/测速仪/电子牌）
            - installation_date: 安装日期
            - status: 设备状态（正常/故障/维修中/离线）
            
            Indexes:
            - 设备位置索引(idx_device_location) 
            
            Related Tables:
            - 维护记录表(maintenance_records) 
            """
            # 创建traffic_devices表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_devices (
                device_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_type TEXT CHECK(device_type IN ('摄像头','信号灯','测速仪','电子牌')),
                location TEXT NOT NULL,
                installation_date DATE NOT NULL,
                status TEXT CHECK(status IN ('正常','故障','维修中','离线'))
            )
            """)

            # 创建maintenance_records表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER REFERENCES traffic_devices(device_id),
                maintenance_date DATE NOT NULL,
                operation_type TEXT CHECK(operation_type IN ('日常维护','故障维修','零件更换')),
                cost REAL,
                FOREIGN KEY (device_id) REFERENCES traffic_devices(device_id)
            )
            """)

            # 创建operation_logs表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT NOT NULL,
                detail TEXT
            )
            """)

            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_violation_time ON violations(violation_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_location ON traffic_devices(location)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_violation_location ON violations(location)")

            conn.commit()
            conn.close()
            logging.info("Database initialized successfully")

        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            raise

    def add_log(self, user_id: str, action_type: str, detail: str):
        """添加操作日志"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO operation_logs (user_id, action_type, detail)
                VALUES (?, ?, ?)
            """, (user_id, action_type, detail))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logging.error(f"Log addition error: {e}")
            raise

    def backup_database(self, backup_path: str):
        """数据库备份"""
        try:
            conn = self.get_connection()
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
            conn.close()
            logging.info(f"Database backed up successfully to {backup_path}")
        except sqlite3.Error as e:
            logging.error(f"Database backup error: {e}")
            raise

    def execute_transaction(self, sql: str, params: tuple = None) -> Any:
        """执行事务"""
        with self._lock:
            conn = None
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                result = cursor.lastrowid
                conn.commit()
                return result
            except sqlite3.Error as e:
                if conn:
                    conn.rollback()
                self.logger.error(f"执行事务失败: {e}")
                raise
            finally:
                if conn:
                    conn.close()
                    
    def get_violation_stats(self, time_range: str) -> dict:
        """获取违章统计数据
        
        Args:
            time_range: 时间范围('day', 'week', 'month', 'year')
            
        Returns:
            包含违章统计数据的字典
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 根据时间范围构建SQL查询条件
            if time_range == 'day':
                time_condition = "date(violation_time) = date('now')"
            elif time_range == 'week':
                time_condition = "date(violation_time) >= date('now', 'weekday 0', '-7 days')"
            elif time_range == 'month':
                time_condition = "strftime('%Y-%m', violation_time) = strftime('%Y-%m', 'now')"
            elif time_range == 'year':
                time_condition = "strftime('%Y', violation_time) = strftime('%Y', 'now')"
            else:
                time_condition = "1=1"  # 默认查询所有
                
            # 查询违章类型统计
            cursor.execute(f"""
                SELECT violation_type, COUNT(*) as count
                FROM violations
                WHERE {time_condition}
                GROUP BY violation_type
                ORDER BY count DESC
            """)
            
            violation_stats = {}
            for row in cursor.fetchall():
                violation_stats[row['violation_type']] = row['count']
                
            # 查询违章总数
            cursor.execute(f"""
                SELECT COUNT(*) as total
                FROM violations
                WHERE {time_condition}
            """)
            
            violation_stats['total'] = cursor.fetchone()['total']
            
            conn.close()
            return violation_stats
            
        except sqlite3.Error as e:
            self.logger.error(f"获取违章统计数据失败: {e}")
            raise
            
    def get_traffic_stats(self, time_range: str) -> dict:
        """获取交通流量统计数据
        
        Args:
            time_range: 时间范围('day', 'week', 'month', 'year')
            
        Returns:
            包含交通流量统计数据的字典
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 根据时间范围构建SQL查询条件
            if time_range == 'day':
                time_condition = "date(violation_time) = date('now')"
            elif time_range == 'week':
                time_condition = "date(violation_time) >= date('now', 'weekday 0', '-7 days')"
            elif time_range == 'month':
                time_condition = "strftime('%Y-%m', violation_time) = strftime('%Y-%m', 'now')"
            elif time_range == 'year':
                time_condition = "strftime('%Y', violation_time) = strftime('%Y', 'now')"
            else:
                time_condition = "1=1"  # 默认查询所有
                
            # 查询交通流量统计
            cursor.execute(f"""
                SELECT location, COUNT(*) as count
                FROM violations
                WHERE {time_condition}
                GROUP BY location
                ORDER BY count DESC
            """)
            
            traffic_stats = {}
            for row in cursor.fetchall():
                traffic_stats[row['location']] = row['count']
                
            # 查询总流量
            cursor.execute(f"""
                SELECT COUNT(*) as total
                FROM violations
                WHERE {time_condition}
            """)
            
            traffic_stats['total'] = cursor.fetchone()['total']
            
            conn.close()
            return traffic_stats
            
        except sqlite3.Error as e:
            self.logger.error(f"获取交通流量统计数据失败: {e}")
            raise
            
    def get_device_stats(self, time_range: str) -> dict:
        """获取设备状态统计数据
        
        Args:
            time_range: 时间范围('day', 'week', 'month', 'year')
            
        Returns:
            包含设备状态统计数据的字典
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 根据时间范围构建SQL查询条件
            if time_range == 'day':
                time_condition = "date(installation_date) = date('now')"
            elif time_range == 'week':
                time_condition = "date(installation_date) >= date('now', 'weekday 0', '-7 days')"
            elif time_range == 'month':
                time_condition = "strftime('%Y-%m', installation_date) = strftime('%Y-%m', 'now')"
            elif time_range == 'year':
                time_condition = "strftime('%Y', installation_date) = strftime('%Y', 'now')"
            else:
                time_condition = "1=1"  # 默认查询所有
                
            # 查询设备类型统计
            cursor.execute(f"""
                SELECT device_type, COUNT(*) as count
                FROM traffic_devices
                WHERE {time_condition}
                GROUP BY device_type
                ORDER BY count DESC
            """)
            
            device_stats = {}
            for row in cursor.fetchall():
                device_stats[row['device_type']] = row['count']
                
            # 查询设备状态统计
            cursor.execute(f"""
                SELECT status, COUNT(*) as count
                FROM traffic_devices
                WHERE {time_condition}
                GROUP BY status
                ORDER BY count DESC
            """)
            
            status_stats = {}
            for row in cursor.fetchall():
                status_stats[row['status']] = row['count']
                
            # 查询总设备数
            cursor.execute(f"""
                SELECT COUNT(*) as total
                FROM traffic_devices
                WHERE {time_condition}
            """)
            
            device_stats['total'] = cursor.fetchone()['total']
            device_stats['status'] = status_stats
            
            conn.close()
            return device_stats
            
        except sqlite3.Error as e:
            self.logger.error(f"获取设备状态统计数据失败: {e}")
            raise

    def update_violation(self, violation_id, vehicle_id, driver_id, violation_time, location, violation_type, status):
        """
        更新违章记录
        :param violation_id: 要更新的违章记录ID
        其他参数同add_violation
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE violations 
                SET vehicle_id=?, driver_id=?, violation_time=?, location=?, violation_type=?, status=?
                WHERE violation_id=?""",
                (vehicle_id, driver_id, violation_time, location, violation_type, status, violation_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logging.error(f"更新违章记录失败: {e}")
            return False
        finally:
            conn.close()

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 初始化数据库
    db = DatabaseManager()
    logging.info("Database system initialized and ready")