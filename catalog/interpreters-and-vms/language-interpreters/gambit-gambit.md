# Gambit Scheme

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Scheme/C` · `Apache-2.0 OR LGPL-2.1` · 🟢 active

> Scheme-to-C compiler and runtime whose executables run about 2x faster than Guile 3.0.11 on the R7RS benchmark suite.

| | |
|---|---|
| **Beats** | Guile 3.0.11 (guild compile -O3); Chez Scheme 10.3.0 also in the same suite (Gambit is slower than Chez on aggregate) |
| **Claimed result** | From all.csv (derived from page data): gambitc-v4.9.7 is faster than guile-3.0.11 on 45 of 53 benchmarks with numeric times for both under the same name, geomean about 1.95x. Examples: fib:40:5 3.46268 s vs 6.489886582 s; tak:40:20:11:1 1.968017 vs 3.113433651; mbrot:75:1000 4.223346 vs 22.496891153; nucleic:50 1.545574 vs 5.551796865; ctak:32:16:8:1 3.573319 vs 83.031008426; cat:50 2.095778 vs 15.986089402. Slower than Guile on string:500000:100 (3.197634 vs 0.204681098), pi:50:500:50:100 (0.76942 vs 0.107659156), gcbench:20:1 (8.414929 vs 1.512640708). Versus chez-10.3.0+r7rs the same method gives geomean about 0.79x (Gambit faster in 17 of 54). |
| **Workload** | ecraven/r7rs-benchmarks: wall-clock seconds of about 55 R7RS benchmark programs (Gabriel, Kernighan and Van Wyk, Larceny set: fib, tak, ctak, mbrot, nucleic, ray, array1, cat, etc.), Gambit gsc -exe executable versus Guile precompiled with guild compile -O3. |
| **Metric** | throughput |
| **Hardware** | Intel Core i3-N305 @ 3.8 GHz, 48 GB RAM, Arch Linux packages (per the suite's index.html); results logs show host kernel Linux 6.16.8-arch3-1 x86_64; Gambit run dated 2026-02-03 (re-run after the commit 'Run with correct gambit-c version', same host and kernel), Guile run 2026-01-16. |
| **Compiler and flags** | bench script: Gambit 'gsc -o &lt;out&gt; -exe &lt;file&gt;' with no extra flags (safe mode, no 'declare (not safe)'); the C compiler is gcc (named in results.GambitC; version and the packaged gsc default C flags not stated); Guile 'guild compile -O3' then run with GC_INITIAL_HEAP_SIZE=100000000; Chez '--optimize-level 2 --program'; versions in all.csv gambitc-v4.9.7, guile-3.0.11, chez-10.3.0+r7rs; one run per benchmark (NB_RUNS=1). Packages are the Arch Linux packages per README. |
| **Adoption** | 1.4k stars; widely used Scheme-to-C compiler (Gerbil Scheme runs on it) |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/gambit/gambit) · [benchmark](https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/all.csv) |

## Verdict

ecraven/r7rs-benchmarks (about 55 Larceny/Gabriel programs, one run each, Intel Core i3-N305, Arch Linux packages): Gambit v4.9.7 executables built with 'gsc -o &lt;out&gt; -exe' in safe mode beat Guile 3.0.11 (guild compile -O3) on 45 of 53 shared rows, geomean 1.95x (1.78x excluding the call/cc rows ctak, fibc and cpstak), while Chez 10.3.0 is about 1.26x faster than Gambit overall; all ratios derived from all.csv.

## Use it when

- AOT-compiled Scheme programs where Guile, Chicken, Cyclone, Larceny or Racket is the current choice and throughput matters: in ecraven/r7rs-benchmarks Gambit 4.9.7 is about 1.95x faster than Guile 3.0.11 (median 1.95x), 2.7x faster than Chicken 5.4.0 and 1.45x faster than Racket 9.0 by geomean (derived from page data)
- Floating-point-heavy kernels (fft, mbrot, nucleic, ray, simplex, pnpoly), where Gambit is 3-5.6x faster than Guile and also ahead of Chez 10.3.0
- Code using call/cc or deep continuations (ctak 23x and fibc 17x faster than Guile)
- Shipping a standalone native executable or embedding Scheme in a C program, or targeting JavaScript from the same source
- As the base for Gerbil Scheme, which runs on Gambit

## Skip it when

- When raw speed is the only criterion and Chez Scheme is an option: Chez is faster on aggregate (Gambit geomean about 0.79x of Chez speed, faster on 17 of 54 rows), and much faster on gcbench (9x), graphs (4.6x) and ctak/fibc (about 4x)
- Bignum-heavy work: no GMP integration (issue #761, open bounty, reports about a 100x fixnum-to-bignum gap); pi and chudnovsky run 7.1x and 2.9x slower than Guile
- String-building and allocation-heavy GC workloads: string:500000:100 is 15.6x slower than Guile (3.20 s vs 0.20 s, about the same as Chez) and gcbench 5.6x slower
- Multicore parallelism: the manual says Scheme threads are managed by Gambit's runtime, not OS threads, and at most one runs at a time (an --enable-smp configure option exists but is not the default)
- Very large single source files: the suite's compiler.scm failed because gcc's cc1 was killed while compiling the generated C (COMPILEERROR), and INSTALL.txt warns single-host builds with --enable-gcc-opts take about 2 GB and over 10 minutes

## How it is fast

Whole-module compilation to C with --enable-single-host, which emits each Scheme module as a single C function; INSTALL.txt says this roughly doubles interpreter speed, and that GCC's computed gotos cut execution time by about 35%. With (standard-bindings), (extended-bindings) and (block) declarations the compiler can inline primitives such as + and car and treat file-local definitions as constants; proper tail calls are kept without relying on C TCO. Floating-point code is strong: in the suite Gambit beats even Chez on fft (2.6x), mbrot (1.7x) and pnpoly (1.4x) (derived from page data).

## Compared with alternatives

Pick Gambit over Bigloo or Loko when you want the fastest of the three on general Scheme code: in the same all.csv Gambit is about 1.28x faster than Bigloo 4.6a and 1.22x faster than Loko 0.12.1 by geomean (derived from page data), plus it has a C embedding story and a JS target; pick Chez Scheme (already catalogued) instead when GC-heavy or continuation-heavy throughput matters more than C output.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | a C compiler (GCC strongly recommended for computed gotos; clang works); OpenSSL optional |
| **Minimum toolchain** | GCC 3.3 or later recommended by INSTALL.txt; any C99-era compiler for the generated C |
| **Platforms** | Linux, macOS and Windows (CI badge), portable C output for other Unix-likes; JavaScript target via -target js |
| **Thread safety** | Green (runtime-managed) SRFI-18/21 threads, at most one running per VM; hash tables are not safe for concurrent modification by Gambit threads (issue #322, open) |
| **Drop-in for the baseline** | partial — portable R7RS programs compile with gsc, but Guile modules, GOOPS, Guile's FFI and its JIT/REPL workflow do not carry over |

## Gotchas

- The measured numbers depend on the suite's GambitC-prelude.scm, which adds (declare (standard-bindings) (extended-bindings) (block)); Gambit's defaults are (not standard-bindings) and (not extended-bindings), so plain code without these declarations will not inline primitives and will be slower. Safe mode was kept; (not safe) and (fixnum) are faster still but change semantics.
- Harness and version sensitivity: one run per benchmark (NB_RUNS=1) on an Intel i3-N305; the suite first ran a v4.9.5-78 Gambit on 2026-01-16 (after switching the default from 'gambitc' to 'gsc', and Arch renames gsc to gambitc because of a Ghostscript clash), then re-ran v4.9.7 on 2026-02-03; v4.9.7 was about 1.11x faster by geomean than the earlier build, up to 4.3x on fft and 2.5x on mbrot (derived from the two results.GambitC revisions). The current release v4.9.8 (2026-08-09) is unmeasured.
- Performance depends heavily on configure options: README recommends --enable-single-host --enable-march=native --enable-dynamic-clib for best performance, and INSTALL.txt calls --enable-single-host 'highly recommended' (about 2x interpreter speed), so a plain ./configure build will be slower than the Arch package used in the suite (the archived 4.9.4 PKGBUILD and the 4.9.5 options quoted in issue #854 both use --enable-single-host and --enable-gcc-opts; the 4.9.7 PKGBUILD could not be fetched).
- Open performance anomaly issue #422 (2019): ##unchecked-structure-ref measured about 7x slower than the checked ##direct-structure-ref in an indirect-call loop.

## Known shortcomings

- ecraven/r7rs-benchmarks all.csv (Intel Core i3-N305, 48 GB, Arch Linux): 45 of 53 rows faster than Guile 3.0.11, geomean 1.953x (derived from page data), but slower than Chez Scheme (0.79x), 8 rows slower than Guile (string 15.6x slower), gcc version and gsc default C flags not stated, and the Gambit re-run of 2026-02-03 was not interleaved with the Guile run of 2026-01-16.
- Enricher: 1.95x geomean over Guile falls to 1.78x without the call/cc rows (ctak, fibc, cpstak); 0.79x of Chez, 1.28x over Bigloo, 1.22x over Loko (derived from all.csv). The numbers depend on the suite's GambitC-prelude.scm declarations (standard-bindings, extended-bindings, block); Gambit's defaults are slower. One run per benchmark; the January 2026 run used v4.9.5-78 and the February rerun v4.9.7, about 1.11x faster by geomean (fft 4.3x), so results are version-sensitive. compiler.scm failed with COMPILEERROR (cc1 killed). No GMP (issue #761), so bignum rows are slow; green threads only.

## Caveats and trade-offs

Independent community suite run on an Intel Core i3-N305 with Arch packages; the page says 'No guarantees for any of the numbers', each benchmark runs once, and the gcc version and default C flags behind gsc are not stated, so tier B not A. Gambit was re-run on 2026-02-03 while Guile and Chez ran on 2026-01-16 (same host and kernel). The 1.95x geomean is a derived figure over rows matched by exact benchmark name; floating-point rows named with '35.' versus '35.0' in different implementations were not paired. Gambit's own bench/ directory commits no comparison results, and the Gambit repo makes no benchmark claim. Chez Scheme (already listed) beats Gambit on aggregate (geomean about 0.79 derived), and Gambit is slower than Guile on 8 of 53 rows (pi, string, dynamic, graphs, paraffins, chudnovsky, nboyer, gcbench), much slower on string and bignum rows. Lua was not part of the suite, so no Lua comparison is recorded. Gambit has one COMPILEERROR row ('compiler': gcc's cc1 was killed while compiling the generated C) in all.csv, excluded from the geomean.

Compiles Scheme to C and a native executable (gsc -exe) with an interpreter and REPL (gsi). Safe mode is the benchmarked default; unsafe declarations would run faster. Dual-licensed; the repo root holds LICENSE-2.0.txt and LGPL.txt (version 2.1) and the README states no licence, so the SPDX expression is inferred from those files.

## Maintenance

Actively maintained (commits through 2026-10-02, v4.9.8 tagged 2026-08-09); dual-licensed Apache-2.0 or LGPL-2.1 per the LICENSE-2.0.txt and LGPL.txt files, so copyable, though the README itself states no licence terms.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (ecraven/r7rs-benchmarks: public bench script and src/ programs, gambitc-v4.9.7 'gsc -o &lt;out&gt; -exe', CPU Intel i3-N305 stated in the repo's index.html), but gsc compiles through gcc (named only in an error line of results.GambitC) with the Arch package's default C flags and no stated gcc version, so it falls just short of A.
- **Verifier notes:** All quoted numbers and derived ratios re-computed from all.csv (45 of 53 faster than Guile, geomean 1.953x; versus Chez 0.794x, faster on 17 of 54). Shortcomings: slower than already-listed Chez on aggregate, slower than Guile on 8 rows (string 15.6x slower, pi 7.1x, gcbench 5.6x), single run on a low-power i3-N305, gcc version unstated. Licence kept as Apache-2.0 OR LGPL-2.1: the repo root ships LICENSE-2.0.txt and LGPL.txt (v2.1) and GitHub shows both, but no README text states the dual-licence terms and source headers say 'All Rights Reserved'.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** interleaved run with stated flags; repeated runs with default declarations on one version
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/all.csv>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/README.org>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/bench>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/index.html>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/results.Guile>
  - <https://github.com/ecraven/r7rs-benchmarks>
  - <https://github.com/ecraven/r7rs-benchmarks/commits>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/results.GambitC>
  - <https://github.com/gambit/gambit>
  - <https://github.com/gambit/gambit/commits>
  - <https://raw.githubusercontent.com/gambit/gambit/HEAD/README.md>
  - <https://raw.githubusercontent.com/gambit/gambit/HEAD/LGPL.txt>
  - <https://raw.githubusercontent.com/gambit/gambit/HEAD/LICENSE-2.0.txt>
  - <https://raw.githubusercontent.com/gambit/gambit/HEAD/INSTALL.txt>
  - <https://raw.githubusercontent.com/gambit/gambit/HEAD/lib/_kernel.scm>
  - <https://raw.githubusercontent.com/gambit/gambit/HEAD/doc/gambit.txi>
- **Sources the enricher read:**
  - <https://github.com/gambit/gambit>
  - <https://github.com/gambit/gambit/commits>
  - <https://github.com/gambit/gambit/tags>
  - <https://raw.githubusercontent.com/gambit/gambit/HEAD/README.md>
  - <https://raw.githubusercontent.com/gambit/gambit/HEAD/INSTALL.txt>
  - <https://raw.githubusercontent.com/gambit/gambit/HEAD/doc/gambit.txi>
  - <https://github.com/gambit/gambit/issues?q=is%3Aissue+performance>
  - <https://github.com/gambit/gambit/issues/761>
  - <https://github.com/gambit/gambit/issues/422>
  - <https://github.com/gambit/gambit/issues/854>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/all.csv>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/bench>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/README.org>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/index.html>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/results.GambitC>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/f6ea76c/results.GambitC>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/GambitC-prelude.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/Guile-prelude.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/common.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/common-postlude.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/string.scm>
  - <https://github.com/ecraven/r7rs-benchmarks/commits>
  - <https://github.com/ecraven/r7rs-benchmarks/commits/master/results.GambitC>
  - <https://raw.githubusercontent.com/archlinux/svntogit-community/packages/gambit-c/trunk/PKGBUILD>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/gambit/gambit`) · [data/wave12/enrich/raw/github_com_gambit_gambit.json](../../../data/wave12/enrich/raw/github_com_gambit_gambit.json) (enrichment confidence 0.78)

</details>
