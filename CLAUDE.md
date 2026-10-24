# fastpp: notes for Claude Code and other agents

The conventions an agent session follows when it extends or maintains the catalog. Keep them current when a rule or
lesson changes. Reader-facing docs are in `docs/`.

## Goal

A centralized list of the fastest C++ code (other languages later) so agents and developers can find faster
implementations and libraries for their projects. C++ comes first; C libraries callable from C++ count. The spec is
`pipeline/spec.md` (Part 4 lists each wave's categories and baselines). Scripts are in `pipeline/`, data in
`data/waveN/`, the rendered catalog in `catalog/` (plus `catalog.jsonl`, `catalog.csv` and the generated blocks of
`README.md`), written by `pipeline/render_lists.py`; never hand-edit those outputs. Reader docs are in `docs/` (the
build history is `docs/build-log.md`).

## Rules

- **Commit after every milestone** (each search merged, verifier batch applied, enrichment recorded, lists
  rendered). Stage only the files a step produced; never commit raw files that a still-running agent is writing.
- **Keep flagged entries and document their shortcomings** in `data/decisions.json` instead of dropping them (not
  faster, off-baseline, private repo, wrong category, low confidence, security bugs, quality failures). Reject only
  when the evidence is invalid or fabricated (precedents: MQF timed a no-op; FastestJSONInTheWest benchmarked a
  sleep; zokio hard-coded its baseline column; ClickBench-disqualified results; stb-zip's fast path computed a
  different checksum; Go stdlib's libp2p "OpenSSL" columns ran Go code).
- **Models:** Sonnet for search (get coverage from more search agents, not a bigger model), Opus for verify, enrich
  and re-tier checks.
- **Final replies:** every subagent prompt ends with a terse final-reply rule (max ~8 lines; the JSON output stays
  normal prose) and asks for caveman ultra in all the agent's own text. The prompt templates (`render.py`,
  `seed.py`, `enrich.py`, `verifier_prompt.txt`) carry it; the wording is in `pipeline/cloud_harness.md`.
- **docs/QUEUE.md** holds later extensions. Its first section, "Unfinished work", is the open backlog of the wave
  loop (deferred searches, retier checks, seed passes); resume from there and keep it current.
- **Developer source:** a private repository, not published yet. Its 8 entries carry ids `private:developer-source[#category]`, are
  capped at tier C and show "private repository, not published yet". When it is published, record `repo_url`
  overrides and re-check the tier.

## Privacy and security (repeat these in every agent prompt)

- Never send personal identifiers (email, name) to any outside service (URLs, headers, payloads), and do not build
  headers from `git config`. For APIs that want a User-Agent (crates.io and others) use exactly
  `User-Agent: fastpp-research-bot/1.0`.
- Agents write nothing in the repo except their named output file. They `mkdir -p` their own scratch directory
  under the session's scratchpad and save every fetched file there by absolute path (a relative `readme.md` can
  overwrite `README.md`, since macOS file names are case-insensitive). Check `git status` after each report and
  restore or delete strays.
- Never disable the sandbox.
- No personal data, home-directory paths or credentials in tracked files or commit metadata. Prompts rendered on a
  local machine embed the checkout's absolute path: run `python3 pipeline/check_pii.py --fix` before committing them
  (CI runs the same check with `--commits`). Copyright lines say "the fastpp contributors".

## Evidence tiers

- A: public benchmark code + compiler + flags + CPU model (fully reproducible), whoever ran it.
- B: independent or peer-reviewed measurement.
- C: first-party only.
- D: directional, no numbers.

Ratios a verifier derives are allowed if labelled "(derived from page data)". CC0/public-domain code counts as
copyable.

## The wave loop

Each wave has `data/waveN/assignments.json`: categories x 8 source batches (b1 gh-cpp, b2 papers, b3 gh-cpp2,
b4 shootouts, b5 registry, b6 gh-any, b7 blogs, b8 hn), plus an optional `seed` assignment. Build a new wave's file
from spec Part 4 the same way as `data/wave8/assignments.json`, and create `data/waveN/leads.md`.

1. `python3 pipeline/render.py data/waveN --batch bK` renders search prompts to `data/waveN/prompts/`. Render a
   category's gh-cpp2 prompt after its papers search finishes.
