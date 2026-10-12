# Blosc (c-blosc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Blocked, multithreaded meta-compressor (shuffle/bitshuffle plus BloscLZ, LZ4, Zstd, zlib) for typed numeric arrays; can outrun memcpy on compressible data.

| | |
|---|---|
| **Beats** | memcpy (single ctypes.memmove call; Blosc's own named baseline) |
| **Claimed result** | memcpy via ctypes.memmove 0.276 s (2.70 GB/s). arange data: blosclz+shuffle 17.77 GB/s compress and 27.18 GB/s decompress (ratio 57.1x); lz4+shuffle 22.58 / 22.03 GB/s (68.6x); zstd+shuffle 7.97 / 32.71 GB/s (156.7x). random data: lz4+shuffle 11.02 / 26.03 GB/s (4.5x); blosclz+shuffle 8.21 / 44.29 GB/s (3.9x). Roughly 6.6x memcpy compress and 10x memcpy decompress for blosclz+shuffle on arange (derived from page data). Without the shuffle filter blosclz is slower than memcpy: 1.95 / 2.48 GB/s at ratio 1.0x. |
| **Workload** | python-blosc bench/compress_ptr.py: NumPy arrays of 10\*\*8 int64/float64 elements (about 800 MB; arange, linspace and random distributions), clevel 5, 24 threads, compress and decompress through Blosc 1.11.2 (the C library) with each codec and the shuffle/bitshuffle filters, timed against a plain ctypes.memmove() copy of the array. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2695 v3 @ 2.30GHz (56 cores detected), 24 threads used, CentOS 7.2, Linux 3.10.0 (as printed in the README run) |
| **Adoption** | 1.1k stars; official Python wrapper (python-blosc, 362 stars) and HDF5 filter (hdf5-blosc); the README says c-blosc is in pure maintenance mode and recommends C-Blosc2 for new work |
| **Last commit** | 2026-08-27 |
| **Links** | [repository](https://github.com/Blosc/c-blosc) · [benchmark](https://github.com/Blosc/python-blosc) |

## Verdict

The project's own 2017 run printed in the python-blosc README (Blosc 1.11.2 with BloscLZ 1.0.5, LZ4 1.7.5, Zstd 1.1.2; Xeon E5-2695 v3, CentOS 7.2; C-library compiler flags not given) compresses 10^8 int64/float64 elements (800 MB) at clevel 5 and compares each codec with one ctypes.memmove of the same array: memmove 0.276 s (2.70 GiB/s) versus blosclz+shuffle on arange 17.77 GiB/s compress and 27.18 GiB/s decompress at 57.1x, and lz4+shuffle on randint(0, 1000) data 11.02 / 26.03 GiB/s at 4.5x. Each figure is one time.time() sample, the baseline is one thread against a pool labelled 24 threads, and the baseline time includes page faults on a fresh destination that compression mostly avoids.

## Use it when

- Low-entropy numeric arrays of 2-8 byte elements (time series, regular grids, sorted ids, sparse data) where shuffle lifts the ratio well above 2x; the README run reached 57x-320x on arange data.
- Buffers of roughly 1 MB and up with spare cores: README_THREADED.rst says the thread pool only pays off above 64/128 KB, with a sweet spot near 1 MB per call.
- Code or data that must stay on the Blosc 1.x chunk format and C ABI (python-blosc, hdf5-blosc, bloscpack, existing files).
- Random access to a slice of items inside a compressed buffer via blosc_getitem().
- C89-only toolchains or unusual platforms (README: any C89 compiler; IBM Blue Gene Q A2 reported to work).

## Skip it when

- New projects: the README says c-blosc is in pure maintenance mode with no new features and points to C-Blosc2 (NEON/AltiVec shuffles, AVX512 bitshuffle, super-chunks, frames).
- Text, already-compressed or high-entropy bytes, or wrong typesize: without shuffle the README's own run has blosclz at 1.95 GiB/s compress and 2.48 GiB/s decompress at ratio 1.0x, slower than the 2.70 GiB/s memcpy line.
- Single-threaded or small-buffer use: the memcpy-beating figures are many-thread runs against a one-thread memmove, and the threaded path falls back to serial below 64/128 KB.
- Buffers near 2 GB: BLOSC_MAX_BUFFERSIZE is INT_MAX minus 16, and open issue #385 (Aug 2024, no maintainer reply) reports a Valgrind invalid 8-byte write in fastcopy.c copy_16_bytes and a -1 return when compressing 2,147,483,631 bytes.
- Builds with GCC 15 auto-vectorization on some CPUs: open issue #402 (June 2026) reports blosclz+shuffle/bitshuffle tests segfaulting on Cascade Lake and Zen 4 with GCC 15.2.0 -O3 -ftree-vectorize -march=native (workaround -fno-tree-vectorize), root cause unknown.

## How it is fast

The shuffle filter transposes the bytes (bitshuffle: the bits) of each typesize-element so equal-significance bytes sit together, which turns slowly varying numbers into long runs that a fast LZ codec compresses well; x86 gets SSE2/AVX2 kernels chosen at run time by cpuid under pthread_once, other architectures fall back to generic C. The buffer is split into cache-sized blocks (automatic block size up to 256 KB for fast codecs since 1.19) that a worker thread pool shuffles and compresses in cache, the 'blocking technique' of the 2010 CISE 'Starving CPUs' paper. Beating memcpy comes from moving fewer bytes through memory and from using many cores while memcpy uses one.

## Compared with alternatives

Pick c-blosc over c-blosc2 only when you need the Blosc 1.x format, its frozen C ABI or a C89 compiler; otherwise C-Blosc2 is the maintained successor with ARM SIMD. Over calling LZ4 or Zstd directly, pick Blosc for typed numeric arrays with spare cores (shuffle plus blocking raises both ratio and speed); use plain LZ4/Zstd for text, streams or single-threaded work, and test Stenos if its numbers on your data beat Blosc plus Zstd.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake); also shipped prebuilt inside python-blosc wheels |
| **Dependencies** | none required: LZ4 1.10.0, zlib 1.3.1, Zstd 1.5.6 and BloscLZ are bundled in internal-complibs (PREFER_EXTERNAL_\* switches to system copies); Snappy is off by default (DEACTIVATE_SNAPPY=ON) because it needs a C++ compiler; pthreads |
| **Minimum toolchain** | C89 C compiler; CMake 3.10+ on main (the v1.21.6 release has open issue #394, failure to build with CMake 4.0) |
| **Platforms** | any C89 platform; mostly tested on x86 Linux, macOS and Windows and on ARM Linux; SSE2/AVX2 shuffle kernels only on x86 (runtime cpuid dispatch), generic C shuffle elsewhere |
| **Thread safety** | blosc_compress/blosc_decompress use one global context behind a global mutex after blosc_init(); for concurrent callers use blosc_compress_ctx/blosc_decompress_ctx exclusively (no blosc_init needed), which start and release their own worker pool on every call when numinternalthreads &gt; 1 |
| **Drop-in for the baseline** | partial — not a memcpy replacement: it produces a compressed copy that must be decompressed, and only wins over memcpy on compressible typed data with several threads |

## Gotchas

- Harness flaw behind the memcpy comparison: the README run (python-blosc 1.5.1.dev0, Blosc 1.11.2) came from the bench/compress_ptr.py of that era (identical at tags v1.5.0 and v1.5.1), which allocates the memmove destination and every decompression destination with np.empty right before timing, so the 0.276 s single-threaded memcpy baseline includes first-touch page faults on 800 MB of fresh memory, while compression writes only the compressed bytes into an oversized uninitialised bytes object (blosc_extension.c v1.5.0 lines 200 and 245) and so faults about 1/57 of the pages at 57x; the np.full pre-fault ('cause page faults here') was only added in v1.9.0. The 6.6x-memcpy compress figure is inflated by the baseline's page-fault cost.
- The README run's thread count cannot be reproduced from the published script: the v1.5.x script labels the thread count with blosc.ncores and never calls set_nthreads (python-blosc 1.5.x defaults to min(ncores, 4) threads), yet the pasted output prints 'Detected cores: 56', 'Number of threads to use by default: 4' and then '24 threads', which one run of that script cannot produce; the output came from a locally modified script or was edited, so whether 4 or 24 threads ran is unknown.
- blosc_decompress() takes no source length and trusts the compressed size stored in the 16-byte header; for untrusted input call blosc_cbuffer_validate(cbuffer, cbytes, &nbytes) first, which checks the header against the real byte count.
- Environment variables silently change the non-ctx calls: BLOSC_NTHREADS, BLOSC_NOLOCK, BLOSC_CLEVEL, BLOSC_SHUFFLE, BLOSC_TYPESIZE, BLOSC_COMPRESSOR and BLOSC_SPLITMODE override the arguments given in code.

## Known shortcomings

- python-blosc README numbers compare one single-threaded memmove against 24-thread Blosc in single-shot GiB/s timings; the 'random' input is randint(0,1001) int64, so every input compresses well. No compiler flags. Maintenance mode; c-blosc2 is the active successor.
- Enricher: the README run (python-blosc 1.5.1.dev0) used the v1.5.x bench/compress_ptr.py, which allocates the memmove and decompress destinations with np.empty right before timing, so the 0.276 s single-thread memcpy baseline includes page faults on 800 MB of fresh memory while compress only writes cbytes into an oversized bytes object (the np.full prefault arrived only in v1.9.0), inflating the 6.6x compress figure; the pasted output ('Detected cores: 56', 'default: 4', '24 threads') cannot come from the unmodified script. Open crash issues #385 (invalid write near 2 GB) and #402 (GCC 15 -ftree-vectorize segfault). Downgraded C to D (AssemblyScript precedent: baseline crippled by the harness).

## Caveats and trade-offs

The numbers are the project's own, printed in the README of the Python wrapper (python-blosc 1.5.1.dev0 driving Blosc 1.11.2, a 2017 run) from bench/compress_ptr.py, with partial methodology: CPU and thread count are stated, the compiler flags of the C library are not (the header only shows Python 3.5.2 built with GCC 4.4.7). Each figure is a single time.time() measurement with no repetitions, and the 'GB/s' figures are GiB/s (N\*8/t/2\*\*30); decompressed output is checked with an assert. The memcpy baseline is one single-threaded ctypes.memmove call on the arange array while Blosc ran 24 threads, so the ratio mixes parallelism with compression. All three inputs are highly compressible: arange and linspace are synthetic linear sequences (ratio up to 260x with bitshuffle), and the 'random' distribution is np.random.randint(0, 1001) stored as int64 (about 10 significant bits per 8-byte element), not incompressible data. Without shuffle blosclz is slower than memcpy. The c-blosc2 repo's own bench/results-corex/blosclz-suite-corex.out (Blosc 2.0.0.beta.6.dev, 2020, no CPU named, 4 MB synthetic data with 19 significant bits, blosclz+shuffle) shows the same shape: at 1 thread and clevel 1, decompress 10667.6 MB/s vs memcpy(read) 8289.1 MB/s and compress 4714.6 vs memcpy(write) 4628.8 MB/s. The blosc.org benchmark pages and the 2010 CISE paper are EGRESS_BLOCKED here, so they were not read. c-blosc is in pure maintenance mode (README); the Blosc2 successor (github.com/Blosc/c-blosc2) is already in the catalogue at tier C. [retier] python-blosc README numbers (1.5.1.dev0) compare one single-threaded memmove against 24-thread Blosc in single-shot GiB/s timings on randint(0,1001) int64 'random' data, so every input compresses well; no compiler flags. The v1.5.x bench/compress_ptr.py allocates the memmove and decompress destinations with np.empty right before timing, so the 0.276 s memcpy baseline includes page faults on 800 MB of fresh memory while compress only writes cbytes into an oversized bytes object (blosc_extension.c v1.5.0 lines 200 and 245; the np.full prefault arrived in v1.9.0), inflating the 6.6x compress figure. The script prints blosc.ncores with a default of min(ncores,4), yet the pasted output shows 'Detected cores: 56', 'default: 4' and '24 threads', so it was edited or came from a modified script. Open crash issues #385 (invalid write near 2 GB) and #402 (GCC 15 -ftree-vectorize segfault, no reply). Maintenance mode, last release v1.21.6 (2024-06-24); c-blosc2 is the active successor.

Meta-compressor: the speedup comes from blocking, the shuffle/bitshuffle filters, SIMD and its own thread pool, and it pays off for typed binary data such as numeric arrays (needs the type size); bundles LZ4, Snappy, Zlib and Zstd. The repository says it is in pure maintenance mode and points to C-Blosc2 for new features. C89 code base.

## Maintenance

Pure maintenance mode by its own README (last release v1.21.6 on 2024-06-24, last commit 2026-08-27 bumping the CMake minimum, crash issues #385 and #402 open without replies); BSD-3-Clause and easy to vendor, but the published benchmark is a 2017 run on long-superseded codec versions, so re-measure, and prefer C-Blosc2 for new work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party run printed in the python-blosc README from its public script bench/compress_ptr.py, with CPU (Xeon E5-2695 v3) and thread count stated but no compiler flags for the C library (only the Python interpreter's GCC 4.4.7 banner); partial methodology, so C, not A or B.
- **Retiered** C to D: Downgraded C to D: the python-blosc README numbers come from the v1.5.x bench/compress_ptr.py, whose memcpy baseline writes into freshly np.empty-allocated memory (page faults on 800 MB) while compress writes only cbytes into a preallocated bytes object, and the pasted thread counts cannot come from the unmodified script (AssemblyScript precedent: baseline crippled by the harness).
- **Verifier notes:** Numbers match the python-blosc README exactly (memmove 0.276 s, 2.70 GB/s; blosclz+shuffle arange 17.77 / 27.18 GB/s; random lz4+shuffle 11.02 / 26.03 GB/s; 6.6x and 10x derived ratios correct). Added harness facts from bench/compress_ptr.py: single-shot timings, GiB units, and the 'random' input is randint(0, 1001) int64, so every dataset is very compressible. Shortcomings: single-threaded memcpy vs 24-thread Blosc, synthetic data, no compiler flags, maintenance mode; not a duplicate of c-blosc2 (separate 1.x library and format), but related.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party python-blosc README (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/Blosc/python-blosc>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/HEAD/README.rst>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/main/bench/compress_ptr.py>
  - <https://github.com/Blosc/c-blosc>
  - <https://github.com/Blosc/c-blosc/commits>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/LICENSE.txt>
  - <https://github.com/Blosc/c-blosc2/tree/main/bench/results-corex>
  - <https://raw.githubusercontent.com/Blosc/c-blosc2/HEAD/bench/results-corex/blosclz-suite-corex.out>
- **Sources the enricher read:**
  - <https://github.com/Blosc/c-blosc>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/README.md>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/README_THREADED.rst>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/RELEASE_NOTES.rst>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/THANKS.rst>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/blosc/blosc.h>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/blosc/blosc.c>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/blosc/shuffle.c>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/bench/bench.c>
  - <https://raw.githubusercontent.com/Blosc/c-blosc/HEAD/tests/CMakeLists.txt>
  - <https://github.com/Blosc/c-blosc/commits>
  - <https://github.com/Blosc/c-blosc/tags>
  - <https://github.com/Blosc/c-blosc/issues>
  - <https://github.com/Blosc/c-blosc/issues/385>
  - <https://github.com/Blosc/c-blosc/issues/402>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/HEAD/README.rst>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/HEAD/bench/compress_ptr.py>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/HEAD/blosc/__init__.py>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/HEAD/blosc/toplevel.py>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/v1.5.0/bench/compress_ptr.py>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/v1.5.0/blosc/__init__.py>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/v1.5.0/blosc/blosc_extension.c>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/v1.5.1/bench/compress_ptr.py>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/v1.5.1/blosc/__init__.py>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/v1.7.0/bench/compress_ptr.py>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/v1.8.0/bench/compress_ptr.py>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/v1.9.0/bench/compress_ptr.py>
  - <https://raw.githubusercontent.com/Blosc/python-blosc/v1.10.0/bench/compress_ptr.py>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/blosc/c-blosc`) · [data/wave9/enrich/raw/github_com_blosc_c_blosc.json](../../../data/wave9/enrich/raw/github_com_blosc_c_blosc.json) (enrichment confidence 0.75)

</details>
