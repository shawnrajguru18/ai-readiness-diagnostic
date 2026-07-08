"""Session record persistence.

Two backends, selected at import time by the ``AIDIAG_DDB_TABLE`` env var:

  - unset  -> in-memory dict (V0 default; local dev + tests, no AWS needed).
  - set     -> Amazon DynamoDB table named by the var (survives restarts,
               shared across App Runner / ECS instances).

Both backends expose the same tiny record API used by ``app.api``:

  put(rec)         upsert a record
  save(rec)        alias for put (call after mutating a record you read back)
  get(sid)         -> record dict | None
  all_records()    -> list[record dict]   (partner-review queue)

A *record* is the plain dict ``app.api`` builds:
  {id, session: Session, scorecard: dict, created_at, status, partner_note}

The in-memory backend stores the live objects as-is. The DynamoDB backend
serializes the record to a single JSON blob (the ``Session`` via Pydantic,
everything else JSON-native) so floats/enums round-trip without DynamoDB's
Decimal/empty-string quirks, and rehydrates a live ``Session`` on read.
"""
from __future__ import annotations
import json
import os
from typing import Any, Optional

from .models import Session


# ---------- record <-> JSON (DynamoDB backend only) ----------
def _rec_to_json(rec: dict[str, Any]) -> str:
    session: Optional[Session] = rec.get("session")
    return json.dumps({
        "id": rec["id"],
        "session": session.model_dump(mode="json") if session is not None else None,
        "scorecard": rec["scorecard"],
        "created_at": rec["created_at"],
        "status": rec["status"],
        "partner_note": rec.get("partner_note", ""),
    })


def _rec_from_json(blob: str) -> dict[str, Any]:
    d = json.loads(blob)
    sess = d.get("session")
    return {
        "id": d["id"],
        "session": Session.model_validate(sess) if sess is not None else None,
        "scorecard": d["scorecard"],
        "created_at": d["created_at"],
        "status": d["status"],
        "partner_note": d.get("partner_note", ""),
    }


# ---------- backends ----------
class _MemoryStore:
    """Process-local store. State is lost on restart and not shared across instances."""

    def __init__(self) -> None:
        self._d: dict[str, dict[str, Any]] = {}

    def put(self, rec: dict[str, Any]) -> None:
        self._d[rec["id"]] = rec

    save = put

    def get(self, sid: str) -> Optional[dict[str, Any]]:
        return self._d.get(sid)

    def all_records(self) -> list[dict[str, Any]]:
        return list(self._d.values())


class _DynamoStore:
    """DynamoDB-backed store. Table needs a string partition key named ``id``."""

    def __init__(self, table_name: str) -> None:
        import boto3  # imported lazily so local/tests never need boto3 installed

        region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
        kwargs = {"region_name": region} if region else {}
        self._table = boto3.resource("dynamodb", **kwargs).Table(table_name)

    def put(self, rec: dict[str, Any]) -> None:
        self._table.put_item(Item={"id": rec["id"], "doc": _rec_to_json(rec)})

    save = put

    def get(self, sid: str) -> Optional[dict[str, Any]]:
        item = self._table.get_item(Key={"id": sid}).get("Item")
        return _rec_from_json(item["doc"]) if item else None

    def all_records(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        scan_kwargs: dict[str, Any] = {}
        while True:
            resp = self._table.scan(**scan_kwargs)
            items.extend(resp.get("Items", []))
            last = resp.get("LastEvaluatedKey")
            if not last:
                break
            scan_kwargs["ExclusiveStartKey"] = last
        return [_rec_from_json(i["doc"]) for i in items]


# ---------- module-level singleton ----------
_TABLE = os.getenv("AIDIAG_DDB_TABLE")
store: Any = _DynamoStore(_TABLE) if _TABLE else _MemoryStore()

backend = "dynamodb" if _TABLE else "memory"
