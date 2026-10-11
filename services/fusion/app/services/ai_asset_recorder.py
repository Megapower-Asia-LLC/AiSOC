"""Build the observed AI estate out of the event stream.

Depth plan 6.1. This is the writer behind ``aisoc_ai_assets``, and it sits on
the fusion consumer's raw-events branch because that is the one path every
normalized event already travels on the default profile. A recorder behind a
flag, or in a service CORE does not start, is a table nothing writes and a
console page that renders "no AI estate" to a tenant that has one.

What it reads
-------------
Three shapes, each identified by what the ingest normalizer stamped on it
rather than by guessing from field presence:

* ``ai-runtime`` and ``ai-finding`` — the SDK and gateway telemetry. These
  name the agent, the model, the MCP server and the human it acted for.
* ``llm_usage`` provider audit events — these name a provider key and the
  account that minted it, and nothing about any device.
* OCSF Process Activity (class 1007) carrying a known coding-agent or MCP
  server binary — these name the device and the binary, and nothing about
  the model. Depth 6.2 widens this set; the hook is here so the two items do
  not have to touch the same file twice.

Each row records which of the three saw it, because an analyst reading an
asset with no device needs to know whether the link is missing or whether
that source could never have supplied it.

Why it buffers
--------------
A busy agent emits a span per tool call. Upserting per span would put a
write on the hot path of every AI event in the deployment to update a
``last_seen_at`` that nobody reads at that resolution. Sightings coalesce in
memory by identity and flush on size or age, the same shape the lake writer
uses, so one row is written per asset per flush interval however chatty the
agent is.

Fail-soft, in one direction
---------------------------
A Postgres outage drops the buffered sightings and logs it. It must never
wedge the consumer: an inventory is a governance surface, and losing an hour
of it is survivable in a way that stalling alert promotion is not. The drop
is counted and logged at ``warning`` so a quiet inventory is diagnosable
rather than mysterious.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger()

#: Flush when either is reached. Sized so a tenant with one agent still sees
#: its first asset inside a minute of the first span.
_MAX_PENDING = 200
_MAX_AGE_SECONDS = 30.0

#: Process names that mean a coding agent is running on a device. Matched on
#: the executable's base name, lowercased. Deliberately a small, named list
#: rather than a substring heuristic: "agent" matches half the EDR estate,
#: and a false positive here puts somebody's antivirus on an AI inventory.
CODING_AGENT_PROCESSES: dict[str, str] = {
    "claude": "Anthropic",
    "codex": "OpenAI",
    "aider": "Aider",
    "goose": "Block",
    "continue": "Continue",
    "opencode": "OpenCode",
    "gemini": "Google",
    "copilot": "GitHub",
    "copilot-language-server": "GitHub",
    "amazonq": "Amazon",
    "cline": "Cline",
}

#: Process names that mean an MCP server is running locally.
MCP_SERVER_PROCESSES: tuple[str, ...] = (
    "mcp-server",
    "mcp_server",
    "mcp-proxy",
    "uvx",
)

#: The six kinds. Mirrors `app.models.ai_asset.AI_ASSET_KINDS` in the API
#: service; the two cannot import each other because both package their code
#: as a top-level ``app``, which is the same reason the capability vocabulary
#: is mirrored rather than shared.
KIND_AI_APP = "ai_app"
KIND_CODING_AGENT = "coding_agent"
KIND_MCP_SERVER = "mcp_server"
KIND_IDE_EXTENSION = "ide_extension"
KIND_PROVIDER_KEY = "provider_key"
KIND_OAUTH_GRANT = "oauth_grant"

ALL_KINDS = (
    KIND_AI_APP,
    KIND_CODING_AGENT,
    KIND_MCP_SERVER,
    KIND_IDE_EXTENSION,
    KIND_PROVIDER_KEY,
    KIND_OAUTH_GRANT,
)

_UPSERT_SQL = """
INSERT INTO aisoc_ai_assets (
    tenant_id, kind, external_id, display_name, vendor, discovery_source,
    principal, device, attributes, risk_score, risk_reasons,
    first_seen_at, last_seen_at, observation_count
)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb, $10, $11::jsonb, $12, $13, $14)
ON CONFLICT ON CONSTRAINT aisoc_ai_assets_identity DO UPDATE SET
    -- LEAST/GREATEST rather than assignment: a replayed Kafka batch or a
    -- late-arriving span must not be able to move first_seen_at forward,
    -- which would erase the one fact an inventory exists to keep.
    first_seen_at     = LEAST(aisoc_ai_assets.first_seen_at, EXCLUDED.first_seen_at),
    last_seen_at      = GREATEST(aisoc_ai_assets.last_seen_at, EXCLUDED.last_seen_at),
    observation_count = aisoc_ai_assets.observation_count + EXCLUDED.observation_count,
    display_name      = COALESCE(EXCLUDED.display_name, aisoc_ai_assets.display_name),
    vendor            = COALESCE(EXCLUDED.vendor, aisoc_ai_assets.vendor),
    -- A later sighting that did not learn the person must not erase one an
    -- earlier sighting did. COALESCE in this order keeps the newer value
    -- when there is one and the older value when there is not.
    principal         = COALESCE(EXCLUDED.principal, aisoc_ai_assets.principal),
    attributes        = aisoc_ai_assets.attributes || EXCLUDED.attributes,
    risk_score        = EXCLUDED.risk_score,
    risk_reasons      = EXCLUDED.risk_reasons,
    updated_at        = NOW()
