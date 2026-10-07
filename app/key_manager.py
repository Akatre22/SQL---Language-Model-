"""
API Key Management & Authentication Engine for Tiny SQL-SLM.
Generates, validates, and manages custom branded API keys with prefix:
AK-nice-<random_secure_hex>
"""

import os
import json
import secrets
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

KEYS_FILE = Path(__file__).resolve().parent / "api_keys.json"

class APIKeyManager:
    def __init__(self, storage_path: Path = KEYS_FILE):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        if not self.storage_path.exists():
            default_data = {
                "keys": {}
            }
            # Generate default developer master key
            default_key = self._generate_raw_key("NICE-Developer-Master")
            default_data["keys"][default_key["key_id"]] = default_key
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=2)

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"keys": {}}

    def _save_data(self, data: Dict[str, Any]):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _generate_raw_key(self, client_name: str, prefix: str = "AK-nice-") -> Dict[str, Any]:
        random_part = secrets.token_hex(20)  # 40 chars secure hex
        full_key = f"{prefix}{random_part}"
        key_id = f"key_{secrets.token_hex(6)}"
        created_at = time.strftime("%Y-%m-%d %H:%M:%S")

        return {
            "key_id": key_id,
            "api_key": full_key,
            "client_name": client_name,
            "prefix": prefix,
            "created_at": created_at,
            "last_used": None,
            "total_requests": 0,
            "is_active": True
        }

    def create_key(self, client_name: str = "Default Client", prefix: str = "AK-nice-") -> Dict[str, Any]:
        """Creates and stores a new branded API key."""
        data = self._load_data()
        new_key_meta = self._generate_raw_key(client_name=client_name, prefix=prefix)
        data["keys"][new_key_meta["key_id"]] = new_key_meta
        self._save_data(data)
        return new_key_meta

    def list_keys(self) -> List[Dict[str, Any]]:
        """Lists all keys (masking middle characters for security)."""
        data = self._load_data()
        keys_list = []
        for k in data.get("keys", {}).values():
            raw_key = k["api_key"]
            masked = raw_key[:12] + "..." + raw_key[-4:]
            keys_list.append({
                **k,
                "masked_key": masked
            })
        return keys_list

    def validate_and_record_use(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validates the incoming API key. If valid and active, increments usage and returns metadata.
        """
        if not api_key:
            return None
        
        # Clean Bearer prefix if passed
        cleaned_key = api_key.strip()
        if cleaned_key.lower().startswith("bearer "):
            cleaned_key = cleaned_key[7:].strip()

        data = self._load_data()
        for k_id, meta in data.get("keys", {}).items():
            if meta.get("is_active") and meta.get("api_key") == cleaned_key:
                meta["total_requests"] = meta.get("total_requests", 0) + 1
                meta["last_used"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self._save_data(data)
                return meta
        return None

    def revoke_key(self, key_id: str) -> bool:
        """Deactivates an existing API key."""
        data = self._load_data()
        if key_id in data.get("keys", {}):
            data["keys"][key_id]["is_active"] = False
            self._save_data(data)
            return True
        return False

    def delete_key(self, key_id: str) -> bool:
        """Permanently removes an API key."""
        data = self._load_data()
        if key_id in data.get("keys", {}):
            del data["keys"][key_id]
            self._save_data(data)
            return True
        return False

if __name__ == "__main__":
    km = APIKeyManager()
    new_k = km.create_key("Demo User")
    print(f"[+] Generated API Key: {new_k['api_key']}")
    print(f"[+] Validated: {bool(km.validate_and_record_use(new_k['api_key']))}")
