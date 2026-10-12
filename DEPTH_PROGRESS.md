# AiSOC depth plan: progress

Mirrors `plans/aisoc_depth_plan.plan.md`, which is locked and is the source of
truth. This file is the mutable half.

Legend: `[ ]` not started, `[~]` in progress, `[x]` done, `[!]` blocked (with
exactly what is needed).

An item is `[x]` only when all three of these are recorded against it: the test
or gate that failed on the pre-fix tree for the stated reason, the change, and
the negative control showing that reverting it fails again.

- **Base commit:** `1b8bc2d4` (`origin/main`, v17.1.0).
- **Plan captured at:** `90ea2fd`. Figures in the plan body are hints at that
  commit; Phase 0.2 below re-derives each one and the tree wins.

## Reconciliation, 2026-10-09

Eleven items had merged to `main` and every one still read `[ ]` here. The
tracker is the mutable half of a locked plan, so a tick that lags the tree
makes it describe a repository that no longer exists -- the same failure the
plan exists to catch, one level up.

Reconciled against the tree rather than against the pull requests: each item
below was confirmed by the artefact it was supposed to produce being present
on `main` (the corpus file, the OCSF decision table, the event catalogue
directory, the scorecard fields, the notify arms, the report scheduler, the
step bounds, the access-conditions routes, the security pack), not by a merged
title. Each carries the reproduce, change and negative control the legend
requires in its own pull request body.

| Item | Landed in | Confirmed by |
| --- | --- | --- |
| 1.1 | #1205 | `services/agents/tests/eval_data/verdict/verdict_corpus_v1.json` |
| 1.2 | #1191 | nine scorecard fields in `aisoc_benchmark/replay.py` |
| 1.3 | #1197 | `scripts/check_verdict_corpus.py`, `prompting/tool_results.py` |
| 2.1 | #1195 | `internal/normalizer/ocsf_classes.go` |
| 2.2 | #1204 | `scripts/check_activity_projection.py` |
| 2.3 | #1209 | `schemas/event_catalog/` |
| 5.1 | #1203 | `live_actions/notify_arms.py` |
| 5.2 | #1211 | `app/workers/report_scheduler.py` |
| 5.3 | #1207 | `app/playbook/bounds.py` |
| 8.2 | #1206 | `endpoints/access_conditions.py` |
| 8.3 | #1210 | `docs/security/` |

Not started: phases 3, 4, 6, 7, 9 and the whole of 10, and
2.4--2.7. Those remain `[ ]` and are not claimed here.

## Migration and ADR numbers claimed

Phases run in parallel lanes, so a number is claimed here **before** the file
is written. Next free at capture: migration `095`, ADR `0010`
(`docs/decisions/`, not `docs/adr/` -- the plan's wording; the directory is
`decisions/` and the highest is `0009-auto-close-without-an-earned-grant.md`).

| Number | Claimed by | Status |
|---|---|---|
| ADR `0010` | 2.7 — entity and session context in CORE | **landed**, `docs/decisions/0010-entity-and-session-context-in-core.md`, accepted |
| migration `102` | 2.4 — `102_sessions.sql` | claimed |
| migration `103` | 2.5 — `103_posture_snapshots.sql` | claimed |
| migration `104` | 9.1 — `104_mcp_access.sql` | claimed |
| migration `105` | 9.2 — `105_semantic_memory.sql` | claimed |
| migration `106` | 9.3 — `106_case_depth.sql` | claimed |
| migration `107` | 9.4 — `107_case_war_rooms.sql` | claimed |
| migration `108` | 9.5 — `108_hunt_reports.sql` | claimed |
| migration `109` | 9.6 — `109_push_devices.sql` | claimed |
| migration `110` | 8.1 — `110_console_webauthn.sql` | claimed |
| migration `111` | 8.1 — `111_audit_retention.sql` | claimed |
| migration `112` | 8.1 — released, taken by another lane (D12) | **struck** |
| migration `113` | 8.1 — `113_entitlement_enforcement.sql` | claimed |
| ADR `0011` | 8.1 — truncating a hash-chained audit log | claimed |

| migration `110` | 4.2 — `110_stream_inputs.sql` (Kafka customer topics, TAXII collections) | claimed |
| migration `111` | 4.3 — `111_lake_query_jobs.sql` (cold-query cost estimate and progress state) | claimed |
| migration `112` | 4.5 — `112_scheduler_leases.sql` (connector-scheduler leader election) | claimed |
| ADR `0011` | 4.4 — partitioning fusion by entity rather than by alert | claimed |

Highest migration on `main` at claim time was `101_audit_immutable_nullify.sql`,
so `095`--`101` were taken by sibling lanes between the capture above and this
claim; re-read `services/api/migrations/` rather than trusting the capture row.

Phase 9 re-read `services/api/migrations/` on 2026-10-11 before claiming:
`101_audit_immutable_nullify.sql` was still the highest on `main`, and `102`
and `103` were already spoken for in the table above, so Phase 9 takes `104`
through `109`, one per item. A number left unused at the end of the phase is
released by striking its row rather than by silently leaving a gap.

Item 8.1 re-read `services/api/migrations/` on 2026-10-11 before claiming:
`105_semantic_memory.sql` was the highest on `main`, and `102`--`109` were
already spoken for above, so 8.1 takes `110`--`112` and ADR `0011`. The three
sub-items that need no schema — the containerised-IdP CI leg,
internationalisation and accessibility — claim no number. The same release
rule applies: an unused number is struck, not silently skipped.

Phase 4 (items 4.2--4.5) re-read the directory on 2026-10-11 immediately
before claiming: `101_audit_immutable_nullify.sql` is still the highest file
on `main`, `102`--`109` are spoken for above, so this lane takes `110`--`112`
and ADR `0011`. The numbers are claimed before any file is written, because
two lanes recently picked `102`/`103` within minutes of each other and one
had to renumber. Unused numbers are struck at the end of the phase.

## Phase 0: Kickoff

- [x] **0.1** `DEPTH_PROGRESS.md` exists (this file), modelled on
  `PARITY_PROGRESS.md`.
- [x] **0.2** Every figure re-derived against the base commit. See below.
- [~] **0.3** Baselines captured. Four of five recorded; `make up-full` and the
  hosted-model matrix are noted under Deviations.

### 0.2 Re-derived figures

Measured on `1b8bc2d4`, 2026-10-07, each by the generator or gate the plan
names. Where the captured and measured values differ, **the measured value is
the one later phases are graded against**.

| Figure | Captured in plan | Measured | Note |
|---|---|---|---|
| Executable detections | 2,603 | **2,603** | `generate_corpus_stats.py --check` |
| On disk | 6,991 | **6,991** | same |
| Quarantined | — | **4,388** | same |
| Unreachable native rules | 119 | **119** | `check_detection_fields.py`; `MAX_UNREACHABLE = 119` |
| … needing a windowed evaluator | 74 | **74** | the family Phase 3.1 translates |
| … identity enrichment | 24 | **24** | Phase 3.3 |
| … fields nothing emits | 8 | **8** | Phase 3.3 |
| … first-seen / age | 8 | **8** | Phase 3.3 |
| … other | 6 | **6** | |
| … behavioural baseline | 2 | **2** | Phase 3.4 |
| Windowed rules | 18 | **18** | `services/fusion/app/data/windowed_ruleset.json` |
| Executor arms | 73 | **74** | classes declaring `capability = "…"` under `services/actions/app/live_actions/`. **33 distinct capability verbs.** Phase 5.5 counts arms, so its target is measured from 74 |
| Claim-to-gate matrix | 290 rows, all GATED | **290 rows, 290 GATED, 0 PARTIAL, 0 NO GATE** | `check_claim_gate_matrix.py` |
| CORE / full services | 16 / 22 | **16 / 22** | `check_profile_service_counts.py` (production stack: 16 / 21) |
| Next migration | 095 | **095** | highest is `094_user_delete_fk.sql` |
| Next ADR | 0010 | **0010** | in `docs/decisions/`, highest `0009` |

