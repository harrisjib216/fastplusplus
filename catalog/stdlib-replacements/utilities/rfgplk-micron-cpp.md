# micron.cpp (cmemory memcpy/memset/memmove)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Utilities](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only inline memcpy/memset/memmove from the freestanding micron libc/STL rewrite; 1.13-1.91x fewer cycles than glibc on SPEC2017-size random copies.

| | |
|---|---|
| **Beats** | glibc memcpy / memset / memmove (system libc, called as ::memcpy in the harness; glibc version not stated) |
| **Claimed result** | benches/results/mem_random_s2_final.csv cycles/byte micron vs libc: memcpy 0.2803 vs 0.3480 at 32768 (1.24x, derived from page data), 0.2590 vs 0.3815 at 262144 (1.47x, derived), 0.3045 vs 0.4829 at 1048576 (1.59x, derived); memset 0.2377 vs 0.4532 at 1048576 (1.91x, derived), 0.1936 vs 0.2190 at 32768 (1.13x, derived); memmove 0.3236 vs 0.4231 at 1048576 (1.31x, derived). micron is faster in all 18 rows of that file. |
| **Workload** | benches/memory_random_bench.cpp: batches of 16384 random-offset operations with SPEC2017 size and alignment distributions over a working set of 32 KiB to 1 MiB, 5 measurements, CPU pinned, cycles per byte; micron mc::memcpy/memset/memmove versus libc. |
| **Metric** | throughput |
| **Hardware** | Not stated in the CSV. Sibling result files name an Intel Core i7-5960X (Haswell-E, 8C/16T, 20 MiB L3), Linux 7.1.9-200.fc44 (Fedora 44), CPU pinned. |
| **Compiler and flags** | Not stated in the CSV. Sibling result files from the same author and dates (abcmalloc_core_baseline.csv, rng_final_native.csv) state GCC 16.2.1 20260819, -O3 -march=native, built with 'duck --perf --fp --no-ssp --no-lto -i .'. The bench source adds #pragma GCC optimize(-fno-tree-loop-distribute-patterns). |
| **Adoption** | 13 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/rfgplk/micron.cpp) · [benchmark](https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/mem_random_s2_final.csv) |

## Verdict

On an Intel i7-5960X (Haswell-E, 20 MiB L3; CPU and the GCC 16.2.1 -O3 -march=native build are named only in sibling result files), with CPU 0 pinned and median of 5 batches of 16384 SPEC2017-distributed random copies, micron used 0.2803 vs 0.3480 cycles/byte for memcpy at 32 KiB and 0.3045 vs 0.4829 at 1 MiB (1.24x and 1.59x), 0.2377 vs 0.4532 for zero memset at 1 MiB (1.91x) and 0.3236 vs 0.4231 for memmove at 1 MiB (1.31x) against glibc of unstated version (ratios derived from page data). The same author's fixed-size detail runs show glibc faster overall for hot memcpy (geomean 0.96) and memmove (0.89) and for every cold memcpy cell.

## Use it when

- Projects already built on micron, or freestanding/no-libc Linux binaries that need fast mem\* routines without glibc.
- Hot loops issuing many small variable-size copies (the SPEC2017 mix: mean 104 bytes, 77% of calls at 32 bytes or less) over working sets of 32 KiB to 1 MiB, where inlining the size ladder removes per-call overhead.
- Zero-filling buffers in cache-resident working sets: memset of zero won 1.13x at 32 KiB to 1.91x at 1 MiB in the random-size run and 222 of 386 hot cells in the detail run.
- x86-64 Linux builds with -march=native on AVX2-class cores (results come from a Haswell-E i7-5960X).

## Skip it when

- Cold-cache or streaming copies: glibc won all 14 cold memcpy cells (geomean libc/micron 0.85) and 11 of 14 cold memset cells in the author's detail file.
- Tiny memmoves and non-zero memset: glibc took 3-byte memmove at 0.27 vs 1.12 cycles/byte and won 29 of 50 hot memset cells with fill byte 0x5A.
- Hosted programs wanting a global ::memcpy replacement: the C-ABI symbols exist only in freestanding builds, and the mc:: API has different semantics.
- Non-Linux targets or code that needs a stable ABI: Linux is the only supported OS, aarch64 and i386 are 'compiles, untested', and the README says the ABI may change without notice and that performance takes precedence over safety.
- Teams needing an independently reviewed routine: 13 stars, one author, no external measurements, and evidence only from a single Haswell-E machine with an unstated glibc version.

## How it is fast

Copies up to 256 bytes (128 without AVX2) go through an always_inline size ladder that loads the head and tail with overlapping 2/4/8/16/32-byte moves and issues all loads before any store, the same unaligned head/tail technique glibc's memmove-vec-unaligned-erms uses, so memmove shares the code. Larger sizes go to a noinline tier chosen from a one-time CPUID probe: a vector loop below the rep threshold, rep movsb from 2112 bytes (FSRM) or 8192 bytes (ERMS), and non-temporal stores above max(L3/4, 1 MiB). Because the ladder is inlined into the caller, small variable-size copies avoid the out-of-line call, PLT jump and ifunc-selected entry that ::memcpy pays.

