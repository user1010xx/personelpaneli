from .user import User
from .personnel import Personnel
from .sales import SalesData
from .attendance import AttendanceData
from .warning import WarningData
from .training import TrainingData
from .call_monitoring import CallMonitoring
from .whatsapp import WhatsAppData
from ..database import Base

__all__ = [
    "User",
    "Personnel",
    "SalesData",
    "AttendanceData",
    "WarningData",
    "TrainingData",
    "CallMonitoring",
    "WhatsAppData",
    "Base",
]
