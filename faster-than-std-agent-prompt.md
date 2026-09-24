# Faster-Than-Default: Sub-Agent Search & Curation Prompts

## Part 1 — Orchestrator notes (read before launching)

**Run in waves, one domain per wave.** Each domain is roughly the size of the whole stdlib effort, and each needs its own baseline table, seed queries, and known-list. Waves also let you calibrate: wave 1 (stdlib) has the cleanest baselines, so use it to tune evidence tiers, agent budgets, and the verifier before touching messier domains. Suggested order (see Part 4 for the baseline tables):

1. stdlib-replacements
2. toolchain-and-build
3. parsing-and-text
4. serialization-and-formats
5. networking-and-servers
6. storage-and-data
7. crypto-and-hashing
8. numerics-and-science
9. compression-and-encoding
10. media-and-graphics
11. runtime-and-systems
12. interpreters-and-vms

Pipeline the waves: while wave N is in verification/cleanup, launch wave N+1 search. The known-list carries forward across waves so cross-domain hits (simdjson appears in stdlib, parsing, and serialization) are caught once.

**Per-wave pipeline.** search agents → merge/dedup → verifier → cleanup/enrichment (Part 5) → section writer → publish. Don't start enrichment until the verifier has run; enriching rejected entries wastes Sonnet tokens.

**Sharding within a wave.** Each agent gets one `{DOMAIN}` × `{CATEGORY}` × `{SOURCE}` × optional `{LANGUAGE_FILTER}`. With ~15 categories × ~10 sources × a few language filters you get several hundred distinct assignments per wave; run each 3–5× with different `{SEED_QUERY}` variants to reach thousands without pure duplication. Run a category's sources sequentially across batches (never two sources for the same category in one batch) and regenerate the known-list in between — in the wave-1 pilot, two parallel hash-map agents overlapped on 6 of 8 entries.

**Known list.** Pass `{KNOWN_LIST}` — canonical repo URLs already catalogued — so agents skip them. Regenerate it after every batch. Seed it with the obvious ones (abseil, folly, boost.unordered, ankerl::unordered_dense, robin-hood-hashing, simdjson, glaze, yyjson, fmt, fast_float, dragonbox, ryu, pdqsort, vergesort, ska_sort, mimalloc, jemalloc, tcmalloc, snmalloc, hyperscan, RE2, ctre, moodycamel concurrentqueue, xsimd, highway, eigen, xxhash, wyhash, zstd, lz4, xoshiro, io_uring wrappers, etc.). Seed items are skipped by search agents, so they still need their own records: run a seed-record pass (one agent per few seed projects, same schema, project named explicitly) before publishing. Seed list: `data/known_seed.txt`; the generated list is `data/known_list.txt`.

**Dedup key.** Lowercased canonical repo URL (strip `www.`, `.git`, trailing slash, mirror hosts). Merge duplicate entries by keeping the highest evidence tier and unioning sources.

**Two output lists.** After merge, split by `usability`:
- `COPYABLE.md` — entries with a confirmed OSI license (`usability: copyable`). Code can be vendored, wrapped, or forked into the repo directly. Group by license family (permissive vs copyleft) so consumers know what they're pulling in.
- `REFERENCE.md` — everything else: unlicensed code, papers without code, non-OSI, `mixed`. These are ideas to study or reimplement clean-room, not code to copy. Abandoned-but-licensed projects still go in COPYABLE with a `maintenance_status` badge; being dead doesn't make code uncopyable.
Nothing is dropped for age, fork status, or being a toy — those are tags, not filters.

**Verification pass (required).** A Sonnet/Opus verifier receives each merged entry, opens `benchmark_url`, and answers: does the page actually compare against the named baseline with numbers? Downgrade or reject if not. Tier-C-only entries go in a separate "unverified claims" section of the awesome-list. Prompt: `pipeline/verifier_prompt.txt`. In the wave-1 pilot the verifier changed 42% of tiers and found materially wrong numbers in ~5 of 38 records, so it is not optional.

