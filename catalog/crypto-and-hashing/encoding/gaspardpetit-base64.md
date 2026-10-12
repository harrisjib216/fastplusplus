# GaspardPetit SIMD base64

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Small BSD-3 C/C++ Base64 codec with AVX2/NEON kernels; edges out aklomp/base64, simdutf and Turbo-Base64 at 32 KiB.

| | |
|---|---|
| **Beats** | base64 (aklomp/base64, the reference SIMD-accelerated C99 base64 codec) |
| **Claimed result** | Windows 32 KiB combined encode+decode: 11.155 GB/s vs aklomp/base64 9.118 GB/s (\~1.22x), Turbo-Base64 10.206 GB/s (\~1.09x) and simdutf 9.2.0 9.077 GB/s (\~1.23x) (ratios derived from page data). Also leads Linux 32 KiB (9.802 GB/s) and ranks #2 on macOS (7.179 GB/s), each on different hardware. |
| **Workload** | Combined encode+decode of a 32 KiB payload, measured by the base64-benchmark harness across input sizes 32B-64KiB |
| **Metric** | throughput |
| **Hardware** | Windows: Intel Core i9-13900K @ 3.0 GHz. Linux: Ubuntu 24.04, AMD Ryzen 7 5700G. macOS: MacBook Air M4 (named on gaspardpetit.github.io/base64-benchmark). |
| **Compiler and flags** | Windows: MSVC 19.51 (VS 2026, v145 toolset), Release\|x64, /O2 (MaxSpeed) with intrinsics and /arch:AVX2 on base64_avx2.c. Linux: Clang 20.1.2, CMake Release (-mavx2 on the AVX2 file). macOS: AppleClang 21, CMake Release. |
| **Adoption** | 0 stars (new library); the benchmark repo that surfaced it has 117 stars |
| **Last commit** | 2026-09-18 |
| **Links** | [repository](https://github.com/gaspardpetit/base64) · [benchmark](https://github.com/gaspardpetit/base64-benchmark#compared-implementations) |

## Verdict

In the author's base64-benchmark (32 B to 64 KiB, Release builds, default wrapper-inclusive reports), combined 32 KiB encode+decode on an i9-13900K with MSVC 19.51 /O2 /arch:AVX2 was 11.16 GB/s, against 10.21 for Turbo-Base64, 9.12 for aklomp/base64 and 9.08 for simdutf 9.2.0 (about 1.09-1.23x). The Ryzen 7 5700G (Clang 20.1) and M4 (AppleClang 21) runs led by only 1-3% (9.78 vs 9.49 GB/s aklomp; 7.60 vs 7.52 GB/s simdutf in the current page data, derived from the page's result files). Turbo-Base64 was not measured on Linux or macOS, and the README's macOS figure (7.179 GB/s, rank 2) is older than the refreshed page data.

## Use it when

- In-memory encode/decode of payloads from about 256 B to 64 KiB on AVX2 x86-64 or AArch64, where it led or tied the published combined-throughput rankings at 256 B, 1 KiB, 32 KiB and 64 KiB.
- Decode-heavy workloads such as JSON/HTTP/JWT payloads. Its lead is clearer on decode (Linux 32 KiB: 18.15 vs 16.21 GB/s for aklomp) than on encode.
- When you want Turbo-Base64-class AVX2 speed under a permissive license: in the benchmark README's table Turbo-Base64 is GPL-3.0, while this is BSD-3-Clause.
- Portable or header-only builds where you cannot use intrinsics. The scalar path alone (2.66 GB/s combined at 32 KiB on Windows) beat every other architecture-neutral codec in the benchmark, e.g. Chromium modp_b64 at 1.96 GB/s.
- When you need something easy to vendor: a handful of .c/.h files, BSD-3, no dependencies, and a GNU-coreutils-compatible CLI in the same repo.

## Skip it when

- On AVX-512 hardware, or when you need to be sure you have the fastest codec there. There is no AVX-512 backend, and none of the three benchmark CPUs (i9-13900K, Ryzen 7 5700G, Apple M4) exercises the AVX-512 kernels in simdutf or base64-avx512.
- On x86-64 without AVX2 (pre-Haswell), 32-bit x86, or MSVC on ARM64. Dispatch only covers _M_X64 / __x86_64__ AVX2 and __aarch64__ NEON, and everything else gets the scalar path. There is no SSSE3/SSE4 middle tier like aklomp/base64 has.
- Streaming or chunked encode/decode, or line-wrapped (MIME/PEM) input. The API is one-shot, and whitespace makes the decoder fail unless you first run base64_compact (which mutates your buffer). Only the CLI does chunking and wrapping.
- Encode-only workloads on Linux or macOS: aklomp/base64 encoded faster at 32-64 KiB on the Ryzen 5700G (22.88 vs 21.21 GB/s at 32 KiB), and on the M4 the two were within 1%.
- Production code that needs a track record. The repo was created 2026-09-14, has 0 stars, one tag (v1.0.0) and no fuzzing in CI (the CI runs CLI ctest and a GNU coreutils oracle on valid and garbage input), and all the performance evidence comes from the author's own benchmark.

