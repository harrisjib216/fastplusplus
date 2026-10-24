# zoo (thecppzoo) zoo::VTableFunction / zoo::Function

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only, policy-based type erasure whose zoo::Function holds move-only callables inline, beating std::function plus a shared_ptr workaround.

| | |
|---|---|
| **Beats** | std::function (with a shared_ptr wrapper for the move-only capture, since std::function cannot hold a move-only callable) |
| **Claimed result** | BM_MoveOnlyCapture, median ns over 5 repetitions, std::function holding a shared_ptr wrapper vs zoo: gcc-12/libstdc++ 42.69 (3 allocs) vs 13.43; clang-20/libstdc++ 43.29 vs 14.00; clang-20/libc++ 45.64 vs 12.72 (about 3.2x, 3.1x and 3.6x faster, derived from page data); README: 'About 3x faster, 3 allocations down to 1.' BM_QueueThroughput (enqueue 1024 then drain), median ns per iteration, lower is better, std vs zoo: 5519.25 vs 5073.65, 6633.06 vs 5609.81, 7068.30 vs 5697.49 (about 1.09x, 1.18x and 1.24x faster, derived from page data). BM_ConstructInvokeDestroy small inline capture, std vs zoo: 2.66 vs 2.35, 2.64 vs 2.30, 2.63 vs 2.33 ns (about 1.13-1.15x, derived from page data; the README sums it up as 2.3-3.2 ns for all three candidates). Mixed elsewhere in results/summary.txt: BM_MoveConstruct small capture std 2.34 vs zoo 3.74 ns (gcc-12/libstdc++) and 2.34 vs 6.91 ns (clang-20/libstdc++), zoo slower; BM_MoveAssign large capture under libc++ std 14.76 vs zoo 17.62 ns, zoo slower; BM_MoveAssign boundary and large capture under clang-20/libstdc++ std 20.73 and 21.12 vs zoo 14.32 and 14.63 ns, zoo faster. Compile time, 300 instantiations, best of 3, std vs zoo: 3.67s vs 3.58s, 2.79s vs 2.53s, 7.46s vs 2.88s. Object .text bytes std vs zoo: 5229 vs 3111, 3256 vs 2114, 3633 vs 2108. |
| **Workload** | Third-party Google Benchmark harness in tenstorrent/tt-metal PR #57569 (issue #57444): std::function&lt;void()&gt; vs zoo::Function&lt;zoo::AnyContainer&lt;zoo::Policy&lt;void\*[kInlinePointers], zoo::Destroy, zoo::Move, zoo::RTTI&gt;&gt;, void()&gt; vs fu2::function_base, all pinned to std::function's inline capacity; construct/invoke/destroy, move-construct and move-assign at small, boundary and large capture sizes, a move-only (unique_ptr) capture, queue throughput over 1024 jobs, plus compile time and object size. |
| **Metric** | latency |
| **Compiler and flags** | g++-12 with libstdc++, clang++-20 with libstdc++, clang++-20 with -stdlib=libc++; C++20; README build commands pass -DCMAKE_BUILD_TYPE=Release (the CMakeLists also defaults to Release) and set no other optimization flags; google-benchmark v1.9.1, fu2 4.2.5, zoo pinned at commit 7fb5eed6331651e9d94c0f7e9017f2d56ba4b993; bench run with --benchmark_repetitions=5; harness bench.cpp as of commit ef313b0 |
| **Adoption** | 139 stars; the author's presentation says its type-erasure framework ran in production at Snapchat |
| **Last commit** | 2026-04-15 |
| **Links** | [repository](https://github.com/thecppzoo/zoo) · [benchmark](https://github.com/tenstorrent/tt-metal/commit/ef313b0) |

## Verdict

In tenstorrent's tt-metal harness (Google Benchmark 1.9.1, Release build, median of 5 repetitions, 32-thread x86-64 host with 48 KiB L1d and 1.25 MiB L2 per core, CPU model not named) zoo::Function with a void\*[N] buffer pinned to std::function's inline size ran a unique_ptr-capture construct/invoke/destroy in 12.7-14.0 ns against 42.7-45.6 ns for std::function holding a shared_ptr wrapper (about 3.1-3.6x) on gcc-12/libstdc++, clang-20/libstdc++ and clang-20/libc++, and an enqueue-1024-then-drain std::deque loop 1.09-1.24x faster. Other rows are mixed: inline construct-invoke-destroy is about 1.13x faster, while small-capture move construction under libstdc++ and large-capture move assignment under libc++ are slower than std::function.

## Use it when

- Job queues, thread-pool enqueue paths or callbacks that must own move-only state (unique_ptr, file handles) and today wrap it in shared_ptr to satisfy std::function's copyability.
- Pre-C++23 toolchains without std::move_only_function, or libc++ builds where you want a move-only function with a small inline buffer and zoo's smaller object (40 vs 48 bytes in the tt-metal run).
- Code that wants to choose inline capacity per type (void\*[N]) and pay only for the operations it needs (no Copy entry for move-only, RTTI only if wanted).
- Codebases that want smaller object code and faster builds than std::function: in the tt-metal measurement zoo had the smallest .text in all three configurations and compiled 300 instantiations in 2.88 s against 7.46 s under libc++.

## Skip it when

- Copyable callables with small captures where you already use std::function: the inline construct-invoke-destroy gain is about 0.3 ns (2.3 vs 2.6 ns), and small-capture move construction under libstdc++ was slower (3.74 vs 2.34 ns on gcc-12, 6.91 vs 2.34 ns on clang-20).
- Builds with -fno-rtti: typeid in VTablePolicy.h and FunctionPolicy.h breaks compilation even without the RTTI policy (per the tt-metal evaluation).
- When you can use C++23 std::move_only_function, the fair baseline, which was never measured against zoo.
- Projects that need tagged releases or a stable API: zoo has no tags or releases, recent commits are documentation, and the README calls the released CppCon 2022 code a complete implementation that may not be production-ready.
- Code that assigns callables whose construction can throw and must stay exception-safe (see gotchas).

## How it is fast

The callable is stored in a small buffer whose size and alignment are a template parameter, so the caller can match or exceed std::function's inline capacity; targets that are not nothrow-move-constructible, too large or misaligned fall back to a single heap allocation (BuilderDecider in VTablePolicy.h). Each policy builds one static, constexpr vtable of only the requested operations, and zoo::Function keeps the invoker pointer in the object, so a call is one indirect jump with no empty-check branch (the empty state holds a throwing executor). The headline 3x comes from holding a unique_ptr capture inline with one allocation, where std::function needs make_shared plus its own heap block (3 allocations under libstdc++, 2 under libc++).

## Compared with alternatives

Pick zoo over stdext::inplace_function, SmallFunction or Delegate when the callable must own move-only state and you still want a heap fallback for large captures; those siblings were measured only on copyable or inline targets. woid and sy_callback target call speed of copyable callables; zoo's measured win is allocation count on the move-only path, plus smaller code and faster compiles than std::function.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the headers (Catch2 submodule only for tests) |
| **Minimum toolchain** | C++17; CI builds tests with g++-9, clang-17 and MSVC (MSVC failures do not block changes); the tt-metal evaluation used g++-12 and clang++-20 in C++20 mode |
| **Platforms** | any (portable C++17); no SIMD or OS requirements in the type-erasure headers |
| **Thread safety** | not documented; it is a value type like std::function (no internal synchronisation) |
| **Drop-in for the baseline** | partial — the call syntax, operator bool and nullptr comparisons match std::function, but the type must be spelled as zoo::Function&lt;zoo::AnyContainer&lt;zoo::Policy&lt;void\*[N], zoo::Destroy, zoo::Move, zoo::RTTI&gt;&gt;, Sig&gt; (add Copy for copyability), and target()/target_type() exist only on the separate zoo::function alias; tt-metal needed a wrapper of about 45 lines for its own checks. |

## Gotchas

- Assigning a new callable destroys the old target first and then constructs the new one in place (AnyContainerBase::emplace_impl); if that construction throws (bad_alloc on the heap path or a throwing capture constructor) the object is left with a vtable for a value that was never built, so later destruction is undefined. std::function's assignment gives the strong guarantee. Source reading, not tested.
- A moved-from zoo::Function stays engaged: the defaulted move keeps the executor and, on the heap path, nulls only the target pointer, so operator bool still returns true and calling it invokes a moved-from or null target, where libstdc++'s std::function is left empty and throws bad_function_call. Source reading, not tested.
- The tt-metal README says zoo's noexcept move entry accepts throwing-move targets and would terminate; the pinned VTablePolicy.h (identical to master) routes any type that is not nothrow-move-constructible to the heap (ByReference), whose move only steals the pointer, so that terminate path does not appear in the source.
- The repo's own benchmark (benchmark/catch2Functions.cpp) only stores plain function pointers and, unless built with USE_FOLLY, its 'folly' column is a std::function alias; it publishes no numbers.

## Known shortcomings

- tt-metal harness (ef313b0; gcc-12/clang-20 Release, no CPU model) measured zoo::Function&lt;AnyContainer&lt;Policy&lt;..., RTTI&gt;&gt;&gt;, not VTableFunction&lt;2&gt;; baseline is std::function plus shared_ptr, an idiom gap. zoo is slower on small-capture move-construct (6.91 vs 2.34 ns, clang/libstdc++) and on large-capture move-assign under libc++; no -fno-rtti support. The tt-metal PR #57569 is unmerged and its result files were later removed (103f9f0); Snapchat usage claim unchecked.
- Enricher: summary.txt and the raw out-\*.txt files come from different runs; loaded host (load average 4.2-5.6) with clock varying 2133-3397 MHz; no CPU model; the evaluation's size and throwing-move claims are wrong (32 = 32 bytes under libstdc++; throwing-move targets go to the heap); converting assignment is not exception-safe.

## Caveats and trade-offs

Evidence is independent but not the project's own: the repo's benchmark/catch2Functions.cpp compares zoo::function against std::function, folly::Function and a function pointer but publishes no numbers, and the README contains none. The 3x figure is against std::function plus a shared_ptr workaround for a move-only capture, an idiom gap; the harness README notes std::move_only_function was unavailable in its toolchains, so the fair baseline was not measured. The measured type is zoo::Function over AnyContainer with the RTTI affordance (bench.cpp at ef313b0 says zoo::VTableFunction was deliberately not used); an earlier harness commit, b28acab, used zoo::VTableFunction&lt;kInlinePointers, void()&gt;, but the checked-in results include BoundaryCapture rows that exist only in the later harness. Results are mixed outside the headline rows: zoo is slower than std::function on small-capture move construction under libstdc++ (3.74 vs 2.34 ns on gcc-12, 6.91 vs 2.34 ns on clang-20) and on large-capture move assignment under libc++ (17.62 vs 14.76 ns). CPU model not stated; flags are only the CMake Release build type. The harness commits carry a Claude co-author line, and commit 103f9f0 later removed the checked-in result files, saying the data moves to a PR comment, so the commit-time numbers may be superseded by a rerun. zoo does not compile under -fno-rtti (per the harness README). PR #57569 is still open and unmerged: an intermediate commit (6b4a4e7) was 'backed by zoo', but the current head ships an in-house ttsl::move_only_function that adapts zoo's and LLVM unique_function's designs; the PR description's table (42.94 ns vs 12.96 ns on gcc-12) measures that in-house type, not zoo, so it is not used here. Queue-throughput gains are small (9-24%). The book lead matches the repo only by author name. Category changed from small-buffer-and-strings to smart-pointers-and-refcount because the compared facility is std::function (spec Part 3 map). [retier] Enricher: results/summary.txt comes from a different run than results/out-\*.txt (e.g. MoveOnly std 42.69 vs 42.3 ns), though the ratios agree within about 1%. The host was loaded (load average 4.2-5.6) and the reported clock varied from 2133 to 3397 MHz across configurations; partial hardware only (32 threads, 48 KiB L1d, 1.25 MiB L2 per core). The libc++ baseline makes 2 allocations, not 3. Source gotchas: converting assignment destroys the old target before building the new one, so a throw leaves undefined behaviour; a moved-from Function stays engaged; the repo's own bench 'folly' column is only a std::function alias.

Header-only C++17 (MSVC supported but occasionally buggy per the README). Policy-based inline buffer and ownership (zoo::AnyContainer, AnyCallable, Function), so capacity is a template choice; zoo::function is AnyCallable&lt;Any, Signature&gt;. Per the tt-metal evaluation: sizeof grows from 24 to 32 bytes under libstdc++ (40 vs 48 under libc++); does not build under -fno-rtti; its move vtable entry is noexcept but accepts throwing-move targets, which would terminate; needed a roughly 45-line wrapper to satisfy tt-metal's compliance checks. The README's CppCon 2022 note says the implementation it released may not be production-ready.

## Maintenance

MIT-licensed and header-only, so easy to vendor, but untagged (pin by SHA; tt-metal pinned master HEAD 7fb5eed of 2026-04-15), the ten latest commits are documentation edits, and 18 pull requests and 10 issues are open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party evaluation by tenstorrent engineers with public harness code (tests/tt_stl/move_only_function_bench/bench.cpp at ef313b0), compilers gcc-12 and clang-20 and the CMake Release build type stated, results checked in at commit ef313b0; no CPU model is given, so it falls short of A.
- **Verifier notes:** Main fix: record said the benchmark measured zoo::VTableFunction&lt;2, void()&gt;; the results at ef313b0 come from bench.cpp using zoo::Function&lt;AnyContainer&lt;Policy&lt;..., RTTI&gt;&gt;&gt; (VTableFunction was only in earlier harness b28acab). Queue-throughput unit confirmed as median ns (lower is better), so the zoo win stands. License MIT, 139 stars, last commit 2026-04-15 (docs) confirmed; the Snapchat production claim in stars_or_usage was not checked and left as is.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-79 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/tenstorrent/tt-metal/commit/ef313b0>
  - <https://github.com/tenstorrent/tt-metal/commit/ef313b0.patch>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/README.md>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/results/summary.txt>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/results/item6.txt>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/results/item7.txt>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/bench.cpp>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/b28acab/tests/tt_stl/move_only_function_bench/bench.cpp>
  - <https://github.com/tenstorrent/tt-metal/pull/57569>
  - <https://github.com/thecppzoo/zoo>
  - <https://github.com/thecppzoo/zoo/commits/master>
- **Sources the enricher read:**
  - <https://github.com/thecppzoo/zoo>
  - <https://github.com/thecppzoo/zoo/commits/master>
  - <https://github.com/thecppzoo/zoo/issues>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/master/README.md>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/master/inc/zoo/FunctionPolicy.h>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/master/inc/zoo/function.h>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/master/inc/zoo/AnyCallable.h>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/master/inc/zoo/AnyContainer.h>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/master/inc/zoo/Any/VTablePolicy.h>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/master/inc/zoo/any.h>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/master/inc/zoo/AlignedStorage.h>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/7fb5eed6331651e9d94c0f7e9017f2d56ba4b993/inc/zoo/Any/VTablePolicy.h>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/master/.github/workflows/master.yaml>
  - <https://raw.githubusercontent.com/thecppzoo/zoo/master/benchmark/catch2Functions.cpp>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/README.md>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/bench.cpp>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/results/summary.txt>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/results/out-gcc.txt>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/results/out-clang.txt>
  - <https://raw.githubusercontent.com/tenstorrent/tt-metal/ef313b0/tests/tt_stl/move_only_function_bench/results/out-libcxx.txt>
  - <https://github.com/tenstorrent/tt-metal/tree/ef313b0/tests/tt_stl/move_only_function_bench/results>
  - <https://github.com/tenstorrent/tt-metal/pull/57569>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/thecppzoo/zoo`) · [data/wave1/enrich/raw/github_com_thecppzoo_zoo.json](../../../data/wave1/enrich/raw/github_com_thecppzoo_zoo.json) (enrichment confidence 0.75)

</details>
