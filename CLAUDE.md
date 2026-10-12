# fastpp: working notes for Claude Code

These notes carry the project's conventions between machines. They were written from the
orchestrating session's memory on 2026-09-28; keep them current when a rule or lesson changes.

## Goal

A centralized list of the fastest C++ code (other languages later) so agents and developers can
find faster implementations and libraries for their projects. C++ comes first; C libraries callable
from C++ count. The spec is `faster-than-std-agent-prompt.md` (Part 4 lists each wave's categories
and baselines). Scripts are in `pipeline/`, data in `data/waveN/`, rendered lists in the repo root.

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
- **Tokens are not a concern:** raise or remove caps when it yields more or better results.
  Sonnet for search (get coverage from more search agents, not a bigger model), Opus for verify,
  enrich and re-tier checks.
- **QUEUE.md** holds later extensions (waves 13-14, cross-language claims, seed-list mining).
  Keep it out of the spec, pipeline and data until waves 3-12 are finished, unless the user pulls
  it forward. Its first section, "Unfinished work", is the open backlog of the wave loop (deferred
  searches, retier checks, seed passes); resume from there and keep it current.
- **Developer source repo:** it is private, so its entries are capped at tier C and link to a 404. Do not
  change its visibility or modify its checkout without an explicit instruction.
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
   `python3 pipeline/render_lists.py`, commit, push, and update these notes.

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

## Status (2026-10-13)

- Waves 13 and 14 closed and the single enrichment pass (wave 1 stdlib seeds, wave 13, wave 14) finished on
  2026-10-13; QUEUE extensions 2 (whole-stdlib decomposition, run as wave 1 stdlib seeds: 10 entries), 3 (wave 13)
  and 4 (wave 14) are done. Lists: COPYABLE 2689, REFERENCE 263, REJECTED 41; tiers A 594, B 475, C 1638, D 245;
  2953 verified entries across all waves, every one enriched except RetroWrite (user hold); SEEDS_NO_EVIDENCE 620.
  Every category sits in one domain (cafs-lib needed a `domain` override to stdlib-replacements). Next: QUEUE
  extensions 5-6 (per-language curated lists, dynamic pages), the paper-access retiers and thin-yield re-runs
  listed in QUEUE.md "Unfinished work", and the presentation pass.
