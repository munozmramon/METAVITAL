"""
METAVITAL Clinical Rule Engine
Implements ADA/EASD Standards of Care and ESC/ESH Hypertension Guidelines.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any


class AlertLevel(Enum):
    NORMAL = "GREEN"
    WARNING = "YELLOW"
    CRITICAL = "RED"
    EMERGENCY = "CODE_BLUE"


@dataclass
class TriageResult:
    level: AlertLevel
    title: str
    action_instructions: str
    trigger_sound: bool
    trigger_call_prompt: bool
    push_family_contact: bool


class ClinicalRuleEngine:
    @staticmethod
    def evaluate_glucose(
        glucose_mg_dl: int, 
        context: str = "FASTING",
        target_min: int = 70,
        target_max: int = 130
    ) -> TriageResult:
        """
        Evaluates glucose against ADA clinical cutoffs and personalized clinical targets.
        """
        if glucose_mg_dl < 54:
            return TriageResult(
                level=AlertLevel.EMERGENCY,
                title="HIPOGLUCEMIA SEVERA (< 54 mg/dL)",
                action_instructions=(
                    "RIESGO VITAL DE DETERIORO NEUROLÓGICO. Tome de inmediato 15g de glucosa de acción rápida "
                    "(1 cucharada de miel, medio vaso de zumo o 3 terrones de azúcar disueltos). "
                    "Solicite asistencia sanitaria urgente si presenta obnubilación."
                ),
                trigger_sound=True,
                trigger_call_prompt=True,
                push_family_contact=True,
            )
        elif glucose_mg_dl < target_min:
            return TriageResult(
                level=AlertLevel.CRITICAL,
                title=f"HIPOGLUCEMIA (< {target_min} mg/dL)",
                action_instructions=(
                    "REGLA DE LOS 15: Tome 15g de hidratos simples (medio vaso de zumo). "
                    "Espere 15 minutos en reposo absoluto y repita la medición con el glucómetro."
                ),
                trigger_sound=True,
                trigger_call_prompt=False,
                push_family_contact=False,
            )
        elif glucose_mg_dl > 300:
            return TriageResult(
                level=AlertLevel.CRITICAL,
                title="HIPERGLUCEMIA SEVERA (> 300 mg/dL)",
                action_instructions=(
                    "Beba abundante agua. Compruebe si omitió su dosis antidiabética. "
                    "Si presenta náuseas, vómitos o polipnea, acuda al hospital."
                ),
                trigger_sound=True,
                trigger_call_prompt=False,
                push_family_contact=True,
            )
        elif context == "FASTING" and glucose_mg_dl > target_max:
            return TriageResult(
                level=AlertLevel.WARNING,
                title=f"GLUCEMIA BASAL FUERA DE RANGO (> {target_max} mg/dL)",
                action_instructions="Evite hidratos simples en el desayuno y realice un paseo activo de 15 minutos.",
                trigger_sound=False,
                trigger_call_prompt=False,
                push_family_contact=False,
            )
        else:
            return TriageResult(
                level=AlertLevel.NORMAL,
                title=f"GLUCEMIA CONTROLADA ({target_min} - {target_max} mg/dL)",
                action_instructions="Valor dentro de su objetivo cardioprotector.",
                trigger_sound=False,
                trigger_call_prompt=False,
                push_family_contact=False,
            )

    @staticmethod
    def evaluate_blood_pressure(
        systolic: int, 
        diastolic: int, 
        has_symptoms: bool = False,
        target_sys_max: int = 130,
        target_dia_max: int = 80
    ) -> TriageResult:
        """
        Evaluates blood pressure against ESC/ESH guidelines and personalized target thresholds.
        """
        if systolic >= 180 or diastolic >= 120:
            if has_symptoms:
                return TriageResult(
                    level=AlertLevel.EMERGENCY,
                    title="EMERGENCIA HIPERTENSIVA (≥ 180/120 mmHg con síntomas)",
                    action_instructions="PELIGRO DE DAÑO A ÓRGANO DIANA. Llame al 112 de inmediato.",
                    trigger_sound=True,
                    trigger_call_prompt=True,
                    push_family_contact=True,
                )
            else:
                return TriageResult(
                    level=AlertLevel.CRITICAL,
                    title="URGENCIA HIPERTENSIVA ASINTOMÁTICA",
                    action_instructions=(
                        "Siéntese en reposo durante 15 minutos en ambiente tranquilo. "
                        "Repita la medición. Si persiste elevada, contacte con su centro médico."
                    ),
                    trigger_sound=True,
                    trigger_call_prompt=False,
                    push_family_contact=False,
                )
        elif systolic >= target_sys_max or diastolic >= target_dia_max:
            return TriageResult(
                level=AlertLevel.WARNING,
                title=f"PRESIÓN ARTERIAL ELEVADA (≥ {target_sys_max}/{target_dia_max} mmHg)",
                action_instructions="Compruebe la toma de su antihipertensivo prescrito y restrinja el sodio.",
                trigger_sound=False,
                trigger_call_prompt=False,
                push_family_contact=False,
            )
        elif systolic < 90 or diastolic < 60:
            return TriageResult(
                level=AlertLevel.WARNING,
                title="HIPOTENSIÓN ARTERIAL (< 90/60 mmHg)",
                action_instructions="Beba agua o caldo salado. Mantenga reposo con piernas elevadas si nota mareo.",
                trigger_sound=False,
                trigger_call_prompt=False,
                push_family_contact=False,
            )
        else:
            return TriageResult(
                level=AlertLevel.NORMAL,
                title=f"PRESIÓN ARTERIAL CONTROLADA (< {target_sys_max}/{target_dia_max} mmHg)",
                action_instructions="Valores en rango óptimo de protección vascular.",
                trigger_sound=False,
                trigger_call_prompt=False,
                push_family_contact=False,
            )

    @staticmethod
    def correlate_medication_omission(
        has_missed_dose_48h: bool, 
        current_systolic: int, 
        current_glucose: int
    ) -> Optional[str]:
        """
        Cross-correlates missed doses with hemodynamic and glycemic rebounds.
        """
        if has_missed_dose_48h and current_systolic >= 145:
            return (
                "CORRELACIÓN DETECTADA: Elevación de presión arterial vinculada a dosis omitidas en las "
                "últimas 48 horas. No duplique la toma actual; retome la pauta normal en el próximo horario."
            )
        if has_missed_dose_48h and current_glucose >= 150:
            return (
                "CORRELACIÓN DETECTADA: Elevación glucémica vinculada a olvido de medicación antidiabética. "
                "Beba agua y reanude la dosis regular pautada."
            )
        return None

