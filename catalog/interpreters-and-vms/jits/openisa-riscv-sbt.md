# riscv-sbt (OpenISA RISC-V static binary translator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Research static RV32-to-x86/ARM binary translator built on LLVM; translated MiBench runs near native, far ahead of QEMU and rv8.

| | |
|---|---|
| **Beats** | QEMU (user-mode RISC-V dynamic binary translation) and rv8 |
| **Claimed result** | Committed result CSVs (mibench/results): geomean slowdown versus native 32-bit x86 of 1.08x (abi mapping) and 1.23x (locals mapping) over 19 MiBench programs, counting only cycles spent in the benchmark's own code (x86-avx-gcchf.csv 'x' columns, derived from page data); with libc time included the SBT geomeans are 1.02x abi and 1.11x locals (x86-avx-gcchf-wlibc.csv, derived from page data). QEMU 6.13x total-time geomean over 19 programs (qemu_slowdown.csv geomean row) and rv8 2.85x over the 10 programs it could run (rv8_slowdown.csv geomean row; the other 9 rows are zero-filled placeholders). On the same 10 programs: SBT abi 1.10x, SBT locals 1.24x, QEMU 5.39x, rv8 2.85x (derived from page data). Per-benchmark example: rijndael-encode 14.54x under QEMU, 4.51x under rv8, 1.11x for the SBT (abi). The 2018 paper gives an SBT average of 1.12x versus 3.16x for RV8 (commit 1d4d1ee) and 7.07x for QEMU (v2.12.0-835-g360a7809d2-dirty) (search snippet of the ResearchGate figure caption only; paper not opened). |
| **Workload** | MiBench programs (dijkstra, crc32, rijndael encode/decode, sha, adpcm encode/decode, stringsearch, blowfish encode/decode, basicmath, bitcount, fft std/inv, patricia, susan smoothing/edges/corners, lame; 19 rows) built for RV32 and translated ahead of time to 32-bit x86 (AVX) with LLVM, run time measured with perf as slowdown versus the same program built natively for 32-bit x86; QEMU and rv8 run the RV32 binaries. |
| **Metric** | throughput |
| **Compiler and flags** | gcc -O3 -fno-exceptions for both RISC-V and native binaries (scripts/auto/config.py: GOPTS.cc and rvcc = gcc, _O = -O3); RISC-V binaries use -march=rv32g with the ilp32d hard-float ABI; native x86 binaries are 32-bit (i686-linux-gnu-gcc-7 when present, otherwise gcc -m32) with -mfpmath=sse -mavx; the SBT lowers translated code with LLVM llc -relocation-model=static -march=x86 -mattr=avx; static linking is forced only for rv8 and OVP runs (GOPTS.static), QEMU runs as qemu-riscv32 -L &lt;sysroot&gt;. gcc, LLVM, QEMU and rv8 versions are not stated in the repo (the paper snippet names RV8 commit 1d4d1ee and QEMU v2.12.0-835-g360a7809d2-dirty). |
| **Adoption** | 18 stars, 5 forks |
| **Last commit** | 2019-03-06 |
| **Links** | [repository](https://github.com/OpenISA/riscv-sbt) · [benchmark](https://github.com/OpenISA/riscv-sbt/tree/master/mibench/results) |

## Verdict

Committed MiBench result CSVs (19 programs, RV32G built with gcc -O3, translated ahead of time to 32-bit x86 AVX via LLVM; CPU not stated) show the SBT at 1.08x (abi) and 1.23x (locals) of native gcc -O3 i686 time counting only the program's own code, or 1.02x and 1.11x with libc time included, while qemu-riscv32 user mode is 6.13x and rv8 2.85x on the 10 programs it could run (total time, emulating RISC-V libc).

## Use it when

- Research on RISC-V emulation quality: it gives an upper bound for what a translator can reach (committed CSVs: 1.02-1.08x native on x86 with 'abi' mapping, 1.16x on ARM) to compare a DBT design against.
- Running RV32 programs you build yourself (gcc -O3 objects, single-threaded, ABI-conformant C) on a 32-bit x86 or ARM Linux host when you can rebuild them through its toolchain.
- Teaching or prototyping LLVM-based binary lifting: the translator is compact C++ (sbt/\*.cpp) with debug options such as -commented-asm and -a2s for source-annotated output.

## Skip it when

- Running arbitrary or stripped RISC-V executables, RV64 code, self-modifying or JIT-generating code, or dynamically loaded libraries: it needs relocatable RV32 objects and translates statically; use QEMU, rv8, rv32emu or libriscv instead.
- Programs calling libc functions outside the whitelist in sbt/libc.c, external functions with more than 8 parameters (rejected by the translator), or indirect calls to code the dispatcher does not know (aborts with 'FATAL ERROR: at icaller: function not found').
- Code that needs exact RISC-V floating-point state: FCSR emulation and fcvt input validation are off by default (-enable-fcsr, -enable-fcvt-validation), and 'abi' mode assumes every function obeys the calling convention.
- Anything needing maintenance or a current toolchain: last commit 2019-03-06, built from pinned OpenISA forks of LLVM and clang and a gcc 7.3.0 RISC-V toolchain branch, no issues or releases.
- Deep recursion or large stack frames without tuning: the guest stack is a fixed buffer (-stack-size, default 4096 bytes; the MiBench builds pass 16 KB, 128 KB or 1 MB per program).

## How it is fast

Ahead-of-time whole-program translation removes the run-time costs a dynamic translator pays (decode, translation, code-cache lookup, dispatch), and LLVM's -O3 pipeline re-optimizes the lifted code. The register mapping mode matters most: 'globals' keeps guest registers in global variables (2-15x slower than native on several programs), 'locals' gives each function a local register file that LLVM can promote to host registers and syncs it at calls, and 'abi' syncs only the registers the RISC-V calling convention makes live across calls and returns, which yields the best numbers. libc and libm calls run as native host code.

## Compared with alternatives

Pick it over rv8, rv32emu or libriscv only when you can rebuild the RV32 program and want near-native speed as a research reference; those dynamic translators and interpreters run unmodified binaries, are maintained (rv32emu, libriscv), and handle code this SBT cannot. Instrew is the closer LLVM-based design if you need dynamic translation of real executables.

## Integration

| | |
|---|---|
| **Form** | translator CLI (riscv-sbt) plus Python Makefile generator; build from source or Docker image |
| **Dependencies** | OpenISA forks of LLVM and clang (submodules pinned in docker/commits.txt), OpenISA riscv-gnu-toolchain (gcc-7.3.0 branch), riscv-isa-sim/fesvr/pk, i686 gcc for native comparisons, perf for measurement |
| **Minimum toolchain** | not documented beyond the pinned submodule commits; the Dockerfiles in docker/ are the stated reference |
| **Platforms** | input RV32G objects (ilp32d hard-float or ilp32 soft-float ABI); output 32-bit x86 Linux (i686, AVX by default, MMX option) or ARM Linux (Thumb) |
| **Thread safety** | not documented; translated programs use a single fixed-size guest stack and all measured workloads are single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- Like-for-like flaw in the QEMU/rv8 comparison: the SBT binds libc/libm calls to native host libc (sbt/libc.c, Caller::callExternal), while QEMU and rv8 emulate the RISC-V libc too. On the 5 programs where native code spends under 10% of cycles in its own code (stringsearch, basicmath, fft-std, fft-inv, patricia), the SBT's total-time slowdown is 1.03x against QEMU's 9.76x; on the other 14 the gap is still large (SBT abi 1.01x, QEMU 5.19x), so the win holds but is inflated for libc-heavy rows (derived from page data).
- The headline 'x' columns (x86-avx-gcchf.csv) multiply wall time by perf's share of cycles in the benchmark's own DSO, so for basicmath (2.77% own code natively) the ratio rests on a few milliseconds of samples; runs are short (0.05-2.4 s, n=10 default) and several translated rows beat native (adpcm-encode 0.70x, bitcount abi 0.77x, dijkstra 0.87x), which reflects gcc -O3 native versus LLVM -O3 re-optimization rather than translation alone.
- Paper and repo numbers disagree: the SSCAD 2018 abstract (search snippet only; sol.sbc.org.br is blocked here) reports 12% overhead on x86 and 35% on ARM, while the committed CSVs give 1.08x (abi) and 1.23x (locals) on x86 and 1.16x (abi) and 1.34x (locals) on ARM (derived from page data); no CPU model is stated anywhere reachable.
- rv8 and OVP rows cover only 10 of 19 programs (notes/rv8: crashes, wrong results, build failures) and the other 9 are zero-filled placeholders, so their geomean rows (rv8 2.85x, OVP 4.92x) are over a different program set than QEMU's 6.13x.

## Known shortcomings

- CPU model not stated anywhere reachable; the paper numbers (1.12x vs rv8 3.16x and QEMU 7.07x) were seen only in a search snippet. The SBT CSVs count only time in the benchmark's own code with libc excluded while the QEMU and rv8 CSVs use total time; with libc included SBT is still 1.02x (abi) and 1.11x (locals) (derived from page data); rv8 ran 10 of 19 programs; ahead-of-time vs runtime translators is not like for like. Abandoned 2019; the repo now redirects to lmcad-unicamp/riscv-sbt.
- Enricher: the SBT binds libc and libm calls to the native host libc (sbt/libc.c, Caller::callExternal) while QEMU and rv8 emulate the RISC-V libc, so on the 5 libc-dominated rows SBT is 1.03x vs QEMU 9.76x and on the other 14 rows SBT abi 1.01x vs QEMU 5.19x (derived from page data); the win holds but the gap is inflated on libc-heavy rows, and some translated rows beat native because gcc and LLVM -O3 differ. The paper abstract (snippet, sol.sbc.org.br blocked) says 12% x86 and 35% ARM while the CSVs say 1.08x/1.23x x86 and 1.16x/1.34x ARM. Input must be relocatable RV32 objects, 4096-byte default stack, FCSR emulation off.

## Caveats and trade-offs

CPU model is not stated in anything reachable (the paper is blocked in this environment), so tier A is unmet; the paper numbers (1.12x, 3.16x, 7.07x) come only from a search snippet and differ from the committed CSVs. Metric mismatch in the committed CSVs: scripts/auto/measure.py multiplies run time by the fraction of perf cycles in the benchmark's own DSO for the SBT runs (x86-avx-gcchf.csv, so libc time is excluded), while --rv32 emulator runs disable perf_libc and use total time (qemu.csv and rv8.csv show 100% for every row); the like-for-like total-time file x86-avx-gcchf-wlibc.csv gives 1.02x abi and 1.11x locals, so the win holds either way. The rv8 column covers only 10 of 19 programs (notes/rv8: basicmath crash, bitcount wrong result, fft never ends, patricia does not build, susan and lame fail) and its geomean row is over those 10; QEMU's 6.13x is over all 19 (5.39x on the same 10, derived). rv8 and QEMU are dynamic translators that pay translation cost at run time, while the SBT output is native x86 produced ahead of time, so the comparison is not like for like. github.com/OpenISA/riscv-sbt now redirects to github.com/lmcad-unicamp/riscv-sbt (current owner; same 18 stars and 5 forks). The OpenISA-input SBT results (x86-oi_slowdown.csv) are a separate translator and not this claim. Last commit 2019-03-06.

Static (ahead-of-time) translator: no self-modifying code, JIT-generated code or dynamic loading of untranslated binaries; translates RV32 ELF to x86 and ARM through LLVM IR; needs a custom RISC-V toolchain and the MiBench programs rebuilt, so it is a research prototype rather than a drop-in emulator. ecall translation is limited.

## Maintenance

Abandoned since 2019-03-06 (repo now redirects to lmcad-unicamp/riscv-sbt, no issues filed), MIT-licensed and copyable, but a research prototype tied to 2018-era forked LLVM, clang and gcc 7.3.0 toolchains; expect to rebuild through its Docker setup.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed paper (Lupori et al., 'Towards a High-Performance RISC-V Emulator', 2018, IEEE Xplore 8748908) reports the SBT at 1.12x slowdown versus RV8 3.16x and QEMU 7.07x (figure caption seen only as a search snippet), and the repo carries the harness (mibench/genmake.py, scripts/auto/measure.py, scripts/auto/config.py) plus committed result CSVs that show the same ordering; no CPU model is stated anywhere reachable, so not A.
- **Verifier notes:** Committed CSV geomeans re-derived and match the record (abi 1.075, locals 1.233 over 19 programs). Shortcomings to record: no CPU model; paper reached only via snippet; SBT CSV excludes libc time while the QEMU/rv8 CSVs use total time (with-libc SBT file still shows 1.02x/1.11x); rv8 measured on 10 of 19 programs; static versus dynamic translation is not like for like; abandoned since 2019. The repo URL now redirects to lmcad-unicamp/riscv-sbt; consider a repo_url override.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** paper access and total-time comparison; emulated-libc comparison
- **Pages the verifier opened:**
  - <https://github.com/OpenISA/riscv-sbt>
  - <https://github.com/OpenISA/riscv-sbt/commits>
  - <https://github.com/OpenISA/riscv-sbt/tree/master/mibench/results>
  - <https://github.com/lmcad-unicamp/riscv-sbt>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/README.md>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/mibench/results/qemu_slowdown.csv>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/mibench/results/rv8_slowdown.csv>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/mibench/results/x86-avx-gcchf.csv>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/mibench/results/x86-avx-gcchf-wlibc.csv>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/mibench/results/qemu.csv>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/mibench/results/rv8.csv>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/mibench/results/plot.sh>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/scripts/auto/config.py>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/scripts/auto/measure.py>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/notes/rv8>
- **Sources the enricher read:**
  - <https://github.com/lmcad-unicamp/riscv-sbt>
  - <https://github.com/lmcad-unicamp/riscv-sbt/commits/master>
  - <https://github.com/lmcad-unicamp/riscv-sbt/issues?q=is%3Aissue>
  - <https://github.com/lmcad-unicamp/riscv-sbt/tree/master/sbt>
  - <https://github.com/lmcad-unicamp/riscv-sbt/tree/master/mibench/results>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/README.md>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/scripts/auto/measure.py>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/scripts/auto/config.py>
  - <https://raw.githubusercontent.com/OpenISA/riscv-sbt/HEAD/notes/rv8>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/sbt/sbt.cpp>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/sbt/Caller.cpp>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/sbt/Options.cpp>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/sbt/Options.h>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/sbt/Translator.cpp>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/sbt/libc.c>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/sbt/Function.cpp>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/sbt/Syscall.cpp>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/sbt/Object.cpp>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/mibench/genmake.py>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/mibench/results/x86-avx-gcchf.csv>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/mibench/results/x86-avx-gcchf-wlibc.csv>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/mibench/results/qemu_slowdown.csv>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/mibench/results/rv8_slowdown.csv>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/mibench/results/ovp_slowdown.csv>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/mibench/results/arm.csv>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/docker/commits.txt>
  - <https://raw.githubusercontent.com/lmcad-unicamp/riscv-sbt/HEAD/.gitmodules>
  - <https://github.com/orgs/lmcad-unicamp/repositories>
  - https://sol.sbc.org.br/index.php/sscad/article/view/15664 (EGRESS_BLOCKED; abstract from search snippet)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/openisa/riscv-sbt`) · [data/wave12/enrich/raw/github_com_openisa_riscv_sbt.json](../../../data/wave12/enrich/raw/github_com_openisa_riscv_sbt.json) (enrichment confidence 0.75)

</details>
