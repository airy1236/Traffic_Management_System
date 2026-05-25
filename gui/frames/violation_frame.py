from .base_frame import BaseFrame
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from database import DatabaseManager
from datetime import datetime
from violations.violation_types import ViolationType, VIOLATION_RULES

class ViolationFrame(BaseFrame):
    def __init__(self, parent):
        self.db = DatabaseManager()
        self.fields = [
            ('车牌号:', 'license_plate'),
            ('驾驶员:', 'driver_name'),
            ('违章时间:', 'violation_time'),
            ('地点:', 'location'),
            ('违章类型:', 'violation_type'),
            ('状态:', 'status')
        ]
        super().__init__(parent)
        self._refresh_data()
        
    def _create_main_area(self):
        """创建违章列表区域"""
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('violation_id', 'license_plate', 'driver_name', 'violation_time', 
                  'location', 'violation_type', 'status')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # 设置列头
        headings = {
            'violation_id': 'ID',
            'license_plate': '车牌号',
            'driver_name': '驾驶员',
            'violation_time': '违章时间',
            'location': '地点',
            'violation_type': '违章类型',
            'status': '状态'
        }
        
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def _create_detail_area(self):
        """创建违章详细信息区域"""
        super()._create_detail_area()
        
        self.detail_vars = {}
        for i, (label, field) in enumerate(self.fields):
            ttk.Label(self.detail_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            var = tk.StringVar()
            self.detail_vars[field] = var
            
            if field == 'violation_type':
                combo = ttk.Combobox(self.detail_frame, textvariable=var,
                                    values=[vt.value for vt in ViolationType],
                                    state='readonly')
                combo.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            elif field == 'status':
                combo = ttk.Combobox(self.detail_frame, textvariable=var,
                                    values=['未处理', '已处理', '申诉中'],
                                    state='readonly')
                combo.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            else:
                ttk.Label(self.detail_frame, textvariable=var).grid(
                    row=i, column=1, padx=5, pady=5, sticky='w')

    def _on_add(self):
        """新增违章记录"""
        dialog, entries = self._create_dialog("新增违章记录", self.fields)
        
        # 设置违章类型下拉框
        violation_types = ttk.Combobox(entries['violation_type'].master,
                                        values=[vt.value for vt in ViolationType])
        violation_types.grid(row=4, column=1, padx=5, pady=5)
        entries['violation_type'] = violation_types
        
        # 设置状态下拉框
        status_combo = ttk.Combobox(entries['status'].master,
                                    values=['未处理', '已处理', '申诉中'])
        status_combo.grid(row=5, column=1, padx=5, pady=5)
        status_combo.set('未处理')
        entries['status'] = status_combo

    def _refresh_data(self):
        """刷新违章列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.violation_id, veh.license_plate, d.name,
                       v.violation_time, v.location, v.violation_type, v.status
                FROM violations v
                JOIN vehicles veh ON v.vehicle_id = veh.vehicle_id
                JOIN drivers d ON v.driver_id = d.driver_id
                ORDER BY v.violation_time DESC
            """)
            
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=tuple(row))
                
            conn.close()
            
        except Exception as e:
            self.show_message("错误", f"加载数据失败: {str(e)}", "error")

    def _on_select(self, event):
        """选择记录事件"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            self.current_id = values[0]
            self.current_violation_id = values[0]
            
            # 更新详细信息显示
            fields = ['license_plate', 'driver_name', 'violation_time', 
                     'location', 'violation_type', 'status']
            for field, value in zip(fields, values[1:]):
                if field in self.detail_vars:
                    self.detail_vars[field].set(value)

    def _on_dialog_confirm(self, dialog, entries):
        """保存违章记录"""
        try:
            data = {field: entry.get() for field, entry in entries.items()}
            
            # 验证数据
            if not all(data.values()):
                self.show_message("错误", "请填写所有字段", "error")
                return
            
            # 获取车辆ID和驾驶员ID
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 查找车辆ID
            cursor.execute("SELECT vehicle_id FROM vehicles WHERE license_plate = ?",
                         (data['license_plate'],))
            vehicle_result = cursor.fetchone()
            if not vehicle_result:
                self.show_message("错误", "未找到对应车辆", "error")
                return
            vehicle_id = vehicle_result[0]
            
            # 查找驾驶员ID
            cursor.execute("SELECT driver_id FROM drivers WHERE name = ?",
                         (data['driver_name'],))
            driver_result = cursor.fetchone()
            if not driver_result:
                self.show_message("错误", "未找到对应驾驶员", "error")
                return
            driver_id = driver_result[0]
            
            # 保存违章记录
            if hasattr(self, 'current_violation_id'):
                success = self.db.update_violation(
                    self.current_violation_id,
                    vehicle_id,
                    driver_id,
                    data['violation_time'],
                    data['location'],
                    data['violation_type'],
                    data['status']
                )
            else:
                sql = """
                    INSERT INTO violations 
                    (vehicle_id, driver_id, violation_time, location, violation_type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                params = (vehicle_id, driver_id, data['violation_time'],
                         data['location'], data['violation_type'], data['status'])
                success = self.db.execute_transaction(sql, params)
            
            dialog.destroy()
            self._refresh_data()
            self.show_message("成功", "违章记录已保存")
            
        except Exception as e:
            self.show_message("错误", str(e), "error")
        finally:
            if 'conn' in locals():
                conn.close()

    def _on_edit(self):
        """编辑违章记录"""
        if not self.current_id:
            self.show_message("提示", "请先选择一条记录", "warning")
            return
            
        dialog, entries = self._create_dialog("编辑违章记录", self.fields)
        
        # 填充现有数据
        for field, value in self.detail_vars.items():
            if field in entries:
                entries[field].insert(0, value.get())

    def _on_delete(self):
        """删除违章记录"""
        if not self.current_id:
            self.show_message("提示", "请先选择一条记录", "warning")
            return
            
        if messagebox.askyesno("确认", "确定要删除这条记录吗？"):
            try:
                self.db.execute_transaction(
                    "DELETE FROM violations WHERE violation_id = ?", 
                    (self.current_id,)
                )
                self._refresh_data()
                self.show_message("成功", "记录已删除")
            except Exception as e:
                self.show_message("错误", str(e), "error")

    def _on_search(self, event=None):
        """搜索违章记录"""
        keyword = self.search_var.get()
        if not keyword:
            self._refresh_data()
            return
            
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.violation_id, veh.license_plate, d.name,
                       v.violation_time, v.location, v.violation_type, v.status
                FROM violations v
                JOIN vehicles veh ON v.vehicle_id = veh.vehicle_id
                JOIN drivers d ON v.driver_id = d.driver_id
                WHERE veh.license_plate LIKE ? 
                   OR d.name LIKE ?
                   OR v.location LIKE ?
                ORDER BY v.violation_time DESC
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=tuple(row))
                
            conn.close()
            
        except Exception as e:
            self.show_message("错误", f"搜索失败: {str(e)}", "error")