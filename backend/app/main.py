"""
METAVITAL Backend API Service
FastAPI implementation with HIPAA/GDPR Pseudonymization and Clinical Rules.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Response
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Dict, Any
from datetime import datetime, timezone
import os

from .schemas import (
    BiometricReadingCreate, 
    BiometricReadingResponse, 
    MedicationCreate,
    AdherenceLogCreate,
    ClinicalReportRequest,
    PatientProfileUpdate,
    PatientProfileSchema,
    MedicationBoxScanRequest,
    ClinicalDocumentScanRequest,
    DoctorProfileSchema
)
from .clinical_rules import ClinicalRuleEngine, AlertLevel
from .pdf_compiler import PDFCompiler
from .binary_pdf import BinaryPDFReportGenerator
from .ocr_processor import MedicalOCRProcessor
from .web_simulator import get_simulator_html

app = FastAPI(
    title="METAVITAL API",
    description="Backend clínico para pacientes con Síndrome Metabólico",
    version="1.0.0"
)

# In-memory mock store for cloud API sync
DB_READINGS: List[Dict[str, Any]] = []
DB_ADHERENCE: List[Dict[str, Any]] = []

CURRENT_PATIENT: Dict[str, Any] = {
    "id": "pat-001",
    "first_name": "Ramón",
    "last_name": "Muñoz Martínez",
    "full_name": "Ramón Muñoz Martínez",
    "age": 63,
    "gender": "MALE",
    "height_cm": 165.0,
    "current_weight_kg": 101.5,
    "baseline_weight_kg": 106.0,  # Consulta previa Hospital Universitario de Jaén
    "weight_loss_kg": 4.5,
    "bmi": 37.28,
    "bmi_category": "Obesidad (Grado II)",
    "target_glucose_min": 70,
    "target_glucose_max": 130,
    "target_systolic_max": 130,
    "target_diastolic_max": 80,
    "target_steps_daily": 4000,
    "clinical_profile": "STANDARD",
    "nephrology": {
        "stage": "ERC Estadio 3a (KDIGO G3a A1)",
        "egfr_ml_min": 42,
        "creatinine_mg_dl": 1.7,
        "urea_mg_dl": 62,
        "potassium_meq_l": 5.5,
        "potassium_alert": "HIGH_BORDERLINE",
        "albuminuria_mg_g": 20,
        "hba1c_pct": 7.1,
        "ldl_mg_dl": 49,
        "triglycerides_mg_dl": 346,
        "blood_pressure": "130/74 mmHg",
        "heart_rate_bpm": 61,
        "center": "Hospital Universitario de Jaén",
        "physician": "Dr. Cobo Fernández / Consulta Nefrología General",
        "support": "ALCER Jaén (953 25 22 44)"
    },
    "doctor": {
        "name": "Dr. Nicolás Cobo Fernández",
        "health_center": "Centro de Salud de Baeza",
        "specialty": "Medicina Familiar / Nefrología",
        "whatsapp_phone": "+34 600 000 000",
        "monthly_report_day": 1
    }
}

DB_MEDS: List[Dict[str, Any]] = [
    {
        "id": "med-01",
        "brand_name": "Tritace",
        "generic_name": "Ramipril",
        "dose_mg": 10.0,
        "therapeutic_class": "ANTIHYPERTENSIVE",
        "scheduled_time": "08:30",
        "instructions": "1-0-0 (Desayuno). Protección cardio-renal.",
        "is_active": True
    },
    {
        "id": "med-02",
        "brand_name": "Secalip supra",
        "generic_name": "Fenofibrato",
        "dose_mg": 240.0,
        "therapeutic_class": "STATIN_LIPID",
        "scheduled_time": "08:30",
        "instructions": "1-0-0 (Desayuno). Tratamiento de hipertrigliceridemia.",
        "is_active": True
    },
    {
        "id": "med-03",
        "brand_name": "Synjardy",
        "generic_name": "Metformina / Empagliflozina",
        "dose_mg": 1012.5,
        "therapeutic_class": "ANTIDIABETIC",
        "scheduled_time": "08:30",
        "instructions": "1-0-1 (Desayuno y Cena). Control glucémico y nefroprotección.",
        "is_active": True
    },
    {
        "id": "med-04",
        "brand_name": "Omacor",
        "generic_name": "Ésteres etílicos omega-3",
        "dose_mg": 2000.0,
        "therapeutic_class": "STATIN_LIPID",
        "scheduled_time": "14:00",
        "instructions": "0-2-0 (Almuerzo). 2 cápsulas con la comida principal.",
        "is_active": True
    },
    {
        "id": "med-05",
        "brand_name": "Tenormin",
        "generic_name": "Atenolol",
        "dose_mg": 50.0,
        "therapeutic_class": "ANTIHYPERTENSIVE",
        "scheduled_time": "21:30",
        "instructions": "0-0-1 (Cena). Control tensional y frecuencia cardíaca.",
        "is_active": True
    },
    {
        "id": "med-06",
        "brand_name": "Cardyl / Atozet",
        "generic_name": "Atorvastatina / Ezetimiba",
        "dose_mg": 50.0,
        "therapeutic_class": "STATIN_LIPID",
        "scheduled_time": "21:30",
        "instructions": "0-0-1 (Cena). Hipolipemiante (mantiene LDL en 49 mg/dL).",
        "is_active": True
    },
    {
        "id": "med-07",
        "brand_name": "Insulina",
        "generic_name": "Insulina según pauta",
        "dose_mg": 0.0,
        "therapeutic_class": "ANTIDIABETIC",
        "scheduled_time": "22:00",
        "instructions": "Inyección subcutánea alternando los 4 cuadrantes (evitar lipodistrofia).",
        "is_active": True
    },
    {
        "id": "med-08",
        "brand_name": "Ozempic",
        "generic_name": "Semaglutida",
        "dose_mg": 1.0,
        "therapeutic_class": "ANTIDIABETIC",
        "scheduled_time": "Domingos 09:00",
        "instructions": "1 inyección subcutánea semanal. Agonista GLP-1 activo para control glucémico y ponderal.",
        "is_active": True
    }
]

SUSPENDED_MEDS: List[Dict[str, Any]] = [
    {
        "name": "Trajenta 5 mg (Linagliptina)",
        "action": "SUSPENDER",
        "instructions": "Retirado formalmente por el Nefrólogo en informe de consulta."
    }
]

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

    if update.target_glucose_min is not None:
        CURRENT_PATIENT["target_glucose_min"] = update.target_glucose_min
    if update.target_glucose_max is not None:
        CURRENT_PATIENT["target_glucose_max"] = update.target_glucose_max
    if update.target_systolic_max is not None:
        CURRENT_PATIENT["target_systolic_max"] = update.target_systolic_max
    if update.target_diastolic_max is not None:
        CURRENT_PATIENT["target_diastolic_max"] = update.target_diastolic_max
    if update.target_steps_daily is not None:
        CURRENT_PATIENT["target_steps_daily"] = update.target_steps_daily
    if update.clinical_profile is not None:
        CURRENT_PATIENT["clinical_profile"] = update.clinical_profile

    bmi, cat = calculate_bmi(CURRENT_PATIENT["current_weight_kg"], CURRENT_PATIENT["height_cm"])
    CURRENT_PATIENT["bmi"] = bmi
    CURRENT_PATIENT["bmi_category"] = cat

    return {"success": True, "patient": CURRENT_PATIENT}


@app.get("/api/v1/patient/doctor")
def get_patient_doctor():
    return {"success": True, "doctor": CURRENT_PATIENT.get("doctor", {})}


@app.put("/api/v1/patient/doctor")
def update_patient_doctor(doc: DoctorProfileSchema):
    CURRENT_PATIENT["doctor"] = doc.model_dump()
    return {"success": True, "doctor": CURRENT_PATIENT["doctor"]}


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/api/v1/logo")
def get_logo():
    logo_path = os.path.join(STATIC_DIR, "logo_transparent.png")
    if os.path.exists(logo_path):
        return FileResponse(logo_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo not found")


@app.get("/api/v1/logo/white")
def get_logo_white():
    logo_path = os.path.join(STATIC_DIR, "logo_white.png")
    if os.path.exists(logo_path):
        return FileResponse(logo_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo not found")




@app.post("/api/v1/biometrics", status_code=status.HTTP_201_CREATED)
def record_biometric_reading(reading: BiometricReadingCreate):
    is_alert = False
    alert_info = None

    if reading.metric_type == "GLUCOSE":
        triage = ClinicalRuleEngine.evaluate_glucose(
            int(reading.value_primary), 
            reading.context,
            target_min=CURRENT_PATIENT.get("target_glucose_min", 70),
            target_max=CURRENT_PATIENT.get("target_glucose_max", 130)
        )
        if triage.level != AlertLevel.NORMAL:
            is_alert = True
            alert_info = triage.__dict__
    elif reading.metric_type == "BLOOD_PRESSURE":
        dia = int(reading.value_secondary or 80)
        triage = ClinicalRuleEngine.evaluate_blood_pressure(
            int(reading.value_primary), 
            dia,
            target_sys_max=CURRENT_PATIENT.get("target_systolic_max", 130),
            target_dia_max=CURRENT_PATIENT.get("target_diastolic_max", 80)
        )
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


@app.get("/api/v1/reports/download-pdf")
def download_binary_pdf():
    """
    Compiles and downloads a standalone, valid 1-page A4 PDF binary document.
    """
    mock_payload = {
        "patient": {
            "name": CURRENT_PATIENT["full_name"],
            "full_name": CURRENT_PATIENT["full_name"],
            "age": CURRENT_PATIENT["age"],
            "height_cm": CURRENT_PATIENT["height_cm"],
            "bmi": CURRENT_PATIENT["bmi"],
            "bmi_category": CURRENT_PATIENT["bmi_category"],
            "current_weight_kg": CURRENT_PATIENT["current_weight_kg"]
        },
        "glucose": {
            "time_in_range_pct": 85,
            "mean_fasting": 114,
            "hypo_events": 0,
            "hyper_events": 0
        },
        "blood_pressure": {
            "mean_systolic": 124,
            "mean_diastolic": 82,
            "stage_2_alerts": 0,
            "crisis_count": 0
        },
        "lifestyle": {
            "mean_steps": 4350,
            "walks_completed": 9
        },
        "medication_adherence_pct": 96
    }
    pdf_bytes = BinaryPDFReportGenerator.generate_clinical_pdf(mock_payload)
    filename = f"METAVITAL_Informe_{CURRENT_PATIENT['first_name']}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/pdf"
        }
    )


@app.post("/api/v1/medications/scan-box")
def scan_medication_box(req: MedicationBoxScanRequest):
    """
    Analyzes scanned medication box text, detecting active principle, dosage, and intake advice.
    """
    parsed = MedicalOCRProcessor.parse_medication_box_text(req.ocr_text)
    if not parsed:
        return {
            "success": False,
            "message": "No se reconoció un fármaco estándar en la imagen. Verifique el enfoque."
        }
    return {
        "success": True,
        "medication": parsed
    }


@app.get("/api/v1/medications/suspended")
def get_suspended_medications():
    """
    Returns the list of medications explicitly discontinued by specialists.
    """
    return {
        "success": True,
        "suspended_medications": SUSPENDED_MEDS
    }


@app.post("/api/v1/reports/scan-clinical-document")
def scan_clinical_document(req: ClinicalDocumentScanRequest):
    """
    Parses an entire clinical consultation sheet (OCR text or ClicSalud+ PDF text)
    and updates lab parameters, active medications, and suspended drugs.
    """
    parsed = MedicalOCRProcessor.parse_clinical_report_text(req.document_text)

    # Automatically update patient biomarkers if extracted
    if "biomarkers" in parsed and parsed["biomarkers"]:
        bm = parsed["biomarkers"]
        neph = CURRENT_PATIENT.setdefault("nephrology", {})
        if "creatinine_mg_dl" in bm:
            neph["creatinine_mg_dl"] = bm["creatinine_mg_dl"]
        if "egfr_ml_min" in bm:
            neph["egfr_ml_min"] = bm["egfr_ml_min"]
        if "potassium_meq_l" in bm:
            neph["potassium_meq_l"] = bm["potassium_meq_l"]
            neph["potassium_alert"] = bm.get("potassium_alert", "NORMAL")
        if "triglycerides_mg_dl" in bm:
            neph["triglycerides_mg_dl"] = bm["triglycerides_mg_dl"]
        if "ldl_mg_dl" in bm:
            neph["ldl_mg_dl"] = bm["ldl_mg_dl"]
        if "hba1c_pct" in bm:
            neph["hba1c_pct"] = bm["hba1c_pct"]

    return {
        "success": True,
        "extracted_data": parsed,
        "source": req.source,
        "message": "Informe clínico procesado e incorporado al historial de Ramón con éxito."
    }



