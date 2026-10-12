# teptris

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> C99 TOML parser/emitter with a zero-copy arena DOM; its own benchmarks show 5-8x toml++ parse throughput.

| | |
|---|---|
| **Beats** | toml++ (tomlplusplus) |
| **Claimed result** | Run-3 table (M1 Max, min-of-10, MB/s): teptris is 5.2-8.5x toml++ v3.4.0 on all 9 shapes (array_heavy 312 vs 60, scalar_float 186 vs 22, table_heavy 256 vs 38) (derived from page data). Against the best competitor per shape in the same table (tomlc17, cpptoml or tomlc99) it is 2.7-3.6x (derived from page data). toml11 is 116-2247x slower by ms (derived from page data). Latest ledger entry (2026-09-25, v0.1.27, 4 gate shapes): 4.13-5.84x the best competitor (mixed 408 vs tomlc17 98.7 MB/s, cargo_like 379 vs cpptoml 81.1, deep_tables 418 vs tomlc99 84.1, table_heavy 402 vs cpptoml 68.8). The ledger's own summary lines (3.2-7.5x toml++, 2.0-2.8x tomlc17, 1.9-3.5x cpptoml, '5.2-8.2x the best competitor') do not match its run-3 table: 5.2-8.2x is roughly the toml++ ratio, not the best-competitor ratio. |
| **Workload** | Min-of-10 in-memory parse throughput (MB/s) on a seeded 9-file synthetic TOML corpus (array_heavy, cargo_like, datetime_heavy, deep_tables, mixed, scalar_float, scalar_int, scalar_string, table_heavy; 248KB-1.5MB each) against tomlplusplus v3.4.0, tomlc99, tomlc17, cpptoml, and toml11 v4.2.0. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max (Darwin arm64) |
| **Compiler and flags** | teptris and the tomlc99/tomlc17 static libraries: CMake Release (-O3 -DNDEBUG) with CMAKE_INTERPROCEDURAL_OPTIMIZATION on (ledger: -O3 -DNDEBUG -flto=thin). The bench_parse target, which compiles the header-only C++ competitors (toml++, toml11, cpptoml), adds -O2 after the Release flags (benchmarks/CMakeLists.txt), so those baselines effectively build at -O2. Compiler and version not stated (Darwin arm64). From 2026-09-16 the ledger's rounds may use PGO for teptris only (TEPTRIS_PROFILE_USE; competitors stay flag-free), and the 2026-09-25 entry does not say whether PGO was on. |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/leptris/teptris) · [benchmark](https://github.com/leptris/teptris/blob/main/benchmarks/LEDGER.md) |

## Verdict

First-party results on an Apple M1 Max (unnamed compiler; min-of-10 in-memory parse of nine seeded synthetic 0.25-1.5 MB files): early teptris (v0.1.0-era) ran 186-335 MB/s against toml++ v3.4.0's 22-60 MB/s (5.2-8.5x), and 2.7-3.6x the best of tomlc17, cpptoml and tomlc99. The latest ledger entry (v0.1.27, four shapes, 379-418 MB/s) puts it at 4.1-5.8x the best competitor. teptris is built with -O3 plus ThinLTO (and possibly PGO), while the header-only C++ competitors build at -O2, and the JSON artifact the ledger cites is empty. The project's own CI artifacts from GitHub macOS and Ubuntu runners (run 36075071946) show a wider margin: 8.7-28x toml++.

## Use it when

