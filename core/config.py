"""
Configuration, Thresholds, and Constants for SIH26188 Phase 2 VisionX
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_SAMPLE_DATA_DIR = os.path.join(BASE_DIR, "storage", "sample_data")

if os.environ.get("VERCEL"):
    STORAGE_DIR = "/tmp/storage"
else:
    STORAGE_DIR = os.path.join(BASE_DIR, "storage")

SAMPLE_DATA_DIR = STATIC_SAMPLE_DATA_DIR
REGIONAL_CACHE_DIR = os.path.join(STORAGE_DIR, "regional_cache")
BLOCKCHAIN_LEDGER_FILE = os.path.join(STORAGE_DIR, "blockchain_ledger.json")

# Security & Department Settings
SECTOR_ID = "SSB-IN-NPL-SECTOR-04"
DEFAULT_OFFICER_GUARD = "GUARD_0482_SINGH"
DEFAULT_OFFICER_COMMAND = "COMMAND_OFFICER_VERMA"

# Risk Thresholds (AVER Engine)
RISK_THRESHOLD_GREEN_MAX = 35.0
RISK_THRESHOLD_YELLOW_MAX = 70.0

# Biometric ArcFace Cosine Distance Threshold
BIOMETRIC_COSINE_SIMILARITY_MIN = 0.65
BIOMETRIC_AGE_COMPENSATION_FACTOR = 0.05

# Forensic Bounds
ELA_MAX_TOLERANCE_SCORE = 30.0
GRADIENT_HALO_MAX_TOLERANCE = 40.0

# Known Typos and Counterfeit Indicators
KNOWN_HEADER_FORGERY_INDICATORS = ["INDIYA", "BHARAT SARKR", "AADHAR", "आदमी का अधिकार"]
AUTH_VALID_HEADERS = ["GOVERNMENT OF INDIA", "भारत सरकार", "आम आदमी का अधिकार"]
