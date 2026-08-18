from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

import redis

from core.config import get_settings


JOB_PREFIX = "sql:job"

def _utcnow() -> str: 
    return datetime.now(timezone.utc).isoformat()


class JobStore:
    def __init__(self, client: redis.Redis, ttl_seconds: int):
        self.client = client 
        self.ttl_seconds = ttl_seconds

    def ping(self) -> bool: 
        return bool(self.client.ping())

    def create_job(self, job_id: str, payload: dict[str, Any]) -> None:
        message = payload.get("user_message")
        pipe = self.client.pipeline()
        pipe.hset(
            self._job_key(job_id),
            mapping={
                "status": "pending",
                "completed_user_gueries": "0",
                "failed_user_gueries": "0",
                "created_at": _utcnow(),
                "error": ""
                "celery_id": "",
            },
        )
        pipe.set(self._payload_key(job_id), json.dumps(payload, ensure_ascii=False))
        self._expire_job_keys(pipe, job_id)
        pipe.execute()

    def set_celery_id(self, job_id: str, celery_id: str) -> None:
        self.client.hset(self._job_key(job_id), mapping={"celery_id": celery_id})
        self._refresh_ttl(job_id)

    def get_payload(self, job_id: str) -> dict[str, Any]:
        raw = self.client.get(self._payload_key(job_id))
        if not raw: 
            raise KeyError(job_id)
        return json.loads(raw)

    def exists(self, job_id: str) -> bool:
        return bool(self.client.exists(self._job_key(job_id)))