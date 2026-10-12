# Stenos

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C/C++ compressor for arrays of fixed-size numeric elements that picks its own filter; claims better ratio and speed than Blosc2+Zstd.

| | |
|---|---|
| **Beats** | Blosc2 byte shuffle + Zstd and Blosc2 bitshuffle + Zstd |
| **Claimed result** | README: Stenos 'usually compress better and faster than Blosc + Zstd or lz4'; the SIMD block algorithm 'can compress at more or less 2GB/s and decompress at 3GB/s'. docs/benchmarks.svg plots ratio against speed for 10 files from stenos_dataset (e.g. 16_2048_sq_float4.bin, 2_WA.txt, 8_SHYBPTOT.txt) comparing Stenos only with Zstd+Byteshuffle and Zstd+bitshuffle; no LZ4 curve and no numeric values in text. |
| **Workload** | Compress structured binary arrays (integers, floats) from the stenos_dataset; plots compression ratio versus speed against Blosc with byte or bit shuffle plus Zstd, single thread. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-10850H @ 2.70GHz (AVX2), single-threaded |
| **Adoption** | 18 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/Thermadiag/stenos) · [benchmark](https://github.com/Thermadiag/stenos) |

## Verdict

The author's own benchmark (benchs/bench_to_csv.cpp, single thread, Intel Core i7-10850H with AVX2, compiler and flags unstated) times compression only at levels 1-9 against Blosc2 byte shuffle + Zstd and Blosc2 bitshuffle + Zstd on 10 to 12 files from the stenos_dataset repo, and docs/benchmarks.svg plots ratio against compression speed with no numeric table. The README's '2GB/s compress, 3GB/s decompress' for the block codec and its 'or lz4' comparison are not backed by published numbers; the Blosc2+LZ4 variants in bench_all.cpp are commented out and decompression is not timed.

## Use it when

- Compressing in-memory arrays of sensor samples, image or volume data, time series or float tables on x86-64 with SSE4.1/AVX2, where you would otherwise reach for Blosc + Zstd.
- You do not know which filter (byte shuffle, bit shuffle, delta) suits the data and want the library to choose per superblock.
- Hard latency budgets: the time-limited mode adjusts the level during compression and falls back to memcpy so a call finishes in roughly the requested time.
- Large compressed arrays on slow storage where you need only some element ranges back (stenos_decompress_sub_part skips untouched superblocks).
- Multi-threaded block compression of big buffers via stenos_set_threads.

## Skip it when

- General byte streams such as text or logs: it targets typed arrays, and plain zstd or LZ4 is the simpler choice there.
- ARM or other non-x86 targets when speed matters: block compression is disabled under NEON ('Disable block compression on ARM for now' in stenos.cpp), leaving only the shuffle+Zstd paths, which is roughly what Blosc2 already offers.
- Streaming compression: the README says it is not supported yet.
- When you need interoperable or long-lived files read by other tools: the format is Stenos-only, the project has no tagged releases and 18 stars, and a container class (cvector) was pulled in September 2026 because it 'needs corrections first'.
- When you need independent proof of the speed claims: the only benchmark is the author's own, timing compression only.

## How it is fast

For each superblock it estimates compressibility (a write-free 'dry' LZ4 pass or a block size guess) and picks among four paths: a SIMD block codec, byte transposition (Blosc's shuffle code) plus Zstd, transposition plus byte delta plus Zstd, or raw Zstd. The SIMD block codec works on 256-element blocks, choosing per 16-element row between bit packing, delta coding and RLE with SSE4.1/AVX2 (BMI2 where available), and can hand residuals to Zstd at higher levels. Level 1 on multi-byte elements uses the block codec alone, which the README puts at about 2 GB/s compression and 3 GB/s decompression.

## Compared with alternatives

Pick Stenos over plain Zstandard or LZ4 when the input is an array of fixed-width numbers on x86-64 and you want transposition, delta and bit packing chosen automatically; for byte streams, on ARM, or when you need a stable widely supported format, Zstandard or LZ4 remain the safer choices.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake) |
| **Dependencies** | Zstd (fetched and built by default via FetchContent); OpenCL SDK fetched by default for the bundled video codec unless STENOS_WITH_OPENCL=OFF; bundles Blosc shuffle code, a simplified LZ4 and sse2neon |
| **Minimum toolchain** | README says C++14, but CMakeLists.txt sets cxx_std_17; CMake 3.16+ |
| **Platforms** | x86-64 with SSE4.1 for the SIMD block codec (AVX2 used when present); other Zstd-supported platforms, including ARM, run without the block codec; CI builds Windows/MSVC, Linux/GCC and macOS/Clang |
| **Thread safety** | Documented: one context must not be used from several threads without external locking; different contexts may run in parallel. Internally a context can use multiple worker threads. |
| **Drop-in for the baseline** | partial: same role and element-size parameter as Blosc's typesize, but a different API and an incompatible frame format |

## Gotchas

- The CMake option STENOS_NATIVE_ARCH defaults to ON and adds -march=native (and -mno-avx512f off macOS), so a default build may not run on older CPUs; turn it off for distributable binaries.
- The README lists STENOS_BUILD_ZSTD as OFF by default, but CMakeLists.txt defaults it to ON, so a default build fetches and statically links its own Zstd instead of the system one; STENOS_WITH_OPENCL is also ON by default and pulls the Khronos OpenCL SDK.
- bytesoftype is not stored in the frame: decompressing with a different element size than the compressor used is a caller error.
- Compressed data from an x86 SIMD build decodes on non-SSE machines through a scalar block_decompress path, but compression there never uses the block codec, so ratio and speed differ by platform.

## Known shortcomings

- Tier C: the README SVG compares only against Zstd with byteshuffle/bitshuffle (no LZ4 curve), no compiler or flags.
- benchs/bench_to_csv.cpp and bench_all.cpp time compression only, so the README's 'decompress 3 GB/s' is unmeasured, and the Blosc2+LZ4 variants in bench_all.cpp are commented out. The block codec is disabled under NEON; the README says C++14 but CMake sets cxx_std_17; STENOS_NATIVE_ARCH=ON adds -march=native by default; STENOS_BUILD_ZSTD defaults ON despite the README; the OpenCL SDK is fetched by default; cvector was removed 2026-09 ('needs corrections first'); no releases.

## Caveats and trade-offs

Own benchmark and dataset; compiler and flags not stated; numbers only as SVG curves. The README's 'or lz4' claim is not shown in the published graph, although benchs/bench_all.cpp contains Blosc2+LZ4 variants. Baseline is Blosc+Zstd, not plain zstd; specialised for typed binary arrays, not a general byte compressor. Stenos depends on Zstd and borrows Blosc's shuffle code and a simplified LZ4.

For arrays of fixed-width numeric elements, not general byte streams; depends on Zstd; SIMD block mode needs SSE4.1/AVX2 and is skipped on ARM; no streaming compression yet.

## Maintenance

Actively developed (146 commits, last 2026-09-21) and MIT-licensed, but young, single-author, with no releases and few users; vendor it only with your own round-trip tests.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party: README states the CPU (Intel Core i7-10850H, single thread) and the repo has the benchmark code (benchs/bench_all.cpp, which times Blosc2 shuffle/bitshuffle with zstd and lz4), but no compiler or flags are given and results appear only as ratio-vs-speed curves in docs/benchmarks.svg with no numeric table.
- **Verifier notes:** Metadata OK: MIT, 18 stars, last commit 2026-09-21, not a fork. SVG text labels were parsed; plotted values were not extracted.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/Thermadiag/stenos>
  - <https://github.com/Thermadiag/stenos/commits>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/README.md>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/docs/benchmarks.svg>
  - <https://github.com/Thermadiag/stenos/tree/main/benchs>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/benchs/bench_all.cpp>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/benchs/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/Thermadiag/stenos>
  - <https://github.com/Thermadiag/stenos/commits>
  - <https://github.com/Thermadiag/stenos/tree/main/stenos>
  - <https://github.com/Thermadiag/stenos/tree/main/stenos/internal>
  - <https://github.com/Thermadiag/stenos/tree/main/benchs>
  - <https://github.com/Thermadiag/stenos/tree/main/docs>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/README.md>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/stenos/stenos.h>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/stenos/internal/simd.h>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/stenos/internal/block_compress.h>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/stenos/internal/stenos.cpp>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/benchs/bench_all.cpp>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/benchs/bench_to_csv.cpp>
  - <https://raw.githubusercontent.com/Thermadiag/stenos/HEAD/docs/benchmarks.svg>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/thermadiag/stenos`) · [data/wave9/enrich/raw/github_com_thermadiag_stenos.json](../../../data/wave9/enrich/raw/github_com_thermadiag_stenos.json) (enrichment confidence 0.75)

</details>
