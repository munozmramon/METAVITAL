"""
METAVITAL Local Optical Character Recognition (OCR) Processor
Pre-processing and feature extraction for LCD/7-Segment medical displays.
"""

import re
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageOps, ImageFilter
import io


class MedicalOCRProcessor:
    @staticmethod
    def preprocess_lcd_image(image_bytes: bytes) -> Image.Image:
        """
        Applies grayscale conversion, contrast enhancement and adaptive binarization
        to isolate 7-segment LCD digits from backlights and glare.
        """
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        
        # Enhance contrast
        img = ImageOps.autocontrast(img, cutoff=2)
        
        # Median filter to eliminate camera sensor grain
        img = img.filter(ImageFilter.MedianFilter(size=3))
        
        # Thresholding (Otsu-like fixed thresholding for high-contrast LCDs)
        threshold = 128
        img = img.point(lambda p: 255 if p > threshold else 0)
        
        return img

    @staticmethod
    def parse_screen_text(raw_text: str) -> Optional[Dict[str, Any]]:
        """
        Extracts biometric readings from recognized characters.
        Categorizes between Glucometers (mg/dL) and Sphygmomanometers (mmHg).
        """
        cleaned = raw_text.upper().replace("\n", " ").strip()

        # 1. Blood Pressure Pattern: "128/82" or "SYS 128 DIA 82"
        bp_match = re.search(r'(\d{2,3})\s*[\/|\\]\s*(\d{2,3})(?:\s*(\d{2,3}))?', cleaned)
        if bp_match:
            sys = int(bp_match.group(1))
            dia = int(bp_match.group(2))
            pulse = int(bp_match.group(3)) if bp_match.group(3) else None
            
            if 70 <= sys <= 260 and 40 <= dia <= 160:
                return {
                    "metric_type": "BLOOD_PRESSURE",
                    "value_primary": sys,
                    "value_secondary": dia,
                    "value_tertiary": pulse,
                    "unit": "mmHg",
                    "confidence": 0.95
                }

        # Check for keyword-labeled blood pressure
        sys_match = re.search(r'(?:SYS|SIS|MAX)\D*(\d{2,3})', cleaned)
        dia_match = re.search(r'(?:DIA|MIN)\D*(\d{2,3})', cleaned)
        pul_match = re.search(r'(?:PUL|PULSE|HR)\D*(\d{2,3})', cleaned)

        if sys_match and dia_match:
            sys = int(sys_match.group(1))
            dia = int(dia_match.group(1))
            pulse = int(pul_match.group(1)) if pul_match else None
            if 70 <= sys <= 260 and 40 <= dia <= 160:
                return {
                    "metric_type": "BLOOD_PRESSURE",
                    "value_primary": sys,
                    "value_secondary": dia,
                    "value_tertiary": pulse,
                    "unit": "mmHg",
                    "confidence": 0.96
                }

        # 2. Digital Scale (Weight) Pattern: "84.5 KG", "84,5 kg" or "PESO: 84.5"
        weight_match = re.search(r'(\d{2,3}(?:[.,]\d)?)\s*(?:KG|KGS|KILOS)?', cleaned)
        has_kg = "KG" in cleaned or "KILO" in cleaned or "BASCULA" in cleaned or "PESO" in cleaned
        if weight_match and has_kg:
            val = float(weight_match.group(1).replace(",", "."))
            if 25.0 <= val <= 350.0:
                return {
                    "metric_type": "WEIGHT",
                    "value_primary": val,
                    "value_secondary": None,
                    "value_tertiary": None,
                    "unit": "kg",
                    "confidence": 0.97
                }

        # 3. Glucose Pattern: "114 MG/DL" or single isolated number 30-500
        glu_match = re.search(r'(\d{2,3})\s*(?:MG\/DL|MG\s*DL|MGDL)?', cleaned)
        if glu_match:
            val = int(glu_match.group(1))
            if 30 <= val <= 500:
                return {
                    "metric_type": "GLUCOSE",
                    "value_primary": val,
                    "value_secondary": None,
                    "value_tertiary": None,
                    "unit": "mg/dL",
                    "confidence": 0.94
                }

        return None

    @staticmethod
    def parse_medication_box_text(raw_text: str) -> Optional[Dict[str, Any]]:
        """
        Parses drug packaging text (boxes or blister packs).
        Extracts active ingredient, dosage, therapeutic category and suggests timing.
        """
        cleaned = raw_text.upper().replace("\n", " ").strip()

        KNOWN_DRUGS = [
            # Antidiabetics
            {"name": "METFORMINA", "class": "ANTIDIABETIC", "brand": "Dianben", "timing": "08:30", "instructions": "Tomar junto con el desayuno para evitar molestias digestivas."},
            {"name": "EMPAGLIFLOZINA", "class": "ANTIDIABETIC", "brand": "Jardiance", "timing": "08:30", "instructions": "Tomar por la mañana con o sin comida."},
            {"name": "DAPAGLIFLOZINA", "class": "ANTIDIABETIC", "brand": "Forxiga", "timing": "08:30", "instructions": "Tomar por la mañana. Mantener buena hidratación."},
            {"name": "SITAGLIPTINA", "class": "ANTIDIABETIC", "brand": "Januvia", "timing": "09:00", "instructions": "Una vez al día con o sin alimentos."},
            {"name": "OZEMPIC", "class": "ANTIDIABETIC", "brand": "Ozempic", "timing": "Domingos 09:00", "instructions": "1 inyección subcutánea semanal. Agonista GLP-1 para control glucémico y ponderal."},
            {"name": "SEMAGLUTIDA", "class": "ANTIDIABETIC", "brand": "Ozempic", "timing": "Domingos 09:00", "instructions": "1 inyección subcutánea semanal."},
            # Antihypertensives
            {"name": "RAMIPRIL", "class": "ANTIHYPERTENSIVE", "brand": "Tritace", "timing": "08:30", "instructions": "Tomar por la mañana (1-0-0). Protección cardio-renal."},
            {"name": "ATENOLOL", "class": "ANTIHYPERTENSIVE", "brand": "Tenormin", "timing": "21:30", "instructions": "Tomar por la noche (0-0-1). Control tensional y frecuencia."},
            {"name": "ENALAPRIL", "class": "ANTIHYPERTENSIVE", "brand": "Renitec", "timing": "09:00", "instructions": "Tomar por la mañana con agua."},
            {"name": "LOSARTAN", "class": "ANTIHYPERTENSIVE", "brand": "Cozaar", "timing": "09:00", "instructions": "Tomar por la mañana preferentemente."},
            {"name": "VALSARTAN", "class": "ANTIHYPERTENSIVE", "brand": "Diovan", "timing": "09:00", "instructions": "Tomar por la mañana con un vaso de agua."},
            {"name": "AMLODIPINO", "class": "ANTIHYPERTENSIVE", "brand": "Norvas", "timing": "09:00", "instructions": "Tomar por la mañana."},
            # Statins & Lipid Lowering
            {"name": "ATORVASTATINA", "class": "STATIN_LIPID", "brand": "Cardyl", "timing": "21:30", "instructions": "Tomar por la noche tras la cena (0-0-1)."},
            {"name": "SECALIP", "class": "STATIN_LIPID", "brand": "Secalip supra", "timing": "08:30", "instructions": "Fenofibrato: Tomar 1 cápsula por la mañana (1-0-0) para reducir triglicéridos."},
            {"name": "FENOFIBRATO", "class": "STATIN_LIPID", "brand": "Secalip supra", "timing": "08:30", "instructions": "Tomar 1 cápsula por la mañana (1-0-0) con desayuno."},
            {"name": "OMACOR", "class": "STATIN_LIPID", "brand": "Omacor", "timing": "14:00", "instructions": "Omega-3: Tomar 2 cápsulas al mediodía (0-2-0) con la comida."},
            {"name": "ROSUVASTATINA", "class": "STATIN_LIPID", "brand": "Crestor", "timing": "21:30", "instructions": "Tomar por la noche con o sin alimentos."},
            {"name": "SIMVASTATINA", "class": "STATIN_LIPID", "brand": "Zocor", "timing": "21:30", "instructions": "Tomar invariablemente por la noche."},
        ]

        # Extract dosage in mg
        dose_match = re.search(r'(\d{1,4}(?:[.,]\d)?)\s*(?:MG|MILIGRAMOS)', cleaned)
        extracted_dose = float(dose_match.group(1).replace(",", ".")) if dose_match else 20.0

        for drug in KNOWN_DRUGS:
            if drug["name"] in cleaned or drug["brand"].upper() in cleaned:
                return {
                    "generic_name": drug["name"].capitalize(),
                    "brand_name": drug["brand"],
                    "dose_mg": extracted_dose,
                    "therapeutic_class": drug["class"],
                    "scheduled_time": drug["timing"],
                    "instructions": drug["instructions"],
                    "confidence": 0.96
                }

        return None

    @staticmethod
    def parse_clinical_report_text(raw_text: str) -> Dict[str, Any]:
        """
        Parses full clinical and nephrological consultation reports (e.g. Hospital Universitario de Jaén).
        Extracts renal function (eGFR, Creatinine, Urea, Potassium), lipid panel, glycemic metrics,
        active prescriptions, and suspended medications.
        """
        cleaned = raw_text.replace("\n", " ").strip()
        result: Dict[str, Any] = {
            "hospital": "Hospital Universitario de Jaén" if "JAÉN" in cleaned.upper() else "Centro Hospitalario",
            "specialty": "Nefrología General" if "NEFROLOG" in cleaned.upper() else "Medicina Interna",
            "biomarkers": {},
            "active_medications": [],
            "suspended_medications": [],
            "clinical_notes": []
        }

        # 1. Creatinine
        cr_match = re.search(r'(?:CR|CREATININA)\s*[:=]?\s*(\d+[.,]\d+)\s*(?:MG\/DL)?', cleaned, re.IGNORECASE)
        if cr_match:
            result["biomarkers"]["creatinine_mg_dl"] = float(cr_match.group(1).replace(",", "."))

        # 2. Urea
        urea_match = re.search(r'(?:UREA)\s*[:=]?\s*(\d+)\s*(?:MG\/DL)?', cleaned, re.IGNORECASE)
        if urea_match:
            result["biomarkers"]["urea_mg_dl"] = int(urea_match.group(1))

        # 3. Potassium (K)
        k_match = re.search(r'\bK\s*[:=]?\s*(\d+[.,]\d+)\s*(?:MEQ\/L|MMOL\/L)?', cleaned, re.IGNORECASE)
        if k_match:
            val_k = float(k_match.group(1).replace(",", "."))
            result["biomarkers"]["potassium_meq_l"] = val_k
            result["biomarkers"]["potassium_alert"] = "HIGH_BORDERLINE" if val_k >= 5.0 else "NORMAL"

        # 4. Estimated GFR (FG estimado)
        fg_match = re.search(r'(?:FG ESTIMADO|FILTRADO|CDP-EPI|CKD-EPI)\D*(\d{1,3})\s*(?:ML\/MIN)?', cleaned, re.IGNORECASE)
        if fg_match:
            val_fg = int(fg_match.group(1))
            result["biomarkers"]["egfr_ml_min"] = val_fg
            result["biomarkers"]["ckd_stage"] = "ERC Estadio 3a" if 45 <= val_fg < 60 or val_fg >= 30 else "ERC"

        # 5. Glucose & HbA1c
        glu_match = re.search(r'(?:GLUCOSA|GLICEMIA)\s*[:=]?\s*(\d{2,3})', cleaned, re.IGNORECASE)
        if glu_match:
            result["biomarkers"]["glucose_mg_dl"] = int(glu_match.group(1))

        hba1c_match = re.search(r'(?:HBA1C)\s*[:=]?\s*(\d+[.,]\d+)\s*%', cleaned, re.IGNORECASE)
        if hba1c_match:
            result["biomarkers"]["hba1c_pct"] = float(hba1c_match.group(1).replace(",", "."))

        # 6. Lipids (LDL & Triglycerides)
        ldl_match = re.search(r'(?:COLESTEROL\s+LDL|LDL)\s*[:=]?\s*(\d{2,3})', cleaned, re.IGNORECASE)
        if ldl_match:
            result["biomarkers"]["ldl_mg_dl"] = int(ldl_match.group(1))

        tg_match = re.search(r'(?:TRIGLIC[EÉ]RIDOS|TG)\s*[:=]?\s*(\d{2,4})', cleaned, re.IGNORECASE)
        if tg_match:
            result["biomarkers"]["triglycerides_mg_dl"] = int(tg_match.group(1))

        # 7. Check for Suspended Drugs
        if re.search(r'TRAJENTA.*?SUSPEND', cleaned, re.IGNORECASE):
            result["suspended_medications"].append({
                "name": "Trajenta 5 mg (Linagliptina)",
                "action": "SUSPENDIDO",
                "reason": "Retirado por Nefrólogo en revisión de consulta"
            })

        # 8. Check for Active Prescriptions
        if "OZEMPIC" in cleaned.upper():
            result["active_medications"].append({"name": "Ozempic 1 mg (Semaglutida)", "posology": "1 inyección subcutánea semanal (Pauta activa)"})
        if "RAMIPRIL" in cleaned.upper():
            result["active_medications"].append({"name": "Ramipril 10 mg", "posology": "1-0-0 (Desayuno)"})
        if "ATENOLOL" in cleaned.upper():
            result["active_medications"].append({"name": "Atenolol 50 mg", "posology": "0-0-1 (Noche)"})
        if "SECALIP" in cleaned.upper() or "FENOFIBRATO" in cleaned.upper():
            result["active_medications"].append({"name": "Secalip supra 240 mg", "posology": "1-0-0 (Desayuno)"})
        if "OMACOR" in cleaned.upper() or "OMEGA 3" in cleaned.upper():
            result["active_medications"].append({"name": "Omacor (Omega-3)", "posology": "0-2-0 (Almuerzo 2 cápsulas)"})
        if "ATORVASTATINA" in cleaned.upper():
            result["active_medications"].append({"name": "Atorvastatina 40/10 mg", "posology": "0-0-1 (Noche)"})
        if "METFORMINA" in cleaned.upper() or "EMPAGLIFLOZINA" in cleaned.upper() or "SYNJARDY" in cleaned.upper():
            result["active_medications"].append({"name": "Metformina 1000 mg / Empagliflozina 12.5 mg", "posology": "1-0-1 (Desayuno y Cena)"})
        if "INSULINA" in cleaned.upper():
            result["active_medications"].append({"name": "Insulina", "posology": "Pauta médica habitual con rotación de cuadrante"})

        # 9. Key Warnings
        if "NO SE REALIZA CORRECTA" in cleaned.upper() and "INSULINA" in cleaned.upper():
            result["clinical_notes"].append("LIPODISTROFIA: Imprescindible alternar punto de inyección de insulina en 4 cuadrantes para evitar absorciones erráticas.")
        if "ANTIINFLAMATORIOS" in cleaned.upper() or "AINES" in cleaned.upper():
            result["clinical_notes"].append("NEFROTOXICIDAD: Evitar AINEs (Ibuprofeno, Enantyum). Usar Paracetamol o Metamizol.")
        if "ALCER" in cleaned.upper():
            result["clinical_notes"].append("SOPORTE: Contacto disponible de ALCER Jaén (953 25 22 44).")

        return result

