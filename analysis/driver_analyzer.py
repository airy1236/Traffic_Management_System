from .base_analyzer import BaseAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class DriverAnalyzer(BaseAnalyzer):
    def analyze_driver_behavior(self) -> pd.DataFrame:
        """分析驾驶员行为特征"""
        try:
            query = """
                SELECT 
                    d.driver_id,
                    d.name,
                    julianday('now') - julianday(d.valid_until) as driving_years,
                    COUNT(v.violation_id) as violation_count
                FROM drivers d
                LEFT JOIN violations v ON d.driver_id = v.driver_id
                GROUP BY d.driver_id, d.name
            """
            
            df = pd.read_sql_query(query, self.get_connection())
            
            # 创建散点图
            plt.figure(figsize=(12, 8))
            sns.scatterplot(data=df, x='driving_years', y='violation_count')
            
            # 添加趋势线
            sns.regplot(data=df, x='driving_years', y='violation_count', 
                       scatter=False, color='red')
            
            plt.title('驾龄与违章次数关系分析')
            plt.xlabel('驾龄(年)')
            plt.ylabel('违章次数')
            
            # 添加注释
            correlation = df['driving_years'].corr(df['violation_count'])
            plt.annotate(f'相关系数: {correlation:.2f}', 
                        xy=(0.05, 0.95), xycoords='axes fraction')
            
            self.save_plot(plt.gcf(), 'driver_behavior.png')
            return df
            
        except Exception as e:
            self.logger.error(f"分析驾驶员行为失败: {str(e)}")
            raise