2. Launch one Sonnet agent per prompt. When it reports: `python3 pipeline/merge.py data/waveN`, then
   `python3 pipeline/verify.py render data/waveN --assignments <assignment ids>` (renders only that search's new
   entries; batches of 3).
3. Launch one Opus agent per verifier batch. When it reports, record shortcomings, then
   `python3 pipeline/verify.py apply data/waveN` and `python3 pipeline/enrich.py data/waveN`.
4. Launch Opus enrichers for newly verified entries (two prompts per agent works well). Record their shortcomings.
5. Collect leads from enrichers in `leads.md`; before closing, add a `seed` assignment with a `projects` list, run
   `python3 pipeline/seed.py data/waveN --batch seed`, then merge, verify and enrich the seed records.
6. Close: final `verify.py apply`, confirm every verified entry has `enrich/raw/<slug>.json`
   (slug = `re.sub(r"[^a-z0-9]+","_", id.removeprefix("https://")).strip("_")`), run
   `python3 pipeline/render_lists.py` (and `pipeline/seeds_no_evidence.py` when seeds changed), run
   `python3 pipeline/check_pii.py`, commit, and update these notes.

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

Agent prompt shape (search/verify/enrich): "Read <prompt file> and carry out that task exactly; it names your output
file." plus a harness note: which sources to use (`gh`, prefer `gh api graphql` when REST search is rate-limited;
WebFetch; PDFs via curl + pdftotext; HN Algolia; arXiv; IACR ePrint; crossref.org since DBLP blocks bots), draft
output early, move on after 2 failed fetches, the privacy/scratch rules above, and the terse final-reply rule. Long
prompts go in a scratchpad file; the Agent call then says only "Your full instructions are in <path>. Read that file
first..." plus the final-reply rule.

## External limits

- `gh search` allows ~30 requests/min across all agents; the authenticated REST limit (5000/h) runs out at ~30-40
  concurrent agents, so agents fall back to `gh api graphql`, github.com pages or raw.githubusercontent.com.
- WebSearch has a per-session budget shared by all subagents (it ran out at 200/200 with ~28 agents running);
  prefer the arXiv, Semantic Scholar and HN Algolia APIs and draft from github.com pages first. kerkour.com asks
  not to be scraped.
- The Agent tool refuses a 21st concurrent subagent, so run 20 at a time and launch new work as reports arrive.
  Set `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=50` in `.claude/settings.local.json` (gitignored).
- Cloud sessions (claude.ai): egress depends on the environment's network policy. github.com (WebFetch),
  raw.githubusercontent.com (curl), gitlab.com and pypi.org usually work; api.github.com, arXiv, HN Algolia,
  crossref, DBLP, doi.org, publisher sites and most blogs are often blocked, which limits the b7/b8 searches and
  paper-based retiers. Papers checked into a repo are reachable via raw.githubusercontent.com. Give every agent
  `pipeline/cloud_harness.md` as an override of the prompt's tool notes and output path, and do not let agents use
  the mcp__github__ tools (their scope is this repository only).
- Tool output is capped near 30 KB, so dump 4-8 records per call with truncated fields.

## Lessons

Merging and ids:

- `merge.py` reads every raw file, including drafts of running agents; render verify batches with `--assignments`
  so drafts stay out. `verify.py apply` likewise picks up a verifier's draft before its report arrives (harmless;
  re-apply afterwards), and enrich.py then renders prompts for records whose verdict may still change: do not
  launch those enrichers until the batch reports.
- Records sharing one repo URL, or pointing at an already-known repo (SUPERCOP mirror, Crypto++), need a `paper:` id
  set in the raw file before merging. For a seed record whose repo is already verified in another wave, the order is:
  set the id in the raw file, merge, record `duplicate`, then `verify.py render`. `adddec.py` refuses `paper:` ids
  until the merge has happened, and `addretier_w.py` refuses an id until `verify.py apply` has put it in
  verified.json.
- Id drift: when a later raw file carries the same repo with a different name and category, the merged record flips
  to the higher-tier or higher-confidence copy, or gains a `#category` suffix whose position depends on raw-file
  sort order. After every merge, compare merged.json against the verify ids.json files; fix the ids.json of an
  unlaunched batch, record `duplicate` for a split id, and record `name`/`category` overrides to keep a verified
  record's identity.
