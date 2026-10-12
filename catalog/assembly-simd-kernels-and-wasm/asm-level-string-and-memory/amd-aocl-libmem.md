# AOCL-LibMem (AMD optimized memory and string functions)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> AMD's Zen-tuned replacements for glibc memcpy/memmove/memset/memcmp and str\* functions, loaded by LD_PRELOAD or static link; no published speedups.

| | |
|---|---|
| **Beats** | glibc memcpy, memmove, memset, memcmp, memchr, strcpy, strncpy, strcmp, strncmp, strlen, strnlen, strcat, strncat, strstr, strspn, strchr (benchmark tool compares against the glibc installed on the test host) |
| **Claimed result** | No numbers. README: library 'highly optimized for AMD Zen micro-architecture' with multiple implementations per function chosen at runtime; benchmark_guide.md: 'Gives the Throughput gains in %age' against glibc. |
| **Workload** | No results published. The repo ships a benchmark framework (TinyMemBench, Google Benchmark hot/cold cache, Google FleetBench v0.2 and v0.3.3, Meta DCPerf) that reports throughput gain in percent of LibMem over host glibc for memcpy, memmove, memset and memcmp. |
| **Metric** | throughput |
| **Hardware** | AMD Zen microarchitecture (AVX2 or AVX-512 builds) |
| **Compiler and flags** | AOCC or GCC per the benchmark guide; CMake flag ALMEM_ARCH selects AVX2 or AVX512 builds; no benchmark flags stated |
| **Adoption** | 38 stars, 11 forks; AMD's official AOCL component (commits titled 'Updates for AOCL 5.0 Release' through 'Updates for AOCL 5.3.2 Release'; the GitHub Releases section is empty) |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/amd/aocl-libmem) · [benchmark](https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/tools/benchmark/benchmark_guide.md) |

## Verdict

Nothing has been measured publicly: the repo only provides a harness whose default report times the host glibc against LibMem (LD_PRELOAD on one Google Benchmark binary, best of three runs with -bestperf) and prints throughput gain as (LibMem - glibc) / glibc in percent per size. The claim 'highly optimized for AMD Zen' is AMD's own and carries no hardware, compiler or numbers.

## Use it when

- Linux on AMD EPYC or Ryzen (Zen1 to Zen6) where profiles show memcpy/memmove/memset or str\* time and you can test an LD_PRELOAD swap without rebuilding the application.
- Fleet or HPC deployments already on the AOCL stack (AOCC, AOCL-BLIS, etc.) that want a matching libc string layer, built natively per node type or with IFUNC dispatch for mixed Zen fleets.
- Copy-heavy workloads in the multi-KB to multi-MB range where Zen-specific rep-movsb and non-temporal thresholds can matter more than glibc's generic tunables.
- When you are prepared to measure: the repo ships a harness (Google Benchmark hot/cold, tinymembench, FleetBench, DCPerf) that prints per-size throughput gain over the host glibc.

## Skip it when

- When you need published evidence: AMD gives no numbers in the README, User_Guide.md or benchmark_guide.md, so any gain over glibc must be measured on your own hardware.
- Intel or non-x86 machines: the library is tuned and documented for Zen only; Linux only; an AVX-512 build crashes with illegal instructions on CPUs without AVX-512 (and the user guide warns behaviour is undefined if AVX-512 is disabled in BIOS on Zen4+).
- Programs that hand a large memcpy result to another thread through a plain flag store: the Zen4 and AVX2 kernels stream non-temporal stores without a trailing sfence (see gotchas).
- Builds that must run under strict memory checkers without extra configuration: the default build reads past the requested length inside the same page for small sizes; use ALMEM_STRICT_BOUNDS=Y for masked loads.
- Portable binaries across glibc versions: a library built on glibc 2.34 or newer will not resolve its dlopen/dlsym symbols on older glibc.

## How it is fast

Size-tiered vector kernels: overlapping head/tail ZMM or YMM loads and stores for small sizes (up to 512 B on Zen4), then a destination-aligned 4- or 8-vector loop with software prefetch, rep movsb (ERMS) in a middle band on the AVX-512 optimised path, and non-temporal streaming stores above a threshold derived at load time from CPUID cache sizes (L2 per core, L3 per CCX). Per-microarchitecture variants (src/uarch/zen1..zen6) choose between these tiers and thresholds for each Zen generation, much like glibc's memmove-vec-unaligned-erms but with AMD-specific cut-offs.

## Compared with alternatives

