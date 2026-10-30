import unittest
import sys
import os

# Ensure backend app is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.clinical_rules import ClinicalRuleEngine, AlertLevel


class TestClinicalRuleEngine(unittest.TestCase):
    def test_severe_hypoglycemia_trigger(self):
        result = ClinicalRuleEngine.evaluate_glucose(48)
        self.assertEqual(result.level, AlertLevel.EMERGENCY)
        self.assertTrue(result.trigger_call_prompt)
        self.assertTrue(result.push_family_contact)
        self.assertIn("HIPOGLUCEMIA SEVERA", result.title)

    def test_mild_hypoglycemia_rule_of_15(self):
        result = ClinicalRuleEngine.evaluate_glucose(65)
        self.assertEqual(result.level, AlertLevel.CRITICAL)
        self.assertFalse(result.trigger_call_prompt)
        self.assertIn("REGLA DE LOS 15", result.action_instructions)

    def test_target_glucose_normal(self):
        result = ClinicalRuleEngine.evaluate_glucose(112, "FASTING")
        self.assertEqual(result.level, AlertLevel.NORMAL)
        self.assertFalse(result.trigger_sound)

    def test_high_fasting_glucose_warning(self):
        result = ClinicalRuleEngine.evaluate_glucose(155, "FASTING")
        self.assertEqual(result.level, AlertLevel.WARNING)
        self.assertIn("GLUCEMIA BASAL FUERA DE RANGO", result.title)

    def test_severe_hyperglycemia(self):
        result = ClinicalRuleEngine.evaluate_glucose(340)
        self.assertEqual(result.level, AlertLevel.CRITICAL)
        self.assertTrue(result.push_family_contact)

    def test_hypertensive_emergency_with_symptoms(self):
        result = ClinicalRuleEngine.evaluate_blood_pressure(195, 125, has_symptoms=True)
        self.assertEqual(result.level, AlertLevel.EMERGENCY)
        self.assertTrue(result.trigger_call_prompt)
        self.assertIn("EMERGENCIA HIPERTENSIVA", result.title)

    def test_hypertensive_urgency_without_symptoms(self):
        result = ClinicalRuleEngine.evaluate_blood_pressure(185, 115, has_symptoms=False)
        self.assertEqual(result.level, AlertLevel.CRITICAL)
        self.assertFalse(result.trigger_call_prompt)
        self.assertIn("URGENCIA HIPERTENSIVA", result.title)

    def test_stage_1_hypertension_warning(self):
        result = ClinicalRuleEngine.evaluate_blood_pressure(145, 92)
        self.assertEqual(result.level, AlertLevel.WARNING)
        self.assertIn("PRESIÓN ARTERIAL ELEVADA", result.title)

    def test_controlled_blood_pressure(self):
        result = ClinicalRuleEngine.evaluate_blood_pressure(122, 78)
        self.assertEqual(result.level, AlertLevel.NORMAL)

    def test_hypotension_warning(self):
        result = ClinicalRuleEngine.evaluate_blood_pressure(84, 55)
        self.assertEqual(result.level, AlertLevel.WARNING)
        self.assertIn("HIPOTENSIÓN ARTERIAL", result.title)

    def test_pharmacological_correlation_detection(self):
        msg = ClinicalRuleEngine.correlate_medication_omission(
            has_missed_dose_48h=True, 
            current_systolic=152, 
            current_glucose=110
        )
        self.assertIsNotNone(msg)
        self.assertIn("CORRELACIÓN DETECTADA", msg)
        self.assertIn("presión arterial vinculada a dosis omitidas", msg)


if __name__ == '__main__':
    unittest.main()

