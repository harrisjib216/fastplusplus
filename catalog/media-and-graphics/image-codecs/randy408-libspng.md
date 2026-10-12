# libspng

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-2-Clause` · 🟡 stale

> Small C PNG decoder/encoder with a simpler API than libpng; decodes 1.02-1.07x faster on most images, 1.36x on 32bpp.

| | |
|---|---|
| **Beats** | libpng 1.6.37 (Debian Bullseye) |
| **Claimed result** | google/wuffs doc/benchmarks.md (third-party, reproducible; libspng 0.7.3, i5-10210U, clang 11.0.1 and gcc 10.2.1 -O3, libpng = 1.00x): 1.02x to 1.05x on the 19k, 40k, 77k and 4002k images, 1.36x on 552k_32bpp with checksum verification, 1.60x with checksums ignored (libpng cannot skip checksums). Older blog run (m3-6Y30): 1.02-1.07x and 1.33-1.39x verify, 1.62x ignore. mango README (i7-11800H, first-party single cold run, SPNG_CRC_USE also disables Adler-32): 2560x1600 decode 37.7 vs 57.3 ms (1.52x), encode 215.9 vs 820.5 ms (3.8x); 4833x5875 decode 296.6 vs 379.5 ms (1.28x), encode 2424.7 vs 14051.3 ms. |
| **Workload** | PNG decode speed in the Wuffs project's 'mimic' benchmarks on six test images from 19k (8bpp) to 4002k (24bpp) decoded bytes, libspng 0.7.3 vs libpng 1.6.37. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-10210U (google/wuffs doc/benchmarks.md run); Intel Core m3-6Y30 at 0.90 GHz for the older Wuffs blog run; Intel Core i7-11800H for the mango README numbers |
| **Compiler and flags** | clang 11.0.1 and gcc 10.2.1 at -O3 with -DWUFFS_MIMIC (doc/benchmarks.md; gcc -O3 test/c/std/png.c -DWUFFS_MIMIC -lm -lpng -lz); libspng spng.c is #included into the harness translation unit; libpng 1.6.37 is the Debian Bullseye package |
| **Adoption** | 843 stars |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/randy408/libspng) · [benchmark](https://raw.githubusercontent.com/google/wuffs/HEAD/doc/benchmarks.md) |

## Verdict

Wuffs' doc/benchmarks.md (the benchmark_url; Debian Bullseye, Intel Core i5-10210U, clang 11.0.1 and gcc 10.2.1 at -O3, Wuffs commit 315b2e52, September 2022) measures libspng 0.7.3 against Debian's libpng 1.6.37 at 1.02x, 1.05x, 1.04x and 1.05x on the 19k, 40k, 77k and 4002k images and 1.36x on 552k_32bpp with checksums verified (1.60x when libspng skips checksums, which libpng's simplified API cannot do); the earlier Wuffs blog run on an Intel Core m3-6Y30 gives 1.02-1.07x and 1.33-1.39x. In that harness libspng still skips the final IDAT CRC-32 but also pays a scalar RGBA-to-BGRA swap that libpng does not, while mango's 1.28-1.52x decode figures come from a single cold run with libspng's CRC-32 and Adler-32 checks off.

## Use it when

- You want a small, embeddable PNG reader/writer (two C files plus zlib or miniz) with a simpler API than libpng and slightly faster decoding.
- Decoding 32bpp RGBA PNGs to RGBA8: 1.36x libpng 1.6.37 with checksum verification in Wuffs' September 2022 run (392 vs 289 MB/s, libspng 0.7.3).
- Untrusted input where you want explicit limits: spng_set_image_limits() and spng_set_chunk_limits() cap dimensions and chunk memory to guard against decompression bombs, and the code is fuzzed on OSS-Fuzz.
- Progressive or row-by-row decoding and encoding of large images with a fixed small working set (two rows, three if interlaced).
- arm64 targets with indexed-colour or truecolour images, where the NEON defilter and palette-expansion paths apply.

## Skip it when

- Maximum decode speed: on the same Wuffs harness Wuffs decodes at 1.55-3.16x libpng (1.5-2.6x libspng, derived from page data), and image-png and fpng are also faster; libspng is only 1.02-1.07x libpng on 8bpp and 24bpp images.
- Fast encoding at libpng-equivalent settings: open issue #224 (labelled bug, confirmed) shows libspng at 740 ms vs libpng 510 ms with zlib-ng at level 6 on a 2708x2160 RGB image, and #274 reports 64-bit encode 3x slower than 32-bit; fpng, fpnge or mtpng are the fast encoders.
- Animated PNG (APNG): still listed as planned in the README.
- Code that is written against libpng's API or needs libpng's transform set: the APIs are incompatible, and gamma correction is not implemented for SPNG_FMT_PNG, G8, GA8 and GA16 outputs.
- Projects that need an actively developed library: the last code change was v0.7.4 (2023-05-08); 2026 commits only bump the copyright year, with 69 open issues and 18 open PRs.

## How it is fast

It inflates the IDAT stream one scanline at a time into a two-row buffer using whole IDAT chunks per read, then defilters with SSE2 (x86) or NEON (arm64) Sub/Avg/Paeth kernels derived from libpng's own intrinsics, with optional target_clones (AVX2) for the Up filter. Row-level fast paths (memcpy when the output layout matches, a dedicated RGB8 to RGBA8 widening, NEON palette expansion) replace per-pixel transform chains. Inflate itself is whatever zlib it links, so on large images the gain over libpng is small; the biggest win in third-party data is on 32bpp images.

## Compared with alternatives

Pick libspng over image-png or Wuffs when you need a C library that both decodes and encodes, handles every standard chunk and is a two-file drop-in; pick Wuffs for raw decode speed (1.5-2.6x libspng in Wuffs' own run, derived from page data) and fpng, fpnge or mtpng when encode speed matters.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | zlib (&gt;= 1.2.11 for inflateValidate and Adler-32 control) or miniz via SPNG_USE_MINIZ; libm |
| **Minimum toolchain** | C99 (meson c_std=c99); CMake or Meson builds, or compile spng.c directly; SSE2 enabled by default on x86 without extra flags |
| **Platforms** | any platform with 32-bit int and size_t, CHAR_BIT 8 and two's complement (16-bit targets unsupported); SIMD on x86 (SSE2 tested, SSSE3/SSE4.1 selectable) and arm64 NEON (only arm64 builds are tested) |
| **Thread safety** | not documented; all decoder and encoder state lives in the spng_ctx (spng.c has no mutable globals), so one context per thread is the safe pattern |
| **Drop-in for the baseline** | no |

## Gotchas

- spng_decode_image() returns at end-of-image without reading the rest of the last IDAT chunk, so that chunk's CRC-32 is only checked if you then call spng_decode_chunks() (Wuffs' harness flags this as WUFFS_MIMICLIB_PNG_DOES_NOT_VERIFY_FINAL_IDAT_CHECKSUMS, still defined at Wuffs HEAD).
- spng_set_crc_action(ctx, SPNG_CRC_USE, ...) also turns off Adler-32 checking of the zlib stream, not only chunk CRCs; SPNG_CTX_IGNORE_ADLER32 is silently ignored with miniz or zlib older than 1.2.11.
- Use v0.7.4 or later: older releases do a wild read on a zero-length eXIf chunk (fixed in #248, reported as security notice #285, no CVE), and v0.7.2 fixed an encoder heap overflow.
- The README's 'outperforms the reference implementation' is backed only by a chart image on libspng.org; the repository has no benchmark numbers of its own.

## Known shortcomings

- Tier B on the Wuffs benchmark blog (Intel Core m3-6Y30, gcc -O3, harness test/c/mimiclib/png.c at wuffs v0.3.0-beta.1). Not A: the libspng commit is unpinned and libspng 0.6.2 skipped Adler-32 through an inverted-flag bug (fixed 9c35dc3), so the 1.62x row has libspng skipping checksums while libpng verifies; checksum-verified rows are 1.02-1.39x. In mango's png_benchmark.cpp, spng ignores CRC, encodes at level 3 and writes files 14-21% larger.
- libspng skips the final IDAT CRC-32 (decode_image stops at SPNG_STATE_EOI); the mango rows are first-party single cold runs where SPNG_CRC_USE also disables Adler-32, libpng runs defaults in native layout and milliseconds are printed as us%10. Encode is slower than libpng per its own issues (#224 confirmed: 740 ms vs 510 ms at level 6 with zlib-ng; #274: 64-bit encode 3x slower). Maintenance is stale (last code release v0.7.4 on 2023-05-08, 69 issues and 18 PRs open), not active as recorded. Retier-19 raises the tier to A on the reproducible doc/benchmarks.md run (i5-10210U, clang 11.0.1 and gcc 10.2.1 -O3).
- Re-found by seed group w10-mine-l from the same source (Wuffs doc/benchmarks.md, libspng 0.7.3 vs libpng 1.6.37, 1.02x to 1.05x on five rows, 1.36x on 552k 32bpp, 1.60x with checksum ignored; i5-10210U, gcc 10 and clang 11); no new evidence.

## Caveats and trade-offs

Decode gains over libpng are modest and image-dependent (1.02x to 1.07x on four of five Wuffs test images). Wuffs' mimiclib notes that libspng 0.6.2 did not verify Adler-32 (an inverted SPNG_CTX_IGNORE_ADLER32 check, fixed in commit 9c35dc3, Dec 2020) and never verifies the final IDAT chunk's CRC-32; the blog does not pin the libspng commit, so the small gains may partly reflect skipped verification. In mango's png_benchmark.cpp the spng decoder is set to SPNG_CRC_USE (CRC errors ignored) while libpng uses defaults, and the spng encoder uses compression level 3 with the Up filter only while libpng uses default settings, so spng's 3.8x to 5.8x encode lead comes with 14% to 21% larger files (3232 vs 2843 KB; 34083 vs 28180 KB). The same blog shows libpng with zlib-ng is 1.01x to 1.21x faster than stock libpng, which narrows the gap. Code activity: the only 2026 commits are a copyright-year update; the previous commit is from 2023-12-20. [retier] libspng skips the final IDAT CRC-32 (decode_image stops at SPNG_STATE_EOI) while paying a scalar RGBA-to-BGRA swap in the harness. The mango rows are first-party single cold runs where SPNG_CRC_USE also disables Adler-32, libpng runs its defaults in native layout, and milliseconds are printed as us%10 (decimal error). Encode is slower than libpng in the project's own issues: #224 (confirmed bug) spng 740 ms vs libpng 510 ms at level 6 with zlib-ng; #274 64-bit encode 3x slower. #285 eXIf wild read fixed in 0.7.4 without a CVE.

Simpler API than libpng, not API-compatible; security focus (OSS-Fuzz); does not require zlib (optional miniz); encoder included; progressive read supported; animated PNG still planned. Same file format so output is interchangeable.

## Maintenance

BSD-2-Clause and easy to vendor, but in maintenance mode: last release v0.7.4 (2023-05-08), no code changes since December 2023, issues and PRs unanswered.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Third-party measurement by the Wuffs author against Debian's libpng16 with public harness code (google/wuffs v0.3.0-beta.1 test/c/std/png.c and test/c/mimiclib/png.c), gcc -O3 and clang 9/gcc 10, on an Intel Core m3-6Y30, plus independent numbers in mango's examples/image/png_benchmark; not raised to A because the libspng commit measured is not pinned and the harness notes libspng 0.6.2 skipped Adler-32 verification (inverted-flag bug fixed in commit 9c35dc3), so equal work against libpng is not assured.
- **Retiered** B to A: Raised B to A: the record's benchmark_url, google/wuffs doc/benchmarks.md, is a reproducible third-party run that pins libspng 0.7.3 (post-9c35dc3), Wuffs 315b2e52, an Intel Core i5-10210U, clang 11.0.1 and gcc 10.2.1 at -O3 with the public mimic harness (test/c/std/png.c -DWUFFS_MIMIC), giving libspng 1.02-1.05x libpng on the small images, 1.36x on 552k_32bpp with checksum verification and 1.60x with checksums ignored; the record had cited the older blog run on an m3-6Y30. Public code, compiler, flags and CPU are all stated, so A. Caveats: libspng still skips the final IDAT CRC-32 (decode_image stops at SPNG_STATE_EOI) while paying a scalar RGBA-to-BGRA swap; the mango README rows are first-party, single cold runs where SPNG_CRC_USE also disables Adler-32 and libpng runs its defaults in native layout, with milliseconds printed as us%10 (a decimal error). Maintenance correction: the last code release is v0.7.4 (2023-05-08) with 69 issues and 18 PRs open, so not active.
- **Verifier notes:** All cited Wuffs and mango numbers are on the pages and belong to the libspng/spng rows. The record wrongly said the blog gives no CPU model (it names the Intel Core m3-6Y30 under Hardware); the tier stays B rather than A because of the Adler-32 verification bug in libspng 0.6.2 and the unpinned version. Metadata checked: BSD-2-Clause, 843 stars, last commit 2026-08-31 (copyright-year bump only).
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `claimed_speedup`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** seed w10-mine-l (wave 10)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nigeltao/nigeltao.github.io/master/blog/2021/fastest-safest-png-decoder.md>
  - <https://raw.githubusercontent.com/google/wuffs/v0.3.0-beta.1/test/c/mimiclib/png.c>
  - <https://github.com/randy408/libspng/commit/9c35dc3>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/README.md>
  - <https://github.com/randy408/libspng>
  - <https://github.com/randy408/libspng/commits/master>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/README.md>
  - <https://github.com/t0rakka/mango>
  - <https://github.com/t0rakka/mango/tree/main/examples/image/png_benchmark>
  - <https://raw.githubusercontent.com/t0rakka/mango/main/examples/image/png_benchmark/png_benchmark.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/main/examples/image/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/randy408/libspng>
  - <https://github.com/randy408/libspng/commits/master>
  - <https://github.com/randy408/libspng/releases>
  - <https://github.com/randy408/libspng/issues>
  - <https://github.com/randy408/libspng/issues/285>
  - <https://github.com/randy408/libspng/issues/224>
  - <https://github.com/randy408/libspng/issues/274>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/README.md>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/spng/spng.h>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/spng/spng.c>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/meson.build>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/docs/build.md>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/docs/decode.md>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/docs/encode.md>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/docs/context.md>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/docs/chunk.md>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/tests/README.md>
  - <https://raw.githubusercontent.com/randy408/libspng/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/google/wuffs/v0.3.0-beta.1/test/c/mimiclib/png.c>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/test/c/mimiclib/png.c>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/test/c/std/png.c>
  - <https://raw.githubusercontent.com/t0rakka/mango/main/examples/image/png_benchmark/png_benchmark.cpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/randy408/libspng`) · [data/wave10/enrich/raw/github_com_randy408_libspng.json](../../../data/wave10/enrich/raw/github_com_randy408_libspng.json) (enrichment confidence 0.8)

</details>
