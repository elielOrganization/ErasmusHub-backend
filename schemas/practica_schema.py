from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class ScheduleRead(BaseModel):
    id: int
    weekday: str
    morning_hours: Optional[str] = None
    afternoon_hours: Optional[str] = None

    class Config:
        from_attributes = True


class InternshipList(BaseModel):
    id: int
    company_name: str
    company_address: Optional[str] = None
    start_date: date
    end_date: date
    total_hours: int
    status: str

    class Config:
        from_attributes = True


class InternshipDetail(BaseModel):
    id: int
    # Student data
    student_first_name: str
    student_last_name: str
    student_email: str
    # Company data
    company_name: str
    company_tax_id: Optional[str] = None
    company_address: Optional[str] = None
    company_tutor_name: Optional[str] = None
    company_tutor_email: Optional[str] = None
    # Internship data
    academic_tutor_name: Optional[str] = None
    start_date: date
    end_date: date
    total_hours: int
    status: str
    # Schedule
    schedules: List[ScheduleRead] = []


class FollowUpRead(BaseModel):
    id: int
    type: str
    scheduled_date: date
    completed: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FollowUpSubmit(BaseModel):
    answers: str


class DailyLogRead(BaseModel):
    id: int
    date: date
    status: str
    morning_start: Optional[str] = None
    morning_end: Optional[str] = None
    afternoon_start: Optional[str] = None
    afternoon_end: Optional[str] = None
    incidents: Optional[str] = None

    class Config:
        from_attributes = True


class DailyLogCreate(BaseModel):
    date: date
    morning_start: Optional[str] = None
    morning_end: Optional[str] = None
    afternoon_start: Optional[str] = None
    afternoon_end: Optional[str] = None
    activities: Optional[str] = None
    incidents: Optional[str] = None


class DailyLogUpdate(BaseModel):
    status: Optional[str] = None
    morning_start: Optional[str] = None
    morning_end: Optional[str] = None
    afternoon_start: Optional[str] = None
    afternoon_end: Optional[str] = None
    activities: Optional[str] = None
    incidents: Optional[str] = None


class AttendanceRead(BaseModel):
    id: int
    date: date
    type: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class CommunicationRead(BaseModel):
    id: int
    sender_id: int
    recipient_type: str
    type: str
    subject: str
    body: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CommunicationCreate(BaseModel):
    recipient_type: str  # company_tutor, co_tutor
    type: str  # message, query, incident
    subject: str
    body: str
