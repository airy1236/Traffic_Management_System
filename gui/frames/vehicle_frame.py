from tkinter import messagebox
from .base_frame import BaseFrame
import tkinter as tk
from tkinter import ttk
from database import DatabaseManager

class VehicleFrame(BaseFrame):
    def __init__(self, parent):
        self.db = DatabaseManager()
        self.fields = [
            ('车牌号:', 'license_plate'),
            ('车辆类型:', 'vehicle_type'),
            ('所有人:', 'owner'),
            ('注册日期:', 'registration_date')
        ]
        super().__init__(parent)
        self._refresh_data()
        
    def _create_main_area(self):
        """创建车辆列表区域"""
        # 创建Treeview和滚动条的框架
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建Treeview
        columns = ('vehicle_id', 'license_plate', 'vehicle_type', 'owner', 'registration_date')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # 设置列头
        self.tree.heading('vehicle_id', text='ID')
        self.tree.heading('license_plate', text='车牌号')
        self.tree.heading('vehicle_type', text='车辆类型')
        self.tree.heading('owner', text='所有人')
        self.tree.heading('registration_date', text='注册日期')
        
        # 设置列宽
        self.tree.column('vehicle_id', width=50)
        self.tree.column('license_plate', width=100)
        self.tree.column('vehicle_type', width=100)
        self.tree.column('owner', width=100)
        self.tree.column('registration_date', width=100)
        
        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def _on_add(self):
        """新增车辆"""
        dialog, entries = self._create_dialog("新增车辆", self.fields)

    def _on_dialog_confirm(self, dialog, entries):
        """保存车辆信息"""
        try:
            # 收集表单数据
            data = {field: entry.get() for field, entry in entries.items()}
            
            # 验证数据
            if not all(data.values()):
                self.show_message("错误", "请填写所有字段", "error")
                return
                
            # 保存到数据库
            if 'vehicle_id' in data and data['vehicle_id']:
                sql = """
                    UPDATE vehicles SET
                        license_plate = ?,
                        vehicle_type = ?,
                        owner = ?,
                        registration_date = ?
                    WHERE vehicle_id = ?
                """
                params = (data['license_plate'], data['vehicle_type'],
                         data['owner'], data['registration_date'], data['vehicle_id'])
            else:
                sql = """
                    INSERT INTO vehicles (license_plate, vehicle_type, owner, registration_date)
                    VALUES (?, ?, ?, ?)
                """
                params = (data['license_plate'], data['vehicle_type'],
                         data['owner'], data['registration_date'])
            
            self.db.execute_transaction(sql, params)
            
            # 关闭对话框并刷新数据
            dialog.destroy()
            self._refresh_data()
            self.show_message("成功", "车辆信息已保存")
            
        except Exception as e:
            self.show_message("错误", str(e), "error")

    def _refresh_data(self):
        """刷新车辆列表数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 从数据库加载数据
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vehicle_id, license_plate, vehicle_type, owner, registration_date
                FROM vehicles
                ORDER BY vehicle_id DESC
            """)
            
            # 填充数据
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=tuple(row))
                
            conn.close()
            
        except Exception as e:
            self.show_message("错误", f"加载数据失败: {str(e)}", "error")

    def _create_detail_area(self):
        """创建车辆详细信息区域"""
        super()._create_detail_area()
        
        # 创建详细信息显示框
        self.detail_vars = {}
        for i, (label, field) in enumerate(self.fields):
            ttk.Label(self.detail_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            var = tk.StringVar()
            self.detail_vars[field] = var
            ttk.Label(self.detail_frame, textvariable=var).grid(row=i, column=1, padx=5, pady=5, sticky='w')
        
    def _on_select(self, event):
        """选择记录事件"""
        selection = self.tree.selection()
        if selection:
            # 获取选中的记录
            item = self.tree.item(selection[0])
            values = item['values']
            self.current_id = values[0]  # 保存当前选中的ID
            
            # 更新详细信息显示
            fields = ['license_plate', 'vehicle_type', 'owner', 'registration_date']
            for field, value in zip(fields, values[1:]):
                if field in self.detail_vars:
                    self.detail_vars[field].set(value)

    def _on_edit(self):
        """编辑车辆"""
        if not self.current_id:
            self.show_message("提示", "请先选择一条记录", "warning")
            return
            
        dialog, entries = self._create_dialog("编辑车辆", self.fields)
        
        # 填充现有数据
        entries['vehicle_id'] = tk.Entry(dialog)
        entries['vehicle_id'].insert(0, str(self.current_id))
        entries['vehicle_id'].grid_remove()  # 隐藏ID输入框
        for field, value in self.detail_vars.items():
            if field in entries:
                entries[field].insert(0, value.get())

    def _on_delete(self):
        """删除车辆"""
        if not self.current_id:
            self.show_message("提示", "请先选择一条记录", "warning")
            return
            
        if messagebox.askyesno("确认", "确定要删除这条记录吗？"):
            try:
                self.db.execute_transaction(
                    "DELETE FROM vehicles WHERE vehicle_id = ?", 
                    (self.current_id,)
                )
                self._refresh_data()
                self.show_message("成功", "记录已删除")
            except Exception as e:
                self.show_message("错误", str(e), "error")

    def _on_search(self, event=None):
        """搜索车辆"""
        keyword = self.search_var.get()
        if not keyword:
            self._refresh_data()
            return
            
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vehicle_id, license_plate, vehicle_type, owner, registration_date
                FROM vehicles
                WHERE license_plate LIKE ? OR owner LIKE ?
                ORDER BY vehicle_id DESC
            """, (f"%{keyword}%", f"%{keyword}%"))
            
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 填充搜索结果
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=tuple(row))
                
            conn.close()
            
        except Exception as e:
            self.show_message("错误", f"搜索失败: {str(e)}", "error")