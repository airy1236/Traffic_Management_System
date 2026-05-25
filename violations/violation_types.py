from enum import Enum
from dataclasses import dataclass
from typing import Dict

class ViolationType(Enum):
    SPEEDING = "超速行驶"
    WRONG_WAY = "违反禁令标志"
    ILLEGAL_PARKING = "违法停车"
    OVERLOAD = "超载"
    RUN_RED_LIGHT = "闯红灯"
    NO_LICENSE = "无证驾驶"
    DRUNK_DRIVING = "酒后驾驶"
    
@dataclass
class ViolationRule:
    points: int  # 扣分
    fine: float  # 罚款金额
    detention_days: int = 0  # 扣留天数
    
# 违章处罚规则配置
VIOLATION_RULES: Dict[ViolationType, ViolationRule] = {
    ViolationType.SPEEDING: ViolationRule(points=6, fine=200),
    ViolationType.WRONG_WAY: ViolationRule(points=3, fine=100),
    ViolationType.ILLEGAL_PARKING: ViolationRule(points=0, fine=50),
    ViolationType.OVERLOAD: ViolationRule(points=6, fine=500),
    ViolationType.RUN_RED_LIGHT: ViolationRule(points=6, fine=200),
    ViolationType.NO_LICENSE: ViolationRule(points=12, fine=1000, detention_days=15),
    ViolationType.DRUNK_DRIVING: ViolationRule(points=12, fine=2000, detention_days=30)
}