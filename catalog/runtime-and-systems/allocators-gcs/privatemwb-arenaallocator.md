# ArenaAllocator (privateMwb)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 fixed-capacity bump arena with frame rollback; about 1.2-1.8x faster per allocate() than std::pmr::monotonic_buffer_resource.

| | |
|---|---|
| **Beats** | std::pmr::monotonic_buffer_resource (stdArena in benchmarks/\*/support/reference.h) |
| **Claimed result** | Google Benchmark run: allocate 0.73 ns vs 1.31 ns (small) and 0.77 vs 1.07 ns at 256 B; the README reset-and-refill gap (101.67 ms vs 14.16 s) comes from std release() freeing the 64 MiB upstream block every iteration, and the failure-path gap from the std side throwing bad_alloc; construction is about 7x slower |
| **Workload** | 1M-iteration benchmarks of a fixed-capacity bump arena versus a new[]-based stdArena: capacity-failure path, reset and refill, large and over-aligned allocations. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-latest runner (context block: 4 CPUs, 4342 MHz, 48 KiB L1d, 1 MiB L2, 32 MiB L3; CPU model not recorded), Google Benchmark v1.9.1 |
| **Compiler and flags** | clang (ubuntu-latest apt package), CMAKE_BUILD_TYPE=Release via .github/workflows/benchmark.yml; no explicit optimization flags stated |
| **Adoption** | 1 star |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/privateMwb/ArenaAllocator) · [benchmark](https://github.com/privateMwb/ArenaAllocator#benchmarks) |

## Verdict

The committed comparisons are against std::pmr::monotonic_buffer_resource (not new[] as the README says): in the Google Benchmark v1.9.1 run on a 4-CPU GitHub Actions runner (clang Release, CPU model not recorded) allocate() costs 0.73 vs 1.31 ns small, 0.77 vs 1.07 ns for 256 B and 0.73 vs 1.07 ns at 64 B alignment (about 1.4-1.8x, derived from page data), while the custom-framework 1M-iteration run shows 0.62 vs 1.34 ms small. The headline reset+refill (64.7 ns vs 43.8 us) and failure-path (0.12 vs 907 ns) gaps come from release() freeing the upstream block and from exception handling, and construction is about 7x slower.

## Use it when

- Per-frame or per-request scratch memory with a known upper bound, reclaimed all at once with reset() or a scoped frame.
- Hot loops doing many small, short-lived allocations (a few to a few hundred bytes) where a virtual call into std::pmr::monotonic_buffer_resource shows up.
- Code that must treat out-of-memory as a plain nullptr branch with no exceptions (games, embedded-ish, real-time paths).
- Over-aligned blocks (cache-line or page aligned) carved from one buffer, provided the arena is constructed with that base alignment.

## Skip it when

- Unknown or unbounded memory needs: capacity is fixed at construction and there is no growth or chaining.
- Workloads that need per-object free or reuse of freed holes; destroy() never returns storage.
- When you need std::pmr containers or an allocator-aware interface; it is not a memory_resource, so std::pmr::monotonic_buffer_resource over a fixed buffer is the drop-in choice.
- Many short-lived arenas: construction is about 7x slower than monotonic_buffer_resource (23.4 ns vs 3.3 ns in the committed Google Benchmark run) because the buffer is allocated eagerly.
- Shared use across threads: no synchronization is documented or present.

## How it is fast

Classic bump-pointer (linear/monotonic) allocation: alignment is rounded with a power-of-two mask derived from countr_zero, followed by two independent bounds checks, so the hot path is a few integer ops on one cache line. There is no upstream resource, no virtual dispatch (unlike std::pmr::memory_resource::allocate) and no block chaining, which is where its edge over monotonic_buffer_resource comes from. Optional statistics compile away via if constexpr and [[no_unique_address]].

## Compared with alternatives

Pick it over NotKeira/fast-alloc or cleeus/obstack when you want a single bounded buffer with nested RAII rollback, nullptr-on-full semantics, and a fuzzed, sanitizer-tested C++20 header; pick fast-alloc for pool (fixed-size free list) needs and a general malloc replacement such as mimalloc-class siblings for anything unbounded.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (CMake 3.20+ for the install/find_package path; Google Benchmark only for the benchmark suite) |
| **Minimum toolchain** | C++20 (concepts, &lt;bit&gt;, [[no_unique_address]]); README lists GCC, Clang, MSVC and AppleClang as tested |
| **Platforms** | any (portable C++20, no intrinsics) |
| **Thread safety** | not documented; the class has no locking or atomics, so treat one arena as single-threaded |
| **Drop-in for the baseline** | partial — same bump-allocation model as std::pmr::monotonic_buffer_resource, but a different, non-virtual API that returns nullptr instead of growing or throwing |

## Gotchas

- Preconditions are assert()-only (AP_PRE expands to assert): with NDEBUG, a ninth nested beginFrame() writes past the 8-slot frame stack, endFrame() without a matching beginFrame() underflows frameDepth_, and a request alignment above the construction alignment is silently not honored.
- Reset + refill and failure-path speedups (hundreds to hundreds of thousands of percent) are not like-for-like: the benchmark calls monotonic_buffer_resource::release(), which returns its 64 MiB upstream block so the refill re-allocates it every iteration, and the bounded std side signals exhaustion by throwing std::bad_alloc that the loop catches.
- The README describes the baseline as 'a naive new[] + linear-scan stdArena', but benchmarks/{custom,google}/support/reference.h define stdArena as std::pmr::monotonic_buffer_resource; and the README table's numbers match neither committed baseline (v1.0.0.md or gv1.0.0.md).
- Several committed Google Benchmark rows (destroy_\*, reset_arena, reset_std) report 0.00 ns, i.e. the work was optimized away; ignore them.

## Known shortcomings

- The baseline stdArena is std::pmr::monotonic_buffer_resource (benchmarks/{custom,google}/support/reference.h), not new[], so it is compared against the C++ standard library directly. The README table matches neither committed baseline (v1.0.0.md, gv1.0.0.md). Google Benchmark run: allocate 0.73 vs 1.31 ns small, 0.77 vs 1.07 ns at 256 B. The reset-and-refill gap comes from release() freeing the 64 MiB upstream block every iteration; the failure-path gap is the std side throwing bad_alloc; construction is about 7x slower.

## Caveats and trade-offs

Baseline is the author's own naive stdArena (new[] + linear scan), not malloc or a known arena library; the largest ratios compare an O(1) reset/bounds-check with a baseline that grows or frees per object. Arena is slower on Construction, Destroy and the 4 KiB buffer case. Numbers from a shared CI runner with no CPU model. Baseline JSON lives at benchmarks/baselines/v1.0.0/v1.0.0.json (not benchmarks/baselines/v1.0.0.json as the README says).

Header-only fixed-capacity bump-pointer arena with frame rollback; capacity fixed at construction; no per-object free.

## Maintenance

Active (v1.0.0 released 2026-07-28, commits into October 2026, 1 star, no issues filed); MIT, small and header-only, so easy to vendor, with CI for sanitizers, clang-tidy, CodeQL and ClusterFuzzLite differential fuzzing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks table (1M iterations) compares ArenaPro against the author's own stdArena (naive new[] + linear-scan) baseline; benchmark code and a Google Benchmark JSON (benchmarks/baselines/v1.0.0/v1.0.0.json) are public, but the run was on a GitHub Actions ubuntu-latest runner (4 CPUs @ 4342 MHz, no CPU model) with clang Release and no explicit flags, and the baseline is not a recognized incumbent, so C.
- **Verifier notes:** Real, well-tooled header-only arena, but the comparison is against a strawman baseline; keep at C with the baseline caveat. Last commit 2026-10-04 and 1 star confirmed on github.com.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `benchmark_url`, `caveats`, `baseline`, `compared_against_cpp_std_directly`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/README.md>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/LICENSE>
  - <https://github.com/privateMwb/ArenaAllocator/tree/main/benchmarks/baselines>
  - <https://github.com/privateMwb/ArenaAllocator/tree/main/benchmarks/baselines/v1.0.0>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/main/benchmarks/baselines/v1.0.0/v1.0.0.json>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/main/.github/workflows/benchmark.yml>
  - <https://github.com/privateMwb/ArenaAllocator/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/README.md>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/include/ArenaPro/Arena.h>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/include/ArenaPro/Arena.tpp>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/include/ArenaPro/ArenaScope.h>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/include/ArenaPro/Contract.h>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/benchmarks/custom/README.md>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/benchmarks/custom/support/reference.h>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/benchmarks/google/support/reference.h>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/benchmarks/google/support/framework.h>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/benchmarks/google/suite/core/allocate.cpp>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/benchmarks/google/suite/core/reset_refill.cpp>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/benchmarks/google/suite/scaling/exhaustion.cpp>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/HEAD/benchmarks/google/suite/lifecycle/construction.cpp>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/main/benchmarks/baselines/v1.0.0/v1.0.0.json>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/main/benchmarks/baselines/v1.0.0/v1.0.0.md>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/main/benchmarks/baselines/v1.0.0/gv1.0.0.json>
  - <https://raw.githubusercontent.com/privateMwb/ArenaAllocator/main/benchmarks/baselines/v1.0.0/gv1.0.0.md>
  - <https://github.com/privateMwb/ArenaAllocator/tree/main/benchmarks/google>
  - <https://github.com/privateMwb/ArenaAllocator/tree/main/benchmarks/google/suite>
  - <https://github.com/privateMwb/ArenaAllocator/tree/main/benchmarks/google/support>
  - <https://github.com/privateMwb/ArenaAllocator/tree/main/benchmarks/custom>
  - <https://github.com/privateMwb/ArenaAllocator/tree/main/benchmarks/baselines/v1.0.0>
  - <https://github.com/privateMwb/ArenaAllocator/tree/main/benchmarks/results>
  - <https://github.com/privateMwb/ArenaAllocator/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/privatemwb/arenaallocator`) · [data/wave11/enrich/raw/github_com_privatemwb_arenaallocator.json](../../../data/wave11/enrich/raw/github_com_privatemwb_arenaallocator.json) (enrichment confidence 0.75)

</details>
