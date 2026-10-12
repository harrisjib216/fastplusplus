# Turbo-Base64

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0` · 🟢 active

> GPL-3 C base64 codec with SSSE3/AVX2/AVX-512 VBMI/Neon kernels; author's tables beat Chrome's codec 7-11x, aklomp 11-70%.

| | |
|---|---|
| **Beats** | base64 (RFC 4648 encode/decode) |
| **Claimed result** | On the i7-9700K with gcc 11.2 and a 1 MB buffer (2022.02), tb64v256 AVX2 runs at 29,086/29,748 MB/s encode/decode. That compares with Google Chrome base64 at 2,541/4,289 MB/s (about 11.4x encode and 6.9x decode, derived from page data), lemire fb64avx2 at 23,686/21,231 and aklomp b64avx2 at 26,153/22,515. At 50,000 B, tb64v256 reaches 32,794/37,837 MB/s against b64avx2 at 27,789/22,264 and fb64avx2 at 25,305/21,980. On the Ryzen 9 7950X (gcc 12.2, 1 MB, 2023.07), tb64v512vbmi reaches 77,619/76,716 MB/s, but it is compared only with its own variants and with memcpy (37,047/31,694), with no external baseline on that machine. |
| **Workload** | Single-thread encode/decode with error checking. On the AMD Ryzen 9 7950X: 1,000,000 B and 10,000 B buffers. On the Intel i7-9700K: 50,000 B, 1 MB and short strings of 4-128 B. There are also ARM tables (Apple M1, ODROID-N2). |
| **Metric** | throughput |
| **Hardware** | Intel i7-9700k 3.6GHz; AMD Ryzen 9 7950X @4.5GHz DDR5-6000 CL30; Apple M1 3.5GHz; ARMv8 A73 ODROID-N2 1.8GHz |
| **Compiler and flags** | gcc-12.2 (Ryzen 9 7950X, 2023.07); gcc 11.2 (i7-9700K, 2022.02). The README states no flags. The public makefile uses -O3 with -march=haswell for the AVX2 file and -march=skylake-avx512 -mavx512vbmi for the AVX-512 file. |
| **Adoption** | 340 stars |
| **Last commit** | 2026-06-28 |
| **Links** | [repository](https://github.com/powturbo/Turbo-Base64) · [benchmark](https://github.com/powturbo/Turbo-Base64#benchmark-incl-the-best-simd-base64-libs) |

## Verdict

These are the author's own tables, and the competitor harness is not published. On an i7-9700K with gcc 11.2 (2022), the AVX2 path encodes/decodes a 1 MB buffer at 29.1/29.7 GB/s, against 2.5/4.3 for Google Chrome's codec (about 11.4x/6.9x) and 26.2/22.5 for aklomp AVX2; the Ryzen 9 7950X AVX-512 VBMI figures (77.6/76.7 GB/s) have no external row. As a partial outside check, base64-turbo's criterion harness (upstream per-file flags, default partial-check build) measured it at 80.7/107.8 GiB/s at 64 KiB on Zen 5 EPYC 9R45, against 13.5/27.9 for Rust's base64 crate.

## Use it when

- x86-64 servers with AVX-512 VBMI (Ice Lake or later, Zen 4/5) moving 10 KB to multi-MB standard-base64 blobs, where GPL-3 or a commercial license is acceptable. The author's Ryzen 9 7950X table shows 77.6/76.7 GB/s at 1 MB, against 45.3/46.7 GB/s for its own AVX2 path. On Zen 5 in base64-turbo's harness it still leads at 10 MB (37.7/55.8 vs 29.4/45.7 GiB/s).
- AVX2-only machines where you want more than aklomp/base64 or fastbase64 give. On the author's i7-9700K, tb64v256 beats aklomp b64avx2 by 11%/32% (encode/decode) at 1 MB and 18%/70% at 50 KB.
- Apple M1 or other aarch64 targets built with clang: the M1 50 KB table shows 24.0/15.4 GB/s against aklomp's neon64 at 19.1/12.5.
- CPUs with no usable SIMD path (the RISC-V build is scalar only): the tb64x scalar codec runs 6.5/5.5 GB/s at 1 MB on the i7-9700K, against Chrome's scalar codec at 2.5/4.3.

## Skip it when

- You can't ship GPL-3 and won't buy a license. ClickHouse dropped it for aklomp/base64 in Sept 2023 (PR 54119) over GPL-3 and its non-thread-safe initialization, and accepted slower base64 in exchange.
- You need base64url (JWT, URLs), MIME/PEM line breaks, whitespace tolerance or forgiving decoding. None is supported, and tb64dec rejects any input over 20 bytes whose length is not a multiple of 4.
- You rely on the decoder to reject every malformed input. The default build checks only part of the input, so corrupted characters in the unchecked parts decode to garbage without an error. Full checking needs make FULLCHECK=1, and the CMake FULLCHECK option is broken (it defines DB64CHECK instead of B64CHECK).
- Memory-safety-sensitive code run under ASAN/fuzzers with exact-size buffers. Open issue #26 (Sept 2024, no reply) reports tb64enc reading past in+inlen and writing past tb64enclen(inlen) for inlen=94.
- You need independently reproducible cross-library numbers. The competitor harness (xtb64.mak, xb64test.h) is not in the repo, and the README tables were last updated in Aug 2023.

## How it is fast

The SIMD kernels follow Mula and Lemire's AVX2 base64 method (arXiv 1704.00605, cited in the source): pshufb splits 3-byte groups, mulhi/mullo shifts unpack 6-bit fields, and a pshufb offset table maps them to ASCII. Decode uses aqrit's hashed-LUT variant (avg_epu8 + two pshufb lookups), with maddubs/madd to pack 6-bit values back into bytes. The AVX-512 VBMI path does encode with vpermb + vpmultishiftqb, per Mula's AVX-512 notes. Loops are unrolled 128-256 bytes with software prefetch. By default only part of the input is validated (in the AVX2 main loop, 1 of every 4 32-byte vectors), which removes most of the check work. The fast scalar path (tb64x) uses an 8 KB 12-bit encode table and four 1 KB decode tables.

## Compared with alternatives

Pick it over aklomp/base64 (BSD-2; ClickHouse's 2023 replacement) or the research codecs fastbase64/base64simd only when you need the last 10-70% of AVX2 throughput, or its AVX-512 VBMI path, on standard-alphabet data and GPL-3 or a commercial license is fine. In Rust, base64-turbo (0BSD, fully validated, base64url) ties it in cache and trails only on DRAM-sized buffers; simdutf is the choice for base64url or forgiving decoding.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (make builds libtb64.a/libtb64.so; the CMake target is turbo::base64); a handful of .c files, so a source-drop also works |
| **Dependencies** | none (libc only) |
| **Minimum toolchain** | C (no standard stated). The README lists GCC&gt;=4.6 or Clang&gt;=3.2 on x86, GCC&gt;=6.3 or Clang&gt;=6.0 on aarch64, Xcode&gt;=9, VS2017 and ppc64le GCC&gt;=8. The AVX-512 file needs -mavx512vbmi support; otherwise build with NAVX512=1. The CMake build needs 3.15+. |
| **Platforms** | x86/x86-64 with runtime dispatch (scalar, SSSE3, AVX, AVX2, AVX-512 VBMI); aarch64 Neon and ppc64le Power9 Altivec chosen at compile time; s390x and big-endian are supported; RISC-V gets only the scalar plus generic v128 build |
| **Thread safety** | Encode/decode calls are stateless. The first-call CPU dispatch (tb64ini) sets a plain static flag and global function pointers with no synchronization, so call tb64ini(0,0) once before starting threads. ClickHouse cited this as 'non-threadsafe initialization'. |
| **Drop-in for the baseline** | partial — standard alphabet and padding only, caller-allocated buffers through a C API, no base64url, no whitespace or line-break handling, no streaming; padding and validation rules differ from strict decoders |

## Gotchas

- Buffers: tb64enc does not write a trailing NUL, so allocate tb64enclen(n)+1 if you terminate the output yourself (issue #23). Open issue #26 shows it can also touch bytes past both buffer ends, so leave slack.
- Validation is partial unless you build with FULLCHECK=1 through make. A return of 0 means both 'invalid' and 'empty input'. Unpadded inputs of 20 bytes or fewer are decoded best-effort (ClickHouse PR 54119 notes this), while longer ones are rejected.
- tb64ini(0,1) turns on the short-string AVX2 mode (_tb64v256\*). Its decoder skips most checks and may read up to 32 bytes past the input end, and a ClickHouse bug (PR 31797) had this path leaking the next string's bytes into encoded output. The mode is ignored on AVX-512 machines.
- On x86-64 the CMake build compiles the scalar core with -march=native, so the library it produces may not run on older CPUs; the makefile does not do this. README MB/s figures are counted on base64-text size for both encode and decode (issue #11), so raw-byte throughput is 0.75x.

## Known shortcomings

- First-party numbers from a harness (xtb64.mak / xb64test.h) that is not public, with no compiler flags stated. Earlier ratio mixed 7950X numbers with an i7 Chrome row; corrected i7 1 MB figures: 29,086/29,748 MB/s vs Chrome 2,541/4,289 (\~11.4x encode, \~6.9x decode).
- GPL-3.0. Codec untouched since 2023-08 (2025-26 commits are contributor build fixes); open ASan issue #26 (encoder over-read/over-write) unanswered since 2024-09. Default build validates only part of the input (AVX2 main loop checks 1 of 4 vectors); the CMake FULLCHECK option is a no-op typo, only `make FULLCHECK=1` validates fully. Lazy CPU dispatch is not thread-safe. No base64url, whitespace or streaming. ClickHouse dropped it in 2023 (GPL, init race) for aklomp/base64.

## Caveats and trade-offs

The numbers are first-party. The build that includes competitor codecs (XBASE64=1: xtb64.mak, xb64test.h, xtb64test_.c) is not public, so the cross-library tables cannot be reproduced from the repo. The Ryzen 7950X AVX-512 table has no Chrome or other external row. The original claim divided 7950X numbers by the i7-9700K Chrome row, a cross-machine ratio, and '\~10-18x' was also miscomputed. The README benchmark tables were last updated in August 2023. The code is GPL-3.0 with a commercial license available.

GPLv3 (separate commercial license available); runtime CPU dispatch picks scalar/SSE/AVX/AVX2/AVX512 path; RISC-V currently falls back to the generic scalar core with no dedicated RVV backend

## Maintenance

The codec itself has not changed since the Aug 2023 release. Later commits (2025-2026) are contributor build fixes for Apple Silicon and RISC-V, and the 2024 ASAN report is still unanswered. It is GPL-3 with a commercial license on request, and small enough to vendor if the license works for you.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README's i7-9700K tables (gcc 11.2) compare against Google Chrome and Linux base64 and against the aklomp and fastbase64 AVX2 codecs. The numbers are first-party, though, and the harness that links those competitor codecs is not in the public repo. tb64app.c only #includes xb64test.h and xtb64test_.c under XBASE64, and the makefile includes xtb64.mak; none of those files are in the tree or the 2023.04/2023.08 tags. The page also states no flags, so this is first-party with partial methodology: C.
- **Verifier notes:** The claimed ratio was invalid because it mixed machines; I replaced it with same-table i7-9700K ratios. The metadata checks out: GPL-3.0, 340 stars, not a fork, not archived, last commit 2026-06-28 (active). I found no independent benchmark: Algolia search of HN turned up only the author's own Show HN posts, and the Muła/Lemire AVX-512 paper (arXiv 1910.05109) does not test it.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** base64-turbo (hacer-bark) harness, Zen 5, 64 KiB: Turbo-Base64 80.7 / 107.8 GiB/s enc/dec.
- **Pages the verifier opened:**
  - <https://github.com/powturbo/Turbo-Base64#readme>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Base64/master/README.md>
  - <https://github.com/powturbo/Turbo-Base64>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Base64/master/makefile>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Base64/master/tb64app.c>
  - <https://arxiv.org/pdf/1910.05109>
  - <https://hn.algolia.com/api/v1/search?query=Turbo-Base64&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=turbobase64>
- **Sources the enricher read:**
  - <https://github.com/powturbo/Turbo-Base64>
  - <https://github.com/powturbo/Turbo-Base64#readme>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/turbob64.h>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/turbob64_.h>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/turbob64v256.c>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/turbob64v128.c>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/turbob64v512.c>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/turbob64d.c>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/turbob64c.c>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/makefile>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/CMakeLists.txt>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/.github/workflows/build.yaml>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/rust/README.md>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/rust/Cargo.toml>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/rust/build.rs>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/rust/src/lib.rs>
  - <https://github.com/powturbo/Turbo-Base64/blob/master/conf.h>
  - <https://github.com/powturbo/Turbo-Base64/issues>
  - <https://github.com/powturbo/Turbo-Base64/issues/26>
  - <https://github.com/powturbo/Turbo-Base64/issues/25>
  - <https://github.com/powturbo/Turbo-Base64/issues/23>
  - <https://github.com/powturbo/Turbo-Base64/issues/19>
  - <https://github.com/powturbo/Turbo-Base64/issues/18>
  - <https://github.com/powturbo/Turbo-Base64/issues/12>
  - <https://github.com/powturbo/Turbo-Base64/issues/11>
  - <https://github.com/powturbo/Turbo-Base64/issues/9>
  - <https://github.com/powturbo/Turbo-Base64/issues/6>
  - <https://github.com/powturbo/Turbo-Base64/commits/master>
  - <https://github.com/powturbo/Turbo-Base64/releases>
  - <https://github.com/powturbo/Turbo-Base64/pulls>
  - <https://github.com/ClickHouse/ClickHouse/pull/31797>
  - <https://github.com/ClickHouse/ClickHouse/pull/54119>
  - <https://github.com/ClickHouse/ClickHouse/issues/31643>
  - <https://github.com/ClickHouse/ClickHouse/issues/45790>
  - <https://github.com/ClickHouse/ClickHouse/issues/41957>
  - <https://hn.algolia.com/api/v1/search?query=turbo-base64&tags=comment&hitsPerPage=15>
  - <https://github.com/hacer-bark/base64-turbo#benchmarks>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/results/c8a-large-latest.txt>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/tb64-sys/build.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/tb64-sys/src/lib.rs>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/powturbo/turbo-base64`) · [data/wave7/enrich/raw/github_com_powturbo_turbo_base64.json](../../../data/wave7/enrich/raw/github_com_powturbo_turbo_base64.json) (enrichment confidence 0.8)

</details>
