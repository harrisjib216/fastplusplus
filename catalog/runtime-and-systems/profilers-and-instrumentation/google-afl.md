# AFL (american fuzzy lop)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> Original coverage-guided fuzzer: edge-coverage feedback plus a fork server; far more code reached than blind mutation fuzzing.

| | |
|---|---|
| **Beats** | blind fuzzing (random mutation without coverage guidance) |
| **Claimed result** | Coverage, not speed: AFL model reached 1,765 blocks and 2,597 edges versus 182 blocks / 205 edges (blind fuzzing S, single round), 228 / 265 (blind fuzzing L, comparable number of cycles), 855 / 1,130 (block-coverage guidance) and 1,452 / 2,070 (edge-coverage guidance), from an initial file at 156 / 163. Deterministic-only experiment seeded with a valid unified diff (initial 624 / 717): AFL model 1,452 blocks / 2,040 edges and 1 unique crash versus blind fuzzing 1,101 / 1,409, block coverage 1,255 / 1,649 and edge coverage 1,259 / 1,734, all with 0 crashes. Separate speed claims in the same docs: LLVM-mode instrumentation lets some slow CPU-bound programs run up to around 2x faster and stays within about 10% for fast binaries (versus afl-gcc/afl-clang assembly-level rewriting); the fork server usually gives 1.5x-2x on fast targets; deferred fork server 10x+ on some targets. The README calls the fuzzer far superior to blind fuzzing or coverage-only tools. |
| **Workload** | Coverage reached on GNU patch 2.7.3 compiled with -O3, seeded with a dummy text file, one pass over the afl-fuzz input queue, AFL's coverage-guided model against blind fuzzing and against block-only and edge-only guidance; a second experiment with only deterministic stages seeded with a valid unified diff. |
| **Metric** | other |
| **Compiler and flags** | Target GNU patch 2.7.3 compiled with -O3; instrumenting compiler and afl-fuzz build flags not stated |
| **Adoption** | 4.2k stars, 672 forks; repository archived by the owner on 2024-03-22 |
| **Last commit** | 2021-06-08 |
| **Links** | [repository](https://github.com/google/AFL) · [benchmark](https://github.com/google/AFL/blob/master/docs/technical_details.txt) |

## Verdict

AFL's own technical notes report a single pass over the queue on GNU patch 2.7.3 (-O3, dummy text seed): the AFL model reached 1,765 blocks and 2,597 edges against 182/205 (blind, one round), 228/265 (blind, comparable cycles), 855/1,130 (block-coverage guidance) and 1,452/2,070 (edge-coverage guidance), and with deterministic stages only from a valid diff 1,452/2,040 and 1 crash against 1,101/1,409 blind with no crashes. CPU, compiler for the instrumented build, run count and the blind and block-guided harness variants are not published.

## Use it when

- Fuzzing C or C++ file-format parsers, decoders and libraries whose source you can rebuild with afl-gcc or afl-clang-fast, ideally with a small harness that reads one file from stdin or @@.
- Pairing with AddressSanitizer (AFL_USE_ASAN) or AFL_HARDEN and libdislocator to turn silent memory corruption into crashes the fuzzer can see, within the memory-limit constraints in notes_for_asan.txt.
- Black-box Linux binaries with no source via QEMU mode, accepting the documented 2-5x slowdown against compile-time instrumentation.
- Building a small, self-contained corpus of 'does something new' inputs to seed slower test regimes (browsers, office suites, closed-source tools), as the README suggests.
- Learning how coverage-guided fuzzing works: docs/technical_details.txt explains every design choice in plain text.

## Skip it when

- New fuzzing campaigns: the repository was archived on 2024-03-22 and the last release is 2.57b (2020-06-30); AFL++ (release 5.03c) is the maintained fork and calls itself faster with more and better mutations, but its default licence is now AGPL-3.0-or-later (harness-compiled parts stay Apache-2.0).
- Recent clang/LLVM: llvm_mode is reported broken with LLVM/Clang 13 (open issues #151 and #156), and persistent and deferred modes only work with afl-clang-fast.
- Fast, stateless library APIs where exec rate is everything: llvm_mode/README.llvm itself says persistent mode is not as fast as in-process fuzzing such as LLVM's libFuzzer.
- Network services, daemons, interactive programs, or formats wrapped in checksums, signatures, encryption or compression: no direct support, and coverage stays shallow unless you patch the checks out.
- Very large targets: the fixed 64 kB map collides on about 7% of tuples at 10,000 branches, 14% at 20,000 (sqlite) and 30% at 50,000.

## How it is fast

Compile-time instrumentation adds shared_mem[cur ^ prev]++ at every branch, with random block ids, into a 64 kB shared-memory bitmap that fits in L2 and is compared with the global map in a few word-wide operations; hit counts are bucketed (1, 2, 3, 4-7, ... 128+) so loop-count changes register as new behaviour. A fork server stops the target at its first instrumented function and clones it with copy-on-write fork() instead of execve() per input (docs: usually 1.5-2x on fast targets); deferred __AFL_INIT() skips user initialisation (10x+ on some targets) and persistent __AFL_LOOP() reuses one process for many inputs (5x or more). Search effort is kept cheap with test-case trimming, periodic corpus culling that favours small, fast entries, and aggressive timeouts (5x the calibrated run time, rounded up to 20 ms).

## Compared with alternatives

None of the catalogued siblings is a fuzzer; AFL is the coverage engine they serve. RetroWrite and E9Patch are static binary rewriters that can add AFL-style coverage to binary-only targets, and are worth trying before AFL's QEMU mode with its 2-5x cost; AddressSanitizer is the usual bug detector to compile into an AFL target.

## Integration

| | |
|---|---|
| **Form** | built tool (make): afl-fuzz plus compiler wrappers and a runtime object linked into the instrumented target |
| **Dependencies** | none for the core (GNU make and a C compiler); llvm_mode needs clang with llvm-config and LLVM development headers; qemu_mode builds a patched QEMU |
| **Minimum toolchain** | GCC or clang for afl-gcc/afl-clang; llvm_mode reported failing with LLVM/Clang 13 (#151, #156); built with -O3 -funroll-loops by default |
| **Platforms** | Linux x86 (primary); OpenBSD, FreeBSD and NetBSD on x86 with gmake; macOS on x86 with caveats (slower fork(), crash reporter must be disabled); Solaris reportedly; non-x86 via AFL_NO_X86=1 with llvm_mode or QEMU; QEMU mode Linux only; Android support added in 2.57b |
| **Thread safety** | afl-fuzz runs one target process at a time per instance; scale with parallel -M/-S instances that sync queues. In targets, afl-gcc/afl-clang keep the previous-location state in a global and afl-clang-fast in a thread-local variable; bitmap counter updates are not atomic, so multi-threaded targets give noisier coverage. |
| **Drop-in for the baseline** | partial — replaces a blind mutation fuzzer for any target that reads a file or stdin, but the target must be rebuilt with AFL's compiler wrappers (or run under the slower QEMU mode), and persistent or deferred speed-ups need source changes |

## Gotchas

- Evidence check: the coverage tables come from one afl-fuzz session on GNU patch 2.7.3, with no CPU, run count or variance, and the docs do not say how blocks and edges were counted; 'Blind fuzzing L' was given a comparable number of execution cycles, while the guided runs needed more time, so the strategies were not compared at equal wall time. All baselines are AFL itself with guidance removed. The speed ratios (fork server 1.5-2x, persistent 5x or more and 5-10x in perf_tips.txt, deferred 10x+, llvm_mode up to 2x) are prose against AFL's own slower modes, not measurements against another fuzzer.
- 64-bit ASAN builds reserve huge virtual memory and clash with the default 50 MB child memory limit (-m); notes_for_asan.txt recommends 32-bit builds, cgroups limits or careful measurement, and ASAN cannot be combined with -static.
- Persistent and deferred modes must fully reset target state and must start before threads, timers, sockets or any access to the input; otherwise you get false positives or wasted cycles. Targets that install their own SIGSEGV/SIGABRT handlers hide crashes from afl-fuzz.
- AFL produces no human-readable coverage report (the README points to afl-cov), and edge hit counters can wrap to zero because the instrumentation has no saturating add.

## Known shortcomings

- Numbers are coverage (blocks, edges), not speed, apart from README.llvm prose (2x, 10%, fork server 1.5x-2x, deferred 10x+); baselines are AFL's own variants; no CPU, single session. Archived 2024-03-22, last commit 2021-06-08; AFL++ is the maintained successor.
- Enricher: block and edge counting method unstated and the guided runs took longer than the blind run, so coverage is not compared at equal wall time; speed claims are prose ratios against AFL's own slower modes, not another fuzzer; llvm_mode broken with LLVM/Clang 13 (#151, #156); a fuzzer, not a profiler, so its category fits loosely.

## Caveats and trade-offs

First-party table in the project's own technical notes, one target and one session, no CPU, no run count and no repeat variance, so not reproducible as written. It measures discovered blocks and edges, not execs per second or time to bug, and the blind baseline is AFL's own fuzzer with guidance removed, not an independent blind fuzzer. The docs do not claim to beat libFuzzer: llvm_mode/README.llvm says the persistent mode is not as fast as pure in-process fuzzing such as LLVM's LibFuzzer, though much faster than the fork() model and more robust. No AFL versus libFuzzer numbers found in the repo. Last commit date taken from the github.com commits page; repo archived and read-only. [retier] Enricher: the docs do not say how blocks and edges were counted, and the guided runs took longer than 'Blind fuzzing L', so the coverage comparison is not at equal wall time. The speed claims (LLVM mode up to about 2x, fork server 1.5x-2x, deferred fork server 10x+) are prose ratios against AFL's own slower modes, not against another fuzzer. AFL is a fuzzer, not a profiler, so it fits its category loosely.

Needs an instrumented target (afl-gcc, afl-clang or the LLVM plugin; QEMU mode for black-box binaries is about 2-5x slower than compile-time instrumentation) and takes input as a file; persistent and deferred modes need small code changes and care to reset state. Archived and read-only; the maintained community fork is AFL++ (not checked in this session).

## Maintenance

Abandoned: last release 2.57b (2020-06-30), last commit 2021-06-08, archived 2024-03-22; Apache-2.0 and easy to build, but new campaigns should start from the maintained AFL++ fork.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party coverage tables in docs/technical_details.txt (GNU patch 2.7.3 at -O3, one session) with no CPU, no run count and no published harness for the variant fuzzers; speed claims in llvm_mode/README.llvm and technical_details.txt are first-party prose ratios without methodology.
- **Verifier notes:** All numbers match docs/technical_details.txt and llvm_mode/README.llvm; metadata confirmed (Apache-2.0, 4.2k stars, 672 forks, archived 2024-03-22, last commit 2021-06-08). The metric is coverage, not speed, and the baselines are AFL's own variants; the maintained successor AFL++ is a separate fork and may be a lead.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-67 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/google/AFL/master/docs/technical_details.txt>
  - <https://raw.githubusercontent.com/google/AFL/master/llvm_mode/README.llvm>
  - <https://raw.githubusercontent.com/google/AFL/master/README.md>
  - <https://github.com/google/AFL>
  - <https://github.com/google/AFL/commits/master>
- **Sources the enricher read:**
  - <https://github.com/google/AFL>
  - <https://github.com/google/AFL/issues?q=is%3Aissue+llvm>
  - <https://raw.githubusercontent.com/google/AFL/master/README.md>
  - <https://raw.githubusercontent.com/google/AFL/master/docs/technical_details.txt>
  - <https://raw.githubusercontent.com/google/AFL/master/llvm_mode/README.llvm>
  - <https://raw.githubusercontent.com/google/AFL/master/llvm_mode/afl-llvm-rt.o.c>
  - <https://raw.githubusercontent.com/google/AFL/master/afl-as.h>
  - <https://raw.githubusercontent.com/google/AFL/master/docs/perf_tips.txt>
  - <https://raw.githubusercontent.com/google/AFL/master/docs/notes_for_asan.txt>
  - <https://raw.githubusercontent.com/google/AFL/master/docs/INSTALL>
  - <https://raw.githubusercontent.com/google/AFL/master/docs/ChangeLog>
  - <https://raw.githubusercontent.com/google/AFL/master/docs/env_variables.txt>
  - <https://raw.githubusercontent.com/google/AFL/master/docs/parallel_fuzzing.txt>
  - <https://raw.githubusercontent.com/google/AFL/master/docs/historical_notes.txt>
  - <https://raw.githubusercontent.com/google/AFL/master/docs/status_screen.txt>
  - <https://raw.githubusercontent.com/google/AFL/master/qemu_mode/README.qemu>
  - <https://raw.githubusercontent.com/google/AFL/master/config.h>
  - <https://raw.githubusercontent.com/google/AFL/master/Makefile>
  - <https://github.com/AFLplusplus/AFLplusplus>
  - <https://raw.githubusercontent.com/AFLplusplus/AFLplusplus/stable/README.md>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/google/afl`) · [data/wave11/enrich/raw/github_com_google_afl.json](../../../data/wave11/enrich/raw/github_com_google_afl.json) (enrichment confidence 0.8)

</details>
