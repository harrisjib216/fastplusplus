# K2 (smartnic/superopt, BPF superoptimizing compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (inferred from main.cc and z3server.cc in the file listing; the Languages bar was empty)` · `MIT` · 🔴 abandoned

> K2: stochastic superoptimizer for eBPF bytecode that shrinks clang -O1/-O2/-O3 BPF output with SMT-checked equivalence.

| | |
|---|---|
| **Beats** | clang BPF output: -O3 per the abstract, and the best of the clang -O1/-O2/-O3 variants per benchmark in the throughput runs (the artifact example's best clang variant for xdp_map_access is O1); clang version not stated on the pages opened |
| **Claimed result** | Artifact README (submission-version abstract): relative to clang -O3, 6-26% smaller code, 13-85 microseconds lower latency and -0.03 to 5% higher throughput (packets per second per core) on Cilium and Linux kernel programs; camera-ready abstract (arXiv 2103.00022, snippet only): 6-26% smaller code, 1.36%-55.03% lower average packet-processing latency and 0-4.75% higher throughput than the best clang-compiled program. The size figures count instruction slots K2 replaces with goto +0 padding as removed (xdp1 'cost' 61 to 59 while the output keeps 61 slots, issue #102), and the latency/throughput figures are the best of up to five K2 variants selected after measurement against the best of three clang levels. |
| **Workload** | Superoptimizing eBPF programs from Cilium, Facebook and the Linux kernel samples for program size, average packet-processing latency and throughput. |
| **Metric** | other |
| **Hardware** | Submitted-paper Table 2 ran on CloudLab d6515 (AMD) machines; the artifact replication uses CloudLab xl170 (Intel) machines with a TRex traffic generator on a second node. CPU models are not named on the pages opened. |
| **Compiler and flags** | Baseline clang BPF builds at -O1/-O2/-O3 (version not stated on the pages opened). K2 is built from superopt with z3 at a pinned commit ('make main_ebpf.out'). Reproduction scripts are in smartnic/sigcomm21_artifact (4_reproduce_results/1_insn_count/insn_count.sh, 2_eq_chk_time/eq_chk.sh, and the TRex-based run_mlffr_user.py on CloudLab). |
| **Adoption** | 30 stars |
| **Last commit** | 2021-09-16 |
| **Links** | [repository](https://github.com/smartnic/superopt) · [benchmark](https://github.com/smartnic/sigcomm21_artifact) |

## Verdict

Against the best of clang -O1/-O2/-O3 BPF builds (clang version not stated), the artifact's 11-program table shows 6.25-16.67% fewer instructions (sys_enter_open 24 to 20, xdp_devmap_xmit 36 to 30), and the paper reports 6-26% smaller code. Latency and throughput come from a TRex generator on CloudLab (AMD d6515 in the submission, Intel xl170 in the artifact rerun; CPU models not named): 13-85 us lower latency and -0.03 to 5% throughput in the submission, 1.36-55.03% lower average latency and 0-4.75% throughput in the camera-ready abstract (snippet only), and in the artifact examples xdp_map_access reaches about 15.5 against 15 Mpps.

## Use it when

- Small, hot XDP or socket BPF programs (tens of instructions; the paper says it cannot optimize 200+ instruction programs quickly) where a few instructions per packet matter.
- Programs close to the verifier's size or complexity limits, where cutting 6-17% of instructions (artifact Table 1) can get them accepted.
- Programs loaded with CAP_SYS_ADMIN, where the kernel verifier strips the goto +0 placeholders K2 leaves behind, so the instruction savings are realized.
- Offline builds that can spend seconds to about 26 minutes per program (artifact Table 1: socket-0 30 s overall, sys_enter_open 1564 s) and can load-test every candidate variant.

## Skip it when

- Throughput-bound pipelines: per-core throughput gains are -0.03 to 5% (submission) or 0 to 4.75% (camera-ready, search snippet), within the artifact's Tx-rate resolution on xdp_fwd.
- Programs using tail calls, ld_abs/ld_ind packet loads or bpf_get_prandom_u32: open issues #90, #92 and #91 say these are modelled as always-successful tail calls, plain input memory and a limited helper, so the equivalence proof does not cover the real semantics.
- Large programs (200+ instructions per the paper snippet) or anything needing a fast build: the search is stochastic, outputs differ between runs, and compile time is minutes to tens of minutes.
- Production use that needs a maintained tool: last commit 2021-09-16, no releases, install-only README ('Todo: add more instructions soon'), Ubuntu 18.04 / macOS 10.15 build against a pinned 2020-era Z3 commit, 33 open issues; support for later BPF features is not documented.

## How it is fast

It runs STOKE-style Markov chain Monte Carlo search: proposals rewrite a random operand, a random instruction, two consecutive instructions, or turn an instruction into a NOP, scored by an error cost on test inputs plus a performance cost (program length or an estimated runtime, per main.cc). Candidates are proved equivalent to the input with Z3 over a first-order-logic model of BPF, with domain-specific speedups (artifact Table 3 shows 415x to 35,107x less equivalence-checking time with all four enabled) and windowed modular verification to scale. The runtime gain comes from fewer executed instructions (for example two byte loads plus shift and or become one 16-bit load in xdp1).

## Compared with alternatives

Pick K2 over STOKE when the target is eBPF rather than x86-64: it applies the same MCMC superoptimization idea with a BPF semantics model and kernel-verifier safety checks; pick SLOTHY instead for hand-written Arm or RISC-V kernels where you want scheduling without instruction changes.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Z3 built from source at commit 1c7d27bdf31ca038f7beee28c41aa7dbba1407dd in a sibling ../z3 directory (hard-coded paths, issue #88); for object files libelf and smartnic/bpf-elf-tools; llvm for objdump; benchmarks in smartnic/superopt-input-bm; a prebuilt Docker image on Google Drive |
| **Minimum toolchain** | C++11 (g++ -std=c++11); tested on Ubuntu 18.04 and macOS 10.15.2 |
| **Platforms** | Host Linux or macOS; output is Linux eBPF bytecode (XDP, socket and tracepoint programs in the benchmarks) |
| **Thread safety** | not documented (search talks to a separate z3server process over a port; issue #97 reports zombie z3server processes) |
| **Drop-in for the baseline** | partial — the optimized .o replaces clang's BPF object in place, but deleted instructions stay as goto +0 padding (issue #102) and some variants fail the kernel verifier |

## Gotchas

- Size savings are counted without the padding: K2 patches the ELF in place and fills removed slots with goto +0 (artifact 2.3: xdp1 'perf cost' 61 to 59, yet the output still has 61 slots; issue #102), and the Linux v5.4 verifier removes ja 0 only when is_priv = capable(CAP_SYS_ADMIN) (opt_remove_nops), so unprivileged loads keep every slot.
- Not every output is loadable: artifact Table 7 shows 35 of 38 K2 variants accepted by the kernel checker (4 of 5 for xdp2, xdp_router_ipv4 and xdp_redirect), so each variant must be load-tested.
- The latency and throughput comparison picks the best of up to five stochastic K2 variants (k0 to k4) after measurement against the best of three clang levels, with three trials and MLFFR read off at the Tx-rate step resolution (xdp_fwd: all variants about 4.9 Mpps; latency at MLFFR 57 us for -O2 against 50 us for k2); the paper (snippet) also says its latency cost function is a weak predictor of real latency.
- Build quirks: the final link line compiles every source except main.cc with plain 'g++ -std=c++11' and no -O flag, so the published search times come from a largely unoptimized build; issue #87 reports a segfault when -n is omitted.

## Known shortcomings

- Throughput gain is tiny or negative (-0.03 to 5%, 13-85 us lower latency in the submission version; camera-ready 1.36-55.03% from a snippet only); stochastic search; the CloudLab rerun needs reviewer credentials; clang version and CPU model unstated. SIGCOMM 2021 paper PDF blocked here (arXiv, par.nsf.gov), paper-access retier could reach A.
- Harness flaws: the size gain counts goto +0 padding as removed (issue #102: xdp1 'cost' 61 to 59 but still 61 slots; Linux v5.4 opt_remove_nops strips ja 0 only under CAP_SYS_ADMIN); the latency and throughput comparison picks the best of up to 5 K2 variants after measurement against the best of 3 clang levels, with 3 trials near the Tx-step resolution (xdp_fwd all about 4.9 Mpps); the equivalence model assumes tail calls always succeed (#90) and treats ld_abs/ld_ind as plain memory (#92); the search binary is mostly built without -O.

## Caveats and trade-offs

The paper PDF was not opened (arXiv, ar5iv, par.nsf.gov and k2.cs.rutgers.edu are unreachable here); the camera-ready numbers are from a search snippet, while the artifact README carries the submission-version abstract with different latency and throughput figures. Throughput gains are tiny (-0.03 to 5%, i.e. sometimes slightly slower), and the artifact says rerun numbers will not match Table 2 because it moved from AMD d6515 to Intel xl170 machines; the latency/throughput rerun requires CloudLab credentials and disk images given only to SIGCOMM reviewers. The search is stochastic, so outputs vary between runs, and optimisation takes minutes to over 20 minutes per program (e.g. sys_enter_open 1564 s); the paper says programs over about 200 instructions cannot be optimised quickly. Not every K2 variant passes the kernel verifier (e.g. 4 of 5 for xdp2, xdp_router_ipv4 and xdp_redirect). The superopt README is install-only ('Todo: add more instructions soon'). The baseline is clang BPF output, not GNU as, NASM or MASM, so the fit to assemblers-and-asm-tooling is weak. [retier] The paper PDF was not opened; the camera-ready numbers are from a search snippet while the artifact README carries the submission-version abstract with different latency and throughput figures. Size savings are counted without the padding: K2 patches the ELF in place and fills removed slots with goto +0, and the Linux v5.4 verifier removes ja 0 only when is_priv = capable(CAP_SYS_ADMIN) (opt_remove_nops), so unprivileged loads keep every slot. Throughput gains are tiny (-0.03 to 5%, sometimes slightly slower); the latency and throughput comparison picks the best of up to five stochastic K2 variants (k0 to k4) after measurement against the best of three clang levels, with three trials and MLFFR read off at the Tx-rate step resolution (xdp_fwd: all variants about 4.9 Mpps), and the paper says its latency cost function is a weak predictor of real latency. Not every output is loadable (artifact Table 7: 35 of 38 K2 variants accepted by the kernel checker). The equivalence model assumes tail calls always succeed (#90) and treats ld_abs/ld_ind as plain memory (#92). The artifact says rerun numbers will not match Table 2 (machines moved from AMD d6515 to Intel xl170) and the latency/throughput rerun requires CloudLab credentials given only to SIGCOMM reviewers; the search is stochastic. The final link line compiles every source except main.cc with plain 'g++ -std=c++11' and no -O flag, so the published search times come from a largely unoptimized build; issue #87 reports a segfault when -n is omitted.

BPF bytecode only; needs the z3 SMT solver (README install steps build main_ebpf.out against z3); the search runs offline at compile time, cost not seen.

## Maintenance

Abandoned since 2021-09-16 (MIT, 30 stars, research prototype with no releases); usable as an offline post-pass on small XDP programs if you load-test each variant, but the published size gain counts goto +0 padding as removed (only privileged loads strip it), the speed gains are a best-of-five post-hoc pick near measurement resolution, and the equivalence model has open gaps for tail calls and ld_abs/ld_ind.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded from C. K2 is an ACM SIGCOMM 2021 paper (DOI 10.1145/3452296.3472929 in a search result), and its official artifact repo smartnic/sigcomm21_artifact restates the accepted paper's numbers against clang -O3 and ships reproduction scripts (4_reproduce_results: insn_count.sh, eq_chk.sh, the TRex run_mlffr_user.py flow). The paper PDF itself could not be opened (arXiv and par.nsf.gov are blocked), the clang version and CPU models are not stated on the pages opened, and the latency rerun needs reviewer-only CloudLab credentials, so it is not A.
- **Retiered** B to C: Enricher: the code-size savings count goto +0 padding slots that remain in the program (issue #102; the v5.4 verifier strips them only for CAP_SYS_ADMIN loads), the latency and throughput comparison picks the best of up to five stochastic K2 variants after measurement against the best of three clang levels with three trials at Tx-step resolution, the equivalence model has known gaps (#90, #92), and the artifact says reruns will not match Table 2. Peer-reviewed paper whose headline metrics rest on a padded size count and post-hoc best-of selection: B to C.
- **Verifier notes:** The record's numbers match the camera-ready abstract (snippet only); the artifact README gives the submission-version figures (13-85 us lower latency, -0.03 to 5% throughput), and both are now in claimed_speedup. MIT licence (Srinivas Narayana, 2019), 30 stars and last commit 2021-09-16 (abandoned) are confirmed. A paper-access retier could check Table 2's clang version and CPU model, which might reach A, since the artifact code is public.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-51 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/smartnic/superopt>
  - <https://github.com/smartnic/superopt/commits/master>
  - <https://github.com/smartnic/superopt/tree/master/measure>
  - <https://github.com/smartnic/superopt/tree/master/doc>
  - <https://raw.githubusercontent.com/smartnic/superopt/HEAD/LICENSE>
  - <https://github.com/smartnic>
  - <https://github.com/smartnic/sigcomm21_artifact>
  - <https://raw.githubusercontent.com/smartnic/sigcomm21_artifact/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/smartnic/superopt>
  - <https://raw.githubusercontent.com/smartnic/superopt/HEAD/README.md>
  - <https://raw.githubusercontent.com/smartnic/superopt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/smartnic/superopt/HEAD/Makefile>
  - <https://raw.githubusercontent.com/smartnic/superopt/HEAD/main.cc>
  - <https://github.com/smartnic/superopt/issues?q=is%3Aissue>
  - <https://github.com/smartnic/superopt/issues/90>
  - <https://github.com/smartnic/superopt/issues/92>
  - <https://github.com/smartnic/superopt/issues/102>
  - <https://github.com/smartnic/superopt/issues/112>
  - <https://raw.githubusercontent.com/smartnic/sigcomm21_artifact/HEAD/README.md>
  - <https://raw.githubusercontent.com/smartnic/sigcomm21_artifact/HEAD/install.sh>
  - <https://github.com/smartnic/throughput-experiments>
  - <https://raw.githubusercontent.com/torvalds/linux/v5.4/kernel/bpf/verifier.c>
  - <https://raw.githubusercontent.com/torvalds/linux/master/kernel/bpf/verifier.c>
  - WebSearch snippet: arXiv 2103.00022 (camera-ready abstract and conclusion; paper not opened)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/smartnic/superopt`) · [data/wave13/enrich/raw/github_com_smartnic_superopt.json](../../../data/wave13/enrich/raw/github_com_smartnic_superopt.json) (enrichment confidence 0.6)

</details>
