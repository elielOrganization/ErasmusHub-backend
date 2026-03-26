from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import datetime


class CalificacionRead(BaseModel):
    id: int
    interview: float
    grade_certificate: float
    motivation_letter: float
    language_certificate: float
    disability_certificate: float
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class CalificacionUpdate(BaseModel):
    interview: float
    grade_certificate: float
    motivation_letter: float
    language_certificate: float
    disability_certificate: float

    @field_validator(
        "interview", "grade_certificate", "motivation_letter",
        "language_certificate", "disability_certificate"
    )
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Todos los campos son obligatorios y deben ser mayor que 0")
        if v > 100:
            raise ValueError("El valor debe estar entre 0 y 100")
        return v

    @model_validator(mode="after")
    def total_must_be_100(self) -> "CalificacionUpdate":
        total = (
            self.interview
            + self.grade_certificate
            + self.motivation_letter
            + self.language_certificate
            + self.disability_certificate
        )
        if abs(total - 100) > 0.01:
            raise ValueError(f"La suma total debe ser exactamente 100% (actual: {total:.1f}%)")
        return self
