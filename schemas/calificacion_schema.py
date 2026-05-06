from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List
from datetime import datetime


# ── Others sub-structure ───────────────────────────────────────────────────────

class OtherSubField(BaseModel):
    label: str
    weight: float

class OthersField(BaseModel):
    weight: float
    subfields: List[OtherSubField] = []


# ── Read ───────────────────────────────────────────────────────────────────────

class CalificacionRead(BaseModel):
    id: int
    interview: float
    grade_certificate: float
    motivation_letter: float
    language_certificate: float
    disability_certificate: float
    others: Optional[OthersField] = None
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# ── Update ─────────────────────────────────────────────────────────────────────

class CalificacionUpdate(BaseModel):
    interview: float
    grade_certificate: float
    motivation_letter: float
    language_certificate: float
    disability_certificate: float
    others: Optional[OthersField] = None

    @field_validator(
        "interview", "grade_certificate", "motivation_letter",
        "language_certificate", "disability_certificate"
    )
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("All required fields must be greater than 0")
        if v > 100:
            raise ValueError("Value must be between 0 and 100")
        return v

    @model_validator(mode="after")
    def validate_totals(self) -> "CalificacionUpdate":
        others_weight = self.others.weight if self.others else 0.0

        total = (
            self.interview
            + self.grade_certificate
            + self.motivation_letter
            + self.language_certificate
            + self.disability_certificate
            + others_weight
        )
        if abs(total - 100) > 0.01:
            raise ValueError(
                f"Total must be exactly 100% (current: {total:.1f}%)"
            )

        if self.others:
            if self.others.weight <= 0 or self.others.weight > 100:
                raise ValueError("'Others' weight must be between 0 and 100")
            sub_total = sum(sf.weight for sf in self.others.subfields)
            if abs(sub_total - self.others.weight) > 0.01:
                raise ValueError(
                    f"Subfield weights sum ({sub_total:.1f}%) must equal the 'Others' weight ({self.others.weight:.1f}%)"
                )

        return self
