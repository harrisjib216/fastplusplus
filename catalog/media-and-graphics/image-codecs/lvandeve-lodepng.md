# LodePNG

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Zlib` · 🟢 active

> Two-file, dependency-free PNG encoder/decoder; decodes small PNGs about 1.1x faster than libpng+zlib 1.2.11, larger ones slower.

| | |
|---|---|
| **Beats** | libpng 1.6.37 (with zlib 1.2.11, as shipped with Debian Bullseye) |
| **Claimed result** | Decode 1.13x (138 vs 122 MB/s, 19k_8bpp), 1.13x (166 vs 147 MB/s, 40k_24bpp), 1.09x (404 vs 370 MB/s, 77k_8bpp); but slower on the larger images: 0.89x (258 vs 289 MB/s, 552k_32bpp_verify_checksum) and 0.77x (165 vs 214 MB/s, 4002k_24bpp). Ratios are the page's vs_mimic column, libpng = 1.00x. |
| **Workload** | PNG decode throughput in MB/s on five test images (19k 8bpp, 40k 24bpp, 77k 8bpp, 552k 32bpp, 4002k 24bpp decoded size) in the Wuffs 'mimic' benchmarks, where lodepng 20220717 is swapped in for libpng behind the same decode harness. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i5-10210U CPU @ 1.60GHz, Debian Bullseye, measured September 2022 |
| **Compiler and flags** | clang 11.0.1 and gcc 10.2.1 are the Debian Bullseye compilers named on the page (it does not say which one built the mimic rows, which carry no compiler suffix); recipe in the header comment of test/c/std/png.c is -O3 plus the 'wuffs mimic cflags' -DWUFFS_MIMIC -lm -lpng -lz. To bench lodepng instead of libpng, test/c/mimiclib/png.c must be edited: the line '#define WUFFS_MIMICLIB_USE_LODEPNG_INSTEAD_OF_LIBPNG 1' ships commented out and the '#include "/path/to/your/copy/of/github.com/lvandeve/lodepng/lodepng.cpp"' placeholder path must point at a lodepng checkout (20220717 in the table). libpng 1.6.37 and zlib 1.2.11 are the Debian Bullseye system builds. |
| **Adoption** | 2.3k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/lvandeve/lodepng) · [benchmark](https://github.com/google/wuffs/blob/main/doc/benchmarks.md) |

## Verdict

Third-party Wuffs mimic benchmark (September 2022, Intel Core i5-10210U, Debian Bullseye, -O3, clang 11.0.1 or gcc 10.2.1 unspecified for mimic rows) decoding five test images to gray or BGRA: lodepng 20220717 reached 138/166/404 MB/s against libpng 1.6.37 with zlib 1.2.11 at 122/147/370 MB/s on the 19k, 40k and 77k images (1.09-1.13x) but 258 vs 289 MB/s on the 552k image and 165 vs 214 MB/s on the 4002k image (0.89x, 0.77x); about parity overall (geomean about 0.99x, derived from page data).

## Use it when

- You want PNG load/save with zero dependencies (no zlib, no libpng) by dropping two files into a C or C++ project, including C90 or old-compiler targets.
- Decoding many small images (icons, sprites, UI assets, tens of KB decoded), where Wuffs' benchmark shows it 1.09-1.13x faster than system libpng.
- Embedded or tooling code that needs both encoder and decoder, full color-type conversion and metadata chunks in one permissively licensed (Zlib) source drop.
- Encoding where smallest file size matters more than speed: its encoder is slow but compresses harder than fpng or stb_image_write (issue #179).

## Skip it when

- Large images or throughput-critical decode: 0.77x of libpng on the 4002k-byte image and 0.89x on the 552k image in Wuffs' table, and slower than stb_image and Wuffs in the issue #179 timings (26 MP/s vs 45 and 59 MP/s on a Ryzen 5 3600).
- Fast encoding: issue #179 measured about 3 MP/s release-build encode vs 137-155 MP/s for fpng; use fpng, fpnge or Zpng when encode time matters.
- Memory-constrained or streaming decode: it holds the whole compressed stream, the whole filtered scanline buffer and the output (plus a second output buffer when color conversion is needed); partial/stream decoding is still an open TODO.
- Untrusted input on versions older than 20261006: an integer overflow in ucvector_reserve and a size_t-to-unsigned Adler-32 length truncation (issue #232) were fixed only on 2026-10-01 and 2026-10-06.
- APNG or libpng-API compatibility: animation chunks are not supported and the API is different.

## How it is fast

It is not built for speed; its small-image edge over libpng comes from low per-call overhead: one pass collects all IDAT data, a two-level Huffman lookup table (9-bit first table, added in 2019 for about 25% faster decoding) drives a simple inflate that decodes two literals per bit refill, and unfiltering runs over the whole scanline buffer at once. Since April 2023 it also uses a slicing-by-8 CRC-32 (eight 256-entry tables). There is no SIMD (the maintainer says so in issue #179) and no streaming, so on large images the extra full-image passes (inflate buffer, unfilter, separate color-conversion buffer) make it fall behind libpng.

## Compared with alternatives

Pick LodePNG when a no-dependency, two-file encoder plus decoder with full color conversion and metadata support matters more than speed; for decode throughput libspng (1.02-1.60x libpng on the same Wuffs page), image-png or Wuffs are faster, and for fast encoding fpng/fpnge win by one to two orders of magnitude.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (standard C library; standard C++ library for the optional C++ wrapper) |
| **Minimum toolchain** | C90 (ANSI C) or C++03 per lodepng.h; README build line g++ -ansi -pedantic -O3 |
| **Platforms** | any (portable scalar code, no SIMD, CHAR_BIT &gt;= 8) |
| **Thread safety** | not documented; lodepng.cpp has no mutable globals (lookup tables are const and each call uses its own state), so concurrent calls with separate LodePNGState objects appear safe |
| **Drop-in for the baseline** | partial — replaces libpng's job in a program but not its API: one-shot whole-image functions, no row callbacks, progressive reading or png_struct-style transforms |

## Gotchas

- Harness detail in the Wuffs numbers: the lodepng mimic path decodes into lodepng's own malloc'd buffer, then memcpy's it into Wuffs' dst and, on the four rows decoded to BGRA (40k_24bpp, 77k_8bpp, 552k_32bpp, 4002k_24bpp, not only the 32bpp one), runs a byte-wise RGBA-to-BGRA swap, while the libpng simplified API decodes straight into BGRA; the measured ratios therefore slightly understate lodepng.
- The benchmarked version is 20220717; the April 2023 slicing-by-8 CRC-32 rewrite and the 2026 overflow-check additions came later and were not re-measured.
- Default decoding converts to the requested color type (8-bit RGBA for lodepng_decode32); set state.decoder.color_convert = 0 to skip that extra full-image pass when you can consume the PNG's native format. 16-bit samples are returned big-endian.
- Open reports: crash with some 16-bit/channel images (issue #227, March 2026, no maintainer reply), stack corruption with lodepng::State (#191); double-frees when clearing and re-setting iTXt/iCCP chunks were fixed in January 2026. The project publishes no release tags (issues #199, #205), so pin a commit.

## Known shortcomings

- Partial win only on the third-party Wuffs doc/benchmarks.md table (lodepng 20220717 vs libpng 1.6.37 on zlib 1.2.11, Sept 2022, decode only): 1.09-1.13x on 19k, 40k and 77k images, 0.89x on 552k and 0.77x on 4002k, geomean about 0.99x (derived from page data); libspng, stb_image and Wuffs are faster on the same page; the harness adds a malloc and memcpy for lodepng. The project itself makes no speed claim.
- Enricher: the Wuffs mimic harness runs a byte-wise RGBA-to-BGRA swap on 4 of 5 rows (40k, 77k, 552k, 4002k decode to BGRA_NONPREMUL) plus a memcpy on all 5 while libpng writes BGRA directly, so the ratios slightly understate lodepng; the measured 20220717 predates the 2023 slicing-by-8 CRC32; no SIMD; issue #179: decode 26 MP/s vs stb 45 vs wuffs 59, encode about 3 MP/s vs fpng 137-155. Security issue #232 (ucvector_reserve overflow, Adler32 size_t truncation) fixed only 2026-10-01/06, use 20261006 or later; open crash #227 with 16-bit images; no release tags.

## Caveats and trade-offs

The project itself makes no speed claim (README has no performance section); the numbers come from the Wuffs project's mimic benchmark. Mixed result: lodepng is 1.09-1.13x faster than libpng only on the three small images (19k, 40k, 77k decoded bytes) and slower on the two larger ones (0.89x on 552k_32bpp_verify_checksum, 0.77x on 4002k_24bpp); geometric mean over the five rows is about 0.99x (derived from page data), i.e. parity overall. On the same page libspng (1.02-1.60x) and stb_image (0.76-1.23x) are comparable or better alternatives, and Wuffs itself is 1.55-3.16x. Decode only; no encode numbers against libpng were reached (fpng's README and lodepng issue #179 show lodepng encoding at \~3-17 MP/s with no libpng row). The libpng baseline is the Debian system build linked to zlib 1.2.11, whose inflate is slow; a libpng built on zlib-ng or libdeflate would likely widen lodepng's deficit on large images. The harness slightly handicaps lodepng: lodepng_decode_memory allocates its own output buffer that the mimic code then memcpy's into Wuffs' dst (plus a per-pixel RGBA-to-BGRA swap on the 32bpp image), while the libpng simplified-API path decodes straight into dst. lodepng version in the table is 20220717, older than the current repo (numbers measured September 2022). The page does not state which of clang/gcc built the mimic rows, and the lodepng mimic path does not support the ignore-checksum quirk, so only the verify_checksum row exists for the 552k image.

Two-file C89/C++ library with no dependencies (lodepng.cpp/lodepng.h, rename to .c for C). Own inflate/deflate, so no zlib needed. Encoder and decoder are small and portable, but the project does not target peak speed; libpng/spng/stb/wuffs are the usual fast choices.

## Maintenance

Actively maintained by its single author (version 20261006, commits in October 2026 hardening allocation-size overflow checks after security report #232), Zlib-licensed and trivially vendored, but with 67 open issues, 32 open PRs and no release tags.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Third-party Wuffs doc/benchmarks.md (PNG section) lists mimiclodepng rows against mimiclibpng = 1.00x with public harness code (test/c/std/png.c plus test/c/mimiclib/png.c, lodepng branch), -O3 recipe in the png.c header comment, compilers clang 11.0.1 / gcc 10.2.1, and CPU Intel Core i5-10210U; same page and tier as the wave 10 libspng retier to A.
- **Verifier notes:** All five lodepng numbers and vs_mimic ratios match the PNG table of google/wuffs doc/benchmarks.md exactly; metadata verified (Zlib license, 2.3k stars, not a fork or archived, last commit 2026-10-06, active). Shortcomings to record: only a partial win (faster on small images, 0.77-0.89x on large ones, \~0.99x geomean derived from page data), third-party 2022 numbers on lodepng 20220717 against a zlib-1.2.11-based libpng, no encode comparison, and libspng/stb/Wuffs are faster alternatives on the same page.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-115 (wave 10); enricher w10 pair-030
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/test/c/std/png.c>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/test/c/mimiclib/png.c>
  - <https://github.com/lvandeve/lodepng>
  - <https://github.com/lvandeve/lodepng/commits>
  - <https://raw.githubusercontent.com/lvandeve/lodepng/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/lvandeve/lodepng>
  - <https://github.com/lvandeve/lodepng/commits>
  - <https://github.com/lvandeve/lodepng/issues>
  - <https://github.com/lvandeve/lodepng/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/lvandeve/lodepng/issues/232>
  - <https://github.com/lvandeve/lodepng/issues/179>
  - <https://github.com/lvandeve/lodepng/issues/227>
  - <https://github.com/lvandeve/lodepng/commit/e584a84>
  - <https://raw.githubusercontent.com/lvandeve/lodepng/HEAD/README.md>
  - <https://raw.githubusercontent.com/lvandeve/lodepng/HEAD/lodepng.h>
  - <https://raw.githubusercontent.com/lvandeve/lodepng/HEAD/lodepng.cpp>
  - <https://raw.githubusercontent.com/lvandeve/lodepng/HEAD/lodepng_benchmark.cpp>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/test/c/mimiclib/png.c>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/test/c/std/png.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/lvandeve/lodepng`) · [data/wave10/enrich/raw/github_com_lvandeve_lodepng.json](../../../data/wave10/enrich/raw/github_com_lvandeve_lodepng.json) (enrichment confidence 0.85)

</details>
