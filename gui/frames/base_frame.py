import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class BaseFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.current_id = None  # 当前选中的记录ID
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI组件"""
        # 工具栏
        self._create_toolbar()
        
        # 主数据区
        self._create_main_area()
        
        # 详细信息区
        self._create_detail_area()
        
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # 通用按钮
        ttk.Button(toolbar, text="新增", command=self._on_add).pack(side='left', padx=2)
        ttk.Button(toolbar, text="编辑", command=self._on_edit).pack(side='left', padx=2)
        ttk.Button(toolbar, text="删除", command=self._on_delete).pack(side='left', padx=2)
        ttk.Button(toolbar, text="刷新", command=self._on_refresh).pack(side='left', padx=2)
        
        # 搜索框
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var)
        self.search_entry.pack(side='right', padx=2)
        self.search_entry.bind('<Return>', self._on_search)
        ttk.Label(toolbar, text="搜索:").pack(side='right', padx=2)

    def _create_dialog(self, title: str, fields: list):
        """创建数据编辑对话框"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.transient(self)  # 设置为主窗口的临时窗口
        dialog.grab_set()  # 模态窗口
        
        # 创建表单
        entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[field] = entry
            
        # 按钮区域
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="确定", 
                  command=lambda: self._on_dialog_confirm(dialog, entries)
                  ).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="取消", 
                  command=dialog.destroy
                  ).pack(side='left', padx=5)
        
        return dialog, entries

    def _on_dialog_confirm(self, dialog, entries):
        """对话框确认按钮事件"""
        # 在子类中实现具体的保存逻辑
        pass

    def _on_add(self):
        """新增按钮事件"""
        # 在子类中实现具体的新增逻辑
        pass

    def _on_edit(self):
        """编辑按钮事件"""
        if not self.current_id:
            self.show_message("提示", "请先选择一条记录", "warning")
            return
        # 在子类中实现具体的编辑逻辑

    def _on_delete(self):
        """删除按钮事件"""
        if not self.current_id:
            self.show_message("提示", "请先选择一条记录", "warning")
            return
        # 在子类中实现具体的删除逻辑

    def _on_refresh(self):
        """刷新按钮事件"""
        # 在子类中实现具体的刷新逻辑
        pass

    def _on_search(self, event=None):
        """搜索事件"""
        # 在子类中实现具体的搜索逻辑
        pass

    def show_message(self, title: str, message: str, message_type: str = 'info'):
        """显示消息框"""
        if message_type == 'error':
            messagebox.showerror(title, message)
        elif message_type == 'warning':
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
    
    def _create_detail_area(self):
        """创建详细信息区域"""
        self.detail_frame = ttk.LabelFrame(self, text="详细信息")
        self.detail_frame.pack(fill='x', padx=5, pady=5)