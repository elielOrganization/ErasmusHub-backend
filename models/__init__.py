from .user import User
from .role import Role
from .user_role import UserRole
from .opportunity import Opportunity
from .application import Application
from .document import Document
from .application_document import ApplicationDocument
from .task import Task
from .notification import Notification
from .internship import Internship
from .weekly_schedule import WeeklySchedule
from .follow_up import FollowUp
from .daily_log import DailyLog
from .attendance import Attendance
from .communication import Communication
from .exemption import Exemption
from .selection_process import SelectionProcess
from .chat import Chat, ChatMessage
from .opportunity_teacher import OpportunityTeacher
__all__ = [
    "User",
    "Role",
    "UserRole",
    "Opportunity",
    "Application",
    "Document",
    "ApplicationDocument",
    "Task",
    "Notification",
    "Internship",
    "WeeklySchedule",
    "FollowUp",
    "DailyLog",
    "Attendance",
    "Communication",
    "Exemption",
    "SelectionProcess",
    "Chat",
    "ChatMessage",
    "OpportunityTeacher",
]
