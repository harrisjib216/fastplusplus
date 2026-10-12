# Generalized Elias-Fano (GEF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Elias-Fano-style compressed integer arrays for unsorted sequences, with O(1) random access; claims smaller than ALP, LeCo and DAC.

| | |
|---|---|
| **Beats** | ALP, LeCo, DAC (random-access integer compressors); also compared with Xz and Brotli |
| **Claimed result** | Snippet only (project site): up to 42.83% more compact than compressors with high throughput and random access (e.g. ALP, LeCo, DAC); compression ratios typical of general-purpose compressors (Brotli, Zstd) while keeping constant-time random access; up to 500x faster compression than general-purpose compressors (e.g. Brotli, Xz) and learned compressors (e.g. NeaTS); &gt;1 GB/s throughput. |
| **Workload** | Compressed storage of arbitrary (non-monotone) integer sequences with constant-time random access, plus &gt;1 GB/s throughput. |
| **Metric** | memory |
| **Adoption** | 4 stars |
| **Last commit** | 2026-02-01 |
| **Links** | [repository](https://github.com/mxpucci/generalized-elias-fano) · [benchmark](https://gef.di.unipi.it/) |

## Verdict

The headline numbers (up to 42.83% smaller than ALP, LeCo and DAC; near Brotli/Zstd ratios with O(1) access; up to 500x faster compression than Brotli, Xz and NeaTS; over 1 GB/s) come only from a search snippet of the authors' site, with no compiler or CPU for the baseline runs. The repo's own Google Benchmark JSON (bench_partition_size_tradeoff, 72-CPU 3.7 GHz host, Release) shows B_GEF alone at, for example, 10.5 bits per element on AP.bin and 9.3 on CT.bin (64-bit inputs) with single-thread compression around 70-170 MB/s at 8,000-element partitions; the &gt;1 GB/s figure matches only the multi-threaded throughput plot (up to about 5,000 MB/s).

## Use it when

- Large read-mostly arrays of 32/64-bit integers with locally smooth values (sensor or financial time series, fixed-point floats) where you need random access without decompressing blocks.
- Replacing block compressors (zstd/brotli per block) or fixed-width bit packing when point lookups dominate and space matters more than build time.
- Workloads that decode long ranges: get_elements streams partitions and goes multi-threaded with OpenMP for spans of at least 100,000 elements across 4 or more partitions.
- GPL-compatible projects already using sdsl-lite, where the extra dependency costs nothing.

## Skip it when

- Proprietary or Apache-only codebases: the GEF code is Apache-2.0, but it links sdsl-lite (GPLv3 or later) and pasta bit_vector (GPLv3), so any binary built with it is effectively GPLv3.
- Sorted sequences or rank/select bitvectors: plain or partitioned Elias-Fano, or LA-vector, are the established choices there.
- Data that changes: there is no append or update; you rebuild the whole structure.
- When you need independently checked numbers: the ALP/LeCo/DAC/Brotli/Xz comparisons live only on the first-party project site (gef.di.unipi.it, not opened here); the repo's benchmarks and plots cover GEF variants only and ship no datasets.
- MSVC or other compilers without __int128 and __builtin_\* (the README lists MSVC 2019+, but the headers use unsigned __int128 and GCC builtins).

## How it is fast

Each value minus the sequence minimum is split at a chosen bit b into low bits (stored verbatim in an sdsl int_vector L) and high bits. In B_GEF, small up/down changes between consecutive high parts are written in unary into two gap bitvectors (G+ and G-), while large jumps are flagged in an exception bitvector B and stored in full in H; rank/select over these pasta bitvectors gives O(1) access. b is chosen per partition (default 32,000 elements) by exhaustive search (OPTIMAL) or a closed-form estimate (APPROXIMATE); partitions are built in parallel with OpenMP, and range decoding batch-decodes the unary gaps 64 at a time with ctz/prefetch and AVX2 or NEON bit writers.

## Compared with alternatives

Pick it over LA-vector when the integers are not sorted (LA-vector and Elias-Fano need monotone input); for sorted posting lists or rank/select bitvectors use LA-vector, CPEF or the rank/select siblings instead.

## Integration

| | |
|---|---|
| **Form** | header-only templates exposed as a CMake INTERFACE target (gef::gef), but it links the compiled sdsl-lite library |
| **Dependencies** | sdsl-lite (fetched from simongog/sdsl-lite master and patched at configure time), vigna/sux (master), pasta-toolbox/bit_vector (main, pulls tlx), optional OpenMP; googletest and Google Benchmark 1.8.3 for tests/benchmarks |
| **Minimum toolchain** | C++20, CMake 3.14+; GCC or Clang (README says GCC 10+/Clang 10+/MSVC 2019+, but CI builds only GCC on Alpine and needs -Wno-error=template-body and CMAKE_POLICY_VERSION_MINIMUM=3.14) |
| **Platforms** | x86-64 (BMI1/AVX2 paths) and AArch64 (NEON path) with scalar fallback via GEF_DISABLE_SIMD; CI builds Linux x86-64 only |
| **Thread safety** | not documented; const accessors appear read-only, and construction plus large get_elements calls use OpenMP threads internally |
| **Drop-in for the baseline** | no |

## Gotchas

- Linking gef::gef injects -O3 -march=native -ffast-math -funroll-loops into every consumer target's Release compile (INTERFACE compile options), changing your floating-point semantics and making binaries CPU-specific unless you override GEF_TARGET_ARCH and strip the flags.
- Dependencies are fetched from unpinned master/main branches (sdsl-lite, sux, pasta) and sdsl-lite's CMakeLists is rewritten at configure time, so builds are not reproducible; CI only checks that test binaries exist and never runs them.
- The partition size K is a template parameter that serialize() does not store: loading a file with a different K silently gives wrong indexing. The format is raw native-endian size_t/T writes, and load() trusts the stream (no bounds or consistency checks), so treat serialized files as trusted input only.
- operator[] on the top-level classes throws std::out_of_range, but the internal partition decoders have no bounds checks; signed 64-bit inputs spanning more than 2^63 rely on signed overflow in the base + offset reconstruction (long long), which is undefined behaviour without -fwrapv.

## Known shortcomings

- Weak evidence: baseline numbers exist only in a search snippet of gef.di.unipi.it (blocked here); the repo's result JSONs cover GEF variants only, with no baseline rows. Kept at C on the snippet; drop to D if the site stays unreachable.
- Licence: GEF code is Apache-2.0 but links sdsl-lite (GPLv3+) and pasta bit_vector (GPLv3), so binaries are effectively GPLv3. The gef::gef INTERFACE target pushes -O3 -march=native -ffast-math into every consumer's Release build. Dependencies are fetched from unpinned master/main and sdsl's CMakeLists is patched at configure time; CI builds tests but never runs them. README claims MSVC support but the code uses __int128 and __builtin_\*. The partition size K is not serialised, so loading with a different K silently gives wrong indexing; load() trusts the stream. Possible signed-overflow UB for int64 inputs spanning more than 2^63. Repo benchmarks cover GEF variants only: single-thread compression 70-170 MB/s, and the '&gt;1 GB/s' matches only the multi-thread plot (about 5000 MB/s).

## Caveats and trade-offs

Numbers come from a WebSearch snippet of the project site gef.di.unipi.it (blocked, not opened); the README has no numbers. The repo has benchmarks/ (bench_compression, bench_decompression, bench_random_access, bench_multithread_scalability, bench_partition_size_tradeoff) and benchmark_results/ JSONs for GEF variants only, with no baseline rows, compiler or CPU model. Baselines are not SDSL or sux, so the entry is borderline for this category. Mostly a space win with random access. Needs C++20.

Header-only, C++20; generalizes Elias-Fano to unsorted sequences; repo has a benchmarks directory, benchmark_results folder and run_benchmarks.sh (contents not opened).

## Maintenance

Active (last commit 2026-02-01, 136 commits, 4 stars), research-grade code from the University of Pisa; Apache-2.0 on its own but GPLv3 in practice through sdsl-lite and pasta, and no tagged release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The baseline comparisons exist only on the first-party project site gef.di.unipi.it (EGRESS_BLOCKED; only a WebSearch snippet was read). The repo's benchmark_results/benchs_st JSONs (Google Benchmark, bench_partition_size_tradeoff, 72-CPU 3.7 GHz host, release build) cover GEF variants only and contain no ALP/LeCo/DAC/Xz/Brotli rows. This is C on snippet evidence; drop to D if snippet-only numbers are not accepted.
- **Verifier notes:** The record's claim 'matches Xz and Brotli in space while orders of magnitude faster' was a loose paraphrase; it is replaced with the snippet wording. Apache-2.0, 4 stars, 136 commits, not archived, last commit 2026-02-01. A paper or the site would be needed for any tier above C.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** first-party claim (snippet)
- **Pages the verifier opened:**
  - <https://github.com/mxpucci/generalized-elias-fano>
  - <https://github.com/mxpucci/generalized-elias-fano/commits>
  - <https://github.com/mxpucci/generalized-elias-fano/tree/main/benchmark_results>
  - <https://github.com/mxpucci/generalized-elias-fano/tree/main/benchmark_results/benchs_st>
  - <https://github.com/mxpucci/generalized-elias-fano/tree/main/benchmarks>
  - <https://github.com/mxpucci/generalized-elias-fano/blob/main/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/README.md>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/benchmark_results/benchs_st/B_GEF.json>
- **Sources the enricher read:**
  - <https://github.com/mxpucci/generalized-elias-fano>
  - <https://github.com/mxpucci/generalized-elias-fano/tree/main/include>
  - <https://github.com/mxpucci/generalized-elias-fano/tree/main/include/gef>
  - <https://github.com/mxpucci/generalized-elias-fano/tree/main/tests>
  - <https://github.com/mxpucci/generalized-elias-fano/tree/main/plots>
  - <https://github.com/mxpucci/generalized-elias-fano/tree/main/scripts>
  - <https://github.com/mxpucci/generalized-elias-fano/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/include/gef/gef.hpp>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/include/gef/B_GEF.hpp>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/include/gef/B_STAR_GEF.hpp>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/include/gef/U_GEF.hpp>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/include/gef/RLE_GEF.hpp>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/include/gef/UniformPartitioning.hpp>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/include/gef/FastUnaryDecoder.hpp>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/include/gef/FastBitWriter.hpp>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/include/gef/gap_computation_utils.hpp>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/.github/workflows/build-linux.yml>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/benchmark_results/benchs_st/B_GEF.json>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/plots/compression_ratio_by_compressor.pdf>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/plots/compression_throughput_by_compressor_st.pdf>
  - <https://raw.githubusercontent.com/mxpucci/generalized-elias-fano/HEAD/plots/compression_throughput_by_compressor_mt.pdf>
  - <https://raw.githubusercontent.com/simongog/sdsl-lite/master/COPYING>
  - <https://raw.githubusercontent.com/pasta-toolbox/bit_vector/main/LICENSE>
  - <https://raw.githubusercontent.com/pasta-toolbox/bit_vector/main/README.md>
  - <https://raw.githubusercontent.com/vigna/sux/master/README.md>
  - WebSearch: "Generalized Elias-Fano" compressed index arbitrary integer sequences (snippet of gef.di.unipi.it; page not opened)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/mxpucci/generalized-elias-fano`) · [data/wave9/enrich/raw/github_com_mxpucci_generalized_elias_fano.json](../../../data/wave9/enrich/raw/github_com_mxpucci_generalized_elias_fano.json) (enrichment confidence 0.7)

</details>
