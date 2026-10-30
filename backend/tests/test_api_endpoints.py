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
    health_check
)
from app.schemas import (
    BiometricReadingCreate, 
    MetricType, 
    MeasurementContext, 
    CaptureMethod,
    MedicationCreate,
    AdherenceLogCreate,
    ClinicalReportRequest
)
from app.ocr_processor import MedicalOCRProcessor


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


if __name__ == '__main__':
    unittest.main()
