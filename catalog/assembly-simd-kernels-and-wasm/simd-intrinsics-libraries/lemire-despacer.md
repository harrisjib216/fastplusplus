# despacer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟡 stale

> C research library of SSE4/AVX2 in-place whitespace strippers; 3-5x faster than the best scalar loop, 10-15x the naive one.

| | |
|---|---|
| **Beats** | scalar despace loop (branching) in the same repo; also faster_despace and despace64 scalar variants |
| **Claimed result** | README sample ('Possible results', unnamed CPU), in cycles per byte: despace (scalar) 5.337891, faster_despace 1.689453 and despace64 2.429688, against sse4_despace_branchless_u4 0.351562 (15.2x vs despace and 4.8x vs faster_despace, derived from page data) and avx2_despace_branchless_u2 0.535156 (10.0x vs despace and 3.2x vs faster_despace, derived from page data); memcpy reference 0.111328. |
| **Workload** | Removing ' ', '\n' and '\r' in place from an 8 KiB buffer (N=8192) of random bytes above 32 with about 3% whitespace (1% of each character). Best of 100 repetitions, with the output length checked. The README sample reports cycles per byte; the current harness prints GB/s. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the README sample; the README notes clang gives better results than gcc. The current CMakeLists.txt builds the library and benchmarks/despacebenchmark.c with -march=native (GCC or clang, x86-64 only). The README build line sets -DCMAKE_BUILD_TYPE=Release, but the Makefile's build and 'make benchmark' targets configure without a build type, so a single-config generator build gets no -O level. |
| **Adoption** | 159 stars |
| **Last commit** | 2024-09-05 |
| **Links** | [repository](https://github.com/lemire/despacer) · [benchmark](https://github.com/lemire/despacer) |

## Verdict

The README's 'Possible results' sample (unnamed CPU and compiler, most likely built with the pre-2021 Makefile's -O3 -march=native) covers an 8 KiB buffer of printable ASCII with 1% each of space, LF and CR, best of 100 calls: sse4_despace_branchless_u4 used 0.35 cycles per byte against 5.34 for the naive branchy loop (15.2x) and 1.69 for the table-driven scalar faster_despace (4.8x); avx2_despace_branchless_u2 used 0.54 (10.0x and 3.2x), with memcpy at 0.11. The current harness prints GB/s, warns its numbers are illustrative, and no other density, size or CPU has been published.

## Use it when

- Stripping spaces and line breaks from large ASCII or UTF-8 text in place (minifying, normalising base64 or hex dumps, cleaning logs) on x86-64 with SSE4.1 or AVX2, where a branchy scalar loop costs about 5 cycles per byte.
- Sparse whitespace (a few percent of bytes), the regime the benchmark measures: most 16-byte blocks then have no whitespace or one, and the shuffle table stays hot in cache.
- As a reference collection of stream-compaction (left-pack) techniques to copy into your own code: table-driven pshufb, 1 KB LUT, prefix-sum, vpermd and VBMI2 compress-store side by side with a harness to compare them on your CPU.
- Builds compiled for one known machine or a fixed ISA level, since each SIMD function exists only when the matching -m flag is on.

## Skip it when

