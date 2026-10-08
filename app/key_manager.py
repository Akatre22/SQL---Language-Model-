"""
API Key Management & Authentication Engine for Tiny SQL-SLM.
Features:
1. Branded Key Generation (AK-nice-<random_secure_hex>).
2. Lifecycle Controls: Revoke, Activate, Delete.
3. Quota Limits & Rate Limit Configuration.
4. Deep Usage Telemetry & Per-Key Analytics.
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
            default_key = self._generate_raw_key("NICE-Developer-Master", quota_limit=None)
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

    def _generate_raw_key(
        self,
        client_name: str,
        prefix: str = "AK-nice-",
        quota_limit: Optional[int] = None,
        rate_limit_rpm: Optional[int] = 60
    ) -> Dict[str, Any]:
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
            "successful_requests": 0,
            "failed_requests": 0,
            "quota_limit": quota_limit,  # None means unlimited
            "rate_limit_rpm": rate_limit_rpm,
            "is_active": True,
            "recent_latency_ms": []
        }

    def create_key(
        self,
        client_name: str = "Default Client",
        prefix: str = "AK-nice-",
        quota_limit: Optional[int] = None,
        rate_limit_rpm: Optional[int] = 60
    ) -> Dict[str, Any]:
        """Creates and stores a new branded API key with configurable limits."""
        data = self._load_data()
        new_key_meta = self._generate_raw_key(
            client_name=client_name,
            prefix=prefix,
            quota_limit=quota_limit,
            rate_limit_rpm=rate_limit_rpm
        )
        data["keys"][new_key_meta["key_id"]] = new_key_meta
        self._save_data(data)
        return new_key_meta

    def list_keys(self) -> List[Dict[str, Any]]:
        """Lists all registered keys with masked tokens and quota status."""
        data = self._load_data()
        keys_list = []
        for k in data.get("keys", {}).values():
            raw_key = k["api_key"]
            masked = raw_key[:12] + "..." + raw_key[-4:]
            quota = k.get("quota_limit")
            total = k.get("total_requests", 0)
            is_exhausted = (quota is not None) and (total >= quota)
            
            keys_list.append({
                **k,
                "masked_key": masked,
                "is_exhausted": is_exhausted,
                "remaining_quota": max(0, quota - total) if quota is not None else "Unlimited"
            })
        return keys_list

    def validate_and_record_use(self, api_key: str, latency_ms: Optional[float] = None, is_success: bool = True) -> Optional[Dict[str, Any]]:
        """
        Validates the incoming API key.
        Checks active status and quota limits, then records telemetry.
        """
        if not api_key:
            return None
        
        cleaned_key = api_key.strip()
        if cleaned_key.lower().startswith("bearer "):
            cleaned_key = cleaned_key[7:].strip()

        data = self._load_data()
        for k_id, meta in data.get("keys", {}).items():
            if meta.get("api_key") == cleaned_key:
                if not meta.get("is_active"):
                    return None  # Revoked key
                
                quota = meta.get("quota_limit")
                total = meta.get("total_requests", 0)
                if quota is not None and total >= quota:
                    return None  # Quota exhausted
                
                meta["total_requests"] = total + 1
                if is_success:
                    meta["successful_requests"] = meta.get("successful_requests", 0) + 1
                else:
                    meta["failed_requests"] = meta.get("failed_requests", 0) + 1
                
                meta["last_used"] = time.strftime("%Y-%m-%d %H:%M:%S")
                if latency_ms is not None:
                    lat_list = meta.get("recent_latency_ms", [])
                    lat_list.append(round(latency_ms, 1))
                    meta["recent_latency_ms"] = lat_list[-20:]  # Keep last 20
                
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

    def activate_key(self, key_id: str) -> bool:
        """Re-activates a revoked API key."""
        data = self._load_data()
        if key_id in data.get("keys", {}):
            data["keys"][key_id]["is_active"] = True
            self._save_data(data)
            return True
        return False

    def update_limit(self, key_id: str, quota_limit: Optional[int] = None, rate_limit_rpm: Optional[int] = None) -> bool:
        """Updates request quota and rate limit for an existing key."""
        data = self._load_data()
        if key_id in data.get("keys", {}):
            if quota_limit is not None or quota_limit == 0 or quota_limit == -1:
                data["keys"][key_id]["quota_limit"] = None if quota_limit in [None, -1, 0] else quota_limit
            if rate_limit_rpm is not None:
                data["keys"][key_id]["rate_limit_rpm"] = rate_limit_rpm
            self._save_data(data)
            return True
        return False

    def delete_key(self, key_id: str) -> bool:
        """Permanently removes an API key from registry."""
        data = self._load_data()
        if key_id in data.get("keys", {}):
            del data["keys"][key_id]
            self._save_data(data)
            return True
        return False

    def get_analytics(self) -> Dict[str, Any]:
        """Calculates aggregated usage analytics across all registered API keys."""
        data = self._load_data()
        keys = list(data.get("keys", {}).values())
        total_keys = len(keys)
        active_keys = sum(1 for k in keys if k.get("is_active"))
        revoked_keys = total_keys - active_keys
        total_requests = sum(k.get("total_requests", 0) for k in keys)
        total_success = sum(k.get("successful_requests", 0) for k in keys)
        total_failed = sum(k.get("failed_requests", 0) for k in keys)
        
        all_latencies = []
        for k in keys:
            all_latencies.extend(k.get("recent_latency_ms", []))
        avg_latency = round(sum(all_latencies) / len(all_latencies), 1) if all_latencies else 0.0

        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "revoked_keys": revoked_keys,
            "total_requests": total_requests,
            "successful_requests": total_success,
            "failed_requests": total_failed,
            "success_rate_pct": round((total_success / total_requests * 100), 1) if total_requests > 0 else 100.0,
            "average_latency_ms": avg_latency,
            "keys_summary": [
                {
                    "key_id": k["key_id"],
                    "client_name": k["client_name"],
                    "masked_key": k["api_key"][:12] + "..." + k["api_key"][-4:],
                    "total_requests": k.get("total_requests", 0),
                    "quota_limit": k.get("quota_limit"),
                    "is_active": k.get("is_active", True),
                    "last_used": k.get("last_used") or "Never"
                }
                for k in keys
            ]
        }

if __name__ == "__main__":
    km = APIKeyManager()
    print("API Key Analytics:", km.get_analytics())
