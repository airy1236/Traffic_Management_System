from .base_frame import BaseFrame
import tkinter as tk
from tkinter import ttk,messagebox
from database import DatabaseManager
from datetime import datetime

class DriverFrame(BaseFrame):
    def __init__(self, parent):
        self.db = DatabaseManager()
        self.fields = [
            ('姓名:', 'name'),
            ('驾驶证号:', 'license_number'),
            ('联系电话:', 'contact_phone'),
            ('有效期至:', 'valid_until'),
            ('当前积分:', 'current_score')
        ]
        super().__init__(parent)
        self._refresh_data()
        
    def _create_main_area(self):
        """创建驾驶员列表区域"""
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建Treeview
        columns = ('driver_id', 'name', 'license_number', 'contact_phone', 
                  'valid_until', 'current_score')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # 设置列头
        self.tree.heading('driver_id', text='ID')
        self.tree.heading('name', text='姓名')
        self.tree.heading('license_number', text='驾驶证号')
        self.tree.heading('contact_phone', text='联系电话')
        self.tree.heading('valid_until', text='有效期至')
        self.tree.heading('current_score', text='当前积分')
        
        # 设置列宽
        self.tree.column('driver_id', width=50)
        self.tree.column('name', width=100)
        self.tree.column('license_number', width=150)
        self.tree.column('contact_phone', width=120)
        self.tree.column('valid_until', width=100)
        self.tree.column('current_score', width=80)
        
        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def _create_detail_area(self):
        """创建驾驶员详细信息区域"""
        super()._create_detail_area()
        
        self.detail_vars = {}
        for i, (label, field) in enumerate(self.fields):
            ttk.Label(self.detail_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            var = tk.StringVar()
            self.detail_vars[field] = var
            ttk.Label(self.detail_frame, textvariable=var).grid(
                row=i, column=1, padx=5, pady=5, sticky='w')

    def _on_add(self):
        """新增驾驶员"""
        dialog, entries = self._create_dialog("新增驾驶员", self.fields)

    def _on_dialog_confirm(self, dialog, entries):
        """保存驾驶员信息"""
        try:
            data = {field: entry.get() for field, entry in entries.items()}
            
            # 验证数据
            if not all(data.values()):
                self.show_message("错误", "请填写所有字段", "error")
                return
            
            # 验证驾驶证号
            if not len(data['license_number']) == 18:
                self.show_message("错误", "驾驶证号必须为18位", "error")
                return
            
            # 验证积分
            try:
                score = int(data['current_score'])
                if not 0 <= score <= 12:
                    raise ValueError("积分必须在0-12之间")
            except ValueError as e:
                self.show_message("错误", str(e), "error")
                return
            
            if 'driver_id' in data and data['driver_id']:
                sql = """
                    UPDATE drivers SET
                        name = ?,
                        license_number = ?,
                        contact_phone = ?,
                        valid_until = ?,
                        current_score = ?
                    WHERE driver_id = ?
                """
                params = (data['name'], data['license_number'], data['contact_phone'],
                         data['valid_until'], score, data['driver_id'])
            else:
                sql = """
                    INSERT INTO drivers (name, license_number, contact_phone, valid_until, current_score)
                    VALUES (?, ?, ?, ?, ?)
                """
                params = (data['name'], data['license_number'], data['contact_phone'],
                     data['valid_until'], score)
            
            self.db.execute_transaction(sql, params)
            dialog.destroy()
            self._refresh_data()
            self.show_message("成功", "驾驶员信息已保存")
            
        except Exception as e:
            self.show_message("错误", str(e), "error")

    def _refresh_data(self):
        """刷新驾驶员列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT driver_id, name, license_number, contact_phone, valid_until, current_score
                FROM drivers
                ORDER BY driver_id DESC
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
            
            fields = ['name', 'license_number', 'contact_phone', 'valid_until', 'current_score']
            for field, value in zip(fields, values[1:]):
                if field in self.detail_vars:
                    self.detail_vars[field].set(value)

    def _on_edit(self):
        """编辑驾驶员"""
        if not self.current_id:
            self.show_message("提示", "请先选择一条记录", "warning")
            return
            
        dialog, entries = self._create_dialog("编辑驾驶员", self.fields)
        
        # 填充现有数据
        entries['driver_id'] = tk.Entry(dialog)
        entries['driver_id'].insert(0, str(self.current_id))
        entries['driver_id'].grid_remove()  # 隐藏ID输入框
        for field, value in self.detail_vars.items():
            if field in entries:
                entries[field].insert(0, value.get())

    def _on_delete(self):
        """删除驾驶员"""
        if not self.current_id:
            self.show_message("提示", "请先选择一条记录", "warning")
            return
            
        if messagebox.askyesno("确认", "确定要删除这条记录吗？"):
            try:
                self.db.execute_transaction(
                    "DELETE FROM drivers WHERE driver_id = ?", 
                    (self.current_id,)
                )
                self._refresh_data()
                self.show_message("成功", "记录已删除")
            except Exception as e:
                self.show_message("错误", str(e), "error")

    def _on_search(self, event=None):
        """搜索驾驶员"""
        keyword = self.search_var.get()
        if not keyword:
            self._refresh_data()
            return
            
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT driver_id, name, license_number, contact_phone, valid_until, current_score
                FROM drivers
                WHERE name LIKE ? OR license_number LIKE ? OR contact_phone LIKE ?
                ORDER BY driver_id DESC
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=tuple(row))
                
            conn.close()
            
        except Exception as e:
            self.show_message("错误", f"搜索失败: {str(e)}", "error")