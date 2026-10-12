# Efficient Compression Tool (ECT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Command-line PNG/JPEG/gzip/ZIP optimizer whose modified-zopfli deflate matches zopfli -i30 output size about 15x faster.

| | |
|---|---|
| **Beats** | zopfli (and gzip -9); the published benchmark is gzip/deflate on enwik8, not PNG |
| **Claimed result** | On enwik8 (100,000,000 bytes) compressed to gzip format, ECT v0.9.2: ECT -3 35,014,543 bytes in 16.2 s vs zopfli -i15 34,966,078 bytes in 3m 59.9s (14.8x faster at 0.14% larger, derived from page data); ECT -2 35,019,440 bytes in 14.8 s vs zopfli -i5 34,983,757 bytes in 2m 12.0s (8.9x faster at 0.10% larger, derived from page data); ECT -5 34,942,796 bytes in 25.1 s vs zopfli -i30 34,961,453 bytes in 6m 30.6s (smaller and 15.6x faster, derived from page data); ECT -9 34,937,781 bytes in 3m 17.9s vs zopfli -i30 (smaller and 2.0x faster, derived from page data); ECT -1 36,493,257 bytes in 3.5 s vs gzip -9 36,475,811 bytes in 5.8 s (1.66x faster at 0.05% larger, derived from page data). The repo publishes no PNG or JPEG numbers. |
| **Workload** | Compressing enwik8 (100,000,000 bytes) into gzip format at ECT levels 1-9 versus gzip -9 and zopfli with 1, 5, 15 and 30 iterations. |
| **Metric** | throughput |
| **Hardware** | Intel i7-7700HQ |
| **Compiler and flags** | clang on macOS 12.5 (version and flags not stated); command lines not given. ECT defaults to single-threaded deflate (--mt-deflate is opt-in in src/main.cpp), so the ECT runs were probably single-threaded like zopfli, but the README does not say. |
| **Adoption** | 746 stars |
| **Last commit** | 2026-08-30 |
| **Links** | [repository](https://github.com/fhanau/Efficient-Compression-Tool) · [benchmark](https://github.com/fhanau/Efficient-Compression-Tool) |

## Verdict

One first-party run of ECT v0.9.2 on macOS 12.5, Intel i7-7700HQ, clang (version and flags not stated; zopfli and GNU gzip versions not stated): enwik8 compressed to gzip, ECT -5 gives 34,942,796 bytes in 25.1 s versus zopfli -i30 34,961,453 bytes in 6m 30.6s (smaller and about 15.6x faster, derived from page data), and ECT -1 (bundled zlib level 9) 36,493,257 bytes in 3.5 s versus gzip -9 36,475,811 bytes in 5.8 s. Both tools appear single-threaded by default, but ECT splits input into 5 MB independent master blocks (1 MB at levels 2-3) while upstream zopfli uses 1 MB, so the two are not tuned identically; no script or command lines are published.

## Use it when

- Precompressing static web assets (.gz for gzip_static, ZIP downloads) where every byte counts and zopfli is too slow: ECT -5 beat zopfli -i30 on size in 25.1 s versus 6m 30.6s on enwik8 in the author's run.
- Build or CI steps that already run zopfli or zopflipng and can trade a CLI swap for a large time cut at equal or smaller output.
- Batch optimization of mixed PNG, JPEG, gzip and ZIP trees in one tool (folders, -recurse, --mt-file).
- Shrinking existing .gz files in place: ECT re-deflates them and keeps the result only if it is smaller.

## Skip it when

- Online or per-request compression: even -2 ran at about 6.8 MB/s on enwik8 (14.8 s for 100 MB); use zlib-ng, libdeflate or ISA-L for throughput.
- Embedding as a library: there is no public API, the encoder reads up to 8 bytes past the input (a source TODO says callers must over-allocate), and level 1 depends on the bundled zlib fork.
- Inputs of 1,200,000,000 bytes or more: fileHandler prints 'File too big' and skips them; empty files are refused in gzip mode, and ZIP mode skips files over 4 GiB.
- Expecting multicore scaling: open issue #134 (Oct 2023) reports --mt-deflate=16 --mt-file=16 keeping only two of 16 threads busy, and --mt-deflate disables cost-model reuse, so output differs from the single-threaded result.
- Builds with GCC 15 at -O3: open issue #145 (Aug 2025) reports a segfault in Bt3Zip_MatchFinder_GetMatches2 on PNG files at level 2 and above (not seen with GCC 14, Clang 20 or GCC 15 -O2); the match finder relies on unaligned type-punned loads.

## How it is fast

Levels 2-9 run a heavily modified zopfli: the hash-chain longest-match search is replaced by a 7-Zip LzFind-derived binary-tree match finder (Bt3Zip) with an RLE fast path, plus an LZ4HC-style hash chain hashed with the SSE4.2/ARMv8 CRC32C instruction; match results are cached across iterations, the optimal-parsing cost model is reused between blocks, and the iteration count is cut to 1-60 by level (zopfli defaults to 15) with entropy-based block splitting at level 2. Level 1 does not use that engine at all: in gzip mode it calls the bundled zlib at level 9, a fork carrying Cloudflare zlib changes, Chromium's SIMD CRC-32/Adler-32 and gildor2/fast_zlib's longest_match with a CRC32C hash.

## Compared with alternatives

Pick ECT when the goal is the smallest possible standard deflate/gzip/ZIP output and compression time is offline: zlib, zlib-ng, libdeflate and the Cloudflare or fast_zlib forks are far faster but larger, while ECT reaches zopfli-class size an order of magnitude faster. For the speed of its -1 mode alone, the catalogued fast_zlib, Cloudflare zlib or Chromium zlib entries supply the same patches as a linkable library.

## Integration

| | |
|---|---|
| **Form** | CLI executable built with CMake (no installed library or stable API; the deflate engine can be vendored as source) |
| **Dependencies** | git submodules libpng and mozjpeg (recursive clone required), nasm for mozjpeg SIMD; zopfli, zlib fork, LzFind, lodepng, optipng, miniz and Leanify are vendored |
| **Minimum toolchain** | C++17 (std::filesystem), CMake 3.10+; GCC, Clang, AppleClang or MSVC |
| **Platforms** | x86-64 (CMake adds -msse4.2 -mpclmul unconditionally, so binaries need SSE4.2 and PCLMULQDQ) and arm64 (-march=armv8-a+crc); 32-bit x86 is described as no longer officially supported; Windows builds have needed repeated fixes (Aug 2026 commits) |
| **Thread safety** | Not a library; the CLI offers per-file (--mt-file) and per-block (--mt-deflate) threads, and the deflate engine keeps match-finder state in thread_local globals. |
| **Drop-in for the baseline** | partial: same deflate/gzip/ZIP output formats as zopfli and gzip, but different command-line options (levels -1 to -9 instead of --i&lt;N&gt;) and no zopfli-compatible library API |

## Gotchas

- ECT -1 is not the zopfli-derived engine: in gzip mode it is the bundled zlib at level 9 (deflateInit2 level 9, memLevel 8), so the README's 'ECT -1 vs gzip -9' row measures a patched zlib against GNU gzip.
- Numeric levels of 10 or more are parsed as an iteration count with level-9 settings, and values of 10000 or more turn on repeated block splitting (ZopfliInitOptions in src/zopfli/util.c); this is undocumented in -help.
- Releases lag master: the last tagged release is 0.9.5 (Jan 2024), which fixed an infinite loop on long byte runs present since 0.9.2 (issue #125); master's CMake says 0.9.6 while -help still prints 0.9.5.
- The gzip header and trailer (MTIME, CRC-32, ISIZE) are written with host-endian unaligned stores in zopfli_gzip.cpp, so big-endian builds would write wrong trailers (source reading; not reported as an issue).

## Known shortcomings

- The only numbers are gzip output on enwik8 (ECT -5 25.1 s vs zopfli -i30 390.6 s, smaller output, 15.6x derived; also vs gzip -9; i7-7700HQ, clang, no flags), so this belongs with general-lossless compressors rather than image codecs; no PNG numbers anywhere in the repo (the css-ig.net PNG benchmark is blocked here).
- The 'ECT -1 vs gzip -9 1.66x' row measures ECT's bundled zlib fork at level 9 (Cloudflare patches, Chromium SIMD, fast_zlib longest_match, CRC32C hash) against GNU gzip, not the zopfli engine, so it overlaps the catalogued fast_zlib, Chromium zlib and Cloudflare zlib entries; the ECT -5 versus zopfli -i30 row stands, with ECT using 5 MB master blocks (1 MB at levels 2-3) against upstream zopfli's 1 MB. The benchmark is from v0.9.2, which had the infinite-loop bug #125 (fixed 0.9.5). No library API; the encoder over-reads 8 bytes past its input; files of 1,200,000,000 bytes or more are rejected; the x86 build forces -msse4.2 -mpclmul; open #145 (segfault with GCC 15 -O3) and #134 (2 of 16 threads busy); the gzip trailer is written host-endian.

## Caveats and trade-offs

The only published benchmark is deflate (gzip) output on enwik8 text; there are no PNG or JPEG timings in the repo, so the record's numbers support general lossless compression (ECT gzip vs zopfli and gzip -9), not image codecs. ECT's deflate is built on a modified zopfli, so zopfli is the apt incumbent for maximum-compression deflate. Single run, old version (v0.9.2), no benchmark script, flags or command lines. ECT bundles modified copies of zopfli/zopflipng, mozjpeg, zlib, libpng, optipng, pngcrush, brotli, lodepng and Leanify under their own permissive licenses. An independent PNG optimizer benchmark that includes ECT exists at css-ig.net (benchmark/png-lossless), but it is blocked here and was not used.

Optimizer for PNG, JPEG (bundles mozjpeg), GZIP and ZIP files; needs nasm and a recursive clone. Multithreading can be turned off at CMake time.

## Maintenance

Actively maintained by one author (last commit 2026-08-30, dependency and zlib 1.3.2 backports), Apache-2.0 with bundled permissive third-party licenses; the published benchmark is from v0.9.2 and predates the 0.9.4 match-search speedups, so current builds may differ.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Performance (v0.9.2)' table times ECT -1 to -9 against gzip -9 and zopfli -i1/-i5/-i15/-i30 on enwik8 compressed to gzip format, stating macOS 12.5, Intel i7-7700HQ and clang but no compiler version, flags or command lines, and no benchmark script is in the repo. A single first-party run, so C.
- **Verifier notes:** Category: the record's numbers compare ECT gzip vs zopfli and gzip -9, not ECT PNG optimisation vs OptiPNG/zopflipng, so file it under general-lossless (id kept unchanged). The rows were checked against the README table and the ratios recomputed; ECT -5 is added as the clearest smaller-and-faster comparison against zopfli -i30. A PNG-category entry would need the css-ig.net benchmark or similar from an environment that can reach it.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fhanau/Efficient-Compression-Tool>
  - <https://github.com/fhanau/Efficient-Compression-Tool/commits>
  - <https://github.com/fhanau/Efficient-Compression-Tool/tree/master/doc>
  - <https://github.com/fhanau/Efficient-Compression-Tool/tree/master/licenses>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/README.md>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/licenses/Licenses.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/README.md>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/licenses/Licenses.txt>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/main.h>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/gztools.cpp>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/support.h>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/LzFind.c>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/LzFind.h>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zopfli/zopfli_gzip.cpp>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zopfli/deflate.cpp>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zopfli/squeeze.c>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zopfli/lz77.c>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zopfli/blocksplitter.c>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zopfli/util.c>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zopfli/util.h>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zopfli/zopfli.h>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zopfli/match.h>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zopfli/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zlib/deflate.c>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zlib/crc32_simd.c>
  - <https://raw.githubusercontent.com/fhanau/Efficient-Compression-Tool/HEAD/src/zlib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/google/zopfli/HEAD/src/zopfli/util.h>
  - <https://github.com/fhanau/Efficient-Compression-Tool/tree/master/src/zopfli>
  - <https://github.com/fhanau/Efficient-Compression-Tool/commits/master>
  - <https://github.com/fhanau/Efficient-Compression-Tool/releases>
  - <https://github.com/fhanau/Efficient-Compression-Tool/issues>
  - <https://github.com/fhanau/Efficient-Compression-Tool/issues?q=is%3Aissue+corrupt>
  - <https://github.com/fhanau/Efficient-Compression-Tool/issues/134>
  - <https://github.com/fhanau/Efficient-Compression-Tool/issues/141>
  - <https://github.com/fhanau/Efficient-Compression-Tool/issues/145>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/fhanau/efficient-compression-tool`) · [data/wave10/enrich/raw/github_com_fhanau_efficient_compression_tool.json](../../../data/wave10/enrich/raw/github_com_fhanau_efficient_compression_tool.json) (enrichment confidence 0.75)

</details>
