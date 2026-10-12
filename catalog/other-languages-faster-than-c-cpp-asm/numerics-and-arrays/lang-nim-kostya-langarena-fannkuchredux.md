# Nim (clang backend) in LangArena: CLBG::Fannkuchredux

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `MIT` · 🟢 active

> Nim's checked release build with the clang backend runs fannkuch-redux(8) 1.13x faster than the best C build; with the gcc backend it loses.

| | |
|---|---|
| **Beats** | C in the same suite: C/Gcc `make prod` (gcc -O2 with hardening), the -O3 -march=native `Fast` builds, and the suite's other C and C++ build variants (Fast, Unsafe, PGO, mycc, cproc) |
| **Claimed result** | 2026-10-05 run, CLBG::Fannkuchredux runtime in s: Nim/Clang 0.918 vs C/Gcc (prod, -O2) 1.036, about 1.13x (derived from page data); C/Clang 1.174; C++/Clang++ 1.128; C/Gcc/Fast 1.364; C/Clang/Fast 1.278; best -O3 row C++/Clang++/Unsafe 1.137, about 1.24x (derived from page data). Other Nim rows: Nim/Clang/ARC 0.934, Nim/NLVM 0.944, but Nim/Clang/Danger 1.114 and Nim/Clang/Max 1.231. The hobby compiler row C/mycc/LLVM/Default ran 1.026. Nim/Clang was 0.918-0.933 s in all six monthly runs from 2026-05-17 to 2026-10-05 against 1.020-1.047 s for C/Gcc prod, the best gcc or clang C/C++ build in every one of those runs. |
| **Workload** | CLBG fannkuch-redux with n = 8 (permutations held in fixed 32-element arrays), 700 timed iterations after 140 warm-up iterations, checksum checked (run.js); same algorithm line for line in every language, runtime in seconds. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB (result file 2026-10-05-kostya-ms7c37.js) |
| **Compiler and flags** | Nim 2.2.12 `nim c --threads:on -d:release --cc:clang` (system clang 22.1.8; no project nim.cfg or config.nims, so Nim's stock speed options apply, without -march=native; -d:release keeps runtime checks). C baseline rows (c/Makefile): prod = cc -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer with -Wl,-z,relro,-z,now -Wl,--gc-sections (gcc 16.0.1 trunk r16-8246 or clang 22.1.8); Fast = -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops, with -flto=thin passed only at link time (no -flto at compile time, so LTO is inert); Unsafe = -O3 -march=native -DNDEBUG -pipe -fno-stack-protector -fomit-frame-pointer -ffast-math -fvisibility=hidden -fno-common -fstrict-overflow -fno-trapping-math, with -flto=full only at link time. C++ rows use the same modes from cpp/Makefile. Versions and build commands from the build-cmd and version fields of results/2026-10-05-kostya-ms7c37.js. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://github.com/kostya/LangArena/blob/master/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

LangArena's 2026-10-05 run on an AMD Ryzen 7 3800X timed 700 calls of fannkuch-redux(8). Nim 2.2.12 (nim c --threads:on -d:release --cc:clang; clang 22.1.8 -O3, bound and overflow checks on) took 0.918 s. C/Gcc prod (GCC 16.0.1 trunk, -O2 hardened) took 1.036 s and C/Clang prod 1.174 s, and the best -O3 C/C++ row, C++/Clang++/Unsafe, took 1.137 s. That is about 1.13x, 1.28x and 1.24x (derived from page data), with all checksums matching 135762480.

## Use it when

- Nim kernels over small fixed-size integer arrays with short inner loops (permutation enumeration, combinatorial search) built with the stock -d:release flags and --cc:clang: the checked build matched or beat hand-written C here.
- Evidence that Nim's default runtime checks need not cost speed on such loops: the checked Nim/Clang build (0.918-0.933 s) beat the unchecked -d:danger build (1.114-1.146 s) in all five monthly runs checked (2026-07-14 to 2026-10-05).
- Picking a Nim backend for integer loop kernels: clang (0.918 s) and NLVM (0.944 s) beat gcc (1.116 s) on the same Nim source.

## Skip it when

- As evidence that Nim beats C: with gcc as the backend Nim loses (Nim/GCC 1.10-1.14 s vs C/Gcc 1.02-1.047 s in every run from 2026-07-14 to 2026-10-05), and a hobby C compiler row (C/mycc/LLVM/Default, 1.026 s) also beats C/Gcc. The spread between equivalent C sources is about 15 percent.
- Expecting -d:danger or -Ofast -march=native to add speed: on this test they are slower (Nim/Clang/Danger 1.114 s, Nim/Clang/Max 1.231 s, Nim/GCC/Max 1.41 s).
- Floating-point or larger numeric kernels: in the same run Nim/Clang is slower than C/Gcc on CLBG::Nbody (1.73 vs 1.465 s), CLBG::Spectralnorm (1.011 vs 0.925 s) and Matmul::Single (8.788 vs 5.019 s).
- The real CLBG fannkuch-redux workload (n=12, multithreaded, SIMD reference programs): only n=8, single-threaded and fully cache-resident, was measured.
- Anyone needing a large margin: 1.13x over C/Gcc, below the V/Clang row (0.875 s) on the same test.

## How it is fast

No language mechanism is behind this: it is a codegen difference between two equivalent C programs built by the same LLVM 22.1.8 (the nim_clang and clang_c Docker images both start FROM langarena:base_clang). In the source, the hand-written C copies the permutation with memcpy(perm, perm1, n\*sizeof(int)) at a runtime length for each of the 40,320 permutations, swaps through a pointer helper, and uses 32-bit int. Nim emits a plain element-copy loop over 64-bit ints, with -d:release keeping bound and overflow checks. Per permutation that is 32.5 ns for Nim/Clang against 36.7 ns for C/Gcc and 41.6 ns for C/Clang (derived from page data over 28.2M timed permutations). Untested hypothesis (assembly not inspected): the runtime checks stop clang from turning the copy loop into a memcpy call or from vectorising and unrolling loops of at most 8 iterations, which helps here.

## Compared with alternatives

The V/Clang (0.875 s) and Zig ReleaseSafe (0.977 s) rows of this test show the same codegen effect with a larger or similar margin, and V also reverses with gcc. Cite this Nim row only for Nim on clang; when citing the test itself, prefer the V or Zig rows.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Nim 2.2.12 compiler plus clang (the LLVM 22.1.8 release tarball in the measured image); the kernel uses only Nim's system module |
| **Minimum toolchain** | Nim 2.2.12 with clang 22.1.8 as measured (the nimble file requires nim &gt;= 2.0.0); other versions were not measured, and the result depends on backend codegen |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X, 78 GB) in Docker images built FROM ubuntu:26.04; the Nim build targets generic x86-64 (no -march=native) |
| **Thread safety** | Not applicable: single-threaded pure function over stack arrays |
| **Drop-in for the baseline** | no |

