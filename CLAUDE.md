# fastpp: working notes for Claude Code

These notes carry the project's conventions between machines. They were written from the
orchestrating session's memory on 2026-09-28; keep them current when a rule or lesson changes.

## Goal

A centralized list of the fastest C++ code (other languages later) so agents and developers can
find faster implementations and libraries for their projects. C++ comes first; C libraries callable
from C++ count. The spec is `pipeline/spec.md` (Part 4 lists each wave's categories and baselines).
Scripts are in `pipeline/`, data in `data/waveN/`, the rendered catalog in `catalog/` (plus `catalog.jsonl`,
`catalog.csv` and the generated blocks of `README.md`), written by `pipeline/render_lists.py`; never hand-edit
those outputs. Reader docs are in `docs/` (the build history is `docs/build-log.md`).

## Standing rules from the user

- **Commit and push after every milestone** (each search merged, verifier batch applied,
  enrichment recorded, lists rendered). Pushing to `origin main` is pre-authorized. Stage only
  the files a step produced; never commit raw files that a still-running agent is writing.
- **Keep flagged entries and document their shortcomings** in `data/decisions.json` instead of
  dropping them (not faster, off-baseline, private repo, wrong category, low confidence, security
  bugs, quality failures). Reject only when the evidence is invalid or fabricated (precedents:
  MQF timed a no-op; FastestJSONInTheWest benchmarked a sleep; zokio hard-coded its baseline
  column; ClickBench-disqualified results; stb-zip's fast path computed a different checksum;
  Go stdlib's libp2p "OpenSSL" columns ran Go code).
- **Quiet runs:** no progress updates to the user after each agent report. Speak when blocked,
  when a wave closes, or when asked. Every subagent prompt ends with a terse final-reply rule
  (max ~8 lines; the JSON output stays normal prose).
- **Caveman ultra everywhere (2026-10-03):** the orchestrator's replies to the user and every
  subagent's final reply use caveman ultra style (fragments, no articles, no filler, no arrows,
  no invented abbreviations; names, numbers, paths and errors exact). Data files, rendered
  lists, decisions and commit messages stay normal prose. The subagent wording is in
  `pipeline/cloud_harness.md`; repeat it in prompts that do not include that file.
- **Token discipline (2026-10-13):** user saw heavy token use; orchestrator and agents keep caveman ultra in all
  their own text, read files in slices (grep/head/sed ranges, never whole large files), dump few records per call,
  and skip restating findings. Agent wrappers carry a TOKEN DISCIPLINE line.
- **Tokens are not a concern:** raise or remove caps when it yields more or better results.
  Sonnet for search (get coverage from more search agents, not a bigger model), Opus for verify,
  enrich and re-tier checks.
- **docs/QUEUE.md** holds later extensions (waves 13-14, cross-language claims, seed-list mining).
  Keep it out of the spec, pipeline and data until waves 3-12 are finished, unless the user pulls
  it forward. Its first section, "Unfinished work", is the open backlog of the wave loop (deferred
  searches, retier checks, seed passes); resume from there and keep it current.
- **Developer source repo:** it is private for now (the user will make it public when ready), so its entries are
  capped at tier C. Its 8 entries carry ids `private:developer-source[#category]`,
  `repo_url` and `benchmark_url` read `private:developer-source...`, and pages show "private
  repository, not published yet". When it is published, record `repo_url` overrides and re-check the tier. Do
  not change its visibility or modify its checkout without an explicit instruction.
- Hard-to-reverse actions need the user's confirmation.

## Privacy and security (repeat these in every agent prompt)

- Never send the user's email, name or other personal identifiers to any outside service (URLs,
  headers, payloads). Do not build headers from `git config`. For APIs that want a User-Agent
  (crates.io and others) use exactly `User-Agent: fastpp-research-bot/1.0`.
- Agents write nothing in the repo except their named output file. They must `mkdir -p` their
  own scratch directory under the session's scratchpad and save every fetched file there by
  absolute path. A relative `readme.md` overwrote `README.md` twice in wave 7 (macOS file names
  are case-insensitive). Check `git status` after each report and restore/delete strays.
