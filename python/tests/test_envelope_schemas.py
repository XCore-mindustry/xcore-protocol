from __future__ import annotations

import json

from xcore_protocol.paths import spec_root
from xcore_protocol.schema_validation import validate_instance


def test_event_envelope_schema_accepts_canonical_sample() -> None:
    schema_path = spec_root() / "envelopes" / "event-envelope.v1.json"
    payload = {
        "messageType": "moderation.ban.created",
        "messageVersion": 1,
        "target": {"playerUuid": "uuid-1", "playerName": "Target"},
        "actor": {"actorName": "admin"},
        "reason": "rule violation",
    }
    envelope = {
        "schema_version": "1",
        "message_kind": "event",
        "message_type": "moderation.ban.created",
        "message_version": 1,
        "message_id": "evt-1",
        "producer": "server:mini-pvp",
        "created_at": "1713870000000",
        "expires_at": "1713870120000",
        "content_type": "application/json",
        "payload_json": json.dumps(payload),
    }

    validate_instance(schema_path, envelope)


def test_rpc_request_envelope_schema_requires_reply_to_and_timeout() -> None:
    schema_path = spec_root() / "envelopes" / "rpc-request-envelope.v1.json"
    payload = {"messageType": "maps.list.request", "messageVersion": 1, "server": "mini-pvp"}
    envelope = {
        "schema_version": "1",
        "message_kind": "rpc_request",
        "message_type": "maps.list.request",
        "message_version": 1,
        "message_id": "req-1",
        "correlation_id": "corr-1",
        "producer": "discord-bot",
        "target": "mini-pvp",
        "created_at": "1713870000000",
        "expires_at": "1713870005000",
        "content_type": "application/json",
        "payload_json": json.dumps(payload),
        "reply_to": "xcore:rpc:resp:discord-bot",
        "timeout_ms": "5000",
    }

    validate_instance(schema_path, envelope)
