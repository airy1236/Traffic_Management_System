import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class BaseFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
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
        ttk.Button(toolbar, text="新增").pack(side='left', padx=2)
        ttk.Button(toolbar, text="编辑").pack(side='left', padx=2)
        ttk.Button(toolbar, text="删除").pack(side='left', padx=2)
        ttk.Button(toolbar, text="刷新").pack(side='left', padx=2)
        
        # 搜索框
        ttk.Entry(toolbar).pack(side='right', padx=2)
        ttk.Label(toolbar, text="搜索:").pack(side='right', padx=2)
        
    def _create_main_area(self):
        """创建主数据区"""
        # 在子类中实现具体内容
        pass
        
    def _create_detail_area(self):
        """创建详细信息区"""
        # 在子类中实现具体内容
        pass
        
    def show_message(self, title: str, message: str, message_type: str = 'info'):
        """显示消息框"""
        if message_type == 'error':
            messagebox.showerror(title, message)
        elif message_type == 'warning':
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)