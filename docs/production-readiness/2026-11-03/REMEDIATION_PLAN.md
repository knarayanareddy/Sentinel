# Sentinel — remediation plan

This is future work, not completed remediation. Findings refer to [REVIEW.md](REVIEW.md). No target code, tests or deployments were run.

## Phase 0 — establish an isolated baseline

**Entry:** owner approves synthetic-only use. **Exit:** entry points, substitutes and baseline are documented without real mail or financial data.

### T01 — Reproduce the decision path (correctness; F01–F07)

Prerequisites: isolated workspace, synthetic IDs and fake services. Observed: `sentinel/server.py`, `sentinel/orchestrator.py`, `sentinel/pipeline.py`.

1. Map `/api/run` → proposal → gate → decision → executor → incident seal, including state and policy installation.
2. Exercise passing action, each failed signal, absent policy, rejection, approval and executor exception; record responses, events and executor calls.
3. Restart and use a second worker against a frozen action; record accessibility and cross-process duplicate checks.

**Output:** reproducible baseline and unknowns. **Verification:** compare observations with source and fake-executor counts; send no external message.

- [ ] Every case has inputs, expected outcome and observed outcome or an explicit blocker.
- [ ] Restart and cross-worker findings are recorded separately from source assumptions.

## Phase 1 — secure and correct the decision boundary

**Entry:** T01 baseline and owner-defined identities. **Exit:** denied requests cause no execution; gate and execution states are independently observable.

### T02 — Authorize HTTP and stream access (security; F01, F02)

Prerequisites: owner-approved identity provider, operator roles, action ownership and ingress design. Observed: `sentinel/server.py`, `deploy/nginx.conf`, `frontend/src/App.tsx`.

1. Define principals and permission matrix for run, decision, corpus and stream, including action/session scope; inventory any trusted proxy and prevent bypass to the backend.
2. Implement server-enforced authentication and authorization for each route and WebSocket handshake/reconnect; restrict browser origins separately, with CSRF defenses appropriate to the chosen credential transport.
3. Bind decision audit records to actor, action and result without logging credentials or sensitive document content; specify expiry and revocation behavior.

**Output:** reviewed boundary and permission matrix. **Verification:** test missing, expired, wrong-role and cross-session credentials through ingress and direct backend where reachable; assert denial, no execution and no history disclosure. Remove a guard and confirm the test fails.

- [ ] HTTP, WebSocket history and reconnect all enforce the same approved access model.
- [ ] Authorized decisions and denied attempts have appropriately redacted audit evidence.

### T03 — Make the gate and execution outcome explicit (correctness; F05–F07)

Prerequisites: T01 and owner decision on durable storage, concurrency and effect semantics. Observed: `sentinel/orchestrator.py`, `sentinel/pipeline.py`, `sentinel/server.py`.

1. Make a missing or failed policy prevent irreversible execution; explicitly model signal failure and verify that startup wires the policy used by the live request path.
2. Separate approval from execution success, failure and unknown outcome; preserve the latter when an executor may have acted before raising, and expose it in the incident record.
3. Implement durable, atomic decision transitions and an effect-specific idempotency/reconciliation strategy, or document and enforce a single-process demo-only boundary until supported.

**Output:** state contract and recovery path. **Verification:** inject absent policy, model failure, concurrent approvals, timeouts before and after an effect, and restart; inspect effect counts and resulting state.

- [ ] No irreversible effect occurs without a valid gate and authorized transition.
- [ ] Ambiguous effects are not reported as successful or retried blindly.

## Phase 2 — meaningful automation and operator experience

**Entry:** T02–T03 interfaces agreed. **Exit:** CI exercises behavior and operators can resolve failures.

### T04 — Build behavioral gates (automation; F03, F05–F07)

Prerequisites: isolated fakes from T01 and documented test dependencies. Observed: `.github/workflows/ci.yml`, `requirements.txt`, `tests/`, `frontend/package.json`; proposed paths: new test fixtures and workflow steps as needed.

1. Separate offline and live-provider tests; prevent collection creation or real calls in CI.
2. Add end-to-end boundary tests that invoke the actual server and instrument a fake executor, including unauthorized approval, missing policy, signal failure, duplicate decisions and uncertain execution.
3. Run offline tests and frontend `build` and `lint` in CI; define a frontend test script before using one. Gate live tests separately.

**Output:** CI and test-tier documentation. **Verification:** break an authorization guard and a gate transition in a disposable change; corresponding tests must fail. Record the job result and selected tests.

- [ ] CI runs behavioral assertions without production credentials or external effects.
- [ ] Negative controls prove the tests detect the named regressions.

### T05 — Make operator status actionable (UI/UX and accessibility; F04, F06, F08, F09)

Prerequisites: T03 state contract and authoritative status. Observed: `frontend/src/App.tsx`, `frontend/src/pages/GatePage.tsx`, `frontend/src/hooks/useEventStream.ts`, `frontend/src/components/OperatorGate.tsx`; proposed: status component.

