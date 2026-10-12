# LC Scheme BBV JIT (bsaleil/lc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Scheme` · `BSD-3-Clause` · 🔴 abandoned

> Research Scheme JIT using lazy basic-block versioning; generated code edges out Gambit and Chez on 38 classic benchmarks.

| | |
|---|---|
| **Beats** | Gambit Scheme v4.9.3 and Chez Scheme v9.5.2 (mature AOT Scheme compilers, safe and unsafe modes); also Pycket (February 2019 build, Racket tracing JIT on RPython) for total time |
| **Claimed result** | PhD thesis (Saleil 2019, Fig. 6.16, execution time excluding GC and compilation time, 38 benchmarks): average execution time relative to LC is Gambit safe 1.38x, Chez safe 1.27x, Gambit unsafe 1.12x, Chez unsafe 1.09x; LC is faster on more than half of the benchmarks; best case fftrad4 with Gambit at 4.03x (safe) / 3.29x (unsafe) and Chez at 5.10x (safe) / 4.60x (unsafe) of LC's time. Against Pycket (Fig. 6.17, including JIT compile time, excluding GC): LC is 0.87x Pycket's time on average (0.80x with f64vectors), faster on 22 of 38, best nucleic 0.13x, worst fft 3.40x. VMIL 2018 paper (Section 6.3, i7-4870HQ, Gambit v4.8.9 cited): LC optimized generated code 1.47x faster than Gambit on average, faster on 26 of 38; 1.35x faster than Pycket on average (22 of 37 significantly faster); 2.25x over LC naive mode. ECOOP 2017 abstract: 'up to 50% faster' refers to interprocedural versus intraprocedural LC; against Gambit unsafe the generated code ranges from 34% faster (browse) to 390% slower (pnpoly). The README fib(40) timing (0.550 s real) has no baseline. |
| **Workload** | JIT compiler for Scheme on Linux x86-64 using lazy basic-block versioning with interprocedural code specialization (entry and return point tables). Experiments use 38 classic Scheme benchmarks taken from Gambit with Gambit's iteration counts (ack, boyer, browse, compiler, conform, cpstak, deriv, earley, fft, fftrad4, fib, fibfp, mbrot, nbody, nqueens, nucleic, peval, pnpoly, simplex, sum, sumfp, tak, takl and others), driven by tools/benchtimes/run.py; the Gambit and Chez comparison times generated code only (GC and compile time excluded), the Pycket comparison includes JIT compile time. |
| **Metric** | throughput |
| **Hardware** | Thesis: Intel Core i7-7700K 4.20 GHz, 16 GB DDR4, GNU/Linux (otherwise unused machine). VMIL 2018 and ECOOP 2017: Intel Core i7-4870HQ, 16 GB DDR3, GNU/Linux; 10 runs per benchmark, min and max dropped, mean of the remaining 8. |
| **Compiler and flags** | LC built against the modified Gambit fork (bsaleil/gambit); the Makefile default target compiles LC with gsc -prelude "(declare (not safe))" and config-release.scm (README shows make debug); benchmark runs use --max-versions 5 with interprocedural specialization, tagging and eager flonum unboxing. Gambit v4.9.3: gsc -:m512000 -exe with prefix (declare (standard-bindings) (extended-bindings) (block)), plus (not safe) for unsafe mode. Chez Scheme 9.5.2 single-threaded build: compile-program, optimize-level 2 (safe) or 3 (unsafe), run with scheme --program. The optimize-level and (not safe) settings are stated in the thesis text, not in the committed harness. |
| **Adoption** | 33 stars, 1 fork; ECOOP 2017 (artifact-evaluated, DARTS 3.2.14), VMIL 2018, SFPW 2014 and SFPW 2015 papers, and Baptiste Saleil's 2019 Universite de Montreal PhD thesis |
| **Last commit** | 2019-05-11 |
| **Links** | [repository](https://github.com/bsaleil/lc) · [benchmark](https://raw.githubusercontent.com/bsaleil/bsaleil.github.io/master/docs/BaptisteSaleilPhD.pdf) |

## Verdict

In Saleil's 2019 PhD thesis (Intel Core i7-7700K, Linux, 38 Gambit-suite benchmarks, mean of 8 of 10 runs, GC and compile time excluded), Gambit v4.9.3 code takes 1.38x (safe) and 1.12x (unsafe) of LC's time on average and Chez 9.5.2 takes 1.27x and 1.09x, with fftrad4 the best case; including JIT compile time, LC takes 0.87x of Pycket's time (faster on 22 of 38). The peer-reviewed VMIL 2018 paper (i7-4870HQ) reports LC 1.47x faster than Gambit on average and faster on 26 of 38.

## Use it when

- Studying or reproducing BBV and interprocedural code specialisation for a dynamic language; the codebase is under 15 KLOC of Scheme written by one person.
- Benchmark-style Scheme programs with type-stable fixnum or flonum hot code (Gabriel and Gambit suite programs), where LC beat Gambit and Chez on more than half of 38 programs.
- Flonum-heavy loops over heterogeneous vectors, where eager unboxing gave the best rows (fftrad4: Gambit 3.29x to 4.03x and Chez 4.60x to 5.10x of LC's time).
- A reference design when building a baseline JIT without an interpreter or profiling tier: warm-up equals compile time.

## Skip it when

- Any production Scheme work: last commit 2019-05-11, one closed issue, single author, and it needs the author's Gambit fork on PATH at build and run time.
- Programs that need call/cc, full eval, threads, stack-overflow safety or vector bounds checks; LC omits them, and that omission is part of its speed edge over safe-mode Gambit and Chez.
- Code where unsafe-mode Gambit or Chez is acceptable: the average lead shrinks to 1.12x and 1.09x and LC loses on a large minority of benchmarks.
- Loop-heavy flonum vector code such as fft, where Pycket's tracing JIT was 3.40x faster than LC with heterogeneous vectors (1.63x with f64vectors).
- Platforms other than Linux x86-64.

## How it is fast

Lazy basic block versioning (BBV, Chevalier-Boisvert and Feeley): each basic block is compiled on first execution and specialised for the type context that reached it, so type checks seen once are removed from later code, with a version cap (the experiments use --max-versions 5). Interprocedural extensions propagate argument and return types through per-closure entry-point and return-point tables, and eager flonum unboxing keeps floats unboxed in registers and stack slots, which is where the largest wins (fftrad4, nucleic) come from.

## Compared with alternatives

Pick LC over Chez Scheme only to study or extend BBV for Scheme; Chez is the production choice and is within about 9% of LC in unsafe mode. Against Higgs, LC is the Scheme counterpart of the same Montreal BBV line of work and adds interprocedural entry/return-point specialisation and flonum unboxing.

## Integration

| | |
|---|---|
| **Form** | standalone JIT executable (bash launcher that runs gsc -i over compiled Gambit .o1 modules) |
| **Dependencies** | modified Gambit Scheme (github.com/bsaleil/gambit, fork of gambit/gambit, LGPL/Apache-2.0) built with --enable-single-host and its gsc on PATH; bash; Python 3 for the benchmark scripts |
| **Minimum toolchain** | the bsaleil/gambit fork (a 2019-era Gambit 4.9 tree); no other version documented |
| **Platforms** | Linux x86-64 only |
| **Thread safety** | single-threaded; the thesis says multi-tasking is not implemented |
| **Drop-in for the baseline** | partial: runs plain R5RS-style programs like the Gambit benchmark suite, but lacks first-class continuations, full eval, threads and safety checks that Gambit and Chez provide |

## Gotchas

- The 'excluding compilation time' numbers come from main.scm's --time mode, which runs the whole program once, resets globals and the stack, forces a GC and then times a second in-process run; Gambit and Chez are timed on their single run in a fresh process. That removes JIT cost as intended but also gives LC warmed memory, so the Fig. 6.16 ratios compare a warm second run with a cold first run.
- The committed harness runs Gambit and Chez with generic arithmetic and heterogeneous vectors (the fixnum/flonum-specialised fl+/fx+ macro block in prefix/Gambit.scm is commented out), and prefix/Gambit.scm has no (not safe) while prefix/ChezScheme.scm and the Chez compile command carry neither an optimize-level nor the (import (rnrs) ...) line the thesis cites; the thesis's safe/unsafe Gambit and optimize-level 2/3 Chez runs were configured outside the committed scripts, and run.py has every system except LC5 commented out with /home/bapt paths.
- README build steps clone the 'stable' branch (last updated 2018-08-29, before the 2019 thesis-era commits such as 'Improve div ops') and run `make debug`, which builds LC with gsc -debug and assertions on (config-debug.scm); the release target is plain `make`. This matters most for compile-inclusive timings such as the Pycket comparison.
- Correctness is checked: every benchmark's ok? predicate prints '\*\*\* wrong result \*\*\*' and run.py aborts on '\*\*\*' or any stderr output, so the timed runs did produce the expected results; the thesis does not say whether its averages are arithmetic or geometric means of the per-benchmark ratios, and the VMIL 2018 Pycket figure includes GC time while the thesis version excludes it.

## Known shortcomings

- Thesis and VMIL 2018 numbers (i7-7700K, flags stated, harness in tools/benchtimes): Gambit v4.9.3 takes 1.38x LC's time in safe mode but only 1.12x in unsafe mode, Chez 9.5.2 1.27x safe and 1.09x unsafe, so the lead is small once LC's skipped bounds, stack and polling checks are accounted for; GC and compile time excluded; the ECOOP 'up to 50%' compares LC's interprocedural mode with its own intraprocedural mode. Abandoned since 2019.
- Enricher: LC's --time (main.scm) runs the program once, resets globals, GCs and then times a second in-process run, while Gambit and Chez are timed on a single cold fresh-process run, so the thesis Fig. 6.16 ratios compare warm against cold. The committed harness also differs from the thesis setup: the Gambit prefix has (not safe), the Chez prefix has no optimize-level and no rnrs import, and the fl/fx specialised macros are commented out, so the baselines run generic arithmetic; the README builds the stable branch (2018-08-29) with make debug (asserts on); the thesis does not say whether means are arithmetic or geometric. Correctness checks are present (ok? predicate, run.py aborts on '\*\*\*').

## Caveats and trade-offs

Research JIT, last commit 2019-05-11, abandoned; x86-64 Linux only and needs the author's modified Gambit fork. The averages are modest and mode-dependent: LC skips vector bounds checks, stack-overflow checks and interrupt polling (the thesis cites about 15% polling overhead for Gambit), so the safe-mode leads (1.38x Gambit, 1.27x Chez) partly compare unequal safety, and in unsafe mode the lead shrinks to 1.12x and 1.09x with LC losing on a large minority of benchmarks; the Gambit and Chez times exclude GC and compilation time. VMIL 2018 lists missing features (no first-class continuations, limited eval). The repo commits no timing results; the numbers live in the papers and thesis (PDFs in github.com/bsaleil/bsaleil.github.io/docs; the dagstuhl and schemeworkshop.org copies were EGRESS_BLOCKED). The harness hard-codes the author's /home/bapt paths, has every system except LC5 commented out, and does not set Chez's optimize-level or Gambit's (not safe) mode, which only the thesis states. The ECOOP 2017 'up to 50% faster' figure is LC interprocedural versus LC intraprocedural, not versus Gambit or Chez. [retier] Thesis and VMIL 2018 numbers (i7-7700K, flags stated, harness in tools/benchtimes) give Gambit v4.9.3 1.38x LC's time in safe mode and 1.12x unsafe, Chez 9.5.2 1.27x and 1.09x, but LC's --time measures a warm second in-process run against cold fresh-process baselines, and the committed baseline prefixes use generic arithmetic without the thesis settings; GC and compile time excluded; the ECOOP 'up to 50%' compares LC's own modes. README builds the 2018 stable branch with make debug. Papers reachable only through the author's github.io repo via raw.githubusercontent.com. Abandoned since 2019.

Research JIT, Linux x86-64 only, written in Gambit Scheme and needs a modified Gambit (bsaleil/gambit) fork built first and gsc on PATH at build and run time; the build target is 'make debug'. Specialises by lazy basic-block versioning, so code size and entry-point table memory grow with version limits (the paper tracks code size and table sizes).

## Maintenance

Abandoned research artifact (last commit 2019-05-11) under BSD-3-Clause; usable for experiments and as a reference implementation of BBV, but it depends on an unmaintained Gambit fork and the committed harness needs hand edits (paths, system list, safety modes) to reproduce the thesis numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D: the author's papers and PhD thesis are checked into github.com/bsaleil/bsaleil.github.io/docs and reachable via raw.githubusercontent.com. The thesis (Universite de Montreal, May 2019, Section 6.5.1) compares LC against Gambit v4.9.3 and Chez Scheme v9.5.2 with flags stated (Gambit block/standard-bindings declarations and (not safe); Chez optimize-level 2/3, --program) on an Intel Core i7-7700K, and the harness is public in the repo (tools/benchtimes/run.py with gambit_no_options and chez_no_options, tools/benchtimes/prefix/Gambit.scm and ChezScheme.scm, tools/benchtimes/bench/\*.scm); the peer-reviewed VMIL 2018 paper independently reports 1.47x over Gambit on an i7-4870HQ.
- **Retiered** A to C: A to C (PISA and DASP precedent: harness flaw): the public tools/benchtimes harness times LC's second warm in-process run against single cold fresh-process runs of Gambit and Chez, and its committed baseline prefixes run generic arithmetic (no fl/fx specialisation, Gambit not in safe mode, Chez without optimize-level), so the thesis ratios (Gambit 1.38x LC's time safe, 1.12x unsafe; Chez 1.27x and 1.09x; i7-7700K) are not like for like; first-party thesis and VMIL 2018 paper, abandoned since 2019.
- **Verifier notes:** Upgrade D to A with verdict confirm: the papers the search agent could not reach are in the author's bsaleil.github.io repo, and the thesis gives Gambit v4.9.3 and Chez 9.5.2 comparisons with flags and CPU, backed by the public tools/benchtimes harness and the peer-reviewed VMIL 2018 result (1.47x over Gambit). Shortcomings to record: modest averages (1.12x/1.09x in unsafe mode), safety-check asymmetry in safe mode, GC and compile time excluded, harness with hard-coded paths and modes set outside it, abandoned since 2019. Baselines gambit/gambit and cisco/chezscheme are already in the catalog.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** unsafe-mode comparison including GC and compile time; cold-vs-cold run with the thesis baseline settings
- **Pages the verifier opened:**
  - <https://github.com/bsaleil/lc>
  - <https://github.com/bsaleil/lc/commits>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/README.md>
  - <https://github.com/bsaleil/lc/tree/master/documents>
  - <https://github.com/bsaleil/lc/tree/master/tools>
  - <https://github.com/bsaleil/lc/tree/master/tools/benchtimes>
  - <https://github.com/bsaleil/lc/tree/master/tools/benchtimes/prefix>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/ecoop17-paper.sh>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/run.py>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/prefix/Gambit.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/prefix/ChezScheme.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/Makefile>
  - <https://github.com/bsaleil?tab=repositories>
  - <https://github.com/bsaleil/bsaleil.github.io>
  - <https://github.com/bsaleil/bsaleil.github.io/tree/master/docs>
  - <https://raw.githubusercontent.com/bsaleil/bsaleil.github.io/master/docs/BaptisteSaleilPhD.pdf>
  - <https://raw.githubusercontent.com/bsaleil/bsaleil.github.io/master/docs/vmil18.pdf>
  - <https://raw.githubusercontent.com/bsaleil/bsaleil.github.io/master/docs/ecoop17.pdf>
  - <https://raw.githubusercontent.com/bsaleil/bsaleil.github.io/master/docs/sfpw15.pdf>
- **Sources the enricher read:**
  - <https://github.com/bsaleil/lc>
  - <https://github.com/bsaleil/lc/commits/master>
  - <https://github.com/bsaleil/lc/branches/all>
  - <https://github.com/bsaleil/lc/issues?q=is%3Aissue>
  - <https://github.com/bsaleil/lc/tree/master/tools/benchtimes/bench>
  - <https://github.com/bsaleil/gambit>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/README.md>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/lazy-comp.template>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/main.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/strat1.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/copy-with-declare.sh>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/config-release.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/config-debug.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/ecoop17-paper.sh>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/run.py>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/num-iters.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/prefix/Gambit.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/prefix/ChezScheme.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/prefix/LC.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/suffix/LC.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/suffix/Gambit.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/suffix/ChezScheme.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/bench/fib.scm>
  - <https://raw.githubusercontent.com/bsaleil/lc/HEAD/tools/benchtimes/bench/fftrad4.scm>
  - <https://raw.githubusercontent.com/bsaleil/bsaleil.github.io/master/docs/BaptisteSaleilPhD.pdf>
  - <https://raw.githubusercontent.com/bsaleil/bsaleil.github.io/master/docs/vmil18.pdf>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/bsaleil/lc`) · [data/wave12/enrich/raw/github_com_bsaleil_lc.json](../../../data/wave12/enrich/raw/github_com_bsaleil_lc.json) (enrichment confidence 0.75)

</details>
