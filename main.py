from gui.main_window import MainWindow
from database import DatabaseManager
import logging

def main():
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 配置中文字体
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    try:
        # 初始化数据库
        db = DatabaseManager()
        
        # 启动GUI
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logging.error(f"程序运行错误: {e}")
        raise

if __name__ == "__main__":
    main()