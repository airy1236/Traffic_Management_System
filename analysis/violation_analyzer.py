from .base_analyzer import BaseAnalyzer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

class ViolationAnalyzer(BaseAnalyzer):
    def analyze_top_violations(self, limit: int = 5) -> pd.DataFrame:
        """分析各路段违章类型分布TOP5"""
        try:
            query = """
                SELECT 
                    r.road_name,
                    v.violation_type,
                    COUNT(*) as violation_count
                FROM violations v
                JOIN roads r ON v.location LIKE '%' || r.road_name || '%'
                GROUP BY r.road_name, v.violation_type
                ORDER BY violation_count DESC
                LIMIT ?
            """
            
            df = pd.read_sql_query(query, self.get_connection(), params=(limit,))
            
            # 创建三维柱状图
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            roads = df['road_name'].unique()
            types = df['violation_type'].unique()
            x_pos = range(len(roads))
            y_pos = range(len(types))
            
            X, Y = np.meshgrid(x_pos, y_pos)
            Z = df.pivot(index='violation_type', columns='road_name', 
                        values='violation_count').values
            
            ax.bar3d(X.ravel(), Y.ravel(), np.zeros_like(Z.ravel()),
                    1, 1, Z.ravel(), alpha=0.8)
            
            ax.set_xticks(x_pos)
            ax.set_yticks(y_pos)
            ax.set_xticklabels(roads, rotation=45)
            ax.set_yticklabels(types)
            ax.set_xlabel('道路名称')
            ax.set_ylabel('违章类型')
            ax.set_zlabel('违章次数')
            plt.title('各路段违章类型分布TOP5')
            
            self.save_plot(plt.gcf(), 'violations_distribution.png')
            return df
            
        except Exception as e:
            self.logger.error(f"分析违章分布失败: {str(e)}")
            raise