Pick it over asmlib (generic x86, numbers from glibc 2.7/2.8 era) or DPDK rte_memcpy (inline memcpy for small cached copies only) when you run Linux on AMD Zen and want a maintained, symbol-compatible LD_PRELOAD replacement for the whole mem\*/str\* set with per-Zen thresholds; Arm Optimized Routines is the counterpart for Arm and is not an alternative on x86.

## Integration

| | |
|---|---|
| **Form** | shared lib (libaocl-libmem.so via LD_PRELOAD) or static lib (libaocl-libmem.a linked before libc) |
| **Dependencies** | none at run time beyond glibc (2.34+ for the dynamic dispatcher build); building needs CMake 3.22 and GCC or AOCC; the benchmark tool needs Python 3.10+, numpy, pandas and Bazel below 8.0.0 for FleetBench |
| **Minimum toolchain** | C99, CMake 3.22; GCC 14.1 for znver5 (newer GCC for znver6) or AOCC 5.0; IFUNC dispatch needs a recent toolchain |
| **Platforms** | Linux x86-64 on AMD Zen1-Zen6; AVX2 or AVX-512 builds (AVX-512 build requires AVX-512 hardware) |
| **Thread safety** | Not documented; the functions keep no mutable state after the load-time constructor sets thresholds and cache sizes (read in source) |
| **Drop-in for the baseline** | partial — symbol-compatible drop-in for the 17 listed functions (plus strrchr in source) via LD_PRELOAD or static linking; every other libc function stays glibc's, and tunable variants such as LIBMEM_OPERATION=erms,w,w or avx2,y,y can corrupt data or crash on lengths or alignments they do not support |

## Gotchas

- Missing store fence (read in source, not reported in issues): src/uarch/zen4/memcpy_impl_zen4.c and src/isa/avx2/optimized/memcpy_avx2.c (the Zen3 variant) switch to non-temporal streaming stores at or above __nt_start_threshold and return without an sfence, while the AVX-512 optimised path (Zen5) issues ALM_STORE_FENCE() after its streaming loop and glibc does the same; NT stores are weakly ordered on x86, so a later plain store (e.g. a release flag) can become visible before the copied data.
- CPU detection bug: RDSEED is tested in CPUID leaf 7 ECX bit 18 (src/cpu_features.c and the IFUNC resolver in src/libmem_ifunc_dispatcher.c) instead of EBX bit 18, so a dynamic-dispatch build on Zen1 (no RDPID, no VPCLMULQDQ) falls through to the generic 'system' variant instead of the zen1 kernels; GCC 16+ builds avoid it by using __builtin_cpu_is.
- Vendor gating is inconsistent: the constructor computes cache sizes and thresholds only on AuthenticAMD, but the GCC&lt;16 IFUNC resolver has no vendor check, so on Intel CPUs with AVX-512 it selects zen4/zen5/zen6 kernels running with unset (0 and 0xffffffff) cache sizes and thresholds.
- Harness asymmetry in the shipped benchmark: with -preload n the LibMem binary links libaocl-libmem.a statically while the 'glibc' binary is still dynamically linked to libc (only -static-libgcc -static-libstdc++), so glibc pays PLT/IFUNC call overhead the LibMem arm does not; the default -preload y runs one binary both ways and is the fair mode. Both GBM drivers (gbm.py behind the documented bench.py, and new_gbm.py behind the redesigned benchmark.py) share that asymmetry; gbm.py also compiles the benchmark with no -O flag, new_gbm.py with -O3. README's note that ALMEM_ARCH selects AVX2/AVX512 is stale: BUILD_RUN.md and CMake use ALMEM_ISA for that and ALMEM_ARCH for zen1..zen6.

## Known shortcomings

- Bench framework (glibc vs LibMem) exists but the repo publishes no numbers; amd.com blocked; no AMD figure found.
- Enricher: still no published numbers; Zen4 memcpy_impl_zen4.c and the AVX2 memcpy_avx2.c (Zen3 variant) use non-temporal stores with no trailing sfence (the Zen5 AVX-512 path has one); RDSEED is tested in CPUID leaf 7 ECX bit 18 instead of EBX bit 18, so Zen1 dynamic dispatch falls back to 'system'; the GCC&lt;16 IFUNC resolver has no vendor check; the benchmark's static mode (-preload n) links LibMem statically but glibc dynamically (default -preload y is fair); the README ALMEM_ARCH note is stale (ALMEM_ISA selects avx2/avx512).

## Caveats and trade-offs