## Gotchas

- The result depends on the backend: the same Nim source is 0.918 s through clang but 1.116 s through gcc 16, slower than the hand-written C/Gcc row (1.036 s). This pattern held in all five runs checked, and the V/GCC row (1.126 s) shows the same reversal, so read it as clang codegen on Nim-emitted C, not as a Nim property.
- Turning safety checks off makes it slower: Nim/Clang/Danger runs 1.114-1.146 s against 0.918-0.933 s checked across five runs. Similarly, C at -O3 -march=native -funroll-loops (1.278-1.364 s) loses to C at -O2 (1.036-1.174 s). On loops this short, extra unrolling or vectorisation costs time.
- The three baselines are not line for line. C uses a runtime-length memcpy and a pointer swap helper, and C++ uses std::copy, std::reverse and std::rotate, so the C++ rows also measure library-algorithm codegen. Nim's arrays hold 64-bit ints where C and C++ use 32-bit int.
- There is one in-process timing per configuration per monthly run, with no variance reported. The C/C++ prod rows are -O2 with -fstack-protector-strong and frame pointers, while Nim's nim.cfg passes clang -O3 -fno-strict-aliasing; the -O3 and -ffast-math C/C++ rows also lose, though their -flto is passed only at link time and is therefore inert.

## Known shortcomings

- Lead stable over 6 runs, but Nim's own -d:danger (1.114 s) and -Ofast (1.231 s) builds lose, so the win looks like codegen luck rather than the language; flags unmatched and 64-bit vs 32-bit ints; the C Fast/Unsafe rows' link-only -flto is inert.
- Backend codegen luck rather than a Nim property: Nim/GCC (1.116 s) loses to C/Gcc (1.036 s) in all five runs checked and Nim/Clang/Danger is slower than the checked build. The baselines are not line for line (C uses a runtime-length memcpy and a pointer-swap helper, C++ uses std::copy, std::reverse and std::rotate). Nim is slower than C on Nbody, Spectralnorm and Matmul::Single in the same suite. Nim/Clang and C/Clang share the same LLVM 22.1.8 image; -O3 mapping and the ORC default confirmed at the v2.2.12 tag.

## Caveats and trade-offs

