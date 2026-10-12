# faster-utf8-validator

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🔴 abandoned

> Single-file AVX2/SSE4 UTF-8 validator in C; about 1.5-1.7x faster than fastvalidate-utf-8 AVX2 on random UTF-8.

| | |
|---|---|
| **Beats** | fastvalidate-utf-8 AVX2 validators (validate_utf8_fast_avx and validate_utf8_fast_avx_asciipath) |
| **Claimed result** | README table, cycles per byte, best of 50: on 64K random UTF-8, z_validate_utf8_avx2 0.264 vs validate_utf8_fast_avx 0.410 and validate_utf8_fast_avx_asciipath 0.436 (1.55x and 1.65x, derived from page data); on 16M UTF-8, 0.290 vs 0.496 and 0.457 (1.71x and 1.58x, derived from page data). The README text says roughly 1.5-1.7x faster than fastvalidate-utf-8. On random ASCII there is no gain over the asciipath variant: 0.079 vs 0.074 (64K) and 0.160 vs 0.156 (16M). The SSE4 version (0.568 on 64K UTF-8) is slower than the AVX2 baseline. |
| **Workload** | UTF-8 validation of random UTF-8 and random ASCII buffers of 64K and 16M bytes, best of 50 runs, cycles per byte. |
| **Metric** | throughput |
| **Hardware** | 2.4 GHz Haswell laptop |
| **Compiler and flags** | Not stated for the benchmark run, whose harness (a modified fastvalidate-utf-8 benchmark) is not published. The repo's rules.py builds the library with cc -O3 -march=native -std=gnu11 -DAVX2 or -DSSE4 (plus -fcolor-diagnostics, a clang flag); compiler version unstated. |
| **Adoption** | 222 stars |
| **Last commit** | 2019-11-18 |
| **Links** | [repository](https://github.com/zwegner/faster-utf8-validator) · [benchmark](https://github.com/zwegner/faster-utf8-validator) |

## Verdict

First-party README, best of 50 runs on a 2.4 GHz Haswell laptop with a private modification of the fastvalidate-utf-8 harness (compiler unstated): AVX2 validates random UTF-8 at 0.264 cycles/byte (64K) and 0.290 (16M), against 0.410/0.436 and 0.496/0.457 for fastvalidate-utf-8's two AVX2 functions (about 1.55-1.71x, derived), with no gain on pure ASCII. Lemire's validateutf8-experiments README (an adapted port named zwegneravx, CMake Release with -march=native, unnamed 3.5 GHz CPU) independently shows 19.7 GB/s on hongkong.html and 41.0 GB/s on twitter.json. That is 1.28x and 1.82x the fastvalidate-style 'basic' row (15.5 and 22.5 GB/s), and 0.94x and 1.11x the lookup4 algorithm (20.9 and 37.0 GB/s) (ratios derived from page data).

## Use it when

- Studying or teaching SIMD UTF-8 validation: the long comment in z_validate.c is one of the clearest write-ups of the nibble-lookup error tables
- Vendoring a tiny, dependency-free validator into a C codebase that already targets AVX2 at build time, after fixing the tail over-read described under gotchas
- Mostly non-ASCII text (CJK, mixed scripts) on Haswell-or-newer x86, where it measured 0.26-0.29 cycles/byte versus 0.41-0.50 for fastvalidate-utf-8
- Buffers from KiB to MiB sizes where only a valid/invalid answer is needed, not the error position

## Skip it when

- Production code: use simdutf, which implements the successor lookup algorithm with runtime CPU dispatch, AVX-512 and NEON kernels, error positions and transcoding, and is maintained
- Pure-ASCII workloads: no gain over fastvalidate-utf-8's asciipath variant (0.079 vs 0.074 cycles/byte at 64K, 0.160 vs 0.156 at 16M)
- ARM, POWER or other non-x86 targets: master has only AVX2 and SSE4 paths; the AVX-512 and NEON work exists only on an unmerged wip branch whose AVX-512 build fails its own tests (issue #6)
- Binaries that must run on unknown x86 CPUs: there is no runtime dispatch, so an AVX2 build raises SIGILL on pre-Haswell parts
- Buffers that end near an unmapped page, or code run under ASan or Valgrind, until the tail over-read is fixed

## How it is fast

Continuation structure is checked in the scalar domain on movemask bitmasks: masks of bytes starting 11, 111 and 1111 are shifted forward 1, 2 and 3 positions and summed with one lea-style add into a 'required continuation' mask, which must equal the mask of actual 10xxxxxx bytes. A carry mask handles sequences that cross vector boundaries. The special-case errors (C0/C1 and E0/F0 overlongs, ED surrogates, F4 above U+10FFFF, F5-FF) are found with three vpshufb nibble lookups (the high and low nibble of the previous byte and the high nibble of the current byte), ANDed into one error-bit vector that must be zero. This three-nibble-lookup idea was adopted by the Keiser-Lemire 'lookup' algorithm now in simdutf. All-ASCII vectors exit after a single movemask test.

## Compared with alternatives

Against lemire/validateutf8-experiments (the lookup algorithm, labelled research-only): this is the smaller, self-contained C file, and the same lookup idea in production form is simdutf, which should be preferred for shipped code. Pick zwegner's file only when you want a dependency-free single source file to read or vendor on AVX2-only x86.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (immintrin.h, stdint.h) |
| **Minimum toolchain** | C99/C11 compiler with x86 intrinsics; the repo's rules.py uses cc -std=gnu11 -O3 -march=native (the -fcolor-diagnostics flag suggests clang); compiler version not documented |
| **Platforms** | x86-64 with AVX2 (-DAVX2) or SSSE3 plus SSE4.1 (-DSSE4, needed for _mm_test_all_zeros); no ARM on master |
| **Thread safety** | Reentrant: a pure function with no global or static mutable state (checked in the source); not documented in the README |
| **Drop-in for the baseline** | partial — same (const char\*, size_t) shape as fastvalidate-utf-8's validate_utf8_fast_avx, but a different name, an int return, and a compile-time ISA macro instead of a header |

## Gotchas

- Out-of-bounds read: the main loop loads the next shifted vector, v_load(data + offset + V_LEN - 1), before re-testing the loop condition. On the last loop iteration it therefore reads up to 30 bytes (AVX2) or 14 bytes (SSE4) past the end of the input, for every length above one vector except lengths of 0 or V_LEN-1 modulo V_LEN (60 of the 65 lengths from 32 to 96 with AVX2, counted with a Python model of the loop). The value is discarded, so results are unaffected. The read can still fault when the buffer ends near an unmapped page, and ASan will report it. test.lua cannot see it because it embeds every input in a padded 128-byte buffer. Fix: load data + offset - 1 at the top of the next iteration. Codegen was not inspected because nothing was built here.
- The validation logic itself checks out: a Python model of HEAD's masks and tables agreed with Python's strict UTF-8 decoder on 4.25 million crafted inputs (all two-byte pairs with continuation and ASCII tails at boundary offsets, plus token fuzzing, for vector widths 32 and 16). The F0-overlong fix (2b0ad07) changed only table constants, and the ASCII early-exit change (cf48201) only affects invalid input, so the README timings still reflect HEAD on valid data.
- Build traps: z_validate_vec is declared plain 'inline' (not static). Under C99/C11 inline rules, an unoptimised build has no out-of-line definition; rules.py's avx2/deb and sse4/deb configs use -g with no -O. The 'cont' variable draws a maybe-uninitialised warning that -Werror turns into a build error; the maintainer agreed to fix it in issue #5, but the fix never landed. test.lua declares the functions as returning bool while the C returns int.
- Compiler sensitivity: a user reported (issue #5) that a hand-unrolled variant ran about 2x faster under MSVC 2017, so the published cycles/byte assume a GCC/Clang-style compiler (unstated).

## Known shortcomings

- Private harness; numbers predate the F0-overlong correctness fix 2b0ad07; no ASCII gain over the asciipath baseline. Licence MIT (z_validate.c header), usability copyable.
- Out-of-bounds read: the main loop loads the next shifted vector before the loop check, so it reads up to 30 bytes (AVX2) or 14 bytes (SSE4) past the input end for most lengths, can fault near an unmapped page and trips ASan; test.lua's padding hides it. A Python model of HEAD's logic matched a strict decoder on 4.25 million cases, and the F0 fix 2b0ad07 changed only table constants, so the README timings hold for valid input. lemire/validateutf8-experiments carries an adapted port (zwegneravx) at 1.28x/1.82x over the fastvalidate-style 'basic' routine. Plain inline breaks -O0 builds, cont is maybe-uninitialized under -Werror, and there is no runtime dispatch.

## Caveats and trade-offs

The license is MIT, given only in the header of z_validate.c (commit 507bdea 'Add MIT license to library'). There is no LICENSE file, and test.lua and rules.py carry no license text. The baseline is an older SIMD validator, not a scalar one, and the 'fastest validator in the world' statement is the author's. The benchmark harness is a private modification and is not in the repo. The README table was written on 2019-11-15, before the error tables were fixed for missing F0 overlong sequences on 2019-11-17 (2b0ad07, a correctness bug reported on HN) and before the ASCII early-exit change on 2019-11-18 (cf48201), so the numbers were measured on pre-fix code. The baseline fastvalidate-utf-8 is marked obsolete in its own README in favour of simdutf (already catalogued). Only AVX2 and SSE4 are supported, and AVX-512 is untested. [retier] The license is MIT, given only in the header of z_validate.c; no LICENSE file. The baseline is an older SIMD validator, not a scalar one, and the benchmark harness (a modified fastvalidate-utf-8 benchmark) is not published; the README table (2019-11-15) predates the F0 table fix 2b0ad07, which changed only constants, so the timings hold. Independent numbers: lemire/validateutf8-experiments' adapted port (zwegneravx) runs 1.28x and 1.82x the speed of the fastvalidate-style 'basic' routine. Out-of-bounds read: the main loop loads the next shifted vector before the loop check, so it reads up to 30 bytes (AVX2) or 14 bytes (SSE4) past the input end for most lengths, can fault near an unmapped page and trips ASan; test.lua's padding hides it. Plain inline breaks -O0 builds, cont is maybe-uninitialized under -Werror, no runtime dispatch, abandoned since 2019-11-18.

Single C file, x86 AVX2 or SSE4 only; no AVX-512 or ARM version; an AVX-512 port is only proposed in the README.

## Maintenance

Abandoned since 2019-11-18 (9 commits; the maintainer's 2020 wip branch with AVX-512/NEON never reached master). MIT-licensed via the z_validate.c header only, with no LICENSE file. It is small enough to vendor, but fix the tail over-read first; for production prefer simdutf.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** First-party README table (best of 50, cycles/byte) on a '2.4GHz Haswell laptop', with no CPU model or compiler version. The harness is a private modification of the fastvalidate-utf-8 benchmark and is not in the repo, so the evidence is C. The numbers also predate the 2019-11-17 correctness fix (2b0ad07), which would cap them at C regardless.
- **Retiered** C to B: Enricher: lemire/validateutf8-experiments carries an adapted port (zwegneravx) measured at 1.28x and 1.82x over the fastvalidate-style 'basic' routine, an independent measurement; a Python model of the validation logic matched a strict decoder on 4.25 million cases and the F0 fix changed only table constants, so the README timings hold for valid input. C to B, with the tail over-read recorded.
- **Verifier notes:** Numbers match the README table. The license was wrong in the record: z_validate.c carries an MIT header, so usability is copyable. Metadata checked: 222 stars, 8 commits, not a fork, last commit 2019-11-18 (abandoned). Shortcomings: private harness, unnamed CPU model and compiler, numbers predating a correctness fix (F0 overlong), no ASCII gain over the asciipath baseline, and a baseline that is itself superseded by simdutf.
- **Fields the verifier corrected:** `license`, `usability`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-25 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/zwegner/faster-utf8-validator>
  - <https://github.com/zwegner/faster-utf8-validator/commits>
  - <https://github.com/zwegner/faster-utf8-validator/commits/master>
  - <https://github.com/zwegner/faster-utf8-validator/commits/master/README.md>
  - <https://raw.githubusercontent.com/zwegner/faster-utf8-validator/HEAD/README.md>
  - <https://raw.githubusercontent.com/zwegner/faster-utf8-validator/HEAD/z_validate.c>
  - <https://raw.githubusercontent.com/zwegner/faster-utf8-validator/HEAD/rules.py>
  - <https://raw.githubusercontent.com/zwegner/faster-utf8-validator/HEAD/test.lua>
- **Sources the enricher read:**
  - <https://github.com/zwegner/faster-utf8-validator>
  - <https://raw.githubusercontent.com/zwegner/faster-utf8-validator/HEAD/README.md>
  - <https://raw.githubusercontent.com/zwegner/faster-utf8-validator/HEAD/z_validate.c>
  - <https://raw.githubusercontent.com/zwegner/faster-utf8-validator/HEAD/rules.py>
  - <https://raw.githubusercontent.com/zwegner/faster-utf8-validator/HEAD/test.lua>
  - <https://github.com/zwegner/faster-utf8-validator/commits/master>
  - <https://github.com/zwegner/faster-utf8-validator/commit/2b0ad07>
  - <https://github.com/zwegner/faster-utf8-validator/commit/cf48201>
  - <https://github.com/zwegner/faster-utf8-validator/branches>
  - <https://github.com/zwegner/faster-utf8-validator/issues?q=is%3Aissue>
  - <https://github.com/zwegner/faster-utf8-validator/issues/3>
  - <https://github.com/zwegner/faster-utf8-validator/issues/5>
  - <https://github.com/zwegner/faster-utf8-validator/issues/6>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/benchmarks/benchmark.cpp>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/src/avx2/implementations.h>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/src/generic/utf8_zwegner_algorithm.h>
  - <https://github.com/lemire/validateutf8-experiments/tree/master/benchmarks>
  - <https://github.com/lemire/validateutf8-experiments/tree/master/dependencies>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/zwegner/faster-utf8-validator`) · [data/wave13/enrich/raw/github_com_zwegner_faster_utf8_validator.json](../../../data/wave13/enrich/raw/github_com_zwegner_faster_utf8_validator.json) (enrichment confidence 0.85)

</details>
