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

## Status (2026-10-06)

- Waves 1-11 are finished except the open items below. Lists after the 2026-10-06 session: COPYABLE 1669,
  REFERENCE 193, REJECTED 29. The next open work is in QUEUE.md "Unfinished work" (wave 11 seed leads,
  the RetroWrite enrichment and paper-access retiers in data/wave11/leads.md; then wave 12).
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
