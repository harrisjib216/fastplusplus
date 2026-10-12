# Cloudflare zlib fork

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Zlib` · 🟢 active

> Deprecated Cloudflare fork of zlib 1.2.8 with SSE4.2/NEON hashing and SIMD checksums; about 4x faster deflate than stock zlib.

| | |
|---|---|
| **Beats** | zlib |
| **Claimed result** | zlib-ng discussion 871, deflatebench on Silesia-small.tar. Aug 2025 (mxmlnkn, Ryzen 9 3900X, GCC 13.3.0): level 9 compress Cloudflare 0.476 s vs zlib (zlib-ng minigzip) 2.106 s (4.4x, derived from page data), decompress 0.031 s vs 0.099 s (3.2x, derived from page data); level 6 compress 0.308 s vs 1.149 s (3.7x, derived from page data). Mar 2021 (Dead2, i9-9900K, GCC 4.8.5): level 9 compress 0.544 s vs zlib with its own minigzip 2.760 s (5.1x, derived from page data), decompress 0.041 s vs 0.131 s (3.2x, derived from page data). Cloudflare output at level 9 is about 0.5% larger (6,404,085 vs 6,371,682 bytes). |
| **Workload** | Level-9 compress and decompress of Silesia-small.tar via deflatebench/minigzip. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3900X (2025); Intel i9-9900K (2021) |
| **Compiler and flags** | GCC 13.3.0 (2025 run); GCC 4.8.5 (2021 run); flags not stated |
| **Adoption** | 706 stars |
| **Last commit** | 2026-02-25 |
| **Links** | [repository](https://github.com/cloudflare/zlib) · [benchmark](https://github.com/zlib-ng/zlib-ng/discussions/871) |

## Verdict

The zlib-ng maintainers' deflatebench runs on Silesia-small.tar measured Cloudflare zlib against stock zlib: on a Ryzen 9 3900X with GCC 13.3.0 (2025), level 9 compression took 0.476 s vs 2.106 s and decompression 0.031 s vs 0.099 s; on an i9-9900K with GCC 4.8.5 (2021), level 9 compression took 0.544 s vs 2.760 s. Compiler flags were not stated.

## Use it when

- Legacy C/C++ code that links zlib and needs level 6-9 deflate 3.7-4.4x faster with byte-compatible streams and no API changes (zlib-ng discussion 871: level 9 0.476 s vs 2.106 s on Silesia-small, Ryzen 9 3900X).
- Rust projects already using cloudflare-zlib-sys that cannot switch yet; Cloudflare itself recommends moving to zlib-rs.
- x86-64 servers with SSE4.2 or ARMv8 machines with the CRC extension, where a fixed build target is acceptable.
- High-level compression (levels 6-9) where its speed matches zlib-ng's and the API surface of zlib 1.2.8 is enough.

## Skip it when

- New projects: the README marks it deprecated with no further development planned; zlib-ng (actively maintained, runtime CPU dispatch) is as fast at level 9 and faster at levels 1-6, and libdeflate is faster still for whole-buffer use.
- Fast levels: at level 1 it took 0.147 s vs zlib-ng 0.078 s and libdeflate 0.076 s in the 2025 run (it keeps zlib-like ratio, 44.16%, where zlib-ng trades ratio for speed).
- Portable binaries: configure aborts on x86-64 without SSE4.2 and on aarch64 without CRC ('CRC and SSE4.2 support is required') and compiles with -msse4.2 or -march=armv8-a+crc, so the build will not run on older CPUs; there is no runtime dispatch except for PCLMUL CRC.
- Code that calls newer zlib APIs: the 1.2.8-based zlib.h lacks crc32_z, adler32_z, gzfread, gzfwrite, deflateGetDictionary, inflateCodesUsed and crc32_combine_gen.
- Pipelines that need output identical to stock zlib (tests with golden files, reproducible archives): the different hash produces different, at level 9 about 0.5% larger, streams.

## How it is fast

Deflate hashes 4 input bytes with one hardware CRC32C instruction (_mm_crc32_u32 on SSE4.2, __crc32cw on ARMv8 CRC) instead of zlib's 3-byte rolling shift-xor hash, which gives fewer hash collisions and shorter chain walks, and longest_match compares several bytes per step using wide unaligned loads. CRC-32 uses PCLMULQDQ carry-less-multiply folding on x86 (code copied from zlib-ng) and the ARMv8 __crc32d/w/h/b instructions on aarch64. Adler-32 uses SSSE3/NEON SIMD, and inflate uses Chromium-derived SSE2/NEON chunk copies (inffast_chunk, chunkcopy); PR #23 measured 15-34% faster decompression on Silesia files from those last two.

## Compared with alternatives

Rarely: pick it only when you need a zlib-1.2.8-compatible library already wired into your build (for example via cloudflare-zlib-sys) and cannot move; otherwise zlib-ng gives the same level-9 speed with active maintenance and runtime dispatch, and libdeflate is faster with better ratio when whole buffers suffice.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (configure/make or CMake); also a Rust -sys crate |
| **Dependencies** | none |
| **Minimum toolchain** | C89-style C (zlib 1.2.8 code base) built with GCC or Clang supporting -msse4.2 (x86-64) or -march=armv8-a+crc (aarch64) |
| **Platforms** | x86-64 with SSE4.2 (PCLMUL optional, detected at runtime for CRC-32) and aarch64 with NEON and CRC; other architectures fall back to a generic multiply-xor hash in the source, but the README and configure checks only target these two |
| **Thread safety** | Same model as zlib: separate z_stream objects are independent and can run on different threads (bundled zlib README: 'All the code is thread safe'); the PCLMUL CPU check in crc32.c uses a lazily initialised static flag. |
| **Drop-in for the baseline** | partial — same zlib API, ABI and stream format, but it exposes only the zlib 1.2.8 API set (no crc32_z, gzfread and other 1.2.9+ functions), requires SSE4.2/ARMv8 CRC, and its compressed bytes differ from stock zlib |

## Gotchas

- The fork reports ZLIB_VERSION 1.2.8; selected upstream security fixes were backported by hand (the 2018 sym_buf fix, the CVE-2022-37434 extra-field bound, CVE-2016-9842 in Oct 2023, NULL checks and inflate state zeroing in Feb 2026), so version checks by scanners misreport it and anything not backported stays unfixed after deprecation.
- The default branch is gcc.amd64, not master; check out that branch when vendoring.
- zlib-ng's maintainer notes in discussion 871 that the fork keeps the old zlib code style and lands 'mega-commits' mixing optimizations and refactoring, with no public CI, which makes auditing hard.
- Compressed output is not bit-identical to madler/zlib; ratio is slightly worse at level 9 (40.696% vs 40.490%) and slightly better at level 1 (44.160% vs 44.805%).

## Known shortcomings

- Tier B on zlib-ng discussion #871 (public deflatebench, no flags). A fork of madler/zlib rather than zlib-ng, so it stands on its own evidence, but it is deprecated and its level 9 output is about 0.5% larger.
- Deprecated; based on the zlib 1.2.8 API (lacks crc32_z, adler32_z, gzfread, gzfwrite, deflateGetDictionary, inflateCodesUsed), so only a partial drop-in. configure refuses x86-64 without SSE4.2 and aarch64 without CRC, compiles with -msse4.2 and has no runtime dispatch except PCLMUL; output is not byte-identical to zlib; level 1 is about 2x slower than zlib-ng and libdeflate; security fixes are backported by hand. PR #23 (+15-34% inflate from Chromium's adler32/chunkcopy) is open.

## Caveats and trade-offs

GitHub fork of madler/zlib (default branch gcc.amd64). README marks it deprecated: Cloudflare is avoiding memory-unsafe languages, plans no further development, and recommends zlib-rs; the February 2026 commits are hardening fixes (NULL checks, inflate state zeroing). Its higher levels emit slightly larger output than zlib (level 9: 6,404,085 vs 6,371,682 bytes on Silesia-small). In the same 2025 run zlib-ng (0.546 s) and libdeflate (0.441 s) are as fast or faster at level 9 with smaller output. Not included in lzbench. The repo itself carries no benchmark numbers.

Drop-in zlib replacement; README calls it a fork with massive performance improvements; ratio slightly lower than zlib (40.696% vs 40.490%).

## Maintenance

Deprecated by Cloudflare (no further development; recommends zlib-rs); last commits on 2026-02-25 are backported hardening fixes, and the Zlib license makes it easy to vendor if you must.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** zlib-ng discussion 871 ('2.0.0 Benchmark comparisons') runs the public deflatebench harness (github.com/zlib-ng/deflatebench) on Silesia-small.tar and lists Cloudflare zlib next to stock zlib at levels 1-9 in two runs (i9-9900K/GCC 4.8.5, Ryzen 9 3900X/GCC 13.3.0); all quoted numbers match. Measured by the zlib-ng maintainers, independent of Cloudflare, but no compiler flags are stated, so B, not A.
- **Verifier notes:** Numbers verified on discussion 871. Fold question: it is a fork of the baseline (madler/zlib), not of the listed zlib-ng, and has its own independent evidence and distinct SIMD/CRC code, so it stands as its own entry rather than folding into zlib-ng; tag it deprecated. maintenance_status left 'active' by commit date (2026-02-25) although the authors announced no further development.
- **Fields the verifier corrected:** `claimed_speedup`, `is_fork_of`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/zlib-ng/zlib-ng/discussions/871>
  - <https://github.com/cloudflare/zlib>
  - <https://github.com/cloudflare/zlib/commits/gcc.amd64>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/cloudflare/zlib>
  - <https://github.com/cloudflare/zlib/commits/gcc.amd64>
  - <https://github.com/cloudflare/zlib/issues>
  - <https://github.com/cloudflare/zlib/pull/23>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/README>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/configure>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/Makefile.in>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/deflate.c>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/crc32.c>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/inflate.c>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/zlib.h>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/zconf.h>
  - <https://raw.githubusercontent.com/cloudflare/zlib/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/cloudflare-zlib-sys>
  - <https://github.com/zlib-ng/zlib-ng/discussions/871>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/cloudflare/zlib`) · [data/wave9/enrich/raw/github_com_cloudflare_zlib.json](../../../data/wave9/enrich/raw/github_com_cloudflare_zlib.json) (enrichment confidence 0.85)

</details>