- Portable binaries or non-x86 targets: no runtime dispatch, the CMake build forces -march=native (issue #21 open), and there is no NEON port (issue #4 open since 2017); on ARM only the scalar loops are available.
- Dense whitespace (source code, pretty-printed JSON, tables): untested here, and the SSE4/AVX2 table variants then spread lookups across a 512 KiB shuffle table (plus a 64 KiB popcount table) that overflows L1 and often L2.
- When the whitespace set must be exact and consistent: '\t' is kept by despace and the SSE4/AVX2 variants but removed by aqrit's variants, the \*32, skinny and VBMI2 variants drop every byte up to 0x20, and nothing handles Unicode whitespace (issue #8 open).
- UTF-8 or Latin-1 text with the AVX-512 VBMI2 or skinny variants: signed-char comparisons make them delete non-ASCII bytes (see gotchas).
- Production use without your own tests: the maintainer calls it research code and asks serious users to contact him (issue #21); the last commit was 2024-09-05.

## How it is fast

Each 16-byte block is compared against the three whitespace bytes, the comparison is turned into a 16-bit movemask, and that mask indexes a precomputed pshufb shuffle table (despace_mask16, 32,768 entries of 16 bytes) that packs the kept bytes to the left; the store pointer then advances by 16 minus the popcount, so the hot loop has no data-dependent branch. The AVX2 variants run two 16-byte lanes per 256-bit vector and the _u2/_u4 versions unroll; aqrit's variants replace the big table with a 1 KB table or a prefix-sum, and the AVX-512 version uses vpcompressb (_mm512_mask_compressstoreu_epi8) with no table at all.

## Compared with alternatives

Pick despacer over komrad36's Leftpack when the job is byte-level whitespace removal and you want ready-made SSE4/AVX2 kernels plus a harness; Leftpack is the general left-pack-by-predicate primitive for 8- to 64-bit elements. Like validateutf8-experiments from the same author it is research code that is best copied and re-tested, not depended on.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target despacer) or source-drop (src/despacer.c, the 3 MB src/despacer_tables.h and include/\*.h) |
| **Dependencies** | none |
| **Minimum toolchain** | C99 and CMake 3.15+; GCC, Clang or MSVC (CI on Ubuntu 22.04 GCC 11 and Visual Studio 2022); the benchmark needs GCC or Clang on x86-64 |
| **Platforms** | x86-64 for the SIMD paths (SSSE3, SSE4.1, SSE4.2, AVX2, AVX-512 VBMI2, chosen at compile time); scalar functions build anywhere; no NEON |
| **Thread safety** | Functions are reentrant over caller-owned buffers; gen_table_512kb() fills the global 512 KB lut_1mb table and must be called once, before any thread uses despace_ssse3_lut_512kb |
| **Drop-in for the baseline** | partial: replaces a hand-written erase-remove loop (same in-place semantics, returns the new length, no NUL), but the signatures differ between families ((bytes, n), (dst, src, n), (src, n, out)) and so does the whitespace set |

## Gotchas

- Signed-char bugs outside the headline functions: vbmi2_despace compares with the signed _mm512_cmpgt_epi8_mask(x, ' '), so it deletes every byte from 0x80 up, i.e. all UTF-8 multibyte characters, despite the README's UTF-8/Latin-1 claim; sse4_despace_skinny_u2/u4 keep such bytes in the vector loop but delete them in the scalar tail ((int)c &lt;= 0x20 on signed char), corrupting UTF-8 in the final n mod 16 bytes; countspaces32 counts bytes from 0x80 up as whitespace. The unused vbmi2_256_despace passes a 32-bit byte mask to the 16-bit-lane _mm256_mask_compressstoreu_epi16 and would output garbage.
- Harness and test blind spots hide these: the benchmark's fillwithtext rejects (char)rand() &lt;= 32 with signed char, so the input is printable 7-bit ASCII (33-127) plus 3% whitespace, never a byte from 0x80 up; the benchmark checks only the returned length, not the bytes; in tests/unit.c the random-text branch is dead (if (i &lt; 128) with repeat = 128), so the unit tests only try 128-byte runs of 'c' with a single space, and vbmi2_despace is never tested. The headline SSE4/AVX2 functions use exact byte equality and are not affected.
- Reproducing the README with the documented 'make benchmark' builds unoptimized: since July 2021 the Makefile runs cmake with no CMAKE_BUILD_TYPE and --config Release, which single-config generators ignore, so library and benchmark get only -march=native; the README sample predates that change (it lacks aqrit's variants, already in the code by 2018 per issue #8), when the Makefile used -std=c99 -O3 -march=native. Use cmake -DCMAKE_BUILD_TYPE=Release.
- Each timed call is bracketed by cpuid+rdtsc and the README figures are TSC reference cycles, not core cycles; on VMs, where cpuid traps to the hypervisor, the fixed overhead per 8 KiB call can swamp the faster kernels. Each despace_ssse3_lut_512kb call also silently returns wrong bytes if gen_table_512kb() was never called.

## Known shortcomings

- Sample on an unnamed CPU from an older harness; the 15x is against a naive loop and about 4.8x against faster_despace (derived); 'make benchmark' builds with no build type.
- The headline sse4/avx2 functions are correct. Signed-char bugs elsewhere: vbmi2_despace deletes every byte from 0x80 up (all UTF-8 multibyte characters); sse4_despace_skinny_u2/u4 drop such bytes in the scalar tail; countspaces32 miscounts them; vbmi2_256_despace uses the wrong compress width. The harness hides them: input is 7-bit ASCII 33-127 only, the check is length-only, and the random branch of tests/unit.c is dead (i &lt; 128 with repeat 128). 'make benchmark' has built without -O since July 2021; the 512 KiB shuffle table and only 3% whitespace density are tested.

## Caveats and trade-offs

The README output is labelled 'Possible results': a sample on an unnamed CPU, in the cycles/op format of an older harness. The current benchmarks/despacebenchmark.c prints GB/s and warns that its estimates are 'for illustrative purposes and may not be accurate'. The 15x headline is against the naive branchy despace loop; against the repo's best scalar version (faster_despace, a table-driven branchless loop) the SIMD gain is about 3-5x (derived from page data). A single 8 KiB in-cache buffer with 3% whitespace is used, so other densities were not tested. The Makefile path builds without optimization flags. The linked 2017 blog post was not opened (blogs blocked).

x86-64 only for the SIMD variants (SSE4/AVX2); the README lists no NEON or AVX-512 results. C library with D bindings.

## Maintenance

Stale (last commit 2024-09-05, CI and D-binding fixes) and self-described research code, but BSD-3-Clause with no dependencies, so the one or two functions you need are easy to vendor once you add your own tests for non-ASCII input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party 'Possible results' sample in the README, with no CPU model, compiler version or flags. The harness is public (benchmarks/despacebenchmark.c, built with -march=native by CMakeLists.txt) and compares against the repo's own scalar loops, so the evidence is C.
- **Verifier notes:** All README numbers match the record. Metadata checked: BSD-3-Clause, 159 stars, not a fork, last commit 2024-09-05 (stale). Shortcomings: unnamed CPU, no flags or compiler version, sample output from an older harness, headline ratio against the naive loop rather than the best scalar loop (about 4.8x), and 'make benchmark' configures without a build type.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-25 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/lemire/despacer>
  - <https://github.com/lemire/despacer/commits>
  - <https://github.com/lemire/despacer/commits/master/README.md>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/benchmarks/despacebenchmark.c>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/src/despacer.c>
- **Sources the enricher read:**
  - <https://github.com/lemire/despacer>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/benchmarks/despacebenchmark.c>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/src/despacer.c>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/src/despacer_tables.h>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/include/despacer.h>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/include/despacer_generic.h>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/include/despacer_SSSE3.h>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/include/despacer_AVX2.h>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/include/despacer_AVX512.h>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/tests/unit.c>
  - https://raw.githubusercontent.com/lemire/despacer/HEAD/dub.json (404)
  - <https://github.com/lemire/despacer/commits/master>
  - <https://github.com/lemire/despacer/commits/master/Makefile>
  - <https://raw.githubusercontent.com/lemire/despacer/a06275967fd16fa6132902b3803dd3118f8a15f0/Makefile>
  - <https://github.com/lemire/despacer/issues?q=is%3Aissue>
  - <https://github.com/lemire/despacer/issues/8>
  - <https://github.com/lemire/despacer/issues/21>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/lemire/despacer`) · [data/wave13/enrich/raw/github_com_lemire_despacer.json](../../../data/wave13/enrich/raw/github_com_lemire_despacer.json) (enrichment confidence 0.8)

</details>
