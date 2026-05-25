from .frames import base_frame as BaseFrame
from tkinter import ttk
import tkinter as tk

class VehicleFrame(BaseFrame):
    def _create_main_area(self):
        """创建车辆列表区域"""
        # 创建Treeview
        columns = ('vehicle_id', 'license_plate', 'vehicle_type', 'owner', 'registration_date')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
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
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def _create_detail_area(self):
        """创建车辆详细信息区域"""
        detail_frame = ttk.LabelFrame(self, text="车辆详细信息")
        detail_frame.pack(fill='x', padx=5, pady=5)
        
        # 表单字段
        fields = [
            ('车牌号:', 'license_plate'),
            ('车辆类型:', 'vehicle_type'),
            ('所有人:', 'owner'),
            ('注册日期:', 'registration_date')
        ]
        
        # 创建表单
        self.entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(detail_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(detail_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field] = entry