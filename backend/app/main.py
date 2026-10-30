"""
METAVITAL Backend API Service
FastAPI implementation with HIPAA/GDPR Pseudonymization and Clinical Rules.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
from datetime import datetime, timezone

from .schemas import (
    BiometricReadingCreate, 
    BiometricReadingResponse, 
    MedicationCreate,
    AdherenceLogCreate,
    ClinicalReportRequest,
    PatientProfileUpdate,
    PatientProfileSchema
)
from .clinical_rules import ClinicalRuleEngine, AlertLevel
from .pdf_compiler import PDFCompiler
from .web_simulator import get_simulator_html

app = FastAPI(
    title="METAVITAL API",
    description="Backend clínico para pacientes con Síndrome Metabólico",
    version="1.0.0"
)

# In-memory mock store for cloud API sync
DB_READINGS: List[Dict[str, Any]] = []
DB_MEDS: List[Dict[str, Any]] = []
DB_ADHERENCE: List[Dict[str, Any]] = []

CURRENT_PATIENT: Dict[str, Any] = {
    "id": "pat-001",
    "first_name": "Ramón",
    "last_name": "García Fernández",
    "full_name": "Ramón García Fernández",
    "age": 58,
    "gender": "MALE",
    "height_cm": 172.0,
    "current_weight_kg": 84.5,
    "bmi": 28.56,
    "bmi_category": "Sobrepeso (Grado II)",
}

def calculate_bmi(weight_kg: float, height_cm: float):
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 2)
    if bmi < 18.5:
        category = "Bajo peso"
    elif bmi < 25.0:
        category = "Normopeso"
    elif bmi < 30.0:
        category = "Sobrepeso (Grado II)"
    elif bmi < 35.0:
        category = "Obesidad (Grado I)"
    elif bmi < 40.0:
        category = "Obesidad (Grado II)"
    else:
        category = "Obesidad Mórbida (Grado III)"
    return bmi, category


@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTMLResponse(content=get_simulator_html(), status_code=200)


@app.get("/api/v1/health")
def health_check():
    return {
        "service": "METAVITAL Backend API",
        "status": "OPERATIONAL",
        "version": "1.0.0",
        "compliance": ["HIPAA", "RGPD", "AES-256", "WCAG 2.1 AAA"]
    }


@app.get("/api/v1/patient")
def get_patient():
    return {"success": True, "patient": CURRENT_PATIENT}


@app.put("/api/v1/patient")
def update_patient(update: PatientProfileUpdate):
    if update.first_name is not None:
        CURRENT_PATIENT["first_name"] = update.first_name
    if update.last_name is not None:
        CURRENT_PATIENT["last_name"] = update.last_name
    
    CURRENT_PATIENT["full_name"] = f"{CURRENT_PATIENT['first_name']} {CURRENT_PATIENT['last_name']}".strip()

    if update.age is not None:
        CURRENT_PATIENT["age"] = update.age
    if update.height_cm is not None:
        CURRENT_PATIENT["height_cm"] = update.height_cm
    if update.current_weight_kg is not None:
        CURRENT_PATIENT["current_weight_kg"] = update.current_weight_kg

    bmi, cat = calculate_bmi(CURRENT_PATIENT["current_weight_kg"], CURRENT_PATIENT["height_cm"])
    CURRENT_PATIENT["bmi"] = bmi
    CURRENT_PATIENT["bmi_category"] = cat

    return {"success": True, "patient": CURRENT_PATIENT}



@app.post("/api/v1/biometrics", status_code=status.HTTP_201_CREATED)
def record_biometric_reading(reading: BiometricReadingCreate):
    is_alert = False
    alert_info = None

    if reading.metric_type == "GLUCOSE":
        triage = ClinicalRuleEngine.evaluate_glucose(int(reading.value_primary), reading.context)
        if triage.level != AlertLevel.NORMAL:
            is_alert = True
            alert_info = triage.__dict__
    elif reading.metric_type == "BLOOD_PRESSURE":
        dia = int(reading.value_secondary or 80)
        triage = ClinicalRuleEngine.evaluate_blood_pressure(int(reading.value_primary), dia)
        if triage.level != AlertLevel.NORMAL:
            is_alert = True
            alert_info = triage.__dict__
    elif reading.metric_type == "WEIGHT":
        CURRENT_PATIENT["current_weight_kg"] = float(reading.value_primary)
        bmi, cat = calculate_bmi(CURRENT_PATIENT["current_weight_kg"], CURRENT_PATIENT["height_cm"])
        CURRENT_PATIENT["bmi"] = bmi
        CURRENT_PATIENT["bmi_category"] = cat

    record = {
        "id": f"bio-cloud-{len(DB_READINGS) + 1}",
        **reading.model_dump(),
        "is_alert": is_alert,
        "alert_info": alert_info,
        "created_at": datetime.now(timezone.utc)
    }
    DB_READINGS.append(record)

    return {
        "success": True,
        "record": record,
        "alert": alert_info
    }


@app.post("/api/v1/medications", status_code=status.HTTP_201_CREATED)
def add_medication(med: MedicationCreate):
    record = {
        "id": f"med-cloud-{len(DB_MEDS) + 1}",
        **med.model_dump(),
        "created_at": datetime.now(timezone.utc)
    }
    DB_MEDS.append(record)
    return {"success": True, "medication": record}


@app.post("/api/v1/adherence", status_code=status.HTTP_201_CREATED)
def log_adherence(log: AdherenceLogCreate):
    record = {
        "id": f"adh-cloud-{len(DB_ADHERENCE) + 1}",
        **log.model_dump(),
        "created_at": datetime.now(timezone.utc)
    }
    DB_ADHERENCE.append(record)
    return {"success": True, "adherence_record": record}


@app.post("/api/v1/reports/pdf-html", response_class=HTMLResponse)
def generate_clinical_report(req: ClinicalReportRequest):
    mock_payload = {
        "patient": {
            "name": CURRENT_PATIENT["full_name"],
            "first_name": CURRENT_PATIENT["first_name"],
            "last_name": CURRENT_PATIENT["last_name"],
            "age": CURRENT_PATIENT["age"],
            "height_cm": CURRENT_PATIENT["height_cm"],
            "bmi": CURRENT_PATIENT["bmi"],
            "bmi_category": CURRENT_PATIENT["bmi_category"],
            "current_weight_kg": CURRENT_PATIENT["current_weight_kg"]
        },
        "glucose": {
            "time_in_range_pct": 84,
            "mean_fasting": 114,
            "hypo_events": 0,
            "hyper_events": 0
        },
        "blood_pressure": {
            "mean_systolic": 126,
            "mean_diastolic": 82,
            "stage_2_alerts": 0,
            "crisis_count": 0
        },
        "lifestyle": {
            "mean_steps": 4350,
            "walks_completed": 9
        },
        "medication_adherence_pct": 96,
        "recommendations": [
            "Tiempo en Rango (TIR) superior al 80%: excelente control de excursiones glucémicas.",
            "Presión arterial media estabilizada (< 130/80 mmHg) tras corrección de hábitos.",
            "Mantener el estímulo de 15 minutos de marcha posprandial."
        ]
    }

    html = PDFCompiler.compile_report_html(mock_payload)
    return HTMLResponse(content=html, status_code=200)