- Wave 13 (assembly-simd-kernels-and-wasm) closed 2026-10-12: 56 raw files (b1-b8 for all 7 categories plus seed
  passes), 344 merged, 118 verify batches, 303 verified (A 43, B 21, C 187, D 52; copyable 270, reference 30,
  mixed 3; wasm-libraries-and-apps 73, simd-intrinsics-libraries 58, assemblyscript-and-wasm-langs 46,
  hand-written-asm-kernels 45, asm-level-string-and-memory 34, assemblers-and-asm-tooling 32,
  wasm-runtimes-and-compilers 6, plus 9 filed in other waves' categories by override), 37 duplicates, 3 rejects for
  invalid evidence (tslime/simdmatrixalgorithm computes wrong answers; unconfirmedlabs/bcs measures TypeScript
  codegen while the bcs-zig wasm build is never called, Go-stdlib-libp2p precedent; industrial-algebra/orlando
  README table predates any benchmark, r8e precedent). Retier files retier-01 (2), retier-02 (1) and the
  enricher-driven retier-03 (156 entries): up to A dioxus, iced, simd-radix-sort, yaxpeax-x86, cafs-lib,
  positional-popcount, pqm4, corvus, neon-ntt, ultraviolet, quickenshtein, ermig1979/Simd, udis86, BLAKE3; to B
  bls-eth-wasm, ispc, loro, validateutf8-experiments, minotaur, source-map, rust-dominator, leptos,
  ppopp2017_artifact, vectorvisor, stoke, sycamore, unison, wasm-bindgen, faster-utf8-validator; 68 moved to C
  (asymmetric flags, first-party provenance gaps, numbers on code later fixed: fastnoise2, almide,
  parallelreductionsbenchmark, libgcrypt, libco, absurd-sql, argminmax, diamond-types, md5-simd, constantine,
  nasm, tinymembench, markdown-wasm, wasmtime-mte, simd-sort, uasm and others); 33 to D (no valid measurement,
  degenerate workloads, stale or never-run numbers: supercoder, memcpy_benchmark, ttf2woff2-wasm, faster,
  kmstrsearch, intel-intrinsics, mmemmove, brepkit, wasm-runtime-performance, ai-kernel-optimizer, tar-wasm,
  md5-wasm, memcpy_fast, clipper2-wasm, alphadev, sax-wasm, autozig, webmscore, wasmboy, camaro and others).
- Wave 14 (other-languages-faster-than-c-cpp-asm) closed 2026-10-13: 48 raw files (b1-b8 for all 6 active
  categories; historical-and-minimal yielded nothing cataloguable), 324 merged, 110 verify batches (107 files after
  deletions and re-renders), 274 verified (A 63, B 16, C 139, D 56 after enrichment; the verifier stage ended at
  A 73, B 21, C 157, D 23; copyable 254, reference 20; systems-and-safety 62, string-and-text 57, web-and-serving
  53, runtime-jit-beats-aot 45, numerics-and-arrays 35, concurrency-runtimes 21, one http-servers-frameworks by
  override), 49 duplicates (second claims on listed repos carry `paper:` ids), 1 reject (dev0x13/gemm-benchmark-2023
  Mojo kernels do not compute a full GEMM). Record ids are `lang:<language>/<owner>/<repo>#<benchmark>`, one row per
  benchmark. Enricher-driven retier-01 (274 entries): to D rust-sort, zog, statico, fastGPT, EvoTrees.jl, monolake,
  ziggit, ranwalk, SymbolicUtils.jl, FFTA.jl, Platinum Searcher, wut-server, awkrs, DiffEqGPU.jl, Traefik, PDFOxide,
  xerg, during, related_post_gen (C3, D and Rust rows), Chapel fbench, Erlang and Go thread-ring, yosssi
  Go-vs-nginx gist, JuliaLang Microbenchmarks userfunc_mandelbrot (Fortran and Julia rows: the project's own 2026
  data shows parity), xemantic almost-pseudo-random, alya Bun binary trees, AcceleratedKernels LJG, Lingua Franca
  Savina (actor-system startup charged to the CAF and Akka baselines only), Pony message ring (the Pony example
  runs one of its repetitions), c-blake dups (author's own like-mode run has jdupes faster); to C sambamba,
  llama2.zig, zipir, Futhark, zroar, hpla-rs, ioxide, needletail, PowPow, Kairos, Thruster, TrueAsync, libbzip2-rs,
  Undertow, JSON3.jl, Koka cfold (C++ port copies the spine per Add), OCaml benchLANG binary trees (C frees inside
  the timer, OCaml never collects), rustc compile throughput (unlocked rustup switches mid-run); up to A fib; to B
  hist-rs, hck, runiq. Name correction: kostya/jit-benchmarks k-nucleotide measures the OpenResty luajit2 fork.
  Category override bitdp to string-and-text. Open: paper-access retiers and seed leads in data/wave14/leads.md
  (Savina TACO 2023, Rewrite-it-in-Rust CBET paper, NPB-Rust arXiv 2502.15536, ixy ANCS 2019, plus the second-claim
  and project leads listed there).

## Status (2026-10-11)

- QUEUE extension 1 (seed-list mining, awesome-cpp and awesome-c, rounds 1 and 2) closed 2026-10-11: 152 seed groups
  (`data/waveN/raw/wN-mine-*.json`, about 7 seeds each), 324 raw records, 266 verified (A 39, B 41, C 153, D 33; wave 1
  68, wave 8 37, wave 11 26, wave 5 27, wave 4 28, wave 6 17, wave 10 18, wave 3 15, wave 12 11, wave 7 8, wave 9 6,
  wave 2 5), 637 no-evidence seeds in `data/seeds/no_evidence/` rendered to SEEDS_NO_EVIDENCE.md (620 after dedup).
  Lists: COPYABLE 2155, REFERENCE 210, REJECTED 36; tiers A 486, B 438, C 1309, D 132. Every verified entry is
  enriched except RetroWrite (user hold). Round 2 (2026-10-11) ran under the user's order "searches and verifies
  first, enrichment at the very end": 23 backfill groups (w10-mine-m to t, w11-mine-e to o, w12-mine-d to g), 26
  verify batches (w7 54-55, w8 172-179, w9 67, w10 112-119, w11 56-62, w12 98-100), then one enrichment pass of
  37 Opus pairs (73 entries across waves 5-12). Enricher-driven retiers from that pass: down PostgreSQL, MySQL and
  ODB to D (cross-run comparisons), Crypto++ and Botan to D (harness UB; OpenSSL re-keyed per message), clBLAS to D,
  ThreadPool to D (degenerate benchmark), GStreamer B to C (single-threaded FFmpeg baseline), Psi4 B to C, SHOGUN
  B to C (unequal k-means work, later rewritten), PEGTL B to C (stale cached build), TensorFlow B to C (asymmetric
  DLPerf harness), libfacedetection A to C (numbers predate PR #383), Box2D A to C, ONNX Runtime A to C, Ultimate++
  A to C, Boost.Log B to C, OpenEXR A to B; up G3log B to A (Quill benchmark), Sophia D to C (Howard Chu gist),
  MuJS C to B. Retier files: w5 retier-03, w6 retier-03/04, w7 retier-03, w8 retier-18, w9 retier-08, w10
  retier-40, w11 retier-05, w12 retier-02. Second claims on already-listed repos (FFmpeg ffvp9, OpenCV DNN,
  Boost.Fiber, icey, oneTBB parallel reduce, AngelScript, ChakraCore, pocketpy, QuickJS re-seeds) carry `paper:`
  ids with decision `duplicate`. Domain overrides now keep every category inside one domain. Next: QUEUE
  extension 2 (whole-stdlib decomposition), then waves 13-14.

## Status (2026-10-06, kept for history)

- Waves 1-12 are finished except the open items below. Lists after the 2026-10-07 backlog seed sweep: COPYABLE 1905,
  REFERENCE 202, REJECTED 34. The next open work is in QUEUE.md "Unfinished work" (wave 11 seed leads and the
  RetroWrite enrichment, wave 12 seed leads and paper-access retiers in data/wave12/leads.md; then the
  QUEUE extensions: waves 13-14, cross-language claims, presentation).
- Backlog seed sweep (2026-10-07, QUEUE "Unfinished work"): 29 uncatalogued leads from data/wave{8,9,10,11,12}/leads.md
  seeded in one pass (w8-seed-m, w9-seed-d, w10-seed-e/f, w11-seed-a, w12-seed-e; 6 Sonnet agents), 12 verify batches
  (w8 162-163, w9 63, w10 104-107, w11 50, w12 92-94), 22 verified and enriched, 4 duplicates (mps-flash-attention is a
  binding of metal-flash-attention, YAFU shares avx-ecm's only claim, goant is a Go port of ant, dsx-ai-factory/
  model-streamer is the renamed run-ai repo, recorded with a repo_url correction), 0 rejects. New A entries:
  tsl::array_map (wave 9, hash-maps-sets by category override), ConvectionKernels (wave 10), evm.zig (wave 12); B:
  JPEGDEC, hxcpp, Cuik; C or D for the rest (bluebox, zurand, SpLLT, bzip2gpu, DeLZSA repo 404, zenquant not faster,
  BoofCV, Canvas-Txt, nssfactory, honeydiff withdrawn 6x, Simd slower than OpenCV in user issues, scany, clownresampler,
  angelsea, Box86, FAFO). Enricher-driven retiers: avxbls-sig B to C (harness compares SwiftEC hashing against blst's
  SSWU), LC A to C (warm second run vs cold baselines, generic-arithmetic prefixes), AssemblyScript-style caveat
  corrections for hxcpp (JS rows double-counted), zurand (randompack built without AVX2), evm.zig (mock-host storage
  rows, stale baseline versions), BoofCV (unequal kernels), Canvas-Txt (cached mode, UAX-29 breaks), nssfactory
  (bm3dcuda BM3Dv2 ambiguity), JPEGDEC (TJpgDec not at its fastest; open OOB write #119), bzip2gpu (stateless RLE1
  decoder, CRC unchecked), Simd, FAFO (precomputed write sets), Box86 (stale). Retier files: wave8 retier-15, wave9
  retier-06, wave10 retier-39, wave11 retier-02, wave12 retier-01. Wave-aware helper copies (WAVE=N) of check_ids,
  addretier, gen_enrich and mk_verify live in the scratchpad; gen_enrich must skip prompts of entries later marked
  duplicate (stale prompts for maskedvbyte, iczelia/bzip3 and nanorand-rs were deleted). RetroWrite (wave 11) still
  needs the user's go before its enricher is relaunched.
- Wave 12 (interpreters-and-vms) closed 2026-10-06 in one cloud session: searches b1-b8 for all 4 categories
  (32 raw files; b7/b8 on WebSearch snippets plus github.com since blogs and HN were blocked, 36 records) plus
  seed-a..d (28 lead projects); 239 merged, 90 verify batches with 236 verdicts (confirm 209, downgrade 22,
  reject 5), 220 verified (A 38, B 62, C 112, D 8; copyable 214, reference 3, mixed 3; jits 57,
  embedded-scripting 56, bytecode-vms-and-wasm 53, language-interpreters 50, plus 4 filed by category override),
  every verified entry enriched. Rejected for invalid evidence: R8/NoClip (interpreter pattern-matches the
  benchmark's function names and replaces them with fused native loops, hard-coded pass_hash), wazero (PolkaVM
  benchtool compile row hits an in-memory module cache; MQF precedent), Pipa (RegExp suite fast path does a
  literal find, no regex runs; stb-zip precedent), r8e (memory figures are design targets copied from
  ARCHITECTURE.md) and zig-evm (README 5-6x table is a hard-coded array in src/benchmark_demo.zig; zokio
  precedent). 14 duplicates: LuaJIT Remake second id, libriscv second id, lua-aot and quickjs-ng suffixed ids,
  wasm-compiler suffix, rquickjs, bare, zig-mquickjs, OpenResty luajit2 (fork of LuaJIT with an anecdote only),
  fastschema/qjs (quickjs-ng on wazero), go-quickjs (Go port of quickjs-ng), ulua (Rust port of Luau),
  cinderx (same project as cinder). Retier file data/wave12/verify/raw/retier-01.json (82 entries): up to A
  fakelua, julia, GraalPython, ruby/ruby YJIT, CPython JIT, daScript, Apogee, wazy, goja-perf, musql, Loko, jz,
  jrsonnet, Zipp; to B WasmNow (copy-and-patch paper via a github.io mirror), Luau, Moddable, TruffleRuby,
  Wizard (OOPSLA 2022 artifact), wasmer, Graal, Pythran, evmone, Guile, revmc (SkelOT artifact); down
  Paserati A to C (numbers predate inline-cache fix #550), Topaz A to C (kostya fork breaks hash semantics,
  warm best-of-5 vs one cold CRuby iteration), pevm A to C and vnmakarov MJIT A to C (first-party, collapsed
  empty-loop row), AssemblyScript C to D (JS baseline crippled by useDefineForClassFields, reproduced 7x),
  zig-js and tpy-lang to D; many caveat corrections (Web49, Zef richards 20x loop, Regorus stale v0 commands,
  pocketlang module-scope Python loops, Wizard validation-excluded timer, Bigloo I/O rows, Quirrel swapped
  f2s/s2f rows, Cyber stale). Keep-and-document overrides for every verifier "not notable" reject. Open: seed
  leads in data/wave12/leads.md (angelsea, goant, Box86, hxcpp, fafo, 0xjojoex/evm.zig, Cuik, LC Scheme),
  paper-access retiers (Instrew VEE'21, TPDE, Box64 EuroSys, aWsm, WARP, rv32emu VMIL, HHVM, Deegen, Pallene,
  YJIT, mutable EDBT 2023 and ADC 2023 arXiv 2311.04692, Higgs arXiv 1507.02437), repo_url overrides to
  consider (kostya/topaz, lmcad-unicamp/riscv-sbt), and cross-wave leads (xsum, matprod, qj, tsv-utils,
  Turso, splintr) parked in QUEUE.md.
- Wave 11 (runtime-and-systems) closed 2026-10-06 in one cloud session: searches b1-b8 for all 6 categories
  (48 raw files; b7/b8 on WebSearch snippets since blogs and HN were blocked) , 147 merged, 49 verify batches,
  144 verified after three duplicate folds (A 19, B 19, C 92, D 14; copyable 125, reference 17, mixed 2;
  allocators-gcs, coroutines-fibers, filesystems-and-io, logging-tracing, profilers-and-instrumentation,
  thread-pools-work-stealing). Six verifier rejects were overridden to keep with shortcomings (Neco, llco,
  heapusage, Tracy, memtrail, E9Patch: no baseline or not faster); none rejected for invalid evidence.
  Duplicates: ForkUnion (second id), Morgan Stanley binlog (hyphenated id), google/sanitizers (same tool and
  numbers as the llvm-project ASan entry). Retier file data/wave11/verify/raw/retier-01.json (24 entries):
  up to A ThunderBolt-HT; to B Trio (SOSP paper from a repo mirror) and FastMap (author thesis from a repo
  mirror); to C obstack A, v8malloc A (competitor columns probably ran v8malloc itself), Marl D; to D
  fc_malloc (benchmarked a different file with bugs), dp::thread_pool (timed submission, never waited), hop
  (startup-dominated), memtrail; claim or licence corrections for ripgrep, zlob, NanoLog (Iyengar111, MIT),
  IsoAlloc ('jemalloc' row timed IsoAlloc), tbox, Tracy (2.25 ns/zone overstated 12x), ArenaAllocator, FluxIO
  and others. Open: RetroWrite has no enrich file (its enricher was stopped by a safety classifier mid-write,
  shortcomings recorded from its report; ask the user before relaunching), no seed pass was run.
- Wave 10 (media-and-graphics) closed 2026-10-05 across three cloud sessions (2026-10-03 to
  2026-10-05): searches b1-b8 for all 5 categories (40 raw files; b7/b8 on WebSearch snippets plus
  github.com, HN and blogs blocked) plus seed-a..d (32 lead projects); 276 merged, 103 verify
  batches with 269 verdicts (confirm 223, downgrade 41, reject 3, duplicate 2), 254 verified
  (A 28, B 22, C 174, D 30; copyable 230, reference 19, mixed 5; image-codecs 72, video-audio 58,
  color-and-resampling 57, rasterizers-2d 33, font-shaping-text-layout 23, plus 9 unicode-utf8,
  1 general-lossless and 1 websocket-grpc-rpc filed by category override), every verified entry
  enriched (128 enricher pairs). Rejected for invalid evidence: Imageflow (bench.sh backgrounds
  the tool with an unquoted '&', so hyperfine timed job launch; MQF precedent), fast_resize (NEON
  bilinear path wraps int16 and outputs 0 for channels at or above 128; stb-zip precedent),
  ucstrcase (self-comparison hits the s == t early return), zenwebp (numbers from an incomplete
  encoder, own parity report shows it slower) and av2-turbo (no encoder in the repo, disabled
  CPU-only perf test). 17 duplicates (wrappers and ports: sharp, net-vips, jpeg4py, pyspng,
  python-soxr, skia-canvas, @napi-rs/canvas, resvg-js, agg-rust, edge264-mvc, rusty_png, trez,
  nvavif-py, gamut, soundkit, savonet/shine, bc7enc_rdo tables identical to bc7enc). Retiers are
  in data/wave10/verify/raw/retier-{01..38}.json; tier moves: bc7e C to B and NV_path_rendering
  C to B (papers and independent runs reached), libspng B to A (wuffs doc/benchmarks.md),
  giflib-turbo D to C, pngencoder C to B (FPNG-Java JMH), bcdec D to C (aras-p harness, capped by
  the later-fixed-bug rule), muSkia D to B (camera-ready OOPSLA2 paper in bhargavkulk/skia-paper:
  1.12x geomean, not 18.7%); down: yuv2rgb A to C and libjxl fjxl A to C (numbers from code later
  fixed), uniwidth A to C (bug in hot path), FFmpeg swscale B to C, LunaSVG B to C (resvg-py
  baseline built at opt-level z), Smolscale, lodepng-turbo, RGB2Y, TGFX and libqoi to D. Many
  entries kept with harness flaws documented (opencodecs PackBits row an artifact, imgdiff claim
  obsolete, kb and fastGaussianBlur flagged not faster, sst-basic-blocks timed copy reads its
  table out of bounds).
- Wave 9 (compression-and-encoding) closed 2026-10-03: searches b1-b8 for all 4 categories
  (34 raw files, b7/b8 thin: blogs and HN blocked, 17 records) plus seed-a/b (13 lead projects);
  150 merged, 61 verify batches with 148 verdicts (confirm 123, downgrade 21, reject 4), 136
  verified (A 33, B 21, C 74, D 8; copyable 124, reference 10, mixed 2), every verified entry
  enriched. Rejected for invalid evidence: NZ1 (README table contradicted by its own tests.txt)
  and SnellerInc/iguana (decoder unimplemented, ClickHouse port slower than ZSTD); torch_ans and
  miniz rejects overridden to keep. Duplicates: zlib-rs, iczelia/bzip3, fast-pack/maskedvbyte,
  quickwit bitpacking, go-simd/bitpack, brotli, miara (PTHash port), pzip (klauspost wrapper),
  m77rip (misa77 port), hybrid-fenwick-tree (now in sux). Retiers in
  data/wave9/verify/raw/retier-{01..05}.json: 01 FastPFor C to A (SPE paper on the paperhub S3
  mirror); 02 fifteen lzbench 2.4 entries B to A for consistency with FastLZ (public Makefile
  flags, gcc 15.2.0, EPYC 9555P); 03 genedex restored to A (quadrank precedent); 04 fdeflate D
  to B and jtkukunas/zlib C to B on independent numbers; 05 PISA A to C (search-benchmark-game
  driver returns fewer than k docs and mis-parses queries; moved to text-search-and-indexing).
  ZipNN moved to general-lossless (vendored FSE Huffman).
- Wave 8 (numerics-and-science) closed: searches b1-b8 for all 7 categories and two seed passes
  (52 projects) plus seed-j/k/l merged; 404 verdicts (confirm 353, downgrade 37, reject 14), 398
  verified (A 74, B 78, C 221, D 25), every verified entry enriched. Retier checks 12-14
  (2026-10-03) re-tried 13 blocked papers: only gpuNUFFT moved (D to C on cufinufft issue #126);
  arXiv, ACM, IEEE, Springer, Dagstuhl, archive.org and zenodo all stay blocked here. Rejected for invalid evidence: SIMDxorshift,
  SIMD-MT, ra_prng, CUDA-L1, OxiBLAS, cpp-matmul; the other rejects were overridden to keep per
  the keep-and-document rule. Retiers are in data/wave8/verify/raw/retier-{01..14}.json (08 PFT
  C to B on the KDD paper; 09 metal-float64 usability to reference; 10 DASP B to C on harness and
  correctness evidence; 11 vpxyz/xorshift A to C on generator bugs).
- b7/b8 in this environment ran on WebSearch snippets plus github.com, since HN Algolia, HN
  threads, arXiv and most blogs were blocked; their yield was thin (55 records).
- Waves 9-12 are set up (2026-10-01): `data/wave{9,10,11,12}/assignments.json` (152 assignments,
  19 categories x b1-b8) and leads.md; b1/b2 prompts rendered. Re-render b1/b2 before launching a
  later wave so its known list is current. zlib-ng and libdeflate are already filed under wave 9's
  general-lossless category.
- Cloud-session workflow that worked on 2026-10-03: 8-10 agents at a time (Opus verifiers, then
  Opus enrichers with two prompts each; Sonnet searches and seed passes), record each report and
  push before launching the next; no usage-limit kills across wave 9 (about 110 agents). One
  agent left pip wheels in the repo root; tell agents never to pip download inside the repo and
  delete strays on sight. Enrichers often read code the verifier did not: when they find a
  correctness bug behind the measured numbers, write a retier file rather than only a
  shortcoming. Paper PDFs on an author's USERNAME.github.io repo (and hpcrl/ICS2025-webpage) are
  reachable through raw.githubusercontent.com even when the site itself is blocked.
- Decision ids must exist in verified.json: two decisions were recorded under mistyped ids (rusty_alloc,
  aw-backtrace) and had to be re-keyed; check ids against the verified list before recording (the scratchpad
  adddec.py wrapper refuses unknown ids). Hyphen, underscore and case variants of one repo (fork_union and
  forkunion, morgan-stanley and morganstanley) slip past merge: scan verified ids with punctuation stripped
  before enrichment. Never `git add` a whole raw directory while agents run; stage named finished files.
