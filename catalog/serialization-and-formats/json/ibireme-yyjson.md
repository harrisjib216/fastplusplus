# yyjson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> ANSI C JSON DOM library beating RapidJSON via single-file design, in-situ parsing, and low-allocation strategy.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | On AWS EC2 (AMD EPYC 7R32, gcc 9.3), twitter.json: yyjson(insitu) 1.80 GB/s parse / 1.51 GB/s stringify vs rapidjson(insitu) 0.77 GB/s parse (\~2.3x, derived from page data), vs rapidjson(utf8) 0.26 GB/s parse / 0.39 GB/s stringify (\~6.9x / \~3.9x, derived from page data), vs simdjson 1.52 GB/s parse / 0.61 GB/s stringify (\~1.18x / \~2.5x, derived from page data), vs cjson 0.32 GB/s parse / 0.17 GB/s stringify (\~5.6x / \~8.9x, derived from page data). On Apple A14 (clang 12): yyjson 2.39 GB/s (3.51 insitu) parse vs simdjson 2.19, rapidjson 0.30 (utf8) / 0.75 (insitu), cjson 0.48. |
| **Workload** | Parse and stringify twitter.json (616.7KB) at GB/s, DOM API, single-threaded, benchmarked via the separate yyjson_benchmark harness across multiple platforms/compilers/datasets |
| **Metric** | throughput |
| **Hardware** | AWS EC2 c5a.large (AMD EPYC 7R32) and Apple A14 (iPhone 12 Pro) for the two tables shown in the README; additional platforms (Intel Core i5-8259U NUC, Graviton2 ARM64) covered in linked interactive charts |
| **Compiler and flags** | gcc 9.3 for the EC2 table; clang 12 for the Apple A14 table. yyjson_benchmark's CMakeLists.txt defaults CMAKE_BUILD_TYPE to Release (CMake's default Release flags for GCC/Clang are -O3 -DNDEBUG) and adds -march=native when the compiler supports it. The linked interactive reports also cover msvc 2019 and clang 10. |
| **Adoption** | 3.9k stars; "The fastest JSON library in C" per repo description |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/ibireme/yyjson) · [benchmark](https://github.com/ibireme/yyjson#performance) |

## Verdict

On AWS EC2 (AMD EPYC 7R32, gcc 9.3, CMake Release build i.e. -O3 -DNDEBUG plus -march=native) yyjson(insitu) parses twitter.json at 1.80 GB/s and stringifies at 1.51 GB/s versus RapidJSON(insitu) 0.77 GB/s parse and RapidJSON(utf8) 0.26/0.39 GB/s parse/stringify, roughly 2.3x-6.9x. On Apple A14 (clang 12) yyjson reaches 2.39-3.51 GB/s parse versus RapidJSON's 0.30-0.75 GB/s.

## Use it when

- Parsing/serializing JSON in a C or C++ codebase where RapidJSON is the current baseline and a plain-C DOM API is acceptable
- Need strict int64/uint64/double round-trip fidelity and RFC 8259 conformance
- Want to vendor one header + one source file with no build system, on ANSI C89 for portability (CI covers x86/arm/ppc/riscv/s390x/wasm with gcc/clang/msvc/tcc/watcom)
- Can parse into a mutable buffer and use YYJSON_READ_INSITU to cut allocation/copy overhead
- Need JSON Pointer/Patch/Merge Patch or opt-in JSON5 leniency (comments, trailing commas) built in

## Skip it when

- Access pattern is index/key lookup-heavy rather than sequential iteration — arrays/objects use a linked-list-like structure (README Limitations)
- Need to mutate a document immediately after parsing — read results are immutable; requires yyjson_doc_mut_copy first
- simdjson's On-Demand API applies (most fields known at compile time) — README states it beats yyjson there; this benchmark only covers DOM-vs-DOM
- Cross-version ABI stability is required — 'Ensure ABI stability' is still an unchecked TODO in the README
- Building/mutating one yyjson_mut_doc from multiple threads — mutable types are documented not thread-safe

## How it is fast

No explicit SIMD anywhere (ANSI C89 throughout); the README attributes speed instead to a modern-CPU-friendly code shape (high ILP, good branch prediction, tolerant of misaligned access) plus three concrete design choices visible in the docs: a single up-front memory allocation per document sized via yyjson_read_max_memory_usage rather than per-node mallocs, an optional in-situ reader (YYJSON_READ_INSITU) that parses strings in place inside the caller's buffer to skip copies, and a built-in fast float parse/print path that bypasses libc strtod/dtoa (toggle: YYJSON_DISABLE_FAST_FP_CONV). doc/Performance.md is a TODO stub, so no deeper algorithmic writeup exists in-repo.

## Compared with alternatives

Pick yyjson over simdjson when you want one portable ANSI C89 file with no SIMD/CPU-feature dependency and a DOM object you keep around (simdjson's DOM stringify trails at 0.61 vs yyjson's 1.51 GB/s on the EC2 table); pick simdjson instead when its On-Demand API fits or peak SIMD throughput outweighs portability. Pick yyjson over glaze when the codebase is C rather than C++, or you need a runtime dynamic DOM instead of glaze's reflection-based static-type serialization.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (ANSI C89, no explicit SIMD); optionally built as a static/shared lib via CMake |
| **Minimum toolchain** | C89 (CI also builds under gcc, clang, msvc, tcc, watcom) |
| **Platforms** | x86, arm, ppc, riscv, s390x, wasm per CI matrix; no SIMD/CPU-feature requirement |
| **Thread safety** | No global variables. yyjson_doc/yyjson_val (immutable, post-parse) are thread-safe for concurrent reads; yyjson_mut_doc/yyjson_mut_val (mutable, build-side) are not thread-safe. |
| **Drop-in for the baseline** | false — different API paradigm (plain C accessor functions vs RapidJSON's C++ template DOM); same JSON-DOM concept, not source-compatible |

## Gotchas

- YYJSON_READ_INSITU requires a mutable, non-const buffer with extra padding bytes; passing a const string with this flag is a caller error
- Parsed (immutable) docs can be edited via yyjson_set_\* functions, but the README calls this 'breaking the immutable convention' and says to only do it from a single thread
- Duplicate object keys are preserved, not deduped or rejected (README Limitations; issue #254 asking for a forbid-duplicates flag is still open)
- Calling setlocale() concurrently with parsing can corrupt float parsing if the platform isn't IEEE-754 or YYJSON_DISABLE_FAST_FP_CONV is set (falls back to strtod)

## Caveats and trade-offs

The interactive benchmark charts linked from the README are dated 'last updated 2020-12-12'; build uses CMake 'Release' config rather than an explicitly printed compiler flag string. README itself notes simdjson's newer On-Demand API can beat yyjson when most fields are known at compile time -- this benchmark only exercises the DOM APIs of both.

Arrays/objects use a linked-list-like internal structure, so indexed access is slower than sequential iterator access; parsed documents are immutable (a mutable copy is required to modify); ANSI C89 with no explicit SIMD intrinsics, trading some raw peak throughput for portability vs simdjson.

## Maintenance

Active: release 0.13.0 shipped 2026-09-08, same day as the latest commit; MIT-licensed, 3,883 stars, and trivial to vendor as one .h/.c pair.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Performance tables compare yyjson with rapidjson (insitu and utf8), simdjson and cjson on twitter.json. They state the compiler (gcc 9.3, clang 12) and the CPU model (AMD EPYC 7R32, Apple A14). The public benchmark code in github.com/ibireme/yyjson_benchmark (src/, CMakeLists.txt) fixes the flags: the Release build type by default, plus -march=native.
- **Verifier notes:** Every figure in the record matches the README; the only fix was adding the required 'derived from page data' markers to the ratios. Flags are pinned in the public harness CMakeLists (Release + -march=native), so tier A stands. The harness repo was last pushed 2023-06. Metadata checks out: 3,883 stars, MIT, last commit 2026-09-08.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`
- **Shortcomings recorded by:** On the same 20k-record parse-and-extract workload yyjson took 191.56 ns/record vs simdjson's 113.546 (simdjson 1.69x), with 733 KB of source vs 10.5 MB and no SIMD dispatch to mis-build (selection: 643 MB/s, 2.6x RapidJSON). Its documented pool-allocator idiom showed no benefit in a repeated-parse loop (193.125 vs 191.56 ns), although a one-shot 13.86 MB parse during selection did show \~45%. (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://github.com/ibireme/yyjson>
  - <https://github.com/ibireme/yyjson#performance>
  - <https://github.com/ibireme/yyjson_benchmark>
  - <https://github.com/ibireme/yyjson_benchmark/blob/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/ibireme/yyjson>
  - <https://github.com/ibireme/yyjson#performance>
  - https://github.com/ibireme/yyjson (README via gh api repos/ibireme/yyjson/readme)
  - https://github.com/ibireme/yyjson/tree/master (repo tree via gh api git/trees)
  - <https://github.com/ibireme/yyjson/blob/master/doc/API.md>
  - <https://github.com/ibireme/yyjson/blob/master/doc/BuildAndTest.md>
  - <https://github.com/ibireme/yyjson/blob/master/doc/Performance.md>
  - https://github.com/ibireme/yyjson (repo metadata via gh api repos/ibireme/yyjson)
  - https://github.com/ibireme/yyjson/releases (via gh api repos/ibireme/yyjson/releases)
  - https://github.com/ibireme/yyjson/issues (search via gh search issues)
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/ibireme/yyjson`) · [data/wave0-seed/enrich/raw/github_com_ibireme_yyjson.json](../../../data/wave0-seed/enrich/raw/github_com_ibireme_yyjson.json) (enrichment confidence 0.85)

</details>
