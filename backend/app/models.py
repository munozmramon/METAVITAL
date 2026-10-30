from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    medical_record_hash = Column(String(64), unique=True, nullable=False)
    birth_date = Column(String(10), nullable=False)
    gender = Column(String(10), nullable=False)
    height_cm = Column(Float, nullable=False)
    baseline_weight_kg = Column(Float, nullable=False)
    target_glucose_min = Column(Integer, default=70)
    target_glucose_max = Column(Integer, default=130)
    target_systolic_max = Column(Integer, default=130)
    target_diastolic_max = Column(Integer, default=80)
    created_at = Column(DateTime, default=datetime.utcnow)

    biometrics = relationship("BiometricRecord", back_populates="patient")
    medications = relationship("MedicationModel", back_populates="patient")


class BiometricRecord(Base):
    __tablename__ = "biometric_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    metric_type = Column(String(20), nullable=False)
    value_primary = Column(Float, nullable=False)
    value_secondary = Column(Float, nullable=True)
    value_tertiary = Column(Float, nullable=True)
    measurement_context = Column(String(20), nullable=False)
    capture_method = Column(String(20), nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    is_alert = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="biometrics")


class MedicationModel(Base):
    __tablename__ = "medications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    commercial_name = Column(String(100), nullable=False)
    active_ingredient = Column(String(100), nullable=False)
    dose_mg = Column(Float, nullable=False)
    therapeutic_class = Column(String(50), nullable=False)
    scheduled_time = Column(String(8), nullable=False)
    instructions = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    patient = relationship("Patient", back_populates="medications")
    adherences = relationship("AdherenceRecord", back_populates="medication")


class AdherenceRecord(Base):
    __tablename__ = "adherence_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    medication_id = Column(String(36), ForeignKey("medications.id"), nullable=False)
    scheduled_timestamp = Column(DateTime, nullable=False)
    taken_timestamp = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)
    notes = Column(String(255), nullable=True)

    medication = relationship("MedicationModel", back_populates="adherences")

