import tkinter as tk
from tkinter import ttk
import datetime
from gui.frames.vehicle_frame import VehicleFrame
from gui.frames.driver_frame import DriverFrame
from gui.frames.road_frame import RoadFrame
from gui.frames.violation_frame import ViolationFrame
from gui.frames.monitor_frame import MonitorFrame
from gui.frames.analysis_frame import AnalysisFrame

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("SmartRoad 交通综合管理平台")
        self.state('zoomed')  # 最大化窗口
        self.configure(bg='#f0f0f0')
        
        self._init_ui()
        self._setup_style()
        
    def _init_ui(self):
        """初始化UI布局"""
        self._create_header()
        self._create_main_content()
        self._create_status_bar()
        
    def _setup_style(self):
        """设置主题样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置Treeview样式
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="#ffffff")
        style.map('Treeview',
                    background=[('selected', '#0078D7')])

    def _create_header(self):
        """创建头部区域"""
        header = tk.Frame(self, height=50, bg='#333333')
        header.pack(fill='x', pady=1)
        
        # 系统标题
        title = tk.Label(header, 
                        text="SmartRoad 交通综合管理平台",
                        font=('微软雅黑', 16, 'bold'),
                        fg='white',
                        bg='#333333')
        title.pack(side='left', padx=20)
        
        # 用户信息
        self.user_label = tk.Label(header,
                                    text="管理员",
                                    font=('微软雅黑', 10),
                                    fg='white',
                                    bg='#333333')
        self.user_label.pack(side='right', padx=20)
        
        # 时间显示
        self.time_label = tk.Label(header,
                                    font=('微软雅黑', 10),
                                    fg='white',
                                    bg='#333333')
        self.time_label.pack(side='right', padx=20)
        self._update_time()
        
    def _create_main_content(self):
        """创建主要内容区域"""
        # 创建左侧导航栏和主工作区的容器
        content = tk.Frame(self, bg='#f0f0f0')
        content.pack(fill='both', expand=True, pady=1)
        
        # 左侧导航菜单
        self._create_nav_menu(content)
        
        # 主工作区
        self.main_frame = ttk.Notebook(content)
        self.main_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # 初始化各功能模块
        self.frames = {
            'vehicle': VehicleFrame(self.main_frame),
            'driver': DriverFrame(self.main_frame),
            'road': RoadFrame(self.main_frame),
            'violation': ViolationFrame(self.main_frame),
            'monitor': MonitorFrame(self.main_frame),
            'analysis': AnalysisFrame(self.main_frame)
        }
        
        # 添加标签页
        self.main_frame.add(self.frames['vehicle'], text='车辆管理')
        self.main_frame.add(self.frames['driver'], text='驾驶员管理')
        self.main_frame.add(self.frames['road'], text='道路管理')
        self.main_frame.add(self.frames['violation'], text='违章处理')
        self.main_frame.add(self.frames['monitor'], text='实时监控')
        self.main_frame.add(self.frames['analysis'], text='统计分析')
        
    def _create_nav_menu(self, parent):
        """创建左侧导航菜单"""
        nav_frame = tk.Frame(parent, width=200, bg='#2c3e50')
        nav_frame.pack(side='left', fill='y', padx=1)
        nav_frame.pack_propagate(False)
        
        # 菜单项配置
        menu_items = [
            ('数据管理', [
                ('车辆管理', lambda: self.main_frame.select(0)),
                ('驾驶员管理', lambda: self.main_frame.select(1)),
                ('道路管理', lambda: self.main_frame.select(2))
            ]),
            ('违章处理', lambda: self.main_frame.select(3)),
            ('实时监控', lambda: self.main_frame.select(4)),
            ('统计分析', lambda: self.main_frame.select(5)),
            ('系统设置', None)
        ]
        
        for item in menu_items:
            if isinstance(item[1], list):  # 子菜单
                menu_btn = tk.Menubutton(nav_frame,
                                        text=item[0],
                                        font=('微软雅黑', 12),
                                        fg='white',
                                        bg='#2c3e50',
                                        activebackground='#34495e',
                                        relief='flat')
                menu_btn.pack(fill='x', pady=1)
                
                submenu = tk.Menu(menu_btn, tearoff=0)
                menu_btn.configure(menu=submenu)
                
                for sub_item in item[1]:
                    submenu.add_command(label=sub_item[0],
                                        command=sub_item[1],
                                        font=('微软雅黑', 10))
            else:  # 普通菜单项
                btn = tk.Button(nav_frame,
                                text=item[0],
                                font=('微软雅黑', 12),
                                fg='white',
                                bg='#2c3e50',
                                activebackground='#34495e',
                                relief='flat',
                                command=item[1])
                btn.pack(fill='x', pady=1)
                
    def _create_status_bar(self):
        """创建状态栏"""
        status_bar = tk.Frame(self, height=25, bg='#f0f0f0')
        status_bar.pack(fill='x', side='bottom')
        
        # 数据库状态
        self.db_status = tk.Label(status_bar,
                                text="数据库状态: 已连接",
                                font=('微软雅黑', 9),
                                bg='#f0f0f0')
        self.db_status.pack(side='left', padx=10)
        
        # 记录统计
        self.record_count = tk.Label(status_bar,
                                    text="总记录数: 0",
                                    font=('微软雅黑', 9),
                                    bg='#f0f0f0')
        self.record_count.pack(side='left', padx=10)
        
        # 版本信息
        version = tk.Label(status_bar,
                            text="v1.0.0",
                            font=('微软雅黑', 9),
                            bg='#f0f0f0')
        version.pack(side='right', padx=10)
        
    def _update_time(self):
        """更新时间显示"""
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.configure(text=current_time)
        self.after(1000, self._update_time)
        
    def update_status(self, db_status: str, record_count: int):
        """更新状态栏信息"""
        self.db_status.configure(text=f"数据库状态: {db_status}")
        self.record_count.configure(text=f"总记录数: {record_count}")