1. Match decisions, proposals, citations and incidents to the current frozen `action_id`, preserving correct monitor alerts and controls across runs and history replay.
2. Show pending, denied, failed, approved, executed and uncertain states separately. Never claim dispatch based on approval alone; require authoritative evidence of execution.
3. Fix [OperatorGate.tsx:148–169](https://github.com/knarayanareddy/Sentinel/blob/1736f0cbec25ed0d3190d692a03bd3c4eadb033e/frontend/src/components/OperatorGate.tsx#L148-L169): type and await the decision callback, hold pending through settlement, and propagate non-OK/network failures from the parent. Reconcile ambiguous outcomes before retry.
4. Provide keyboard-operable controls, focus management and a screen-reader announcement for changes and errors; avoid relying on color alone.

**Output:** action-scoped, accessible operator flow. **Verification:** render decision A followed by freeze B and assert B's alert, evidence and controls remain visible; repeat after reconnect with replayed, deduplicated history. Inject an executor exception and assert no dispatch claim without authoritative execution evidence. Delay the decision response, double-click and assert one request and pending controls until settlement; fail the request and verify visible error and safe reconciliation before retry. Deliberately restore the unscoped decision predicate and early loading clear to confirm those tests fail. Check keyboard and announced status.

- [ ] Failure and uncertainty remain visible outside the developer console.
- [ ] Decision A cannot suppress freeze B, including after history replay; displayed evidence belongs to B.
- [ ] Executor exception never produces an unsupported dispatch claim.
- [ ] A delayed response permits one submission; pending persists and failure recovery is safe.
- [ ] Keyboard and assistive-technology checks are recorded with observed results.

## Phase 3 — security, operations and independent acceptance

**Entry:** T02–T05 complete; owner approves deployment boundaries. **Exit:** observed restore, rollback and boundary checks support a release decision.

### T06 — Data, supply chain and recovery (DevOps/security; F02, F03, F07; preventive)

Prerequisites: owner-approved hosting, retention and recovery objectives; test-only provider credentials. Observed: `deploy/DEPLOYMENT.md`, `deploy/nginx.conf`, `requirements.txt`, `frontend/package-lock.json`, `sentinel/server.py`.

1. Inventory ingress/TLS, backend reachability, process count, secret storage and rotation, outbound memo sink, vector-store tenancy and sensitive event/log fields; compare the deployed configuration with the checked-in example.
2. Review dependencies and transitive integrity using approved tooling; exercise malicious retrieved text against the real gate with fake services, documenting prompt-injection limits instead of claiming model immunity.
3. Define startup ingestion idempotence, backup scope, retention, restore and immutable release/rollback procedures; restore synthetic incidents and vector data in isolation and observe a rollback.

**Output:** inventory, risk decisions and restore/rollback record. **Verification:** check restored records, ingress denial, redaction and no unexpected mail; document unmet targets.

- [ ] Restore and rollback are observed, not merely described.
- [ ] Owner accepts residual dependency, data and provider risks before release.

### T07 — Independent acceptance (all five disciplines; all findings)

Prerequisites: T02–T06 evidence, approved test environment and reviewer independent of implementation. Observed paths: all paths named above; proposed: acceptance report stored with release evidence.

1. Re-run the original unauthorized decision, stream access, missing-policy and failed-executor cases against the release candidate and compare with the baseline.
2. Inspect CI selection and negative-control evidence; independently test operator failure/reconnect flow and confirm deployment, backup and rollback observations match the candidate.
3. Record open risks, domain validation and owner approvals; block release if required authorization, effect safety or recovery evidence is missing.

**Output:** acceptance report or rejection. **Verification:** reviewer observes denial and executor counts and matches the release identifier to the tested artifact; test totals are insufficient.

- [ ] Every finding is closed with evidence or explicitly accepted as unresolved.
- [ ] Owner and independent reviewer make separate release decisions.

## Dependencies and release policy

| Task | Depends on | Release role |
|---|---|---|
| T01 | Synthetic environment | Baseline |
| T02, T03 | T01; owner identity and state decisions | Security and correctness gates |
| T04, T05 | T02/T03 contracts | Automation and operator gates |
| T06 | T02–T05; approved hosting and data | Operations and recovery gate |
| T07 | T02–T06 | Independent acceptance |

**Production checklist:** [ ] authenticated, action-scoped access; [ ] fail-closed gate; [ ] execution uncertainty reconciled; [ ] behavioral and accessibility checks; [ ] observed restore and rollback; [ ] owner accepts domain, privacy and provider risks. Not certification.

Owner approval is required for live credentials, hosting, real documents, mail, retention, release and effect semantics. Release a reviewed immutable candidate; retain the previous artifact and recovery point. On regression, disable new actions, preserve evidence, roll back and verify restored state; never replay an uncertain memo automatically. Future commands are planned, not executed or presumed available.