Flags are not matched: C `prod` is -O2 with hardening and the Nim row is built for generic x86-64 with runtime checks on, but the -O3 Fast and -ffast-math C/C++ builds are also slower on this test (1.137-1.364 s). Nim emits C, so the gap is Nim-generated C versus hand-written C compiled by the same clang. The Nim source matches the C source loop for loop, except that Nim's int arrays are 64-bit where C uses 32-bit int. The result is fragile to build settings: Nim's own unchecked -d:danger clang build (1.114 s) and -Ofast -march=native LTO build (1.231 s) are slower than the checked default build (0.918 s), and C at -O3 with -funroll-loops (1.278-1.364 s) is slower than C at -O2 (1.036-1.174 s), which suggests the tiny loops (trip counts of at most 8) are hurt by aggressive unrolling or vectorisation and that the Nim/Clang default build happens to avoid it (inference, assembly not inspected). No mechanism, so the tier is capped at C. A hobby C compiler row (C/mycc/LLVM/Default) reached 1.026 s and 1.006 s in the 2026-08-14 run. One benchmark only: Nim/Clang is slower than C on CLBG::Nbody (1.73 s vs C/Gcc 1.465 s) and Matmul::Single (8.788 s vs 5.019 s). Single measurement per configuration per run; subjective AI-assisted suite. The C Fast and Unsafe LTO flags are link-only and inert. [retier] Enricher: backend codegen effect rather than a Nim property; Nim/GCC (1.116 s) loses to C/Gcc (1.036 s) in all five runs checked and Nim/Clang/Danger (1.114-1.146 s) is slower than the checked build (0.918-0.933 s). The baselines are not line for line (C uses a runtime-length memcpy and a pointer-swap helper, C++ uses std::copy, std::reverse and std::rotate). Nim is slower than C on Nbody, Spectralnorm and Matmul::Single in the same suite. Nim/Clang and C/Clang share the same LLVM 22.1.8 image; the -O3 mapping and ORC default are confirmed at the v2.2.12 tag.

Nim compiles to C and then to native code via the system C compiler, so the claim is about the C that Nim emits (garbage collection mode, bounds checks and overflow checks follow -d:release defaults).

## Maintenance

LangArena is an active MIT suite (41 stars, last commit 2026-10-08, monthly reruns), and the 80-line Nim file is copyable; the speedup is a backend-codegen effect that disappears with gcc or -d:danger, so the entry stays at tier C.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Methodology is A-grade (nim/src/benchmarks/fannkuchredux.nim vs c/src/fannkuchredux.c and cpp/src/fannkuchredux.cpp, line-for-line the same algorithm, build commands, flags in c/Makefile, compiler versions and the Ryzen 7 3800X in the results file) and the lead is stable over six monthly runs, but no mechanism can be read from the sources: Nim's own unchecked (-d:danger, 1.114 s) and -Ofast -march=native (1.231 s) clang builds lose to the checked default build, as -O3 C loses to -O2 C, which points at backend loop-optimisation luck rather than the language, so it stays at C under the no-mechanism cap.
- **Verifier notes:** Numbers match the CLBG::Fannkuchredux-runtime rows of results/2026-10-05-kostya-ms7c37.js, and the Nim/Clang lead holds in all six runs checked (2026-05-17 to 2026-10-05). Shortcomings to record: no mechanism; win vanishes in Nim's own -d:danger and -Ofast builds (codegen luck, not language); flags not matched (Nim generic x86-64 with checks vs C -O2 hardened; -O3 C rows also lose); 64-bit vs 32-bit element types; one benchmark only, Nim slower on Nbody and Matmul; single measurement per run; subjective suite. Metadata checks out (MIT, 41 stars, not a fork, last commit 2026-10-08).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-47 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-06-16-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-05-17-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/nim/src/benchmarks/fannkuchredux.nim>
  - <https://github.com/kostya/LangArena/commits/master/nim/src/benchmarks/fannkuchredux.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/nim/src/benchmark.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/nim/benchmarks.nimble>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/nim/run>
  - <https://github.com/kostya/LangArena/tree/master/nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/fannkuchredux.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/fannkuchredux.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/run.js>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/commits/master/c/src/fannkuchredux.c>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue+nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker-compose.yaml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/base>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/base_clang>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/clang_c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/base_gcc>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/gcc_c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/nim_clang>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/nim_gcc>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/src/benchmarks/fannkuchredux.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/src/benchmark.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/src/benchmarks.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/benchmarks.nimble>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/run>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/fannkuchredux.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/fannkuchredux.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/nim-lang/Nim/v2.2.12/config/nim.cfg>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:nim/kostya/langarena#fannkuchredux`) · [data/wave14/enrich/raw/lang_nim_kostya_langarena_fannkuchredux.json](../../../data/wave14/enrich/raw/lang_nim_kostya_langarena_fannkuchredux.json) (enrichment confidence 0.6)

</details>
