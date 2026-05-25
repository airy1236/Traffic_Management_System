from .base_frame import BaseFrame
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from database import DatabaseManager
import os

class AnalysisFrame(BaseFrame):
    def __init__(self, parent):
        self.db = DatabaseManager()
        super().__init__(parent)
        self._create_charts()

    def _create_main_area(self):
        """创建分析主界面"""
        # 创建选项卡
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建各个分析页面
        self.violations_tab = ttk.Frame(self.notebook)
        self.traffic_tab = ttk.Frame(self.notebook)
        self.devices_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.violations_tab, text='违章分析')
        self.notebook.add(self.traffic_tab, text='交通流量')
        self.notebook.add(self.devices_tab, text='设备状态')

    def _create_detail_area(self):
        """创建分析详细信息区域"""
        super()._create_detail_area()
        
        # 添加分析控制按钮
        ttk.Button(self.detail_frame, text="更新数据", 
                  command=self._update_analysis).pack(side='left', padx=5)
        ttk.Button(self.detail_frame, text="导出报告", 
                  command=self._export_report).pack(side='left', padx=5)
        
        # 时间范围选择
        ttk.Label(self.detail_frame, text="时间范围:").pack(side='left', padx=5)
        self.time_range = ttk.Combobox(self.detail_frame, 
                                      values=['今日', '本周', '本月', '本年'],
                                      state='readonly')
        self.time_range.set('今日')
        self.time_range.pack(side='left', padx=5)
        self.time_range.bind('<<ComboboxSelected>>', lambda e: self._update_analysis())

    def _create_charts(self):
        """创建图表"""
        # 违章分析图表
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        canvas1 = FigureCanvasTkAgg(fig1, master=self.violations_tab)
        canvas1.get_tk_widget().pack(fill='both', expand=True)
        
        # 交通流量图表
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        canvas2 = FigureCanvasTkAgg(fig2, master=self.traffic_tab)
        canvas2.get_tk_widget().pack(fill='both', expand=True)
        
        # 设备状态图表
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        canvas3 = FigureCanvasTkAgg(fig3, master=self.devices_tab)
        canvas3.get_tk_widget().pack(fill='both', expand=True)
        
        self.figures = {
            'violations': (fig1, ax1),
            'traffic': (fig2, ax2),
            'devices': (fig3, ax3)
        }
        
        self._update_analysis()

    def _update_analysis(self):
        """更新分析数据"""
        # 更新违章分析
        fig, ax = self.figures['violations']
        ax.clear()
        violations = self.db.get_violation_stats(self.time_range.get())
        pd.DataFrame(violations, index=[0]).plot(kind='bar', ax=ax)
        ax.set_title('违章分布图')
        ax.set_xlabel('状态（未处理、已处理、申诉中）')
        ax.set_ylabel('数量')
        fig.canvas.draw()
        
        # 更新交通流量
        fig, ax = self.figures['traffic']
        ax.clear()
        traffic = self.db.get_traffic_stats(self.time_range.get())
        pd.DataFrame(traffic, index=[0]).plot(kind='line', ax=ax)
        ax.set_title('交通流量')
        ax.set_xlabel('时间')
        ax.set_ylabel('流量')
        fig.canvas.draw()
        
        # 更新设备状态
        fig, ax = self.figures['devices']
        ax.clear()
        devices = self.db.get_device_stats(self.time_range.get())
        pd.DataFrame(devices).plot(kind='pie', ax=ax, autopct='%1.1f%%', y='status')
        ax.set_title('设备状态分布')
        ax.set_xlabel('状态（正常、异常）')
        ax.set_ylabel('数量')
        fig.canvas.draw()

    def _export_report(self):
        """导出分析报告"""
        try:
            # 获取并转换数据
            time_range = self.time_range.get()
            os.makedirs('reports', exist_ok=True)
            
            # 转换查询结果为DataFrame
            # 转换并验证数据结构
            violations_data = self.db.get_violation_stats(time_range)
            if not isinstance(violations_data, dict):
                violations_data = violations_data.__dict__
            traffic_data = self.db.get_traffic_stats(time_range)
            devices_data = self.db.get_device_stats(time_range)

            violations = pd.DataFrame([violations_data], columns=violations_data.keys())
            traffic = pd.DataFrame([traffic_data], columns=traffic_data.keys())
            devices = pd.DataFrame([devices_data], columns=devices_data.keys())
            
            # 带路径的导出
            filename = os.path.join('reports', f'交通分析报告_{time_range}.xlsx')
            with pd.ExcelWriter(filename) as writer:
                violations.to_excel(writer, sheet_name='违章统计', index=False)
                traffic.to_excel(writer, sheet_name='交通流量', index=False)
                devices.to_excel(writer, sheet_name='设备状态', index=False)
                
                # 自动打开文件资源管理器
                if os.name == 'nt':
                    os.startfile(os.path.abspath('reports'))
                
            self.show_message("成功", f"报告已导出为: 交通分析报告_{time_range}.xlsx")
        except pd.errors.EmptyDataError:
            self.show_message("错误", "无有效数据可供导出")
        except PermissionError:
            self.show_message("错误", "文件被占用，请关闭Excel后重试")
        except Exception as e:
            self.show_message("错误", f"导出失败：{str(e)}")


plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题