- Parsing large TOML files or many of them (hundreds of KB to MB, or bulk ingestion of manifests and lockfiles), where toml++'s 22-60 MB/s (project's M1 Max run) shows up in profiles. teptris ran 186-335 MB/s in that same run.
- C code, or C++/FFI hosts that want a plain C ABI with opaque handles and status codes instead of C++17 templates and exceptions.
- Read-mostly config access where the input buffer already outlives the parsed document (owned or mmap'd file contents), so zero-copy key views cost nothing.
- Tables with tens of thousands of keys: its hash index keeps lookups O(1). In the same benchmark tomlc99 went quadratic (4.3-4.5 s on 60k keys) and tomlc17 rejected those tables ('table too large').
- Ruby or Python services that need faster TOML loading, through the teptris-ruby and teptris-py bindings (ledger: 11-37x tomli and 1.6-124x tomlib on the project's corpus).

## Skip it when

- Format-preserving edits: the DOM keeps no comments or source formatting, and emit is canonical (hex, octal and binary integers become decimal; multi-line strings are written as single-line escaped strings).
- Strict TOML 1.0 validation: the parser always accepts the 1.1 additions (\e, \xNN, optional seconds, newlines and trailing commas in inline tables), and teptris_options has no switch to turn them off. So files it accepts can fail in 1.0-only parsers.
- Small-config latency: the C benchmark corpus is 0.25-1.5 MB of synthetic files, so the few-KB configs most programs load are not measured. Each document also mallocs its struct plus at least one 64 KiB arena block.
- Memory-constrained or custom-allocator environments: the arena calls malloc directly and there is no allocator hook. The whole tree stays resident until teptris_document_free, and peak-memory measurement is listed as still open (TODO.impl/09).
- Conservative production dependencies: the repo was created 2026-09-13 and has 0 stars. It has had 28 tags (v0.1.0-v0.1.27) in its first ten days and no issues from outside users. The README says 'stable C ABI', but the ABI and soname policy document (TODO.impl/10) is still pending.

## How it is fast

One forward pass writes nodes of at most 64 bytes into a per-document bump arena (64 KiB blocks that double in size, a three-instruction inline allocation, and the whole tree freed at once), and table keys stay as views into the input instead of being copied. Each table is an insertion-order entry vector plus an open-addressing index with linear probing over FNV-1a hashes. The hash is computed during the bare-key scan and cached in the entry, and a missed probe reports its empty slot so the insert that follows skips a second walk. The common shapes have fused fast paths: bare `key = value` lines, bare dotted headers, plain integers of up to 18 digits (Horner's method), floats via Clinger's exact fast path (at most 15 digits, exponent within ±22) with Ryu s2d as fallback, string bodies via memchr plus a NEON/SSE2 escape and control-character check, and a SWAR ASCII skip during UTF-8 validation. The ledger records that wider SIMD kernels and word-at-a-time hashing lost on TOML's 3-10-byte tokens, and optional PGO added another 2-13%.

## Compared with alternatives

No TOML sibling is catalogued yet. The siblings parse YAML (fkYAML, rapidyaml, libfyaml, yeptris) or XML (RapidXml, simdxml and others), so pick teptris whenever the input is TOML. If you already use the same org's yeptris or libleptris, it follows their conventions (C ABI with opaque handles, per-document arena, first-party perf ledger) and carries the same maturity caveats.

## Integration

| | |
|---|---|
| **Form** | static lib (default) or shared lib (TEPTRIS_BUILD_SHARED) via CMake; ships install rules, a CMake package export and teptris.pc |
| **Dependencies** | none at runtime (Ryu is vendored); the tests fetch GoogleTest v1.17.0 unless BUILD_TESTING=OFF |
| **Minimum toolchain** | C99 compiler and CMake 3.20+. project() also enables CXX, so a C++ compiler must be present at configure time (tests use C++11, benchmarks C++17). |
| **Platforms** | x86-64 (SSE2 baseline) and aarch64 (NEON), with a scalar fallback elsewhere; CI builds and tests on Linux x86-64/arm64, macOS arm64/Intel and Windows x64/arm64 (MSVC) |
| **Thread safety** | Not documented in the public header. The CI TSAN lane cites a one-document-per-thread contract. The sources read have no mutable global state and each document owns its arena, but sharing one document across threads is undocumented. teptris_parse_batch parses sequentially on the calling thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Table keys are views into your input buffer and are not NUL-terminated. Freeing or reusing the buffer before teptris_document_free leaves them dangling. String values are NUL-terminated arena copies.
- teptris_parse sets \*out even when it fails, so the error can be read. You must free the document on both paths. Only the first error is reported: line and column plus a message of up to 192 bytes.
- The vendored Ryu code (src/teptris/common/ryu) is dual-licensed Apache-2.0 / Boost-1.0, not MIT, and the license files its headers point to are not in the repo.
- Two float paths call strtod: values with more than 17 significant digits, and values Ryu s2d fails on. strtod follows the process LC_NUMERIC locale, so under a comma-decimal locale those values could misparse (inferred from the code, not tested). The public header still says 'Parse a TOML 1.0 document', and the GitHub description still says C11, while the build is C99 with 1.1 syntax accepted.

## Caveats and trade-offs

First-party ledger; not independently reproduced. The ledger cites benchmarks/results/bench_parse.json as its source, but the committed file is empty (0 bytes since the first commit). The ledger's summary ratios are stale against its own run-3 table (see claimed_speedup), and the README repeats the wrong label '5.2-8.2x the best competitor'. cpptoml, not toml++, is the fastest C++ competitor wherever it parses (it rejects array_heavy). The header-only C++ competitors build at -O2 while teptris gets -O3 plus ThinLTO. No compiler version stated. The project's own CI bench lane shows a larger margin with the same harness on GitHub-hosted runners (run 36075071946, 2026-09-24, comp.json artifacts): teptris is 8.7-28x toml++ and 3.8-8.6x the best competitor on macos-latest and ubuntu-latest (derived). The 100-1000x toml11 gap reflects toml11's per-token source-location tracking (0-3 MB/s). Very new (repo created 2026-09-13), 0 stars, same org as leptris and yeptris.

Pure C99, zero-copy parsing (input buffer must stay alive for the document's lifetime), passes toml-test 714/714 (TOML 1.1 view) and 711/711 (1.0 view); Ruby/Python bindings were initially far slower than the C core due to per-node FFI crossings, since partly closed by native-binding + bulk-drain work but bindings still trail the core's raw speedup.

## Maintenance

Actively developed (last push 2026-09-24) and MIT-licensed with CMake install targets, but pre-1.0 with 0 stars and no outside users visible yet: small enough to vendor, as long as you accept being an early adopter.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The ledger numbers come from the project's public harness (benchmarks/bench_main.cpp, bench_tomlplus.cpp and the other bench_\*.cpp files, scripts/run_benchmarks.sh, scripts/gen_bench_corpus.py). The CPU (Apple M1 Max) and teptris's flags are stated, but no compiler or compiler version is named. The committed artifact the ledger cites, benchmarks/results/bench_parse.json, is empty (0 bytes since the first commit). So it is not A, and first-party numbers are C.
- **Verifier notes:** Downgraded A to C: no compiler or version is stated, and the JSON artifact the ledger cites is empty. The win over toml++ is real, and larger in the project's own CI artifacts. But the ledger's summary ratios and its 'best competitor' label are wrong against its own table, so I rewrote claimed_speedup from the table.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/leptris/teptris>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/LEDGER.md>
  - <https://github.com/leptris/teptris/blob/main/README.md>
  - <https://github.com/leptris/teptris/blob/main/LICENSE.md>
  - <https://github.com/leptris/teptris/blob/main/CMakeLists.txt>
  - <https://github.com/leptris/teptris/blob/main/src/CMakeLists.txt>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/bench_main.cpp>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/bench_common.hpp>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/bench_tomlplus.cpp>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/bench_toml11.cpp>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/bench_cpptoml.cpp>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/bench_tomlc17.cpp>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/bench_tomlc99.cpp>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/results/bench_parse.json>
  - <https://github.com/leptris/teptris/blob/main/scripts/run_benchmarks.sh>
  - <https://github.com/leptris/teptris/blob/main/scripts/gen_bench_corpus.py>
  - <https://github.com/leptris/teptris/blob/main/.github/workflows/bench.yml>
  - <https://github.com/leptris/teptris/blob/main/src/teptris/api.c>
  - <https://github.com/leptris/teptris/actions/runs/36075071946>
- **Sources the enricher read:**
  - <https://github.com/leptris/teptris>
  - <https://github.com/leptris/teptris/blob/main/README.md>
  - <https://github.com/leptris/teptris/blob/main/TODO.md>
  - <https://github.com/leptris/teptris/blob/main/DESCRIPTOR_ABI.md>
  - <https://github.com/leptris/teptris/blob/main/LICENSE.md>
  - <https://github.com/leptris/teptris/blob/main/CMakeLists.txt>
  - <https://github.com/leptris/teptris/blob/main/src/CMakeLists.txt>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/LEDGER.md>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/bench_main.cpp>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/bench_tomlplus.cpp>
  - <https://github.com/leptris/teptris/blob/main/benchmarks/bench_cpptoml.cpp>
  - <https://github.com/leptris/teptris/blob/main/scripts/gen_bench_corpus.py>
  - <https://github.com/leptris/teptris/blob/main/src/include/teptris/teptris.h>
  - <https://github.com/leptris/teptris/blob/main/src/teptris/api.c>
  - <https://github.com/leptris/teptris/blob/main/src/teptris/dom/dom.h>
  - <https://github.com/leptris/teptris/blob/main/src/teptris/memory/arena.h>
  - <https://github.com/leptris/teptris/blob/main/src/teptris/memory/arena.c>
  - <https://github.com/leptris/teptris/blob/main/src/teptris/parse/parser.c>
  - <https://github.com/leptris/teptris/blob/main/src/teptris/parse/scalars.c>
  - <https://github.com/leptris/teptris/blob/main/src/teptris/common/simd.h>
  - <https://github.com/leptris/teptris/blob/main/src/teptris/common/ryu/d2s.c>
  - <https://github.com/leptris/teptris/blob/main/src/teptris/emit/emitter.c>
  - <https://github.com/leptris/teptris/blob/main/TODO.impl/02-foundations.md>
  - <https://github.com/leptris/teptris/blob/main/TODO.impl/03-parser.md>
  - <https://github.com/leptris/teptris/blob/main/TODO.impl/04-dom.md>
  - <https://github.com/leptris/teptris/blob/main/TODO.impl/05-emitter.md>
  - <https://github.com/leptris/teptris/blob/main/TODO.impl/07-conformance.md>
  - <https://github.com/leptris/teptris/blob/main/TODO.impl/09-benchmarks.md>
  - <https://github.com/leptris/teptris/blob/main/TODO.impl/10-packaging.md>
  - <https://github.com/leptris/teptris/blob/main/TODO.max-perf/02-simd-byte-classification.md>
  - <https://github.com/leptris/teptris/blob/main/TODO.max-perf/12-dev-hw-ratio-confirmation.md>
  - <https://github.com/leptris/teptris/blob/main/TODO.max-perf/13-structural-memchr-scanning.md>
  - <https://github.com/leptris/teptris/blob/main/test/CMakeLists.txt>
  - <https://github.com/leptris/teptris/blob/main/.github/workflows/ci.yml>
  - <https://github.com/leptris/teptris/blob/main/.github/workflows/bench.yml>
  - <https://github.com/leptris/teptris/blob/main/.github/workflows/fuzz.yml>
  - <https://github.com/leptris/teptris/issues?q=is%3Aissue+is%3Apr>
  - <https://github.com/leptris/teptris/tags>
  - <https://github.com/leptris/teptris/actions/runs/36075071946>
  - <https://github.com/leptris/teptris-ruby>
  - <https://github.com/leptris/teptris-py>
  - <https://github.com/marzer/tomlplusplus>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/leptris/teptris`) · [data/wave4/enrich/raw/github_com_leptris_teptris.json](../../../data/wave4/enrich/raw/github_com_leptris_teptris.json) (enrichment confidence 0.8)

</details>
