from sqlmodel import SQLModel, Field


class OpportunityTeacher(SQLModel, table=True):
    __tablename__ = "opportunity_teacher"

    opportunity_id: int = Field(foreign_key="opportunity.id", primary_key=True)
    teacher_id: int = Field(foreign_key="user.id", primary_key=True)