**Cloud, identity, SaaS and code executable rules: captured 461, measured
395.** The gap is a definition the plan does not pin, not a change in the
tree, so it is recorded here rather than reconciled silently. Measured by
`log_source` on executable entries in `marketplace/index.json`, grouping:

| Group | Count | `log_source` values counted |
|---|---|---|
| cloud | 225 | aws 76, azure 50, gcp 40, kubernetes 36, docker 10, cloud 8, multi-cloud 5 |
| identity | 123 | identity 47, okta 35, active-directory 22, auth0 5, duo 5, ping 5, keycloak 4 |
| saas | 34 | google-workspace 8, m365 7, slack 6, email 3, salesforce 3, + 7 others |
| code | 13 | github 12, gitlab 1 |
| **total** | **395** | |

Phase 3.6 must therefore raise **395 → 800** and ship the `make stats` line
with a `--check` gate that fixes this grouping in code, so the figure stops
being re-derivable two ways.

**Two measurement caveats found while re-deriving, both worth carrying:**

1. **1,724 of the 2,603 executable rules live under
   `detections/sigma-imports/_quarantine/`.** "Executable" and "quarantined"
   overlap, because the Sigma compiler began translating rules in place
   without moving them. Any later statement of the form "N executable rules"
   must not be read as "N rules outside quarantine".
2. **The plan's "1,798 of 2,603 are Windows (69%)" does not reproduce from
   the index.** Only 111 executable entries carry `log_source: windows`, and
   218 are Windows by path or log source (8%). The 1,770 Sigma imports carry
   **no `log_source` at all**, which is where the difference lives: the
   captured figure counted the Sigma corpus as Windows, which is
   approximately but not exactly true. Phase 3.6's gate should classify by a
   field that exists rather than by corpus membership.

### 0.3 Baseline artefacts

Hardware: Apple M5 Max, 18 cores, 128 GiB host; Docker 29.5.2 in a 6-CPU /
15.6 GiB Linux VM. Date 2026-10-07. Commit `1b8bc2d4`.

| Baseline | Result | Artefact |
|---|---|---|
| `make up` (CORE) | **PASS** -- 16 services healthy, administrator created | — |
| `make smoke` | **PASS 10/10 stages** -- event traversed ingest → Kafka → fusion → alert, severity and source attribution survived | — |
| Behavioural injection suite | **19 passed.** Overall flip rate **0.2593**, unsafe-action rate **0.037** over 27 cases | `services/agents/tests/eval_data/behavioural_injection.json` |
| Live-agent model matrix | **0 of 2 models measured** -- "no live LLM key configured", reported as *not measured* rather than zeros | — |
| Load harness, 20,000 events | **pipeline 130.3 alerts/s**, ingest accepted 397.6 events/s, p50 **54.9 s**, p95 **100.2 s**, p99 103.9 s, delivery ratio **1.0**, duplicates **0**, dead letters **0** | `docs/perf/results/2026-10-07-compose-depth-baseline.json` |

Per-family injection flip rates at baseline, from the artefact above:

| Family | Cases | Flip rate | Guard catch rate |
|---|---|---|---|
| command_line | 4 | 0.25 | 0.75 |
| email_subject | 3 | 0.3333 | 0.6667 |
| fake_analyst_note | 2 | 0.0 | 1.0 |
| **fake_tool_output** | — | **1.0** | **0.0** |
| file_path, process_name, url, username | — | 0.0 | — |
| persona | — | 0.67 | — |

`fake_tool_output` at 1.0 flip / 0.0 catch is the figure Phase 1.3 must bring
to **at or below 0.10 on tuned *and* held-out payloads**.

The load-harness row is the "before" for Phase 4.4, whose target is a
sustained 5,000 events/s at p95 under 2 s on documented cloud hardware. The
measured p95 of 100 s is a *drain* latency under a 20,000-event burst on a
6-CPU laptop VM, not a steady-state figure, and must be labelled that way
wherever it is quoted.

## Deviations

Recorded as they happen. A deviation is not a failure; an unrecorded one is.

### D1 -- The load harness could not run from a clean checkout (fixed here)

`scripts/perf/load_harness.py` invoked `go run ./services/demo-producer` with
`cwd=` the repository root. There is no `go.mod` at the root -- the producer
is its own module at `services/demo-producer/go.mod` -- so the subprocess
failed before starting:

```
producer failed (1): go: go.mod file not found in current directory or any
parent directory; see 'go help modules'
```

The harness has therefore never produced a run on the path it documents; the
published laptop figures must have come from a prebuilt `--producer-bin`,
which needs no module context. Fixed in the Phase 0 commit by running `go run
.` from the producer's own directory, which is what produced the baseline
above. Phase 4.4 extends this harness and inherits the fix.

### D2 -- `make up-full` not captured on this host

Deferred rather than claimed. The `full` profile is 22 services at ~12 GiB
against a 15.6 GiB VM that is already running the 16 CORE services, and a
baseline taken under memory pressure would describe the host rather than the
stack. Recorded as unmeasured; Phase 4.5 (`helm install` brings up all of
CORE) and Phase 3.4 (baselines in CORE) are the items that need it, and both
will re-take it on a sized host.

### D3 -- Hosted model rows are maintainer-blocked (M2)

`scripts/run_model_matrix.py` reports **0 of 2 models measured** with "no live
LLM key configured". This is the gate behaving correctly: it refuses to
publish `0.000` where it means "not measured". Phase 1.4 has since measured
two local candidates, which need no key: see the verdict-quality table on the
benchmark page and the 1.4 note below. The hosted rows stay `[!]` until the
maintainer funds a key, and still read "not measured" rather than zero.

### D4 -- Not all 74 "windowed" rules need a window

The reachability gate attributes a rule to the windowed family by matching
its field names against `_count$|^count_|_per_|time_window|_window_|_5min|_ratio$`.
Eight of the 74 are per-event properties the pattern misreads: `row_count` is
the size of one export record, `answer_count` the number of records in one DNS
response, `insecure_registries_count` the length of a list in one daemon
config event, `subdomain_hex_ratio` a property of one query name, and
`active_keys_per_account` the state of an account at one moment. They are
refused under the `not-windowed` kind rather than translated, and the family
label in `check_detection_fields.py` is left as it is: changing the classifier
would move the published family counts that Phase 0.2 recorded, for no gain
now that each rule carries an individual reason.

### D5 -- Five windowed rules that predate this work group by a field nothing emits

`wd-secret-enumeration` (`distinct_by=secret_name`), `wd-windows-password-spray`,
`wd-sysmon-remote-thread-fanout`, `wd-sysmon-dns-query-fanout` and
`wd-sysmon-process-spawn-burst` name entity fields outside the statically
recovered namespace. Four of the five are Windows `EventData` keys the
`windows_event` connector lifts wholesale, so the namespace under-approximates
and the rules are probably fine; `secret_name` has no such explanation. The
new gate **reports** these rather than failing on them, because failing would
be a false alarm about working rules, and the entity question is answered by
replay rather than by a name lookup. Not fixed here: changing a shipped
rule's `group_by` is a content decision with its own blast radius.

### D6 -- The windowed engine ran a narrower field namespace than the stateless one

`WindowedDetectionEngine._fields` carried a docstring saying it matched the
stateless engine's namespace "exactly". It did not: the stateless engine then
applies `derived_fields.enrich()` and the per-tenant allowlist overlay, and
the windowed engine applied neither. Two of the rules translated here carry an
`<x>_in_allowlist` clause, so without fixing this they would have moved from
one engine that could not fire them to another. Both passes are now applied in
`evaluate()`, which takes the overlay the consumer had already resolved for
the stateless engine.

### D7 -- There is no "existing watermark" in fusion to order sequences by

