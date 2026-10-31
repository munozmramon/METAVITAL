import unittest
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import (
    record_biometric_reading, 
    add_medication, 
    log_adherence, 
    generate_clinical_report, 
    health_check,
    get_patient,
    update_patient,
    download_binary_pdf,
    scan_medication_box,
    scan_clinical_document,
    get_patient_doctor,
    update_patient_doctor,
    get_logo,
    get_logo_white
)
from app.schemas import (
    BiometricReadingCreate, 
    MetricType, 
    MeasurementContext, 
    CaptureMethod,
    MedicationCreate,
    AdherenceLogCreate,
    ClinicalReportRequest,
    PatientProfileUpdate,
    MedicationBoxScanRequest,
    ClinicalDocumentScanRequest,
    DoctorProfileSchema
)
from app.ocr_processor import MedicalOCRProcessor
from app.clinical_rules import ClinicalRuleEngine, AlertLevel


class TestAPIEndpointsAndOCR(unittest.TestCase):
    def test_health_check(self):
        res = health_check()
        self.assertEqual(res["status"], "OPERATIONAL")
        self.assertIn("HIPAA", res["compliance"])

    def test_record_glucose_normal(self):
        reading = BiometricReadingCreate(
            patient_id="pat-test-01",
            metric_type=MetricType.GLUCOSE,
            value_primary=112.0,
            context=MeasurementContext.FASTING,
            capture_method=CaptureMethod.OCR_CAMERA,
            timestamp=datetime.now(timezone.utc)
        )
        res = record_biometric_reading(reading)
        self.assertTrue(res["success"])
        self.assertFalse(res["record"]["is_alert"])

    def test_record_glucose_hypoglycemia_alert(self):
        reading = BiometricReadingCreate(
            patient_id="pat-test-01",
            metric_type=MetricType.GLUCOSE,
            value_primary=49.0,
            context=MeasurementContext.FASTING,
            capture_method=CaptureMethod.OCR_CAMERA,
            timestamp=datetime.now(timezone.utc)
        )
        res = record_biometric_reading(reading)
        self.assertTrue(res["success"])
        self.assertTrue(res["record"]["is_alert"])
        self.assertIn("HIPOGLUCEMIA SEVERA", res["alert"]["title"])

    def test_record_blood_pressure_crisis_alert(self):
        reading = BiometricReadingCreate(
            patient_id="pat-test-01",
            metric_type=MetricType.BLOOD_PRESSURE,
            value_primary=188.0,
            value_secondary=122.0,
            context=MeasurementContext.RANDOM,
            capture_method=CaptureMethod.OCR_CAMERA,
            timestamp=datetime.now(timezone.utc)
        )
        res = record_biometric_reading(reading)
        self.assertTrue(res["success"])
        self.assertTrue(res["record"]["is_alert"])
        self.assertIn("URGENCIA HIPERTENSIVA", res["alert"]["title"])

    def test_medication_creation_and_adherence(self):
        med = MedicationCreate(
            brand_name="Dianben",
            generic_name="Metformina",
            dose_mg=850.0,
            therapeutic_class="ANTIDIABETIC",
            scheduled_time="08:30",
            instructions="Con desayuno",
            is_active=True
        )
        res_med = add_medication(med)
        self.assertTrue(res_med["success"])
        med_id = res_med["medication"]["id"]

        adh = AdherenceLogCreate(
            medication_id=med_id,
            scheduled_time=datetime.now(timezone.utc),
            taken_time=datetime.now(timezone.utc),
            status="TAKEN_ON_TIME"
        )
        res_adh = log_adherence(adh)
        self.assertTrue(res_adh["success"])

    def test_report_compilation_output(self):
        req = ClinicalReportRequest(patient_id="pat-test-01", period_days=30)
        response = generate_clinical_report(req)
        html_content = response.body.decode("utf-8")
        self.assertIn("METAVITAL", html_content)
        self.assertIn("Ramón", html_content)
        self.assertIn("Tiempo en Rango", html_content)
        self.assertIn("Presión Arterial", html_content)

    def test_ocr_processor_screen_parsing(self):
        # Blood pressure display string
        bp_parsed = MedicalOCRProcessor.parse_screen_text("SYS 128 / DIA 82 PULSE 72")
        self.assertIsNotNone(bp_parsed)
        self.assertEqual(bp_parsed["metric_type"], "BLOOD_PRESSURE")
        self.assertEqual(bp_parsed["value_primary"], 128)
        self.assertEqual(bp_parsed["value_secondary"], 82)

        # Glucose display string
        glu_parsed = MedicalOCRProcessor.parse_screen_text("114 MG/DL")
        self.assertIsNotNone(glu_parsed)
        self.assertEqual(glu_parsed["metric_type"], "GLUCOSE")
        self.assertEqual(glu_parsed["value_primary"], 114)

        # Scale (Weight) display string from scale photo
        scale_parsed = MedicalOCRProcessor.parse_screen_text("84.5 KG BASCULA")
        self.assertIsNotNone(scale_parsed)
        self.assertEqual(scale_parsed["metric_type"], "WEIGHT")
        self.assertEqual(scale_parsed["value_primary"], 84.5)

    def test_patient_profile_management(self):
        pat_res = get_patient()
        self.assertTrue(pat_res["success"])
        self.assertEqual(pat_res["patient"]["first_name"], "Ramón")
        self.assertEqual(pat_res["patient"]["last_name"], "Muñoz Martínez")
        self.assertEqual(pat_res["patient"]["full_name"], "Ramón Muñoz Martínez")
        self.assertEqual(pat_res["patient"]["age"], 63)
        self.assertEqual(pat_res["patient"]["height_cm"], 165.0)
        self.assertEqual(pat_res["patient"]["current_weight_kg"], 101.5)
        self.assertAlmostEqual(pat_res["patient"]["bmi"], 37.28, places=2)
        self.assertEqual(pat_res["patient"]["bmi_category"], "Obesidad (Grado II)")

        # Update patient: e.g. weight progress to 98.0 kg
        update_data = PatientProfileUpdate(
            first_name="Ramón",
            last_name="Muñoz Martínez",
            age=63,
            height_cm=165.0,
            current_weight_kg=98.0
        )
        up_res = update_patient(update_data)
        self.assertTrue(up_res["success"])
        self.assertEqual(up_res["patient"]["full_name"], "Ramón Muñoz Martínez")
        self.assertEqual(up_res["patient"]["age"], 63)
        self.assertEqual(up_res["patient"]["height_cm"], 165.0)
        self.assertEqual(up_res["patient"]["current_weight_kg"], 98.0)
        # BMI = 98 / (1.65^2) = 98 / 2.7225 = 35.996 -> 36.00
        self.assertAlmostEqual(up_res["patient"]["bmi"], 36.00, places=2)
        self.assertEqual(up_res["patient"]["bmi_category"], "Obesidad (Grado II)")

    def test_record_weight_updates_patient_bmi(self):
        # Emulate scale reading
        reading = BiometricReadingCreate(
            patient_id="pat-001",
            metric_type=MetricType.WEIGHT,
            value_primary=100.8,
            context=MeasurementContext.FASTING,
            capture_method=CaptureMethod.OCR_CAMERA,
            timestamp=datetime.now(timezone.utc)
        )
        res = record_biometric_reading(reading)
        self.assertTrue(res["success"])
        pat_res = get_patient()
        self.assertEqual(pat_res["patient"]["current_weight_kg"], 100.8)

    def test_download_binary_pdf_endpoint(self):
        resp = download_binary_pdf()
        self.assertEqual(resp.media_type, "application/pdf")
        self.assertTrue(resp.body.startswith(b"%PDF-1.4"))
        self.assertIn("attachment", resp.headers.get("content-disposition", ""))

    def test_scan_medication_box_endpoint(self):
        req = MedicationBoxScanRequest(ocr_text="METFORMINA 850 MG DIANBEN")
        res = scan_medication_box(req)
        self.assertTrue(res["success"])
        med = res["medication"]
        self.assertEqual(med["generic_name"], "Metformina")
        self.assertEqual(med["dose_mg"], 850.0)
        self.assertEqual(med["therapeutic_class"], "ANTIDIABETIC")

        # Test another drug box (Atorvastatina 20 mg)
        req_statin = MedicationBoxScanRequest(ocr_text="CARDYL ATORVASTATINA 20 MG")
        res_statin = scan_medication_box(req_statin)
        self.assertTrue(res_statin["success"])
        self.assertEqual(res_statin["medication"]["generic_name"], "Atorvastatina")
        self.assertEqual(res_statin["medication"]["dose_mg"], 20.0)

    def test_personalized_clinical_targets_and_frail_profile(self):
        # Normal profile: 75 mg/dL is NOT hypoglycemia if target_min = 70
        res_standard = ClinicalRuleEngine.evaluate_glucose(75, target_min=70, target_max=130)
        self.assertEqual(res_standard.level, AlertLevel.NORMAL)

        # Frail elderly profile: 75 mg/dL IS hypoglycemia if target_min = 80
        res_frail = ClinicalRuleEngine.evaluate_glucose(75, target_min=80, target_max=160)
        self.assertEqual(res_frail.level, AlertLevel.CRITICAL)
        self.assertIn("HIPOGLUCEMIA", res_frail.title)

        # Blood pressure adaptation: 135 mmHg systolic is elevated for standard (<130), but normal for frail (<140)
        res_bp_standard = ClinicalRuleEngine.evaluate_blood_pressure(135, 78, target_sys_max=130, target_dia_max=80)
        self.assertEqual(res_bp_standard.level, AlertLevel.WARNING)

        res_bp_frail = ClinicalRuleEngine.evaluate_blood_pressure(135, 78, target_sys_max=140, target_dia_max=90)
        self.assertEqual(res_bp_frail.level, AlertLevel.NORMAL)

    def test_scan_clinical_document_endpoint(self):
        sample_doc = """
        Hospital Universitario de Jaen - Nefrologia General
        Paciente: RAMON MUNOZ MARTINEZ
        Analitica:
        glucosa 122 mg/dl, urea 62 mg/dl, Cr 1.7 mg/dl, colesterol ldl 49mg/dl, trigliceridos 346 mg/dl, K 5.5 mEq/l, HbA1c 7.1 %
        Funcion renal: FG estimado( CDP-EPI):42 ml/min/1,73m2
        Medicacion:
        Ramipril 10mg.- 1-0-0
        ATENOLOL 50 mg.- 0-0-1
        Ozempic 1mcg.- Suspender.
        TRAJENTA 5 mg.- suspender
        Secalip supra 240mg.- 1-0-0
        OMACOR.- 0-2-0
        Atorvastatina 40/10mg.- 0-0-1
        Insulina segun pauta
        """
        req = ClinicalDocumentScanRequest(document_text=sample_doc, source="CAMERA_PHOTO")
        res = scan_clinical_document(req)
        self.assertTrue(res["success"])
        extracted = res["extracted_data"]
        self.assertEqual(extracted["biomarkers"]["egfr_ml_min"], 42)
        self.assertEqual(extracted["biomarkers"]["creatinine_mg_dl"], 1.7)
        self.assertEqual(extracted["biomarkers"]["potassium_meq_l"], 5.5)
        self.assertEqual(extracted["biomarkers"]["potassium_alert"], "HIGH_BORDERLINE")
        self.assertEqual(extracted["biomarkers"]["triglycerides_mg_dl"], 346)
        self.assertEqual(extracted["biomarkers"]["ldl_mg_dl"], 49)
        self.assertEqual(extracted["biomarkers"]["hba1c_pct"], 7.1)
        self.assertEqual(len(extracted["suspended_medications"]), 1)
        self.assertEqual(extracted["suspended_medications"][0]["name"], "Trajenta 5 mg (Linagliptina)")
        self.assertTrue(any("Ozempic" in m["name"] for m in extracted["active_medications"]))

    def test_patient_doctor_endpoints(self):
        doc_res = get_patient_doctor()
        self.assertTrue(doc_res["success"])
        doctor = doc_res["doctor"]
        self.assertIn("Cobo", doctor["name"])
        self.assertEqual(doctor["health_center"], "Centro de Salud de Baeza")
        self.assertIn("+34", doctor["whatsapp_phone"])

        # Update doctor details
        new_doc = DoctorProfileSchema(
            name="Dr. Nicolás Cobo Fernández",
            health_center="Centro de Salud de Baeza (Jaén)",
            specialty="Medicina Familiar / Nefrología",
            whatsapp_phone="+34 612 345 678",
            monthly_report_day=1
        )
        up_res = update_patient_doctor(new_doc)
        self.assertTrue(up_res["success"])
        self.assertEqual(up_res["doctor"]["whatsapp_phone"], "+34 612 345 678")

    def test_logo_endpoints(self):
        resp_trans = get_logo()
        self.assertEqual(resp_trans.media_type, "image/png")
        self.assertTrue(os.path.exists(resp_trans.path))

        resp_white = get_logo_white()
        self.assertEqual(resp_white.media_type, "image/png")
        self.assertTrue(os.path.exists(resp_white.path))




if __name__ == '__main__':
    unittest.main()
