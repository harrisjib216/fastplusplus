# libbsc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Block-sorting (BWT/ST + LZP + QLFC) compressor library that reaches xz -5 ratios with 5x faster single-thread compression.

| | |
|---|---|
| **Beats** | xz (xz 5.8.4); also bzip2 1.0.8 |
| **Claimed result** | lzbench 2.4: bsc 3.3.12 -m0 -e1 compresses at 19.4 MB/s with ratio 23.26; xz 5.8.4 -5 compresses at 3.84 MB/s with ratio 23.70 (5.1x faster compression and a smaller output, derived from page data); bzip2 1.0.8 -9 does 12.7 MB/s with ratio 25.75 (1.5x, derived). Decompression is slower: 25.0 MB/s versus xz 121 MB/s. |
| **Workload** | Silesia tar single-thread compression and decompression through lzbench; block-sorting compressor versus xz and bzip2. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04; silesia.tar (211,947,520 bytes) |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 352 stars |
| **Last commit** | 2026-02-03 |
| **Links** | [repository](https://github.com/IlyaGrebnov/libbsc) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

lzbench 2.4 (gcc 15.2.0 release binary, one thread of an AMD EPYC 9555P at 3.2 GHz with turbo off, silesia.tar) shows bsc 3.3.12 -m0 -e1 at 19.4 MB/s compress and 25.0 MB/s decompress to 23.26% of input, versus xz 5.8.4 -5 at 3.84 / 121 MB/s to 23.70% (5.1x faster compression, 4.8x slower decompression, derived from page data) and bzip2 1.0.8 -9 at 12.7 / 35.5 MB/s to 25.75%. lzbench's wrapper drops LIBBSC_FEATURE_MULTITHREADING when run with one thread, and libbsc then calls libsais with one thread, so the numbers are single-core even in an OpenMP build.

## Use it when

- Archival or backup of text-like, log or source data where you want xz-class ratio but cannot afford xz -5..-9 compression time: bsc -m0 -e1 compresses silesia at 19.4 MB/s to 23.26% versus xz -5 at 3.84 MB/s to 23.70%.
- Write-once, read-rarely data where compression and decompression times are both acceptable at about 20-25 MB/s per core.
- Machines with many cores or an NVIDIA GPU: OpenMP processes blocks in parallel and the CUDA build offloads forward/inverse BWT and ST.
- In-memory block compression of large buffers (megabytes to 2 GB per block) where a self-checking format matters: headers, payload and original data each carry an Adler-32.

## Skip it when

- Read-heavy data: decompression is 25.0 MB/s for -m0 -e1 and 14.7-15.8 MB/s for the ST modes, versus xz at about 121 MB/s and zstd/LZ4 at hundreds to thousands of MB/s.
- Small messages or random access: BWT needs whole blocks and the format has no seeking within a block; the default 25 MB CLI block is where the ratio comes from.
- Memory-constrained systems: compression and decompression both need about 16 MB + 5 x block size x parallel blocks (the GPU paths 7-21 x block size).
- When interoperability matters: the .bsc format is read only by bsc/libbsc; use xz or zstd for files other tools must open.
- 32-bit ARM: lzbench disables bsc there because its multithreaded decompress path faults (SIGBUS, lzbench#293).

## How it is fast

Each block optionally passes through LZP (Lempel-Ziv prediction, default 2^15 hash, minimum match 72) to strip long repeats, then a Burrows-Wheeler Transform built with libsais (a fast SA-IS suffix-array construction by the same author) or a Sort Transform of order 3-8, then QLFC (Quantized Local Frequency Coding) with static, adaptive or fast models. Compression cost is dominated by the linear-time suffix sort rather than LZMA's optimal-parse match search, which is why it compresses several times faster than xz at a similar ratio. SIMD paths exist for MTF, QLFC (AVX-512) and Adler-32 (SSSE3/AVX2) with runtime CPU dispatch, and optional OpenMP and CUDA (compute capability 7.5+) paths parallelise blocks, the BWT and the ST.

## Compared with alternatives

Pick libbsc over bzip3 when compression speed matters (19.4 versus 11.9 MB/s and 25.0 versus 12.4 MB/s decode in lzbench 2.4) and a 1-point worse ratio is fine, and over xz when compression time dominates and decompression at 25 MB/s is acceptable; Kanzi -6 gives a similar ratio (23.36%) with faster decode (31.2 MB/s) but slower compression (15.0 MB/s).

## Integration

| | |
|---|---|
| **Form** | static lib (default) or shared lib via CMake -DBSC_BUILD_SHARED_LIB=ON; sources are also easy to vendor (lzbench compiles the libbsc/ tree directly) |
| **Dependencies** | none required (libsais is vendored); optional OpenMP for multithreading and CUDA Toolkit for GPU acceleration |
| **Minimum toolchain** | C++17, CMake 3.24; CUDA compute capability 7.5+ for the GPU path |
| **Platforms** | x86-64 (runtime dispatch to SSE2/AVX/AVX2/AVX-512) and AArch64 (optimised since 3.2.4); Windows, Linux, macOS; 32-bit ARM multithreaded decompress reported to fault |
| **Thread safety** | not documented; bsc_init sets process-wide state (allocator hooks and coder/BWT tables) and must run first; internal parallelism is controlled by LIBBSC_FEATURE_MULTITHREADING plus OpenMP |
| **Drop-in for the baseline** | no |

## Gotchas

- The CMake build defaults to BSC_ENABLE_NATIVE_COMPILATION=ON (-march=native), so binaries built on a newer CPU can SIGILL elsewhere; turn it off for distributable builds.
- LIBBSC_DEFAULT_FEATURES includes MULTITHREADING; pass LIBBSC_FEATURE_FASTMODE alone for single-threaded behaviour (lzbench does this at one thread, so its numbers are single-core).
- Sizes are int: one call handles at most about 2 GB, and bsc_compress can return LIBBSC_NOT_COMPRESSIBLE, in which case the caller should fall back to bsc_store.
- Upgrade past old versions: 3.2.3 fixed LibFuzzer-found out-of-bounds and corruption bugs, 3.2.5 fixed LZP encoder data corruption ('upgrade strongly recommended'), and 3.3.3 fixed out-of-bounds access on large inputs.

## Known shortcomings

- Tier B on lzbench 2.4 (19.4 vs xz -5 3.84 MB/s at a better ratio); the lzbench Makefile builds bsc with OpenMP when available, so a single-thread run is not certain.
- CMake defaults to -march=native. Decompression 25.0 MB/s vs xz 121 MB/s in lzbench 2.4. Memory about 16 MB plus 5x block size. Earlier corruption and out-of-bounds fixes shipped in 3.2.3, 3.2.5 and 3.3.3.

## Caveats and trade-offs

Decompression is much slower than xz in the same table (25.0 MB/s versus about 121 MB/s). The libbsc README has no benchmark numbers, so all evidence comes from the lzbench table. lzbench notes bsc multithreaded decompress faults on 32-bit ARM. The lzbench Makefile compiles bsc with OpenMP multithreading when OpenMP is found, and the results page does not say whether the release binary used it, so the single-thread claim for bsc is not certain.

Compression-side win only; decompression is 5x slower than xz and 50-80x slower than zlib. Optional NVIDIA GPU acceleration. Memory heavy block sorting.

## Maintenance

Active: releases 3.3.5 to 3.3.12 shipped through 2025 (latest 3.3.12, September 2025; last commit 2026-02-03, a build-warning fix), Apache-2.0, 352 stars, single primary author who also maintains libsais; the GitHub issue tracker shows no issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The independent lzbench 2.4 suite (public code, gcc 15.2.0 release binary, single thread of an AMD EPYC 9555P, silesia.tar) lists bsc 3.3.12 -m0 -e1 at 19.4 / 25.0 MB/s, 23.26% vs xz 5.8.4 -5 at 3.84 / 121 MB/s, 23.70% and xz -9 at 2.75 / 122 MB/s, 23.01%; all quoted rows match. Release-binary build details (notably OpenMP) are not on the results page, so B.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** Numbers verified; Apache-2.0, 352 stars, last commit 2026-02-03 (active). Added the OpenMP build caveat from the lzbench Makefile.
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier; lzbench 2.4 numbers are single-core: bench/symmetric_codecs.cpp passes FASTMODE only at 1 thread and bwt.cpp then calls libsais with 1 thread
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://github.com/IlyaGrebnov/libbsc>
  - <https://github.com/IlyaGrebnov/libbsc/commits>
- **Sources the enricher read:**
  - <https://github.com/IlyaGrebnov/libbsc>
  - <https://github.com/IlyaGrebnov/libbsc/commits>
  - <https://github.com/IlyaGrebnov/libbsc/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/IlyaGrebnov/libbsc/HEAD/README>
  - <https://raw.githubusercontent.com/IlyaGrebnov/libbsc/HEAD/CHANGES>
  - <https://raw.githubusercontent.com/IlyaGrebnov/libbsc/HEAD/VERSION>
  - <https://raw.githubusercontent.com/IlyaGrebnov/libbsc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/IlyaGrebnov/libbsc/HEAD/bsc.cpp>
  - <https://raw.githubusercontent.com/IlyaGrebnov/libbsc/HEAD/libbsc/libbsc.h>
  - <https://raw.githubusercontent.com/IlyaGrebnov/libbsc/HEAD/libbsc/libbsc/libbsc.cpp>
  - <https://raw.githubusercontent.com/IlyaGrebnov/libbsc/HEAD/libbsc/bwt/bwt.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/bsc.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/symmetric_codecs.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lzbench.h>
  - <https://github.com/inikep/lzbench>
  - <https://github.com/inikep/lzbench/tree/master/bench>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ilyagrebnov/libbsc`) · [data/wave9/enrich/raw/github_com_ilyagrebnov_libbsc.json](../../../data/wave9/enrich/raw/github_com_ilyagrebnov_libbsc.json) (enrichment confidence 0.85)

</details>
