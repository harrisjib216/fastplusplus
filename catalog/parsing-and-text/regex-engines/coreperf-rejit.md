# rejit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🔴 abandoned

> Prototype non-backtracking JIT regex compiler for x86-64 that beats RE2 and grep on throughput, unmaintained since 2015.

| | |
|---|---|
| **Beats** | RE2 |
| **Claimed result** | Benchmarks Game regex-dna, real time, Benchmarks Game RE2 program vs multi-threaded Rejit: 500KB 0.022s vs 0.011s (2.0x, derived from page data); 5MB 0.183s vs 0.087s (\~2.1x, derived from page data); 50MB 1.629s vs 0.971s (\~1.68x, derived from page data); 500MB 20.693s vs 11.594s (\~1.78x, derived from page data). README: jrep (Rejit-powered grep) 'performs 1.68 times faster than gnu grep' on grep -R over linux-3.10.6 (0.622s vs 0.370s real). Single-threaded Rejit vs V8: 50MB 2.054s vs 1.246s (\~1.65x, derived from page data). |
| **Workload** | DNA-matching benchmark from the Computer Language Benchmarks Game (regex-dna) at input sizes from 500KB to 500MB, multi-threaded Rejit vs RE2; also a recursive `grep -R` over the Linux 3.10.6 kernel source tree vs GNU grep 2.14 |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-2400 @ 3.10GHz (quad-core), 4GiB RAM, Fedora 17 (kernel 3.8.13-100.fc17.x86_64), SSE4.2 |
| **Compiler and flags** | Not stated in README; repo SConstruct release mode adds -O3 (compiler and version unstated) |
| **Adoption** | 197 stars |
| **Last commit** | 2015-04-02 |
| **Links** | [repository](https://github.com/coreperf/rejit) · [benchmark](https://github.com/coreperf/rejit) |

## Verdict

First-party README benchmarks on an Intel Core i5-2400 (quad-core, SSE4.2, Fedora 17, RE2 commit aa957b5e3374 from \~2013): multi-threaded Rejit vs. the Benchmarks Game RE2 regex-dna program is 1.68x-2.1x faster in real time across 500KB-500MB inputs, and Rejit-powered jrep is 1.68x faster than GNU grep 2.14 on `grep -R` over the Linux 3.10.6 source tree (0.370s vs 0.622s real); the compiler and optimization flags actually used for these runs are not stated.

## Use it when

- Bulk, offline x86_64 Linux/macOS text-scanning jobs where you can vendor a small unmaintained C++11 GPLv3 static lib for extra single-machine regex throughput on large inputs (tens of MB+)
- Simple find/match/replace patterns that don't need capture groups, back-references, word boundaries, Unicode/UTF-8, or POSIX BRE syntax
- You already split work across threads yourself (as jrep and the DNA benchmark samples do) and want a non-backtracking engine per thread
- Studying or extending a small, readable non-backtracking SIMD regex JIT implementation
- GPL-3.0 licensing is acceptable in your project

## Skip it when

- You need capture/submatch extraction: issue #6 'Support submatches extraction' has been open since 2014 and unresolved; Match only exposes begin/end of the whole match
- You need word boundaries (\b), back-references, Unicode/UTF-8 encoding, or POSIX BRE syntax: all are open, unimplemented feature requests (issues #1, #3, #5, #7)
- Non-x86_64 targets: issue #10 'Support other architectures' is open and unaddressed; SConstruct only builds arch:x64
- Production or long-lived use: no commits since April 2015, and the SConstruct build script itself prints a warning that 'top-of-tree is not maintained any more, and contains some bugs. In particular, some regular expressions are incorrectly evaluated,' pointing to an apparently-unfinished successor (arames/regit)
- You need permissive licensing or static linking into a non-GPL product: license is GPL-3.0

## How it is fast

Each regex is JIT-compiled at runtime into native x86-64 machine code using a V8-derived assembler/codegen (src/x64/assembler-x64.\*), avoiding backtracking entirely. Matching uses SIMD to test up to 4 characters per instruction (kMaxParallelChars=4 in src/cpu.h, requires SSE4.2, disable with simd:off) and a 'fast forward' skip-ahead mechanism that jumps past non-matching regions instead of scanning byte by byte. The multi-threaded benchmark samples (jrep -R, regexdna-multithread.cc) add throughput by splitting input across threads manually.

## Compared with alternatives

Pick rejit over BLARE or re2jit only if you want a from-scratch, dependency-free non-backtracking JIT engine to study or extend and don't need RE2-compatible behavior; BLARE reports broader RE2/PCRE2/Boost comparisons and re2jit stays API-compatible with RE2 (it falls back to RE2 for cases it doesn't optimize), while rejit offers neither RE2 API compatibility nor capture groups.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the core library at build time (SCons is the build tool, not a runtime dependency); the benchmark harness separately depends on RE2, V8, and PCRE for comparison only |
| **Minimum toolchain** | C++11 (SConstruct sets CXXFLAGS -std=c++11); specific compiler/version not stated; built with SCons |
| **Platforms** | x86_64 only, SIMD path assumes SSE4.2 (kMaxParallelChars=4 in src/cpu.h); SConstruct has Linux and macOS build configs; other architectures are an open, unimplemented issue (#10) |
| **Thread safety** | not documented for the Regej class; the multi-threaded sample programs (jrep, regexdna-multithread.cc) achieve concurrency by giving each thread its own Regej instance and text range |
| **Drop-in for the baseline** | partial — explain: C++-only API (no C bindings; issue #11 'C support' is open), and there is no RE2-style capture-group API, so call sites need to be rewritten, not just relinked |

## Gotchas

- The project's own SConstruct prints a build-time warning: 'top-of-tree is not maintained any more, and contains some bugs. In particular, some regular expressions are incorrectly evaluated.'
- No capture-group/submatch API — Match exposes only begin/end of the whole match (issue #6 open since 2014)
- x86_64-only; the SIMD fast path assumes SSE4.2 and can be turned off at build time with simd:off
- The public header include/rejit.h has `using namespace std;` at file scope, which can leak std:: names into including translation units

## Caveats and trade-offs

GitHub's license detector reports NOASSERTION, but the LICENCE file contains the full GNU GPL v3 text and the README says GPLv3. The RE2 comparison pits multi-threaded Rejit against the Benchmarks Game RE2 program; the README calls that program single-threaded yet links a u32q quad-core page, so thread-count parity is unclear. Compiler and flags are unstated. No commits since 2015; the benchmark numbers date from about 2013 (RE2 commit aa957b5e3374, Linux 3.10.6), and RE2 has been heavily optimized since. Rejit is described as a prototype and supports x86_64 only.

x86_64-only, requires SSE4.2; unmaintained prototype/proof-of-concept, not production-hardened; benchmark hardware (2011-era CPU) and RE2 build (\~2013 commit) are over a decade old so results may not reflect current RE2 performance

## Maintenance

Abandoned since its last commit in April 2015; GPL-3.0, C++11, and small enough (\~20 source files) to vendor as a source-drop, but the build script itself warns of known incorrect-match bugs and never reached a maintained successor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README gives first-party timings for multi-threaded Rejit (sample/regexdna-multithread.cc) against the Benchmarks Game RE2 regex-dna program, and for jrep against GNU grep 2.14. The CPU (i5-2400) and engine commits are stated, but the compiler and flags are not (the repo SConstruct release mode only implies -O3). The RE2 side's program is external, so this is not A. It is first-party, so C.
- **Verifier notes:** The record's '\~1.4x-1.8x across all sizes' was wrong: the README's own RE2 rows give 1.68x-2.1x. The tier drops from A to C because compiler and flags are missing and the benchmark is first-party. License GPL-3.0 is confirmed from the LICENCE file.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/coreperf/rejit>
  - <https://github.com/coreperf/rejit/blob/HEAD/README.md>
  - <https://github.com/coreperf/rejit/blob/HEAD/LICENCE>
  - <https://github.com/coreperf/rejit/blob/HEAD/SConstruct>
- **Sources the enricher read:**
  - <https://github.com/coreperf/rejit>
  - <https://github.com/coreperf/rejit/blob/HEAD/README.md>
  - <https://github.com/coreperf/rejit/blob/HEAD/include/rejit.h>
  - <https://github.com/coreperf/rejit/blob/HEAD/SConstruct>
  - <https://github.com/coreperf/rejit/blob/HEAD/src/cpu.h>
  - <https://github.com/coreperf/rejit/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/coreperf/rejit`) · [data/wave3/enrich/raw/github_com_coreperf_rejit.json](../../../data/wave3/enrich/raw/github_com_coreperf_rejit.json) (enrichment confidence 0.5)

</details>