"""


@dataclass
class _Sighting:
    """One asset as last seen, with everything merged in."""

    tenant_id: str
    kind: str
    external_id: str
    device: str | None
    display_name: str | None = None
    vendor: str | None = None
    discovery_source: str = "ai_runtime"
    principal: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    count: int = 0
    first_seen: float = 0.0
    last_seen: float = 0.0

    @property
    def identity(self) -> tuple[str, str, str, str]:
        # The device participates in identity, and the empty string stands in
        # for "no device" so two unlinked sightings of one provider key
        # coalesce rather than accumulating. The database agrees through
        # NULLS NOT DISTINCT on the same tuple.
        return (self.tenant_id, self.kind, self.external_id, self.device or "")

    def merge(self, other: _Sighting) -> None:
        self.count += other.count
        self.first_seen = min(self.first_seen, other.first_seen) if self.first_seen else other.first_seen
        self.last_seen = max(self.last_seen, other.last_seen)
        self.display_name = other.display_name or self.display_name
        self.vendor = other.vendor or self.vendor
        self.principal = other.principal or self.principal
        for key, value in other.attributes.items():
            if key in ("tools", "models", "prompt_secret_kinds"):
                merged = set(self.attributes.get(key, [])) | set(value or [])
                self.attributes[key] = sorted(merged)
            else:
                self.attributes[key] = value


def _nested(obj: Any, *path: str) -> Any:
    cur: Any = obj
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()[:255]
    return None


def _basename(path: str) -> str:
    stem = path.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return stem[:-4] if stem.endswith(".exe") else stem


def classify(message: dict[str, Any]) -> list[_Sighting]:
    """Turn one normalized event into zero or more AI-asset sightings.

    Pure, so the classification can be tested against vendor-shaped payloads
    without a database — and so the database half can be tested without
    reconstructing an event.
    """
    ocsf = message.get("ocsf_event")
    if not isinstance(ocsf, dict):
        return []
    tenant_id = _text(message.get("tenant_id") or ocsf.get("tenant_uid"))
    if not tenant_id:
        return []

    now = time.time()
    source_type = _text(ocsf.get("source_type")) or _text(_nested(ocsf, "metadata", "product", "name")) or ""
    out: list[_Sighting] = []

    if source_type in ("ai-runtime", "ai-finding", "AI Runtime", "AI Guardrail"):
        out.extend(_from_ai_telemetry(tenant_id, ocsf, now))
    elif ocsf.get("class_uid") == 1007:
        out.extend(_from_process_activity(tenant_id, ocsf, now))
    elif source_type in ("llm_usage", "AI / LLM Usage Audit"):
        out.extend(_from_provider_audit(tenant_id, ocsf, now))

    return out


def _from_ai_telemetry(tenant_id: str, ocsf: dict[str, Any], now: float) -> list[_Sighting]:
    """SDK and gateway spans: the agent, its model, and any MCP server."""
    agent_id = _text(_nested(ocsf, "actor", "process", "name"))
    agent_name = _text(_nested(ocsf, "actor", "process", "path"))
    principal = _text(_nested(ocsf, "actor", "user", "name"))
    device = _text(_nested(ocsf, "src_endpoint", "hostname"))
    model = _text(_nested(ocsf, "metadata", "product", "feature", "name"))
    provider = _text(ocsf.get("cloud", {}).get("provider")) if isinstance(ocsf.get("cloud"), dict) else None
    tool = _text(ocsf.get("activity_name"))
    secret_kinds = _nested(ocsf, "finding", "evidence", "prompt_secret_kinds") or []
    server = _text(ocsf.get("resource", {}).get("name")) if isinstance(ocsf.get("resource"), dict) else None

    out: list[_Sighting] = []
    if agent_id:
        attributes: dict[str, Any] = {}
        if model:
            attributes["models"] = [model]
        if provider:
            attributes["provider"] = provider
        if tool:
            attributes["tools"] = [tool]
        if isinstance(secret_kinds, list) and secret_kinds:
            attributes["prompt_secret_kinds"] = sorted({str(k) for k in secret_kinds})
        # A coding agent is distinguished by its binary, not by the fact that
        # it is an agent. An agent we cannot place is an `ai_app`, which is
        # the honest answer rather than the flattering one.
        base = _basename(agent_name or agent_id)
        is_coding = base in CODING_AGENT_PROCESSES
        out.append(
            _Sighting(
                tenant_id=tenant_id,
                kind=KIND_CODING_AGENT if is_coding else KIND_AI_APP,
                external_id=agent_id,
                device=device,
                display_name=agent_name or agent_id,
                vendor=CODING_AGENT_PROCESSES.get(base) or provider,
                discovery_source="ai_runtime",
                principal=principal,
                attributes=attributes,
                count=1,
                first_seen=now,
                last_seen=now,
            )
        )
    if server:
        out.append(
            _Sighting(
                tenant_id=tenant_id,
                kind=KIND_MCP_SERVER,
                external_id=server,
                device=device,
                display_name=server,
                discovery_source="ai_runtime",
                principal=principal,
                attributes={"tools": [tool]} if tool else {},
                count=1,
                first_seen=now,
                last_seen=now,
            )
        )
    return out


def _from_process_activity(tenant_id: str, ocsf: dict[str, Any], now: float) -> list[_Sighting]:
    """EDR and osquery process telemetry: the device and the binary.

    Depth 6.2 supplies the osquery half and widens the match tables; this
    reads whatever an EDR connector already normalizes to class 1007.
    """
    name = _text(_nested(ocsf, "process", "name")) or _text(_nested(ocsf, "actor", "process", "name"))
    cmdline = _text(_nested(ocsf, "process", "cmd_line")) or ""
    device = _text(_nested(ocsf, "device", "name")) or _text(_nested(ocsf, "src_endpoint", "hostname"))
    principal = _text(_nested(ocsf, "actor", "user", "name"))
    if not name:
        return []
    base = _basename(name)

    if base in CODING_AGENT_PROCESSES:
        attributes: dict[str, Any] = {"process": base}
        # The flag an agent is started with to stop asking. Read from the
        # command line because that is the only place it appears; an agent
        # running this way takes no human confirmation before acting.
        lowered = cmdline.lower()
        if any(flag in lowered for flag in ("--dangerously-skip-permissions", "--yolo", "--auto-approve", "--no-confirm")):
            attributes["permission_prompts_disabled"] = True
        return [
            _Sighting(
                tenant_id=tenant_id,
                kind=KIND_CODING_AGENT,
                external_id=base,
                device=device,
                display_name=name,
                vendor=CODING_AGENT_PROCESSES[base],
                discovery_source="endpoint",
                principal=principal,
                attributes=attributes,
                count=1,
                first_seen=now,
                last_seen=now,
            )
        ]

    if any(token in base for token in MCP_SERVER_PROCESSES):
        return [
            _Sighting(
                tenant_id=tenant_id,
                kind=KIND_MCP_SERVER,
                external_id=base,
                device=device,
                display_name=name,
                discovery_source="endpoint",
                principal=principal,
                attributes={"process": base, "cmd_line": cmdline[:255]} if cmdline else {"process": base},
                count=1,
                first_seen=now,
                last_seen=now,
            )
        ]
    return []


def _from_provider_audit(tenant_id: str, ocsf: dict[str, Any], now: float) -> list[_Sighting]:
    """Provider control-plane audit: keys minted, grants consented to.

    No device is available from any provider's audit log, and that is the
    reason `discovery_source` exists: an analyst must be able to tell an
    unlinked device from an unlinkable one.
    """
    event_type = _text(ocsf.get("activity_name")) or ""
    principal = _text(_nested(ocsf, "actor", "user", "name"))
    provider = _text(_nested(ocsf, "metadata", "product", "vendor_name"))
    subject = _text(_nested(ocsf, "finding", "uid")) or _text(ocsf.get("message"))
    if not subject:
        return []

    lowered = event_type.lower()
    if "api_key" in lowered or "service_account" in lowered:
        kind, source = KIND_PROVIDER_KEY, "provider_audit"
    elif "oauth" in lowered or "consent" in lowered or "token" in lowered:
        kind, source = KIND_OAUTH_GRANT, "oauth_audit"
    else:
        return []

    attributes: dict[str, Any] = {"event_type": event_type}
    scopes = _nested(ocsf, "finding", "evidence", "scopes")
    if isinstance(scopes, list) and scopes:
        attributes["scopes"] = sorted({str(s) for s in scopes})

    return [
        _Sighting(
            tenant_id=tenant_id,
            kind=kind,
            external_id=subject,
            device=None,
            display_name=subject,
            vendor=provider,
            discovery_source=source,
            principal=principal,
            attributes=attributes,
            count=1,
            first_seen=now,
            last_seen=now,
        )
    ]


class AiAssetRecorder:
    """Coalesce AI-asset sightings and upsert them into Postgres."""

    def __init__(
        self,
        pool_provider: Callable[[], Any],
        *,
        max_pending: int = _MAX_PENDING,
        max_age_seconds: float = _MAX_AGE_SECONDS,
    ) -> None:
        self._pool_provider = pool_provider
        self._max_pending = max_pending
        self._max_age = max_age_seconds
        self._pending: dict[tuple[str, str, str, str], _Sighting] = {}
        self._last_flush = time.monotonic()
        self._metrics = {"observed": 0, "written": 0, "dropped": 0}

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    async def observe(self, message: dict[str, Any]) -> int:
        """Buffer any AI assets this event evidences. Returns how many."""
        sightings = classify(message)
        for sighting in sightings:
            existing = self._pending.get(sighting.identity)
            if existing is None:
                self._pending[sighting.identity] = sighting
            else:
                existing.merge(sighting)
        self._metrics["observed"] += len(sightings)
        if len(self._pending) >= self._max_pending:
            await self.flush()
        return len(sightings)

    async def flush_if_stale(self) -> None:
        if self._pending and (time.monotonic() - self._last_flush) >= self._max_age:
            await self.flush()

    async def flush(self) -> int:
        """Write everything buffered. Never raises into the consumer."""
        if not self._pending:
            self._last_flush = time.monotonic()
            return 0
        batch = list(self._pending.values())
        self._pending.clear()
        self._last_flush = time.monotonic()

        pool = self._pool_provider() if callable(self._pool_provider) else self._pool_provider
        if pool is None:
            self._metrics["dropped"] += len(batch)
            logger.warning(
                "ai_asset_recorder.no_pool",
                dropped=len(batch),
                detail="no database pool; AI inventory sightings were discarded",
            )
            return 0

        written = 0
        try:
            async with pool.acquire() as conn:
                for sighting in batch:
                    score, reasons = _score(sighting)
                    await conn.execute(
                        _UPSERT_SQL,
                        sighting.tenant_id,
                        sighting.kind,
                        sighting.external_id,
                        sighting.display_name,
                        sighting.vendor,
                        sighting.discovery_source,
                        sighting.principal,
                        sighting.device,
                        _json(sighting.attributes),
                        score,
                        _json(reasons),
                        _utc(sighting.first_seen),
                        _utc(sighting.last_seen),
                        sighting.count,
                    )
                    written += 1
        except Exception as exc:  # noqa: BLE001 — an inventory must never wedge promotion
            self._metrics["dropped"] += len(batch) - written
            logger.warning("ai_asset_recorder.flush_failed", error=str(exc)[:300], dropped=len(batch) - written)
        self._metrics["written"] += written
        return written


def _json(value: Any) -> str:
    return json.dumps(value, default=str)


def _utc(epoch: float) -> datetime:
    return datetime.fromtimestamp(epoch or time.time(), tz=UTC)


def _score(sighting: _Sighting) -> tuple[int, list[str]]:
    """Risk for a freshly observed asset.

    Mirrors ``services/api/app/services/ai_inventory.py::score_risk`` for the
    inputs a sighting carries. The two services cannot import each other, so
    ``scripts/check_ai_asset_inventory.py`` is not the thing holding them
    together — ``services/fusion/tests/test_ai_asset_recorder.py`` asserts
    the two agree on a shared table of cases, which is the only way a mirror
    stays a mirror.

    `sanctioned` is always None here: a newly observed asset is by definition
    one nobody has judged yet, and the sanction route recomputes the score
    when somebody does.
    """
    points = 0
    reasons: list[str] = []
    if not sighting.principal:
        points += 15
        reasons.append("No person is linked: nobody is accountable for what it does.")
    if not sighting.device and sighting.kind in {KIND_CODING_AGENT, KIND_IDE_EXTENSION, KIND_MCP_SERVER}:
        points += 10
        reasons.append("No device is linked, so containment has nowhere to act.")
    points += 20
    reasons.append("Not declared in the inventory: nobody has reviewed it.")
    if sighting.attributes.get("permission_prompts_disabled"):
        points += 25
        reasons.append("Started with its permission prompts disabled, so a human confirms nothing.")
    source = str(sighting.attributes.get("install_source") or "")
    if source and source not in {"official", "vendor", "internal"}:
        points += 20
        reasons.append(f"Installed from an unvetted source ({source}).")
    secret_kinds = sighting.attributes.get("prompt_secret_kinds") or []
    if secret_kinds:
        points += 20
        reasons.append(f"Credential material has appeared in its prompts ({', '.join(sorted(secret_kinds)[:3])}).")
    tools = {str(t) for t in (sighting.attributes.get("tools") or [])}
    risky = sorted(tools & _HIGH_RISK_TOOLS)
    if risky:
        points += 15
        reasons.append(f"Calls tools that change an estate ({', '.join(risky[:3])}).")
    scopes = {str(s) for s in (sighting.attributes.get("scopes") or [])}
    broad = sorted(scopes & _BROAD_OAUTH_SCOPES)
    if broad:
        points += 25
        reasons.append(f"Holds an OAuth scope covering a whole mailbox, drive or org ({broad[0]}).")
    return min(points, 100), reasons


#: Mirrors of the two tables in `app/services/ai_inventory.py`, kept here for
#: the same reason the capability vocabulary is mirrored: two independently
#: deployable services, one shared meaning, and a test that compares them.
_HIGH_RISK_TOOLS: frozenset[str] = frozenset(
    {
        "execute_command",
        "run_shell",
        "write_file",
        "delete_file",
        "send_email",
        "create_user",
        "grant_permission",
        "deploy",
        "terraform_apply",
        "database_write",
    }
)

_BROAD_OAUTH_SCOPES: frozenset[str] = frozenset(
    {
        "https://mail.google.com/",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/admin.directory.user",
        "Mail.ReadWrite",
        "Mail.Read",
        "Files.ReadWrite.All",
        "Sites.ReadWrite.All",
        "Directory.ReadWrite.All",
        "repo",
        "admin:org",
    }
)