Item 3.2 says to order sequences "by event time with the existing
watermark". No watermark exists anywhere in the detection path: the only two
in the tree belong to `services/actions`' shadow-reconcile router and the
dead-letter replay, which are unrelated subsystems. Rather than invent one or
quietly order by arrival, the engine orders strictly by event time and
declares its own bound,
`SEQUENCE_REORDER_TOLERANCE_SECONDS = 300`, for how late an event may arrive
and still be stitched into a sequence. The bound is stated in the module
rather than inherited from something that does not exist.

Ordering by arrival would have been the easy implementation and is wrong
here: almost every connector in this tree **polls**, so a batch arrives in
the vendor's order and the event that starts a sequence routinely lands after
the one that finishes it. `test_a_batch_delivered_out_of_arrival_order_still_fires`
is the regression test for that, and reverting the event-time read makes it
and two others fail.

### D11 -- Semantic recall measured *worse* than the full-text baseline on every embedding backend reachable from here

Parity 6.5 asks for the accuracy delta. It is measured, by
`scripts/score_memory_recall.py` over 12 hand-authored probes against a
12-item corpus, and the delta is negative:

| metric | lexical | semantic (`qwen2.5:0.5b`) | delta |
|---|---|---|---|
| recall@1 | 0.667 | 0.333 | **-0.333** |
| recall@3 | 0.750 | 0.417 | **-0.333** |
| recall@5 | 0.750 | 0.667 | -0.083 |
| MRR | 0.708 | 0.465 | **-0.243** |

The honest reading is not "semantic recall does not work". It is that
**no embedding model is reachable from this project without a funded key**.
The two models served locally are *generative* models used as embedders,
which is a known-poor substitute; `nomic-embed-text` was attempted and the
pull did not complete in ten minutes. Hosted embedding rows are blocked by
the same thing as D3 (maintainer item M2).

Three things follow, and all three are in the tree rather than in this note:

1. **The default did not move.** `POST /kb/query` stays full-text; semantic
   recall is `recall_memory: false` and strictly additive, so a caller that
   does not ask for it gets byte-identical behaviour. Putting a measurably
   worse retriever in front of the ranker would have made analyst search
   worse on exactly the deployments that cannot pay for an embedding model.
   The field's docstring carries the number and says to move the default when
   the measurement does.
2. **The measurement found a real defect in the first implementation.** The
   3,072-dimension model initially scored 0.167 at recall@1 — and that was
   measuring `_fit()` *truncating* the vector to the collection's 1,536, not
   measuring the model. Padding a short vector is harmless under cosine;
   truncating a long one discards most of what the model said. Truncation is
   now refused with a message naming both dimensions, which is a
   configuration an operator can fix rather than a silently worse retriever
   they cannot see.
3. **What is still not measured, stated plainly:** the downstream effect of
   memory recall on *verdict* quality, which is what the Phase 1 scorecard
   grades. That needs an agent run per corpus item against a model worth
   grading, and no such model is funded or locally servable here. The
   retrieval delta above is the part that can be measured honestly today,
   and it is the part that is actually about what 9.2 builds.

### D12 -- Migration `112` was claimed here and taken by another lane first

The claim table above reserved `110`--`112` for 8.1 after re-reading
`services/api/migrations/` against `main`, which is the documented procedure
and was not enough. Sequentially-numbered migrations are a **first-come
namespace across branches, not across `main`**: by the time 8.1 came to write
its third file, `112_scheduler_leases.sql` existed on another lane's pushed
branch. `110` and `111` had three and three other claimants respectively and
survived only because this item pushed first.

Re-derived immediately before committing by scanning the migration directory
of **all 259 remote branches**, not just `main`, which put the first free
number at `113`. The `112` row is struck rather than silently reused, per the
release rule at the top of that table.

The general lesson is that "re-read `main` before claiming" understates the
problem. `main` is the one place a number cannot yet be taken.

### D13 -- Two honest gates disagreed about the claim matrix, and the older one was wrong

`scripts/check_claim_gate_matrix.py` read the matrix as 300 GATED / 2 PARTIAL
while `readme_gates._matrix_counts` read 299 / 3, so the summary block was
reported as stale against a table that was correct.

`readme_gates` classified a row by scanning the **whole line** for `NO GATE`,
then `PARTIAL`, then `GATED`. A row's Notes cell is prose, so the first GATED
row to record *why* it had been PARTIAL -- which is exactly what a row should
say when a gate is built and the status earned -- counted as PARTIAL.

The cheap fix was to reword the row and lose the history. It now reads the
cell the column header names, refuses a table whose Status column cannot be
located rather than counting it as empty, and both properties are pinned by
tests that fail against the previous parser.

### D14 -- 4.6 is not started, and 4.5 is half done. Neither is claimed

Stated plainly rather than folded into a tick.

**4.6 internationalisation** (gap-closure 13.4) is **not started**. It asks
for a Next.js i18n library, externalised strings on five surfaces, a locale
switcher, RTL, locale-aware dates and numbers, a pilot locale and a CI gate
for missing and unused keys. Nothing of it exists: there is no `i18n`
directory, no message catalogue and no i18n dependency in `apps/web`. It is
the one sub-item of 8.1 with no code behind it, and the honest record is a
`[ ]`, not a partial credit for the parts that are easy.

