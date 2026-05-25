from .base_analyzer import BaseAnalyzer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense # type: ignore

class TrafficAnalyzer(BaseAnalyzer):
    def predict_congestion(self, road_id: int, hours: int = 2) -> pd.DataFrame:
        """预测未来2小时拥堵概率"""
        try:
            # 获取历史数据
            query = """
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', violation_time) as hour,
                    COUNT(*) as violation_count
                FROM violations
                WHERE location IN (
                    SELECT road_name FROM roads WHERE road_id = ?
                )
                GROUP BY hour
                ORDER BY hour
            """
            
            df = pd.read_sql_query(query, self.get_connection(), params=(road_id,))
            
            # 数据预处理
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(df['violation_count'].values.reshape(-1, 1))
            
            # 准备LSTM数据
            X, y = [], []
            for i in range(len(scaled_data) - hours):
                X.append(scaled_data[i:i+hours])
                y.append(scaled_data[i+hours])
            X, y = np.array(X), np.array(y)
            
            # 训练模型
            model = Sequential([
                LSTM(50, activation='relu', input_shape=(hours, 1)),
                Dense(1)
            ])
            model.compile(optimizer='adam', loss='mse')
            model.fit(X, y, epochs=100, batch_size=32, verbose=0)
            
            # 预测未来hours小时
            last_data = scaled_data[-hours:]
            predictions = []
            
            for _ in range(hours):
                next_pred = model.predict(last_data.reshape(1, hours, 1))
                predictions.append(next_pred[0, 0])
                last_data = np.roll(last_data, -1)
                last_data[-1] = next_pred
            
            # 绘制预测结果
            plt.figure(figsize=(12, 6))
            plt.plot(df.index[-24:], df['violation_count'].values[-24:], 
                    label='历史数据')
            
            future_index = pd.date_range(
                start=df.index[-1], 
                periods=hours+1, 
                freq='H'
            )[1:]
            
            plt.plot(future_index, 
                    scaler.inverse_transform(np.array(predictions).reshape(-1, 1)), 
                    label='预测数据', linestyle='--')
            
            plt.title('交通流量预测')
            plt.xlabel('时间')
            plt.ylabel('拥堵指数')
            plt.legend()
            plt.grid(True)
            
            self.save_plot(plt.gcf(), f'traffic_prediction_{road_id}.png')
            
            # 返回预测结果
            return pd.DataFrame({
                'time': future_index,
                'congestion_probability': predictions
            })
            
        except Exception as e:
            self.logger.error(f"预测交通流量失败: {str(e)}")
            raise