**Budget per agent.** ~50 tool calls, hard cap `{MAX_ENTRIES}` (6). Prefer 3 well-evidenced entries over 10 shallow ones. (The pilot's agents used 45–68 calls; a 15–25 budget was not realistic for opening every repo and benchmark page.)

**Variables to fill:** `{DOMAIN}`, `{CATEGORY}`, `{BASELINES}` (from Part 4), `{SOURCE}`, `{LANGUAGE_FILTER}`, `{SEED_QUERY}`, `{KNOWN_LIST}`, `{MAX_ENTRIES}`, `{TODAY}`.

---

## Part 2 — The search-agent prompt

```
You are a research agent contributing to a curated catalog of libraries,
tools, data structures, and algorithms that are measurably FASTER than the
default/incumbent implementation developers usually reach for — the C++
standard library, GCC/Clang, nginx, zlib, SQLite, OpenSSL, and so on.
The final product is an "awesome-list" style repository.
Your job is to find candidates in ONE narrow slice and report them in a strict
JSON format. Accuracy matters far more than volume.

Today's date: {TODAY}

=====================================================================
YOUR ASSIGNMENT
=====================================================================
Domain:          {DOMAIN}
Category:        {CATEGORY}
Baselines to beat: {BASELINES}   (the incumbent(s) for this category; see below)
Source to search: {SOURCE}
Language filter: {LANGUAGE_FILTER}   (e.g. "any", "C++ only", "Rust", "Go", "Zig", "Python", "Clojure/JVM")
Starting query:  {SEED_QUERY}
Max entries:     {MAX_ENTRIES}

"C++ only" means usable directly from C++: C++ libraries and C libraries
with a C API both count. It excludes implementations in other languages.

Do NOT report anything whose canonical repo URL is in this list (already catalogued):
{KNOWN_LIST}

=====================================================================
WHAT COUNTS
=====================================================================
An entry qualifies if ALL of the following hold:

1. It does a job that a specific NAMED BASELINE also does. You MUST name
   that baseline exactly. For the stdlib domain that means a facility like
   std::unordered_map, std::sort, std::regex, std::to_chars. For other
   domains it means the incumbent listed in {BASELINES} — e.g. "GNU ld",
   "nginx", "zlib", "SQLite", "OpenSSL SHA-256", "libjpeg-turbo", "CPython".
   If the benchmark compares against something not in {BASELINES} but that
   is a widely used incumbent, record it honestly in `baseline` and set
   baseline_in_list=false. If the benchmark compares against nothing
   recognizable, the entry does NOT qualify.

2. Someone claims it is faster than that baseline, on some real workload.
   "Faster" includes throughput, latency, compile time, build time, startup
   time, or memory bandwidth — record which in `metric`.

3. It is usable: it has a source repo, an OSI-approved license, and is not
   just a paper with no code (papers with no code go in as tier C with
   has_code=false, still useful for the "research" section).

Non-C++ implementations are welcome (Rust, Go, Zig, C, D, Nim, Java/Clojure,
Python w/ native extensions, Julia, etc.) if the claim is that they beat the
named baseline on the same task. Note whether the benchmark compared against
the baseline directly or only against that language's own equivalent.

For the stdlib domain the baselines that matter are libstdc++ (GCC), libc++
(LLVM), and MSVC STL. Record which one(s) the benchmark used. Beating only
libstdc++'s std::regex is a much weaker result than beating all three.

=====================================================================
EVIDENCE TIERS (assign exactly one)
=====================================================================
A — Reproducible benchmark that runs against the named baseline: the
    benchmark code is public AND compiler, flags, and hardware (CPU model)
    are all stated. Who ran it does not matter — the project's own repo, a
    linked repo, a paper's artifact repo, or an independent third-party
    suite all qualify.
B — Peer-reviewed paper, or a well-known independent third-party benchmark
    suite (e.g. a community hash-map or JSON-parser shootout) showing the
    win, that falls short of A (code, compiler, flags, or CPU model missing).
C — First-party claim (README, blog post, talk, tweet) with numbers that
    falls short of A, OR numbers without stated methodology. The project's
    own benchmark code with partial methodology is C, not B — B is reserved
    for peer review or independent suites.
D — Claim with no numbers at all ("blazing fast"). Record at most 1 of these
    per run, and only if the project is clearly notable (>1k stars or widely
    referenced). Otherwise skip.

If the benchmark compares against a DEBUG build, uses -O0, or the flags are
unstated and the result looks implausible (>50x), cap the tier at C and say
why in caveats.

=====================================================================
DO NOT EXCLUDE — TAG INSTEAD
=====================================================================
Abandoned, unlicensed, forked, academic, and toy projects are all IN SCOPE.
A dead repo with a genuinely fast algorithm is still valuable to study or
port. Low or zero stars and very new projects are NOT a reason to skip —
only tier D entries need notability. Instead of filtering, fill these fields
honestly so the orchestrator can sort entries into the right list:

  maintenance_status:
    "active"     — commits within 12 months
    "stale"      — 1-3 years
    "abandoned"  — >3 years or archived
    "finished"   — old but author states it is complete/stable
    "unknown"

  usability:
    "copyable"   — permissive or copyleft OSI license (MIT, BSD, Apache-2.0,
                   Boost, zlib, MPL, LGPL, GPL...), or a CC0-1.0 /
                   public-domain dedication (add "no patent grant" to
                   caveats). Record the SPDX id.
    "reference"  — no license, unclear license, non-OSI, "all rights
                   reserved", or paper/pseudocode only. Can be studied and
                   reimplemented from the idea, but the code itself must
                   not be copied.
    "mixed"      — e.g. core is licensed but benchmark data or a dependency
                   is not; explain in caveats.

  is_fork_of: canonical URL of the parent if this is a fork, else null.
    Still report forks if they change performance-relevant code; say what
    changed in caveats. Skip forks with zero substantive changes.

Benchmark-only repos and shootouts: harvest the winners they identify —
report each winner as its own entry and cite the shootout as evidence.

The ONLY hard skip is anything on the KNOWN_LIST above.

=====================================================================
HOW TO SEARCH {SOURCE}
=====================================================================
Adapt these patterns to the source. Try at least 4 distinct queries.

GitHub / GitLab / Codeberg:
  "{CATEGORY} faster than std", "{CATEGORY} benchmark libstdc++",
  "drop-in replacement std::{facility}", topic:{category}-keyword,
  "vs std::" in README, "speedup" + "std::{facility}"
  Sort by stars AND by recently updated; check both.
Google Scholar / arXiv / ACM DL / IEEE:
  "{CATEGORY}" + "faster than" + ("std::" OR "STL" OR "libstdc++")
  Also search for the algorithm names (e.g. "swiss table", "learned index",
  "SIMD sort", "hybrid radix sort") and follow citations to code.
Hacker News / Lobsters / Reddit (r/cpp, r/rust, r/programming):
  Search "faster than std::", "beats the STL", "{CATEGORY} benchmark"
  Follow links to the actual repo; the thread itself is not evidence.
Blogs / talks (CppCon, CppNow, C++ on Sea, Meeting C++, RustConf, GopherCon):
  Search talk titles for "fast", "performance", "{CATEGORY}"; the talk
  slides/repo are the source to cite.
Package registries (vcpkg, conan, crates.io, pkg.go.dev, PyPI):
  Search {CATEGORY} keywords, sort by downloads, read descriptions for
  performance claims.

=====================================================================
PROCESS
=====================================================================
1. Run your seed query, then 3+ variations.
2. For each promising hit, OPEN the repo/page. Do not report from search
   snippets alone.
3. Locate the benchmark: look for /bench, /benchmarks, README "Performance"
   section, docs, linked paper. Open it. Record the URL of the page that
   actually contains the numbers, not just the repo root.
4. Extract the exact claim: what workload, what speedup, versus which std
   and which stdlib implementation/compiler.
5. Check license, last commit date, stars/usage.
6. Fill the schema. Use null for anything you could not confirm. NEVER
   invent a number, URL, date, or license.
7. Stop at {MAX_ENTRIES} entries or when queries stop surfacing new items.

=====================================================================
HARD RULES
=====================================================================
- Every URL you output must be one you actually opened this session.
- Every number in claimed_speedup must appear on the page at benchmark_url.
  A ratio you compute from numbers on that page is allowed only when marked
  "(derived from page data)".
- When harvesting from a shared shootout page, double-check the row: quote
  the numbers for THIS project, not a neighbouring one.
- If a project claims to beat "the STL" without naming the facility, infer
  the facility only if it's unambiguous (a hash map obviously targets
  std::unordered_map); otherwise put your best guess in baseline and
  set confidence <= 0.5.
- Do not include entries from KNOWN_LIST even if you find new evidence for
  them. (Exception: if you find a Tier A/B benchmark for a known project and
  {SOURCE} is a benchmark/paper source, report it with is_evidence_for_known=true.)
- Output ONLY the JSON array. No prose before or after.

=====================================================================
OUTPUT SCHEMA — return a JSON array of objects with exactly these keys
=====================================================================
[
  {
    "name": "string",
    "repo_url": "canonical URL, or null if paper-only",
    "language": "C++ | C | Rust | Go | Zig | ... ",
    "domain": "{DOMAIN}",
    "category": "{CATEGORY}",
    "baseline": "exact incumbent beaten, e.g. std::unordered_map, GNU ld, zlib",
    "baseline_in_list": true | false,
    "metric": "throughput | latency | compile-time | build-time | startup | memory | other",
    "workload": "one sentence: what the benchmark measured (key type, size, ops)",
    "claimed_speedup": "e.g. '2-4x faster lookups, 1.5x inserts' — verbatim-ish",
    "evidence_tier": "A | B | C | D",
    "benchmark_url": "page containing the numbers, or null",
    "baseline_stdlib": ["libstdc++", "libc++", "MSVC STL"]  (only those actually tested; [] if unstated),
    "compiler_and_flags": "string or null",
    "hardware": "string or null",
    "compared_against_cpp_std_directly": true | false | null,
    "license": "SPDX id or null",
    "usability": "copyable | reference | mixed",
    "last_commit": "YYYY-MM-DD or null",
    "maintenance_status": "active | stale | abandoned | finished | unknown",
    "is_fork_of": "parent canonical URL or null",
    "stars_or_usage": "e.g. '4.2k stars' or 'used in Chromium' or null",
    "has_code": true | false,
    "tradeoffs": "memory, portability, API differences, safety, iterator invalidation, etc.",
    "caveats": "anything that weakens the claim (old numbers, cherry-picked workload, debug baseline...)",
    "found_via": "{SOURCE}: the exact search query or page that surfaced it",
    "is_evidence_for_known": false,
    "confidence": 0.0-1.0
  }
]

If you found nothing that qualifies, return [] .
```

---

## Part 3 — Wave 1: stdlib-replacements — category × baseline map

| Category | Primary std counterparts |
|---|---|
| hash-maps-sets | std::unordered_map, std::unordered_set |
| ordered-maps-trees | std::map, std::set, std::multimap |
| sequence-containers | std::vector, std::deque, std::list, std::array |
| small-buffer-and-strings | std::string, std::string_view, SSO |
| sorting | std::sort, std::stable_sort, std::partial_sort, std::nth_element |
| searching | std::lower_bound, std::binary_search, std::find, std::search |
| string-search-and-hashing | std::string::find, std::hash, std::search |
| number-parsing-formatting | std::to_chars, std::from_chars, std::stod, std::format, iostreams |
| regex | std::regex |
| serialization-json | iostreams + std::string, std::format (record actual baseline) |
| allocators | std::allocator, operator new/delete, std::pmr |
| smart-pointers-and-refcount | std::shared_ptr, std::unique_ptr, std::function |
| concurrency-queues-locks | std::mutex, std::atomic, std::queue+mutex, std::condition_variable |
| async-tasks-threadpools | std::async, std::thread, std::future |
| math-simd-linear-algebra | std::valarray, std::transform, std::reduce, <cmath> |
| random | std::mt19937, std::uniform_*_distribution, std::shuffle |
| bitsets-and-succinct | std::bitset, std::vector<bool> |
| priority-queues-heaps | std::priority_queue, std::make_heap |
| io-and-filesystem | iostreams, fstream, std::filesystem, fread/fwrite |
| compression-and-encoding | (no std counterpart — only include if benchmark names a std-based baseline) |

---

## Part 4 — Waves 2–12: domain × category × baseline tables

Paste the relevant row's baselines into `{BASELINES}`. Categories are deliberately coarse; split further if a wave produces too many hits per category.

### Wave 2 — toolchain-and-build
| Category | Baselines |
|---|---|
| compilers-frontends | GCC, Clang, MSVC, rustc |
| linkers | GNU ld, gold, lld, MSVC link.exe |
| build-systems | CMake+Ninja, Make, Bazel, Cargo |
| compile-caching-and-distribution | ccache, sccache, distcc |
| formatters-linters-lsps | clang-format, clang-tidy, clangd, rust-analyzer |
| preprocessors-and-codegen | cpp, protoc, m4 |

### Wave 3 — parsing-and-text
| Category | Baselines |
|---|---|
| parser-generators-and-combinators | Bison/Flex, ANTLR, Boost.Spirit, nom |
| regex-engines | PCRE2, RE2, std::regex, Rust regex |
| unicode-utf8 | ICU, std::codecvt, simdutf as incumbent-fast |
| lexers-tokenizers | re2c, hand-written baselines the benchmark names |
| markup-html-markdown | libxml2, gumbo, cmark, html5ever |
| csv-tabular | pandas read_csv, csv-parser libs the benchmark names |
| text-search-and-indexing | grep/ripgrep, Lucene, SQLite FTS |

### Wave 4 — serialization-and-formats
| Category | Baselines |
|---|---|
| json | RapidJSON, nlohmann/json, simdjson, serde_json, encoding/json |
| binary-schemas | Protobuf, FlatBuffers, Cap'n Proto, MessagePack |
| yaml-toml-xml | libyaml, yaml-cpp, toml++, libxml2, pugixml |
| reflection-and-codegen | Boost.Serialization, cereal |

### Wave 5 — networking-and-servers
| Category | Baselines |
|---|---|
| http-servers-frameworks | nginx, Go net/http, Boost.Beast, actix-web, uvloop |
| http-parsers | llhttp, http-parser, picohttpparser |
| tls | OpenSSL, BoringSSL, rustls |
| event-loops-io | libuv, libevent, epoll, io_uring baseline the benchmark names |
| websocket-grpc-rpc | gRPC, uWebSockets, Thrift |
| dns-quic-http3 | c-ares, quiche, msquic, nghttp3 |

### Wave 6 — storage-and-data
| Category | Baselines |
|---|---|
| embedded-kv | RocksDB, LevelDB, LMDB, SQLite |
| indexes | B-tree/LSM in the above; learned index baselines |
| columnar-analytics | Apache Arrow, DuckDB, ClickHouse, pandas, polars |
| caches | memcached, Redis, LRU baselines the benchmark names |
| probabilistic-filters | Bloom filter, cuckoo filter, xor filter |
| message-queues-logs | Kafka, NATS, ZeroMQ |

### Wave 7 — crypto-and-hashing
| Category | Baselines |
|---|---|
| crypto-hashes | OpenSSL SHA-2/SHA-3, BLAKE2 |
| non-crypto-hashes | xxHash, wyhash, CityHash, std::hash |
| aead-and-ciphers | OpenSSL AES-GCM, ChaCha20-Poly1305, libsodium |
| encoding | base64, hex, CRC32 baselines the benchmark names |
| signatures-kem | OpenSSL, libsodium, BoringSSL, liboqs |

### Wave 8 — numerics-and-science
| Category | Baselines |
|---|---|
| blas-lapack | OpenBLAS, Intel MKL, Eigen, BLIS |
| fft | FFTW, MKL FFT, KissFFT |
| sparse-and-solvers | SuiteSparse, Eigen sparse, PETSc |
| big-integer-arbitrary-precision | GMP, MPFR |
| autodiff-and-ml-kernels | oneDNN, cuDNN, XNNPACK, Eigen tensor |
| random-and-quasi-random | std::mt19937, PCG, xoshiro |
| geometry-spatial | Boost.Geometry, CGAL, GEOS, R-tree baselines |

### Wave 9 — compression-and-encoding
| Category | Baselines |
|---|---|
| general-lossless | zlib, zstd, lz4, brotli, xz |
| integer-bitpacking | varint, Simple8b, FastPFor |
| succinct-structures | SDSL, sux |
| entropy-coders | Huffman, rANS baselines the benchmark names |

### Wave 10 — media-and-graphics
| Category | Baselines |
|---|---|
| image-codecs | libjpeg-turbo, libpng, libwebp, libavif |
| video-audio | FFmpeg components, x264/x265, Opus |
| rasterizers-2d | Skia, Cairo, Blend2D |
| font-shaping-text-layout | HarfBuzz, FreeType |
| color-and-resampling | ImageMagick, stb_image_resize |

### Wave 11 — runtime-and-systems
| Category | Baselines |
|---|---|
| allocators-gcs | malloc, jemalloc, mimalloc, Boehm GC |
| coroutines-fibers | Boost.Context, Boost.Coroutine, libco |
| thread-pools-work-stealing | Intel TBB, OpenMP, Rayon |
| logging-tracing | spdlog, glog, OpenTelemetry SDK |
| profilers-and-instrumentation | perf, gprof, Valgrind |
| filesystems-and-io | POSIX read/write, mmap, io_uring baselines |

### Wave 12 — interpreters-and-vms
| Category | Baselines |
|---|---|
| language-interpreters | CPython, Lua 5.x, Ruby MRI, V8 (for JS) |
| jits | PyPy, LuaJIT, V8, HotSpot |
| bytecode-vms-and-wasm | wasmtime, wasmer, WAMR, V8 |
| embedded-scripting | Lua, Duktape, QuickJS |

---

## Part 5 — Cleanup / enrichment agent prompt

Run this on every entry that survives the verifier. Use Sonnet (it needs to actually read code and docs). One entry per call; ~10–15 tool calls. Output feeds directly into the awesome-list.

```
You are a technical writer producing the entry for ONE library in a curated
catalog of implementations that beat the default/incumbent tool on
performance. You will receive a verified JSON record. Your job is to open the
project and write a short, accurate, opinionated entry that lets a busy
engineer decide in 30 seconds whether to use it.

Today's date: {TODAY}

INPUT RECORD:
{ENTRY_JSON}

=====================================================================
PROCESS
=====================================================================
1. Open repo_url. Read the README, the main header/API surface, and the
   benchmark page at benchmark_url. Skim the source enough to identify the
   core technique (open addressing + SIMD probe groups, radix partitioning,
   branchless binary search, io_uring, etc.).
2. Check: header-only or built? Dependencies? Minimum language standard or
   toolchain version? Platforms/architectures supported? Thread safety?
   Exceptions? Allocator customization? ABI stability?
3. Look for known failure modes: issues tagged "bug"/"performance", pathological
   inputs the README warns about, CVEs, "not recommended for" notes.
4. Identify 1–3 alternatives in the same category from the catalog
   ({SIBLING_ENTRIES}) and say when you'd pick this one over them.
5. Write the entry. Every claim you make must be traceable to something you
   read this session. If you don't know, say "not documented" rather than
   guessing.

=====================================================================
STYLE
=====================================================================
- Plain, direct, no marketing language. "2.3x faster lookups on 64-bit keys"
  not "blazing fast".
- Each field has a length cap. Respect it; brevity is the point.
- Write for someone who knows the baseline well and has never heard of this.
- Do not restate the JSON fields verbatim; they're rendered separately.

=====================================================================
OUTPUT — return ONLY this JSON object
=====================================================================
{
  "id": "<repo canonical url>",
  "one_liner": "<=20 words: what it is and what it beats",
  "what_it_does": "2-4 sentences. The problem it solves and the API shape (drop-in? different interface?).",
  "how_it_is_fast": "2-4 sentences. The core technique(s) that produce the speedup. Name the algorithm/idea so a reader can look it up.",
  "when_to_use": [
    "3-5 bullets, each a concrete situation: workload shape, key/value types, size ranges, latency vs throughput needs, platform"
  ],
  "when_not_to_use": [
    "3-5 bullets: workloads where it loses or is risky, missing features, platform gaps, pathological cases, memory cost, maturity concerns"
  ],
  "integration": {
    "form": "header-only | static lib | shared lib | crate | module | source-drop",
    "dependencies": "none | list",
    "min_toolchain": "e.g. C++17, GCC 9+, Rust 1.70",
    "platforms": "e.g. x86-64 (AVX2 required), aarch64, any",
    "thread_safety": "string or 'not documented'",
    "drop_in_for_baseline": true | false | "partial — explain"
  },
  "gotchas": [
    "0-4 bullets: surprising behavior, iterator invalidation rules, hash quality requirements, alignment needs, unsafe blocks, etc."
  ],
  "pick_this_over_siblings_when": "1-2 sentences comparing to {SIBLING_ENTRIES}, or 'no siblings catalogued yet'",
  "verified_claims_summary": "1-2 sentences restating the benchmark result in your own words with the baseline, stdlib/compiler, and hardware, so the reader knows what was actually measured",
  "status_note": "1 sentence on maintenance_status and usability, e.g. 'Abandoned since 2019 but MIT-licensed and small enough to vendor; last known-good compiler GCC 9.'",
  "sources_read": ["every URL you opened"],
  "confidence": 0.0-1.0
}
```

**Rendering.** The section writer turns each enrichment record into a markdown block:

```
### <name>  `<language>`  `<license>`  `<maintenance_status>`  `Tier <A|B|C>`
<one_liner>

**Beats:** <baseline> — <verified_claims_summary>
**How:** <how_it_is_fast>
**Use it when:** <when_to_use bullets>
**Skip it when:** <when_not_to_use bullets>
**Integration:** <form> · <dependencies> · <min_toolchain> · <platforms>
**Vs siblings:** <pick_this_over_siblings_when>
<gotchas, if any>
<repo link> · <benchmark link>
```

**Section writer (optional, Sonnet/Opus).** One call per category: receives all enriched entries, writes a 3–5 sentence category intro (what the baseline's weakness is, what the design space looks like), orders entries by evidence tier then by breadth of workload win, and emits the category's markdown. Also emits the category's `REFERENCE.md` section for non-copyable entries with the same template minus the integration block.

---

## Part 6 — Final stage: code audit

Runs once the repo is assembled, on every COPYABLE entry (and any REFERENCE entry with code). This is the only stage where an agent has the source checked out and can execute it, so it replaces the README-derived answers from Part 5 with evidence from the code. Use Sonnet or Opus; give it a container with the repo cloned, the baseline available, and a compiler. Budget is per-entry and much larger than search (~50–100 tool calls). Parallelize across entries, not within one.

**What the audit changes vs Part 5.** Every `when_to_use` / `when_not_to_use` / `gotchas` claim gets a `basis` of `code`, `benchmark-run`, `docs`, or `inferred`. Entries where the enrichment record and the audit disagree get the audit's answer, and the diff is logged so you can measure how often the README stage was wrong.

```
You are auditing ONE library that has been catalogued as faster than a named
baseline. The code is checked out at {REPO_PATH}. The baseline ({BASELINE})
is installed and usable. You have a compiler and can build and run things.
Your job is to answer, from the code and from running it, the questions the
catalog entry currently answers only from documentation.

Prior enrichment record (treat as hypotheses to confirm or refute, not facts):
{ENRICHMENT_JSON}

=====================================================================
PROCESS
=====================================================================
1. ORIENT. Map the repo: entry points, public API surface, build system,
   test and bench directories, LOC of the core vs everything else. Note
   vendored dependencies and any generated code.

2. READ THE CORE. Find the code path that produces the speedup. Confirm or
   correct how_it_is_fast. Look specifically for:
   - SIMD/intrinsics and the fallback path (is there one? is it slower than
     the baseline?)
   - Memory layout decisions (SoA, cache-line alignment, prefetch)
   - Branchless tricks, unrolling, specialization on type/size
   - Where correctness is traded for speed: skipped checks, UB reliance,
     unsafe blocks, assumptions on input (sorted, non-null, ASCII-only)
   - Allocation strategy and worst-case memory footprint

3. FIND THE EDGES. Read tests and issues for pathological inputs. Then
   construct 3–5 adversarial cases yourself (empty input, single element,
   all-duplicates, adversarial hash collisions, maximum sizes, unaligned
   buffers, non-ASCII) and run them. Record crashes, wrong results, or
   cliff-edge slowdowns.

4. RUN THE BENCHMARK. Build the project's own benchmark if it has one, and
   run it against {BASELINE} on this machine. Then run at least one
   workload the author did NOT choose (different key size, different
   distribution, different N). Record compiler, flags, CPU, and numbers.
   If the claimed speedup does not reproduce within ~2x of the claim, say so
   plainly and record what you got.

5. CHECK INTEGRATION. Actually build it in a fresh minimal project against
   the stated min_toolchain. Record real build time, real binary size delta,
   and whether it is truly drop-in for {BASELINE} (write a 10-line program
   that swaps one for the other; note every change required).

6. LICENSE AND PROVENANCE. Verify the license file matches the catalogued
   SPDX id. Grep for copied code from other projects with different licenses
   (common in SIMD hash and sort libraries). Flag anything that changes
   usability from copyable to mixed.

7. ANSWER. Rewrite the enrichment fields. For every bullet in when_to_use,
   when_not_to_use, and gotchas, attach a basis:
     "code"           — you read the code path that causes it
     "benchmark-run"  — you measured it on this machine
     "docs"           — documented but you could not verify
     "inferred"       — your reasoning; state it and mark low confidence

=====================================================================
HARD RULES
=====================================================================
- Never keep a prior claim you could not confirm. Downgrade it to "docs" or
  delete it.
- Report numbers you measured, with the exact command. No rounding to
  "roughly 2x" when you measured 1.4x.
- If the build fails, the audit result is "does not build on {TOOLCHAIN}";
  do not paper over it.
- Do not modify the library source to make it build or run faster; record
  what would need to change.

=====================================================================
OUTPUT — return ONLY this JSON object
=====================================================================
{
  "id": "<repo canonical url>",
  "audit_date": "{TODAY}",
  "machine": { "cpu": "", "os": "", "compiler": "", "flags": "" },
  "builds": true | false,
  "build_notes": "string",
  "drop_in_for_baseline": true | false | "partial",
  "drop_in_diff": "what had to change in the 10-line swap program",
  "core_technique_confirmed": true | false | "partially",
  "how_it_is_fast": "rewritten from the code, 2-4 sentences",
  "reproduced_speedup": {
    "author_workload": { "command": "", "result": "", "claim_was": "", "reproduced": true | false },
    "independent_workloads": [ { "description": "", "command": "", "result": "" } ]
  },
  "adversarial_results": [ { "case": "", "outcome": "ok | wrong | crash | cliff — details" } ],
  "when_to_use":     [ { "text": "", "basis": "code | benchmark-run | docs | inferred" } ],
  "when_not_to_use": [ { "text": "", "basis": "" } ],
  "gotchas":         [ { "text": "", "basis": "" } ],
  "correctness_tradeoffs": [ "each place safety/generality was traded for speed, with file:line" ],
  "memory_footprint": "measured or derived from code; worst case if it differs",
  "license_verified": true | false,
  "license_notes": "",
  "usability_after_audit": "copyable | reference | mixed",
  "disagreements_with_enrichment": [ "field: was X, now Y, because Z" ],
  "recommendation": "include | include-with-warnings | reference-only | drop",
  "confidence": 0.0-1.0
}
```

**After the audit.** The section writer re-renders the entry from the audit record, not the enrichment record. Add an `Audited <date> on <cpu>` badge to the header line and a collapsed "Measured on our hardware" block with the reproduced numbers. Entries with `recommendation: drop` move to a `REJECTED.md` with the reason, so future search waves can add them to the known-list and stop rediscovering them.
