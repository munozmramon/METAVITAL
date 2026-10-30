from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class MetricType(str, Enum):
    GLUCOSE = "GLUCOSE"
    BLOOD_PRESSURE = "BLOOD_PRESSURE"
    WEIGHT = "WEIGHT"
    STEPS = "STEPS"


class MeasurementContext(str, Enum):
    FASTING = "FASTING"
    POSTPRANDIAL = "POSTPRANDIAL"
    RANDOM = "RANDOM"
    BEDTIME = "BEDTIME"


class CaptureMethod(str, Enum):
    OCR_CAMERA = "OCR_CAMERA"
    MANUAL = "MANUAL"
    BLUETOOTH_NATIVE = "BLUETOOTH_NATIVE"


class BiometricReadingCreate(BaseModel):
    patient_id: str
    metric_type: MetricType
    value_primary: float = Field(..., description="mg/dL or Systolic mmHg")
    value_secondary: Optional[float] = Field(None, description="Diastolic mmHg")
    value_tertiary: Optional[float] = Field(None, description="Heart rate pulse bpm")
    context: MeasurementContext
    capture_method: CaptureMethod
    timestamp: datetime


class BiometricReadingResponse(BiometricReadingCreate):
    id: str
    is_alert: bool
    created_at: datetime


class MedicationCreate(BaseModel):
    brand_name: str
    generic_name: str
    dose_mg: float
    therapeutic_class: str
    scheduled_time: str
    instructions: str
    is_active: bool = True


class AdherenceLogCreate(BaseModel):
    medication_id: str
    scheduled_time: datetime
    taken_time: Optional[datetime] = None
    status: str
    notes: Optional[str] = None


class ClinicalReportRequest(BaseModel):
    patient_id: str
    period_days: int = 30

