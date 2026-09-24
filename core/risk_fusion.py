"""
AVER (Adaptive Verification & Evaluation of Risk) Fusion Engine
Implements Dynamic Hardware Renormalization & Standardized Triage (GREEN / YELLOW / RED).
"""
from typing import Dict, Any, List
from core.config import RISK_THRESHOLD_GREEN_MAX, RISK_THRESHOLD_YELLOW_MAX

# Baseline Weights across the 4 Signal Families
BASE_WEIGHTS = {
    "checksum_integrity": 0.25,
    "forensic_layout": 0.25,
    "biometric_face": 0.30,
    "database_or_chip": 0.20
}

def calculate_aver_risk_score(signals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Combines multi-modal signals into a unified risk score.
    Dynamically renormalizes weights over active available signal families.
    """
    active_weights = {}
    signal_scores = {}
    reason_codes = []

    # 1. Checksum & Rule Family
    if "checksum" in signals:
        chk = signals["checksum"]
        is_valid = chk.get("valid", True)
        score = 0.0 if is_valid else 100.0
        active_weights["checksum_integrity"] = BASE_WEIGHTS["checksum_integrity"]
        signal_scores["checksum_integrity"] = score
        if not is_valid:
            reason_codes.append(chk.get("reason", "INVALID_CHECKSUM_ALGORITHM"))

    # 2. Forensic & Layout Family
    if "forensics" in signals:
        fr = signals["forensics"]
        ela_score = fr.get("ela_score", 10.0)
        halo_score = fr.get("halo_score", 10.0)
        typo_penalty = fr.get("typo_penalty", 0.0)
        
        # Combined forensic penalty
        f_risk = min(100.0, (ela_score * 0.3) + (halo_score * 0.3) + typo_penalty)
        active_weights["forensic_layout"] = BASE_WEIGHTS["forensic_layout"]
        signal_scores["forensic_layout"] = f_risk
        
        for anom in fr.get("anomalies", []):
            reason_codes.append(anom.get("code", "FORENSIC_ANOMALY"))

    # 3. Biometric Face Family
    if "biometrics" in signals:
        bio = signals["biometrics"]
        similarity = bio.get("similarity", 90.0)
        # Biometric risk is inverse of similarity
        bio_risk = max(0.0, 100.0 - similarity)
        active_weights["biometric_face"] = BASE_WEIGHTS["biometric_face"]
        signal_scores["biometric_face"] = bio_risk
        if not bio.get("is_match", True):
            reason_codes.append("CRANIOFACIAL_EMBEDDING_MISMATCH")

    # 4. Database Ground-Truth or Chip Family
    if "data_linkage" in signals:
        dl = signals["data_linkage"]
        dl_risk = dl.get("risk", 0.0)
        active_weights["database_or_chip"] = BASE_WEIGHTS["database_or_chip"]
        signal_scores["database_or_chip"] = dl_risk
        if dl_risk > 50:
            reason_codes.append(dl.get("reason", "DATABASE_GROUND_TRUTH_FLAG"))

    # Dynamic Weight Renormalization
    total_active_w = sum(active_weights.values())
    if total_active_w > 0:
        renormalized_weights = {k: v / total_active_w for k, v in active_weights.items()}
    else:
        renormalized_weights = {k: 1.0 / len(BASE_WEIGHTS) for k in BASE_WEIGHTS}

    # Calculate Weighted Final Risk
    final_risk = 0.0
    for key, weight in renormalized_weights.items():
        final_risk += signal_scores.get(key, 0.0) * weight

    final_risk = round(min(100.0, max(0.0, final_risk)), 2)

    # Triage Decision
    if final_risk < RISK_THRESHOLD_GREEN_MAX:
        verdict = "GREEN"
        status_text = "Recommended Clearance (E-Gate Eligible; Officer Confirms)"
        badge_class = "badge-green"
    elif final_risk < RISK_THRESHOLD_YELLOW_MAX:
        verdict = "YELLOW"
        status_text = "Secondary Inspection Referral (Manual Physical Verification Required)"
        badge_class = "badge-yellow"
    else:
        verdict = "RED"
        status_text = "Secondary Inspection Referral + Forensic Workup (High Risk Anomaly Detected)"
        badge_class = "badge-red"

    if not reason_codes and verdict == "GREEN":
        reason_codes = ["ALL_SIGNALS_VERIFIED_AUTHENTIC"]

    return {
        "final_risk_score": final_risk,
        "verdict": verdict,
        "status_text": status_text,
        "badge_class": badge_class,
        "reason_codes": reason_codes,
        "renormalized_weights": {k: round(v, 3) for k, v in renormalized_weights.items()},
        "signal_scores": {k: round(v, 2) for k, v in signal_scores.items()}
    }
