# SAXPY function multiversioning with per-ISA builds and CPUID dispatch (The C++ Programmer's Mindset, ch. 4)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Book sample: one scalar saxpy loop compiled per ISA (SSE4.2, AVX2, AVX-512F) with CPUID dispatch; 1.27-1.35x over default build.

| | |
|---|---|
| **Beats** | default-target build of the same scalar saxpy loop (saxpy_default, x86-64 SSE2 baseline, no runtime dispatch); OpenBLAS cblas_saxpy measured as a reference |
| **Claimed result** | Vector size 5120: default 329 ns, sse4.2 330 ns, hand-crafted AVX2 298 ns, avx2 259 ns, avx512f 243 ns; OpenBLAS saxpy 278 ns. avx512f build about 1.35x and avx2 build about 1.27x faster than the default build (derived); both slightly ahead of OpenBLAS (278/243 about 1.14x, 278/259 about 1.07x, derived). Book figures as paraphrased in the seed lead, not on the repo page. |
| **Workload** | y[i] += a\*x[i] over 5,120 floats (N = 5\*1024, x = 1.0, y = -1.0, a = 2.0), Google Benchmark time per call in ns, comparing the same scalar loop (saxpy.cpp.in) compiled for default, -msse4.2, -mavx2 and -mavx512f, a hand-written AVX2 intrinsics version (saxpy_hand.cpp) and cblas_saxpy. main() calls get_best_instructions() (CPUID) to decide which rows to register; the ct::saxpy dispatcher itself is not timed. |
| **Metric** | latency |
| **Hardware** | Not stated (an AVX-512 capable CPU is implied by the avx512f row). |
| **Compiler and flags** | Not stated; the lead implies GCC -O3. Chapter-04/CMakeLists.txt compiles saxpy.cpp.in once per ISA via configure_file with per-source -msse4.2 / -mavx2 / -mavx512f (or /arch: on MSVC) and saxpy_hand.cpp with -mavx2, but sets no CMAKE_BUILD_TYPE or -O level and the repo has no CMakePresets.json. 329 ns for 5,120 floats (about 0.064 ns per element) implies optimised, vectorised code, so the book's build used an optimisation level the repo does not set (derived). The repo does NOT use [[gnu::target_clones]] for this chapter-4 benchmark (Chapter-14/saxpy_mt.cpp does use target_clones("avx2,default")). |
| **Adoption** | 20 stars (Packt companion repository for the 2025 book) |
| **Last commit** | 2026-01-22 |
| **Links** | [repository](https://github.com/PacktPublishing/The-CPP-Programmers-Mindset) · [benchmark](https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/blob/main/Chapter-04/bench_saxpy.cpp) |

## Verdict

The repository holds code only; the book's run, relayed by the seed lead, times the same scalar loop on 5,120 floats at 329 ns (default x86-64 build), 330 ns (SSE4.2), 259 ns (AVX2), 243 ns (AVX-512F) and 298 ns for hand-written AVX2 intrinsics, against 278 ns for OpenBLAS cblas_saxpy, so the AVX-512F and AVX2 builds are about 1.35x and 1.27x faster than the default build and the hand intrinsics lose to the compiler. Compiler, optimisation level, OpenBLAS version and the AVX-512-capable CPU are not stated, and the CPUID dispatcher a real caller goes through is not timed.

## Use it when

- Shipping one x86-64 binary to a mixed fleet where a hot, simple, auto-vectorisable loop should use AVX2 or AVX-512 when present without raising the baseline ISA.
- When you want explicit control over which ISA tiers are built and how they are chosen, rather than GCC/Clang's [[gnu::target_clones]] (which the same repository uses in Chapter-14/saxpy_mt.cpp).
- Element-wise kernels with more arithmetic per byte than SAXPY, where wider vectors should pay off more than the 1.3x seen here (general expectation, not measured in the repository).
- Learning how per-ISA builds, CPUID feature bits and dispatch fit together before adopting target_clones or a SIMD library.

## Skip it when

- Calling ct::saxpy on small arrays in a hot path as written: the dispatcher calls get_best_instructions(), two or three CPUID instructions, on every call with no caching; CPUID is serialising and under virtualisation it normally traps to the hypervisor, which can rival the roughly 300 ns of work at N = 5,120 (derived; the dispatcher is never timed).
- Large, memory-resident arrays: SAXPY is bandwidth-bound, so wider vectors gain little once the data leave cache; only one cache-resident size (5,120 floats) is benchmarked.
- Non-x86 targets, MSVC or 32-bit builds: my_cpuid.h expands to static_assert(false) on non-x86 targets, tests __MSVC__ (MSVC defines _MSC_VER) so cl.exe gets no my_cpuid definition, and tests __X86__ rather than __i386__ so 32-bit GCC also hits the static_assert.
- Machines or VMs whose OS has not enabled AVX or AVX-512 register state: get_best_instructions() reads CPUID feature bits only, without the OSXSAVE/XGETBV check, so it can select a copy that faults.
- When you want BLAS-grade performance across sizes: the auto-vectorised copies edge out OpenBLAS only at this one small size, where call overhead weighs most.

## How it is fast

No new algorithm: the compiler auto-vectorises the same loop at a wider width when allowed a newer instruction set (4 floats per SSE register, 8 per AVX2, 16 per AVX-512), and run-time CPUID dispatch lets one binary use the widest copy the CPU supports while still running on baseline x86-64. The book's gains (1.27x for AVX2, 1.35x for AVX-512F over the SSE2 default) are far below the width ratios, consistent with SAXPY doing two loads and one store per multiply-add, so cache bandwidth rather than arithmetic sets the pace; the two 20 KB arrays (40 KB together) exceed a 32 KB L1 data cache (derived). SSE4.2 adds no float arithmetic over SSE2 for this loop, which matches its unchanged time.

## Compared with alternatives

Pick this pattern when a few simple loops already auto-vectorise and you only need ISA selection; xsimd or Vc give explicit SIMD types at the cost of rewriting the kernel, NumKong ships ready-made dispatched dot-product and distance kernels, and SLEEF or fmath cover transcendental functions that per-ISA recompilation alone does not speed up.

## Integration

| | |
|---|---|
| **Form** | source-drop (saxpy.cpp.in template, saxpy.h, the saxpy.cpp dispatcher, get_best_instructions.h, my_cpuid.h and the CMake configure_file loop that adds per-file -m flags) |
| **Dependencies** | none for the kernels; the benchmark needs Google Benchmark and optionally a BLAS with cblas.h (CMake asks for a static ILP64 BLAS via BLA_SIZEOF_INTEGER 8 and BLA_STATIC ON and silently drops the OpenBLAS row if none is found); the shared Chapter-04 project also requires GTest, Threads and OpenMP at configure time |
| **Minimum toolchain** | C++20 (std::span), CMake 3.30+, GCC or Clang targeting x86-64 (&lt;cpuid.h&gt;, -msse4.2/-mavx2/-mavx512f) |
| **Platforms** | x86-64 only, with GCC or Clang (clang-cl defines __clang__ and should work); plain MSVC cl.exe and 32-bit GCC do not compile my_cpuid.h as written; the AVX-512F tier needs an AVX-512F CPU |
| **Thread safety** | The kernels are stateless and safe on disjoint output spans; the dispatcher keeps no state (it re-queries CPUID on every call), so it is thread-safe but slow. |
| **Drop-in for the baseline** | partial: ct::saxpy has the same signature as saxpy_default and computes the same mul-then-add, but it needs the per-ISA CMake setup, and its per-call CPUID should be cached before it is worth calling on small arrays. |

## Gotchas

- Cache the dispatch: store the get_best_instructions() result once (a function-local static or a function pointer) or use target_clones/ifunc as Chapter-14 does; as shipped, every ct::saxpy call pays several CPUID instructions.
- -mavx2 does not imply -mfma, so the avx2 tier and saxpy_hand issue a separate multiply and add; -mavx2 -mfma (or -march=x86-64-v3) is the fairer AVX2 tier, and any tier that fuses the multiply-add can differ from the default build in the last bit.
- Neither the per-ISA loops nor saxpy_hand check that x is at least as long as y; only the dispatcher asserts it, and assert compiles away under NDEBUG, so a short x is read out of bounds.
- Chapter-04/CMakeLists.txt sets no CMAKE_BUILD_TYPE, so a plain configure builds without optimisation and none of the tiers vectorise; configure Release. Per-file -mavx2/-mavx512f flags also risk the linker keeping an AVX-compiled copy of an inline header function for the default path (a general hazard of per-file ISA flags, not observed in this repo). Open PR #14 (unmerged) fixes build errors in the chapter's gemm files, so build the bench_saxpy target alone if the full project fails.

## Known shortcomings

- Numbers are the book's; -O level unstated (329 ns implies vectorised code). The CPUID check has no OSXSAVE/XGETBV test, my_cpuid.h tests __MSVC__ instead of _MSC_VER, and the ct::saxpy dispatcher itself is never timed.
- Enricher: the dispatcher runs CPUID on every call (serialising, traps in VMs) and is never timed; -mavx2 without -mfma; CPUID header breaks plain MSVC and 32-bit GCC; no build type in CMake.

## Caveats and trade-offs

The numbers are the book's own figures as paraphrased in the seed lead; they are not printed anywhere in the repository (the Chapter-04 listing shows 23 source and build files and no results), and the book itself was deliberately not consulted. Single small size (20 KB per vector, cache resident); the book itself warns that OpenBLAS call overhead may distort this size. The gains (1.1-1.35x) come from compiler auto-vectorisation at a wider ISA, not from a new algorithm; the 'default' baseline is deliberately the lowest ISA tier, and its speed depends on the unstated -O level (GCC before 12 does not vectorise at -O2). The benchmark main() uses switch fall-through so a given CPU registers every lower tier too. get_best_instructions() checks only CPUID feature bits, not OSXSAVE/XGETBV, so the dispatcher can pick AVX/AVX-512 on an OS that has not enabled that register state; my_cpuid.h tests __MSVC__ rather than _MSC_VER, so its MSVC branch looks unreachable. CPU model, compiler and flags not stated. Tier C: first-party book measurement. [retier] Enricher: built with -mavx2 but without -mfma, so the AVX2 and hand-written versions do separate multiply and add. The kernels do not check x's length (only an assert in the dispatcher). The gain is well below the vector width because the 40 KB working set is cache-bandwidth-bound. CMake sets no build type (a plain build is unoptimised); open PR #14 fixes Chapter-04 build errors.

Several copies of the same loop plus a runtime CPUID dispatcher (my_cpuid.h, get_best_instructions.h); larger binary and an indirect dispatch per call, which dominates at small sizes. x86-only intrinsics and CPUID code. The SSE4.2 build matches the default build (330 versus 329 ns), probably because SSE2 already vectorises the loop.

## Maintenance

Packt book companion repository, MIT-licensed, 20 stars and 8 forks; the last commit (2026-01-22) changed only the README and the code last changed in November 2025, with one open issue (#15, about the clamp loop) and one unmerged build-fix PR (#14); the pattern is a handful of small files to copy, but fix the per-call CPUID and the compiler-macro checks first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter-04/bench_saxpy.cpp registers saxpy_default, saxpy_sse42, saxpy_avx2, saxpy_avx512f, saxpy_hand and (with BLAS) cblas_saxpy over N = 5\*1024 floats, so the code compares against the default-target build and OpenBLAS, but no results are in the repo; the ns figures come from the book via the seed lead, with compiler, flags and CPU unstated, so first-party tier C.
- **Verifier notes:** Code verified (per-ISA builds of one loop, fall-through registration, hand AVX2 version, cblas_saxpy reference, N = 5120); numbers not in the repo (book-only). Chapter-14 target_clones claim confirmed. MIT, 20 stars, last commit 2026-01-22 (active).
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/commits/main>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/tree/main/Chapter-04>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/CMakeLists.txt>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/blob/main/Chapter-04/bench_saxpy.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/bench_saxpy.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/saxpy.cpp.in>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/saxpy.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/saxpy.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/saxpy_hand.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/get_best_instructions.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/my_cpuid.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-14/saxpy_mt.cpp>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/commits/main>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/tree/main/Chapter-04>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/issues/15>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/pulls>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/pull/14/files>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/bench_saxpy.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/saxpy.cpp.in>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/saxpy.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/saxpy.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/saxpy_hand.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/get_best_instructions.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/my_cpuid.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-14/saxpy_mt.cpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-cpp-programmers-mindset-saxpy-multiversioning`) · [data/wave1/enrich/raw/paper_book_the_cpp_programmers_mindset_saxpy_multiversioning.json](../../../data/wave1/enrich/raw/paper_book_the_cpp_programmers_mindset_saxpy_multiversioning.json) (enrichment confidence 0.7)

</details>
