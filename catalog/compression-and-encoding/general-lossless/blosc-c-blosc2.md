# c-blosc2 (Blosc2 shuffle+lz4)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Blocked, multithreaded meta-compressor (shuffle/bitshuffle filters plus LZ4, Zstd, zlib or BloscLZ) for typed binary arrays; outruns memcpy on compressible data.

| | |
|---|---|
| **Beats** | memcpy (uncompressed copy); inner codecs lz4/zstd/zlib are components, not rivals |
| **Claimed result** | At 8 threads, lz4+shuffle clevel 1 (ratio 4.75): decompression 31337.5 MB/s vs memcpy(read) 8962.2 MB/s, and compression 13172.7 MB/s vs memcpy(write) 9641.2 MB/s (derived from page data: about 3.5x on decode and 1.4x on encode). At 16 threads, clevel 1: decomp 28495.0 MB/s and comp 19772.6 MB/s vs memcpy read 9311.2 / write 9828.8 MB/s (the 35428.1 MB/s figure is clevel 0, ratio 1.00, i.e. no compression). Single thread clevel 1 decode (5293.7 MB/s) is slower than memcpy(read) (8581.6 MB/s), and compression (2066.7 MB/s) is slower than memcpy(write) (4691.4 MB/s). |
| **Workload** | Repo bench suite (bench/b2bench.c) on 4 MiB synthetic 32-bit data with 19 significant bits, shuffle filter plus LZ4 codec, 256 MB working set, 8 threads: compressed-chunk read and write versus plain memcpy of the same buffer. |
| **Metric** | throughput |
| **Hardware** | Host named only 'corex' in the output (CPU model not stated) |
| **Adoption** | 586 stars; used by PyTables, h5py, Zarr per README |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/Blosc/c-blosc2) · [benchmark](https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/bench/results-corex/lz4-suite-corex.out) |

## Verdict

The project's own b2bench run (Blosc 2.0.0.beta.6, LZ4 1.9.3, host 'corex' with no CPU, compiler or flags stated) on a 4 MiB synthetic int32 buffer with 19 significant bits, 256 MB working set: with lz4+shuffle at clevel 1 (ratio 4.75) and 8 threads, decompression ran at 31337.5 MB/s versus memcpy(read) 8962.2 MB/s and compression at 13172.7 versus memcpy(write) 9641.2 MB/s (about 3.5x and 1.4x, derived from page data); at one thread both lose to memcpy. There is no head-to-head against standalone lz4 or zstd in the repo.

## Use it when

- Large arrays of fixed-width numeric data (int32, float32/64, timestamps) with smooth or low-entropy high bytes, where typesize-aware shuffle lets LZ4 or Zstd reach ratios a byte-oriented codec cannot.
- Memory- or I/O-bound pipelines on multi-core machines where keeping data compressed in RAM or on disk and decompressing with 4-16 threads beats reading it uncompressed.
- Chunked n-dimensional storage needing partial reads (B2ND slicing, lazy chunks), or when interoperating with PyTables, h5py (hdf5plugin) or Zarr, which already use Blosc.
- Buffers of roughly 1 MB and up: the threading notes say parallel mode only pays off above 64-128 KB per buffer.

## Skip it when

- Single-threaded use with fast-compressing settings: in the repo's own run, clevel 1 at one thread decodes at 5293.7 MB/s versus memcpy(read) 8581.6 MB/s, and compresses at 2066.7 versus 4691.4 MB/s; the default nthreads is 1.
- Text, already-compressed or irregular byte streams: shuffle helps nothing there, and Blosc then adds format and threading overhead on top of the plain codec.
- Parsing untrusted chunks or frames without care: OSS-Fuzz and a Trail of Bits audit keep finding memory bugs in decode paths (BloscLZ heap overflows fixed in 3.3.3 and again in 3.3.5, ZFP plugin over-reads and a frame divide-by-zero in 3.3.5, b2nd shape overflows in 3.3.0, CVE-2024-3203/3204 in 2.14.2); stay on the latest release.
- Multi-socket NUMA servers without tuning: issue #784 (open, June 2026) reports 2-5x slower runs on Xeon Platinum 8480C/8570 DGX nodes than on a Threadripper Pro workstation, attributed to NUMA, with no fix yet.
- When you need a standard stream format readable by gzip, lz4 or zstd tools, or Blosc1 readers of Blosc2 output (forward compatibility is not supported).

