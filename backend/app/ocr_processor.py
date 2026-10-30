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

        # 2. Glucose Pattern: "114 MG/DL" or single isolated number 30-500
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
