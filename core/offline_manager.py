"""
Offline Regional Metadata Manager (Zero Internet Checkpoint Mode)
Enables edge border guards to download sector metadata in basecamp and query
by Primary Key (Aadhaar UID) in disconnected Himalayan/border zones.
"""
import os
import json
import time
from typing import Dict, Any, Optional
from core.config import REGIONAL_CACHE_DIR, SECTOR_ID

CACHE_FILE = os.path.join(REGIONAL_CACHE_DIR, "north_sector_metadata.json")
DEFERRED_QUEUE_FILE = os.path.join(REGIONAL_CACHE_DIR, "deferred_sync_queue.json")

# Preloaded Sector Ground-Truth Metadata
DEFAULT_REGIONAL_DATASET = {
    "sector_id": SECTOR_ID,
    "version": "2026.09.24-R1",
    "last_sync_timestamp": time.time(),
    "records": {
        "001100220033": {
            "primary_key": "001100220033",
            "name": "Atharv",
            "dob": "04-01-1995",
            "gender": "Male",
            "status": "CLEARANCE_ACTIVE",
            "flagged": False,
            "face_hash": "a8f93bc10294e82b7c61d5",
            "registered_sector": "SSB-IN-NPL-SECTOR-04",
            "security_clearance": "GREEN"
        },
        "987654321002": {
            "primary_key": "987654321002",
            "name": "Dhruva",
            "dob": "02-03-1993",
            "gender": "Male",
            "status": "CLEARANCE_ACTIVE",
            "flagged": False,
            "face_hash": "c71e9802bf145a990e1182",
            "registered_sector": "SSB-IN-NPL-SECTOR-04",
            "security_clearance": "GREEN"
        },
        "123412345555": {
            "primary_key": "123412345555",
            "name": "Haroon (FLAGGED)",
            "dob": "07-03-1990",
            "gender": "Male",
            "status": "LOOKOUT_CIRCULAR_ACTIVE",
            "flagged": True,
            "flag_reason": "FORGERY_SUSPECT_WATCHLIST",
            "registered_sector": "SSB-IN-NPL-SECTOR-04",
            "security_clearance": "RED"
        },
        "110022003300": {
            "primary_key": "110022003300",
            "name": "John Loyal (FLAGGED)",
            "dob": "01-01-1995",
            "gender": "Male",
            "status": "INVESTIGATION_PENDING",
            "flagged": True,
            "flag_reason": "PHOTO_SUBSTITUTION_FLAG",
            "registered_sector": "SSB-IN-NPL-SECTOR-04",
            "security_clearance": "RED"
        }
    }
}

class OfflineRegionalManager:
    def __init__(self):
        os.makedirs(REGIONAL_CACHE_DIR, exist_ok=True)
        self._init_cache()

    def _init_cache(self):
        if not os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "w") as f:
                json.dump(DEFAULT_REGIONAL_DATASET, f, indent=2)

    def get_bundle_info(self) -> Dict[str, Any]:
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
            return {
                "sector_id": data.get("sector_id", SECTOR_ID),
                "total_records_cached": len(data.get("records", {})),
                "version": data.get("version", "2026.09.24-R1"),
                "status": "READY_FOR_OFFLINE_DEPLOYMENT",
                "cache_file_size_kb": round(os.path.getsize(CACHE_FILE) / 1024, 2)
            }
        except Exception:
            return {"error": "Cache unavailable"}

    def query_primary_key_offline(self, uid_or_doc_num: str) -> Dict[str, Any]:
        """
        Fast sub-10ms offline search against cached regional dataset.
        """
        clean_key = "".join([c for c in str(uid_or_doc_num) if c.isalnum()])
        start_t = time.time()
        
        try:
            with open(CACHE_FILE, "r") as f:
                bundle = json.load(f)
                
            records = bundle.get("records", {})
            
            # Check exact key or match with spaces removed
            match = None
            if clean_key in records:
                match = records[clean_key]
            else:
                for k, v in records.items():
                    if clean_key in k or k in clean_key:
                        match = v
                        break

            latency_ms = round((time.time() - start_t) * 1000, 2)

            if match:
                is_flagged = match.get("flagged", False)
                verdict = "RED" if is_flagged else "GREEN"
                risk_score = 90.0 if is_flagged else 10.0
                return {
                    "found": True,
                    "offline_mode": True,
                    "primary_key": match.get("primary_key"),
                    "name": match.get("name"),
                    "dob": match.get("dob"),
                    "gender": match.get("gender"),
                    "status": match.get("status"),
                    "flagged": is_flagged,
                    "flag_reason": match.get("flag_reason", "None"),
                    "verdict": verdict,
                    "risk_score": risk_score,
                    "latency_ms": latency_ms,
                    "message": "Matched in Regional Offline Bundle"
                }
            else:
                return {
                    "found": False,
                    "offline_mode": True,
                    "primary_key": clean_key,
                    "verdict": "YELLOW",
                    "risk_score": 50.0,
                    "latency_ms": latency_ms,
                    "message": "Primary Key not in local sector cache. Refer to secondary checkpoint."
                }
        except Exception as e:
            return {"found": False, "error": str(e)}

    def queue_offline_verification(self, scan_payload: Dict[str, Any]):
        """
        Queues an offline scan for deferred sync when internet is restored.
        """
        queue = []
        if os.path.exists(DEFERRED_QUEUE_FILE):
            try:
                with open(DEFERRED_QUEUE_FILE, "r") as f:
                    queue = json.load(f)
            except Exception:
                queue = []
        queue.append({
            "timestamp": time.time(),
            "payload": scan_payload
        })
        with open(DEFERRED_QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2)

offline_mgr = OfflineRegionalManager()