## Compared with alternatives

no siblings catalogued yet

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none outside the repo, but cmemory pulls micron's types, type_traits, attributes and simd headers; hosted builds link glibc/pthread by default |
| **Minimum toolchain** | C++23 (GCC or Clang through duck's flag profiles; the benchmark files cite GCC 16.2.1; duck itself is bootstrapped with -std=c++26) |
| **Platforms** | Linux only; x86-64 (SSE2 floor, AVX2 and AVX-512 tiers via -march), armv7-a; aarch64 and i386 compile but are untested |
| **Thread safety** | Routines are stateless; the one-time CPUID tunables probe is guarded by an atomic compare-and-swap in __mem_tun_get (hosted) or run from _start (freestanding). |
| **Drop-in for the baseline** | partial: mc::memcpy/mc::memmove take typed pointers and an element count, mc::memset a byte count; C-ABI memcpy/memmove/memset replacements are generated only in freestanding (-k) builds |

## Gotchas

- Harness asymmetry behind the numbers: benches/memory_random_bench.cpp inlines mc::memcpy/memset/memmove into the timed loop, while ::memcpy is an out-of-line glibc call through the PLT. At 32 KiB the memcpy gap is about 7 cycles per call (0.0677 cycles/byte x 104-byte mean size, derived from page data), roughly the cost of that call, so part of the 1.24-1.59x reflects call elimination rather than a faster copy loop. memset_rand fills only zero, the one fill value where micron wins in its own detail file.
- The random benchmark never compares micron's output with libc's. The repo's tests/memory/mem_exhaustive_small.cpp (0-300 bytes at every offset, with sentinel guards) and mem_overlap_exhaustive.cpp (overlaps up to 1 MiB against a shadow buffer) do check correctness.
- The cited CSV does not record its build. The 'libc' label holds only for duck's hosted default; in a freestanding -k build, cmemory/memcpy.hpp defines extern "C" memcpy on top of micron's own __memcpy_bytes, so ::memcpy would no longer be glibc.
- mc::memcpy and mc::memmove convert element by element with static_cast when sizeof(F) != sizeof(D) or a type is not trivially copyable, so they do not always copy bytes; their count is in elements of the source type, while mc::memset counts bytes.

## Known shortcomings

- Tier C: 18 CSV rows match; libc wins hot memcpy and memmove, all cold memcpy and tiny sizes, so the 1.1-1.9x win holds only for 32 KiB-1 MiB random sizes (stable across 9 runs); CSV lacks compiler and CPU, glibc version unstated, harness never checks output. abcmalloc MIT, the rest BSL-1.0.
- Enricher: mc:: routines are always_inline into the timed loop while ::memcpy is an out-of-line PLT call; the gap at 32 KiB is about 7 cycles per call (mean 104 B, derived), roughly the call cost; memset_rand fills zero only, micron's one winning fill value; the CSV has no build line, and under the freestanding -k build ::memcpy binds micron's own extern "C" memcpy, not glibc. mc::memcpy counts elements and static_casts when sizes differ while memset counts bytes; C-ABI symbols freestanding only; Linux only; unstable ABI; 13 stars. No correctness bug (exhaustive small and overlap tests exist).

## Caveats and trade-offs

The README and docs publish no numbers; the 'must demonstrate superior performance' line is a design principle. Only the benches/results directory has data, and the only micron-versus-external-baseline rows found are memory primitives against glibc, not the allocator or STL containers named in the seed guess (allocator results are before/after against micron's own earlier revisions, and sort_bench_std.cpp, heap_bench_std.cpp and stack_bench_std.cpp have no recorded results). The claim is selective: the sibling file mem_detail_s2_final_a.csv (same author) shows libc faster overall for hot memcpy (micron wins 170 of 513 cells, geomean libc/micron cycles 0.96) and hot memmove (45 of 182, 0.89), faster on all 14 cold-cache memcpy cells (0.85) and on 11 of 14 cold memset cells, with libc far ahead at tiny sizes (for example memmove at 3 bytes 0.27 vs 1.12 cycles/byte); micron wins hot memset of zero (222 of 386, geomean 1.12) but not memset of 0x5A (21 of 50, 0.98); mem_detail_s2_final_b.csv gives the same picture. The random-size win applies to working sets of 32 KiB to 1 MiB only (all cache-resident on the 20 MiB L3) and is stable across the nine mem_random_\*.csv runs (memcpy 1.36x to 1.64x at 256 KiB to 1 MiB), but the earliest mem_random_baseline.csv had libc faster at 32 KiB for all three ops. The harness subtracts a no-op batch, measures micron immediately before libc in each cell and does not check that the micron output equals the libc output. First-party, single machine (Haswell-E, an older CPU than glibc's newest ifunc tuning targets), glibc version unstated, compiler and CPU absent from the cited CSV, so tier C. Ratios are derived from page data. The abcmalloc component is MIT-licensed; the rest is BSL-1.0. [retier] First-party CSV (no compiler, CPU, glibc version or build line; output unchecked): win of 1.1-1.9x only at 32 KiB-1 MiB random sizes; libc wins hot memcpy/memmove, all cold memcpy and tiny sizes. mc:: routines inline into the timed loop while ::memcpy is a PLT call (gap about 7 cycles per call at 32 KiB, derived); memset_rand fills zero only; freestanding -k build binds ::memcpy to micron's own memcpy. Linux only, unstable ABI, 13 stars; abcmalloc MIT, rest BSL-1.0.

Freestanding re-implementation of libc and the C++ standard library (no libc dependency, C++23 or C++26, x86-64 focus with an ARM32 and bare-metal branch); README states the ABI may change without notice, performance takes precedence over safety, and the code is not a drop-in for the STL ABI. abcmalloc, the bundled allocator, is MIT while the rest is BSL-1.0.

## Maintenance

Very active (last commit 2026-10-03, 407 commits) but a 13-star single-author project with no issue tracker activity and an explicitly unstable ABI; BSL-1.0 (abcmalloc MIT), so the cmemory headers can be vendored with their small simd/types dependencies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party CSV (benches/results/mem_random_s2_final.csv) from public harness code (benches/memory_random_bench.cpp) comparing mc::memcpy/memset/memmove with ::memcpy/::memset/::memmove; all 18 rows and every derived ratio match, but the CSV states neither compiler, flags nor CPU (those appear only in sibling result files for other benchmarks) and the glibc version is unstated, so C.
- **Retiered** C to D: The only numbers compare always_inline mc:: routines against an out-of-line PLT ::memcpy, the measured gap at 32 KiB is about the call cost, memset was timed with the single fill value micron wins on, and under the documented freestanding build ::memcpy binds micron's own symbol rather than glibc; with no build line in the CSV the comparison cannot be trusted (crippled-baseline precedent). Directional only.
- **Verifier notes:** Numbers verified exactly; the selective-win caveats (detail CSV counts and geomeans) were recomputed and match file a. No correctness bug found, but the harness never compares outputs, so a wrong-result fast path cannot be ruled out from the bench alone.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-67 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/mem_random_s2_final.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/memory_random_bench.cpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/mem_detail_s2_final_a.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/mem_detail_s2_final_b.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/abcmalloc_core_baseline.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/rng_final_native.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/cmemory_counters_final.txt>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/mem_random_s2_base.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/mem_random_baseline.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/mem_random_s2_e24.csv>
  - <https://github.com/rfgplk/micron.cpp>
  - <https://github.com/rfgplk/micron.cpp/commits/master>
  - <https://github.com/rfgplk/micron.cpp/tree/master/benches/results>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/README.md>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/memory_random_bench.cpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/mem_random_s2_final.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/mem_detail_s2_final_a.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/cmemory_counters_final.txt>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/abcmalloc_core_baseline.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/benches/results/rng_final_native.csv>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/src/memory/cmemory/memcpy.hpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/src/memory/cmemory/memmove.hpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/src/memory/cmemory/memset.hpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/src/memory/cmemory/bits.hpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/src/memory/cmemory/__unroll_memcpy.hpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/src/memory/cmemory/__unroll_memset.hpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/src/config.hpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/start/start.cpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/start/NOTES.md>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/tools/src/main.cc>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/tools/src/commands.hh>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/tools/src/recipe.hh>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/tools/src/recipes/gnu/config.hh>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/tests/memory/mem_overlap_exhaustive.cpp>
  - <https://raw.githubusercontent.com/rfgplk/micron.cpp/master/tests/memory/mem_exhaustive_small.cpp>
  - <https://github.com/rfgplk/micron.cpp>
  - <https://github.com/rfgplk/micron.cpp/issues?q=is%3Aissue>
  - <https://github.com/rfgplk/micron.cpp/commits/master>
  - <https://github.com/rfgplk/micron.cpp/tree/master/src/memory/cmemory>
  - <https://github.com/rfgplk/micron.cpp/tree/master/start>
  - <https://github.com/rfgplk/micron.cpp/tree/master/tools/src>
  - <https://github.com/rfgplk/micron.cpp/tree/master/tests>
  - <https://github.com/rfgplk/micron.cpp/tree/master/tests/memory>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/rfgplk/micron.cpp`) · [data/wave1/enrich/raw/github_com_rfgplk_micron_cpp.json](../../../data/wave1/enrich/raw/github_com_rfgplk_micron_cpp.json) (enrichment confidence 0.7)

</details>
