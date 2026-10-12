# rv8

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> RISC-V to x86-64 user-mode JIT binary translator; its 2017 paper shows about 1.8x faster than QEMU riscv64 user mode.

| | |
|---|---|
| **Beats** | QEMU (RISC-V user-mode emulation) |
| **Claimed result** | CARRV 2017 paper (Clark and Hoult), Figure 9: geomean runtime ratio to native x86-64 at -O3 is rv8 2.62 vs QEMU riscv64 4.68 and QEMU aarch64 4.57, so about 1.79x faster than QEMU riscv64 and 1.74x faster than the faster QEMU (derived from page data); Figure 10 at -Os: rv8 2.47 vs QEMU riscv64 4.62 (about 1.87x, derived from page data) and QEMU aarch64 5.20. Conclusion: 'on average approximately 75% faster than the leading competitor', and on some benchmarks 'approximately 30% slower than native x86-64 code'. Per-benchmark -O3 runtimes (Figure 7, seconds, rv8 vs QEMU riscv64): qsort 1.22 vs 4.76, dhrystone 0.20 vs 0.57, primes 0.70 vs 1.26, aes 1.53 vs 2.16, miniz 1.60 vs 2.21, sha512 0.81 vs 1.24, norx 1.20 vs 1.17 (rv8 slower on norx). |
| **Workload** | rv8-bench suite (aes, dhrystone, miniz, norx, primes, qsort, sha512) compiled for riscv64 at -O3 and -Os and run under the rv8 x86-64 JIT (hybrid interpretation plus translation of hot paths, macro-op fusion) and QEMU riscv64 user-mode, with QEMU aarch64 running aarch64 builds and native x86-64 builds as references; runtimes in seconds. |
| **Metric** | throughput |
| **Hardware** | Paper names no CPU. rv8-bench data/template.md: Intel Core i7-5557U Broadwell, 3.10-3.40 GHz (the template calls it 6th-gen; the i7-5557U is a Broadwell part). |
| **Compiler and flags** | Paper states none. rv8-bench data/template.md: guest and native benchmarks built with GCC 7.2.0 and musl libc at -O3, -O2 and -Os, all -fPIE (its prose says GCC 7.1.0; README names musl-riscv-toolchain 7.1.0-2); best of 20 runs. Host build flags of rv8 and QEMU, and the QEMU version (riscv/riscv-qemu fork, 2017), not stated. |
| **Adoption** | 727 stars |
| **Last commit** | 2018-09-22 |
| **Links** | [repository](https://github.com/michaeljclark/rv8) · [benchmark](https://carrv.github.io/2017/papers/clark-rv8-carrv2017.pdf) |

## Verdict

In the authors' peer-reviewed CARRV 2017 paper, seven integer rv8-bench programs (aes, dhrystone, miniz, norx, primes, qsort, sha512; riscv64, GCC 7.2.0 and musl, static -fPIE, best of 20 runs) have a geomean runtime of 2.62x native x86-64 under rv8 at -O3, against 4.68x for 2017 riscv-qemu user mode (about 1.79x faster, derived from page data) and 4.57x for QEMU aarch64. At -Os the figures are 2.47x vs 4.62x (about 1.87x). rv8 is slightly slower than QEMU riscv64 on norx at -O3 (1.20 s vs 1.17 s). The host (Core i7-5557U Broadwell) is named only in rv8-bench's results template, not in the paper. A 2018 independent study ('Towards a High-Performance RISC-V Emulator', search snippet only, paper not opened) reports average MiBench slowdowns of 3.16x for rv8 and 7.07x for QEMU.

## Use it when

- Studying or teaching dynamic binary translation: the RV64 emitter (src/jit/jit-emitter-rv64.h, about 4,300 lines) and the CARRV 2017 paper show static register mapping, trace inlining and macro-op fusion in compact form
- Running integer-heavy, statically linked RV64 or RV32 Linux binaries (musl static builds like rv8-bench's) on an x86-64 Linux or macOS host, faster than the 2017-era QEMU riscv64 user mode
- Prototyping new fusion patterns or register-allocation ideas for RISC-V-on-x86 translation, where a small codebase matters more than ISA coverage
- Generating RISC-V opcode maps, LaTeX listings, decoders or instruction histograms with rv-meta and rv-bin

## Skip it when

- Floating-point or atomic-heavy guests: only the base integer and M instructions are JIT-compiled, while F, D and A fall back to the interpreter (README; issues #32 and #34 are still open). Every benchmark behind the speed claim is integer-only
- Dynamically linked, glibc or multithreaded programs, or programs that need more than a small set of Linux syscalls: rv-jit supports static ELF only (#58) and ioctl is a stub (#49)
- Isolating untrusted guest code: the JIT shares one address space with the emulator and emits unchecked host loads and stores, so it is not a sandbox
- Current RISC-V software: the target is the 1.9.1 privileged-spec era (no V, B/Zb\*, or other later extensions), the only JIT host is x86-64, and there are no commits since 2018
- Anything that needs a maintained emulator against a current QEMU: the only head-to-head data uses the 2017 riscv/riscv-qemu fork, and QEMU's RISC-V TCG has been upstream and improved since

## How it is fast

It starts as an interpreter that profiles for hot paths; after a trace runs a set number of times (trace_iters, default 100), it records the path through calls and emits x86-64 code with AsmJit. Register mapping is static: twelve hot RISC-V registers (chosen from dynamic profiles) live in fixed x86-64 registers, and the rest sit in a spill area at [rbp+off] that instructions use directly as CISC memory operands. Hot callees are inlined, with a compare-against-expected-return check. Indirect jumps go through a 1024-entry direct-mapped jump-target cache, and branch-tail trampolines are relinked lazily once their target is translated. Macro-op fusion turns common RISC-V idioms into single x86 instructions (AUIPC+ADDI into MOV, SLLI/SRLI 32 into MOVZX, shift/shift/OR into ROR). Guest loads and stores are emitted as plain host memory accesses at the guest address, with no MMU call or bounds check.

## Compared with alternatives

Pick rv8 only to study or extend a compact RISC-V-to-x86-64 translator built around static register mapping and macro-op fusion. For maintained RISC-V emulation pick libriscv (embeddable, sandboxed), rv32emu (RV32, benchmarked against QEMU v9.0.0) or RVVM (full-system RV64), all of which are active, unlike rv8.

## Integration

| | |
|---|---|
| **Form** | command-line executables (rv-jit, rv-sim, rv-sys, rv-bin, rv-meta) plus internal static libraries (libriscv_asm.a, libriscv_elf.a, libriscv_gen.a, libriscv_model.a, libriscv_util.a); GNU make build |
| **Dependencies** | git submodules: an AsmJit fork (michaeljclark/asmjit, old asmjit/base API) and riscv-meta; uses google::dense_hash_map; a RISC-V GNU toolchain (RISCV env var) is needed to build the test programs |
| **Minimum toolchain** | C++14 (-std=c++1y, -fno-rtti -fno-exceptions, default -O3 -fwrapv). README: gcc 5.4 or clang 3.4 minimum, gcc 6.3 or clang 3.8 recommended. GCC 11.4 fails to build without adding #include &lt;limits&gt; (issue #68, open) |
| **Platforms** | Host: x86-64 only (Linux, macOS; FreeBSD 11 listed as alpha). The host CPU needs RDTSCP (src/util/host.h); issue #48 reports 'illegal hardware instruction' on a Core 2 Duo. Guests: RV32IMAFDC and RV64IMAFDC, privileged ISA 1.9.1 |
| **Thread safety** | Not documented. The JIT run loop registers itself as a process-wide singleton (jit_singleton::current) and installs process-wide signal handlers, so plan on one emulated hart per process. |
| **Drop-in for the baseline** | partial: `rv-jit <elf>` replaces `qemu-riscv64 <elf>` only for static, single-image binaries that use rv8's small proxy-syscall set; no dynamic linking, and only the IM subset is JIT-compiled |

## Gotchas

- Harness flaw: rv8-bench.js counts a run as valid when the exit status is 0 and never checks program output, so the measurements never showed that rv8 computed correct results. The benchmark sources also have bugs. primes.c shifts an int 1 by up to 63 bits (undefined behaviour, so the sieve depends on how the compiler lowers it). qsort.c's comparator `*ia - *ib` overflows on the full-range ints it generates. norx.c's tag check is inverted and main zeroes the tag before decrypting. aes.c and norx.c print their memcmp result but always return 0. The rv8-vs-QEMU comparison stays valid because both run the same riscv64 binary, but native-vs-guest ratios rest on different compilations of UB-laden code.
- Native x86-64 reference runs are launched under `perf stat`, so perf startup is inside the native wall time. This affects only the ratios to native, not rv8 vs QEMU.
- The JIT's use_mmu flag is never set, so the MMU-call load/store path is dead code. Translated code reads and writes host memory directly at guest addresses in an identity-mapped shared address space (MAP_FIXED at the ELF's vaddr). By default it does not update instret (needs -i). fence.i flushes the whole trace cache.
- In the paper's summary table the two QEMU columns are swapped relative to Figures 9 and 10. Its '75% faster than the leading competitor' compares rv8 with QEMU aarch64 running aarch64 builds; against QEMU riscv64 the -O3 gap is 1.79x. Also, the riscv-qemu build line in rv8-bench's README configures only the softmmu targets, not the qemu-riscv64 user-mode binary the harness invokes.

## Known shortcomings

- Raised C to B on the CARRV 2017 paper (reached via raw.githubusercontent.com/carrv/carrv.github.io): geomean 2.62 against QEMU riscv64 4.68 at -O3, about 1.79x (derived from page data), but the paper omits CPU, compiler and QEMU version (i7-5557U and GCC 7.2.0 appear only in the rv8-bench template), its summary table swaps the QEMU columns, and rv8 is slower than QEMU on norx at -O3. Abandoned 2018; repo now at larkmjc/rv8. Off-baseline (QEMU).

## Caveats and trade-offs

Paper is peer-reviewed but written by the project's authors; its summary table swaps the two QEMU columns relative to Figures 9 and 10 (the figures are internally consistent with the runtime tables). rv8 is slower than QEMU riscv64 on norx at -O3. The 'leading competitor' in the 75% claim is QEMU aarch64 running aarch64 binaries, not a RISC-V baseline. The paper omits CPU, compiler and QEMU version; those come from the rv8-bench results template, which may postdate the paper's run (rv8.io/bench, the cited results page, was not reachable). Repo last touched 2018 and now lives at larkmjc/rv8 (the michaeljclark URL redirects). Baseline is not one of PyPy, LuaJIT, V8, HotSpot. rv32emu's VMIL'24 abstract (snippet only) claims to beat rv8.

Targets RISC-V 1.9.1 privileged spec era binaries on x86-64 hosts only; only the Linux syscall proxy ABI is implemented for the JIT simulator (README).

## Maintenance

Abandoned: last commit 2018-09-22, the repo now sits under larkmjc (the michaeljclark URL redirects), 42 open issues, and GCC 11+ needs a one-line &lt;limits&gt; patch to build. It is MIT-licensed, but the LICENSE file has no copyright line (issue #61), so it is usable for study and vendoring, not production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B: the peer-reviewed CARRV 2017 paper (opened via its raw.githubusercontent.com mirror of carrv.github.io) has runtime tables (Figures 7-10) for rv8 versus QEMU riscv64 and QEMU aarch64 on seven benchmarks, and the benchmark code is public in michaeljclark/rv8-bench. Not A: the paper states no host CPU, compiler or QEMU version; CPU (Core i7-5557U) and compiler (GCC 7.2.0, -O3/-O2/-Os, -fPIE) appear only in rv8-bench data/template.md, the template for the rv8.io/bench results page the paper cites, which later added a bigint benchmark, so its tie to the paper's run is unconfirmed.
- **Verifier notes:** Paper reached through raw.githubusercontent.com/carrv/carrv.github.io; numbers in the record's snippet are confirmed and now have tables, so tier raised C to B (could be A if rv8.io/bench shows the same numbers with the i7-5557U host). Shortcomings: paper omits CPU/compiler/QEMU version, swapped QEMU columns in its summary table, slower than QEMU on norx -O3, abandoned since 2018. Metadata checked: MIT (LICENSE lacks a copyright line), 727 stars, last commit 2018-09-22; GitHub now shows owner larkmjc.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/README.md>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/LICENSE>
  - <https://github.com/michaeljclark/rv8>
  - <https://github.com/michaeljclark/rv8/commits/master>
  - <https://github.com/michaeljclark/rv8/tree/master/doc>
  - <https://github.com/michaeljclark/rv8/tree/master/doc/pdf>
  - <https://github.com/michaeljclark/rv8/blob/master/LICENSE>
  - <https://raw.githubusercontent.com/carrv/carrv.github.io/master/2017/papers/clark-rv8-carrv2017.pdf>
  - <https://github.com/michaeljclark/rv8-bench>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/README.md>
  - <https://github.com/michaeljclark/rv8-bench/tree/master/data>
  - <https://github.com/michaeljclark/rv8-bench/tree/master/plots>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/data/tables.txt>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/data/template.md>
- **Sources the enricher read:**
  - <https://github.com/michaeljclark/rv8>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/README.md>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/Makefile>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/.gitmodules>
  - <https://github.com/michaeljclark/rv8/tree/master/src>
  - <https://github.com/michaeljclark/rv8/tree/master/src/emu>
  - <https://github.com/michaeljclark/rv8/tree/master/src/jit>
  - <https://github.com/michaeljclark/rv8/tree/master/src/abi>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/src/jit/jit-runloop.h>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/src/jit/jit-emitter-rv64.h>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/src/jit/jit-tracer.h>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/src/jit/jit-fusion.h>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/src/jit/jit-regalloc.h>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/src/app/rv-jit.cc>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/src/util/host.h>
  - <https://raw.githubusercontent.com/michaeljclark/rv8/HEAD/src/emu/processor-proxy.h>
  - <https://github.com/michaeljclark/rv8/issues?q=is%3Aissue>
  - <https://github.com/michaeljclark/rv8/issues?q=is%3Aissue+jit>
  - <https://github.com/michaeljclark/rv8/issues/48>
  - <https://github.com/michaeljclark/rv8/issues/61>
  - <https://github.com/michaeljclark/rv8/issues/68>
  - <https://raw.githubusercontent.com/carrv/carrv.github.io/master/2017/papers/clark-rv8-carrv2017.pdf>
  - <https://github.com/michaeljclark/rv8-bench>
  - <https://github.com/michaeljclark/rv8-bench/tree/master/src>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/rv8-bench.js>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/package.json>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/data/template.md>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/data/tables.txt>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/src/aes.c>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/src/primes.c>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/src/qsort.c>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/src/sha512.c>
  - <https://raw.githubusercontent.com/michaeljclark/rv8-bench/HEAD/src/norx.c>
  - <https://github.com/OpenISA/riscv-sbt>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/README.md>
  - <https://github.com/OpenISA/riscv-sbt/tree/master/scripts>
  - WebSearch: rv8 RISC-V binary translator benchmark compared QEMU independent evaluation (snippets only; researchgate figure caption for 'Towards a High-Performance RISC-V Emulator', page not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/michaeljclark/rv8`) · [data/wave12/enrich/raw/github_com_michaeljclark_rv8.json](../../../data/wave12/enrich/raw/github_com_michaeljclark_rv8.json) (enrichment confidence 0.75)

</details>