## How it is fast

The x86-64 backend follows the Muła/Lemire AVX2 recipe. Encoding unpacks 6-bit fields with vpmulhuw/vpmullw and translates them with a vpshufb offset table. Decoding packs with vpmaddubsw + vpmaddwd, and its validation hash tables are taken from simdutf (see THIRD_PARTY_NOTICES). The author's own gains are in scheduling and tails: four 24-byte encode blocks per iteration using overlapping 256-bit loads, four 32-byte decode blocks per iteration, errors accumulated in a vector and checked once at the end, separate checked/unchecked and standard/URL-safe loops, and hand-tuned short-length decoders for 24-84 characters. The portable scalar path uses a 64x64 two-character encode table (12 input bits per lookup) and four position-shifted 256-entry uint32 decode tables that are OR-ed together, with invalid characters caught by a single threshold compare per 12 characters.

## Compared with alternatives

Pick it over Turbo-Base64 when you need a BSD license rather than GPL-3.0 and are fine with a slightly faster but unproven codec; pick it over aklomp/base64 or simdutf for in-memory AVX2/NEON decode of payloads up to 64 KiB. Stay with aklomp/base64 for streaming, SSSE3/AVX-512 tiers or maturity, and with simdutf for WHATWG forgiving-base64 (whitespace-tolerant) decoding or AVX-512 machines.

## Integration

| | |
|---|---|
| **Form** | source-drop (compile base64.c or base64.cpp, plus base64_avx2.c with -mavx2 or /arch:AVX2, or base64_neon.c) or header-only (BASE64_HEADER_ONLY / BASE64_CPP_HEADER_ONLY, scalar only) |
| **Dependencies** | none (the C++ layer uses &lt;string&gt; and &lt;stdexcept&gt;; the CLI needs CMake 3.25+) |
| **Minimum toolchain** | C99-style C (the CLI is built as C11); the C++ wrapper writes through std::string::data(), so it needs C++17. Benchmarked with MSVC 19.51, Clang 20.1 and AppleClang 21; runtime AVX2 dispatch needs MSVC x64 or GCC/Clang (__builtin_cpu_supports). |
| **Platforms** | any (scalar); x86-64 with AVX2, detected at runtime including OS YMM-state support; AArch64 NEON selected at compile time |
| **Thread safety** | Not documented. The functions are stateless and write only to caller buffers, and the MSVC AVX2-detection cache uses InterlockedCompareExchange, so concurrent calls on distinct buffers look safe from reading the code. |
| **Drop-in for the baseline** | partial — equivalent padded RFC 4648 output and one-shot semantics, but a different API from aklomp/base64 (no streaming state, no codec flags, no line handling), so call sites need rewriting. |

## Gotchas

- Header-only mode is always scalar, so you get about 2.7 GB/s and not the 10+ GB/s SIMD figures. The SIMD speed needs the compiled build with base64_avx2.c built using -mavx2 or /arch:AVX2 and linked in.
- The C++ base64::decode calls base64url_decode, so it quietly accepts URL-safe and mixed alphabets. For strict standard-alphabet validation, use the C base64_decode.
- base64_decode_unchecked checks only length and padding: invalid characters produce unspecified bytes. The scalar tail also does not appear to reject non-zero trailing bits, so non-canonical encodings decode instead of failing.
- The checked SIMD decoder writes output before reporting an error, and its block stores reach up to 4 bytes past each block's decoded bytes. Size the output with base64_decoded_max_size() and treat the whole buffer as garbage on BASE64_ERROR. Input and output must not overlap.

## Known shortcomings

- The benchmark suite (gaspardpetit/base64-benchmark) is by the same author as the winning codec (conflict of interest); margins over aklomp/base64 and Turbo-Base64 are \~9-22% and ratios are derived from the results page.
- New repo (0 stars, 1 tag, no fuzzing). Turbo-Base64 was not run on Linux/macOS, where the lead over aklomp/simdutf is only 1-3%; aklomp encodes faster on Linux at 32-64 KiB. Header-only build is scalar only (\~2.7 GB/s); no AVX-512 or SSSE3 tier; MSVC ARM64 falls back to scalar; C++ decode silently accepts the URL-safe alphabet; no streaming API.

## Caveats and trade-offs

