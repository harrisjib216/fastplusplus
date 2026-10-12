# TuringAs (SASS assembler for Volta, Turing and Ampere)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `MIT` · 🔴 abandoned

> Python SASS assembler for NVIDIA SM70-SM86; its authors' hand-written Winograd kernels beat cuDNN 7.6.1 2.13-2.65x (paper only).

| | |
|---|---|
| **Beats** | NVIDIA cuDNN 7.6.1 (Winograd convolution kernels that the PPoPP 2020 paper wrote with this assembler) |
| **Claimed result** | Snippet only (paper PDF unreachable here; PPoPP 2020 abstract via search snippets): single-precision batched Winograd convolution kernels written in SASS with TuringAs reach up to 2.13x speedup on a Volta V100 and up to 2.65x on a Turing RTX 2070 over cuDNN 7.6.1, and up to 93% of device peak. The repo README has no numbers. |
| **Workload** | Batched Winograd convolution on NVIDIA Volta/Turing GPUs (paper 'Optimizing Batched Winograd Convolution on GPUs', which the README asks users to cite). |
| **Metric** | throughput |
| **Hardware** | NVIDIA Tesla V100 (Volta) and GeForce RTX 2070 (Turing), per the paper abstract (snippet only) |
| **Adoption** | 249 stars |
| **Last commit** | 2022-01-13 |
| **Links** | [repository](https://github.com/daadaada/turingas) · [benchmark](https://home.cse.ust.hk/~weiwa/papers/yan-ppopp20.pdf) |

## Verdict

The only numbers are in the PPoPP 2020 paper by Yan, Wang and Chu, which could not be opened here; they were read from search snippets only. Single-precision batched Winograd convolution kernels hand-written in SASS with TuringAs reach up to 2.13x on a Tesla V100 and up to 2.65x on an RTX 2070 over cuDNN 7.6.1's Winograd convolution, and up to 93% of device peak. The same snippets say cuDNN 7.6.1's Winograd was itself only 0.81-1.67x (average 1.4x) faster than GEMM-based convolution, so the baseline is cuDNN's Winograd path, not necessarily its fastest algorithm. The repository contains no comparison benchmark and no Winograd code.

## Use it when

- Hand-tuning a hot CUDA kernel (GEMM, convolution, microbenchmarks) on Volta (SM70), Turing (SM75) or Ampere (SM80, SM86) after nvcc output has hit a scheduling or register-allocation ceiling
- GPU microarchitecture research, such as measuring instruction latency, shared-memory throughput or reuse-cache effects; the repo's examples/bench/smem times LDS with SR_CLOCKLO
- Teaching or studying the Volta and Turing encoding and control-code format; tools/disasm.py turns cuobjdump output back into TuringAs syntax
- Pure-Python tooling with no dependencies beyond the standard library, which is easy to vendor and patch

## Skip it when

- Ada (SM89), Hopper (SM90) or Blackwell GPUs: only -arch 70, 75, 80 and 86 are accepted, and issue #13 (2024, no reply) calls the project dead for new GPUs
- You want automatic scheduling: you write every stall count, barrier and yield bit by hand. The owner declined to add a scheduler in issue #4 ('I'd rather leave this task to high-level compilers').
- You want the Winograd speedups: the kernels behind the 2.13x and 2.65x claims were never released (issue #2, open since February 2020, 'We plan to open source the Winograd implementation later')
- Code that needs texture or surface instructions, CALL, JMP, or multiple kernels and relocations in one cubin: these are missing, and one invocation emits one kernel
- Production builds: there are no releases (setup.py version 0.1), no tests, and no maintenance since 2022-01-13

## How it is fast

The assembler itself is not the fast part. Writing SASS directly gives you control that nvcc and ptxas do not expose: register allocation and bank conflicts, operand-reuse cache flags (.reuse), and the per-instruction control codes (stall cycles, yield, read and write dependency barriers, wait masks). The PPoPP 2020 paper used that control to build batched Winograd convolution kernels with better latency hiding and data reuse than cuDNN's. The encoder is a table of regex grammar rules for 59 opcodes that emit 128-bit Volta-style instruction words.

## Compared with alternatives

Pick TuringAs over MaxAs (Maxwell and Pascal only, with a built-in scheduler and register allocator, and a public SGEMM walkthrough that beats cuBLAS by 4.8-25%) and KeplerAs (Kepler only, with a PPoPP 2017 artifact measuring 1.15x over cuBLAS 7.0 SGEMM) when the target is Volta, Turing or Ampere, which neither supports. Unlike those siblings, though, TuringAs ships no published kernel that reproduces its headline numbers.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Python standard library only); running the .cubin needs the CUDA driver API and an NVIDIA GPU |
| **Minimum toolchain** | Python 3.6+ (README; uses f-strings) |
| **Platforms** | Emits SASS for NVIDIA SM70, SM75, SM80 and SM86 (the -arch choices in main.py); the assembler runs anywhere Python runs |
| **Thread safety** | not documented; inline-code blocks and include files are exec()'d into the assembler module's globals, so separate runs in one process share and overwrite state |
| **Drop-in for the baseline** | no |

## Gotchas

- Assembling a file runs arbitrary Python: &lt;CODE&gt; blocks and every -inc include file are passed to exec(), and any {...} on a line is passed to eval(), all in the assembler's module globals. Include files are executed twice, once by ExpandCode and once by ExpandInline. Never assemble untrusted .sass files.
- Control-code notation differs from MaxAs: the wait-barrier mask in 'wait:read:write:yield:stall' is parsed as a decimal integer (int(watdb) in grammar.py ReadCtrl, matching tools/disasm.py's {:02d}), although the regex accepts hex digits. '3f' raises ValueError and '10' means barriers 1 and 3, not barrier 4. Read and write barrier indices are 0 to 5 (fixed in issue #8).
- -arch only sets the cubin ELF header flags (cubin.py). GenCode uses one opcode table for every architecture with no per-architecture check, so an instruction the target lacks is not rejected, for example uniform-datapath ops on SM70 or LDGSTS below SM80 (inference from the source). The register count is a heuristic: the highest register index plus 1, plus 4 when above 8, and a FIXME notes that multi-register operands are not counted. Check the result with cuobjdump.
- The README's TODO list is out of date: grammar.py already has LDSM, F2F, F2FP, F2I, I2F, uniform-datapath ops (UMOV, USHF, UIADD3, ULEA, ULDC, S2UR), the HMMA, IMMA and BMMA tensor-core ops, and Ampere's LDGSTS, LDGDEPBAR and DEPBAR. Texture, surface, CALL and JMP are still absent.

## Known shortcomings

- Repo carries no numbers; the claim rests on the PPoPP 2020 paper (2.13x V100, 2.65x RTX 2070 vs cuDNN 7.6.1) read from search snippets only, and the Winograd kernels were never released. Paper-access retier lead to B.
- Enricher: evidence still snippet only (paper PDF unreachable); the Winograd kernels were never released (issue #2 open since 2020); the baseline is cuDNN 7.6.1's Winograd path, itself only 0.81-1.67x over GEMM convolution; exec/eval of inline Python and include files (include files run twice); wait mask decimal rather than hex like MaxAs; one opcode table for all architectures with no per-arch check. Lead: daadaada/gas (same author's C++ GPU assembly language, no numbers, no licence).

## Caveats and trade-offs

The speedup belongs to the paper's Winograd kernels, not to this repo: the repo holds only the assembler plus two small examples (examples/bench/smem is a shared-memory LDS microbenchmark with no comparison, examples/copy_element), and the Winograd kernels are not public (the author's repository list has no such repo; daadaada/CUDA-Winograd is a fork of xuqiantong/CUDA-Winograd, different CUDA kernels with no SASS). Paper: Yan, Wang, Chu, PPoPP 2020, pages 32-44, DOI 10.1145/3332466.3374520; home.cse.ust.hk, scholars.hkbu.edu.hk and ppopp20.sigplan.org all fail DNS here, so numbers are snippet only. One search summary says the comparison is against cuDNN's Winograd algorithm specifically (not verified). Single precision only. Baseline is NVIDIA's compiled cuDNN kernels, not GNU as, NASM or MASM; NVIDIA ships no public SASS assembler. Last commit 2022-01-13; Ampere support and several instruction classes are unfinished per the README TODO list. Paper-access retier lead (B if the paper is reached).

SASS for SM70, SM75 and SM80 only; many instruction classes are marked TODO in the README (type conversion, LDSM, texture, surface, uniform datapath).

## Maintenance

Abandoned since 2022-01-13 (54 commits, no releases, 2022-2024 issues unanswered), but MIT-licensed and only about 1,900 lines of dependency-free Python, so it is easy to vendor for SM70-SM86 experiments; the evidence tier rests on an unopened paper and on kernels that were never released.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo (README, examples/bench/smem, examples/copy_element) has no performance numbers; the only numbers are in the PPoPP 2020 paper the README asks users to cite, whose PDF host (home.cse.ust.hk) and PPoPP/HKBU pages fail DNS here, so the 2.13x/2.65x figures come from search snippets only. A peer-reviewed paper could support B once opened; snippet-only evidence stays at C.
- **Verifier notes:** Metadata checked: MIT (LICENSE.txt, Copyright 2020 Da Yan @ HKUST), 249 stars, 42 forks, last commit 2022-01-13 (abandoned), not a fork or archived. Numbers could not be opened (paper hosts fail DNS); kept at C on consistent search snippets (2.13x V100, 2.65x RTX 2070 vs cuDNN 7.6.1, 93% of peak). Shortcomings: kernels behind the claim are unreleased, tool itself has no benchmark, snippet-only evidence.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-52 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/daadaada/turingas>
  - <https://github.com/daadaada/turingas/commits>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/README.md>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/LICENSE.txt>
  - <https://github.com/daadaada/turingas/tree/master/examples>
  - <https://github.com/daadaada/turingas/tree/master/examples/bench/smem>
  - <https://github.com/daadaada?tab=repositories>
  - <https://github.com/daadaada/CUDA-Winograd>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/README.md>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/setup.py>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/turingas/main.py>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/turingas/turas.py>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/turingas/grammar.py>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/turingas/cubin.py>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/turingas/ELF.py>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/turingas/__init__.py>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/examples/bench/smem/Makefile>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/examples/bench/smem/lds32.sass>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/examples/bench/smem/main.cu>
  - <https://raw.githubusercontent.com/daadaada/turingas/HEAD/tools/disasm.py>
  - <https://github.com/daadaada/turingas>
  - <https://github.com/daadaada/turingas/tree/master/turingas>
  - <https://github.com/daadaada/turingas/tree/master/examples/bench/smem>
  - <https://github.com/daadaada/turingas/tree/master/tools>
  - <https://github.com/daadaada/turingas/commits/master>
  - <https://github.com/daadaada/turingas/issues?q=is%3Aissue>
  - <https://github.com/daadaada/turingas/issues/2>
  - <https://github.com/daadaada/turingas/issues/4>
  - <https://github.com/daadaada/turingas/issues/13>
  - <https://github.com/daadaada?tab=repositories>
  - <https://github.com/daadaada/gas>
  - <https://github.com/daadaada/misc>
  - https://home.cse.ust.hk/\~weiwa/papers/yan-ppopp20.pdf (ENOTFOUND)
  - https://hgpu.org/?p=20724 (ENOTFOUND)
  - WebSearch: "Optimizing Batched Winograd Convolution on GPUs" Yan Wang Chu PPoPP 2020 cuDNN speedup SASS TuringAs
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/daadaada/turingas`) · [data/wave13/enrich/raw/github_com_daadaada_turingas.json](../../../data/wave13/enrich/raw/github_com_daadaada_turingas.json) (enrichment confidence 0.6)

</details>
