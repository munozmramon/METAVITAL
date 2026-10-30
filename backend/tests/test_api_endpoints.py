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
    update_patient
)
from app.schemas import (
    BiometricReadingCreate, 
    MetricType, 
    MeasurementContext, 
    CaptureMethod,
    MedicationCreate,
    AdherenceLogCreate,
    ClinicalReportRequest,
    PatientProfileUpdate
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

        # Scale (Weight) display string from scale photo
        scale_parsed = MedicalOCRProcessor.parse_screen_text("84.5 KG BASCULA")
        self.assertIsNotNone(scale_parsed)
        self.assertEqual(scale_parsed["metric_type"], "WEIGHT")
        self.assertEqual(scale_parsed["value_primary"], 84.5)

    def test_patient_profile_management(self):
        pat_res = get_patient()
        self.assertTrue(pat_res["success"])
        self.assertEqual(pat_res["patient"]["first_name"], "Ramón")

        # Update patient: name, last name, age, height, weight
        update_data = PatientProfileUpdate(
            first_name="Ramón",
            last_name="García Fernández",
            age=59,
            height_cm=175.0,
            current_weight_kg=81.0
        )
        up_res = update_patient(update_data)
        self.assertTrue(up_res["success"])
        self.assertEqual(up_res["patient"]["full_name"], "Ramón García Fernández")
        self.assertEqual(up_res["patient"]["age"], 59)
        self.assertEqual(up_res["patient"]["height_cm"], 175.0)
        self.assertEqual(up_res["patient"]["current_weight_kg"], 81.0)
        # BMI = 81 / (1.75^2) = 81 / 3.0625 = 26.45
        self.assertAlmostEqual(up_res["patient"]["bmi"], 26.45, places=2)
        self.assertEqual(up_res["patient"]["bmi_category"], "Sobrepeso (Grado II)")

    def test_record_weight_updates_patient_bmi(self):
        # Emulate scale reading
        reading = BiometricReadingCreate(
            patient_id="pat-001",
            metric_type=MetricType.WEIGHT,
            value_primary=79.5,
            context=MeasurementContext.FASTING,
            capture_method=CaptureMethod.OCR_CAMERA,
            timestamp=datetime.now(timezone.utc)
        )
        res = record_biometric_reading(reading)
        self.assertTrue(res["success"])
        pat_res = get_patient()
        self.assertEqual(pat_res["patient"]["current_weight_kg"], 79.5)


if __name__ == '__main__':
    unittest.main()
