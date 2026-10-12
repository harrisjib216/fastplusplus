# STOKE

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Research stochastic superoptimizer for x86-64 that rewrites short loop-free assembly kernels to match or beat gcc -O3 and icc -O3 output.

| | |
|---|---|
| **Beats** | gcc -O3 and icc -O3 compiled x86-64 code (output quality); expert hand-written assembly for some kernels; Google Native Client's shipped libc string functions in the 2017 paper |
| **Claimed result** | ASPLOS 2013 paper, Figure 1 and Section 1: the OpenSSL big-number Montgomery multiplication kernel rewritten by STOKE is '16 lines shorter, 1.6x faster' than the gcc -O3 code 'and slightly faster than expert handwritten assembly'; abstract: STOKE's programs 'either match or outperform the code produced by gcc -O3, icc -O3, and in some cases, expert handwritten assembly'; Figure 11 plots speedups over llvm -O0 for Hacker's Delight p01-p25, saxpy, mont and list (chart only). The README popcount tutorial's 1.046 s vs 0.133 s (7.9x) is struck: it compares g++ -O3 built without -mpopcnt or -march against a rewrite found with --cpu_flags { popcnt }, was timed on an older main.cc, and the checked-in examples/tutorial/main.cc now calls rand() every iteration, so it cannot be reproduced. |
| **Workload** | Runtime of superoptimized loop-free x86-64 kernels (OpenSSL big-number Montgomery multiplication, Hacker's Delight, SAXPY, linked-list traversal) starting from llvm -O0 code, and 13 libc string functions from NaCl newlib. |
| **Metric** | other |
| **Hardware** | ASPLOS 2013: synthesis and optimization on a cluster of 40 dual-core 1.8 GHz AMD Opterons (machine used for the runtime speedups not identified in the extracted text); ASPLOS 2017: machines with two Intel Xeon E5-2667v2 3.3 GHz processors and 256 GB RAM |
| **Compiler and flags** | gcc -O3 and icc -O3 baselines (versions not stated in the extracted paper text); gcc-4.9 used in the 2017 paper's translation mode; README tutorial uses g++ -std=c++11 -O3 -fno-inline |
| **Adoption** | 884 stars |
| **Last commit** | 2020-12-04 |
| **Links** | [repository](https://github.com/StanfordPL/stoke) · [benchmark](https://raw.githubusercontent.com/StanfordPL/stoke/develop/docs/papers/asplos13.pdf) |

## Verdict

The ASPLOS 2013 paper starts from llvm -O0 binaries and reports STOKE rewrites that match gcc -O3 and icc -O3 on Hacker's Delight p01-p25 and beat them on several kernels; the OpenSSL Montgomery multiplication kernel came out 16 lines shorter and 1.6x faster than gcc -O3 and slightly faster than OpenSSL's handwritten assembly. Compiler versions and the timing CPU are not stated (search ran on 40 dual-core 1.8 GHz AMD Opterons), and per-kernel values exist only in Figure 11's chart; the 2017 paper separately reports a median and mean 25% (up to 97%) over Google's NaCl libc string functions on Xeon E5-2667v2 machines, gains that come largely from NaCl's sandboxing no-ops and 32-byte jump alignment.

## Use it when

- A hot, short, loop-free x86-64 sequence (tens of instructions: bit tricks, multi-word arithmetic, fixed-size SIMD bodies) where a few cycles per call matter and you can spend tens of minutes to hours of search per kernel
- Finding a better instruction sequence to hand-port into your own inline assembly or intrinsics, as a research aid next to reading compiler output
- Code built under unusual constraints that compilers handle poorly, such as Native Client sandboxing rules (ASPLOS 2017: median 25%, up to 97% on 13 NaCl libc string functions)
- Reproducing or extending the superoptimization papers (ASPLOS 2013, PLDI 2014 floating point, PLDI 2016 stratified synthesis), since the repo is their artifact

## Skip it when

- General loops or whole programs: the README says 'We're not quite at the point where we can take a generic loop and expect to improve gcc/llvm -O3 code'; on the paper's linked-list benchmark STOKE ended up slower than gcc -O3
- Production builds: the README says 'STOKE isn't production ready' and 'nobody is actively working on this code base'; the last source change was 2019-10-03
- Modern toolchains and ISAs: it builds only with gcc 4.9 on Ubuntu 14.04/16.04 (or the Docker image) and supports a pre-2016 instruction subset, so code from newer compilers may not load
- Non-x86 targets (Arm, RISC-V, GPU) or kernels with complex memory aliasing where test-case generation is weak
- Any case where you cannot afford a sound equivalence proof: rewrites that pass test cases or bounded validation can still be wrong

## How it is fast

The speed comes from the code it finds, not from the tool. Metropolis-Hastings sampling over opcode, operand, swap and rotate moves minimises a cost of test-case Hamming error plus a static sum of instruction latencies. This lets it find algorithmically different sequences that compiler rewrite rules miss: one 128-bit mulq instead of four imulq in OpenSSL's Montgomery kernel, cmov chains for Hacker's Delight p21, a 4-way SSE broadcast for a hand-unrolled SAXPY. In the ASPLOS 2013 pipeline, candidates within 20% of the best cost are re-ranked by measured runtime and checked by an STP-based validator. The 2017 loop work (DDEC with alias relationship mining) proves loop rewrites equivalent.

## Compared with alternatives

Pick STOKE over Minotaur, SuperCoder or Unison when the target is a short x86-64 kernel and you want whole-sequence algorithmic rewrites with an SMT equivalence check rather than LLVM-IR peepholes, model-generated assembly or better register allocation; pick SLOTHY for Arm Cortex-A/M cryptography and DSP kernels, and K2 for eBPF programs.

## Integration

| | |
|---|---|
| **Form** | built command-line tools (stoke, stoke_tcgen and subcommands); output is an assembly file or a patched ELF binary |
| **Dependencies** | gcc/g++ 4.9, Boost (filesystem, thread, regex), jsoncpp, GMP, CLN, ANTLR, bison/flex, ghc and Haskell libraries, Z3 and CVC4, the x64asm submodule and Intel Pin for dynamic test cases; Docker image stanfordpl/stoke recommended |
| **Minimum toolchain** | exactly gcc 4.9 per README ('Below that ... not enough features ... Above that, there are some issues with an ABI change in gcc-5'); Ubuntu 14.04 or 16.04 |
| **Platforms** | Linux x86-64 hosts only; best on Haswell or newer, Sandy Bridge works without AVX2; rewrites target x86-64 only |
| **Thread safety** | not documented (the search itself is single process; the paper parallelised across a cluster with separate runs) |
| **Drop-in for the baseline** | partial — stoke replace patches one rewritten function into an existing x86-64 ELF binary, but only if the new code is no larger than the old function (README FAQ: use -falign-functions to pad); it does not replace a compiler or assembler |

## Gotchas

- Harness flaw in the README demo: the 1.046 s vs 0.133 s popcount timing compares g++ -O3 built without -mpopcnt or -march (so gcc cannot emit popcnt) against a STOKE rewrite that uses popcntq; the checked-in examples/tutorial/synthesize.conf even passes '--cpu_flags "{ popcnt }"' to the search. The timing was also taken with an older main.cc (popcnt(i)); the checked-in examples/tutorial/main.cc now calls rand() on every iteration, so the 7.9x cannot be reproduced from the current tutorial.
- Correctness depends on the verification strategy you choose: the tutorial uses '--strategy hold_out' (8 training and 1016 hold-out test cases), and bounded validation is unsound (issue #1008: a rewrite of a counting loop passed bounded verification at --bound 1024 yet was wrong for inputs above 16 bits; a maintainer replied 'Bounded verification is inherently unsound'). The ASPLOS 2017 run saw 180 candidate rewrites that failed sound verification because they were not equivalent.
- The ASPLOS 2013 validator treats 64-bit multiplication and division as uninterpreted functions and assumes stack addresses are constant offsets from rsp, so 'verified' rewrites are proven only under those assumptions.
- The search cost is a static sum of instruction latencies (cost 'correctness + latency'); the paper re-ranks the best candidates by measured runtime, but a plain stoke synthesize or optimize run does not, and Figure 3 of the paper shows outliers where predicted and actual runtime disagree. Open issues also report wrong instruction semantics (#1004 vfnmadd132pd) and unsupported instructions in the validators (#943 tzcntq).

## Known shortcomings

- ASPLOS 2013 paper (PDF in repo docs/papers): Montgomery multiplication kernel 1.6x faster than gcc -O3, but on hand-picked loop-free kernels with per-kernel speedups chart-only, no gcc/icc versions and no timing CPU named; the README popcount demo compares against -O3 without -march. Research prototype superoptimizer (not an assembler), abandoned since 2019.
- Harness flaw in the README demo: the popcount 7.9x compares g++ -O3 built without -mpopcnt (so gcc cannot emit popcnt) against a rewrite found with the checked-in tutorial synthesize.conf passing --cpu_flags { popcnt }; the timing was taken on an older main.cc, and the current examples/tutorial/main.cc calls rand() every iteration, so the 7.9x is not reproducible. Bounded validation is unsound (issue #1008: a rewrite passed --bound 1024 yet was wrong above 16 bits; the tutorial default is hold_out test cases only); the ASPLOS 2013 validator treats 64-bit mul/div as uninterpreted functions; the ASPLOS 2017 25% median gain came mostly from removing NaCl sandbox no-ops and 32-byte jump alignment; the linked-list kernel is slower than gcc -O3.

## Caveats and trade-offs

The paper is from 2013 and the speedups are on a small set of hand-picked loop-free kernels, plotted relative to llvm -O0 starting points in Figure 11; per-kernel numbers are chart-only, and the paper states no gcc/icc versions and does not name the timing machine. The README says 'We're not quite at the point where we can take a generic loop and expect to improve gcc/llvm -O3 code', calls STOKE a research prototype that 'isn't production ready', and says 'nobody is actively working on this code base'; it needs gcc 4.9 to build. The README popcount tutorial's \~8x win compares against g++ -O3 without -march, so gcc cannot emit the popcnt instruction that STOKE uses; it shows the tool working, not a fair compiler comparison. The category fit (assembly tooling) is a judgement call: STOKE is a superoptimizer, and its baselines are compilers, not GNU as, NASM or MASM. The last commit (2020-12-04) only added a CodeQL workflow; the last code change is from 2019-10-03. [retier] The paper is from 2013 and the speedups are on a small set of hand-picked loop-free kernels plotted relative to llvm -O0 starting points; per-kernel numbers are chart-only, gcc/icc versions and the timing machine are not stated. The README says STOKE cannot yet take a generic loop and beat gcc/llvm -O3, calls it a research prototype that is not production ready, says nobody is actively working on the code base, and needs gcc 4.9 to build. Harness flaw in the README demo: the popcount 7.9x has a crippled baseline (no -mpopcnt) and is not reproducible with the current driver. Correctness depends on the verification strategy: the tutorial uses --strategy hold_out (8 training and 1016 hold-out test cases), bounded validation is unsound (issue #1008: a counting-loop rewrite passed --bound 1024 yet was wrong for inputs above 16 bits; a maintainer replied 'Bounded verification is inherently unsound'), the ASPLOS 2013 validator treats 64-bit multiplication and division as uninterpreted functions and assumes stack addresses are constant offsets from rsp, and the ASPLOS 2017 run saw 180 candidate rewrites fail sound verification. The ASPLOS 2017 translation-mode 25% median gain came mostly from removing NaCl sandbox no-ops and 32-byte jump alignment; the linked-list kernel is slower than gcc -O3. The search cost is a static sum of instruction latencies; a plain stoke run does not re-rank by measured runtime. Open issues report wrong instruction semantics (#1004 vfnmadd132pd) and unsupported instructions in the validators (#943 tzcntq).

x86-64 only and Intel-microarchitecture oriented. Needs test cases plus bounded or SMT-based equivalence checking, search budgets of tens of minutes per kernel on a cluster, and works best on short loop-free sequences. README: 'STOKE isn't production ready' and 'nobody is actively working on this code base'; it says it is 'not quite at the point where we can take a generic loop and expect to improve gcc/llvm -O3 code'.

## Maintenance

Abandoned research artifact (last code change 2019-10-03, a CodeQL workflow added 2020-12-04, 62 open issues) under Apache-2.0; usable from its Docker image to find sequences you then hand-port, but too toolchain-bound (gcc 4.9) and unsound under its default test-case verification to put in a build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ASPLOS 2013 paper (docs/papers/asplos13.pdf, read in full) compares STOKE rewrites against gcc -O3 and icc -O3 output and OpenSSL's handwritten Montgomery kernel; Figure 1 caption and Section 1 state the Montgomery kernel is 16 lines shorter and 1.6x faster than gcc -O3 and slightly faster than the expert handwritten assembly. Not A: the paper gives no gcc/icc versions and does not name the machine that timed the kernels (only the 40-node 1.8 GHz AMD Opteron search cluster), and Figure 11's per-kernel speedups are chart-only.
- **Verifier notes:** Paper numbers match the record; tier B stands on the peer-reviewed ASPLOS paper. Shortcomings: hand-picked loop-free kernels, chart-only per-kernel speedups, no compiler versions or timing CPU, research prototype abandoned since 2019 (README says so), superoptimizer rather than an assembler, README popcount demo compares against -O3 without -march.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-02 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/docs/papers/asplos13.pdf>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/README.md>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/LICENSE>
  - <https://github.com/StanfordPL/stoke>
  - <https://github.com/StanfordPL/stoke/commits/develop>
- **Sources the enricher read:**
  - <https://github.com/StanfordPL/stoke>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/README.md>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/LICENSE>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/Makefile>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/configure.sh>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/.travis.yml>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/docs/papers/asplos13.pdf>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/docs/papers/asplos17.pdf>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/examples/tutorial/main.cc>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/examples/tutorial/Makefile>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/examples/tutorial/synthesize.conf>
  - <https://raw.githubusercontent.com/StanfordPL/stoke/develop/examples/tutorial/testcase.conf>
  - <https://github.com/StanfordPL/stoke/commits/develop>
  - <https://github.com/StanfordPL/stoke/issues>
  - <https://github.com/StanfordPL/stoke/issues?q=is%3Aissue+bug+incorrect>
  - <https://github.com/StanfordPL/stoke/issues/1008>
  - <https://github.com/StanfordPL/stoke/issues/919>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/stanfordpl/stoke`) · [data/wave13/enrich/raw/github_com_stanfordpl_stoke.json](../../../data/wave13/enrich/raw/github_com_stanfordpl_stoke.json) (enrichment confidence 0.78)

</details>
