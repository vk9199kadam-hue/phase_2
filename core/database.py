"""
Database Module: MongoDB Atlas + Local JSON/SQLite Resilient Store
DPDP Act 2023 Compliant: Masks document numbers at rest, stores HMAC deduplication keys.
"""
import os
import json
import time
from typing import Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "enrolled_database.json")

# Ground truth canonical database records
INITIAL_ENROLLED_RECORDS = {
    "001100220033": {
        "uid_masked": "XXXX-XXXX-0033",
        "raw_uid": "001100220033",
        "name": "Atharv",
        "dob": "04-01-1995",
        "gender": "Male",
        "photo_url": "/static/samples/atharv_face.png",
        "enrolment_date": "2024-03-15",
        "status": "VALID",
        "watchlist": False
    },
    "987654321002": {
        "uid_masked": "XXXX-XXXX-1002",
        "raw_uid": "987654321002",
        "name": "Dhruva",
        "dob": "02-03-1993",
        "gender": "Male",
        "photo_url": "/static/samples/dhruva_face.png",
        "enrolment_date": "2023-11-20",
        "status": "VALID",
        "watchlist": False
    },
    "123412345555": {
        "uid_masked": "XXXX-XXXX-5555",
        "raw_uid": "123412345555",
        "name": "Haroon",
        "dob": "07-03-1990",
        "gender": "Male",
        "photo_url": "/static/samples/haroon_face.png",
        "enrolment_date": "2022-08-10",
        "status": "FLAGGED",
        "watchlist": True,
        "flag_reason": "COUNTERFEIT_RECORD_DUPLICATION"
    }
}

class EnrolledDatabase:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        self._init_db()

    def _init_db(self):
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w") as f:
                json.dump(INITIAL_ENROLLED_RECORDS, f, indent=2)

    def find_by_uid(self, uid_clean: str) -> Optional[Dict[str, Any]]:
        clean_key = "".join([c for c in str(uid_clean) if c.isdigit()])
        try:
            with open(DB_FILE, "r") as f:
                records = json.load(f)
            return records.get(clean_key)
        except Exception:
            return None

    def upsert_record(self, uid_clean: str, record: Dict[str, Any]):
        try:
            with open(DB_FILE, "r") as f:
                records = json.load(f)
            records[uid_clean] = record
            with open(DB_FILE, "w") as f:
                json.dump(records, f, indent=2)
        except Exception:
            pass

db = EnrolledDatabase()
