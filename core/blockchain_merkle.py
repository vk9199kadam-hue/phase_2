"""
Cryptographic SHA-256 Merkle Chain & Immutable Audit Ledger
DPDP Act 2023 Compliant (Only cryptographic hashes & audit proofs on-chain)
"""
import os
import json
import time
import hashlib
from typing import List, Dict, Any
from core.config import BLOCKCHAIN_LEDGER_FILE, SECTOR_ID

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

class MerkleBlock:
    def __init__(self, index: int, prev_hash: str, doc_hash: str, verdict: str, 
                 risk_score: float, officer_id: str, modality: str, timestamp: float = None, nonce: int = 0):
        self.index = index
        self.prev_hash = prev_hash
        self.doc_hash = doc_hash
        self.verdict = verdict
        self.risk_score = risk_score
        self.officer_id = officer_id
        self.modality = modality
        self.sector_id = SECTOR_ID
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.block_hash = self.compute_hash()

    def compute_hash(self) -> str:
        payload = f"{self.index}|{self.prev_hash}|{self.doc_hash}|{self.verdict}|{self.risk_score:.2f}|{self.officer_id}|{self.modality}|{self.timestamp}|{self.nonce}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "block_hash": self.block_hash,
            "prev_hash": self.prev_hash,
            "doc_hash": self.doc_hash,
            "verdict": self.verdict,
            "risk_score": self.risk_score,
            "officer_id": self.officer_id,
            "modality": self.modality,
            "sector_id": self.sector_id,
            "timestamp": self.timestamp,
            "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp)),
            "nonce": self.nonce
        }


class BlockchainLedger:
    def __init__(self, ledger_path: str = BLOCKCHAIN_LEDGER_FILE):
        self.ledger_path = ledger_path
        self.chain: List[Dict[str, Any]] = []
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(self.ledger_path):
            try:
                with open(self.ledger_path, "r") as f:
                    self.chain = json.load(f)
            except Exception:
                self.chain = []
        
        if not self.chain:
            # Create Genesis Block
            genesis = MerkleBlock(
                index=0,
                prev_hash=GENESIS_HASH,
                doc_hash=hashlib.sha256(b"VISIONX_GENESIS_ROOT_SSB_2026").hexdigest(),
                verdict="SYSTEM_INIT",
                risk_score=0.0,
                officer_id="ROOT_AUTHORITY",
                modality="GENESIS",
                timestamp=time.time()
            )
            self.chain = [genesis.to_dict()]
            self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        with open(self.ledger_path, "w") as f:
            json.dump(self.chain, f, indent=2)

    def append_record(self, doc_bytes_or_str: str, verdict: str, risk_score: float, 
                      officer_id: str, modality: str) -> Dict[str, Any]:
        """
        Calculates doc hash, creates new Merkle block, and appends to chain.
        """
        if isinstance(doc_bytes_or_str, bytes):
            doc_hash = hashlib.sha256(doc_bytes_or_str).hexdigest()
        else:
            doc_hash = hashlib.sha256(str(doc_bytes_or_str).encode("utf-8")).hexdigest()

        last_block = self.chain[-1]
        new_block = MerkleBlock(
            index=len(self.chain),
            prev_hash=last_block["block_hash"],
            doc_hash=doc_hash,
            verdict=verdict,
            risk_score=risk_score,
            officer_id=officer_id,
            modality=modality,
            timestamp=time.time()
        )

        block_dict = new_block.to_dict()
        self.chain.append(block_dict)
        self._save()
        return block_dict

    def get_chain(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(reversed(self.chain))[:limit]

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Validates cryptographic hash continuity across all blocks.
        """
        if not self.chain:
            return {"valid": False, "total_blocks": 0, "error": "Chain is empty"}

        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i-1]

            if curr["prev_hash"] != prev["block_hash"]:
                return {
                    "valid": False,
                    "total_blocks": len(self.chain),
                    "error": f"Hash broken at block #{curr['index']}: prev_hash mismatch"
                }

            # Recalculate block hash
            block_obj = MerkleBlock(
                index=curr["index"],
                prev_hash=curr["prev_hash"],
                doc_hash=curr["doc_hash"],
                verdict=curr["verdict"],
                risk_score=curr["risk_score"],
                officer_id=curr["officer_id"],
                modality=curr["modality"],
                timestamp=curr["timestamp"],
                nonce=curr.get("nonce", 0)
            )
            if block_obj.block_hash != curr["block_hash"]:
                return {
                    "valid": False,
                    "total_blocks": len(self.chain),
                    "error": f"Tampered block hash at block #{curr['index']}"
                }

        return {
            "valid": True,
            "total_blocks": len(self.chain),
            "latest_block_hash": self.chain[-1]["block_hash"],
            "latest_timestamp": self.chain[-1]["formatted_time"]
        }


# Global ledger instance
ledger = BlockchainLedger()
