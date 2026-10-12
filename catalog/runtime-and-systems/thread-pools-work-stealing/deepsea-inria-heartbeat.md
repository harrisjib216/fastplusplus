# Heartbeat Scheduling (deepsea-inria/heartbeat)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔴 abandoned

> Research prototype of Heartbeat Scheduling (PLDI 2018): amortizes task creation against Cilk Plus-style eager spawning without manual grain-size tuning.

| | |
|---|---|
| **Beats** | Cilk Plus (PBBS implementations) |
| **Claimed result** | Snippet only (paper not opened): on ten PBBS benchmarks, the heartbeat prototype generally matched or beat the Cilk Plus PBBS implementations on 40 cores; task-creation overheads stayed under 5% versus sometimes over 25% for PBBS granularity control. The record's '16-queens 1.86x on a dual dual-core machine' could not be traced to this paper. |
| **Workload** | Nested-parallel benchmarks including 16-queens (PLDI 2018 paper). |
| **Metric** | throughput |
| **Adoption** | 22 stars |
| **Last commit** | 2022-07-01 |
| **Links** | [repository](https://github.com/deepsea-inria/heartbeat) |

## Verdict

Only WebSearch snippets of the PLDI 2018 paper were available: on about ten PBBS benchmarks at 40 cores the heartbeat prototype generally matched or beat the Cilk Plus PBBS implementations, with task-creation overhead under 5% versus sometimes over 25% for PBBS granularity control. Benchmarks were built with GCC -O2 -march=native, and the hardware was 40 cores per the README samples, CPU model not stated in the repo. The paper PDF (chargueraud.org, inria.hal.science) was EGRESS_BLOCKED, so no per-benchmark number was confirmed.

## Use it when

- Studying or reproducing the PLDI 2018 heartbeat results against Cilk Plus PBBS on a many-core x86-64 Linux box (the paper used 40 cores).
- Prototyping granularity-control ideas for very fine-grained nested parallelism (recursive divide and conquer such as fib, with nested parallel loops) where manual cutoffs are hard to choose.
- Comparing work-stealing variants (Chase-Lev, steal-one, steal-half, heartbeat) under one harness with pview visualizations.

## Skip it when

- Production code: there is no license file (reference only), the last commit was in 2022, and it is a research prototype.
- Ordinary C++ code: you must rewrite it as vertex state machines or in the pcfg DSL, and the interpreter adds overhead that the paper's later work (TPAL, PLDI 2021) set out to remove.
- Non-x86 targets: timing uses inline rdtsc and PAUSE assembly, and the build hard-codes -DTARGET_X86_64 -m64 -march=native.
- If you need a maintained heartbeat-style runtime, Spice (Zig) and chili (Rust) are active descendants; for C++ use TBB, Taskflow or a sibling pool.
- Building is not self-contained: you need the external deepsea-inria repos (cmdline, chunkedseq, sptl, cactus-stack, pbbs-include), a Cilk Plus runtime for baselines, and GCC 7-era -fcilkplus, which modern GCC removed.

## How it is fast

Heartbeat scheduling runs code sequentially by default and only promotes the oldest latent parallel task (the outermost spawn point) into a real, stealable task about once every kappa cycles (the 'heartbeat', default 30 us via `-promotion_threshold`). Task-creation cost is therefore bounded to a small fraction of the work no matter how fine-grained the program is, and promoting outermost work keeps the span bounded. That replaces the manual cutoffs or granularity control that PBBS uses with Cilk. The heartbeat is checked by polling rdtsc against a per-worker deadline (fuel.hpp), and the repo includes several work-stealing back ends (std::deque per worker with steal requests, Chase-Lev concurrent deques, steal-half).

## Compared with alternatives

Pick it over Spice or chili only when you want the original PLDI 2018 C++ artifact with Cilk Plus PBBS baselines. For anything you would ship, Spice (Zig) or chili (Rust) implement the same heartbeat idea with maintained code and published numbers, and Nowa or Staccato are the C++ continuation-stealing options with Cilk comparisons.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | deepsea-inria cmdline, chunkedseq, sptl, cactus-stack, pbbs-include (benchmarks); optional hwloc, tcmalloc (gperftools), Cilk Plus runtime for baselines; pthread |
| **Minimum toolchain** | gnu++1y (C++14) with GCC; nix shell pins gcc7; clang possible with -latomic |
| **Platforms** | x86-64 Linux only (rdtsc inline asm, /proc/cpuinfo) |
| **Thread safety** | Its own multi-worker runtime; launched via heartbeat::launch with -proc N; no documented reentrancy or embedding guarantees |
| **Drop-in for the baseline** | no |

## Gotchas

- The heartbeat period is converted from microseconds to TSC cycles using the 'cpu MHz' line of /proc/cpuinfo (default 1.2 GHz if absent), which is the current and not the nominal frequency. Under frequency scaling the real promotion interval can differ from the requested one.
- README sample output reports only absolute exectime and utilization; no comparison is shown in the repo. Cilk comparisons have to be reproduced via bench/bench.ml (pbench/prun/pplot) yourself.
- The example code comments note that a lambda launch path crashes GCC; launch_interpreter is the workaround.
- PBBS input files under _data/ are not in the repo and must be generated separately.

## Known shortcomings

- x86-64 Linux only (rdtsc). The heartbeat period is derived from the current 'cpu MHz' in /proc/cpuinfo, so it is skewed under frequency scaling. Needs external deepsea repos and gcc7 with -fcilkplus. No license file; paper PDF blocked, numbers snippet only.

## Caveats and trade-offs

No license file (LICENSE, LICENSE.txt, LICENSE.md and COPYING all 404), so reference only. Paper PDF EGRESS_BLOCKED; numbers come from search snippets. The '16-queens 1.86x' figure in the original record is unverified and may come from a different paper. The README shows no comparison with Cilk, OpenMP or TBB. Research prototype with interpretive overheads; Cilk Plus is obsolete. Last commit 2022-07-01.

Prototype C++ library for the Heartbeat algorithm; research quality.

## Maintenance

Abandoned since 2022-07-01 with no license file, so reference only; useful as the source artifact of the heartbeat scheduling idea rather than as a library to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The repo README has only absolute exectime/utilization sample output, with no Cilk or OpenMP comparison. The PLDI 2018 paper (chargueraud.org, irif.fr, HAL) is EGRESS_BLOCKED, and WebSearch snippets say only that heartbeat 'generally matched or beat' the Cilk Plus PBBS programs on 40 cores, with overheads under 5% versus over 25%. No per-benchmark number could be confirmed, so the B rests on an unopened paper and is capped at C until someone reads it.
- **Verifier notes:** Real peer-reviewed work (PLDI 2018) and a candidate to go back to B if a retier can open the paper (try a raw.githubusercontent copy). The record's specific number looks misattributed.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/deepsea-inria/heartbeat>
  - <https://github.com/deepsea-inria/heartbeat/commits/master>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/deepsea-inria/heartbeat>
  - <https://github.com/deepsea-inria/heartbeat/tree/master/include>
  - <https://github.com/deepsea-inria/heartbeat/tree/master/bench>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/README.md>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/bench/Makefile>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/bench/shell.nix>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/bench/bench.ml>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/bench/promotion-threshold-experiment.md>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/include/heartbeat.hpp>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/include/scheduler.hpp>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/include/cycles.hpp>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/include/fuel.hpp>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/include/machine.hpp>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/include/edsl.hpp>
  - <https://raw.githubusercontent.com/deepsea-inria/heartbeat/HEAD/example/fib.cpp>
  - https://www.chargueraud.org/research/2018/heartbeat/heartbeat.pdf (EGRESS_BLOCKED)
  - https://inria.hal.science/hal-01937946/document (EGRESS_BLOCKED)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/deepsea-inria/heartbeat`) · [data/wave11/enrich/raw/github_com_deepsea_inria_heartbeat.json](../../../data/wave11/enrich/raw/github_com_deepsea_inria_heartbeat.json) (enrichment confidence 0.6)

</details>