- Never disable the sandbox.
- **Repo hygiene:** MIT license; copyright lines say "the fastpp contributors". No personal data,
  home-directory paths or credentials in tracked files or commit metadata. Prompts rendered on a local machine
  embed the checkout's absolute path: run `python3 pipeline/check_pii.py --fix` before committing them (CI runs
  the same check with `--commits`). Commit as `harrisjibwork <harrisjibwork@users.noreply.github.com>` (set it as
  this repo's `user.name` and `user.email` on a local machine).

## Evidence tiers

- A: public benchmark code + compiler + flags + CPU model (fully reproducible), whoever ran it.
- B: independent or peer-reviewed measurement.
- C: first-party only.
- D: directional, no numbers.
Ratios a verifier derives are allowed if labelled "(derived from page data)". CC0/public-domain
code counts as copyable.

## The wave loop

Each wave has `data/waveN/assignments.json`: categories x 8 source batches
(b1 gh-cpp, b2 papers, b3 gh-cpp2, b4 shootouts, b5 registry, b6 gh-any, b7 blogs, b8 hn),
plus an optional `seed` assignment. Build a new wave's file from spec Part 4 the same way as
`data/wave8/assignments.json`, and create `data/waveN/leads.md`.

1. `python3 pipeline/render.py data/waveN --batch bK` renders search prompts to
   `data/waveN/prompts/`. Render a category's gh-cpp2 prompt after its papers search finishes.
2. Launch one Sonnet agent per prompt. When it reports:
   `python3 pipeline/merge.py data/waveN`, then
   `python3 pipeline/verify.py render data/waveN --assignments <assignment ids>`
   (renders only that search's new entries; batches of 3).
3. Launch one Opus agent per verifier batch. When it reports, record shortcomings, then
   `python3 pipeline/verify.py apply data/waveN` and `python3 pipeline/enrich.py data/waveN`.
4. Launch Opus enrichers for newly verified entries (two prompts per agent works well). Record
   their shortcomings.
5. Collect leads from enrichers in `leads.md`; before closing, add a `seed` assignment with a
   `projects` list, run `python3 pipeline/seed.py data/waveN --batch seed`, then merge, verify
   and enrich the seed records.
6. Close: final `verify.py apply`, confirm every verified entry has `enrich/raw/<slug>.json`
   (slug = `re.sub(r"[^a-z0-9]+","_", id.removeprefix("https://")).strip("_")`), run
   `python3 pipeline/render_lists.py` (and `pipeline/seeds_no_evidence.py` when seeds changed), run
   `python3 pipeline/check_pii.py`, commit, push, and update these notes.

Recording decisions: pipe JSON lines into `python3 pipeline/add_decisions.py`, e.g.

```
python3 pipeline/add_decisions.py <<'EOF'
{"id":"https://github.com/owner/repo","s":"shortcoming text","m":"independent measurement"}
{"id":"https://github.com/owner/port","decision":"duplicate","reason":"why it folds into X"}
EOF
```

Override fields (`name`, `category`, `domain`, `repo_url`, `has_code`, `language`) are applied by
`verify.py apply`. Re-tier a verified entry by writing `data/waveN/verify/raw/retier-NN.json`
(`[{id, evidence_tier_final, tier_reason, corrections{...}, urls_opened}]`).

Agent prompt shape (search/verify/enrich): "Read <prompt file> and carry out that task exactly;
it names your output file." plus a harness note: which sources to use (`gh`, prefer
`gh api graphql` when REST search is rate-limited; WebFetch; PDFs via curl + pdftotext; HN
Algolia; arXiv; IACR ePrint; crossref.org since DBLP blocks bots), draft output early, move on
after 2 failed fetches, the privacy/scratch rules above, and the terse final-reply rule.

## External limits

- `gh search` allows ~30 requests/min across all agents; the authenticated REST limit (5000/h)
  runs out at ~30-40 concurrent agents, so agents fall back to `gh api graphql`, github.com pages
  or raw.githubusercontent.com.
- WebSearch has a per-session budget (exhausted in earlier sessions); prefer arXiv, Semantic
  Scholar and HN Algolia APIs. kerkour.com asks not to be scraped.
- Subagent concurrency: set `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=50` in
  `.claude/settings.local.json` (gitignored, so set it on each machine).

## Lessons

- `merge.py` reads every raw file, including drafts of running agents; render verify batches with
  `--assignments` so drafts stay out. Applying while verifiers are mid-write picks up drafts
  (harmless; re-apply after they report).
- Records sharing one repo URL, or pointing at an already-known repo (SUPERCOP mirror, Crypto++),
  need a `paper:` id set in the raw file before merging.
- Wrappers, ports and FFI bindings of an already-listed project get decision `duplicate`.
- Vendor-blog evidence from a company selling the product is retiered to C; numbers measured on
  code later fixed for correctness bugs, or built with flags absent from public sources, go to C.
- `verify.py render` skips `duplicate` entries; `apply` honors keep/reject/duplicate and the
  override fields above.
- Default search assignments to a C++ language filter; "any"-language passes are extra coverage.

- Cloud sessions (claude.ai): `gh` works only for this repo, and api.github.com, export.arxiv.org,
  crossref and dblp are blocked. In the 2026-10-01 session the egress policy also blocked
  arxiv.org, hn.algolia.com, api.semanticscholar.org, *.github.io, dl.acm.org, ieeexplore, doi.org,
  sciencedirect, springer, readthedocs and most blogs; github.com (WebFetch), raw.githubusercontent.com
  (curl), gitlab.com and pypi.org worked. Papers checked in a repo (e.g. doc/*.pdf) are reachable via
  raw.githubusercontent.com. Give every agent `pipeline/cloud_harness.md` as an override of the
  prompt's tool notes and /Users/... output path. Egress differs by environment: the project
  thread that ran wave 8 b1/b2 could WebFetch arxiv.org/abs and HN Algolia. Widening the
  environment's network access (or adding those hosts), or working from that thread, is what
  unlocks b7/b8 and paper-based retiers.
- Subagents share one WebSearch budget per session (it ran out at 200/200 with ~28 agents running);
  draft from github.com pages first. Do not let agents use mcp__github__ tools: the session's GitHub
  scope is this repo only.
- Category incumbents and wrappers of an already-listed project found again by a later search get
  decision `duplicate` (wave 8: boostorg/geometry, flame/blis, SuiteSparse, libxsmm-dnn).
- Verifier "not-notable-tier-d" rejects are overridden with decision `keep` plus a shortcoming
  (keep-and-document rule); only invalid or fabricated evidence stays rejected.
- A user interrupt in the main session can kill running background agents silently; if an agent
  never reports and its raw file is missing or stale, relaunch it.
- Decision ids must match merged ids exactly (lowercase canonical URL): a shortcoming recorded under
  `https://github.com/DAddYE/trez` did not fold `https://github.com/daddye/trez`; check with
  `verify.py render` output and re-record under the merged id.
- Long agent prompts go in a scratchpad file; the Agent call then says only "Your full
  instructions are in <path>. Read that file first..." plus the caveman final-reply rule. The
  scratchpad gen_enrich.py (pinned pair order in enrich_order.json, skips slugs that already have
  enrich/raw/<slug>.json) made relaunches after kills idempotent.
- A weekly usage-limit kill (2026-10-04, ten Opus enrichers) left complete output files behind:
  check each untracked enrich/raw file for the full key set and a sensible confidence before
  deleting or relaunching; 13 of 13 were usable and only their reports were lost (shortcomings
  were then taken from the files' gotchas and status_note fields).
- Enricher findings that change a record (baseline, numbers, caveats) go in a retier file even
  when the tier stays; add_decisions.py only applies the override fields.

- merge.py id drift (wave 12): when a later raw file carries the same repo with a different name and category,
  the merged record flips to the higher-tier or higher-confidence copy (Apogee, Wangshu, Topaz, lua-rs) or
  gains a `#category` suffix whose position depends on raw-file sort order (CPython JIT became
  `python/cpython#jits`, WARP, lua-aot, quickjs-ng split). Run the scratchpad check_ids.py (compares
  merged.json against a snapshot and the verify ids.json files) after every merge; fix the ids.json of an
  unlaunched batch, record `duplicate` for a split id, and record `name`/`category` overrides to keep a
  verified record's identity when a new raw copy wins the dedup.
- Pin enrichment pairs: gen_enrich.py must never rewrite an existing pair directory; new pairs are only built
  for unenriched prompts not already covered, numbered from the top. Otherwise relaunches after kills
  realign odd/even pairs and launch the wrong prompts. When a verified entry later turns `duplicate`
  (go-quickjs, cinderx), delete its enrich prompt and the unlaunched pair that held it before re-pairing.
- Reject precedents added in wave 12: an interpreter that pattern-matches the benchmark's function names and
  replaces them with native loops (R8/NoClip), a compile row that hits an in-memory cache (wazero via the
  PolkaVM benchtool), a RegExp fast path that never runs a regex (Pipa), design targets presented as
  measurements (r8e) and a hard-coded speedup table (zig-evm). Downgrade precedents: third-party numbers
  measured before a hot-path correctness fix (Paserati #550), a tuned fork measured in place of upstream
  (Topaz), and a baseline crippled by a build default (AssemblyScript's tsc useDefineForClassFields).
- `verify.py apply` picks up a verifier's draft before its report arrives, so enrich.py then renders prompts
  for records whose verdict may still change; do not launch those enrichers until the batch reports.
- A session-limit kill (2026-10-06, nine Opus enrichers) again left complete files behind: all 13 orphaned
  enrich/raw files had the full 13-key set; shortcomings were taken from their gotchas and status_note fields,
  and only the 7 missing partners were relaunched (4 agents at a time after the reset).

- Backfill round 2 (2026-10-11): a seed record for a repo already verified in another wave must get a `paper:` id
  before `merge.py` runs, else the merged copy adopts the old id and verify render silently skips it (icey,
  Boost.Fiber, oneTBB); `adddec.py` refuses `paper:` ids until the merge has happened, so the order is set id in the
  raw file, merge, record `duplicate`, then `verify.py render` (a render before the decision cut three wave-12
  batches that had to be deleted and re-rendered). `addretier_w.py` likewise refuses an id until `verify.py apply`
  has put it in verified.json. Category overrides that move an entry to another wave's category need a `domain`
  override too, or render_lists.py shows the category under two domains. Enrichers keep finding harness defects the
  verifier missed (re-keying on one side only, uninitialised buffers, cached pre-fix builds, single-threaded baselines
  by harness default, GPU-vs-CPU decode asymmetry, degenerate zero-field workloads, cross-run comparisons); each
  becomes a retier entry, and cross-run or no-valid-measurement cases go to D. 18-19 Opus agents at once ran for the
  whole pass without a usage-limit kill on 2026-10-11. The stop hook asks to commit untracked files after every
  turn while agents are writing; decline until each report is recorded.

- Waves 13-14 (2026-10-12/13): the Agent tool refuses a 21st concurrent subagent, so the loop runs at 20 and launches
  new pairs only as reports arrive. An org spend-limit kill and a worker restart each left complete enrich/raw files
  behind: check for the 13-key set plus a confidence, record from the file, and relaunch only the missing partner as
  a single-prompt pair-NNNb variant. Tool output is capped near 30 KB, so dump 4-8 records per call with truncated
  fields. adddec.py is all-or-nothing (one unknown id rejects the whole batch) and applies only the override fields,
  so maintenance_status, compiler_and_flags and claim fixes go through retier corrections; `verify.py apply` appends
  caveat corrections as "[retier] ..." addenda (write addenda, not rewrites) and replaces the other fields. Build
  decision and retier ids from the enrich/raw file's own `id` field rather than retyping them. kostya/benchmarks rows
  are often older than the README's Versions table (the 2026-07-19 bench.b and json rows date from the 2025-08-17
  run); record the measured toolchain, not the listed one. Cross-run or cross-container comparisons (LangArena rows
  before a harness change, related_post_gen, Microbenchmarks CI jobs on separate VMs, plb2 rows added on different
  days) and crippled or asymmetric baselines (startup inside the timed region, -O0 or assert-enabled builds, a
  Debug build against -O2, GC never collecting while C frees) are the main wave-14 downgrade reasons; same-task
  idiom differences (SwissTable against std::unordered_map, borrowed keys, stable against unstable sort) stay at
  their tier with the mechanism documented.

- Seed passes into closed waves (2026-10-13): never bump a wave's `today` in assignments.json; `verify.py apply`
  stamps every applied verdict with it, so a bump restamped all 235 wave 6 verification dates. Keep each wave's
  original `today` (render the seed prompts with it too); the new verdicts carry the old date, which matches earlier
  backfill rounds.
- Public-release pass (2026-10-12): `render_lists.py` now writes `catalog/` (pages per domain, category and
  entry, JSONL and CSV) and the README's marked blocks; CI fails if a fresh render differs from the commit, so
  re-render before every data commit. Auto mode refuses force-pushes, so an amend after a bad `git add` (a
  pathspec error aborts the whole add) has to be a follow-up commit instead.

## Status

Current counts are in the generated block of `README.md`; the per-wave history (what each wave and backfill
round found, retiered and rejected) is in `docs/build-log.md`, newest first. Add a dated entry there when a wave
or round closes, and keep `docs/QUEUE.md` "Unfinished work" current.
