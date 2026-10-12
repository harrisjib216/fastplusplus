# ptpng

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `None stated: no LICENSE file (raw LICENSE, LICENSE.md, LICENSE.txt and COPYING all return 404), the GitHub page shows no license, and README.md, include/ptpng.h and CMakeLists.txt give no terms` · 🟢 active

> Unlicensed C11 PNG decoder and encoder with AVX2/NEON kernels; decodes 1.5-1.8x faster than libpng with zlib-ng on synthetic images.

| | |
|---|---|
| **Beats** | Decoder: libpng 1.6 (vendored libpng16 branch) with zlib-ng 2.2.4 in ZLIB_COMPAT mode. Encoder: libpng with the vendored stock zlib (develop branch) at level 6 and libpng with zlib-ng 2.2.4 at level 6, both with PNG_ALL_FILTERS adaptive filtering. |
| **Claimed result** | README: decoder geometric-mean speedup over libpng + zlib-ng 2.2.4 across 27 cases is 1.80x Linux x64 (27/27 faster), 1.64x Windows x64 (26/27), 1.59x Linux ARM64 (27/27), 1.62x macOS ARM64 (27/27) and 1.46x Windows ARM64 (26/27) in the 30 Sep 2026 nightly run 36753946386. Encoder (1 Oct change, nightly run 36791257328 per PERFORMANCE.md) averages 2.25-2.98x stock zlib level 6 and 1.14-1.52x zlib-ng level 6 across five platforms, faster than zlib-ng in only 4-6 of the 9 fixtures per platform, with PNGs at most 2.4% larger than zlib-ng level 6. |
| **Workload** | PNG decode (27 cases: nine fixtures in native, RGB8 and RGBA8 output, median of 12 alternating rounds) and PNG encode (nine generated fixtures, median of five rotated rounds with a round-trip check) on five GitHub-hosted CI platforms. Fixtures are generated gradients, graphics and random noise at 3200x2400, except the two RGBA16 fixtures and noise_rgba8, which are 1024x768. |
| **Metric** | throughput |
| **Hardware** | GitHub-hosted runners logged in gh-pages bench/data.js. 30 Sep decoder run 36753946386: Linux x64 and Windows x64 AMD EPYC 7763 (4 logical CPUs), Linux ARM64 Neoverse-N2, Windows ARM64 Cobalt 100, macOS Apple M1 (Virtual). Encoder run 36791257328: same, except Windows x64 was AMD EPYC 9V45. Local runs used an Intel Core i7-1355U. |
| **Compiler and flags** | CMake Release build with no explicit -O level in CMakeLists.txt (CMake's defaults, -O3 -DNDEBUG for gcc/clang and /O2 for MSVC), plus per-file -mavx2 or /arch:AVX2 and -mpclmul -msse2 kernels. The nightly matrix uses gcc (ubuntu24 x64 and arm64 images), clang (macos-14) and MSVC cl (win25-vs2026, win11-vs2026-arm64); compiler versions are not stated. PERFORMANCE.md quotes -O3 for paired runs and MSVC /O2 /Ob2 for local runs. |
| **Adoption** | 0 stars; 0 forks; 43 commits |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/bojosos/ptpng) · [benchmark](https://raw.githubusercontent.com/bojosos/ptpng/HEAD/README.md) |

## Verdict

The author's nightly CI on GitHub-hosted runners (EPYC 7763, Neoverse-N2, Cobalt 100, virtual Apple M1; compiler versions not stated, CMake Release defaults) times ptpng against libpng16 built in the same tree with zlib-ng 2.2.4 (and with stock zlib). Both sides decode from memory with CRC and Adler-32 checks on, and the result is the median of 12 alternating rounds: geometric means of 1.46x-1.80x over 27 cases on 30 September 2026. Encoding against libpng at level 6 with all filters gave 2.25x-2.98x versus stock zlib and 1.14x-1.52x versus zlib-ng, with files at most 2.4% larger. Recomputed from gh-pages bench/data.js, the per-platform encoder means match PERFORMANCE.md exactly. On the same commit, the 3 October run gave 1.37x (Windows x64, now an Intel Xeon Platinum 8573C) to 1.79x for decoding and 1.09x-1.49x versus zlib-ng for encoding. The harness looked fair and no correctness bug was found. Caveats: the fixtures are Python-generated gradients plus small noise, flat rectangles and random bytes, written by an unpinned Pillow on each runner, so the compressed inputs differ by OS (PERFORMANCE.md notes stored versus fixed-Huffman noise streams). The libpng encoder also writes through a realloc-doubling memory callback, a small cost charged to the reference.

## Use it when

- Studying or benchmarking a modern single-threaded PNG decode path: the code is compact (one inflate file, one decoder file, per-ISA kernel files), heavily commented, and tested against libpng. Without a licence it is reference material only.
- Single-threaded decoding of large PNGs on x86-64 with AVX2 or on ARM64, where checksum verification must stay on and the baseline is libpng: 1.46x-1.80x geometric mean across 27 cases in the 30 September nightly.
- Palette, flat-graphics and 16-bit RGBA images show the largest decode gains (graphic_pal8 3.46x, graphic_rgba16_paeth 4.50x native output in the 30 September Windows x64 snapshot); noisy images gain little (noise_rgba8 1.02x).
- Encoding 8- or 16-bit gray/RGB/RGBA to roughly zlib level-6 sizes faster than libpng with stock zlib (2.25x-2.98x across platforms), especially graphics, where it beat libpng with zlib-ng level 6 by 1.85x-2.51x in the local i7-1355U table.

## Skip it when

- Anything you ship: the repository has no LICENSE file and no licence terms, so you have no right to copy or vendor it. The x86 CRC code is also derived from zlib-ng.
- Multithreaded image pipelines: every call must be serialized process-wide. Building each Huffman table writes a file-static scratch array (sym_code in ptpng_inflate.c), and CPU dispatch and fixed-Huffman tables are initialised lazily with no synchronisation. Two concurrent decodes can therefore corrupt each other's tables, not just race at start-up.
- Photo-like RGB encoding, or ARM64 encoding against zlib-ng: libpng with zlib-ng level 6 was faster on photo_rgb8 on all five platforms in the 3 October nightly (ptpng at 0.67x-0.93x). On Linux ARM64 ptpng won only 3 of 9 fixtures there (1.09x geometric mean).
- Workflows needing palette, 1/2/4-bit or interlaced output, ICC/gamma/text chunks on write, a compression-level knob, streaming input or progressive display.
- Risk-averse projects: the repository is ten days old (first commit 2026-09-24), has a single author and 0 stars, and is benchmarked only on generated images. Its nightly ratios move with the runner CPU: on the same commit (9a1dadf), the Windows x64 decode geometric mean was 1.69x, 1.56x and 1.37x in the 1, 2 and 3 October nightlies.

## How it is fast

The inflater uses a 64-bit bit buffer refilled a word at a time to keep 48-64 bits available, Huffman tables built from pre-reversed codes so each symbol is one masked table lookup, flat root tables (10-bit literal/length, 8-bit distance) whose entries carry precomputed bases and extra-bit counts, a fast path that decodes up to four literals per refill, and 32- or 64-byte block copies for matches. It inflates straight into the final image buffer because the PNG header fixes the output size. Unfiltering and output conversion use runtime-dispatched AVX2/SSE2 or NEON kernels (prefix-sum Sub, SIMD Paeth for 4-byte pixels). Checksums run on hardware: PCLMUL folding for CRC-32 (derived from zlib-ng), ARMv8 CRC instructions, and AVX2 or NEON Adler-32. The encoder scores every byte of each row for adaptive filtering with SIMD and uses a bounded hash-chain matcher with lazy lookahead. It picks stored, fixed or dynamic DEFLATE blocks by bit cost and writes up to six literals per 64-bit store.

## Compared with alternatives

Use ptpng only as a reference for technique, because it has no licence. For a licensed in-memory libpng alternative take libspng (a few percent over libpng in Wuffs' numbers) or the Rust png crate (1.5-1.8x over libpng in Wuffs' 2022 runs). For encode-only speed take fpnge or fpng, which are far faster than libpng but give up compression ratio, whereas ptpng targets zlib level-6 sizes.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target ptpng::ptpng via add_subdirectory) plus a header-only C++ wrapper |
| **Dependencies** | none at runtime; the default build also configures vendored libpng16, zlib (develop) and zlib-ng 2.2.4 for parity tests and benchmarks (turn off with -DPTPNG_WITH_LIBPNG=OFF); the benchmark fixtures need Python with Pillow |
| **Minimum toolchain** | C11 compiler and CMake 3.15+; C++17 for ptpng.hpp (C++20 for the std::span overloads); compilers accepting -mavx2/-mpclmul or MSVC /arch:AVX2 for the x86 kernels |
| **Platforms** | x86-64 (runtime-dispatched AVX2, SSE2, PCLMUL with scalar fallbacks) and AArch64 (NEON, CRC instructions); CI covers Linux x64/ARM64, macOS ARM64 and Windows x64/ARM64 |
| **Thread safety** | Not thread-safe: the README and ptpng.h require all decode and encode calls to be serialized across threads; inflate uses a shared static scratch array and lazily built shared dispatch and fixed tables. |
| **Drop-in for the baseline** | no |