Tier D: no published numbers in the README, tools/benchmark/benchmark_guide.md or docs/User_Guide.md; amd.com was unreachable here (DNS failure) and a web search found no AMD-published percentage. The benchmark tool (bench.py, default '-perf d' Glibc vs LibMem report) makes the claim checkable on Zen hardware. Default build uses page-boundary-safe unmasked over-reads for small sizes (ALMEM_STRICT_BOUNDS=Y gives a masked strict-bounds variant); an AVX-512 build crashes on non-AVX-512 CPUs; IFUNC needs recent toolchains; binaries built against glibc 2.34+ need glibc 2.34+ at run time. LICENSE.txt: BSD-3-Clause for AMD code, bundled tinymembench is MIT.

Tuned for AMD Zen and Linux only; loading the AVX512 build on a CPU without AVX-512 crashes; small sizes use page-boundary-safe unmasked vector loads like glibc, with an ALMEM_STRICT_BOUNDS=Y masked-load variant; IFUNC and glibc 2.34+ dlopen symbol caveats; includes third-party tinymembench (MIT).

## Maintenance

Maintained by AMD as part of AOCL (one squashed commit per release, 4.2 through 5.3.2 on 2026-08-20, 1 open issue, no GitHub releases or tags), BSD-3-Clause with bundled MIT tinymembench, small enough to vendor, but evidence is tier D until someone publishes runs of the shipped harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** tools/benchmark/benchmark_guide.md describes a bench.py framework (TinyMemBench, Google Benchmark hot/cold, FleetBench v0.2/v0.3.3/latest, DCPerf) whose default report is 'Glibc vs. LibMem' throughput gain in percent, but no result is published in the README, benchmark guide or docs/User_Guide.md; one web search found no AMD-published percentage either. No numbers, so D.
- **Verifier notes:** Accurate record; tier D because AMD publishes no numbers in the repo. Keep as AMD's official Zen-tuned libc string/memory replacement (notable despite 38 stars); shortcoming: no published measurements, claims must be reproduced with the shipped bench.py on Zen hardware.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-29 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/tools/benchmark/benchmark_guide.md>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/README.md>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/docs/User_Guide.md>
  - <https://github.com/amd/aocl-libmem>
  - <https://github.com/amd/aocl-libmem/commits>
- **Sources the enricher read:**
  - <https://github.com/amd/aocl-libmem>
  - <https://github.com/amd/aocl-libmem/commits/main>
  - <https://github.com/amd/aocl-libmem/issues?q=is%3Aissue>
  - <https://github.com/amd/aocl-libmem/issues/2>
  - <https://github.com/amd/aocl-libmem/tree/main/src>
  - <https://github.com/amd/aocl-libmem/tree/main/src/uarch>
  - <https://github.com/amd/aocl-libmem/tree/main/src/uarch/zen4>
  - <https://github.com/amd/aocl-libmem/tree/main/src/isa>
  - <https://github.com/amd/aocl-libmem/tree/main/src/base_impls>
  - <https://github.com/amd/aocl-libmem/tree/main/tools/benchmark>
  - <https://github.com/amd/aocl-libmem/tree/main/tools/benchmark/src>
  - <https://github.com/amd/aocl-libmem/tree/main/tools/benchmark/scripts>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/README.md>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/BUILD_RUN.md>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/docs/User_Guide.md>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/tools/benchmark/benchmark_guide.md>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/libmem.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/libmem_iface.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/libmem_dispatcher.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/libmem_ifunc_dispatcher.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/cpu_features.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/cache_info.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/threshold.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/include/zen_cpu_info.h>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/include/almem_defs.h>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/base_impls/load_store_impls.h>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/base_impls/load_store_avx512_impls.h>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/uarch/zen4/memcpy_impl_zen4.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/uarch/zen4/memcpy_zen4.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/uarch/zen4/memmove_zen4.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/uarch/zen4/memset_zen4.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/uarch/zen4/strlen_zen4.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/uarch/zen4/strstr_zen4.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/uarch/zen5/memcpy_zen5.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/uarch/zen3/memcpy_zen3.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/isa/avx512/optimized/memcpy_impl_avx512.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/src/isa/avx2/optimized/memcpy_avx2.c>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/tools/benchmark/scripts/bench.py>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/tools/benchmark/scripts/gbm.py>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/tools/benchmark/scripts/benchmark.py>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/tools/benchmark/scripts/get_parser.py>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/tools/benchmark/src/gbench_main.cpp>
  - <https://raw.githubusercontent.com/amd/aocl-libmem/HEAD/tools/benchmark/scripts/new_gbm.py>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/amd/aocl-libmem`) · [data/wave13/enrich/raw/github_com_amd_aocl_libmem.json](../../../data/wave13/enrich/raw/github_com_amd_aocl_libmem.json) (enrichment confidence 0.75)

</details>