**4.5** asks for two things. The opt-in limit enforcement the depth plan
names by file is built, wired to two routes and gated (#1332). The **six
console pages** -- branding, SCIM tokens, retention, organisation members and
grants, rule packs, delegations -- are not. Its claim row says so in the row
itself rather than relying on this note, because a reader of the matrix does
not read this file.

Neither is blocking 8.1's stated "Done when": a CI test signs in through OIDC
and SAML with MFA enforced for the role, an elevation expires on schedule
(8.2, merged), and the security pack passes the competitor-name and
comment-path gates. All three hold. The item is `[~]` rather than `[x]`
because the spec lists more than its own done-when.

### D8 -- No upstream Sigma correlation rule exists in this tree to import

`detections/sigma-imports/` holds 3,132 rule documents and **not one carries
a `correlation:` block**, so the missing importer and the missing corpus hid
each other: there was nothing for an importer to have failed on. There is
also no fetcher for the upstream corpus (`scripts/` has `compile_sigma_ruleset.py`,
`sigma_compiler.py` and `sigma_proof_event.py`, none of which downloads
anything).

So the importer is built and exercised against **first-party** correlation
documents hand-authored in the upstream format under
`detections/sigma-correlations/`, four accepted and two refused. The figure
they contribute is first-party content and is labelled that way in the truth
table and in the corpus README; it is not imported coverage. Vendoring the
upstream correlation corpus needs a fetcher and a licence review, and is not
attempted here.

One standard is weaker here than for the stateless Sigma imports, and stays
weaker: those are replayed through the real connector `normalize()` by an
out-of-process worker, and these are replayed through the real **windowed
engine** only. The connector step is not applied, because importing
`services/connectors` into a fusion test process shadows fusion's own `app`
package — the documented reason `compile_sigma_ruleset.py` uses a subprocess.
Instead, every selector field, `group-by` and `distinct_by` is checked
against the emitted-field namespace with **no ceiling**, which caught three
invented fields on the first run of the gate.

## Phase 1: Verdict quality you can publish

- [x] **1.1** Balanced, labelled verdict corpus
- [x] **1.2** Scorecard: balanced accuracy, MCC, per-class precision/recall,
  Wilson interval, false negatives, auto-close precision, escalation rate,
  time to verdict
- [x] **1.3** Close `fake_tool_output` structurally (≤ 0.10 tuned and held-out)
- [x] **1.4** A 7--8B local model in the matrix, chosen by score
- [x] **1.5** `make replay-eval` design-partner kit
- [x] **1.6** Published "Verdict quality" table with a `--check` drift gate

### 1.4 -- five local models measured; the winner is generation, not size

All five graded the same corpus digest through the production triage path,
72 model calls each, zero provider errors.

| Model | Balanced acc. | MCC | Malicious recall | Malicious prec. | ECE | Auto-close prec. |
|---|---|---|---|---|---|---|
| `llama3.1:8b-instruct-q4_K_M` | **0.357** | **0.209** | 0.583 / 36 | **0.724** | **0.349** | 0.111 (9) |
| `llama3.2:3b-instruct-q4_K_M` (CPU default) | 0.285 | 0.047 | 0.250 / 36 | 0.500 | 0.442 | 0.571 (7) |
| `llama3:8b` | 0.279 | 0.113 | **0.639** / 36 | 0.657 | 0.421 | 0.091 (11) |
| `qwen2.5:7b-instruct-q4_K_M` | 0.260 | 0.032 | 0.083 / 36 | 0.750 | 0.594 | 0.243 (37) |
| `mistral:7b-instruct-v0.3-q4_K_M` | 0.210 | 0.202 | **0.639** / 36 | 0.657 | 0.366 | 0.143 (14) |

Four classes: a constant answer scores **0.250** balanced accuracy, and
always guessing the majority class scores **0.500** plain accuracy.

**Decision, strictly by balanced accuracy:** `llama3.1:8b-instruct-q4_K_M`
becomes the default on `docker-compose.gpu.yml` and
`docker-compose.host-llm.yml`. It also leads on MCC, malicious precision and
calibration, and is the only row with ECE below 0.40. The 3B stays the
default for CPU `make up`, where a ~5 GB model does not fit the 8 GB CORE
budget -- a deployment constraint, not a score.

**Size is the wrong unit.** The previous-generation `llama3:8b` scores
*below* the 3B it would replace, so "upgrade to an 8B" is not advice that
survives measurement. An earlier revision of this file recorded exactly that
conclusion from `llama3:8b` alone and was wrong; the LiteLLM config's hint
now carries all five numbers instead.

**Two findings outrank the ranking.** Every model measured is far closer to
chance than to useful -- the best is 0.357 against a 0.250 floor, and three
of five fall below the 0.500 plain accuracy of guessing the majority class.
And auto-close precision is poor across the board (0.091-0.571 on 7-37
candidates), so **nothing measured here supports autonomous closure**. That
is a finding about the auto-close gate, not about which model to pick.

Caveats published rather than smoothed over:

- **Latency is excluded from the comparison.** The 3B ran CPU-bound inside
  the stack container and the four 7--8B rows GPU-accelerated on the host,
  so the figures measure different machines. All are still printed.
- **Per-decision model attribution is unverified.** Every call was placed
  and answered -- each decision carries reasoning specific to its alert --
  but `resolved_models` came back empty on every run, so the scorecard shows
  that 72 calls happened and not which model served each.
- **Auto-close precision rests on 7 to 37 candidates.** Small denominators;
  read the column as a warning sign, not a ranking.

**Writing the winner into the GPU overlay broke the GPU overlay, and CI
caught it.** Adding the model default left the
`deploy.resources.reservations.devices` block nested under `litellm`
instead of `ollama`. The file still parsed, `docker compose config` still
resolved, and `make up-gpu` would still have come up -- with the card
reserved by a proxy that runs no inference while generation fell back to
the CPU. There is no error anywhere in that sequence, which is why the
existing `test_it_touches_only_ollama` was the only thing between it and a
release.

Its companion assertion failed for a legitimate reason at the same time:
the overlay now *must* touch three services, since the measured default
needs a pull instruction on `ollama-pull` and routing on `litellm`. The
assertion was re-expressed rather than relaxed, and two properties added --
a device reserved on any service but `ollama` fails, and the model pulled
must be the model routed to. That second one guards the quiet failure: the
gateway 404s on a model nothing pulled, triage swallows it into the
deterministic fallback, and the stack looks healthy while measuring no
model at all. Each was proven by injecting the defect it names.

### 1.5 -- run end to end against a live stack, not a mock

`make replay-eval` / `make replay-eval-verify` drove a real run through the
API against a mocked Splunk ES holding 200 recorded closed notables: 200
read, 60 replayed in the test window, 240 production writes intercepted, a
signed bundle written and verified, and a wrong key refused with exit 1.

The live run is what found the three defects the unit tests could not: the
decisions route answers a bare array and the kit assumed an envelope; a
machine named only in the agent's reasoning survived redaction; and the
prose and identifier passes named their counter namespace in different
cases, so one host could take two tokens. All three are fixed with
regression tests, each proven to fail against the pre-fix tree.

Known gap: the run abstained on all 60 decisions because the stack's triage
reached no model, so the kit has been exercised on a deterministic run end
to end but **not yet on a run with real model verdicts in it**.

### 1.6 -- the section it replaced was wrong, not merely stale

`apps/docs/docs/benchmark.md` said verdict accuracy was not measured here
and could not be. Item 1.1's corpus made that false. The reasoning is kept
(it is why `score_replay_set.py` still refuses this tree's two all-malicious
corpora) and the conclusion is replaced by the measurement.

`scripts/check_verdict_quality.py --check` is wired into `ci.yml` and fails
on drift between the committed scorecard and the published block, proven by
reverting a number and watching it red. It also refuses five scorecard
shapes that would each publish a score-shaped cell with no measurement
behind it -- the load-bearing one being a row claiming a live measurement
that placed zero model calls, which is precisely what a run against a dead
endpoint produces once triage falls through to its deterministic scorer.

## Phase 2: A semantic layer and live posture

- [x] **2.1** OCSF classes beyond five
- [x] **2.2** Activity projection on every event
- [x] **2.3** Event classification catalogue
- [ ] **2.4** Sessions per principal
- [ ] **2.5** `__posture_snapshot__` collectors (AWS, Azure, GCP, Workspace, GitHub)
- [ ] **2.6** Use the posture everywhere
- [ ] **2.7** Entity context in CORE (ADR first)

## Phase 3: Detection depth for cloud, identity and SaaS

- [x] **3.1** Translate the 74 windowed `det-*` rules — 50 translated, 24
  refused with a reason. `MAX_UNREACHABLE` 119 → 45.
- [x] **3.2** Ordered sequences and Sigma correlations — the windowed engine
  stages ordered and unordered sequences; all four translatable Sigma
- [ ] **3.2** Ordered sequences and Sigma correlations
- [ ] **3.3** Enrichment inputs (parity 5.5)
- [ ] **3.4** Behavioural baselines in CORE
- [ ] **3.5** Threat-and-anomaly condition rules
- [ ] **3.6** 395 → at least 800 cloud, identity, SaaS and code conditions
- [ ] **3.7** Detection engineering agent (gap-closure Phase 9 / parity 6.2)

## Phase 4: Collection and scale

- [ ] **4.1** Cloud-native collection (S3+SQS org trail, Pub/Sub, Event Hubs)
- [x] **4.2** Standard inputs (syslog, OTLP, Kafka, TAXII 2.1). **All four
  bullets closed.** The syslog bullet landed earlier (its entry is below
  and is unchanged); the three that were open are done here.

  **OTLP logs.** `POST /v1/logs` in `services/ingest/internal/otlp`,
  reading `ExportLogsServiceRequest` in both encodings the specification
  defines and gzip bodies, because real collectors emit both and a
  receiver that reads one of them is a receiver half the estates cannot
  use. The path is not ours to choose: an exporter appends `/v1/logs` to
  its endpoint. The partial-success contract is implemented rather than
  skipped — a partly unprojectable batch answers 200 with
  `rejected_log_records`, and a publish failure answers 503 with
  `Retry-After`, because a blanket 200 tells the collector records it
  never delivered have landed and a 400 makes it discard them.

  **Kafka input.** `services/ingest/internal/kafkainput`, one source per
  tenant, the tenant from a minted token and from nothing in the record.
  The failure handling is the whole of it, and it is the shared
  `streamhealth` table rather than a second copy: a rebalance is
  transient and the loop continues, a `TopicAuthorizationFailed` stops it
  naming the operator action, and an undecodable record is poison —
  skipped *and* committed, because a poison record that is not committed
  is re-read forever. A publish failure is the one case that must not
  commit, Kafka being the only input here that can withhold an
  acknowledgement.

  **TAXII 2.1.** A real server at `/api/v1/taxii2/` over
  `threat_intel_iocs` (migration `110`), serving discovery, API root,
  collections, objects, manifest and `added_after` pagination. A
  collection is a filtered view, never a copy. The API root is a fixed
  string because a tenant in the path is a segment any caller can retype,
  on an endpoint whose purpose is to be pointed at by a third party.
  Writes are refused with a 403 that names the posture.

  **The refactor that came first**, because it decides whether the Kafka
  input is a second copy of a table or a second user of one: the
  permanent/transient/poison classifier, the stuck-after escalation and
  the kafka-go reader-error bridge were private to `graph_ws`. They moved
  to `services/ingest/internal/streamhealth`, parameterised by the two
  genuinely per-subsystem things — the published metric stem, which keeps
  its name, and the environment variables the advice tells an operator to
  edit. `graph_ws` keeps its API through aliases and its 555-line test
  passes unchanged.

  Gated by `scripts/check_standard_inputs.py` (self-test: nineteen
  injected violations, one per rule, plus a refusal on both an absent and
  an empty tree) wired into `ci.yml :: python-lint`, and by
  `taxii-live.yml` against real Postgres. **49 new Go tests** (27 OTLP,
  22 Kafka input), **37 Python projection tests**, **15 live TAXII
  tests**. Three claim rows added; the matrix reads 305 rows, 302 GATED.

  **Four defects found by writing this, recorded rather than quietly
  fixed.** A well-formed empty OTLP batch answered 400, because an
  `ExportLogsServiceRequest` with no fields set encodes to zero protobuf
  bytes and the body reader called that unreadable. The partial-success
  path had no reachable trigger, so the contract was a mechanism with no
  caller; a record carrying nothing of its own is now refused and
  counted. `otlp-logs` was absent from `ALLOWED_TEMPLATE_IDS`, so no
  operator could mint a token the receiver accepts — the receiver, its
  route, its template and its readiness entry were all correct and the
  feature was unusable. And the gate's own media-type rule matched the
  error message that names JSON rather than the case arm that accepts it,
  so a receiver that had stopped reading JSON entirely passed.

  **Three verification gaps, stated rather than implied.** No live
  OpenTelemetry Collector, no live Kafka broker and no third-party TAXII
  client has been exercised against any of this. The OTLP bodies are
  built with the vendor's own protobuf types, the Kafka loop is driven
  through a scripted reader so what is proven is the failure handling
  rather than kafka-go's wire protocol, and TAXII conformance is asserted
  against the specification's shapes rather than against a client's
  behaviour.

  **One thing found and left.**
  `GET /api/v1/threatintel/stix/taxii/collections` is a demo-gated stub
  returning a fixed sample list under the description "TAXII 2.1
  collections for server compatibility". Removing a published operation
  is a breaking OpenAPI change, so it stays; its docstring now says
  plainly that it is not the server, and so does the new page.
- [~] **4.2 (historical)** The syslog bullet, closed earlier. `services/ingest`
  accepts UDP and TCP and reads RFC 5424, RFC 3164, CEF and LEEF, with the
  tenant taken from a minted token because syslog carries nothing a sender
  does not control. Gated by `scripts/check_syslog_listener.py` (self-test:
  one injected violation per rule, including each of the three Go syntaxes
  a tenant could leak through) wired into `ci.yml :: python-lint`. 33 new
  Go tests. At the time this was written three bullets were open and were
  named here rather than left to be inferred: an OTLP logs receiver, a
  Kafka input for customer topics, and a TAXII 2.1 server over the tenant
  IOC store. All three are now closed; see the `[x]` entry above. This
  paragraph is kept as the record of what the syslog bullet alone
  covered, not as a live statement of what is missing.
- [x] **4.1** Cloud-native collection (S3+SQS org trail, Pub/Sub, Event Hubs).
  Three connectors (`aws_cloudtrail_s3`, `gcp_pubsub`, `azure_event_hubs`),
  each resumable and each declaring a bounded `collection_budget` that says
  where the overflow goes. Gated by
  `scripts/check_cloud_native_collection.py` (self-test: one injected
  violation per rule, plus a refusal on both an absent and an empty tree),
  wired into `ci.yml :: python-lint`. 83 new tests, connectors suite 1014 ->
  1098. **One verification gap, stated rather than buried:** no Azure
  subscription is reachable from here, so the Event Hubs capture fixture was
  synthesised from the Avro specification rather than recorded from a live
  hub, and the Data Lake Gen2 listing path has never run against a real
  storage account. The claim row is `PARTIAL` for exactly that reason.
- [ ] **4.2** Standard inputs (syslog, OTLP, Kafka, TAXII 2.1)
- [x] **4.3** Retention the tenant chooses. **All three bullets
  closed.** The lake TTL is now a 400-day ceiling rather than a fixed 90
  days, in `001_init.sql`, in the tiering DELETE and in a `MODIFY TTL`
  migration so an existing volume converges; `MAX_LAKE_DAYS` bounds what a
  tenant may choose and the three numbers are held equal. Legal hold now
  blocks the purge, through `may_purge` so the decision has one home, with
  unreadable hold evidence withholding rather than proceeding, and the run
  reporting what it withheld. Gated by
  `scripts/check_retention_window.py` (self-test: eight injected
  violations, one per rule) wired into `ci.yml :: python-lint`. 13 new
  tests, api suite 4,569 -> 4,582.

  **The third bullet is now closed too.** `/lake/sql`'s `cost` was the
  rate limiter's token price — a number about how often you may ask, not
  about how much the asking will read — and there was no progress state
  at all: a cold query either returned inside the published 30-second
  bound or raised a bare timeout.

  Every figure in the new estimate is ClickHouse's own: rows and parts
  from `EXPLAIN ESTIMATE`, the warm/cold split from `system.parts`
  joined to the storage policy's volumes (a part is cold because the
  server says it is on the cold volume, not because of its age — those
  disagree whenever a move is in flight), and progress from
  `system.processes` keyed on a query id we set. There is deliberately
  **no invented throughput constant**: a predicted duration needs a
  bytes-per-second figure and the only honest source is a measurement on
  the deployment's own hardware, so the routing rule is structural — a
  query goes to a job when the estimate says it must read the cold
  volume.

  `estimated_usd` is **null** unless the deployment configures
  `AISOC_LAKE_COLD_RETRIEVAL_USD_PER_GB`.
  `docs/decisions/storage-cost-model.json` prices residency, not reads;
  quoting it for a scan would be the wrong number stated confidently.
  `null` means "we do not know what this costs" and `0.0` means "this
  costs nothing", and a test pins that they are never confused.

  Jobs are rows (migration `111`), not an in-process registry: the API
  runs more than one replica, and that shape has been shipped and
  regretted three times here. 26 pure tests, 12 live ones against real
  Postgres, eight new rules in `check_retention_window.py`, and
  `lake-query-jobs-live.yml`.

  **The test that had to be rewritten, because the first one proved
  nothing.** The claim race originally gathered five concurrent claims
  and asserted one winner — and it passed under a SELECT-then-UPDATE
  implementation as well, measured by subverting the claim and watching
  it stay green. It is now two explicitly interleaved transactions, and
  that version goes red when the predicate is removed.

  **Two of the eight new gate rules were wrong in the same direction**
  and were caught by their own injections: the terminal-state rule
  matched a status string `list_stuck_jobs` legitimately also uses, and
  the routing rule matched a response *field name* rather than the
  branch, so an endpoint that reports `touches_cold` and ignores it
  passed.

  **Not measured, and why: no ClickHouse was exercised.** There is none
  in CI and none on the machine this was written on, so `EXPLAIN
  ESTIMATE`, the `system.parts` join and the `system.processes` read are
  asserted against ClickHouse's documented shapes with the parsing
  tested on recorded rows. What is proven live is the job lifecycle,
  which is where the concurrency defects are.

  **Two limits on what is closed**, recorded rather than left to be found:
  the lake half is gated statically — no test in CI watches a row survive
  past day 90 on a real ClickHouse, so what is proven is that the numbers
  agree and the migration exists; and a hold stops the whole tenant's sweep
  rather than only its own subjects, because both purges are bulk
  statements. Narrowing that needs a per-subject predicate on each store
  and is follow-up.