The benchmark repo and the winning library share an author (gaspardpetit), a conflict-of-interest risk. The library repo was created 2026-09-14 and has 0 stars. Cross-platform figures come from different machines and are not comparable. Margins over Turbo-Base64 (\~9%) and aklomp/simdutf (\~22%) are modest at a single 32 KiB point, and the author notes rankings change with compiler, size and operation. Malformed-input handling is not normalized across implementations.

Runtime-dispatched AVX2/NEON backend plus a slower portable fallback path; margin over #2/#3 (Turbo-Base64, aklomp/base64) is modest (\~9-22%) and could be within noise for a different CPU/compiler

## Maintenance

Active as of 2026-09-18 (tag v1.0.0) and BSD-3-Clause with no dependencies, so it is easy to vendor, but it is a two-week-old, 0-star, single-author project whose only benchmark is also the author's.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A. The base64-benchmark harness is public (src/, CMakeLists.txt with CMAKE_BUILD_TYPE Release and -mavx2 on the AVX2 file; build/msvc/base64.vcxproj Release|x64 with /O2 MaxSpeed and /arch:AVX2). The results page names the compiler and CPU for every run: MSVC 19.51 on an Intel Core i9-13900K @ 3.0 GHz, Clang 20.1.2 on Ubuntu 24.04 with an AMD Ryzen 7 5700G, and AppleClang 21 on a MacBook Air M4. It is not an independent suite, since the benchmark and library share an author, but A does not depend on who ran it.
- **Verifier notes:** All quoted README numbers belong to the GaspardPetit SIMD row. The record wrongly said runs were on GitHub-hosted runners with no CPU model, but the published results page names the i9-13900K, Ryzen 7 5700G and M4 machines, which supports the upgrade to A. BSD-3-Clause, 0 stars and the 2026-09-18 last commit are confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/gaspardpetit/base64-benchmark#compared-implementations>
  - <https://raw.githubusercontent.com/gaspardpetit/base64-benchmark/main/README.md>
  - <https://gaspardpetit.github.io/base64-benchmark/>
  - <https://github.com/gaspardpetit/base64-benchmark/blob/main/CMakeLists.txt>
  - <https://github.com/gaspardpetit/base64-benchmark/blob/main/build/msvc/base64.vcxproj>
  - <https://github.com/gaspardpetit/base64>
  - <https://github.com/gaspardpetit/base64-benchmark>
- **Sources the enricher read:**
  - <https://github.com/gaspardpetit/base64>
  - <https://github.com/gaspardpetit/base64/blob/main/README.md>
  - <https://github.com/gaspardpetit/base64/blob/main/base64.h>
  - <https://github.com/gaspardpetit/base64/blob/main/base64.c>
  - <https://github.com/gaspardpetit/base64/blob/main/base64.hpp>
  - <https://github.com/gaspardpetit/base64/blob/main/base64.cpp>
  - <https://github.com/gaspardpetit/base64/blob/main/base64_avx2.c>
  - <https://github.com/gaspardpetit/base64/blob/main/base64_avx2.h>
  - <https://github.com/gaspardpetit/base64/blob/main/base64_neon.c>
  - <https://github.com/gaspardpetit/base64/blob/main/THIRD_PARTY_NOTICES.md>
  - <https://github.com/gaspardpetit/base64/blob/main/.github/workflows/cli.yml>
  - <https://github.com/gaspardpetit/base64/blob/main/cli/README.md>
  - <https://github.com/gaspardpetit/base64/blob/main/cli/CMakeLists.txt>
  - <https://github.com/gaspardpetit/base64/blob/main/cli/tests/test_api.c>
  - <https://github.com/gaspardpetit/base64/commits/main>
  - <https://github.com/gaspardpetit/base64/tags>
  - <https://github.com/gaspardpetit/base64-benchmark>
  - <https://github.com/gaspardpetit/base64-benchmark#compared-implementations>
  - <https://github.com/gaspardpetit/base64-benchmark/commits/main>
  - <https://github.com/gaspardpetit/base64-benchmark/issues>
  - <https://gaspardpetit.github.io/base64-benchmark/>
  - <https://gaspardpetit.github.io/base64-benchmark/result/encode-msvc1951.js>
  - <https://gaspardpetit.github.io/base64-benchmark/result/decode-msvc1951.js>
  - <https://gaspardpetit.github.io/base64-benchmark/result/encode-clang20.js>
  - <https://gaspardpetit.github.io/base64-benchmark/result/decode-clang20.js>
  - <https://gaspardpetit.github.io/base64-benchmark/result/encode-clang21-macos.js>
  - <https://gaspardpetit.github.io/base64-benchmark/result/decode-clang21-macos.js>
  - <https://github.com/aklomp/base64>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/gaspardpetit/base64`) · [data/wave7/enrich/raw/github_com_gaspardpetit_base64.json](../../../data/wave7/enrich/raw/github_com_gaspardpetit_base64.json) (enrichment confidence 0.62)

</details>
