# 开发编码规范

## 数据库操作规范
1. 必须使用上下文管理器进行会话管理
```python
with Session() as session:
    session.add(new_vehicle)
    session.commit()
```

## 界面组件命名
- 采用`类型_模块_功能`格式
- 示例：
  - tree_vehicle_list（车辆列表树形组件）
  - btn_driver_search（驾驶员搜索按钮）

## 多线程编程
1. 必须实现资源释放逻辑
```python
def device_monitor():
    try:
        while running:
            # 监控逻辑
    finally: 
        close_serial_port()
        release_memory()
```

## 版本控制
- 数据库变更必须提交迁移脚本
- 界面修改需附带屏幕截图