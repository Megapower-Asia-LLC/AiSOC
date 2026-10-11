#!/usr/bin/env python3
"""The MCP server has to be reachable over the network, and accountable on it.

Why this exists
---------------
``services/mcp`` shipped as a stdio child process and nothing deployed it. On
the pre-fix tree all four of these counted zero:

    grep -rn 'StreamableHTTP' services/mcp/src/            -> 0
    grep -rn 'aisoc-mcp' docker-compose.yml infra/helm/     -> 0
    grep -rn 'mcp_tool_grant' services/api/app/             -> 0
    grep -rn '"mcp:' services/api/app/                      -> 0

So the server existed, was unit-tested, and the only way to reach it was to
let an MCP host start it as a subprocess with one operator's API key baked
into the host's config file. That is the repository's recurring defect in its
network form: a working mechanism with no deployed path to it, and no account
of what it read once somebody found one.

Putting it on HTTP changes the threat model rather than only the transport.
Over stdio the credential is the operator's own and the blast radius is their
laptop. Over HTTP the credential arrives in the request, several tenants share
one process, and every tool call is a standing data-egress path into somebody
else's alerts and event lake. The rules below are the properties that have to
hold for that to be safe, each one a thing that was wrong before:

``transport``
    An HTTP transport exists at all.

``per-request-credential``
    The HTTP path never reaches for the process-wide ``AISOC_API_KEY``. The
    tenant must come from the credential the caller presented, never from the
    server's environment and never from an argument -- a server that falls
    back to its own key answers one tenant's question with another tenant's
    data. ``tenant-is-not-an-argument.test.ts`` already pins the argument
    half; this pins the environment half.

``gated``
    Every tool call is authorized by the API before dispatch and reported
    after. The MCP process is not the authority on what a key may do.

``audited``
    The API writes an audit row for the call, reads included. ``audit_log``
    is append-only and hash-chained, which is the point: a revoked key's
    history survives the revocation.

``approval``
    A tool that is not read-only cannot run on the strength of a key alone.
    The registry's own ``readOnlyHint`` decides, so adding a write tool opts
    it into approval automatically rather than by remembering to.

``catalogue-parity``
    The API's copy of the tool list matches the TypeScript registry, name for
    name and flag for flag. Without this the authority and the thing it
    authorises disagree about what a tool is, and the safe-looking direction
    of that drift -- the API not knowing a tool is a write -- is the one that
    matters.

``deployed``
    Named in ``docker-compose.yml`` and in the Helm chart. A transport nobody
    runs is the state this gate was written to end.

Usage:
    python3 scripts/check_mcp_over_http.py
    python3 scripts/check_mcp_over_http.py --self-test

Exit codes: 0 clean, 1 findings.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gate_toolkit import SELF_TEST_FLAG, repo_root, self_test_main  # noqa: E402

MCP_SRC = Path("services/mcp/src")
HTTP_MODULE = MCP_SRC / "http.ts"
GATE_MODULE = MCP_SRC / "gate.ts"
REGISTRY_MODULE = MCP_SRC / "tools" / "index.ts"
CATALOGUE = Path("services/api/app/data/mcp_tool_catalog.json")
POLICY_MODULE = Path("services/api/app/services/mcp_access.py")
ROUTES_MODULE = Path("services/api/app/api/v1/endpoints/mcp_access.py")
COMPOSE = Path("docker-compose.yml")
HELM_DIR = Path("infra/helm/aisoc")

#: The audit action the authorize path must write. Named here rather than
#: matched loosely so renaming it is a deliberate two-file change.
AUDIT_ACTION = "mcp:tool_call"


def _read(root: Path, rel: Path) -> str | None:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _tool_names_from_registry(source: str) -> set[str]:
    """Names a TypeScript tool module advertises, read from its metadata.

    Matches ``name: "aisoc_..."`` inside the ``metadata`` object literal. The
    registry file itself only imports, so callers pass the concatenation of
    every module under ``tools/``.
    """
    return set(re.findall(r'name:\s*"(aisoc_[a-z0-9_]+)"', source))


def _read_only_flags(source: str) -> dict[str, bool]:
    """Map every tool name in ``source`` to its ``readOnlyHint``.

    The annotation can be written on one line or spread over several, and
    both spellings are in the tree, so this scans forward from each name to
    the next name rather than trying to parse the object.
    """
    flags: dict[str, bool] = {}
    hits = list(re.finditer(r'name:\s*"(aisoc_[a-z0-9_]+)"', source))
    for index, hit in enumerate(hits):
        end = hits[index + 1].start() if index + 1 < len(hits) else len(source)
        block = source[hit.start() : end]
        match = re.search(r"readOnlyHint:\s*(true|false)", block)
        # An absent annotation is not a claim to be read-only, so the safe
        # reading -- and the one the MCP client already applies -- is False.
        flags[hit.group(1)] = bool(match) and match.group(1) == "true"
    return flags


def _registry_sources(root: Path) -> str:
    tools_dir = root / MCP_SRC / "tools"
    if not tools_dir.is_dir():
        return ""
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(tools_dir.glob("*.ts"))
        if path.name not in {"index.ts", "types.ts"}
    )


def violations(root: Path) -> list[str]:
    """Every property above that does not hold in the tree at ``root``."""
    found: list[str] = []

    http_src = _read(root, HTTP_MODULE)
    gate_src = _read(root, GATE_MODULE)

    # transport
    if http_src is None or "StreamableHTTPServerTransport" not in http_src:
        found.append(
            f"transport: {HTTP_MODULE} does not build a StreamableHTTPServerTransport, "
            "so the server is stdio-only and no MCP client can reach it over the network."
        )

    # per-request-credential
    if http_src is not None:
        if re.search(r"\b(cfg|config)\.apiKey\b", http_src):
            found.append(
                f"per-request-credential: {HTTP_MODULE} reads the process-wide API key. "
                "Over HTTP the credential must come from the request's Authorization header, "
                "or one tenant's question is answered with the server operator's access."
            )
        if "authorization" not in http_src.lower():
            found.append(
                f"per-request-credential: {HTTP_MODULE} never reads an Authorization header, "
                "so it cannot be deriving the caller's tenant from their credential."
            )

    # gated
    if gate_src is None:
        found.append(f"gated: {GATE_MODULE} is missing; nothing authorizes a tool call before it runs.")
    else:
        if "/mcp/tool-calls/authorize" not in gate_src:
            found.append(f"gated: {GATE_MODULE} never calls POST /mcp/tool-calls/authorize.")
        if "/complete" not in gate_src:
            found.append(f"gated: {GATE_MODULE} never reports a call's outcome back to the API.")
    if http_src is not None and gate_src is not None and "authorizeToolCall" not in http_src:
        found.append(
            f"gated: {HTTP_MODULE} does not call authorizeToolCall, so the gate module exists "
            "and the HTTP path does not use it -- which is the defect this phase is about."
        )

    # audited
    policy_src = _read(root, POLICY_MODULE)
    routes_src = _read(root, ROUTES_MODULE)
    if routes_src is None:
        found.append(f"audited: {ROUTES_MODULE} is missing; the API exposes no authorize route.")
    else:
        if "emit_audit" not in routes_src:
            found.append(f"audited: {ROUTES_MODULE} never calls emit_audit, so a tool call leaves no row.")
        if AUDIT_ACTION not in routes_src:
            found.append(f'audited: {ROUTES_MODULE} does not write the "{AUDIT_ACTION}" action.')

    # approval
    if policy_src is None:
        found.append(f"approval: {POLICY_MODULE} is missing; nothing decides whether a tool needs an approver.")
    elif "read_only" not in policy_src or "approval" not in policy_src:
        found.append(
            f"approval: {POLICY_MODULE} does not derive an approval requirement from the tool's "
            "read-only flag, so a write tool runs on a key alone."
        )

    # catalogue-parity
    registry_src = _registry_sources(root)
    catalogue_raw = _read(root, CATALOGUE)
    if catalogue_raw is None:
        found.append(f"catalogue-parity: {CATALOGUE} is missing; the API has no list of the tools it authorises.")
    elif registry_src:
        try:
            catalogue = json.loads(catalogue_raw)
        except json.JSONDecodeError as exc:
            found.append(f"catalogue-parity: {CATALOGUE} is not valid JSON ({exc}).")
        else:
            declared = {entry["name"]: bool(entry.get("read_only")) for entry in catalogue.get("tools", [])}
            registry = _read_only_flags(registry_src)
            # Only names the registry actually exports; `index.ts` decides
            # which modules are wired, and a module present but unimported is
            # a different defect with its own gate.
            exported = _tool_names_from_registry(_read(root, REGISTRY_MODULE) or "") or set(registry)
            registry = {k: v for k, v in registry.items() if k in exported or not exported}
            missing = sorted(set(registry) - set(declared))
            extra = sorted(set(declared) - set(registry))
            drifted = sorted(n for n in set(registry) & set(declared) if registry[n] != declared[n])
            if missing:
                found.append(
                    f"catalogue-parity: {CATALOGUE} does not know about {', '.join(missing)}. "
                    "An unknown tool is authorised by nothing."
                )
            if extra:
                found.append(f"catalogue-parity: {CATALOGUE} lists {', '.join(extra)}, which the registry does not export.")
            for name in drifted:
                found.append(
                    f"catalogue-parity: {name} is read_only={declared[name]} in {CATALOGUE} and "
                    f"readOnlyHint={registry[name]} in the registry."
                )

    # deployed
    compose_src = _read(root, COMPOSE)
    if compose_src is None or not re.search(r"^\s{2}mcp:", compose_src, re.MULTILINE):
        found.append(f"deployed: {COMPOSE} declares no `mcp` service, so nothing starts the HTTP transport.")
    helm_hit = False
    helm_dir = root / HELM_DIR
    if helm_dir.is_dir():
        for path in helm_dir.rglob("*.yaml"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if "mcp" in text.lower():
                helm_hit = True
                break
    if not helm_hit:
        found.append(f"deployed: nothing under {HELM_DIR} mentions the MCP service.")

    return found


def main() -> int:
    root = repo_root()
    if not (root / MCP_SRC).is_dir():
        print(
            f"check_mcp_over_http: {MCP_SRC} is absent -- refusing to report a clean tree",
            file=sys.stderr,
        )
        return 1

    problems = violations(root)
    if problems:
        print("The MCP server is not safely reachable over the network:\n", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(f"\n{len(problems)} problem(s).", file=sys.stderr)
        return 1

    print("check_mcp_over_http: OK — streamable HTTP, per-request credentials, authorized and audited per call, deployed in compose and Helm")
    return 0


# ---------------------------------------------------------------------------
# Self-test: one injected violation per rule, against a copy of the real tree.
# A self-test that only exercised hand-written fixtures would prove the regexes
# compile and nothing about whether they see this repository.
# ---------------------------------------------------------------------------


def _with_edit(root: Path, edits: dict[Path, str | None]) -> list[str]:
    """Run the rules over ``root`` with some files replaced or deleted.

    Done by reading and restoring rather than by copying the tree: the tree is
    13,000 files and the gate only reads eight of them.
    """
    saved: dict[Path, str | None] = {}
    for rel, new in edits.items():
        path = root / rel
        saved[rel] = path.read_text(encoding="utf-8") if path.exists() else None
        if new is None:
            if path.exists():
                path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new, encoding="utf-8")
    try:
        return violations(root)
    finally:
        for rel, old in saved.items():
            path = root / rel
            if old is None:
                if path.exists():
                    path.unlink()
            else:
                path.write_text(old, encoding="utf-8")


def _rule_self_test() -> list[tuple[str, bool]]:
    root = repo_root()
    checks: list[tuple[str, bool]] = [("the tree as committed is clean", not violations(root))]

    http_src = _read(root, HTTP_MODULE) or ""
    catalogue_raw = _read(root, CATALOGUE) or "{}"

    checks.append(
        (
            "removing the HTTP transport is reported",
            any("transport:" in v for v in _with_edit(root, {HTTP_MODULE: http_src.replace("StreamableHTTPServerTransport", "StdioServerTransport")})),
        )
    )
    checks.append(
        (
            "falling back to the process-wide API key is reported",
            any("per-request-credential:" in v for v in _with_edit(root, {HTTP_MODULE: http_src + "\nconst leaked = cfg.apiKey;\n"})),
        )
    )
    checks.append(
        (
            "skipping the authorize call is reported",
            any("gated:" in v for v in _with_edit(root, {HTTP_MODULE: http_src.replace("authorizeToolCall", "noopToolCall")})),
        )
    )
    checks.append(
        (
            "deleting the audit route is reported",
            any("audited:" in v for v in _with_edit(root, {ROUTES_MODULE: None})),
        )
    )
    checks.append(
        (
            "deleting the approval policy is reported",
            any("approval:" in v for v in _with_edit(root, {POLICY_MODULE: None})),
        )
    )
    try:
        catalogue = json.loads(catalogue_raw)
        flipped = json.loads(catalogue_raw)
        for entry in flipped.get("tools", []):
            if not entry.get("read_only"):
                entry["read_only"] = True
                break
        dropped = json.loads(catalogue_raw)
        dropped["tools"] = dropped.get("tools", [])[1:]
    except json.JSONDecodeError:
        catalogue = flipped = dropped = {"tools": []}
    checks.append(
        (
            "a write tool relabelled read-only in the catalogue is reported",
            catalogue != flipped
            and any("catalogue-parity:" in v for v in _with_edit(root, {CATALOGUE: json.dumps(flipped, indent=2)})),
        )
    )
    checks.append(
        (
            "a tool missing from the catalogue is reported",
            any("catalogue-parity:" in v for v in _with_edit(root, {CATALOGUE: json.dumps(dropped, indent=2)})),
        )
    )
    compose_src = _read(root, COMPOSE) or ""
    checks.append(
        (
            "removing the compose service is reported",
            any("deployed:" in v for v in _with_edit(root, {COMPOSE: compose_src.replace("\n  mcp:\n", "\n  mcp-disabled:\n")})),
        )
    )
    return checks


if __name__ == "__main__":
    if SELF_TEST_FLAG in sys.argv[1:]:
        sys.exit(self_test_main(Path(__file__).name, extra=_rule_self_test()))
    sys.exit(main())