## Gotchas

- Passing NULL encoder options selects adaptive filtering, but a zero-initialised ptpng_encode_opts selects the None filter (filter 0), which gives much larger files.
- RGB8/RGBA8 output keeps the high byte of 16-bit samples (like libpng's png_set_strip_16, not png_set_scale_16 rounding), and RGB8 ignores tRNS.
- The encoder writes pixels only. Metadata such as ICC, gamma and text is dropped, and palette or sub-byte images must be decoded to RGB8/RGBA8 before re-encoding, so they come back larger than the source.
- Each encode allocates about 896 KiB of compression state on top of the image buffers (PERFORMANCE.md).

## Known shortcomings

- No licence (LICENSE, LICENSE.md, LICENSE.txt and COPYING absent, no terms in README or header): reference only. Benchmark code is public (tools/bench_compare.c, tools/bench_encode.c; runner CPUs logged in gh-pages bench/data.js) but compiler versions are never stated, so C. Encoder subset only (no palette, packed-sample, interlace or metadata output); files up to 2.4% larger than zlib-ng level 6, and zlib-ng is faster on 3-5 of 9 fixtures per platform; calls are not thread-safe.
- Not thread-safe beyond init: a file-static sym_code scratch buffer is written by every Huffman table build, so concurrent calls can corrupt tables. Benchmark fixtures are generated per CI runner by an unpinned Pillow, so inputs differ by OS; the libpng encode reference uses a realloc-doubling buffer (a minor cost charged to libpng). The 3 October nightly (run 37111068455, commit 9a1dadf) gives decode 1.37x (Windows x64, Xeon Platinum 8573C) to 1.79x and encode 1.09-1.49x against zlib-ng, with photo_rgb8 encode slower than zlib-ng on all 5 platforms (0.67-0.93x). No licence; repository recently renamed; open PR #1.

## Caveats and trade-offs

No license file or license terms, so the code is reference only. Very new repository (0 stars; commits from 2026-09-24 to 2026-09-30); numbers change nightly and the README says to compare ratios only within a run because hosted runner CPUs change. Fixtures are synthetic (gradients, graphics, noise) and the project says they do not establish a fastest-in-the-world claim. Decoder loses on noise-to-RGB8 on both Windows platforms. PNG encoder trade-offs: it only writes non-interlaced gray, gray+alpha, RGB and RGBA at 8 or 16 bits (no palette, packed-sample or metadata output, so palette images expand to RGBA8); its files are up to 2.4% larger than zlib-ng level 6; and zlib-ng level 6 is faster on 3-5 of the 9 fixtures per platform (for example 0.76x on photo_rgb8 in the local i7-1355U table). Library calls must be serialized across threads because internal tables and dispatch state are shared. Compiler versions are not stated.

No LICENSE file found at the repo root (raw.githubusercontent.com returned 404 for LICENSE, LICENSE.md and LICENSE.txt) and the README has no license section, so reuse rights are unclear. Single-threaded; library calls must be serialized across threads (shared tables and dispatch state). Encoder writes non-interlaced PNG without palette, packed-sample or metadata support. C11 core with a header-only C++17/20 wrapper; AVX2/SSE2 on x86 and NEON on ARM64.

## Maintenance

Actively developed by one author (43 commits between 2026-09-24 and 2026-09-30, open PR #1 from 3 October, nightly benchmarks still publishing), but with no licence it is reference-only, and the repository was recently renamed, so links may move.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README and PERFORMANCE.md numbers match the record and come from public benchmark code (tools/bench_compare.c, tools/bench_encode.c, .github/workflows/nightly.yml) run on GitHub-hosted runners whose CPU models are logged in gh-pages bench/data.js. Compiler versions are never stated (only gcc/clang/MSVC cl on the runner images) and the optimisation flags are only CMake's implicit Release defaults, so it stays first-party C, just short of A.
- **Verifier notes:** No LICENSE confirmed on github.com and in raw paths; usability stays reference. The benchmarks look fair: the reference encoders use PNG_ALL_FILTERS at the same level, every encode round-trips and is compared by memcmp, and CI checks byte parity with libpng; no correctness bug was found behind the published numbers. A compiler-version statement would make this tier A.
- **Fields the verifier corrected:** `license`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/README.md>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/PERFORMANCE.md>
  - <https://github.com/bojosos/ptpng>
  - <https://github.com/bojosos/ptpng/commits>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/COPYING>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/.github/workflows/nightly.yml>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/.github/workflows/compare.yml>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/tools/bench_metadata.py>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/tools/bench_compare.c>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/tools/bench_encode.c>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/include/ptpng.h>
  - <https://raw.githubusercontent.com/bojosos/ptpng/gh-pages/bench/data.js>
- **Sources the enricher read:**
  - <https://github.com/bojosos/ptpng>
  - <https://github.com/bojosos/ptpng/commits>
  - <https://github.com/bojosos/ptpng/pulls>
  - <https://github.com/bojosos/ptpng/tree/HEAD/src>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/README.md>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/include/ptpng.h>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/include/ptpng.hpp>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/src/ptpng.c>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/src/ptpng_inflate.c>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/src/ptpng_deflate.c>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/tools/bench_compare.c>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/tools/bench_encode.c>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/tools/bench_metadata.py>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/tests/gen_bench.py>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/tests/gen_bench16.py>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/.github/workflows/nightly.yml>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/.github/workflows/compare.yml>
  - <https://raw.githubusercontent.com/bojosos/ptpng/gh-pages/bench/data.js>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/COPYING>
  - <https://raw.githubusercontent.com/bojosos/ptpng/HEAD/UNLICENSE>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/bojosos/ptpng`) · [data/wave10/enrich/raw/github_com_bojosos_ptpng.json](../../../data/wave10/enrich/raw/github_com_bojosos_ptpng.json) (enrichment confidence 0.8)

</details>
