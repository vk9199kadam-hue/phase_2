"""
Forensics Engine: ELA (Error Level Analysis), Gradient Boundary Discontinuity, 
and Multimodal Layout/Typographic Forgery Checks.
"""
import io
import os
import numpy as np
import cv2
from PIL import Image, ImageChops, ImageEnhance
from typing import Dict, Any, Tuple
from core.config import (
    ELA_MAX_TOLERANCE_SCORE, 
    GRADIENT_HALO_MAX_TOLERANCE, 
    KNOWN_HEADER_FORGERY_INDICATORS
)

def perform_error_level_analysis(image_input) -> Tuple[float, str]:
    """
    Performs ELA by resaving the image at 90% JPEG quality and calculating
    the pixel-level reconstruction error.
    Returns: (ela_score, ela_heatmap_base64_or_desc)
    """
    try:
        if isinstance(image_input, (str, bytes)):
            if isinstance(image_input, str) and os.path.exists(image_input):
                img = Image.open(image_input).convert('RGB')
            else:
                img = Image.open(io.BytesIO(image_input)).convert('RGB')
        elif isinstance(image_input, np.ndarray):
            img = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
        elif isinstance(image_input, Image.Image):
            img = image_input.convert('RGB')
        else:
            return 0.0, "NORMAL"

        # Resave at 90% quality
        buffer = io.BytesIO()
        img.save(buffer, 'JPEG', quality=90)
        buffer.seek(0)
        resaved = Image.open(buffer)

        # Difference
        diff = ImageChops.difference(img, resaved)
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
        scale = 255.0 / max_diff
        enhanced_diff = ImageEnhance.Brightness(diff).enhance(scale)
        
        # Calculate mean error score
        stat_arr = np.array(enhanced_diff)
        mean_score = float(np.mean(stat_arr))
        
        # Normalized ELA score 0 - 100
        normalized_ela = min(100.0, (mean_score / 255.0) * 140.0)
        return round(normalized_ela, 2), "COMPRESSION_ANALYSIS_OK"
    except Exception as e:
        return 15.0, f"ELA_FALLBACK_{str(e)}"


def check_photo_boundary_gradient(image_bgr: np.ndarray, face_box: tuple = None) -> Tuple[float, bool]:
    """
    Examines the 5-pixel boundary around the photo for edge gradient discontinuity
    (Detects physical cut-and-paste or digital overlay halo artifacts).
    """
    try:
        if image_bgr is None:
            return 0.0, False
            
        h, w = image_bgr.shape[:2]
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1]
        
        # If face_box not provided, default to expected ID card portrait ROI
        if face_box is None:
            x1, y1, x2, y2 = int(w * 0.05), int(h * 0.25), int(w * 0.35), int(h * 0.85)
        else:
            x1, y1, x2, y2 = face_box

        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return 0.0, False

        # Check for chromatic aberration / bright tamper outline along perimeter
        pad = 4
        strip_sat = []
        if y1 > pad: strip_sat.append(np.mean(sat[y1-pad:y1+pad, x1:x2]))
        if y2 + pad < h: strip_sat.append(np.mean(sat[y2-pad:y2+pad, x1:x2]))
        if x1 > pad: strip_sat.append(np.mean(sat[y1:y2, x1-pad:x1+pad]))
        if x2 + pad < w: strip_sat.append(np.mean(sat[y1:y2, x2-pad:x2+pad]))
        
        mean_sat = np.mean(strip_sat) if strip_sat else 0.0
        
        # High perimeter saturation (>80) indicates synthetic/digital halo outline
        if mean_sat > 60:
            halo_score = min(100.0, mean_sat * 1.1)
            is_tampered = True
        else:
            halo_score = max(5.0, min(25.0, mean_sat * 0.4))
            is_tampered = False

        return float(round(float(halo_score), 2)), is_tampered
    except Exception:
        return 12.0, False


def inspect_text_layout_and_typos(extracted_text: str) -> Dict[str, Any]:
    """
    Multimodal rule-based forensic examiner:
    Scans for hallmark forgery keywords (e.g. 'INDIYA' instead of 'INDIA',
    'आदमी का अधिकार' instead of 'आम आदमी का अधिकार', etc.)
    """
    text_upper = (extracted_text or "").upper()
    detected_anomalies = []
    
    # 1. Header typo checks
    if "INDIYA" in text_upper:
        detected_anomalies.append({
            "code": "FORGERY_TYPO_INDIYA",
            "field": "Header",
            "description": "Counterfeit Spelling Detected: 'GOVERNMENT OF INDIYA' (Should be 'INDIA')",
            "severity": "CRITICAL",
            "penalty": 55
        })
        
    if "आदमी का अधिकार" in extracted_text and "आम आदमी" not in extracted_text:
        detected_anomalies.append({
            "code": "SLOGAN_TAMPER",
            "field": "Aadhaar Motto",
            "description": "Corrupted Tagline Detected: 'आदमी का अधिकार' (Authentic is 'मेरा आधार, मेरी पहचान' / 'आम आदमी का अधिकार')",
            "severity": "HIGH",
            "penalty": 30
        })

    # 2. Structure & Keyword checks
    has_dob = ("DOB" in text_upper) or ("जन्म" in extracted_text) or ("YEAR OF BIRTH" in text_upper)
    has_gender = ("MALE" in text_upper) or ("FEMALE" in text_upper) or ("TRANSGENDER" in text_upper) or ("पुरुष" in extracted_text) or ("महिला" in extracted_text)
    
    if not has_dob and len(text_upper) > 20:
        detected_anomalies.append({
            "code": "MISSING_DOB_FIELD",
            "field": "DOB",
            "description": "Standard Date of Birth field header is absent",
            "severity": "MEDIUM",
            "penalty": 20
        })

    total_penalty = int(sum([a["penalty"] for a in detected_anomalies]))
    
    return {
        "anomalies": detected_anomalies,
        "is_counterfeit_flagged": bool(len(detected_anomalies) > 0),
        "total_penalty": total_penalty,
        "summary": "Layout & Typography Validated" if not detected_anomalies else f"Detected {len(detected_anomalies)} structural anomalies"
    }