- Decision ids must match merged ids exactly (lowercase canonical URL). Build decision and retier ids from the
  enrich/raw file's own `id` field rather than retyping them.

Decisions and retiers:

- Wrappers, ports and FFI bindings of an already-listed project, and category incumbents found again by a later
  search, get decision `duplicate`. `verify.py render` skips `duplicate` entries; `apply` honors
  keep/reject/duplicate and the override fields.
- Verifier "not-notable-tier-d" rejects are overridden with decision `keep` plus a shortcoming; only invalid or
  fabricated evidence stays rejected.
- Vendor-blog evidence from a company selling the product is retiered to C; numbers measured on code later fixed for
  correctness bugs, or built with flags absent from public sources, go to C.
- More reject precedents: an interpreter that pattern-matches the benchmark's function names and replaces them with
  native loops (R8/NoClip), a compile row that hits an in-memory cache (wazero via the PolkaVM benchtool), a RegExp
  fast path that never runs a regex (Pipa), design targets presented as measurements (r8e) and a hard-coded speedup
  table (zig-evm).
- Downgrade precedents: third-party numbers measured before a hot-path correctness fix (Paserati #550), a tuned fork
  measured in place of upstream (Topaz), a baseline crippled by a build default (AssemblyScript's tsc
  useDefineForClassFields), cross-run or cross-container comparisons (LangArena rows before a harness change,
  related_post_gen, Microbenchmarks CI jobs on separate VMs, plb2 rows added on different days) and crippled or
  asymmetric baselines (startup inside the timed region, -O0 or assert-enabled builds, a Debug build against -O2, GC
  never collecting while C frees). Same-task idiom differences (SwissTable against std::unordered_map, borrowed
  keys, stable against unstable sort) stay at their tier with the mechanism documented.
- Enrichers keep finding harness defects the verifier missed (re-keying on one side only, uninitialised buffers,
  cached pre-fix builds, single-threaded baselines by harness default, GPU-vs-CPU decode asymmetry, degenerate
  zero-field workloads, cross-run comparisons); each becomes a retier entry, and cross-run or no-valid-measurement
  cases go to D.
- Enricher findings that change a record (baseline, numbers, caveats) go in a retier file even when the tier stays.
  `add_decisions.py`/`adddec.py` apply only the override fields and are all-or-nothing (one unknown id rejects the
  batch), so maintenance_status, compiler_and_flags and claim fixes go through retier corrections. `verify.py apply`
  appends caveat corrections as "[retier] ..." addenda (write addenda, not rewrites) and replaces the other fields.
- Category overrides that move an entry to another wave's category need a `domain` override too, or
  render_lists.py shows the category under two domains.
- kostya/benchmarks rows are often older than the README's Versions table; record the measured toolchain, not the
  listed one.

Running agents:

- Pin enrichment pairs: gen_enrich.py must never rewrite an existing pair directory; new pairs are only built for
  unenriched prompts not already covered, numbered from the top, and it skips slugs that already have
  enrich/raw/<slug>.json. When a verified entry later turns `duplicate`, delete its enrich prompt and the unlaunched
  pair that held it before re-pairing.
- Agents killed by a usage limit or a worker restart usually leave complete output files behind: check each
  untracked enrich/raw file for the full 13-key set and a sensible confidence before deleting or relaunching, take
  shortcomings from its gotchas and status_note fields, and relaunch only the missing partner (as a single-prompt
  pair-NNNb variant). An agent that never reports and whose raw file is missing or stale needs a relaunch.
- Default search assignments to a C++ language filter; "any"-language passes are extra coverage.

Dates and rendering:

- Never bump a closed wave's `today` in assignments.json: `verify.py apply` stamps every applied verdict with it.
  Render seed prompts for a closed wave with its original `today`.
- `render_lists.py` writes `catalog/` (pages per domain, category and entry, JSONL and CSV) and the README's marked
  blocks; CI fails if a fresh render differs from the commit, so re-render before every data commit.

## Status

Current counts are in the generated block of `README.md`; the per-wave history (what each wave and backfill round
found, retiered and rejected) is in `docs/build-log.md`, newest first. Add a dated entry there when a wave or round
closes, and keep `docs/QUEUE.md` "Unfinished work" current.