- [~] **4.4** Throughput (parity 6.9) and a cloud-hardware run. **Every
  parity 6.9 bullet is closed; the cloud-hardware run is not, and cannot
  be from here.**

  **Rules indexed — on required fields, not log source.** The engine ran
  every rule against every event, and its own docstring already recorded
  why a log-source index could not be the fix: connector product names
  do not line up with spec products, a product-based pre-filter was
  tried once and reverted for silently dropping real matches, and a
  mapping table leaves every new connector one missing entry away from a
  detection that stops firing. `match_when` is an AND at the top level,
  so a rule that requires a field the event does not carry cannot match
  it — strictly more selective than log source and provably lossless.
  "Required" is decided by **running the real matcher against an empty
  event**, which is how writing the test found that `neq` requires its
  field in this matcher despite reading like a negation; a hand-written
  operator list would have been wrong in the direction that drops
  detections. Measured: 2,511 rules, 1,751 indexed (69.74%), 797
  candidates for a routine cloud event (68.3% fewer), 2.760 → 1.066
  ms/event over 2,000 iterations.

  **Ordering per entity.** Ingest keyed every message `tenant:event_id`,
  unique per event, so nothing about one entity was ordered relative to
  anything — while fusion correlates on `{tenant}:{entity}:{tactic}`.
  Now `tenant:entity` in the same precedence the correlation key uses,
  held equal by a test, because a partition key disagreeing with the
  correlation key routes an entity's events to a partition and then
  correlates them under a different name.

  **Concurrent triage.** Auto-triage awaited one LLM call at a time.
  Concurrency is per entity, not global: alerts about one host are the
  ones most likely to be one incident and triage reads memory earlier
  triages of that entity wrote, so racing them turns a deterministic
  verdict into a coin toss. Offsets commit only after the in-flight
  window drains, with a time bound as well as a count.

  **Lag hints.** `GET /scale-hint` publishes the backlog and a suggested
  replica count. AiSOC does not act on it — ADR-0011 records why — and
  the per-replica budget is derived from the published realistic-mix run
  rather than chosen, with a test that reads the committed result file
  and fails if the two drift.

  **Realistic mix.** `--alert-every N` sends one alerting event every
  Nth and routine telemetry in between. Published run: 6,000 events
  saturating at 1-in-100, **0 of 5,940 routine events raised an alert**,
  0 missing, 0 duplicates, p95 event-to-alert 1,195 ms, ingest 122.6
  events/s.

  **The first attempt at that run measured a routine alert rate of
  1.00** — every "benign" event became an alert. Not the corpus firing:
  the load path sends an undeclared connector type, the ingest
  normalizer's generic fallback files it as class 2001 Security Finding,
  and the promoter promotes OCSF category 2 unconditionally. **Eight of
  the twelve declared profiles are category 2**, so on those connectors
  no event can be routine whatever it contains. Also fixed: "missing
  events" was counted against every accepted event, so a perfect mix run
  reported losing 99% of its traffic.

  ADR `0011`. 51 new tests (12 index, 8 partition key, 18 entity lanes,
  13 scale hint). Three claim rows; matrix 309 rows, 306 GATED.

  **`[~]` and not `[x]`, for one reason: there is no cloud-hardware
  run.** No cloud instance has been provisioned for this project, so
  every figure on the performance page comes from a laptop or from a
  kind cluster on it. The plan's 5,000 events/s at p95 under 2 s target
  is therefore an aim rather than a result, and the page says so, with
  the exact command that would close it once an instance exists. A
  second, smaller caveat recorded there too: the published mix run went
  through the **published images**, not a build of this branch, so it is
  not a measurement of the rule index — that is measured separately and
  in process.
