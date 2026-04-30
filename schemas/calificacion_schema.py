from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List
from datetime import datetime


# ── Otros sub-structure ────────────────────────────────────────────────────────

class OtroSubField(BaseModel):
    label: str
    weight: float

class OtrosField(BaseModel):
    weight: float
    subfields: List[OtroSubField] = []


# ── Read ───────────────────────────────────────────────────────────────────────

class CalificacionRead(BaseModel):
    id: int
    interview: float
    grade_certificate: float
    motivation_letter: float
    language_certificate: float
    disability_certificate: float
    otros: Optional[OtrosField] = None
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
    otros: Optional[OtrosField] = None

    @field_validator(
        "interview", "grade_certificate", "motivation_letter",
        "language_certificate", "disability_certificate"
    )
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Todos los campos obligatorios deben ser mayor que 0")
        if v > 100:
            raise ValueError("El valor debe estar entre 0 y 100")
        return v

    @model_validator(mode="after")
    def validate_totals(self) -> "CalificacionUpdate":
        otros_weight = self.otros.weight if self.otros else 0.0

        total = (
            self.interview
            + self.grade_certificate
            + self.motivation_letter
            + self.language_certificate
            + self.disability_certificate
            + otros_weight
        )
        if abs(total - 100) > 0.01:
            raise ValueError(
                f"La suma total debe ser exactamente 100% (actual: {total:.1f}%)"
            )

        if self.otros:
            if self.otros.weight <= 0 or self.otros.weight > 100:
                raise ValueError("El peso de 'Otros' debe estar entre 0 y 100")
            sub_total = sum(sf.weight for sf in self.otros.subfields)
            if abs(sub_total - self.otros.weight) > 0.01:
                raise ValueError(
                    f"La suma de subcampos ({sub_total:.1f}%) debe ser exactamente el peso de 'Otros' ({self.otros.weight:.1f}%)"
                )

        return self
