# utf8_range (SIMD Range-based UTF-8 validator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> SIMD range-based UTF-8 validator bundled in protobuf; edges out Lemire's SSE/NEON validator, mostly on ARM.

| | |
|---|---|
| **Beats** | Lemire's SIMD UTF-8 validator (github.com/lemire/fastvalidate-utf-8, the algorithmic ancestor incorporated into simdutf) |
| **Claimed result** | NEON (armv8a): range2 1579.85 MB/s vs Lemire 1198.50 MB/s on UTF-8-demo.txt (\~1.32x, derived from page data). On synthetic buffers range2 beats Lemire by \~1.17x (32 B: 1043.58 vs 891.38) up to \~1.78x (33 B: 1048.12 vs 588.77), and \~1.32x at 1K-1M (derived from page data). SSE4 (Xeon E5-2650): range2 is at parity with Lemire (3986.13 vs 3954.74 MB/s on demo text; 3960.49 vs 3923.51 at 1M) and slower at 32 B (2173.02 vs 2890.52). Vs naive byte-by-byte validation on demo text: \~2.8x on NEON (1579.85 vs 562.25) and \~5.3x on SSE4 (3986.13 vs 753.70) (derived from page data). |
| **Workload** | Byte-by-byte SIMD UTF-8 string validation of UTF-8-demo.txt and synthetic buffers of varying sizes (32B-1M), comparing naive/lookup/Lemire/range/range2 algorithms on NEON (armv8a) and SSE4 (Xeon E5-2650) |
| **Metric** | throughput |
| **Hardware** | SSE4 test: Intel Xeon E5-2650; NEON test: unspecified ARMv8-A chip ("armv8a") |
| **Compiler and flags** | gcc-7.3 (stated in the protobuf-bundled README: 'Built and tested with gcc-7.3'); optimization flags not stated |
| **Adoption** | Bundled into Google Protocol Buffers (72k stars) as third_party/utf8_range; ScyllaDB's utils/utf8.cc uses the range algorithm and credits cyb70289/utf8. Originally developed in cyb70289/utf8 (85 stars, MIT) and the now-archived protocolbuffers/utf8_range (21 stars) |
| **Last commit** | 2026-06-19 |
| **Links** | [repository](https://github.com/protocolbuffers/protobuf) · [benchmark](https://github.com/cyb70289/utf8) |

## Verdict

First-party README benchmark (gcc-7.3, no optimization flags stated) compares 'range2' (a two-block NEON/SSE variant of the range algorithm) against Lemire's 2018 fastvalidate-utf-8 prototype on an unspecified ARMv8-A chip and an Intel Xeon E5-2650 (SSE4.1). On NEON, range2 beats Lemire by about 1.17x-1.78x depending on buffer size (\~1.32x on the UTF-8 demo text and at 1K-1M buffers); on SSE4 it is within noise of Lemire (near parity on demo text and 1M, and slower than Lemire at 32 bytes).

## Use it when

- Already depending on protobuf or Abseil in C/C++ and want its vendored validator instead of adding a new dependency
- Buffers of roughly 1KB+ on ARMv8 NEON, where range2 shows its clearest edge over Lemire-style validation (\~1.3x+)
- ASCII-heavy input, where the wrapper's 8-byte SWAR ASCII skip dominates before SIMD is ever reached
- Only need a boolean valid/invalid result or the longest-valid-prefix length, not decoding
- x86-64 SSE4.1 targets where parity with a 2018-era SIMD validator is acceptable

## Skip it when

- Need AVX2/AVX-512 throughput: the shipped utf8_range.c only dispatches to SSE4.1 or 64-bit ARM NEON; range-avx2.c exists in the tree but is not wired into the wrapper protobuf actually links
- Targeting 32-bit ARM, RISC-V, WASM, or other platforms without SSE4.1/NEON: falls back to a naive per-byte loop with no SIMD speedup
- Small non-ASCII buffers: SSE4 numbers show range2 losing to Lemire at 32 bytes (2173 vs 2891 MB/s)
- Need UTF-8&lt;-&gt;UTF-16/32 transcoding, not just validation: this library only validates
- Want current, independently-run benchmarks: the README table is an unmaintained \~2019 first-party benchmark against Lemire's 2018 prototype, not today's simdutf

## How it is fast

Core technique is the 'range algorithm': load 16 bytes, use a SIMD table lookup (NEON tbl / SSE pshufb) to assign each byte a predicted 'range index' based on where it should fall in a 1-4 byte UTF-8 sequence, then validate all 16 bytes against their [min,max] ranges in one pass, avoiding Lemire's more branch-heavy state tracking and the classic Hoehrmann DFA table walk. The shipped wrapper (utf8_range.c) adds an 8-bytes-at-a-time SWAR ASCII fast-skip (checking the high bit of 8 packed bytes at once) before entering the SIMD range check, and falls back to a naive byte-by-byte loop for tails under 16 bytes or on platforms without SSE4.1/ARM64 NEON.

## Compared with alternatives

Pick it only if you're already pulling in protobuf/Abseil and want its bundled C validator without adding a new dependency; simdutf8 (up to 23x over Rust std), SimdUnicode (up to 14x over .NET), and xutf (1.5-10x over simdutf) show larger and more current speedups, and utf8_range's own edge over Lemire is ARM-specific and within noise on x86 SSE4.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the C library (utf8_range.c/.h); Abseil (absl::strings, for absl::string_view) for the C++ wrapper utf8_validity.h |
| **Minimum toolchain** | C99/C11 for the core C file; C++ (protobuf's current C++17 baseline) for the wrapper; README's own build was tested with gcc-7.3, CMakeLists.txt requires CMake 3.16+ |
| **Platforms** | x86-64 with SSE4.1, or aarch64 with NEON, for the SIMD path; any platform via a naive byte-by-byte fallback otherwise |
| **Thread safety** | not documented, but both entry points are stateless pure functions over caller-owned buffers with no global/static mutable state, so concurrent calls on independent buffers are safe |
| **Drop-in for the baseline** | partial — Lemire's fastvalidate-utf-8 is a research prototype, not a library with a stable API, so there's no baseline API to drop into; utf8_range is a vendorable replacement for hand-rolled or DFA-table UTF-8 checks |

## Gotchas

- The README benchmark tables measure the original standalone research files (range-neon.c, range2-\*.c, lemire-\*.c via main.c), not utf8_range.c, the 2023 Google-rewritten wrapper with the ASCII fast path that protobuf actually ships and links
- No AVX2 dispatch reaches production despite range-avx2.c sitting in the same directory — the wrapper only branches on __SSE4_1__ or __ARM_NEON+64-bit
- Only static-library linkage is provided (CMake/Bazel add_library targets utf8_range and utf8_validity); a shared-library request (issue #14958) was closed without adding one
- The component's own LICENSE file is MIT (Yibo Cai 2019 + Google 2022) even though the surrounding protobuf repo is BSD-3-Clause — relevant if vendoring just this directory

## Caveats and trade-offs

First-party README benchmark with no optimization flags and no ARM CPU model (only 'armv8a'). The tables benchmark the original research files (range-neon.c, range2-\*.c, lemire-\*.c); protobuf's shipped utf8_range.c is a 2023 Google wrapper (ASCII fast path, then range-sse), which these numbers do not cover. The baseline is Lemire's 2018 fastvalidate-utf-8 prototype, not current simdutf. On x86 SSE4 the gain over Lemire is within noise and reversed at 32 B, so the win is ARM-specific. The component is MIT-licensed; protobuf as a whole is BSD-3-Clause. [retier] Tables from 2018 (original repo cyb70289/utf8), older than the 2020 lookup/range optimizations now in protobuf's utf8_range; SSE4 rows reproducible, other rows unchanged.

C API only, no C++ RAII wrappers beyond what protobuf itself provides; win over Lemire's algorithm is ARM-specific, not universal across x86

## Maintenance

Actively maintained as part of protobuf (this component last touched 2026-06-19; the protobuf repo overall as of 2026-09-25); MIT-licensed and small enough to vendor on its own, but only static-library builds are supported.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now A.
- **Tier reason:** The README tables (NEON armv8a and SSE4 E5-2650) are the original author's own numbers, not peer-reviewed or independent. The benchmark code (main.c, './utf8 bench') is public and gcc-7.3 is named, but no optimization flags or ARM CPU model are stated, so this is first-party with partial methodology: C, not B.
- **Retiered** C to A: Raised C to A: the utf8_range tables in the protobuf README come from the original cyb70289/utf8 repo, whose benchmark code, compiler (gcc 7.3), flags (Makefile -O3 -march=native) and CPU (Xeon E5-2650) are public for the SSE4 rows; the tables are from 2018 and predate the 2020 lookup/range optimizations.
- **Verifier notes:** The numbers match the page, but the '\~20-32% consistent edge' was wrong: the NEON edge over Lemire ranges from 17% to 78% by size. Last commit touching third_party/utf8_range is 2026-06-19 (kept); the protobuf repo's overall last commit is 2026-09-25. The component LICENSE file is MIT (Yibo Cai 2019 and Google 2022), not BSD-3-Clause.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`, `benchmark_url`
- **Pages the verifier opened:**
  - <https://github.com/protocolbuffers/protobuf/blob/main/third_party/utf8_range/README.md>
  - <https://github.com/protocolbuffers/protobuf>
  - <https://github.com/protocolbuffers/protobuf/blob/main/third_party/utf8_range/LICENSE>
  - <https://github.com/protocolbuffers/protobuf/blob/main/LICENSE>
  - <https://github.com/protocolbuffers/protobuf/blob/main/third_party/utf8_range/utf8_range.c>
  - <https://github.com/protocolbuffers/utf8_range>
  - <https://github.com/cyb70289/utf8>
  - <https://github.com/scylladb/scylladb/blob/master/utils/utf8.cc>
- **Sources the enricher read:**
  - <https://github.com/protocolbuffers/protobuf/blob/main/third_party/utf8_range/README.md>
  - <https://github.com/protocolbuffers/protobuf/tree/main/third_party/utf8_range>
  - <https://github.com/protocolbuffers/protobuf/blob/main/third_party/utf8_range/utf8_validity.h>
  - <https://github.com/protocolbuffers/protobuf/blob/main/third_party/utf8_range/utf8_range.h>
  - <https://github.com/protocolbuffers/protobuf/blob/main/third_party/utf8_range/LICENSE>
  - <https://github.com/protocolbuffers/protobuf/blob/main/third_party/utf8_range/CMakeLists.txt>
  - <https://github.com/protocolbuffers/protobuf/blob/main/third_party/utf8_range/utf8_range.c>
  - <https://github.com/protocolbuffers/protobuf/issues?q=utf8_range>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/protocolbuffers/protobuf`) · [data/wave3/enrich/raw/github_com_protocolbuffers_protobuf.json](../../../data/wave3/enrich/raw/github_com_protocolbuffers_protobuf.json) (enrichment confidence 0.6)

</details>