- [~] **4.5** Deployment completeness (parity 6.8). **Three of four
  bullets closed; the managed-cluster run is maintainer-blocked.**

  **The chart installs CORE.** `infra/helm/aisoc/values.yaml` declared
  **seven** application services against CORE's sixteen: no response
  execution, no connector polling, no threat-intel store, no LLM
  gateway, no local model, no vector store. `helm install` produced a
  deployment that could not act, could not collect and could not triage
  — and reported success, because nothing compared the two files.
  `actions`, `connectors` and `threatintel` are now entries in
  `.Values.services`; `litellm`, `ollama` and `qdrant` are deliberately
  not, because that map defaults every image tag to
  `.Chart.AppVersion` and tagging a third-party image with AiSOC's
  version renders perfectly and pulls a tag that does not exist. Two of
  them need storage, so they are StatefulSets with volume claims.

  **Restore covers backup.** The two scripts already agreed on all six
  components; nothing held them that way, and a component added to one
  and not the other is discovered during an incident. Now compared in
  both directions.

  **Leader election.** The scheduler adds one job per connector
  instance in process, so two replicas each polled every vendor on every
  cycle — and on a rate-limited API the second replica's poll is the one
  that gets throttled, which looks exactly like expired credentials. A
  Postgres lease (migration `112`), not a Kubernetes Lease: the
  scheduler also runs under Compose and systemd, and an election that
  only works on Kubernetes is off wherever most first runs happen. The
  mechanism is `UPDATE ... WHERE expires_at < now()`, proved by two
  **explicitly interleaved** transactions rather than a race — a race
  between coroutines on one loop passes under a SELECT-then-UPDATE too,
  which this phase measured on its own lake-job claim. A follower
  *removes* its poll jobs rather than declining to add more.

  Gated by `scripts/check_deployment_completeness.py` (self-test: nine
  injected violations, one per rule, plus a refusal on both an absent
  and an empty tree) wired into `ci.yml :: python-lint`, and by
  `scheduler-lease-live.yml`. 13 live lease tests; matrix 311 rows, 308
  GATED.

  **`[~]`, for three things that could not be verified from here**,
  named rather than implied:

  1. **No managed-Kubernetes run.** The plan already says this one waits
     on the maintainer providing a cluster. No managed cluster is
     reachable from this machine, so `docs/perf/` gains no row.
  2. **`helm install` has not been run on a cluster.** `helm lint` is
     clean and `helm template` renders 14 workload components, which is
     static evidence that the chart is well-formed — not evidence that
     it comes up. The kind install the plan's "Done when" names is the
     open half of this item.
  3. **`scripts/check_published_images.py` could not reach GHCR**
     ("ghcr.io unreachable: The read operation timed out") and correctly
     refused a vacuous pass rather than reporting the tree clean. So the
     three new third-party image references and the three new
     first-party ones are **not** confirmed to resolve in the registry.

## Phase 5: Response that finishes

- [x] **5.1** Steps that act (parity 5.3)
- [x] **5.2** Delivery (parity 5.7)
- [x] **5.3** `wait`, `parallel`, `loop` with idempotency keys
- [ ] **5.4** Stateful user and manager verification
- [ ] **5.5** Executor arms 74 → at least 150
- [ ] **5.6** Plain-language playbooks

## Phase 6: AI agent security

- [ ] **6.1** AI asset inventory
- [ ] **6.2** Endpoint discovery with no new agent
- [ ] **6.3** Provider coverage beyond OpenAI and Anthropic
- [ ] **6.4** Agent identity and baselines (parity 6.7)
- [ ] **6.5** AI rule pack
- [ ] **6.6** AI containment and kill-switch

