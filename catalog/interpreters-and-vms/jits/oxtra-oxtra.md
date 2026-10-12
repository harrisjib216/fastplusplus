# oxtra

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Student-built x86-64 to RISC-V user-mode binary translator; up to 2.6x faster than QEMU 4.1.0 on tiny inputs, slower on larger ones.

| | |
|---|---|
| **Beats** | QEMU 4.1.0 (x86-64 binary translation) |
| **Claimed result** | Paper text: oxtra is 'up to twice as fast as QEMU' for small inputs. Medians, oxtra (c) vs QEMU 4.1.0: primes below 10,000 20.68 ms vs 54.71 ms (2.65x, derived from page data); gzip 132 kB 60.42 ms vs 154.83 ms (2.56x, derived from page data); gzip 526 kB 270.5 ms vs 348.9 ms (paper: 'merely 25% faster'); gzip 13 MB 2623 ms vs 3137 ms (paper: 20% faster); primes below 1,000,000 3685 ms vs 2720 ms (oxtra 35% slower). QEMU executes 1.70x (primes 10k) down to 1.13x (gzip 13 MB) as many RISC-V instructions as oxtra (c); oxtra (c) uses 3.87x (primes) and 2.55x (gzip) less peak memory than QEMU. |
| **Workload** | Static x86-64 guest programs (a primes calculator and gzip 1.10.7 compressing floating-point CSV files of 132 kB, 526 kB and 13 MB) translated to RISC-V by oxtra and by QEMU; also instruction counts and memory use. |
| **Metric** | throughput |
| **Hardware** | No real RISC-V hardware: everything ran inside system-mode QEMU running Fedora RISC-V (host CPU not stated); instruction counts given as a hardware-independent proxy |
| **Compiler and flags** | Guests built with a modified musl-gcc fork (no SSE) and statically linked; host flags not stated |
| **Adoption** | 22 stars |
| **Last commit** | 2020-11-16 |
| **Links** | [repository](https://github.com/oxtra/oxtra) · [benchmark](https://github.com/oxtra/oxtra/blob/master/documentation/paper/Results.tex) |

## Verdict

A first-party lab-course report (summer semester 2019, Results.tex) compares oxtra 1.0.1 with QEMU 4.1.0 user mode on static no-SSE musl x86-64 guests, with everything inside system-mode QEMU on an unstated host CPU. Medians: primes below 10,000, 20.68 vs 54.71 ms (2.65x); gzip 132 kB, 60.42 vs 154.83 ms (2.56x); gzip 526 kB, 270.5 vs 348.9 ms (1.29x); gzip 13 MB, 2623 vs 3137 ms (1.20x); primes below 1,000,000, 3685 vs 2720 ms (QEMU 1.35x faster). Ratios are derived from page data. The two large inputs used only 5 runs each.

## Use it when

- Studying how to translate x86-64 to RISC-V without an IR: lazy flags with cross-block liveness, return-stack call/ret and register pinning are each documented in the project report (documentation/paper/Paper.pdf) and in a small BSD-3-Clause codebase
- Short-running, small static musl x86-64 command-line tools on an RV64 Linux host, where translation and startup dominate. The report's wins come from these: primes below 10,000 and gzip on a 132 kB file
- Memory-constrained RV64 hosts, where the report measured peak memory 2.55x (gzip) to 3.87x (primes) lower than QEMU 4.1.0
- As a starting point for a research DBT that targets RISC-V hosts specifically

## Skip it when

- Long-running or compute-heavy guests: on primes below 1,000,000 oxtra was 35% slower than QEMU (3685 vs 2720 ms), and on gzip of a 13 MB file only about 20% faster
- Ordinary x86-64 binaries: any SSE, x87 or AVX instruction is unsupported, and so are glibc, dynamic linking and threads. That excludes almost all distro-built software, and even printf and malloc in stock musl builds needed a no-SSE recompile
- Running untrusted code: guest and translator share one address space, guest memory is not emulated, and the report says not all segmentation faults are detected
- Guests that generate or modify code (JITs, self-modifying code): translated code is translated once and never invalidated
- Anything needing support or newer QEMU baselines: the project stopped after a 2019 lab course (last commit 2020-11-16), and the only comparison is against QEMU 4.1.0

## How it is fast

There is no intermediate representation: fadec decodes each x86 instruction into a C++ class that emits RISC-V directly. All 16 x86 GPRs are statically mapped to RISC-V registers (argument registers line up, so forwarded syscalls need no moves), and s1/s8/s9/s10/s11 hold the return stack, call table, TLB, jump table and context. Blocks run to the next jmp/call/ret/syscall, so conditional branches do not end a block. Translated code is kept forever and static links are patched into direct jumps (block chaining). x86 flags are evaluated lazily: a reverse pass marks which instructions must materialise which flags, with recursive look-ahead into statically linked successor blocks (--flag-depth, default 4). A call table plus ring-buffer return stack turns ret into a check and a direct jump. Guest memory is not emulated: oxtra links itself high (0x7F000000) and the guest uses its own addresses directly.

## Compared with alternatives

Pick oxtra only to study a compact x86-64-to-RISC-V translator without an IR. To actually run x86-64 software on RISC-V, Box64 is the better choice: maintained, with SSE/AVX and dynamic glibc programs on RISC-V hosts. Instrew (LLVM-based, from oxtra's advisor's group) is the research option for peak translated-code quality.

## Integration

| | |
|---|---|
| **Form** | single statically linked executable (CMake build); a prebuilt RV64 binary ships as release v1.0.1 |
| **Dependencies** | vendored libs/fadec (x86 decoder) and libs/fmt; a riscv64-unknown-linux-gnu cross toolchain to build; guests need musl with SSE disabled (the oxtra/musl-gcc fork or helper/compile_c.sh flags) |
| **Minimum toolchain** | CMake 3.11+, GCC only (CMakeLists.txt stops with 'Only GNUCC is supported'), C++17; release flags -O2 -ffixed-s11 -Wl,-Ttext-segment=0x7F000000, linked -static |
| **Platforms** | Host: 64-bit RISC-V Linux only (on x86 machines the README runs it inside QEMU via a Docker image). Guest: x86-64 Linux static ELF, the integer subset listed in Appendix C |
| **Thread safety** | Not applicable for guests: multithreaded guest programs are unsupported (report sections 3.1 and 6); the translator itself runs one guest thread. |
| **Drop-in for the baseline** | partial: `oxtra prog -a "args"` replaces `qemu-x86_64 prog args` only for static, no-SSE musl binaries that stay within the supported instruction and syscall subset |

## Gotchas

- Harness flaw: every timing ran with both translators themselves inside system-mode QEMU (Fedora RISC-V) on an unstated host. The data show instruction counts do not track time there: on primes below 1,000,000 oxtra (c) executes 14% fewer instructions than QEMU (0.8607 normalised) yet runs 35% longer, against the report's claim that instruction counts are the more objective proxy for real hardware. Our inference, untested: the outer emulator must retranslate whatever code each DBT generates, which may favour oxtra (about 0.8x QEMU's generated instructions) on exactly the short inputs where it wins.
- The repo does have a timing script, helper/benchmark.sh. It runs a fixed 10 iterations and timestamps with `date +%s%N`, so a `date` process spawn falls inside every sample. The report's boxplots use 100 runs (small inputs) and 5 runs (large inputs), so the script that produced the published numbers is not in the repo.
- The project's own claims disagree: the README says the current version 'consistently beats qemu', and the conclusion says 'up to 20% faster than QEMU when executing gzip', while Results.tex shows 2.56x on the 132 kB gzip input and a 35% loss on primes below 1,000,000.
- Translated code is never freed (no code cache), so memory grows with the guest's code footprint. The adjust and direction flags are not modelled (std and popf are unimplemented), and common instructions such as sbb, xchg, cmpxchg, bswap and bsf are absent from the supported list.

