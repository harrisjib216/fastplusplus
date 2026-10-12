# glaze

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only, C++23 reflection-based JSON (plus BEVE/CBOR/MessagePack/TOML/YAML/CSV) library; beats RapidJSON in first-party benchmarks.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | Glaze 1.01 s roundtrip / 1396 MB/s write / 1200 MB/s read vs RapidJSON 3.76 s / 289 MB/s / 416 MB/s (\~3.7x roundtrip, \~4.8x write, \~2.9x read, derived from page data); vs nlohmann 15.44 s / 86 MB/s / 81 MB/s (\~15x roundtrip, derived from page data); read 1200 MB/s vs simdjson On-Demand 1163 MB/s (\~1.03x, derived from page data); ABC out-of-order-keys test: Glaze reads at 1219 MB/s vs simdjson On-Demand at 89 MB/s (\~13.7x, derived from page data). |
| **Workload** | Round-trip read/write of a nested JSON test struct (mixed arrays, objects, strings, numbers), 1,000,000 iterations, single core, MacBook Pro M1 |
| **Metric** | throughput |
| **Hardware** | MacBook Pro M1 (single core) |
| **Compiler and flags** | Clang 17 (optimization flags not stated) |
| **Adoption** | 3k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/stephenberry/glaze) · [benchmark](https://github.com/stephenberry/json_performance) |

## Verdict

On a single-core MacBook Pro M1 with Clang 17 (optimization flags not specified in the benchmark harness), Glaze round-trips a nested JSON test struct 1,000,000 times in 1.01s (1396 MB/s write / 1200 MB/s read) versus RapidJSON's 3.76s (289 MB/s write / 416 MB/s read) — roughly 3.7x roundtrip, 4.8x write, 2.9x read — per the author-run json_performance benchmark (results dated June 8, 2025), which also appears verbatim in the Glaze README's Performance table.

## Use it when

- Reading/writing C++ structs known at compile time to/from JSON without hand-written (de)serialization code or macros.
- Need one struct definition to serialize to multiple formats (JSON, BEVE, CBOR, MessagePack, TOML, YAML, CSV).
- Input JSON keys can be missing or out of declared order — Glaze doesn't fall back to re-scanning the way simdjson On-Demand does (1219 MB/s vs simdjson's 89 MB/s in the author's out-of-order-keys test).
- Embedded/constrained builds that want no exceptions and no RTTI (-fno-exceptions/-fno-rtti).
- Team can adopt a C++23 toolchain (Clang 17+, GCC 13+, MSVC 2022+ with /Zc:preprocessor).

## Skip it when

- Stuck on C++17/C++20 — Glaze requires C++23, a higher bar than RapidJSON or nlohmann (C++11+).
- Need a DOM/Value-tree API for dynamic, schema-less JSON manipulation rather than struct binding.
- Non-aggregate classes (custom constructors, virtual functions, private members) without opting into C++26 P2996 reflection, which needs GCC 16+ or a Bloomberg clang fork — not mainstream compilers.
- Care about independently verified numbers: the entire published performance table is first-party (author-designed workload, author-run), evidence tier C, with no stated optimization flags in the benchmark harness's CMakeLists.txt.
- Endianness matters for your target: installation.md states little-endian only, while the README's Compiler/System Support section claims big-endian is supported and CI-tested via QEMU on s390x — the two docs disagree, so verify directly for your platform.

## How it is fast

Uses C++23 compile-time reflection (or C++26 P2996 on GCC 16+/Bloomberg clang-p2996) to generate per-struct parse/serialize code at compile time instead of runtime introspection or macro-generated boilerplate, writing directly into destination objects rather than an intermediate DOM. Adds compile-time perfect-hash maps for key lookup and runtime SIMD dispatch (SSE2 through AVX-512BW on x86-64, NEON on ARM, SIMD128 on Wasm, auto-selected from compiler target macros) for UTF-8 validation, string escaping, and structural whitespace skipping.

## Compared with alternatives

Pick Glaze over simdjson when JSON keys can arrive missing or out of declared order — simdjson's On-Demand API degrades sharply there (89 MB/s vs Glaze's 1219 MB/s in the author's ABC test) — or when you want one API spanning JSON, BEVE, CBOR, MessagePack, TOML, YAML, and CSV from the same struct. Pick yyjson instead if the codebase is C (not C++23) or you need a DOM-style API rather than compile-time struct binding.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for core JSON/binary formats (self-contained, SIMD paths built in); optional networking module (HTTP/WebSocket) pulls in Asio |
| **Minimum toolchain** | C++23; Clang 17+ (18+ in CI), GCC 13+, MSVC 2022+ (requires /Zc:preprocessor) |
| **Platforms** | x86-64 (SSE2 through AVX-512BW auto-detected), aarch64 (NEON), WebAssembly (SIMD128); 64-bit and 32-bit; endianness support is disputed between docs (see gotchas) |
| **Thread safety** | not documented for the core glz::read_json/glz::write_json API; separate opt-in glz::thread_pool and glz::async utilities exist under include/glaze/thread/ but are distinct features, not a concurrency guarantee for read/write calls |
| **Drop-in for the baseline** | partial — same job (JSON read/write) as RapidJSON but a different API shape: compile-time struct reflection, not a DOM/SAX interface, so call sites must be rewritten |

## Gotchas

- docs/installation.md says little-endian systems only; the README's Compiler/System Support section says big-endian is supported and tested via QEMU on s390x — conflicting docs, confirm for your target before relying on either.
- No exceptions/RTTI by default (-fno-exceptions/-fno-rtti); errors come back as glz::error_code, not exceptions, unless you opt into the separate throwing helper API.
- C++26 P2996 reflection (non-aggregate types, unlimited struct members, private member access, automatic enum serialization) needs GCC 16+ or Bloomberg's clang-p2996 fork — not available on the mainstream GCC 13+/Clang 17+ builds most users have.
- MSVC builds need the /Zc:preprocessor flag; without it the standard-conformant preprocessing Glaze's reflection relies on breaks.

## Caveats and trade-offs

First-party benchmark: the Glaze author runs and publishes it in the companion repo json_performance, using a test object and workload he designed. Results are dated June 8, 2025, which is also the harness repo's last commit. The page states the compiler (Clang 17) and machine (MacBook Pro M1, single core), but the harness's CMakeLists.txt sets only -Wall -Wextra, with no optimization flags and no default build type, so flags are unknown. The simdjson comparison uses a known weak case for simdjson's On-Demand API (out-of-order keys), which the same non-neutral author highlights.

Relies on C++20 aggregate reflection (or C++23/26 P2996 reflection on supporting compilers) rather than macros; header-only with format-specific headers to bound compile time; no exceptions/RTTI required (compiles with -fno-exceptions/-fno-rtti), which changes error-handling ergonomics vs exception-based parsers.

## Maintenance

Actively maintained (last commit 2026-09-24, \~3k stars, no open bug-labeled issues found in a repo search); MIT-licensed and header-only so trivially vendorable, but the C++23 requirement (Clang 17+/GCC 13+/MSVC 2022+) is a real adoption bar versus older-standard baselines like RapidJSON.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** The json_performance README ('Latest results (June 8, 2025)') lists Glaze against RapidJSON, nlohmann, simdjson On-Demand, yyjson and others, with the code public in src/main.cpp. It gives Clang 17 on a MacBook Pro M1, but neither the README nor CMakeLists.txt sets optimization flags or a default build type, so flags are missing and the tier stops at C.
- **Verifier notes:** All numbers match the json_performance README and the Glaze README Performance table. Ratios are now marked as derived. Tier C confirmed. Metadata checks out: 3,029 stars, MIT, last commit 2026-09-24, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** In developer source's JSON selection (13.86 MB corpus, 20k nested records, full parse plus 9-field extraction, identical checksums) Glaze ran at 787 MB/s vs simdjson 1445, yyjson 643 and RapidJSON 248 (3.2x RapidJSON). It was not adopted because it failed to compile under -std=c++20 on gcc 13.3 and clang 18.1 (it needs C++23) and has no runtime SIMD dispatch. (developer source, private repo; selection measurement in third_party/simdjson/VENDORING.md, median of repeated runs; evaluation for run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://github.com/stephenberry/glaze>
  - <https://github.com/stephenberry/json_performance>
  - <https://github.com/stephenberry/json_performance/blob/main/CMakeLists.txt>
  - <https://github.com/stephenberry/json_performance/tree/main/src>
- **Sources the enricher read:**
  - <https://github.com/stephenberry/glaze>
  - <https://github.com/stephenberry/glaze/blob/main/docs/installation.md>
  - <https://github.com/stephenberry/glaze/blob/main/docs/FAQ.md>
  - <https://github.com/stephenberry/glaze/blob/main/docs/security.md>
  - <https://github.com/stephenberry/glaze/issues>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/stephenberry/glaze`) · [data/wave0-seed/enrich/raw/github_com_stephenberry_glaze.json](../../../data/wave0-seed/enrich/raw/github_com_stephenberry_glaze.json) (enrichment confidence 0.7)

</details>
