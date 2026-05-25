from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
from database import DatabaseManager
import seaborn as sns
import logging

class BaseAnalyzer:
    def __init__(self, db: DatabaseManager):
        self.db = db
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
        plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self):
        """获取数据库连接"""
        return self.db.get_connection()
    
    def save_plot(self, fig, filename: str):
        """保存图表"""
        try:
            fig.savefig(f"reports/{filename}", dpi=300, bbox_inches='tight')
            plt.close(fig)
        except Exception as e:
            self.logger.error(f"保存图表失败: {str(e)}")
            raise