## How it is fast

Shuffle/bitshuffle transpose bytes or bits of fixed-size elements so that slowly varying high-order bytes line up into runs that a fast LZ codec squeezes well; the shuffles have SSE2, AVX2, NEON and AltiVec kernels (plus an AVX512 bitshuffle) picked at runtime (__builtin_cpu_supports/cpuid in blosc/shuffle.c). Data is processed in cache-sized blocks spread over a worker thread pool (or a user threading callback), so filter and codec run in cache and many cores share the work. The memcpy-beating result comes from moving fewer bytes through memory: with a 4.75x ratio, 8 threads decode faster than a single memcpy can read the uncompressed buffer.

## Compared with alternatives

Pick Blosc2 over calling LZ4 or Zstd directly when the data is typed numeric arrays and you have spare cores, since shuffle plus blocking lifts both ratio and throughput; pick Stenos if its numbers on your data beat Blosc2+Zstd, and plain LZ4/Zstd for text, streams or single-threaded use.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake; also prebuilt in the blosc2 Python wheel) |
| **Dependencies** | LZ4, Zstd and zlib-ng (zlib-compatible) are needed; by default CMake fetches pinned upstream sources with FetchContent at configure time (BLOSC_DEPENDENCY_MODE=BUNDLED), or uses system packages with EXTERNAL; ZFP optional; pthreads (or a user threading callback) |
| **Minimum toolchain** | C99 compiler, CMake 3.16.3+; VS2015+ on Windows; the AVX512 bitshuffle path needs GCC 11.4+ or Clang 13+ (CMakeLists notes Linux wheels built with older GCC ship without it) |
| **Platforms** | Linux, macOS and Windows on x86-64 (SSE2/AVX2/AVX512 with runtime dispatch), ARM Linux/macOS (NEON), PowerPC (AltiVec/VSX); ARM on Windows not supported |
| **Thread safety** | Use the \*_ctx functions with one context per thread; blosc2_compress/blosc2_decompress go through a global context under a global lock (BLOSC_NOLOCK switches them to private contexts), and blosc2_set_threads_callback is not thread-safe and must be called before any other Blosc call. |
| **Drop-in for the baseline** | partial — it replaces memcpy-style storage of arrays only if you adopt its chunk/frame API and format; it is not API- or format-compatible with plain lz4/zstd/zlib |

## Gotchas

- Speed depends on telling Blosc the right typesize and filter; with the wrong typesize or no shuffle it degrades to roughly the plain inner codec plus overhead (an independent float-compression blog series says this, per WebSearch snippet only).
- The default build downloads codec sources during CMake configure; offline or distro builds need BLOSC_DEPENDENCY_MODE=EXTERNAL or the BLOSC_\*_SOURCE_DIR overrides. Issue #469 reports a self-built library running about 2x slower than the one shipped in the Python wheel, so check build type and SIMD flags before benchmarking.
- Chunk sizes are 32-bit: a single chunk is capped at INT_MAX minus the 32-byte maximum overhead, so bigger data must go through super-chunks.
- Environment variables (BLOSC_NTHREADS, BLOSC_NOLOCK, BLOSC_SPLITMODE, BLOSC_TRACE) silently change the behaviour of the non-ctx calls.

## Known shortcomings

- Only baseline is memcpy; bench/ has no run against standalone lz4 or zstd, and the README plot compares NDArray with Zarr(Blosc1)/HDF5. The 16-thread 35428.1 MB/s figure was clevel 0 (ratio 1.00); clevel 1 is 28495.0 MB/s. CPU unnamed, 2020 run. The Aras blog comparison with plain zstd/lz4 was seen in a snippet only.
- Memory bugs keep turning up in decode paths: OSS-Fuzz found BloscLZ heap overflows (fixed 3.3.3, again 3.3.5), ZFP plugin over-reads and a frame divide-by-zero (3.3.5), b2nd shape overflows (3.3.0); CVE-2024-3203/3204 fixed in 2.14.2; Trail of Bits fixes in 3.0.0-rc1. Do not feed untrusted frames to old versions. Single-thread clevel 1 is slower than memcpy and the default nthreads is 1. Issue #784 open: 2-5x slower on Xeon 8480C/8570 NUMA; issue #469: a self-built library ran 2x slower than the wheel. Default CMake fetches codecs at configure time. Chunk cap INT_MAX-32. The benchmark is a 2020 beta run on synthetic 19-bit data with a memcpy baseline only.

