# SLOTHY

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Python` · `MIT` · 🟢 active

> Constraint-solver superoptimizer that reschedules, register-allocates and software-pipelines hand-written Arm and RISC-V assembly for one core.

| | |
|---|---|
| **Beats** | unscheduled 'clean' hand-written assembly and prior hand-optimized implementations of the same kernels (ML-KEM and ML-DSA NTTs, FFT, X25519); no compiler baseline stated on the pages opened |
| **Claimed result** | README: SLOTHY has been used 'to provide the fastest known implementations of various cryptographic and DSP primitives' (ML-KEM and ML-DSA NTTs for Cortex-A55/A72/M55/M85, FFT for Cortex-M55/M85, X25519 for Cortex-A55); no speedup numbers on any page opened. Related adoption number: the AWS-LC pull request that imported the s2n-bignum X25519 rewrite (partly SLOTHY-generated) reports 12867.1 to 22361.9 ops/sec ('74% speedup') on Graviton 2, but that gain is not attributable to SLOTHY alone. |
| **Workload** | Instruction scheduling, register allocation and software pipelining of hand-written Arm AArch64, Armv8.1-M and RISC-V assembly for cryptographic and DSP kernels. |
| **Metric** | other |
| **Hardware** | Targets Cortex-M55, M85, A55 (supported), A72, Cortex-X/Neoverse-V, Apple M1 (experimental) and XuanTie C908 |
| **Adoption** | 352 stars; adopted in AWS-LC / s2n-bignum, Arm EndpointAI CMSIS DSP and mlkem-native |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/slothy-optimizer/slothy) |

## Verdict

The README and TCHES 2024 abstract say SLOTHY-optimized NTT, FFT and X25519 code matches or beats prior hand-optimized code on Cortex-A55, A72, M55 and M85, with no numbers reachable here; a TCHES slide seen only as a search snippet lists 'Ours clean 1914' against 'Ours SLOTHY 891' for an unlabelled workload. The adoption figure is real but not SLOTHY's alone: AWS-LC PR #1478 (merged 2024-03-06; the README links the closed PR #1469) reports 12,867.1 to 22,361.9 X25519 ops/sec (74%, bssl speed, Graviton 2 c6g.16xlarge), but that replaces s2n-bignum's previous code with Lenngren's unsaturated base-25.5 integer/SIMD algorithm, was measured on Graviton 2 rather than the Cortex-A55 the paper's X25519 targets, and the PR notes the _alt forms remain faster on their target microarchitectures.

## Use it when

- You maintain hand-written Neon, Helium or RISC-V assembly for crypto or DSP kernels (NTTs, FFTs, field arithmetic) and want scheduled code without hand-interleaving it.
- In-order targets with accurate models: Cortex-A55, Cortex-M55 and Cortex-M85; the paper artifact says result variation is smaller on these than on the heuristic Cortex-A72 model.
- Straight-line blocks or loop bodies under about 150 instructions (seconds to minutes under 50, minutes to hours up to 150, per the README); larger kernels with the splitting heuristic.
- Code that must stay auditable or formally verified: the clean source carries the logic and the optimized output keeps the same data-flow graph, which s2n-bignum then checks in HOL Light.
- Retargeting existing assembly to a new core (the pqm7 Cortex-M7 migration study) by re-running the solver with another model.

## Skip it when

- You want a faster C or C++ build: SLOTHY never sees compiler output unless you feed it assembly, and it does not choose instructions.
- Out-of-order cores where the model is experimental (Cortex-A72, Cortex-X/Neoverse-V, Apple M1): the scheduling gain may be small and results vary between CP-SAT runs.
- Large monolithic kernels: the splitting heuristic gives up optimality, is incompatible with register allocation on symbolic registers (allocate first), and crashes with software pipelining in open issue #94 (AttributeError in Heuristics.periodic on a 292-instruction Dilithium loop).
- Builds that must be reproducible bit for bit: CP-SAT is non-deterministic, so re-optimization gives different schedules and timings.
- x86-64 targets: there is no x86 model (only AArch64, Armv8.1-M, Armv7-M and RISC-V directories under slothy/targets).

## How it is fast

The input is lifted to a data-flow graph, and the scheduling, register renaming and periodic loop interleaving choices are encoded as a constraint model that Google OR-Tools CP-SAT solves while minimizing predicted stalls. The microarchitecture model holds issue width, latencies, throughputs, forwarding paths and execution-unit counts, so the gain is in-order pipeline latency hiding. Software pipelining moves loads into the previous iteration and peels a preamble and postamble; address offset fixup rewrites immediate offsets so post-increment loads and stores can be reordered.

## Compared with alternatives

Pick SLOTHY over STOKE when you target Arm or RISC-V and must keep your own instruction choice (constant-time crypto), since STOKE searches over x86-64 instruction sequences; pick it over Unison when your kernel is hand-written assembly rather than LLVM back-end output, and over MaxAs or KeplerAs when the target is a CPU core rather than an NVIDIA GPU.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python package pinned to ortools==9.15.6755, sympy==1.14.0, unicorn==2.1.4; LLVM llvm-mc, llvm-nm and llvm-readobj for the selftest, llvm-mca (LLVM 18+) for optional estimates; output is plain assembly with no runtime dependency |
| **Minimum toolchain** | Python 3.10 to 3.14 (3.11+ for development); PyPI slothy 0.2.2 (2026-06-12); used on Ubuntu 21.10+ and macOS 12.6+ |
| **Platforms** | Output targets: Armv8.1-M+Helium (Cortex-M55, M85), Armv7-M (Cortex-M4, M7 models), AArch64 (Cortex-A55; experimental Cortex-A72, Cortex-X/Neoverse-V, Apple M1 Firestorm/Icestorm), RISC-V RV32/64 IMB (XuanTie C908) |
| **Thread safety** | not documented (offline tool run before the build) |
| **Drop-in for the baseline** | partial — the optimized .s replaces your hand-written kernel region with the same symbols and registers you reserve, but SLOTHY itself is an offline Python tool, not a library you link |

## Gotchas

- The built-in selfcheck only proves the output DFG is isomorphic to the input DFG; config.py and the tutorial say it is blind to address offset fixup and to missing reserved_regs or output registers, the most common cause of code that passes the selfcheck but is functionally wrong.
- unsafe_address_offset_fixup is on by default for backwards compatibility, and config.py says it is UNSOUND unless address registers are used only by loads and stores; out-of-range immediates after fixup can also make the output fail to assemble (paper/README.md: re-run the script).
- The empirical selftest (randomized unicorn emulation) is disabled with only a warning when llvm-mc, llvm-nm or llvm-readobj is missing, and it does not handle register-offset loads and stores (#276) or literal-pool loads (#381), both open; #382 (open) says the ld2 lane model is wrong for .S/.H lanes and can over-constrain schedules.
- No SLOTHY-attributable measurement was reachable: the TCHES 2024 tables (eprint 2022/1303) and slides are blocked, the only in-repo number is an LLVM-MCA model estimate (31 to 21 cycles per iteration on a toy Cortex-A55 loop), and pqax/pqmx stub out cycle counts unless built with CYCLES=PMU or PERF on real boards.

## Known shortcomings

- TCHES 2024 paper blocked; the snippet only says it 'matches or beats prior art'; the only number in the repo is a modeled LLVM-MCA estimate on a toy loop; s2n-bignum PR #108 merged but AWS-LC #1469 (74%) was closed unmerged although the README says merged. Paper-access retier candidate (B).
- No SLOTHY-attributable measurement is reachable (the TCHES paper, eprint and iacr.org all ENOTFOUND; a slide snippet 'Ours clean 1914 / Ours SLOTHY 891' has no workload label). Correction: AWS-LC PR #1478 (merged 2024-03-06) reports the same 12867.1 to 22361.9 ops/sec (74%, Graviton 2 c6g.16xlarge), but it swaps in Lenngren's algorithm, runs off the A55 target, and says the _alt forms stay faster. Correctness gotchas: unsafe_address_offset_fixup is on by default and called UNSOUND in config.py; the selfcheck is blind to it; the selftest switches itself off when LLVM tools are missing; open issues #276, #381, #382, #94.

## Caveats and trade-offs

The TCHES 2024 paper 'Fast and Clean: Auditable high-performance assembly via constraint solving' (issue 1, pp. 87-132, artifact at artifacts.iacr.org/tches/2024/a6; eprint 2022/1303) is peer-reviewed but could not be opened (tches.iacr.org and eprint unreachable); WebSearch snippets only say the SLOTHY-optimized code matches or beats prior art in all cases, with no cycle counts. The repo ships clean and optimized sources (paper/clean, paper/opt), optimization scripts (paper/scripts) and a Docker artifact; cycle benchmarks live in pqax/pqmx and need Cortex-A55/A72 devices or an MPS3 FPGA board (AN547/AN555), and builds without CYCLES=PMU/PERF stub out cycle counts. The only number in the repo is the tutorial's LLVM-MCA model estimate for a toy Cortex-A55 loop (31 to 21 cycles per iteration), a model output against its own unscheduled input, not a measurement. Adoption is real: s2n-bignum PR #108 (merged 2024-02-15) imported the SLOTHY-generated Lenngren-based X25519 without benchmark numbers; the AWS-LC PR #1469 that reports 12867.1 to 22361.9 ops/sec ('74% speedup', Graviton 2) was closed without merge on 2024-03-06 (the README calls it merged) and mixes the algorithm change with SLOTHY scheduling. CP-SAT is non-deterministic, so re-optimization results vary, especially for the heuristic Cortex-A72 model. SLOTHY is a Python tool that produces assembly; it is not linked into the user's program.

Microarchitecture-specific by design: each output is scheduled for one core model (portability note: code tuned for Cortex-A55 is not tuned for other cores). Solver time is seconds to minutes for under 50 instructions and minutes to hours for up to 150 instructions; larger kernels need heuristics. Python tool using Google OR-Tools.

## Maintenance

Actively maintained (last commit 2026-10-02, monthly PyPI releases from 0.1.0 in July 2025 to 0.2.2 in June 2026, used by s2n-bignum, mlkem-native and CMSIS-DSP via Arm EndpointAI), MIT-licensed, beta per its classifier; no harness bug found, but correctness rests on the user's reserved_regs/output configuration, the default-on unsound address offset fixup and a selftest that silently turns off without LLVM, and the speed claim has no reachable SLOTHY-attributable measurement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** No SLOTHY-attributable measured speedup was reachable: the peer-reviewed TCHES 2024 paper (issue 1, pp. 87-132; eprint 2022/1303) is blocked and its abstract snippet only says the optimized code matches or beats prior art; the repo's README is directional, its tutorial gives only an LLVM-MCA model estimate for a toy loop, and the paper artifact (paper/, pqax, pqmx) needs boards that were not run.
- **Verifier notes:** Repo confirmed: MIT (LICENSE file, SPDX MIT), 352 stars, 45 forks, not archived, last commit 2026-10-02 (active), PyPI package 'slothy'. Notable despite under 1k stars (TCHES paper, used by s2n-bignum/AWS-LC, CMSIS-DSP via Arm EndpointAI, mlkem-native), so kept at D rather than rejected. Paper-access retier candidate: with the TCHES 2024 tables plus the public pqax/pqmx harness and named cores it could reach B (or A if pqax/pqmx Makefiles give compiler and flags).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-09 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/slothy-optimizer/slothy>
  - <https://github.com/slothy-optimizer/slothy/commits>
  - <https://github.com/slothy-optimizer/slothy/tree/main/paper>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/README.md>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/paper/README.md>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/paper/artifact/README.md>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/docs/source/tutorial/README.md>
  - <https://raw.githubusercontent.com/slothy-optimizer/pqax/HEAD/README.md>
  - <https://raw.githubusercontent.com/slothy-optimizer/pqmx/HEAD/README.md>
  - <https://github.com/aws/aws-lc/pull/1469>
  - <https://github.com/awslabs/s2n-bignum/pull/108>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/README.md>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/paper/README.md>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/paper/artifact/README.md>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/docs/source/tutorial/README.md>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/slothy/core/config.py>
  - <https://raw.githubusercontent.com/slothy-optimizer/slothy/HEAD/slothy/targets/README.md>
  - <https://github.com/slothy-optimizer/slothy/tree/main/slothy/targets>
  - <https://github.com/slothy-optimizer/slothy/tree/main/slothy/targets/arm_v7m>
  - <https://github.com/slothy-optimizer/slothy/tree/main/slothy/targets/riscv>
  - <https://github.com/slothy-optimizer/slothy/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/slothy-optimizer/slothy/issues?q=is%3Aissue+incorrect>
  - <https://github.com/slothy-optimizer/slothy/issues/165>
  - <https://github.com/slothy-optimizer/slothy/issues/382>
  - <https://github.com/slothy-optimizer/slothy/issues/94>
  - <https://pypi.org/pypi/slothy/json>
  - <https://github.com/aws/aws-lc/pull/1478>
  - <https://github.com/dop-amin/ches2025-slothy-tutorial>
  - <https://github.com/mupq/pqm7>
  - <https://raw.githubusercontent.com/mupq/pqm7/HEAD/README.md>
  - <https://raw.githubusercontent.com/mupq/pqm7/HEAD/benchmarks.md>
  - https://eprint.iacr.org/2022/1303.pdf (blocked: ENOTFOUND)
  - https://icscm.ub.rub.de/index.php/TCHES/article/view/11241 (blocked: ENOTFOUND)
  - https://iacr.org/submit/files/slides/2024/tches/tches2024/1_11/slides.pdf (blocked: ENOTFOUND; snippet only via WebSearch)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/slothy-optimizer/slothy`) · [data/wave13/enrich/raw/github_com_slothy_optimizer_slothy.json](../../../data/wave13/enrich/raw/github_com_slothy_optimizer_slothy.json) (enrichment confidence 0.6)

</details>
