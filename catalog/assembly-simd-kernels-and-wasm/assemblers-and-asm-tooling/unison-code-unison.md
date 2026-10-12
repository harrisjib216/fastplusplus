# Unison

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Haskell` · `BSD-3-Clause` · 🔴 abandoned

> Constraint-programming register allocator and instruction scheduler for LLVM 3.8 that produces 1-10% faster or 1-4% smaller code than LLVM's heuristics.

| | |
|---|---|
| **Beats** | LLVM's register allocator and instruction scheduler (output quality, Hexagon, ARM and MIPS back ends) |
| **Claimed result** | TOPLAS 2019 paper (arXiv 1804.02452) as summarised in the author's KTH thesis Table 3.1: mean estimated speedup over LLVM 3.8 of 1.1% to 10% (thesis preprint figures: Hexagon 9.3%, MIPS 5.1%, ARM 1%) and mean code-size reduction of 1.3% to 3.8% (thesis: MIPS 3.9%, ARM 2.4%, Hexagon 0.8%) on functions from MediaBench and SPEC CPU2006; the speedups are static cost-model estimates, and the only executed confirmation is Hexagon at 7.1% mean across MediaBench functions and 5.4% across whole applications. |
| **Workload** | Estimated speedup and code size of functions from MediaBench and SPEC CPU2006 compiled with Unison's integrated combinatorial register allocation and instruction scheduling versus LLVM. |
| **Metric** | other |
| **Hardware** | Hexagon (execution check); estimates for ARM and MIPS |
| **Adoption** | 116 stars |
| **Last commit** | 2023-01-15 |
| **Links** | [repository](https://github.com/unison-code/unison) · [benchmark](https://arxiv.org/abs/1804.02452) |

## Verdict

First-party, peer-reviewed (ACM TOPLAS 2019 and the author's 2018 KTH doctoral thesis) comparison of code quality from Unison versus LLVM 3.8's register allocator and scheduler on systematically selected MediaBench and SPEC CPU2006 functions for Hexagon V4, ARM and MIPS. Mean estimated speedup is about 1% (ARM) to 9-10% (Hexagon), mean code size reduction about 1-4%, and executing MediaBench on Hexagon gave a measured 5.4% mean application speedup. No compile flags or Hexagon execution setup appear in the sources opened here.

## Use it when

- Release builds of hot functions for in-order embedded or DSP cores (Hexagon V4, ARM1156T2F-S Thumb, MIPS32) where minutes of compile time per function are acceptable.
- Code-size-critical firmware on MIPS or ARM, where the authors report mean size reductions of about 2.4-3.9% over LLVM.
- VLIW targets like Hexagon, where the thesis reports 9.3% mean estimated speedup and 5.4% measured speedup over whole MediaBench applications.
- Research: measuring how far LLVM's heuristic register allocator and scheduler are from optimal, or prototyping a back end for an irregular processor feature (register pairing, operand forwarding, double loads).

## Skip it when

- x86-64 or other out-of-order cores: no upstream target, and the author said in issue #56 that the in-order cost model is not accurate enough for speed on x86-64 (an experimental X86.hs exists only in the matsc-at-sics-se fork).
- Large functions: optimal solutions were reached for functions up to 647 instructions and improvements up to 874; issue #60 (a \~1,000-instruction MIPS function) ran out of memory, and the maintainer advised splitting functions or limiting inlining.
- Any modern toolchain: the driver exists only for LLVM 3.8 (branch release_38-unison, last updated 2018-05-22), so you cannot use it with current clang releases.
- Builds where compile time matters: solving takes tens to hundreds of seconds per medium-sized function, versus milliseconds for LLVM's greedy allocator.
- ARM speed: the mean estimated gain over LLVM is only about 1%.

## How it is fast

It speeds up the generated code, not compilation. Constraint programming over a dedicated program representation (Linear SSA with optional copies and alternative temporaries) lets a solver search register allocation and scheduling jointly, so trade-offs a phase-ordered heuristic compiler cannot see (for example spilling versus a longer schedule) are captured. The objective is a static cost model: estimated cycles weighted by basic-block frequency for speed, or total instruction size for size. The solving pipeline combines a presolver, a decomposition-based Gecode solver and a hybrid CP-SAT solver, and starts from LLVM's solution, so the result never costs more than LLVM's under the model.

## Compared with alternatives

Pick Unison over STOKE or Minotaur when the target is an in-order embedded core (Hexagon, ARM Thumb, MIPS32) and you want whole-function register allocation and scheduling of compiler output rather than superoptimizing short x86-64 loop-free kernels or LLVM IR peepholes. Pick SLOTHY instead for hand-written Arm assembly kernels on current cores: it does constraint-based scheduling and register allocation too, but is maintained and targets Cortex-A/M.

## Integration

| | |
|---|---|
| **Form** | standalone tool chain (Haskell binaries plus Gecode C++ solver) driven by a patched llc |
| **Dependencies** | Haskell Stack, Gecode 6.0.0, Qt 5 and Graphviz (both optional), and the unison-code/llvm fork (LLVM 3.8, branch release_38-unison) as the compiler driver; MiniZinc back ends are optional |
| **Minimum toolchain** | Stack with the resolver pinned in the repo (updated 2023-01-15); the LLVM 3.8 fork must be built from source (issue #61 reports trouble building it alongside clang 3.8) |
| **Platforms** | Host: Linux (Debian-based instructions). Targets: Hexagon V4, ARM1156T2F-S (Thumb), MIPS32, plus a toy Minimal target |
| **Thread safety** | Not applicable (offline compiler pass run per function); the solver portfolio can run in parallel processes |
| **Drop-in for the baseline** | partial: switch it on with llc -unison on the 3.8 fork and it replaces LLVM's register allocator and post-RA scheduler per function, but only for three targets and only on LLVM 3.8 |

## Gotchas

- The headline speedups are estimated by Unison's own static cost model (cycles times block frequency). Only Hexagon was executed: 7.1% mean across MediaBench functions and 5.4% across whole applications. The thesis says the estimate overestimates actual speedup for 59% of the mispredicted functions, because of caches and branch prediction.
- Published means differ by version: the 2018 thesis summary of the paper gives 1% to 9.3% estimated speedup and 0.8% to 3.9% size reduction (Hexagon 9.3/0.8, MIPS 5.1/3.9, ARM 1/2.4), while the TOPLAS 2019 abstract (search snippets) gives 1.1% to 10% and 1.3% to 3.8%. The baseline throughout is LLVM 3.8.
- Open MIPS correctness reports: wrong stack offsets (#50, an SW at offset -1, no maintainer reply), uni normalize dropping NOP delay slots (#49), and a core dump on mesa.api.glVertex2i with -unison (#43). Validate the emitted code; do not trust it blindly.
- If Unison cannot improve on LLVM's .asm.mir starting solution (manual chapter 4), it outputs that solution unchanged, so a silent 'no improvement' is a normal outcome, for example when a function is too large for the solver budget.

## Known shortcomings

- Downgraded B to C: the TOPLAS 2019 paper (arXiv 1804.02452) was unreachable (arxiv, deepai, ericsson.com blocked), so the 1.1-10% speedup is snippet-only and estimated from a cost model (measured only on Hexagon); slow constraint-solver compile; abandoned since 2023-01-15. Paper access would restore B.
- Gains are cost-model estimates (Hexagon 9.3%, MIPS 5.1%, ARM 1%) against LLVM 3.8; the only real run is Hexagon at 5.4% across whole applications. The driver is stuck on LLVM 3.8 (release_38-unison); functions of about 1,000 instructions run out of memory (#60); open MIPS bugs: wrong stack offsets (#50), delay slots (#49). The KTH thesis is reachable at raw.githubusercontent.com/robcasloz/robcasloz.github.io/master/publications/TRITA-EECS-AVL-2018-48.pdf; its Table 3.1 summarises the TOPLAS numbers (thesis preprint 1-9.3% speed, 0.8-3.9% size; TOPLAS 1.1-10%, 1.3-3.8%).

## Caveats and trade-offs

Numbers are 'estimated' speedups from a static cost model, not measured runtimes, except for the Hexagon execution check. The metric is the quality of the generated code: Unison's constraint solving is far slower than LLVM's heuristic register allocator and scheduler, and the paper describes scaling to medium-sized functions of up to about 1,000 instructions, so compile time is a cost, not a win. The repo README and project site (unison-code.github.io index.md, checked via raw.githubusercontent.com) make no performance claims and link no results; the paper (arXiv 1804.02452, TOPLAS doi 10.1145/3332373), the project site's publication pages and the Ericsson research blog 'Outperforming state-of-the-art compilers with Unison' were unreachable here, so all numbers are from search-result text. Needs an LLVM fork (unison-code/llvm) as a driver. Last commit 2023-01-15 (abandoned). Filed under assemblers-and-asm-tooling, though it is really a compiler back-end component (register allocation and instruction scheduling). [retier] Numbers are estimated speedups from Unison's own static cost model (cycles times block frequency), not measured runtimes, except for the Hexagon execution check (5.4% across whole applications); the thesis says the estimate overestimates the actual speedup for 59% of the mispredicted functions because of caches and branch prediction. The baseline throughout is LLVM 3.8, and the driver is stuck on LLVM 3.8 (release_38-unison), so the comparison is against a 2016 compiler. Unison's constraint solving is far slower than LLVM's heuristic register allocator and scheduler; it scales to medium-sized functions of up to about 1,000 instructions and runs out of memory beyond that (#60), and if it cannot improve on LLVM's starting solution it outputs it unchanged. Open MIPS correctness reports: wrong stack offsets (#50), uni normalize dropping NOP delay slots (#49), a core dump on mesa.api.glVertex2i with -unison (#43). The repo README and project site make no performance claims.

Haskell tool driving constraint solvers, used through a Unison-enabled LLVM fork (github.com/unison-code/llvm); solving time is far higher than LLVM's heuristics; targets Hexagon, ARM and MIPS rather than x86.

## Maintenance

Abandoned: last commit 2023-01-15 (build-dependency bumps only, last functional fix 2021-09-11), the LLVM driver is frozen at 3.8, and 13 issues are open, some of them MIPS correctness bugs. It is BSD-3-Clause and usable as a research tool or for one-off release builds on its three targets, not as a production back end. Paper-access note: the author's KTH thesis (robcasloz.github.io repo, publications/TRITA-EECS-AVL-2018-48.pdf, reachable via raw.githubusercontent.com) carries the evaluation summary of the TOPLAS paper (Table 3.1 and the Hexagon execution results), so the snippet-only C could move to B.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now B.
- **Tier reason:** The numbers come from a peer-reviewed paper (Castaneda Lozano, Carlsson, Hjort Blindell, Schulte, ACM TOPLAS 41(3) 2019, arXiv 1804.02452), but arXiv, doi.org and every mirror tried (deepai.org, the Ericsson research blog) were unreachable here, and the repo and project-site sources carry no results, so the figures are known only from search snippets. Held at C (snippet-only rule) pending a paper-access retier; it would be B once the paper is opened.
- **Retiered** C to B: Enricher reached the author's KTH thesis (robcasloz.github.io mirror via raw.githubusercontent.com, TRITA-EECS-AVL-2018-48), whose Table 3.1 summarises the peer-reviewed TOPLAS 2019 evaluation: estimated speedups over LLVM 3.8 of 1-9.3% (thesis) / 1.1-10% (TOPLAS) and code-size reductions of 0.8-3.9% / 1.3-3.8% by architecture, with the only real execution on Hexagon at 5.4% across whole applications. Peer-reviewed measurement now read from a primary source: C to B, with the estimate-versus-measurement caveat recorded.
- **Verifier notes:** Real, peer-reviewed project; downgraded B to C only because the paper could not be opened here (arXiv, doi.org, deepai.org, ericsson.com all ENOTFOUND). Add to the paper-access retier list: arXiv 1804.02452 / TOPLAS 2019 would support B. Shortcomings: estimated (cost-model) speedups except on Hexagon, gains of 1.1-10% are small, much slower compile times than LLVM, abandoned since 2023-01-15.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-08 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/unison-code/unison>
  - <https://github.com/unison-code/unison/commits>
  - <https://raw.githubusercontent.com/unison-code/unison/HEAD/LICENSE.md>
  - <https://github.com/unison-code>
  - <https://github.com/unison-code/unison-code.github.io>
  - <https://github.com/unison-code/unison-code.github.io/tree/master>
  - <https://github.com/unison-code/unison-code.github.io/tree/master/doc>
  - <https://raw.githubusercontent.com/unison-code/unison-code.github.io/master/index.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/unison-code/unison/HEAD/README.md>
  - <https://raw.githubusercontent.com/unison-code/unison/HEAD/LICENSE.md>
  - <https://github.com/unison-code/unison>
  - <https://github.com/unison-code/unison/tree/master/src/unison/src/Unison/Target>
  - <https://github.com/unison-code/unison/commits>
  - <https://github.com/unison-code/unison/issues?q=is%3Aissue>
  - <https://github.com/unison-code/unison/issues/50>
  - <https://github.com/unison-code/unison/issues/56>
  - <https://github.com/unison-code/unison/issues/60>
  - <https://github.com/unison-code/unison-code.github.io/tree/master/doc>
  - <https://raw.githubusercontent.com/unison-code/unison-code.github.io/master/doc/manual.pdf>
  - <https://github.com/unison-code/llvm>
  - <https://github.com/unison-code/llvm/branches/all>
  - <https://github.com/unison-code/llvm/branches/all?page=2>
  - <https://raw.githubusercontent.com/unison-code/llvm/release_38-unison/README.md>
  - <https://github.com/robcasloz/robcasloz.github.io>
  - <https://github.com/robcasloz/robcasloz.github.io/tree/master/publications>
  - <https://raw.githubusercontent.com/robcasloz/robcasloz.github.io/master/publications/TRITA-EECS-AVL-2018-48.pdf>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/unison-code/unison`) · [data/wave13/enrich/raw/github_com_unison_code_unison.json](../../../data/wave13/enrich/raw/github_com_unison_code_unison.json) (enrichment confidence 0.78)

</details>