## Caveats and trade-offs

Result file is from Blosc 2.0.0.beta.6 (2020) with LZ4 1.9.3 and Zstd 1.4.9; CPU model, compiler and flags are not stated (first-party, tier C). The baseline is memcpy only: bench/ (b2bench.c, sum_openmp.c, sframe_bench.c, delta_schunk.c, zero_runlen.c and others) has no benchmark against standalone lz4/zstd/zlib, and the one README plot (images/Read-Partial-Slices-B2ND.png) compares the Python NDArray slicing (2.25/1.34/0.75/0.5 GB/s) against Zarr with Blosc1 and HDF5 via h5py-Blosc2, not against a codec. Data is synthetic. An independent blog (Aras Pranckevicius, 'Float Compression 8: Blosc', 2023) says, per a WebSearch snippet only (the site is blocked here), that Blosc defaults beat plain zstd (slightly higher ratio, faster compression, much faster decompression) and mostly beat plain lz4 (much better ratio, faster compression, slightly slower decompression); no numbers were read and its Blosc version is unconfirmed. The zstd sum_openmp output in the same folder shows compressed-in-memory summation slower than uncompressed (1582 MB/s vs 11818 MB/s at 1 thread). The Blosc2 blog, Blosc2-Debunking-Myths.pdf (blosc.org) and the SciPy NDim paper were blocked.

Meta-compressor: needs typed, regular binary data (shuffle/bitshuffle filters) to win; gains come from multithreading and cache effects; chunked frame format and NDim layer add API surface.

## Maintenance

Very active (3.3.6.dev dated 2026-09-24, last commit 2026-10-01, NumFOCUS-sponsored, BSD-3-Clause), with a steady stream of fuzzing-driven security fixes; the benchmark evidence is a 2020 beta, so re-measure on current releases and your hardware.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** bench/results-corex/lz4-suite-corex.out (output of bench/b2bench.c) shows Blosc2 lz4+shuffle against memcpy on the same buffer, but it names no CPU model (host 'corex' only), compiler or flags, and it comes from the project itself, so it is first-party with partial methodology (C). The only comparison against plain zstd/lz4 found is an independent blog's directional statement, read in a search snippet only.
- **Verifier notes:** The 8-thread numbers match the page. The 16-thread decompression figure in the record was the clevel 0 (uncompressed passthrough) row, so I corrected it to clevel 1. The license is BSD-3-Clause (3 clauses in LICENSE.txt), the repo has 586 stars and is not archived, and the last commit is 2026-10-01; all match. Tier C stands; a tier B upgrade would need the Aras blog's numbers from an environment that reaches aras-p.info.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party benchmark
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/bench/results-corex/lz4-suite-corex.out>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/README.rst>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/bench/plot-speeds.py>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/main/images/Read-Partial-Slices-B2ND.png>
  - <https://github.com/Blosc/c-blosc2>
  - <https://github.com/Blosc/c-blosc2/tree/main/bench>
  - <https://github.com/Blosc/c-blosc2/commits/main>
  - <https://github.com/aras-p/float_compr_tester>
- **Sources the enricher read:**
  - <https://github.com/Blosc/c-blosc2>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/README.rst>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/RELEASE_NOTES.md>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/ANNOUNCE.md>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/README_THREADED.rst>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/include/blosc2.h>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/blosc/shuffle.c>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/bench/results-corex/lz4-suite-corex.out>
  - <https://github.com/Blosc/c-blosc2/issues?q=is%3Aissue+performance+OR+slower>
  - <https://github.com/Blosc/c-blosc2/issues/784>
  - <https://github.com/Blosc/c-blosc2/issues/469>
  - WebSearch snippet only: https://aras-p.info/blog/2023/03/02/Float-Compression-8-Blosc/ (site blocked here)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/blosc/c-blosc2`) · [data/wave9/enrich/raw/github_com_blosc_c_blosc2.json](../../../data/wave9/enrich/raw/github_com_blosc_c_blosc2.json) (enrichment confidence 0.8)

</details>
