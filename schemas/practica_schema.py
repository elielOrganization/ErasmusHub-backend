from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class HorarioRead(BaseModel):
    id: int
    dia_semana: str
    horario_manana: Optional[str] = None
    horario_tarde: Optional[str] = None

    class Config:
        from_attributes = True


class PracticaList(BaseModel):
    id: int
    empresa_nombre: str
    empresa_direccion: Optional[str] = None
    fecha_inicio: date
    fecha_fin: date
    horas_totales: int
    estado: str

    class Config:
        from_attributes = True


class PracticaDetail(BaseModel):
    id: int
    # Datos alumno
    estudiante_nombre: str
    estudiante_apellidos: str
    estudiante_email: str
    # Datos empresa
    empresa_nombre: str
    empresa_cif: Optional[str] = None
    empresa_direccion: Optional[str] = None
    tutor_empresa_nombre: Optional[str] = None
    tutor_empresa_email: Optional[str] = None
    # Datos practica
    tutor_educativo_nombre: Optional[str] = None
    fecha_inicio: date
    fecha_fin: date
    horas_totales: int
    estado: str
    # Horario
    horarios: List[HorarioRead] = []


class SeguimientoRead(BaseModel):
    id: int
    tipo: str
    fecha_programada: date
    completado: bool
    fecha_completado: Optional[datetime] = None

    class Config:
        from_attributes = True


class SeguimientoSubmit(BaseModel):
    respuestas: str  # JSON string


class DiarioRead(BaseModel):
    id: int
    fecha: date
    estado: str
    hora_inicio_manana: Optional[str] = None
    hora_fin_manana: Optional[str] = None
    hora_inicio_tarde: Optional[str] = None
    hora_fin_tarde: Optional[str] = None
    incidencias: Optional[str] = None

    class Config:
        from_attributes = True


class DiarioCreate(BaseModel):
    fecha: date
    hora_inicio_manana: Optional[str] = None
    hora_fin_manana: Optional[str] = None
    hora_inicio_tarde: Optional[str] = None
    hora_fin_tarde: Optional[str] = None
    actividades: Optional[str] = None
    incidencias: Optional[str] = None


class DiarioUpdate(BaseModel):
    estado: Optional[str] = None
    hora_inicio_manana: Optional[str] = None
    hora_fin_manana: Optional[str] = None
    hora_inicio_tarde: Optional[str] = None
    hora_fin_tarde: Optional[str] = None
    actividades: Optional[str] = None
    incidencias: Optional[str] = None


class AsistenciaRead(BaseModel):
    id: int
    fecha: date
    tipo: str
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    estado: str
    notas: Optional[str] = None

    class Config:
        from_attributes = True


class ComunicacionRead(BaseModel):
    id: int
    emisor_id: int
    destinatario_tipo: str
    tipo: str
    asunto: str
    mensaje: str
    leido: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ComunicacionCreate(BaseModel):
    destinatario_tipo: str  # tutor_empresa, cotutor
    tipo: str  # mensaje, consulta, incidencia
    asunto: str
    mensaje: str
