"""Depth plan 2.4 — the stateful half of the session projection.

The fake connection here records the SQL and arguments it was given rather
than answering whatever it is asked. A double that returns a plausible row for
any query is how a store that writes to the wrong column passes its tests: the
assertions below are on what would reach Postgres, and the schema those
arguments have to satisfy is asserted against the migration itself.
"""

from __future__ import annotations

import json
import re
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

import pytest
from app.services.sessions import (
    KEY_KINDS,
    SessionStore,
    session_id,
)

MIGRATION = Path(__file__).resolve().parents[3] / "services" / "api" / "migrations" / "102_sessions.sql"

TENANT = "11111111-1111-1111-1111-111111111111"


class RecordingConn:
    def __init__(self, fail: Exception | None = None) -> None:
        self.calls: list[tuple[str, tuple]] = []
        self._fail = fail

    async def execute(self, sql: str, *args):
        if self._fail is not None:
            raise self._fail
        self.calls.append((sql, args))
        return "INSERT 0 1"

    def sql_containing(self, needle: str) -> tuple[str, tuple]:
        for sql, args in self.calls:
            if needle in sql:
                return sql, args
        raise AssertionError(f"no statement containing {needle!r}; saw {[s[:40] for s, _ in self.calls]}")


class RecordingPool:
    def __init__(self, conn: RecordingConn) -> None:
        self.conn = conn

    @asynccontextmanager
    async def acquire(self):
        yield self.conn


def event(session: dict | None, *, tenant_source: str = "aws_cloudtrail", actor_kind: str = "human") -> dict:
    activity: dict = {"actor": {"kind": actor_kind, "id": "arn:aws:iam::1:user/alice"}, "location": {"ip": "203.0.113.10"}}
    if session is not None:
        activity["session"] = session
    return {
        "metadata": {"product": {"name": tenant_source}},
        "time": 1_760_000_000_000,
        "activity": activity,
    }


@pytest.mark.asyncio
async def test_a_vendor_session_is_upserted_with_its_kind():
    conn = RecordingConn()
    store = SessionStore(RecordingPool(conn))

    ref = await store.record_event(
        TENANT,
        event({"key": "ASIAIOSFODNN7EXAMPLE", "key_kind": "vendor_credential", "key_source": "userIdentity.accessKeyId"}),
    )

    assert ref is not None
    assert ref.key == "ASIAIOSFODNN7EXAMPLE"
    assert ref.key_kind == "vendor_credential"
    assert ref.is_vendor_grouping is True

    _, args = conn.sql_containing("INSERT INTO sessions")
    assert args[0] == session_id(TENANT, "aws_cloudtrail", "ASIAIOSFODNN7EXAMPLE")
    assert args[2] == "ASIAIOSFODNN7EXAMPLE"
    assert args[3] == "vendor_credential"
    assert json.loads(args[10]) == ["human"]
    assert json.loads(args[11]) == ["203.0.113.10"]


@pytest.mark.asyncio
async def test_an_event_with_no_session_writes_nothing():
    """None is an answer, and it has to stay None all the way to the console.

    A session of one invented for every unattributable event would make "what
    else did this session do" answerable with a number that means nothing.
    """
    conn = RecordingConn()
    store = SessionStore(RecordingPool(conn))

    assert await store.record_event(TENANT, event(None)) is None
    assert conn.calls == []


@pytest.mark.asyncio
async def test_a_kind_outside_the_closed_set_is_refused():
    """Producer and consumer drift is a deploy-skew bug, not a data quirk.

    Writing the row anyway would fail the CHECK constraint in Postgres and
    surface as an unexplained insert error on the hot path.
    """
    conn = RecordingConn()
    store = SessionStore(RecordingPool(conn))

    assert await store.record_event(TENANT, event({"key": "s1", "key_kind": "guessed"})) is None
    assert conn.calls == []


@pytest.mark.asyncio
async def test_the_derived_kind_is_marked_as_not_the_vendors_grouping():
    conn = RecordingConn()
    store = SessionStore(RecordingPool(conn))

    ref = await store.record_event(
        TENANT, event({"key": "alice|203.0.113.10|curl/8", "key_kind": "derived", "key_source": "principal+ip+user_agent"})
    )

    assert ref is not None
    assert ref.is_vendor_grouping is False


