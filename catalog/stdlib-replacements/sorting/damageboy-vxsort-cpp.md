# vxsort-cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> AVX2/AVX-512 vectorized quicksort for primitive arrays; beats a ported .NET GC introsort, not std::sort.

| | |
|---|---|
| **Beats** | scalar introsort ported from the .NET CoreCLR GC (gcsort::introsort_orig), not std::sort |
| **Claimed result** | The README compares against 'Introspective Sort (Scalar Baseline)', which is a port of the .NET CoreCLR GC introsort sorting 64-bit pointers, not std::sort. It reports roughly 4.8x at 1M int64 with 8x unroll (55ns -&gt; 11.5ns per element; the table gives 53.08ns vs 11.54ns, \~4.6x) and \~4.5x at 128K int64 (45ns -&gt; 10.5ns). No std::sort numbers are published, and the int32 results have no baseline numbers. |
| **Workload** | Single-core sorting of 4,096 to 1,048,576 elements. For int64, vxsort (AVX2, unroll 1/4/8/12) is compared against a scalar introsort on 64-bit pointer arrays. The int32 tables cover vxsort only (unroll 1/4/8), with no baseline. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3950X @ 3.8GHz |
| **Compiler and flags** | Compiler/version not stated (README recommends clang). CMakeLists defaults to a Release build. At the June 2020 commit behind the published results, Release flags for GCC/Clang were '-Ofast -DNDEBUG'; current master uses '-O2 -fomit-frame-pointer -DNDEBUG'. |
| **Adoption** | 33 stars |
| **Last commit** | 2023-05-10 |
| **Links** | [repository](https://github.com/damageboy/vxsort-cpp) · [benchmark](https://github.com/damageboy/vxsort-cpp#results-ryzen-3950x-38ghz) |

## Verdict

The README's reported \~4.5-4.8x speedup (e.g., 1M int64: 53.08ns/elt scalar vs 11.54ns/elt with 8x unroll; measured on an AMD Ryzen 9 3950X @3.8GHz in a June 2020 benchmark) is against gcsort::introsort_orig, a scalar port of the .NET CoreCLR GC's introsort — not std::sort. No compiler version is stated, and no std::sort numbers are published even though the current repo contains a BM_fullsort.stdsort.cpp benchmark file.

## Use it when

- Sorting large arrays (benchmarked 4,096 to 1,048,576 elements) of raw i16/u16/i32/u32/i64/u64/f32/f64 on x86-64 with AVX2 or AVX-512 available
- Throughput-bound batch sorts where you can pick the ISA/unroll variant at compile time and don't need a comparator or non-primitive keys
- You want per-element latency down for pointer-sized keys (README: int64 drops from \~53ns/elt scalar introsort to \~11.5ns/elt with unroll x8, unverified against std::sort)
- You're OK vendoring a small, currently unmaintained C++ codebase (MIT) and rebuilding it for your target ISA

## Skip it when

- Need a drop-in std::sort replacement with comparators, custom types, or non-x86 targets — no comparator API, and NEON/AArch64 support is stubbed (issue #1, open since 2020) but not implemented
- Need std::sort-relative numbers to justify the switch — README only compares against a self-ported CoreCLR-GC scalar introsort, not std::sort, and no std::sort numbers are published despite a BM_fullsort.stdsort.cpp benchmark existing in the repo
- Care about active maintenance — the default branch's last commit is 2023-05-10; only an unrelated-history 'nextgen' branch has recent (2026) activity
- Small arrays under 4K elements (not benchmarked) or workloads needing a stable sort — this is in-place but not stable, and uses a fixed-size internal scratch buffer sized per template instantiation
- Want CI confidence out of the box — an open 'Build fail' issue (#2) shows the bench/test build breaking against a newer clang/CMake/googlebenchmark combination

## How it is fast

Branchless AVX2/AVX-512 vectorized partitioning (the 'partition machine') replaces std::sort's scalar Hoare partition, falling back to an in-register bitonic sorting network for blocks under 1024 elements instead of insertion sort. A depth-limited heap-sort fallback guards worst-case recursion, and an Unroll template parameter (1-12) controls how many vector lanes are processed per partitioning step, trading code size for fewer loop-carried dependencies.

## Compared with alternatives

Pick this only if you specifically want an AVX2/AVX-512 partition-plus-bitonic-network vectorized quicksort port of .NET's VxSort for raw numeric arrays and don't need comparator/generic-type support; x86-simd-sort, BlockQuicksort, quadsort, and fluxsort all publish real std::sort or std::stable_sort comparisons and are more actively maintained, so prefer one of them when the baseline claim matters or adoption/maintenance risk is a concern.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | cpu_features (Google, ISA detection), fmt; googlebenchmark and googletest additionally for bench/tests only |
| **Minimum toolchain** | C++20 (CMakeLists sets CMAKE_CXX_STANDARD 20), CMake 3.24+; clang recommended by the README, GCC also handled in CMakeLists |
| **Platforms** | x86-64 with AVX2 or AVX-512 (ISA chosen per template instantiation at compile time); AArch64/NEON detection is present in demo.cpp but the sort call is unimplemented |
| **Thread safety** | not documented; each vxsort&lt;&gt; instance owns a fixed-size internal scratch buffer (_spill), so sharing one instance across threads is not evidently safe |
| **Drop-in for the baseline** | partial — explain: same job (sort a pointer range in place) but a different call convention: a template class parameterized by type, ISA, and unroll factor, invoked as sorter.sort(begin, end) rather than a generic std::sort(first, last, comp) with iterator/comparator flexibility |

## Gotchas

- ISA is selected at compile time via which header you include (vxsort.avx2.h vs vxsort.avx512.h) and the vxsort_targets_enable_\*.h wrapper; using the wrong one for the running CPU is a caller error (the demo does its own cpu_features runtime check before choosing)
- Only built-in numeric types appear in the benchmark/test suite (i16/u16/i32/u32/f32/i64/u64/f64); no evidence of support for arbitrary structs, strings, or custom comparators
- Internally falls back to heap_sort past a depth limit and to a bitonic-network small-sort under 1024 elements — behavior isn't a single flat algorithm the way std::sort's introsort is, though this is invisible at the call site
- Open issue #2 shows the benchmark/test build breaking under newer clang/CMake due to a googlebenchmark C-dialect flag mismatch — unrelated to the sort code but relevant if you try to reproduce the published numbers

## Caveats and trade-offs

The published baseline is not std::sort. It is gcsort::introsort_orig, a scalar port of the .NET CoreCLR GC introsort, from the 2020 code (bench/BM_fullsort.int64_t.cpp at ec12899). Current master has bench/fullsort/BM_fullsort.stdsort.cpp, which calls std::sort, but no std::sort results are published. The README results date from 2020 and no longer match the current benchmark code. The compiler version is not stated. The Ryzen 3950X (Zen 2) has no AVX-512, so the published numbers are AVX2 only. The default branch was last committed on 2023-05-10. Recent activity (2026-06-12) is on an unrelated-history 'nextgen' branch.

Requires AVX2/AVX-512 x86 hardware; C++ port of the original C# VxSort library, described by its own author as an experimental/rough reimplementation; low adoption relative to other SIMD sorts in this list.

## Maintenance

Abandoned on its default branch since 2023-05-10 (later activity moved to an unrelated-history 'nextgen' branch); MIT-licensed and small/self-contained enough to vendor, but only 33 stars and an open build-fail issue against its bench/test harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README numbers (hardware: Ryzen 3950X) come from the June 2020 benchmark bench/BM_fullsort.int64_t.cpp at commit ec12899. That code compares against gcsort::introsort_orig, a scalar port of the .NET CoreCLR GC introsort, not std::sort. The compiler and version are not stated, and that benchmark and baseline are no longer in master. Numbers without a reproducible run against the named baseline put this at C.
- **Verifier notes:** The page numbers match, but the baseline is misattributed: README results compare against a CoreCLR-GC introsort port, not std::sort. I kept the entry because the repo does have std::sort benchmark code and the introsort is a real incumbent (the .NET GC). The orchestrator should set baseline_in_list=false or seek std::sort numbers. The record's last_commit 2026-06-12 was the repo pushed_at from the orphan 'nextgen' branch (no common ancestor with master). The master branch's last commit is 2023-05-10, so the status is 'abandoned' under the &gt;3-year rule, though the author is still active on nextgen. The earlier caveat that CMake does not pin Release is wrong, because CMakeLists defaults CMAKE_BUILD_TYPE to Release. MIT license and 33 stars are confirmed. [orchestrator: baseline_in_list=false, baseline outside category list]
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compared_against_cpp_std_directly`, `compiler_and_flags`, `workload`, `last_commit`, `maintenance_status`, `caveats`, `baseline_in_list`
- **Pages the verifier opened:**
  - <https://github.com/damageboy/vxsort-cpp>
  - <https://github.com/damageboy/vxsort-cpp#results-ryzen-3950x-38ghz>
  - <https://github.com/damageboy/vxsort-cpp/blob/master/bench/fullsort/BM_fullsort.stdsort.cpp>
  - <https://github.com/damageboy/vxsort-cpp/blob/master/CMakeLists.txt>
  - <https://github.com/damageboy/vxsort-cpp/blob/ec12899a49a0d4cd0a91ebe4885a1544bd19970f/bench/BM_fullsort.int64_t.cpp>
  - <https://github.com/damageboy/vxsort-cpp/blob/ec12899a49a0d4cd0a91ebe4885a1544bd19970f/bench/BM_fullsort.h>
  - <https://github.com/damageboy/vxsort-cpp/blob/ec12899a49a0d4cd0a91ebe4885a1544bd19970f/gcsort/introsort_orig.h>
  - <https://github.com/damageboy/vxsort-cpp/blob/ec12899a49a0d4cd0a91ebe4885a1544bd19970f/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/damageboy/vxsort-cpp>
  - <https://github.com/damageboy/vxsort-cpp#results-ryzen-3950x-38ghz>
  - <https://github.com/damageboy/vxsort-cpp/tree/master>
  - <https://github.com/damageboy/vxsort-cpp/blob/master/vxsort/vxsort.h>
  - <https://github.com/damageboy/vxsort-cpp/blob/master/CMakeLists.txt>
  - <https://github.com/damageboy/vxsort-cpp/blob/master/vxsort/CMakeLists.txt>
  - <https://github.com/damageboy/vxsort-cpp/blob/master/demo/demo.cpp>
  - <https://github.com/damageboy/vxsort-cpp/blob/master/demo/do_avx2.cpp>
  - <https://github.com/damageboy/vxsort-cpp/blob/master/bench/fullsort/BM_fullsort.stdsort.cpp>
  - <https://github.com/damageboy/vxsort-cpp/issues>
  - <https://github.com/damageboy/vxsort-cpp/issues/2>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/damageboy/vxsort-cpp`) · [data/wave1/enrich/raw/github_com_damageboy_vxsort_cpp.json](../../../data/wave1/enrich/raw/github_com_damageboy_vxsort_cpp.json) (enrichment confidence 0.5)

</details>
