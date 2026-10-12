# Spinel

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Ahead-of-time Ruby-subset-to-C compiler by Matz; README geomean 8.5x faster than CRuby 4.0.4 with YJIT.

| | |
|---|---|
| **Beats** | CRuby 4.0.4 (MRI interpreter) and CRuby 4.0.4 with --yjit |
| **Claimed result** | 'Geometric mean: \~8.5x faster than Ruby 4.0.4 with --yjit across the 28 benchmarks (\~15.2x against the interpreter)'. Examples vs YJIT: mandelbrot 18 ms vs 938 ms (53.6x), matmul 6.1 ms vs 201 ms (32.9x), binary_trees 2.7 ms vs 13 ms (4.7x), json_parse 28 ms vs 133 ms (4.7x), csv_process 95 ms vs 396 ms (4.2x). |
| **Workload** | 28 benchmarks in the repository's benchmark/ directory (mandelbrot, fib, matmul, nqueens, sieve, binary_trees, json_parse, ao_render and others), compiled ahead of time to native executables by Spinel versus the same scripts run by CRuby. |
| **Metric** | throughput |
| **Hardware** | '32-core Linux box' (CPU model not stated) |
| **Compiler and flags** | gcc 13.3 builds the generated C; the README does not list flags, but Spinel's cc driver defaults to -O2 (src/main.c opt_level "2", Makefile COPT ?= -O2) plus -ffunction-sections -fdata-sections -ffp-contract=off. CRuby 4.0.4 (revision b89eb1bc) run with --disable-gems, and with --yjit for the JIT column; each cell is the mean of five wall-clock runs under `perf stat -r 5`, measured 2026-09-17 on spinel 74c8e0a4. |
| **Adoption** | 2.2k stars; authored by Yukihiro Matsumoto |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/matz/spinel) · [benchmark](https://github.com/matz/spinel) |

## Verdict

First-party README tables (2026-09-17, spinel 74c8e0a4, gcc 13.3 at the driver's default -O2, unnamed 32-core Linux machine, mean of five perf stat runs) time 28 benchmark scripts as Spinel-compiled binaries against CRuby 4.0.4 with --disable-gems, with and without --yjit; the geomean is 8.51x vs YJIT and 15.21x vs the interpreter (recomputed from the rows). Excluding the five startup-bound rows and the constant-folded fib row leaves 8.54x vs YJIT and 16.35x vs the interpreter over 22 rows (derived from page data).

## Use it when

- CPU-bound Ruby scripts and CLI tools that stay inside the supported subset (numeric loops, arrays, hashes, strings, structs, blocks): the README shows 19-54x over YJIT on integer/float loops such as mandelbrot, matmul, sieve and partial_sums.
- Shipping a Ruby program as a dependency-free native binary (or as generated C plus libspinel_rt.a) to Linux or macOS hosts without a Ruby install.
- Short-lived command-line programs where CRuby's process startup dominates; Spinel binaries start in about 0.8 ms.
- Parallel Ruby code: the threaded runtime runs Thread on an M:N work-stealing scheduler with no GVL (data races are the program's problem, as in JRuby/TruffleRuby).

## Skip it when

- Rails or gem-heavy applications that rely on eval, method_missing, runtime define_method/send, refinements, ObjectSpace or C extensions; these are refused at compile time (docs/limitations.md), and only community transpilers such as roundhouse bridge Rails.
- Code that depends on exact CRuby semantics in corner cases: typed arrays raise TypeError on a mismatched store, integers are fixed-width and raise on overflow by default, and open issues include silent wrong results (#6179: a String appended to by a callee through send/proc/lambda is not seen by the caller; #7612: -2\*\*63 read as nil).
- Allocation-, IO- or hash-bound workloads, where the README's own margins over YJIT shrink to 3.1-4.9x (io_wordcount, csv_process, gcbench, binary_trees).
- Native Windows (MinGW/MSVC unsupported; use WSL) or a toolchain without GCC extensions (__attribute__((cleanup)), inline assembly for fibers).
- Teams that need a stable, reviewable codebase: issue #7033 (Oct 2026) reports 213,837 lines of C in src/ with a single 17,672-line emit_call_body function and asks the project to slow down.

## How it is fast

Whole-program type inference to a fixpoint lets codegen use unboxed C ints, doubles and typed arrays (sp_IntArray, sp_FloatArray, sp_StrArray) and direct C calls instead of dynamic dispatch; polymorphic values fall back to tagged unions. Small immutable classes become stack-allocated value types, short methods are emitted static inline, and gcc -O2 then optimises the whole program (it even folds the pure fib call tree at build time). A generational size-class mark-and-sweep GC, NFA regexp engine and mruby-bigint are linked only when used, and --gc-sections strips the rest, so binaries start in about 0.8 ms.

## Compared with alternatives

Pick Spinel over YJIT or TruffleRuby when the program fits the static subset and you want a small native binary with no Ruby runtime and roughly an order of magnitude more speed; stay on YJIT (drop-in, full compatibility) or TruffleRuby (full Ruby with peak JIT) for dynamic or gem-heavy code, and use Lightstorm only if you are already on mruby.

## Integration

| | |
|---|---|
| **Form** | compiler binary (spinel) plus static runtime library libspinel_rt.a; output is a standalone executable or a single .c file |
| **Dependencies** | build: libprism (fetched by make deps, vendored in release tarballs), system gcc or clang; run time: libc and libm only (pthread when Thread is used); CRuby optional (test oracle, spinel diff) |
| **Minimum toolchain** | gcc or clang with GCC extensions; exact minimum versions not documented (README benchmarks used gcc 13.3; CI runs ubuntu-latest gcc/clang and macos-latest clang) |
| **Platforms** | Linux x86-64 and arm64, macOS Intel and Apple Silicon; BSD expected but not in CI; Windows only via WSL |
| **Thread safety** | Generated programs support true parallel Thread with Mutex/Queue/ConditionVariable over a stop-the-world GC; unsynchronized shared mutation is a data race (docs/thread.md per README) |
| **Drop-in for the baseline** | partial — runs unmodified Ruby only if it fits the supported subset, and you compile instead of interpret; CRuby is kept as the output oracle for tests |

## Gotchas

- Release builds do not nil-check an @ivar before a call: calling through an ivar that a setup/reset method has not yet assigned segfaults (SIGSEGV); only -g/--debug builds raise NoMethodError (docs/limitations.md, kept for a 10-20% optcarrot gain).
- Startup-bound rows: bigint_fib (1000 additions), pidigits (27 digits), str_concat (10,240 appends), fasta (n=1000) and fannkuch finish in 5.7-9.2 ms under CRuby, which is about CRuby's own process startup, so their 4.6-6.8x ratios measure startup, not the workload. I recomputed the geomean without those five and the constant-folded fib row: 8.54x vs YJIT over 22 rows, so the headline still holds.
- The headline geomean covers the 28 benchmarks in the README table; the repo has 61-62 benchmarks (bm_getivar, bm_send_bmethod, bm_object_new, bm_nbody, bm_micro_lisp, bm_sinatra_mini, bm_jekyll_lite and others are not in the table) and the selection is not explained. Spinel's compile time (spinel plus gcc) is excluded while YJIT's warm-up is inside each wall-clock cell.
- Integer +, -, \* raise on 64-bit overflow by default instead of promoting to Bignum; use --int-overflow=promote for CRuby semantics or wrap for speed.

## Known shortcomings

- No CPU model ('32-core Linux box'), no timing script in the repo (make bench only checks output); sub-10 ms cells are mostly startup, the fib row is constant-folded by the C compiler, and YJIT gives no gain on the mandelbrot, matmul and sieve rows. Compiles a Ruby subset only (no eval or metaprogramming); geomean recomputed from 28 rows is 8.51x over YJIT and 15.21x over the interpreter.
- Enricher: five rows are startup-bound (bigint_fib with 1000 adds, pidigits with 27 digits, str_concat, fasta n=1000, fannkuch all run 5.7-9.2 ms under CRuby, roughly CRuby's startup); the headline holds without them and fib (8.54x over YJIT across 22 rows), but the geomean covers 28 of 61-62 benchmarks with the choice unexplained. Release builds segfault on a call through an unset instance variable; open silent wrong-result bugs #6179 and #7612; issue #7033 notes a 213,837-line src/ with one 17,672-line function.

## Caveats and trade-offs

First-party numbers with only a core count for hardware; no timing script is checked in (make bench is a pass/fail output check against CRuby), so the perf stat runs are not reproducible from the repo as-is. Sub-10 ms cells are dominated by process startup (about 0.8 ms per binary; README says those ratios are lower bounds). The README itself warns the fib row (44.6x vs YJIT) reflects the C compiler folding a pure call tree at build time, not per-call speed. YJIT is essentially identical to the interpreter on mandelbrot, nqueens, matmul, partial_sums and sieve, so the largest multiples there are against an un-accelerated baseline. Spinel compiles a Ruby subset (whole-program type inference, no eval or dynamic metaprogramming), so the benchmarks are programs inside that subset. The geometric means (8.5x vs YJIT, 15.2x vs interpreter) reproduce from the 28 table rows (derived from page data).

An ahead-of-time compiler for a Ruby subset (see the README Supported Ruby Features section), not a drop-in interpreter: it does whole-program type inference, emits C and invokes the system cc. Compiled binaries start in about 0.8 ms.

## Maintenance

Very active (dated releases since 2026.09.12, commits and issues daily, 2.2k stars) and MIT-licensed, but young and fast-moving, with open silent-miscompile issues and a contributor-raised maintainability alarm; build it from source and run your program through `spinel diff` against CRuby before trusting it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables (Benchmarks section) compare Spinel-compiled binaries with CRuby 4.0.4 and CRuby 4.0.4 --yjit on the 28 listed scripts in benchmark/ (bm_\*.rb), with gcc 13.3 and perf stat -r 5 stated, but the hardware is only a '32-core Linux box' with no CPU model and the repo has no timing script (make bench only checks output against CRuby), so it falls short of A.
- **Verifier notes:** Record is accurate: every quoted cell (mandelbrot 18 vs 938 ms, matmul 6.1 vs 201 ms, binary_trees 2.7 vs 13 ms, json_parse 28 vs 133 ms, csv_process 95 vs 396 ms) matches the README, and recomputing the geometric mean over the 28 rows gives 8.51x vs YJIT and 15.21x vs the interpreter. Metadata checked on github.com: MIT (LICENSE, Copyright 2024- Yukihiro Matsumoto), 2.2k stars, 142 forks, not a fork, not archived, last commit 2026-10-06. Shortcomings: no CPU model, no checked-in timing harness, startup-dominated small cells, fib row constant-folded, Ruby subset only.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/matz/spinel>
  - <https://github.com/matz/spinel/commits>
  - <https://github.com/matz/spinel/tree/master/benchmark>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/README.md>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/Makefile>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/common.mk>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/src/main.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/README.md>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/Makefile>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/common.mk>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/docs/limitations.md>
  - <https://github.com/matz/spinel/tree/master/benchmark>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_fib.rb>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_bigint_fib.rb>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_pidigits.rb>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_str_concat.rb>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_fasta.rb>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_so_mandelbrot.rb>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_mandel_term.rb>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_matmul.rb>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_sieve.rb>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_nqueens.rb>
  - <https://raw.githubusercontent.com/matz/spinel/HEAD/benchmark/bm_partial_sums.rb>
  - <https://github.com/matz/spinel/issues>
  - <https://github.com/matz/spinel/issues/7033>
  - <https://github.com/matz/spinel/issues/6179>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/matz/spinel`) · [data/wave12/enrich/raw/github_com_matz_spinel.json](../../../data/wave12/enrich/raw/github_com_matz_spinel.json) (enrichment confidence 0.8)

</details>
