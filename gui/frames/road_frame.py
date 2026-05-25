from .base_frame import BaseFrame
import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

class RoadFrame(BaseFrame):
    def __init__(self, parent):
        self.db = DatabaseManager()
        self.fields = [
            ('道路名称:', 'road_name'),
            ('起点:', 'start_point'),
            ('终点:', 'end_point'),
            ('限速:', 'speed_limit'),
            ('状态:', 'status')
        ]
        super().__init__(parent)
        self._refresh_data()

    def _create_main_area(self):
        """创建道路列表区域"""
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建Treeview
        columns = ('road_id', 'road_name', 'start_point', 'end_point', 'speed_limit', 'status')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # 设置列头
        self.tree.heading('road_id', text='ID')
        self.tree.heading('road_name', text='道路名称')
        self.tree.heading('start_point', text='起点')
        self.tree.heading('end_point', text='终点')
        self.tree.heading('speed_limit', text='限速')
        self.tree.heading('status', text='状态')
        
        # 设置列宽
        self.tree.column('road_id', width=50)
        self.tree.column('road_name', width=150)
        self.tree.column('start_point', width=150)
        self.tree.column('end_point', width=150)
        self.tree.column('speed_limit', width=80)
        self.tree.column('status', width=80)
        
        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def _create_detail_area(self):
        """创建道路详细信息区域"""
        super()._create_detail_area()
        
        self.detail_vars = {}
        for i, (label, field) in enumerate(self.fields):
            ttk.Label(self.detail_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            var = tk.StringVar()
            self.detail_vars[field] = var
            if field == 'status':
                combo = ttk.Combobox(self.detail_frame, textvariable=var, 
                                   values=['畅通', '拥堵', '施工', '关闭'], state='readonly')
                combo.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            else:
                ttk.Label(self.detail_frame, textvariable=var).grid(
                    row=i, column=1, padx=5, pady=5, sticky='w')

    def _on_add(self):
        """新增道路"""
        dialog, entries = self._create_dialog("新增道路", self.fields)
        # 设置状态下拉框
        status_entry = ttk.Combobox(entries['status'].master, values=['畅通', '拥堵', '施工', '关闭'])
        status_entry.grid(row=4, column=1, padx=5, pady=5)
        status_entry.set('畅通')
        entries['status'] = status_entry

    def _on_select(self, event):
        """选择记录事件"""
        selection = self.tree.selection()
        if selection:
            # 获取选中的记录
            item = self.tree.item(selection[0])
            values = item['values']
            self.current_id = values[0]  # 保存当前选中的ID
            
            # 更新详细信息显示
            fields = ['road_name', 'start_point', 'end_point', 'speed_limit', 'status']
            for field, value in zip(fields, values[1:]):
                if field in self.detail_vars:
                    self.detail_vars[field].set(value)

    def _refresh_data(self):
        """刷新道路列表数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT road_id, road_name, start_point, end_point, speed_limit, status
                FROM roads
                ORDER BY road_id DESC
            """)
            
            # 填充数据
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=tuple(row))
                
            conn.close()
            
        except Exception as e:
            self.show_message("错误", f"加载数据失败: {str(e)}", "error")

    def _on_dialog_confirm(self, dialog, entries):
        """保存道路信息"""
        try:
            # 收集表单数据
            data = {field: entry.get() for field, entry in entries.items()}
            
            # 验证数据
            if not all(data.values()):
                self.show_message("错误", "请填写所有字段", "error")
                return
            
            # 验证限速值
            try:
                speed_limit = int(data['speed_limit'])
                if speed_limit <= 0:
                    raise ValueError("限速值必须大于0")
            except ValueError:
                self.show_message("错误", "限速值必须是大于0的整数", "error")
                return
                
            # 保存到数据库
            sql = """
                INSERT INTO roads (road_name, start_point, end_point, speed_limit, status)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (data['road_name'], data['start_point'], 
                     data['end_point'], speed_limit, data['status'])
            
            self.db.execute_transaction(sql, params)
            
            # 关闭对话框并刷新数据
            dialog.destroy()
            self._refresh_data()
            self.show_message("成功", "道路信息已保存")
            
        except Exception as e:
            self.show_message("错误", str(e), "error")

    def _on_edit(self):
        """编辑道路"""
        if not self.current_id:
            self.show_message("提示", "请先选择一条记录", "warning")
            return
            
        dialog, entries = self._create_dialog("编辑道路", self.fields)
        
        # 填充现有数据
        for field, value in self.detail_vars.items():
            if field in entries:
                entries[field].insert(0, value.get())
                
        # 设置状态下拉框
        status_entry = ttk.Combobox(entries['status'].master, 
                                   values=['畅通', '拥堵', '施工', '关闭'])
        status_entry.grid(row=4, column=1, padx=5, pady=5)
        status_entry.set(self.detail_vars['status'].get())
        entries['status'] = status_entry

        def on_confirm():
            """确认更新"""
            try:
                # 收集表单数据
                data = {field: entry.get() for field, entry in entries.items()}
                
                # 验证数据
                if not all(data.values()):
                    self.show_message("错误", "请填写所有字段", "error")
                    return
                
                # 验证限速值
                try:
                    speed_limit = int(data['speed_limit'])
                    if speed_limit <= 0:
                        raise ValueError("限速值必须大于0")
                except ValueError:
                    self.show_message("错误", "限速值必须是大于0的整数", "error")
                    return
                    
                # 更新数据库
                sql = """
                    UPDATE roads 
                    SET road_name = ?, start_point = ?, end_point = ?, 
                        speed_limit = ?, status = ?
                    WHERE road_id = ?
                """
                params = (data['road_name'], data['start_point'], 
                         data['end_point'], speed_limit, data['status'],
                         self.current_id)
                
                self.db.execute_transaction(sql, params)
                
                # 关闭对话框并刷新数据
                dialog.destroy()
                self._refresh_data()
                self.show_message("成功", "道路信息已更新")
                
            except Exception as e:
                self.show_message("错误", str(e), "error")
        
        # 替换对话框的确认按钮命令
        for widget in dialog.winfo_children():
            if isinstance(widget, ttk.Frame):  # 按钮框架
                for btn in widget.winfo_children():
                    if isinstance(btn, ttk.Button) and btn['text'] == "确定":
                        btn.configure(command=on_confirm)

    def _on_delete(self):
        """删除道路"""
        if not self.current_id:
            self.show_message("提示", "请先选择一条记录", "warning")
            return
            
        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除这条道路记录吗？"):
            return
            
        try:
            # 检查是否存在关联的违章记录
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM violations v 
                WHERE v.location LIKE (
                    SELECT '%' || road_name || '%' 
                    FROM roads 
                    WHERE road_id = ?
                )
            """, (self.current_id,))
            
            if cursor.fetchone()[0] > 0:
                self.show_message("错误", "该道路存在关联的违章记录，无法删除", "error")
                return
            
            # 执行删除
            self.db.execute_transaction(
                "DELETE FROM roads WHERE road_id = ?",
                (self.current_id,)
            )
            
            self._refresh_data()
            self.show_message("成功", "道路记录已删除")
            
        except Exception as e:
            self.show_message("错误", str(e), "error")
        finally:
            if 'conn' in locals():
                conn.close()

    def _on_search(self, event=None):
        """搜索道路"""
        keyword = self.search_var.get()
        if not keyword:
            self._refresh_data()
            return
            
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT road_id, road_name, start_point, end_point, speed_limit, status
                FROM roads
                WHERE road_name LIKE ? 
                   OR start_point LIKE ? 
                   OR end_point LIKE ?
                ORDER BY road_id DESC
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 填充搜索结果
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=tuple(row))
                
            conn.close()
            
        except Exception as e:
            self.show_message("错误", f"搜索失败: {str(e)}", "error")