## Phase 7: Phishing operations

- [ ] **7.1** Intake to purge (gap-closure Phase 10 / parity 6.4)
- [ ] **7.2** Header, URL and attachment analysis
- [ ] **7.3** Adversary-in-the-middle session reuse

## Phase 8: Enterprise gates

- [~] **8.1** Identity and administration. Five of six sub-items done, each
  in its own pull request; the shortfall is itemised in D14 below.
  - [x] parity 4.1 — a containerised Keycloak signs somebody in over **OIDC**
    and **SAML**, both legs **observed to pass** (#1327). The SSO claim row
    moves PARTIAL → GATED on that evidence, not on a relabel.
  - [x] 4.2 — WebAuthn as a console second factor and MFA enforced **per
    role** (#1328), on top of the TOTP, recovery codes and per-tenant
    enforcement fix pass 4.2 already shipped.
  - [x] 4.4 — the audit retention window is enforced and a truncated chain
    still verifies (#1329). Export already existed on `AuditLogView.tsx`.
  - [~] 4.5 — opt-in limit enforcement in `entitlements.py` (#1332). The
    **six console pages** 4.5 also names are not built: see D14.
  - [ ] 4.6 — internationalisation. Not started: see D14.
  - [x] 4.7 — axe covers the case list and case workspace, the two views
    4.7 left out, and the four defects it found are fixed (#1331).
- [x] **8.2** ABAC, elevation and workload identities
- [x] **8.3** Buyer security pack

## Phase 9: Analyst surfaces

- [ ] **9.1** MCP over streamable HTTP (parity 6.6)
- [x] **9.2** Semantic memory (parity 6.5). All three bullets of parity 6.5
  closed, and the third one — "replay shows the accuracy delta" — produced a
  result that changed the design rather than confirming it. `aisoc_memory_items`
  (migration `105`) is the store of record for past cases, runbooks and
  institutional memory; Qdrant is an index over it, reached through its REST
  API so this service gains no dependency and its lockfile does not move.
  Every item carries an author, a source, a scope, an expiry and a state, and
  the author is the **authenticated principal**, never the body — provenance a
  caller can set is not provenance. Two claims about one subject suspend
  **both** sides and recall returns neither until an analyst settles it;
  preferring the newer one silently restores a bad entry the next time the job
  that wrote it runs, which is the case the feature exists for. Recall is
  tenant-scoped in the Qdrant filter itself and `search()` **raises** rather
  than offering an unscoped branch. With no embedding backend recall is 503
  with the reason, never an empty list. `kind='case'` is written automatically
  by the case-closure path, so the half of the "exists unwired" family that
  reachability analysis cannot see — a table every surface reads and nothing
  writes — does not apply. Measured by
  `scripts/score_memory_recall.py` (12 hand-authored low-overlap probes,
  mean lexical overlap 0.166, `is_synthetic: true`); its self-test is wired
  into `ci.yml :: python-lint`. 17 new tests, api suite +17. Live end to end
  against real Postgres 16, real Qdrant v1.7.0 and a real embedding backend,
  recorded in the PR. **The measurement is published as it came out, and it is
  unflattering:** see D11.
- [x] **9.3** Case depth (parity 5.6 remainder). All four open bullets.
  **Alert merge needed no schema at all**: `is_merged`, `parent_alert_id` and
  `child_alert_ids` have been on `alerts` since migration 001 with the ORM
  model as their only mention anywhere — the repository's recurring defect,
  and worth naming so "new" means something. Merge keeps every row: a
  duplicate is marked and pointed at its parent, the survivor's children are
  **appended** not replaced, re-merging and merging into a merged alert are
  both refused because each would orphan or cycle the chain, and the
  survivor inherits the case a duplicate was already on. Case merge (migration
  `106`) repoints the alerts and keeps both case rows, because deleting loses
  the audit chain, the custody entries and any vendor ticket already naming
  that id. Bulk triage is new in the route **and** the console: a checkbox per
  row, a select-all that selects this page only, and a bar whose Apply
  performs a real write and surfaces the preflight 409 with the real matched
  count instead of silently retrying. `closed` is deliberately unreachable
  there — `bulk-close` snapshots every row first and a weaker second path to
  one destination is how the weaker one wins. Tenant custom fields are two
  tables rather than a JSONB blob so a field can be enumerated, rendered,
  validated at write time and retired cleanly; values are canonicalised on
  write. Workload is counted per request over rows the query selected, a
  merged-away case is not counted as work, and **a mean over nothing is
  `null`, never `0.0`** — with the count it was taken over beside it. Graded
  by `.github/workflows/case-depth-live.yml` against a real Postgres with
  three negative controls, because every statement here is Postgres-only and
  a SQLite stand-in would be a different query. 29 new tests (23 API live, 6
  web). The live suite earned its keep immediately: it caught that
  `aisoc_cases.alert_ids` is `uuid[]` while the two columns beside it are
  JSONB, which a stand-in would have accepted.
- [ ] **9.4** War rooms
- [ ] **9.5** Hunt to report
- [ ] **9.6** Native responder

## Phase 10: Close the books

- [ ] **10** Re-run touched claim rows, update sibling progress files, one
  `[Unreleased]` entry per phase, final report here

## Item log

| Date | Item | What happened |
|---|---|---|
| 2026-10-11 | 9.3 | Reproduced: the alert merge columns had zero writers outside the ORM model; `grep -rn custom_field services/api` and `grep -rn workload` (excluding workload *identities*) both counted zero; and `grep -rn bulk apps/web/src/components/alerts` found only unrelated comments, so the only bulk verb in the product was `POST /alerts/bulk-close` with no console surface at all. The two-case-table trap named in the brief was already closed by migration 083 and `check_one_case_table.py` reports OK, so `aisoc_cases` is the table this item deepens. Three negative controls recorded in the PR and wired into the live workflow. The live suite found a real defect on its first run: `aisoc_cases.alert_ids` is `uuid[]` while `ioc_ids` and `artifact_ids` beside it are JSONB, and the merge statement had assumed JSONB. |
| 2026-10-11 | 9.2 | Reproduced: `knowledge_base.py` searched with `to_tsvector`/`plainto_tsquery` and nothing else; `grep -rn qdrant services/api/app/` found only the migration runner and the tenant-deletion sweep, no recall path; and no memory row anywhere carried an author, a source, a scope, an expiry or a state. Built the store of record, the Qdrant index over it, the conflict state machine, the case-closure writer and the recall scorer. Two negative controls recorded in the PR: restoring last-write-wins on a contradiction fails three tests, and restoring vector truncation fails one. The measurement is negative and is published as such — see D11, which also records that it caught the truncation defect. |
| 2026-10-07 | 0.1 | This file created at base commit `1b8bc2d4`. |
| 2026-10-07 | 0.2 | Every figure re-derived. Two matched exactly (detections, unreachable families); executor arms measured 74 against a captured 73; the cloud/identity/SaaS/code figure measured 395 against a captured 461 on a grouping the plan does not pin, recorded above. Two measurement caveats found: executable and quarantined overlap by 1,724 rules, and the "69% Windows" figure does not reproduce from the index. |
| 2026-10-09 | 4.3 | Reproduced: `check_retention_window.py` on the unmodified tree reported six problems — the lake deleting at 90 days against a 3,650-day cap, no `MODIFY TTL` migration, tiering deleting at 90, and the purge worker calling neither `alerts_under_legal_hold` nor `may_purge` and reporting nothing withheld. Fixed all but the cold-query bullet. Four negative controls recorded in the PR, including the positive control: a purge stuck closed withholds every tenant and fails four of the eight hold tests, which is the only thing that separates a working control from commendable caution. One pre-existing test (`test_storage_tiering.py`) pinned the 90-day tiering DELETE and now reads the shared constant; `test_retention_worker.py`'s session double could not answer the new holds query, so the worker failed closed and five of its cases failed — the double was taught the query rather than the fail-closed behaviour relaxed. |
| 2026-10-09 | 4.2 | Reproduced: `check_syslog_listener.py` against `origin/main` reported "no Go sources under services/ingest/internal/syslog", and the only syslog path was `POST /v1/inbox/cef`, which needs a forwarder that already speaks HTTP. Implemented `services/ingest/internal/syslog` (UDP + TCP, both RFC 6587 framings, four wire formats, token-derived tenant, batched publish, `/readyz` subscription). Five negative controls recorded in the PR; one of them found a hole in the new gate itself, which reported OK while the tenant came from `msg.Hostname` through a struct field — the detector now knows all three Go syntaxes and the self-test exercises each. Writing the tests also found a shutdown deadlock: `Stop` waited on goroutines watching a context the caller had not cancelled yet. Ingest suite green, `internal/syslog` 33 cases. |
| 2026-10-07 | 0.3 | `make up` and `make smoke` (10/10) pass. Injection suite and load-harness baselines committed. `make up-full` deferred (D2) and hosted model rows blocked (D3). Fixing D1 was a precondition for the load-harness baseline. |
| 2026-10-09 | 3.3 | Identity privilege (18 rules) and a per-tenant first-seen store (2) built; 5 rules were never unreachable (gate operator drift, D9); 18 retired with a reason (D10). `MAX_UNREACHABLE` 45 → 2, the two remaining both needing the 3.4 baseline. Two matcher operators three shipped rules already used were implemented. |
| 2026-10-09 | 3.2 | Ordered and unordered sequences in the windowed engine; all four translatable Sigma correlation types compile, seven refusal reasons recorded. No upstream correlation rule exists in this tree to import (D8), so the corpus is first-party and labelled as such. |
| 2026-10-11 | 4.5 | Three of four bullets closed. Reproduced: `check_deployment_completeness.py` on the pre-fix tree reported six CORE services the chart renders no workload for. Added them (three in `.Values.services`, three as their own templates because a third-party image must not inherit `.Chart.AppVersion` and two need volumes), compared restore against backup in both directions, and built Postgres leader election for the connector scheduler (migration `112`). Negative control: removing the lease's expiry predicate makes both interleaved transactions lead and three live cases go red. **Not verified here:** no managed-cluster run, no `helm install` on a cluster, and `check_published_images.py` could not reach GHCR and refused to pass vacuously. |
| 2026-10-11 | 4.4 | Every parity 6.9 bullet closed; the cloud-hardware run is not possible from here and is recorded as unmeasured rather than implied. Rule index on required fields (lossless, proven by replaying every fixture both ways; 68.3% fewer candidates, 2.6x on evaluation), entity partition key held equal to the correlation key, per-entity concurrent triage, lag-based scale hint derived from the published run. The realistic mix found that eight of twelve connector profiles are category 2 and are promoted unconditionally, so on those connectors no event can be routine — the first run measured a routine alert rate of 1.00. ADR-0011; matrix 309 rows, 306 GATED. |
| 2026-10-11 | 4.3 | Third bullet closed. Reproduced: `check_retention_window.py` with the new rules reported no cold-query estimator, no job surface and no job table on the pre-fix tree. Built `lake_cold_query.py` (EXPLAIN ESTIMATE + system.parts + system.processes, no invented throughput or price), `lake_query_runner.py` and migration `111`. Negative control: removing the `status = 'queued'` predicate makes both interleaved transactions claim one job and the live suite goes red. The first version of that test — five gathered claims — passed under the broken implementation and was replaced. 26 pure + 12 live tests; matrix 306 rows, 303 GATED. |
| 2026-10-11 | 4.2 | Reproduced: `check_standard_inputs.py` against the pre-fix tree reported no OTLP package, no Kafka input and no TAXII server — the only TAXII-shaped route being a demo-gated sample list. Built all three, after moving the consumer-health classifier out of `graph_ws` into `streamhealth` so the new Kafka consumer shares the table rather than copying it. Negative controls recorded in the PR: a timestamp-only TAXII cursor loses an indicator in the single-row pagination walk (measured — 3 of 4), and nineteen gate injections each go red. Writing it found four defects, including an OTLP template nobody could mint a token for and a gate rule that read an error message instead of the behaviour. Ingest Go suite green; api projection suite 37; live TAXII suite 15. |
| 2026-10-09 | 4.1 | Reproduced: `check_cloud_native_collection.py` on the unmodified tree reported all three collection paths absent. Implemented `aws_cloudtrail_s3` (SQS-notified S3 objects; management events, data events and VPC flow logs; delete-after-emit), `gcp_pubsub` (REST pull on a log-sink subscription; ack-after-read) and `azure_event_hubs` (Capture blobs over the Data Lake Gen2 JSON API, with a focused Avro OCF reader). Negative controls recorded in the PR: deleting the SQS message before the object is read, acknowledging the Pub/Sub batch before it is built, ignoring the Avro union branch index, and ignoring the flow-log header line each fail a named test, and all were restored. Connectors suite 1014 -> 1098 passed. |
| 2026-10-09 | 3.1 | All 74 decided. 50 translated into `wd-*` rules derived from each original's own clauses and replayed through the real engine (162 assertions); 24 refused with a reason across five kinds. `MAX_UNREACHABLE` 119 → 45, published executable 2,603 → 2,529, windowed 18 → 68. Three findings recorded as D4–D6 below. |
| 2026-10-11 | 8.1 | parity 4.1's containerised-IdP leg **observed to pass**, both halves: `keycloak-oidc` verifies a real `id_token` against Keycloak's published JWKS with an audience-mismatch negative control, and `keycloak-saml` walks the whole SP-initiated flow to the real ACS and signs `alice@example.com` in as `infosec`, with an untrusted-key control answering 400. Run `38124780886`, as `ENVIRONMENT=test` against the DML-only `aisoc_app` role. The SSO claim row moves PARTIAL → GATED on that evidence. Building it found two shipped defects no self-authored provider could expose: `resolve_saml_connection` bound `:i` untyped so `:i IS NULL` raised on asyncpg, and Keycloak's default role-list mapper emits one `<Attribute Name="Role">` per role, which python3-saml refuses. |
| 2026-10-11 | 8.1 | WebAuthn as a console second factor and MFA enforced per role. Fixing the branch's own gates found three `passkey_credentials` reads scoped by user id alone on a tenant-scoped table, and a permission-model violation where the MFA policy route imported `ROLE_PERMISSIONS` directly; the role *vocabulary* now has one owner in `role_grants.known_roles()`. 23 of 23 live cases pass against real Postgres, and deleting the login integration fails 14 of them — measured, where the workflow had said eight. |
| 2026-10-11 | 8.1 | An enforced audit retention window with a re-anchored checkpoint, ADR-0011, and 12 live cases. Writing them found that migration `111` declared `ON DELETE CASCADE` on the checkpoint table and then made the cascade impossible; and, separately, that `audit_log`'s own trigger from migration `101` blocks `DELETE FROM tenants` for every tenant that has written a row, so tenant deletion is impossible on `main`. Reproduced and filed as #1330 rather than fixed here. |
| 2026-10-11 | 8.1 | Opt-in per-tenant limit enforcement (migration `113`, D12), wired to `POST /connectors` and `POST /tenants/me/users` through one helper, with `GET`/`PUT /usage/enforcement` as the operator surface. Nine live cases, half of them positive controls: a guard that never refuses fails 1, a guard stuck closed fails 4. |
| 2026-10-11 | 8.1 | axe extended to the case list and case workspace, the two of parity 4.7's five views that were left out. Four real defects found and fixed: two `<select>` controls with no accessible name (one of them the control that writes a case's status), two indistinguishable `<aside>` landmarks, and panel headings at `h3` directly under the page's `h1`. |