@pytest.mark.asyncio
async def test_the_issued_session_is_written_with_the_edge_back_to_its_parent():
    """The chain is why 2.4 reaches into the AssumeRole response at all.

    The child session's own events name only the role it assumed, so without
    this row the person behind it is unrecoverable once the issuing call ages
    out of the lake.
    """
    conn = RecordingConn()
    store = SessionStore(RecordingPool(conn))

    parent = await store.record_event(
        TENANT,
        event(
            {
                "key": "AKIAPARENT0000000EXM",
                "key_kind": "vendor_credential",
                "key_source": "userIdentity.accessKeyId",
                "issued": {
                    "key": "ASIACHILD0000000EXMP",
                    "key_source": "responseElements.credentials.accessKeyId",
                    "principal": "arn:aws:sts::1:assumed-role/Deploy/build-471",
                    "originating_human": "alice@corp.example",
                    "originating_human_source": "requestParameters.sourceIdentity",
                },
            }
        ),
    )

    assert parent is not None
    _, args = conn.sql_containing("parent_session_id")
    assert args[0] == session_id(TENANT, "aws_cloudtrail", "ASIACHILD0000000EXMP")
    assert args[2] == "ASIACHILD0000000EXMP"
    assert args[6] == "alice@corp.example"
    assert args[7] == "requestParameters.sourceIdentity"
    assert args[9] == parent.id, "the edge must point at the session that issued the credential"


@pytest.mark.asyncio
async def test_a_call_that_issued_its_own_credential_is_not_its_own_parent():
    conn = RecordingConn()
    store = SessionStore(RecordingPool(conn))

    await store.record_event(
        TENANT,
        event(
            {
                "key": "ASIASAME00000000EXMP",
                "key_kind": "vendor_credential",
                "issued": {"key": "ASIASAME00000000EXMP", "key_source": "responseElements.credentials.accessKeyId"},
            }
        ),
    )

    assert all("parent_session_id" not in sql for sql, _ in conn.calls)


@pytest.mark.asyncio
async def test_the_id_is_deterministic_across_stores_and_replays():
    """Three stores have to agree on one id without coordinating, and a Kafka
    replay must upsert the same row rather than minting a second session."""
    first = session_id(TENANT, "okta", "102bFs0Aq6VQ1qjqVqk")
    second = session_id(TENANT, "okta", "102bFs0Aq6VQ1qjqVqk")
    assert first == second
    assert isinstance(first, uuid.UUID)

    # Namespaced by tenant and by source: two tenants may legitimately observe
    # the same vendor identifier, and an Okta session id and a GitHub token
    # hash share no namespace.
    assert session_id("22222222-2222-2222-2222-222222222222", "okta", "102bFs0Aq6VQ1qjqVqk") != first
    assert session_id(TENANT, "github", "102bFs0Aq6VQ1qjqVqk") != first


@pytest.mark.asyncio
async def test_an_unreachable_store_degrades_the_alert_and_does_not_block_it():
    """An alert without session context is degraded; an alert that never
    arrives because the session store was down is an outage."""
    conn = RecordingConn(fail=RuntimeError("connection refused"))
    store = SessionStore(RecordingPool(conn))

    assert await store.record_event(TENANT, event({"key": "s1", "key_kind": "vendor_session"})) is None


@pytest.mark.asyncio
async def test_only_derived_sessions_are_closed_on_an_idle_gap():
    """A vendor session ends when the vendor says so. Guessing on its behalf
    would report a session as over while it is still being used."""
    conn = RecordingConn()
    store = SessionStore(RecordingPool(conn))

    await store.close_idle(900)

    sql, args = conn.sql_containing("UPDATE sessions")
    assert "key_kind = 'derived'" in sql
    assert args[0] == 900.0


def test_the_closed_set_matches_the_migrations_check_constraint():
    """Three declarations of the same vocabulary — Go, this module, and the
    CHECK constraint — and nothing but a test keeps them equal."""
    sql = MIGRATION.read_text()
    match = re.search(r"key_kind IN \(([^)]*)\)", sql)
    assert match, "migration 102 no longer declares a CHECK on key_kind"
    in_sql = {value.strip().strip("'") for value in match.group(1).split(",") if value.strip()}
    assert in_sql == set(KEY_KINDS)


def test_the_upsert_widens_the_window_and_never_rewinds_it():
    """Kafka delivers out of order after a rebalance. A late event must widen
    the session's window, not move `last_seen_at` back before an event that
    has already been counted."""
    from app.services.sessions import _UPSERT_SQL

    assert "least(sessions.first_seen_at" in _UPSERT_SQL
    assert "greatest(sessions.last_seen_at" in _UPSERT_SQL
    assert "event_count   = sessions.event_count + 1" in _UPSERT_SQL


@pytest.mark.parametrize(
    ("raw", "expect_year"),
    [
        (1_760_000_000_000, 2025),  # OCSF milliseconds
        (1_760_000_000, 2025),  # seconds, which must not land in 1970
        ("2026-03-04T05:06:07Z", 2026),
        (None, datetime.now(UTC).year),
    ],
)
def test_event_time_handles_every_shape_the_spine_delivers(raw, expect_year):
    from app.services.sessions import _event_time

    payload = {"time": raw} if raw is not None else {}
    assert _event_time(payload).year == expect_year
