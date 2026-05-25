from .base_analyzer import BaseAnalyzer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class DeviceAnalyzer(BaseAnalyzer):
    def analyze_device_performance(self) -> pd.DataFrame:
        """分析设备效能指标"""
        try:
            # 获取设备故障率数据
            query_failure = """
                SELECT 
                    d.device_type,
                    COUNT(CASE WHEN d.status = '故障' THEN 1 END) * 100.0 / COUNT(*) as failure_rate,
                    AVG(CASE 
                        WHEN m.operation_type = '故障维修' 
                        THEN julianday(m.maintenance_date) - julianday(d.installation_date)
                    END) as avg_response_time
                FROM traffic_devices d
                LEFT JOIN maintenance_records m ON d.device_id = m.device_id
                GROUP BY d.device_type
            """
            
            df = pd.read_sql_query(query_failure, self.get_connection())
            
            # 创建雷达图
            categories = df['device_type'].tolist()
            failure_rates = df['failure_rate'].tolist()
            response_times = df['avg_response_time'].tolist()
            
            # 设置雷达图的角度
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
            
            # 闭合雷达图
            failure_rates += failure_rates[:1]
            response_times += response_times[:1]
            angles = np.concatenate((angles, [angles[0]]))
            
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            # 绘制故障率
            ax.plot(angles, failure_rates, 'o-', linewidth=2, label='故障率(%)')
            ax.fill(angles, failure_rates, alpha=0.25)
            
            # 绘制响应时间
            ax.plot(angles, response_times, 'o-', linewidth=2, label='平均响应时间(天)')
            ax.fill(angles, response_times, alpha=0.25)
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            plt.title('设备效能分析')
            plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
            
            self.save_plot(plt.gcf(), 'device_performance.png')
            return df
            
        except Exception as e:
            self.logger.error(f"分析设备效能失败: {str(e)}")
            raise