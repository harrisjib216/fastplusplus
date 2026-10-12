# Loko Scheme

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Scheme` · `EUPL-1.2` · 🟢 active

> Self-hosted R6RS/R7RS Scheme compiling ahead of time to static amd64 binaries; beats Guile 3 on most r7rs-benchmarks.

| | |
|---|---|
| **Beats** | Guile 3.0.11 (guild compile -O3); Chez Scheme 10.3.0 also in the same suite (Loko is slower than Chez on aggregate) |
| **Claimed result** | From all.csv (derived from page data): loko-0.12.1 is faster than guile-3.0.11 on 48 of 51 shared benchmarks with numeric results, geomean about 1.62x (about 1.52x over 45 rows when the floating-point rows fft, mbrot, mbrotZ, pnpoly, ray and simplex are left out). Examples: tak:40:20:11:1 1.6679999828338623 s vs 3.113433651 s; fib:40:5 3.927000045776367 vs 6.489886582; ctak:32:16:8:1 19.98699951171875 vs 83.031008426; mbrot:75:1000 6.51200008392334 vs 22.496891153; cat:50 3.4140000343322754 vs 15.986089402; paraffins:23:10 1.7589999437332153 vs 3.866057371. Slower: string:500000:100 5.241000175476074 vs 0.204681098; pi:50:500:50:100 156.49200439453125 vs 0.107659156; chudnovsky:50:500:50:1000 also slower. Versus chez-10.3.0+r7rs geomean about 0.65x (Loko faster in 22 of 52). Loko's README adds an own startup claim: REPL starts in 1.2 ms +/- 0.2 ms on an AMD 3950X per hyperfine (no baseline named) and 'does fairly well in the R7RS benchmarks'. |
| **Workload** | ecraven/r7rs-benchmarks: wall-clock seconds of R7RS benchmark programs, Loko ahead-of-time compiled static binary (loko -std=r7rs -ftarget=linux --compile) versus Guile precompiled with guild compile -O3. |
| **Metric** | throughput |
| **Hardware** | Intel Core i3-N305 @ 3.8 GHz, 48 GB RAM, Arch Linux packages (per the suite's index.html); results logs show host kernel Linux 6.16.8-arch3-1 x86_64; Loko and Guile runs dated 2026-01-16. |
| **Compiler and flags** | bench script: 'loko -std=r7rs -ftarget=linux --compile &lt;file&gt; --output &lt;out&gt;' (native code, no C compiler involved); Guile 'guild compile -O3' with GC_INITIAL_HEAP_SIZE=100000000; Chez '--optimize-level 2 --program'; versions loko-0.12.1, guile-3.0.11, chez-10.3.0+r7rs; one run per benchmark (NB_RUNS=1). |
| **Adoption** | 64 stars (GitLab) |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://gitlab.com/weinholt/loko) · [benchmark](https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/all.csv) |

## Verdict

Independent ecraven/r7rs-benchmarks all.csv (one run per benchmark, Intel Core i3-N305, Arch Linux, January 2026; timed by each program's own jiffy clock, so start-up is excluded): loko-0.12.1 static binaries beat guile-3.0.11 (guild compile -O3) on 48 of 51 shared benchmarks, geomean about 1.62x (1.52x without the float rows), and run at about 0.65x of chez-10.3.0's speed (faster on 22 of 52) (derived from page data). Three float benchmarks gave wrong answers and earley ran out of heap, so they have no time.

## Use it when

- Small R6RS/R7RS command-line tools on Linux/amd64 that should ship as one static binary with no libc or C toolchain and start in about a millisecond.
- Call-, closure- and allocation-heavy symbolic code where all.csv shows Loko well ahead of Guile 3.0.11: ctak 4.15x, fibc 3.97x, tak 1.87x, fib 1.65x (derived from page data).
- Port-based text I/O in pure Scheme: cat 4.68x and wc 4.27x faster than Guile in the same run (derived from page data).
- Hobby-OS, bare-metal or driver work in Scheme: multiboot2 and EFI boot, AHCI/IDE disks, e1000e/virtio/rtl81x9 NICs, USB 1/2 (UHCI/EHCI) and a TCP/IP stack.

## Skip it when

- Floating-point code: inexact numbers are single precision only; nucleic, sum1 and sumfp returned wrong answers in the suite, and subnormals such as 5e-40 cannot be read (open issue #60).
- Bignum or exact-arithmetic work: pi takes 156.5 s against Guile's 0.108 s and chudnovsky 28.0 s against 0.124 s; repeated string-append is also slow (string 5.24 s vs 0.205 s).
- Programs that need C libraries (no FFI), platforms other than amd64, multicore parallelism (fibers are cooperative and not parallel within a Loko process), or eval over compiled libraries (open issue #29).
- Peak throughput when Chez Scheme is an option: Loko runs at about 0.65x of Chez 10.3.0's speed on the same suite and is 16x-22x slower on call/cc-heavy fibc and ctak (derived from page data).
- Memory-hungry programs without tuning: the heap has a fixed size (LOKO_HEAP, in megabytes), and earley died with 'out of heap memory' in the benchmark run.

## How it is fast

A native-code compiler (closure conversion, cp0-style inlining, type inference, loop and letrec passes in compiler/) emits amd64 machine code directly, with tagged immediates for fixnums, chars and flonums, so procedure calls, closures and allocation are compiled rather than run on a bytecode VM as in Guile. Inexact numbers are 32-bit IEEE singles packed into the upper half of a tagged 64-bit word (tag #b01001111, shift 32 in arch/amd64/tagging.sls), so float arithmetic never allocates; this is cheaper than Guile's and Chez's 64-bit doubles but less precise. Whole programs are compiled together into one static binary with eval disabled by default.

## Compared with alternatives

Gambit and Bigloo match Loko's lead over Guile in the same suite (Bigloo about 1.62x geomean) and add a C FFI, double-precision flonums and more platforms, and Chez Scheme (catalogued) is about 1.5x faster than Loko overall; pick Loko only when you want static amd64 binaries with no C toolchain or libc, millisecond start-up, or a Scheme that runs on bare hardware.

## Integration

| | |
|---|---|
| **Form** | standalone AOT compiler and runtime; programs become static ELF binaries (loko --compile) |
| **Dependencies** | none at run time (static binary, no libc); building from git needs Chez Scheme 9.5+ to bootstrap, Akku 1.0.0+ and GNU make; the release tarball includes a prebuilt binary and the Akku packages |
| **Minimum toolchain** | Chez Scheme 9.5+ for bootstrapping from git; nothing for the release tarball |
| **Platforms** | amd64 only: Linux, NetBSD and bare metal (Multiboot/Multiboot2, EFI); virtual machines must support alignment checks (#AC) |
| **Thread safety** | One heap per Loko process; fibers are call/cc-based, cooperative and never run in parallel; port access is not multi-fiber safe (open issue #20) and dynamic-wind is broken under fibers (manual, issue #26) |
| **Drop-in for the baseline** | partial — runs portable R6RS and R7RS programs (passes almost all of Racket's R6RS and Chibi's R7RS test suites), but not Guile modules or C bindings, flonums are single precision, and compilation is ahead of time only |

## Gotchas

- Harness flaw: none of the six float benchmarks that passed checks numeric precision. fft transforms a vector of 65,536 zeros (input '100 65536 0.0 0.0', so 0.0 is right at any precision), ray always returns 'ok, mbrot checks the iteration count of one corner pixel, and pnpoly and simplex compare integers. Loko computed them in unboxed single precision while Guile and Chez used doubles, so those rows (1.21x-3.45x over Guile; fft 1.93x faster even than Chez) compare different arithmetic. Without them the Guile geomean is about 1.52x, not 1.62x (derived from page data).
- Harness asymmetry: the bench script runs Guile with GC_INITIAL_HEAP_SIZE=100000000 but leaves Loko at its default fixed heap; earley hit 'Fatal error: out of heap memory' after 19 s and has no Loko time. Each benchmark ran once (NB_RUNS=1).
- Version drift: the suite measured loko-0.12.1 (tagged 2023-09-26). 0.13.0 (2026-06-27) fixes a 'miscompilation due to bad type inference on bitwise-and', so the measured compiler had a known codegen bug and head may time differently.
- Open bugs worth knowing: stack overflows kill the process (#3), the code generator crashes on bad arities (#10), a wrong check is inserted for undefined variables (#38), and the TCP/IP stack gets wedged easily (#58, also noted in the 0.13.0 NEWS).

## Known shortcomings

- ecraven/r7rs-benchmarks all.csv (Intel Core i3-N305, 48 GB, Arch Linux): 48 of 51 rows faster than Guile 3.0.11, geomean 1.617x, 1.52x without the float rows (derived from page data); INCORRECT results on sumfp, nucleic and sum1 look like single-precision floats, earley ran out of heap, the pi row took 156 s vs 0.108 s, and it is slower than Chez Scheme (0.65x).
- Enricher: none of the six float benchmarks that passed checks numeric precision (fft transforms zeros, ray always returns ok, mbrot checks one corner pixel's iteration count), and Loko computed them in unboxed single precision while Guile and Chez used doubles, so those rows (1.21x-3.45x over Guile) compare different arithmetic; without them the Guile geomean is about 1.52x (derived from page data). The bench script gives Guile GC_INITIAL_HEAP_SIZE=100000000 but leaves Loko at its default fixed heap (earley ran out of heap). The suite measured loko-0.12.1 while 0.13.0 (2026-06-27) fixes a miscompilation from bad type inference on bitwise-and. Open bugs: stack overflows kill the process (#3), codegen crashes on bad arities (#10), wrong check for undefined variables (#38). EUPL-1.2 copyleft.

## Caveats and trade-offs

Independent community suite run once per benchmark on an Intel Core i3-N305 with Arch packages; the page says 'No guarantees for any of the numbers'. Loko has INCORRECT results on three floating-point rows (sumfp returned 4.99873677312e11, nucleic 33.797950744628906, sum1 15794.6416015625, all consistent with single-precision flonum arithmetic) and an out-of-heap-memory crash on earley, all excluded from the geomean; the float rows that passed (fft, mbrot, pnpoly, ray, simplex) may also have run at reduced precision and flatter Loko, and without those float rows the derived geomean drops to about 1.52x. Pathological on bignum arithmetic: pi:50:500:50:100 takes 156.5 s versus 0.108 s for Guile. Chez Scheme (already listed) beats Loko on aggregate (about 0.65x derived). The loko 0.12.1 result in all.csv may not match the current head. Lua not part of the suite. [retier] ecraven/r7rs-benchmarks (Intel Core i3-N305, 48 GB, Arch Linux, one run each): 48 of 51 rows faster than Guile 3.0.11, geomean 1.617x, but Loko uses unboxed single-precision flonums and no float benchmark checks precision, so the float rows (1.21x-3.45x) compare different arithmetic; about 1.52x without them (derived from page data). INCORRECT results on sumfp, nucleic and sum1; earley ran out of Loko's default fixed heap while Guile got a 100 MB initial heap; pi 156 s vs 0.108 s; slower than Chez (0.65x). Measured loko-0.12.1, before the 0.13.0 bitwise-and miscompilation fix. EUPL-1.2 copyleft.

Written purely in Scheme plus some assembler; AMD64 only on Linux, NetBSD or bare hardware; no FFI; fixed heap size (LOKO_HEAP); ahead-of-time compilation only (no compiler in eval); inexact numbers use IEEE single precision only (per README).

## Maintenance

Actively maintained by one author (0.13.0 released 2026-06-27, commits to 2026-10-03) under EUPL-1.2-or-later, a copyleft licence; fine as a toolchain for amd64 tools and OS experiments, but its single-precision flonums and slow bignums rule it out for numeric work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B: ecraven/r7rs-benchmarks publishes the bench script (loko_comp: 'loko -std=r7rs -ftarget=linux --compile', guile_comp: 'guild compile -O3') and the src/ programs, all.csv names loko-0.12.1 and guile-3.0.11, and the repo's index.html states the CPU (Intel Core i3-N305 @ 3.8 GHz); Loko emits machine code itself with no C toolchain, so code, compiler, flags and CPU model are all stated.
- **Verifier notes:** All quoted numbers re-computed from all.csv (48 of 51 faster than Guile, geomean 1.617x; versus Chez 0.648x, faster on 22 of 52); the third slower row (chudnovsky) was missing from the record. Upgraded to A because the CPU model is on the suite's index.html and Loko needs no C compiler; shortcomings: three INCORRECT float rows that look like single-precision flonums (possible flattering of passing float rows), earley out of heap, catastrophic bignum pi row, slower than already-listed Chez, single run. GitLab API confirms EUPL-1.2, 64 stars, not a fork, last commit 2026-10-03.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** correct float results on the failing rows; double-precision float rows on the fixed compiler
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/all.csv>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/README.org>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/bench>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/index.html>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/results.Guile>
  - <https://github.com/ecraven/r7rs-benchmarks>
  - <https://github.com/ecraven/r7rs-benchmarks/commits>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/results.Loko>
  - <https://gitlab.com/api/v4/projects/weinholt%2Floko?license=true>
  - <https://gitlab.com/api/v4/projects/weinholt%2Floko/repository/commits?per_page=3>
  - <https://gitlab.com/weinholt/loko/-/raw/master/README.md>
- **Sources the enricher read:**
  - <https://gitlab.com/weinholt/loko/-/raw/master/README.md>
  - <https://gitlab.com/weinholt/loko/-/raw/master/NEWS.md>
  - <https://gitlab.com/weinholt/loko/-/raw/master/arch/amd64/tagging.sls>
  - <https://gitlab.com/weinholt/loko/-/raw/master/runtime/flonums.sls>
  - <https://gitlab.com/weinholt/loko/-/raw/master/Documentation/manual/usage.texi>
  - <https://gitlab.com/weinholt/loko/-/raw/master/Documentation/manual/int-concurrency.texi>
  - <https://gitlab.com/weinholt/loko/-/raw/master/Documentation/manual/introduction.texi>
  - <https://gitlab.com/api/v4/projects/weinholt%2Floko/repository/tree?recursive=true>
  - <https://gitlab.com/api/v4/projects/weinholt%2Floko/repository/tags?per_page=6>
  - <https://gitlab.com/api/v4/projects/weinholt%2Floko/issues?state=opened>
  - <https://gitlab.com/api/v4/projects/weinholt%2Floko/repository/commits?per_page=3>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/all.csv>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/bench>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/results.Loko>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/index.html>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/Loko-prelude.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/Loko-postlude.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/Guile-prelude.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/mbrot.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/fft.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/string.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/pi.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/ray.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/simplex.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/pnpoly.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/inputs/fft.input>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/inputs/mbrot.input>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/inputs/mbrotZ.input>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/inputs/pnpoly.input>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/inputs/ray.input>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/inputs/simplex.input>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/inputs/sumfp.input>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://gitlab.com/weinholt/loko`) · [data/wave12/enrich/raw/gitlab_com_weinholt_loko.json](../../../data/wave12/enrich/raw/gitlab_com_weinholt_loko.json) (enrichment confidence 0.82)

</details>