## Known shortcomings

- Student project report, not peer reviewed: timings were taken inside QEMU emulation with the host CPU unstated and no benchmark scripts; oxtra is 35% slower than QEMU on primes below 1M despite the README's 'consistently beats qemu'. Abandoned 2020; off-baseline (QEMU).

## Caveats and trade-offs

Student project report (documentation/paper/Paper.pdf, Results.tex), not peer reviewed. All timings were taken inside system-mode QEMU running Fedora RISC-V on an unstated host, which the authors say obscures the timing results; the large cases use only 5 runs. The README claims the current version 'consistently beats qemu in our toy examples', but the paper shows oxtra 35% slower on primes below 1 million and its advantage shrinking as inputs grow (the authors: 'oxtra quickly becomes slower than QEMU as input become larger'). The repo ships only the gzip input files, no benchmark scripts. Baseline is QEMU 4.1.0 (2019). oxtra supports only a small x86-64 subset, no SSE, statically linked musl binaries only (guests built with the project's musl-gcc fork). Baseline is not one of PyPy, LuaJIT, V8, HotSpot.

Executes statically linked x86-64 programs only, no SSE support, needs a custom musl fork instead of glibc; RISC-V host only.

## Maintenance

Abandoned university project (last commit 2020-11-16; the README says the authors no longer have time to contribute; 0 open issues). It is BSD-3-Clause and small enough to read or fork as reference code, but it is not a usable x86 compatibility layer for real software.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** documentation/paper/Results.tex (first-party student report, not peer reviewed) gives boxplot medians for oxtra (a/b/c), QEMU 4.1.0 and native on primes and gzip; the repo holds only the gzip input files (documentation/paper/benchmarking/\*.txt), no benchmark scripts, and timings ran inside system-mode QEMU on an unstated host CPU with host compiler flags unstated, so not A or B.
- **Verifier notes:** Record accurate; numbers match Results.tex. Shortcomings: student report, emulated timings on unstated host, no benchmark scripts, loses 35% to QEMU on the larger primes run despite the README's 'consistently beats qemu', toy-scale x86 subset, abandoned since 2020.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/oxtra/oxtra/master/documentation/paper/Results.tex>
  - <https://raw.githubusercontent.com/oxtra/oxtra/master/README.md>
  - <https://raw.githubusercontent.com/oxtra/oxtra/master/LICENSE>
  - <https://github.com/oxtra/oxtra>
  - <https://github.com/oxtra/oxtra/commits>
  - <https://github.com/oxtra/oxtra/tree/master/documentation/paper>
  - <https://github.com/oxtra/oxtra/tree/master/documentation/paper/benchmarking>
- **Sources the enricher read:**
  - <https://github.com/oxtra/oxtra>
  - <https://raw.githubusercontent.com/oxtra/oxtra/master/README.md>
  - <https://raw.githubusercontent.com/oxtra/oxtra/master/LICENSE>
  - <https://raw.githubusercontent.com/oxtra/oxtra/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/oxtra/oxtra/master/documentation/paper/Results.tex>
  - <https://raw.githubusercontent.com/oxtra/oxtra/master/documentation/paper/Paper.pdf>
  - <https://github.com/oxtra/oxtra/tree/master/helper>
  - <https://raw.githubusercontent.com/oxtra/oxtra/master/helper/benchmark.sh>
  - <https://raw.githubusercontent.com/oxtra/oxtra/master/helper/compile_c.sh>
  - <https://github.com/oxtra/oxtra/tree/master/src>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/oxtra/oxtra`) · [data/wave12/enrich/raw/github_com_oxtra_oxtra.json](../../../data/wave12/enrich/raw/github_com_oxtra_oxtra.json) (enrichment confidence 0.75)

</details>
