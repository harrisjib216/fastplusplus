# E9Patch

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-3.0-only` · 🟢 active

> Static x86_64 ELF binary rewriter that skips control-flow recovery; more robust and scalable than Dyninst-style rewriters, but not faster.

| | |
|---|---|
| **Beats** | Dyninst |
| **Claimed result** | No speedup over Dyninst. PLDI 2020 paper, SPEC2006: E9Patch adds +110.81% runtime overhead for patching all jump instructions (A1) and +64.71% for heap writes (A2); the paper cites about 70% for Dyninst basic-block counting, +62% for PEBIL and +60.48% for Multiverse (cited from those tools' papers, not measured side by side) and says those inlining rewriters generally give better performance. Chrome +113%, Firefox +46% on Dromaeo. README: the current -O2 mode is sometimes 2x faster than the PLDI prototype (self-comparison). |
| **Workload** | Static x86_64 binary rewriting for instrumentation; basic-block counting overhead on SPEC-style benchmarks and rewrite time on large binaries (Chrome, Firefox). |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Silver 4114 2.20GHz, 32GB RAM (PLDI 2020 paper) |
| **Compiler and flags** | SPEC2006 built with Ubuntu 16.04 default gcc/g++/gfortran, non-PIE; flags not stated |
| **Adoption** | 1.2k stars; PLDI 2020 |
| **Last commit** | 2026-06-28 |
| **Links** | [repository](https://github.com/GJDuck/e9patch) · [benchmark](https://raw.githubusercontent.com/gaoxiang9430/gaoxiang9430.github.io/HEAD/papers/PLDI20.pdf) |

## Verdict

The PLDI 2020 paper ran the prototype on SPEC2006 (non-PIE, Ubuntu 16.04 default gcc/g++/gfortran) on a Xeon Silver 4114 2.20 GHz: empty instrumentation of all jumps cost +110.81% runtime and of all heap writes +64.71%, with about 113% on Chrome and 46% on Firefox (Dromaeo DOM). The Dyninst (\~70%), PEBIL (+62%) and Multiverse (+60.48%) figures are quoted from those tools' papers, not measured side by side, and the paper itself says inlining rewriters generally perform better; the README says today's -O2 output is sometimes 2x faster than the prototype, which is unmeasured here.

## Use it when

- Instrumenting or patching x86_64 Linux binaries you cannot recompile, especially very large ones (browsers, big shared libraries) where CFG-based rewriters fail or are too slow
- Robustness matters more than overhead: binary hot-patching, hardening (e.g. low-fat pointer heap-write checks) or fuzzing instrumentation on stripped or mixed-language (C, C++, Fortran, assembly) code
- Sparse instrumentation (a few call sites, malloc calls, specific instructions), where the extra two jumps per patch site matter little
- Building your own tool on a programmable backend (E9Tool matching language, call trampolines, plugins) under GPL-3.0

## Skip it when

- When runtime overhead is the priority: the paper's empty instrumentation costs +110.81% on all jumps and +64.71% on heap writes on SPEC2006, versus cited figures of about 70% for Dyninst, +62% for PEBIL and +60.48% for Multiverse (inlining rewriters)
- Non-x86_64 or non-ELF targets: 32-bit support is an open feature request (#16)
- Binaries that mix code and data in .text or need full coverage of single-byte instructions (ret, push, pop): the linear disassembler and the tactics have documented limits; -100 mode falls back to SIGILL handlers and breaks programs that install their own SIGILL handler
- Binaries with very large static .bss on non-PIE builds (gamess, zeusmp in the paper) that exhaust address space for trampolines
- CET shadow-stack environments: compatibility is an open issue (#55)

## How it is fast

It does not relocate code or recover control flow: each patched instruction is replaced in place by a jump to a trampoline, using instruction punning plus three tactics from the PLDI 2020 paper (T1 padded jumps, T2 successor eviction, T3 neighbour eviction) to find valid rel32 offsets, so jump targets are preserved and rewriting is safe without a CFG. Physical page grouping packs scattered trampolines into shared file-backed pages to limit RAM and file-size bloat. The speed story is rewrite scalability (Chrome and libxul.so over 100 MB rewritten) rather than lower runtime overhead; the current E9Tool adds -O1/-O2/-O3 optimizations and an optional -CFR mode that uses heuristic control-flow recovery for faster output binaries.

## Compared with alternatives

Pick it over RetroWrite when the binary is non-PIE, C++ or Fortran, or too large for symbolization-based reassembly, accepting higher overhead; pick bpftime or funtrace instead when you only need probes or function tracing and low per-event cost matters.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | zlib (build.sh also checks for xxd and markdown); prebuilt release binaries available |
| **Minimum toolchain** | gcc/g++ and make (C++); not otherwise documented |
| **Platforms** | x86_64 Linux ELF (PIE and non-PIE executables and shared objects) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — a command-line static rewriter like Dyninst's binary-rewriting mode, but a different API (E9Tool match/patch language and patch binaries, not Dyninst's BPatch C++ API) and no basic-block or CFG information in the default mode |

## Gotchas

- The clean call ABI does not save x87/MMX/SSE/AVX registers and does not guarantee 16-byte stack alignment; patch code built outside e9compile.sh that touches SIMD or calls libc can corrupt state or crash.
- Coverage is not guaranteed in the default mode: some instructions may silently stay unpatched (1098 of about 1.05e7 failed in the paper), so counts-based tools can under-report.
- File size grows with trampolines (+57.43% for all-jumps instrumentation in the paper with page grouping; +2239.83% without it); higher -c compression levels trade file size for thousands of mmap calls at load.
- -CFR mode is faster but heuristic and may introduce rewriting errors; the default mode is the one the authors call official for benchmarking.

## Known shortcomings

- Not faster than the incumbent rewriters: the PLDI 2020 paper reports +110.81% (A1) and +64.71% (A2) overhead on SPEC2006 (Xeon Silver 4114), while the Dyninst, PEBIL and Multiverse figures it cites come from their own papers and were not run side by side. The paper says inlining rewriters are faster; E9Patch trades speed for robustness.
- Clean ABI skips SSE/AVX save and 16-byte alignment; coverage is not guaranteed in default mode; -100 mode breaks programs' own SIGILL handlers; CET is an open issue (55); no 32-bit support (16). Chrome overhead about 113%, Firefox about 46%.

## Caveats and trade-offs

Not faster than the baseline: by its own paper E9Patch has higher overhead than Dyninst, PEBIL and Multiverse, trading speed for not needing control-flow recovery and for scaling to Chrome/Firefox. The baseline numbers are cited from other papers, not run side by side. Dyninst is not in this category's baseline list. The README says the current version with -O2 is sometimes 2x faster than the evaluated prototype, so the paper numbers may overstate today's overhead. GPL-3.0 with some files MIT.

x86_64 Linux ELF only; GPL-3.0; tool-building framework rather than a ready profiler; binaries grow with trampolines.

## Maintenance

Actively maintained (last commit 2026-06-28, 1.2k stars, 4 open issues) and used by several research tools; GPL-3.0 with some MIT files, so linking it into a closed tool needs care, but patched output binaries are standalone.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): reject; tier before verification B, tier now B.
- **Tier reason:** PLDI 2020 paper (read via the author's gaoxiang9430.github.io repo PDF, Section 6.1) measures E9Patch on SPEC2006 on a Xeon Silver 4114 with the default system gcc/g++/gfortran: +110.81% overhead for jump-instruction patching (A1) and +64.71% for heap-write patching (A2). It then cites, from the other tools' own papers, about 70% for Dyninst basic-block counting, +62% for PEBIL and +60.48% for Multiverse, and says those inlining rewriters generally perform better; E9Patch's argument is robustness and scalability, not speed.
- **Verifier notes:** Paper reached through raw.githubusercontent.com/gaoxiang9430/gaoxiang9430.github.io (papers/PLDI20.pdf). Rejected as not-faster under the verifier rules; if the keep-and-document rule applies, keep it flagged as slower than Dyninst. Metadata checked: 1.2k stars, GPL-3.0, last commit 2026-06-28.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** peer-reviewed paper, read from a repo copy
- **Pages the verifier opened:**
  - <https://github.com/GJDuck/e9patch>
  - <https://github.com/GJDuck/e9patch/commits>
  - <https://raw.githubusercontent.com/GJDuck/e9patch/HEAD/README.md>
  - <https://raw.githubusercontent.com/gaoxiang9430/gaoxiang9430.github.io/HEAD/papers/PLDI20.pdf>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/GJDuck/e9patch/HEAD/README.md>
  - <https://raw.githubusercontent.com/GJDuck/e9patch/HEAD/doc/e9tool-user-guide.md>
  - <https://raw.githubusercontent.com/GJDuck/e9patch/HEAD/build.sh>
  - <https://github.com/GJDuck/e9patch/issues>
  - <https://raw.githubusercontent.com/gaoxiang9430/gaoxiang9430.github.io/HEAD/papers/PLDI20.pdf>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/gjduck/e9patch`) · [data/wave11/enrich/raw/github_com_gjduck_e9patch.json](../../../data/wave11/enrich/raw/github_com_gjduck_e9patch.json) (enrichment confidence 0.75)

</details>
