from .base_frame import BaseFrame
import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime

class MonitorFrame(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.start_monitoring()

    def _create_main_area(self):
        """创建监控主界面"""
        # 创建监控网格
        self.monitor_frame = ttk.Frame(self)
        self.monitor_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建监控点位
        self.monitors = {}
        for i in range(4):
            for j in range(3):
                monitor_dict = self._create_monitor_panel(f"监控点 {i*3 + j + 1}")
                monitor_dict['frame'].grid(row=i, column=j, padx=5, pady=5, sticky='nsew')
                self.monitors[f"monitor_{i*3 + j}"] = monitor_dict
        
        # 设置网格权重
        for i in range(4):
            self.monitor_frame.grid_rowconfigure(i, weight=1)
        for j in range(3):
            self.monitor_frame.grid_columnconfigure(j, weight=1)

    def _create_monitor_panel(self, title):
        """创建单个监控面板"""
        frame = ttk.LabelFrame(self.monitor_frame, text=title)
        
        # 模拟视频画面（使用Label显示）
        video = tk.Label(frame, bg='black', width=30, height=10)
        video.pack(fill='both', expand=True, padx=2, pady=2)
        
        # 状态信息
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill='x', padx=2, pady=2)
        
        status_var = tk.StringVar(value="状态: 正常")
        flow_var = tk.StringVar(value="流量: 0 辆/分钟")
        
        ttk.Label(info_frame, textvariable=status_var).pack(side='left', padx=2)
        ttk.Label(info_frame, textvariable=flow_var).pack(side='right', padx=2)
        
        return {
            'frame': frame,
            'video': video,
            'status_var': status_var,
            'flow_var': flow_var
        }

    def _create_detail_area(self):
        """创建监控详细信息区域"""
        super()._create_detail_area()
        
        # 添加统计信息
        self.stats_vars = {
            'total_vehicles': tk.StringVar(value="总车流量: 0"),
            'avg_speed': tk.StringVar(value="平均车速: 0 km/h"),
            'violations': tk.StringVar(value="违章数量: 0")
        }
        
        for i, (key, var) in enumerate(self.stats_vars.items()):
            ttk.Label(self.detail_frame, textvariable=var).pack(side='left', padx=20)

    def start_monitoring(self):
        """开始监控更新"""
        self._update_monitors()
        
    def _update_monitors(self):
        """更新监控数据"""
        for monitor in self.monitors.values():
            # 模拟更新流量数据
            flow = random.randint(0, 100)
            monitor['flow_var'].set(f"流量: {flow} 辆/分钟")
            
            # 模拟更新状态
            status = "正常" if random.random() > 0.1 else "警告"
            monitor['status_var'].set(f"状态: {status}")
            
            # 更新统计信息
            total = sum(random.randint(0, 100) for _ in range(12))
            self.stats_vars['total_vehicles'].set(f"总车流量: {total}")
            self.stats_vars['avg_speed'].set(f"平均车速: {random.randint(40, 80)} km/h")
            self.stats_vars['violations'].set(f"违章数量: {random.randint(0, 10)}")
        
        # 每秒更新一次
        self.after(1000, self._update_monitors)