# Julia (no BLAS) matmul with @fastmath @simd ivdep in kostya/benchmarks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Hand-written Julia matmul loop in kostya/benchmarks that runs 2.7x faster than the suite's strict-FP C dot-product loop.

| | |
|---|---|
| **Beats** | C/gcc matmul (matmul/matmul.c, Attractive Chaos): B is transposed, then a scalar dot-product triple loop (t += p[k] \* r[k]) on double\*\* rows; gcc 16.1.0 -O3 -march=native -flto=auto -std=c23, no -ffast-math and no restrict |
| **Claimed result** | Matmul (MSIZE 1500): Julia (no BLAS) 1.113s (MAD 0.017) vs C/gcc 3.034s (MAD 0.001) and C/clang 3.067s (about 2.7x vs C/gcc, derived from page data); energy 49.41 J vs 113.24 J. The other plain-loop rows (Rust 3.067s, Zig 3.071s, Go 3.153s, Java 3.057s) cluster with C. Library-backed rows (C++/g++ Eigen 0.081s, Julia with OpenBLAS threads: 1 0.170s) are a different algorithm class and are not the claim. |
| **Workload** | 1500x1500 double matrix multiply (MSIZE 1500) written as plain loops (no BLAS) in each language. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E-2324G (README Environment section); Debian forky/sid Docker image |
| **Compiler and flags** | C baseline: gcc 16.1.0 -Wall -Wextra -pedantic -Wcast-align -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries -std=c23 (common/commands.mk GCC_BUILD); the C/clang row uses clang 22.1.8 with the same flags (CLANG_BUILD). Julia run as julia --optimize=3 --check-bounds=no matmul.jl 1500 (common/commands.mk JULIA_RUN, matmul/Makefile run[matmul.jl]) with no -t flag; README Environment lists Julia v"1.11.6" while docker/Dockerfile at HEAD pins julia-1.12.6. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | no |
| **Why it wins** | Per-statement fast-math and ivdep annotations allow the LLVM vectorizer to reassociate and vectorize the inner loop that strict-FP gcc -O3 does not (derived from reading matmul/matmul.jl and matmul.c; not stated in the README). |
| **Adoption** | 2.9k stars |
| **Last commit** | 2026-07-19 |
| **Links** | [repository](https://github.com/kostya/benchmarks) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

On an Intel Xeon E-2324G (README UPDATE 2026-07-19, median with MAD), the 1500x1500 Float64 matmul takes 1.113 s (49.41 J) for the Julia (no BLAS) loop against 3.034 s (113.24 J) for C built with gcc 16.1.0 -O3 -march=native -flto=auto -std=c23, and 3.067 s with clang 22.1.8. That is about 2.7x (derived from page data), but the Julia side uses a vectorisable axpy loop with fast-math while C runs a strict-FP scalar dot product.

## Use it when

- As a reference for how to write a fast naive matmul in Julia: column-major axpy loop order plus @simd ivdep and @fastmath, without BLAS.
- As evidence that loop order and reduction structure matter more than the language here: every plain dot-product row (C, Rust, Zig, Java, Go, Swift) lands at 3.03-3.16 s.
- When teaching or measuring what @simd ivdep and @fastmath change in LLVM's vectoriser on a simple column-major kernel.

## Skip it when

- For real matrix multiplication: Julia's own BLAS call (matmul-native.jl) takes 0.170 s with one OpenBLAS thread on the same machine, 6.5x faster than this loop (derived from page data), and C++ Eigen takes 0.081 s.
- As proof that a JIT beats AOT C: D/gdc reaches 1.505 s, exactly half of C/gcc's 3.034 s, with the same transposed dot-product structure, because std.numeric.dotProduct (Phobos master source) splits the sum over two accumulators (derived from page data and the Phobos source). That is an AOT compiler showing the same reduction effect.
- When bit-identical results matter: @fastmath allows FMA contraction and reassociation, so results may differ from a strict IEEE loop in the last bits.
- In memory-constrained processes: the Julia process starts at about 256 MiB RSS against 2 MiB for C.

## How it is fast

The speedup comes from loop structure, not from JIT compilation. PR #318 (2021, adapted from LoopVectorization.jl's looptests) replaced Julia's earlier transpose-plus-dot-product loop with column-major axpy order (for n, for k, for m: c[m,n] += a[m,k]\*b[k,n]), annotated with @inbounds, @simd ivdep and @fastmath. The inner iterations are independent, so LLVM vectorises them and contracts them to FMAs. The C inner loop is one serial floating-point add chain (t += p[k]\*r[k]) that gcc may not reassociate without -ffast-math, and -std=c23 also turns FMA contraction off.

## Compared with alternatives

Pick it only to illustrate loop order and @simd/@fastmath effects. For a like-for-like Julia vs C++ comparison, the zyth0s density-gradient entry (same routine, about 9% faster) is cleaner. The LangArena Sort::Self entry is another algorithm-mismatch win from the same author's suites (radix sort against introsort).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Julia base only (Sockets is used only for the harness notify call) |
| **Minimum toolchain** | Julia 1.x with @simd ivdep and Threads.@threads; the README lists Julia 1.11.6, while docker/Dockerfile at HEAD pins julia-1.12.6 |
| **Platforms** | any Julia platform; measured on x86-64 (Intel Xeon E-2324G) |
| **Thread safety** | mul() allocates its own output and is safe to call concurrently; Threads.@threads splits the outer loop over columns, but the benchmark runs with Julia's default single worker thread (no -t flag or JULIA_NUM_THREADS in common/commands.mk or docker/Dockerfile) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (unequal work and optimisation level): Julia and C run different loop structures. Julia's axpy loop with @fastmath and @simd ivdep vectorises, while the C reference is a strict-FP serial reduction built with gcc -O3 -march=native -std=c23 (no -ffast-math, no restrict; issue #132 asking for restrict has been open since 2017). C/gcc's 3.034 s works out to 0.90 ns per multiply-add over 1500^3 = 3.375e9 steps, which is consistent with one dependency chain. The two-accumulator D/gdc row at 1.505 s halves it. Both figures are derived from page data, and they make the 2.7x a loop-order and reassociation effect, not a language or JIT effect.
- The README Overview says algorithms should be 'similar between the languages', and Julia's own 2017 commit 'update to use pre-transpose, similar to C' once matched C. PR #318 later dropped the transpose and changed the loop order, so the Julia program now departs from the reference algorithm. The PR author reported 3.4 s to 750 ms on his machine.
- Julia runs with --check-bounds=no plus @inbounds, while Rust, Nim and V keep bounds checks. Issue #312 raised this in 2021, and the maintainers kept it, saying 'there is no way we can have the fair comparison here'.
- The Julia version behind the published row is uncertain (README 1.11.6 against Dockerfile 1.12.6). Timing includes matrix generation and allocation on both sides, and JIT compilation is excluded because calc(101) runs before the notify that starts xtime.rb's clock.

## Known shortcomings

- The work differs: Julia uses an axpy loop order with @fastmath and @simd ivdep while the C side (gcc -std=c23) does a strict-FP dot-product reduction without -ffast-math; Julia runs on one thread; README says Julia 1.11.6 while the Dockerfile pins 1.12.6.
- The JSON3.jl enricher found that kostya/benchmarks' 2026-07-19 update re-measured only the Primes table and the environment table: the Json table rows kept their 2025-08-17 values (gcc 14.2.0, clang 19.1.7), so the compiler versions recorded here (gcc 16.1.0, clang 22.1.8) describe the current environment table and may not be the toolchain behind this table's rows; whether this table was re-run on 2026-07-19 was not checked.
- Harness flaw: different loop structure, not a JIT win. PR #318 (2021, from LoopVectorization.jl's looptests) dropped Julia's transpose plus dot product for an axpy loop order with @fastmath and @simd ivdep, while C is a strict-FP serial add chain built with -std=c23 (no FMA). D/gdc's 1.505 s is exactly half of C/gcc's 3.034 s because Phobos dotProduct uses two accumulators, an AOT row showing the same effect; Rust, Zig, Go and Java with one chain all sit at about 3.05 s. Julia with single-threaded BLAS takes 0.170 s. Issue #132 (C restrict) has been open since 2017. The Julia version is unclear (README 1.11.6, Dockerfile 1.12.6).

## Caveats and trade-offs

Not an equal-work, equal-optimisation comparison. The C inner loop is a scalar floating-point reduction (t += p[k] \* r[k]) that gcc and clang at -O3 may not reorder or vectorise without -ffast-math, so it runs as one serial dependency chain; the Julia inner loop uses the other loop order (c[m,n] += a[m,k] \* b[k,n] down a column-major column), whose iterations are independent and vectorise without reassociation, plus @simd ivdep (no alias checks), @fastmath (FMA contraction and reassociation allowed) and @inbounds. The C file is built with -std=c23, an ISO mode in which GCC's documented default is -ffp-contract=off, so the gcc build does not even fuse multiply-adds. A C version with the same loop order or with -ffast-math would likely close most of the gap. The Julia file wraps the outer loop in Threads.@threads, but neither JULIA_RUN nor docker/Dockerfile sets -t or JULIA_NUM_THREADS, so Julia's default of one thread applies (inferred from the build files, not stated on the README). The timed region includes matrix generation and allocation on both sides; Julia is warmed by calc(101) before timing, so JIT compilation of mul is outside the timed region. The README's Julia version (1.11.6) disagrees with the Dockerfile at HEAD (1.12.6), so the version behind the published row is uncertain. Capped at C for the mismatched optimisation level and loop structure. [retier] PR #318 (2021, from LoopVectorization.jl's looptests) dropped Julia's transpose plus dot product for an axpy loop order with @fastmath and @simd ivdep, while C is a strict-FP serial add chain built with -std=c23 (no FMA); D/gdc's 1.505 s is exactly half of C/gcc's 3.034 s from Phobos' two-accumulator dotProduct, an AOT row showing the same effect, and Rust, Zig, Go and Java with one chain all sit at about 3.05 s. Julia with single-threaded BLAS takes 0.170 s. The Julia version is unclear (README 1.11.6, Dockerfile 1.12.6).

Julia's @fastmath/@simd ivdep license reassociation and assumed no loop-carried dependence; JIT warm-up inside the timed run; Julia uses about 256 MiB base + 51 MiB peak increase versus 2 MiB + 68 MiB for the C program.

## Maintenance

kostya/benchmarks is active (README update 2026-07-19, 2.9k stars, MIT). The Julia kernel is trivially copyable, but the catalogued 'win' is a benchmark-construction artefact, so it is capped at tier C and is no reason to pick Julia over C for matmul.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The measurement meets A methodology (matmul/matmul.jl vs matmul/matmul.c, flags in common/commands.mk and matmul/Makefile, gcc 16.1.0, Intel Xeon E-2324G) and the 1.113s vs 3.034s rows are on the README, but the two sides do not do the same work at the same optimisation level: the Julia loop is an axpy loop order with @fastmath, @simd ivdep and @inbounds, while the C loop is a strict-FP scalar dot-product reduction with no -ffast-math, so the language-level claim is capped at C (unequal-work precedent, as for the batch-06 staged brainfuck rows).
- **Verifier notes:** Numbers, flags, CPU and code check out; tier stays C because same_algorithm and same_opt_level are both false (axpy plus @fastmath/@simd ivdep in Julia vs strict-FP dot-product reduction in C). Corrected compiler_and_flags (the baseline is C built with gcc -std=c23, not g++ -std=c++23) and baseline_stdlib (C with glibc only, no libstdc++). D is arguable under the crippled-baseline precedent, but the C side is a release build (-O3 -march=native -flto) with a cache-friendly transpose, not a debug or naive build, so C matches batch-06.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `baseline_stdlib`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-07 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits/master>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/matmul.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/matmul.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/matmul-native.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/xtime.rb>
- **Sources the enricher read:**
  - <https://github.com/kostya/benchmarks>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/matmul.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/matmul.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/matmul-native.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/matmul.d>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/matmul.rs/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/matmul.java>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/xtime.rb>
  - <https://raw.githubusercontent.com/dlang/phobos/master/std/numeric.d>
  - <https://github.com/kostya/benchmarks/commits/master/matmul/matmul.jl>
  - <https://github.com/kostya/benchmarks/commit/16ce136>
  - <https://github.com/kostya/benchmarks/pull/318>
  - <https://github.com/kostya/benchmarks/issues?q=is%3Aissue+matmul>
  - <https://github.com/kostya/benchmarks/issues/312>
  - <https://github.com/kostya/benchmarks/issues/132>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:julia/kostya/benchmarks#matmul-no-blas`) · [data/wave14/enrich/raw/lang_julia_kostya_benchmarks_matmul_no_blas.json](../../../data/wave14/enrich/raw/lang_julia_kostya_benchmarks_matmul_no_blas.json) (enrichment confidence 0.8)

</details>
