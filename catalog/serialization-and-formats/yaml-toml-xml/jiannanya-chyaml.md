# chyaml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 YAML 1.2.2 parser/emitter whose 8-byte event tape builds about 2x faster than rapidyaml's arena tree on config-shaped YAML.

| | |
|---|---|
| **Beats** | rapidyaml |
| **Claimed result** | chyaml's fast 8-byte event tape parses at about 391 MB/s vs 184 MB/s for rapidyaml 0.16.0 building its arena tree: about 2.13x faster with about 13.18x less incremental memory (6.18 MB vs 81.49 MB) on a 4,627,797-byte, 50,000-record input. Across the 8-shape matrix it is 1.16x-2.16x faster per shape (byte-weighted aggregate 1.92x, geometric mean 1.90x) and uses 1.63x-14.55x less memory. Event tape vs DOM tree is not a like-for-like comparison. |
| **Workload** | Parses/materializes a 4.63MB synthetic YAML file (50,000 records, 15 alternating paired runs) plus an 8-shape workload matrix (mixed records, flat mapping, scalar sequence, nested mappings, flow sequences, quoted strings, sparse values/comments, long scalars) comparing chyaml's fast event tape against rapidyaml 0.16.0's arena tree. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X, Windows x64 |
| **Compiler and flags** | MSVC 19.44, CMake Release config with -DCHYAML_OPTIMIZE_FOR=SPEED (CMakeLists: /O2 /Gy /Gw /utf-8 on the chyaml target, IPO/LTCG on by default; executables /OPT:REF /OPT:ICF) |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/jiannanya/chyaml) · [benchmark](https://github.com/jiannanya/chyaml/blob/main/README.md) |

## Verdict

The author built both sides with MSVC 19.44 Release (/O2, LTCG on chyaml) on a Ryzen 9 9950X under Windows x64. Building chyaml's fast event tape over a 4.63 MB, 50,000-record generated file ran at about 391 MB/s, against 184 MB/s for rapidyaml 0.16.0 `parse_in_arena` into a Tree (2.13x), with 6.18 vs 81.49 MB of extra memory. An 8-shape generated matrix gave 1.16x (nested mappings) to 2.16x. These are first-party numbers from 2026-08-24, taken on code that predates the rewrite. They compare building the tape, without consuming any events, against building a full tree that includes an input copy, so treat 2x as an upper bound.

## Use it when

- One sequential pass over large, generated config or data YAML (block maps and sequences of plain scalars, simple double-quoted strings, short flow sequences) where event throughput matters more than a tree.
- Tight memory budgets: the fast tape reserves about 8 bytes per 6 input bytes and borrows the input. On the author's 3-8 MiB matrix inputs it used 4-10 MiB of extra memory, against 10-150 MiB for rapidyaml trees.
- You want a self-contained, MIT-licensed C++20 YAML library in two files (chyaml.cpp and chyaml.hpp) with portable scalar code and no SIMD or `-march` requirements.
- Long streams of many small, plain documents, where opt-in `parallel_documents` splits the work. The README reports about 2.4x with 8 workers on a 3.95 MB stream of 20,000 documents.

## Skip it when

- YAML with anchors or aliases, tags, block scalars (`|`, `>`), single-quoted or escaped strings, tabs, flow mappings, multi-line scalars or several documents. All of these leave the fast path, and there are no published complete-path-vs-rapidyaml numbers.
- You need fast random access or editing. chyaml's DOM was never benchmarked against rapidyaml's tree, and `node::find()` walks a mapping's children linearly (no key index).
- Strict validation of untrusted input. From reading the source, the fast builder accepts invalid lines such as `key: a: b` and `key: "a" "b"` as scalars instead of rejecting them. The 402-case conformance run goes through `stream_parser`, which never uses the fast path, and it checks only accept/reject, not the parsed events.
- Production use that needs a track record. The repo was created 2026-08-24 and has 8 commits, one author, 0 stars and no tags or releases. A rewrite of about 1,000 lines landed 2026-09-21, after the rapidyaml numbers were taken.
- Inputs of 4 GiB or more: offsets are 32-bit, so they are rejected.

## How it is fast

It parses in two tiers. A line-oriented fast builder accepts only a restricted subset: single-document block mappings and sequences, plain scalars, double-quoted scalars without escapes, scalar-only flow sequences, and comments. For each event it writes one 8-byte record (32-bit input offset plus 24-bit length and type bits) pointing into the borrowed input, with no copying, no unescaping and no line/column tracking; `next()` recovers line and column later with a monotonic scan. A 256-entry byte-class table sends the whole input to the complete recursive-descent parser on any tab, `& * ! { } [ ] | > '` or escaped quote. Colons are found with `memchr`, the tape is pre-reserved at input/6 records, and the DOM fast path preallocates the exact node count in an arena of 64-byte nodes, with stride hints for O(1) `at()`. It uses no SIMD, intrinsics or ISA flags.

## Compared with alternatives

Pick chyaml over rapidyaml (catalogued, and chyaml's own baseline) only for a sequential pass over simple config-shaped YAML where retained memory matters most. Pick rapidyaml for a mature, fast tree over full YAML. fkYAML, PipeYAML and libfyaml were measured against yaml-cpp, and yam and yeptris against libyaml, so no direct comparison with chyaml exists; chyaml's case rests on its borrowed 8-byte tape, not on a head-to-head.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake builds `chyaml` STATIC from chyaml.cpp and exposes `chyaml::chyaml` for add_subdirectory). You can also copy in chyaml.cpp and chyaml.hpp. A `CHYAML_SHARED` export macro exists, but the CMake file does not build a shared target. |
| **Dependencies** | none for YAML; links Threads::Threads (std::thread backs parallel_documents). A rapidyaml 0.16.0 source tree is needed only for the optional comparison executables. |
| **Minimum toolchain** | C++20, CMake 3.21+. The README says it is verified with MSVC 19.44, GCC 12.2 and Apple clang 17. |
| **Platforms** | any (portable scalar C++20, no SIMD or ISA flags). Benchmarked on Windows x64 (Ryzen 9 9950X) and macOS on Apple M4 Max. |
| **Thread safety** | not documented. From the source, all parser and document state is per instance, and the bench suite parses one `document` per thread over a shared read-only input. Sharing one document or parser across threads is not documented. `stream_parser` starts its own worker threads when `parallel_documents` is set. |
| **Drop-in for the baseline** | no |

## Gotchas

- The rapidyaml comparison times only `event_parser::reset_borrowed()`, which builds the tape. It never calls `next()`, so event consumption and the line/column scan are excluded. rapidyaml's timed loop clears its tree and arena, copies the input into the arena and builds a full tree on every iteration. Both sides label MiB/s as "MB/s".
- `allow_duplicate_keys = false` is ignored when input takes the fast path, because only the complete parser checks it. On the complete path the check scans the mapping once per key, so it is quadratic on wide mappings.
- `*_borrowed` calls keep views into your buffer, so the buffer must stay alive and not move. Node handles must not outlive their `document`. The header says event views are valid only until the next `next()` or `clear()`.
- On non-fast input, `event_parser` builds the full DOM plus a vector of event structs before returning the first event, and `stream_parser` parses every document up front, so neither one streams. `document::parse_*` keeps only the first document. The complete path does not catch `std::bad_alloc`. `parse_profile::compact` is undocumented; in the source its only effect is to skip the fast path.

## Known shortcomings

- The timed loop only builds the event tape and never consumes events, while rapidyaml's loop copies input and builds a full tree each iteration, so the \~2x is an upper bound. The fast path is never conformance-tested and, per the source, accepts invalid YAML such as 'key: a: b'; allow_duplicate_keys=false is ignored there. The rapidyaml comparison predates a \~1,000-line rewrite (2026-09-21) and was not re-run. Created 2026-08, one author, 0 stars.

## Caveats and trade-offs

First-party, self-run benchmark, not independently reproduced. The comparison is not like-for-like: chyaml's event tape (borrowed input, no tree) is compared with rapidyaml building a full tree through parse_in_arena, which also copies the whole input into the arena on every timed iteration. chyaml's own DOM is not compared against rapidyaml, and the author says the structures serve different access patterns. IPO is set on the chyaml library, but the rapidyaml library added via add_subdirectory does not get it (only the rapidyaml_compare executable does). The rapidyaml numbers were measured 2026-08-24 and the code has changed a lot since (the 2026-09-21 rewrite). Nested mappings is the weakest case (1.16x). The baseline is rapidyaml, a known fast YAML library, not a stdlib/default incumbent. Repo created 2026-08-24, 0 stars.

Reported speedups target chyaml's portable 8-byte fast-path event tape, which only covers common configuration-YAML shapes; input outside that subset falls back to a slower 'complete path' for full YAML 1.2.2 grammar (directives, complex keys, full block-scalar handling), where a separate matrix shows only 1.03x-7.22x; comparison executables link rapidyaml only for benchmarking, never into the shipped library.

## Maintenance

Active but very young: last commit 2026-09-21, 8 commits, one author, 0 stars, no releases. It is MIT-licensed and small enough to vendor (two files); pin a commit.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** README 'Performance snapshot' compares against rapidyaml 0.16.0. The benchmark code is public (tests/compare_chyaml.cpp, tests/compare_rapidyaml.cpp, tests/benchmark_scenarios.hpp, tests/run_comparison.py), and the compiler (MSVC 19.44), flags (Release plus CHYAML_OPTIMIZE_FOR=SPEED, which CMakeLists maps to /O2 /Gy /Gw with IPO) and CPU (Ryzen 9 9950X) are all stated. That meets A.
- **Verifier notes:** All numbers in the record match the README. rapidyaml v0.16.0 exists (released 2026-07-22). I kept tier A because code, compiler, flags and CPU are all public or stated. I added the event-tape vs DOM-tree and parse_in_arena copy caveats, which make the 2.1x an upper bound for like-for-like use. Metadata matches: MIT, 0 stars, not a fork, last commit 2026-09-21.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jiannanya/chyaml>
  - <https://github.com/jiannanya/chyaml/blob/main/README.md>
  - <https://github.com/jiannanya/chyaml/blob/main/CMakeLists.txt>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/compare_chyaml.cpp>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/compare_rapidyaml.cpp>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/run_comparison.py>
  - <https://github.com/jiannanya/chyaml/commits/main>
  - <https://github.com/biojppm/rapidyaml/releases>
- **Sources the enricher read:**
  - <https://github.com/jiannanya/chyaml>
  - <https://github.com/jiannanya/chyaml/blob/main/README.md>
  - <https://github.com/jiannanya/chyaml/blob/b9ce29d/README.md>
  - <https://github.com/jiannanya/chyaml/blob/main/chyaml.hpp>
  - <https://github.com/jiannanya/chyaml/blob/main/chyaml.cpp>
  - <https://github.com/jiannanya/chyaml/blob/main/CMakeLists.txt>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/compare_chyaml.cpp>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/compare_rapidyaml.cpp>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/benchmark_scenarios.hpp>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/run_comparison.py>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/conformance.cpp>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/materialize_test_suite.py>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/test_chyaml.cpp>
  - <https://github.com/jiannanya/chyaml/blob/main/tests/bench_suite.cpp>
  - <https://github.com/jiannanya/chyaml/commits/main>
  - <https://github.com/jiannanya/chyaml/commit/bdf05a6>
  - <https://github.com/jiannanya/chyaml/issues>
  - <https://github.com/jiannanya/chyaml/releases>
  - <https://github.com/jiannanya/chyaml/tags>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/jiannanya/chyaml`) · [data/wave4/enrich/raw/github_com_jiannanya_chyaml.json](../../../data/wave4/enrich/raw/github_com_jiannanya_chyaml.json) (enrichment confidence 0.6)

</details>
