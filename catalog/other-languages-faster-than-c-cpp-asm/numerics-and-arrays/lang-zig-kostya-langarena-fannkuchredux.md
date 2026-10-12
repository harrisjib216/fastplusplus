# Zig (ReleaseSafe) in LangArena: CLBG::Fannkuchredux

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Bounds-checked Zig fannkuch-redux kernel, about 6% faster than GCC -O2 C in LangArena at n = 8.

| | |
|---|---|
| **Beats** | C in the same suite: C/Gcc `make prod` (gcc -O2 with hardening), the -O3 -march=native `Fast` builds, and the suite's other C and C++ build variants (Fast, Unsafe, PGO, mycc, cproc) |
| **Claimed result** | 2026-10-05 run, CLBG::Fannkuchredux runtime in s: Zig (ReleaseSafe) 0.977 vs C/Gcc 1.036 (best of all gcc and clang C/C++ rows), about 1.06x faster (derived from page data); C/Clang 1.174 (1.20x). Against the -O3 -march=native rows: best -O3 C/C++ row C++/Clang++/Unsafe 1.137 (1.16x), C/Clang/Fast 1.278 (1.31x), C/Gcc/Fast 1.364. Zig/Unchecked (ReleaseFast) is slower than the safe build at 1.024 s. Five monthly runs (2026-07-14 to 2026-10-05): Zig 0.972-0.989 s vs the best gcc or clang C/C++ row, always C/Gcc, at 1.020-1.047 s (1.04-1.07x, derived); Zig/Unchecked 1.024-1.054 s, slower than ReleaseSafe in every run. The suite author's own mycc C compiler (LLVM backend) reached 1.006 s on 2026-08-14, still behind Zig's 0.972 s that month. |
| **Workload** | CLBG fannkuch-redux with n = 8 (8! = 40,320 permutations per call), 700 iterations, checksum 135762480 verified by the suite (run.js); permutation arrays sized 32 ints. Same algorithm in every language. Runtime of the benchmark in seconds. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB (result file 2026-10-05-kostya-ms7c37.js) |
| **Compiler and flags** | Zig 0.17.0 (0.16.0 in the July to September runs) 'zig build build-zig': zig/build.zig builds this row with optimize = .ReleaseSafe (LLVM release optimisation with runtime safety checks kept) and b.standardTargetOptions(.{}), which defaults to the native host CPU, so it is closer to -O3 -march=native with bounds checks than to the generic -O2 prod C build; Zig/Unchecked is the same source at .ReleaseFast. C/C++ rows: GCC 16.0.1 20260322 (trunk r16-8246, Ubuntu build) and Clang 22.1.8. 'prod' (c/Makefile CFLAGS_PROD, cpp/Makefile CXXFLAGS_PROD): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections. 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops, with -flto=thin passed only at link time. 'Unsafe': -O3 -march=native -DNDEBUG -pipe -fno-stack-protector -fomit-frame-pointer -ffast-math -fvisibility=hidden -fno-common -fstrict-overflow -fno-trapping-math, with -flto=full only at link time. Because the LTO flags appear only in LDFLAGS, the Fast and Unsafe builds probably get no real LTO (inference from the Makefiles). PGO rows are -O2 plus profile use. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://github.com/kostya/LangArena/blob/master/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

On an AMD Ryzen 7 3800X (results 2026-10-05), Zig 0.17.0 ReleaseSafe ran 700 n = 8 fannkuch-redux calls in 0.977 s against 1.036 s for C/Gcc prod (GCC 16.0.1, -O2 with stack protector and frame pointers), the best of the 16 GCC 16.0.1 and Clang 22.1.8 C and C++ builds, and 1.137-1.364 s for the -O3 -march=native rows: about 1.06x, derived from page data. The four earlier monthly runs (Zig 0.16.0) give 1.059x, 1.067x, 1.038x and 1.059x.

## Use it when

- Tight integer loops over small fixed-size stack arrays in Zig where you want bounds and overflow checks left on: here the checked ReleaseSafe build beat ReleaseFast in all five monthly runs (0.972-0.989 s vs 1.024-1.054 s).
- New code you would otherwise write in C for permutation or combinatorial kernels, when Zig is acceptable: idiomatic checked Zig matched or beat every GCC and Clang C/C++ build on this kernel.
- As a data point that Zig's safe release mode need not cost speed on branchy integer code, provided you measure your own kernel.

## Skip it when

- To speed up existing C or C++: a 1.04-1.07x edge on one tiny kernel does not justify a rewrite, and the C rows themselves spread by 32% across flag sets on the same source.
- If you want the fastest row on this test: V/Clang (0.875 s), Gossamer (0.913 s), Nim/Clang (0.918 s) and Nim/NLVM (0.944 s) beat Zig's 0.977 s in the same run.
- As a proxy for the real Benchmarks Game workload: this is n = 8 (about 1.4 ms per call) single-threaded, while the CLBG uses n = 12 with threads, so it says nothing about larger n or parallel scaling.
- For portable binaries: the measured Zig binary targets the build host's CPU (b.standardTargetOptions default), whereas the headline C prod build is generic x86-64.

## How it is fast

No distinctive technique: same algorithm and arrays on both sides, with n read from run.js at run time. The Zig flip loop runs while (i &lt; j) with j counting down where the C precomputes the trip count k2 = (k + 1) &gt;&gt; 1, and the Zig row is compiled by LLVM for the host CPU in ReleaseSafe with bounds, cast and overflow checks kept. The margin looks like loop code-generation variance rather than a language effect: on identical C source C/Clang -O2 (1.174 s) is 13% slower than C/Gcc -O2 (1.036 s), every -O3 -march=native C and C++ row (1.137-1.364 s) is slower than C/Gcc -O2, and Zig's own ReleaseFast build (1.024 s) is slower than its checked build (0.977 s); no disassembly was published to pin the cause.

## Compared with alternatives

The catalogued V/Clang (0.875 s) and Nim/Clang (0.918 s) rows for the same test are faster in the same run; pick the Zig row's approach when you want the measured build itself to keep runtime safety checks (ReleaseSafe) without a C backend, not for raw speed. Whether the V and Nim production rows keep runtime checks was not checked.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Zig std builtins only: @memcpy, @memset, @max, @intCast) |
| **Minimum toolchain** | The suite needs Zig 0.16 std APIs (std.process.Init, std.Io); measured with Zig 0.16.0 (July to September 2026) and 0.17.0 (2026-10-05) |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X), built for the host CPU; nothing platform-specific in the kernel |
| **Thread safety** | The kernel is a pure function over its own stack arrays, so it is reentrant; the benchmark runs it single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- Latent crash outside the measured configuration: runImpl does @as(u32, @intCast(result.checksum \* 100 + result.max_flips)), which panics in ReleaseSafe (and is undefined in ReleaseFast) when the sum is negative. A Python replay of the algorithm gives a negative value for n = 2 (checksum -1, max flips 1, so -99); n = 8 gives +161,622. The C version casts to uint32_t and wraps, and runImpl also silently skips n &gt; 16 where the C clamps n to 32.
- Checksum reproduces: the same replay gives checksum 1616 and 22 maximum flips for n = 8, and run.js's expected 135762480 equals 161,622 times 840 calls (140 untimed warm-up plus 700 timed); the results file does not record checksum status.
- Same algorithm, not same source: the C++ row uses std::reverse and std::rotate (1.128 s Clang++, 1.199 s G++ prod), the C row a k2-count swap loop and the Zig row an i &lt; j loop. The 4-7% Zig lead held in all five monthly runs with code unchanged since before the first (zig/src/fannkuchredux.zig last changed 2026-02-23, c/src/fannkuchredux.c 2026-04-21), but the author's own LLVM-based C compiler row (C/mycc/LLVM/Default, 1.026 s) is within 5%, so a compiler update could flip the order.
- One timing per configuration per monthly run, no variance reported; the suite README says its ranking reflects 50 tasks and is 'not my pick for a single test', and calls itself subjective with AI-assisted translations.

## Known shortcomings

- 1.04-1.07x margin on one test with no language mechanism; Zig builds for the native CPU and ReleaseFast is slower than ReleaseSafe in every run; the -O3 -march=native C rows also lose.
- No timing flaw; checksum 135762480 replays (840 calls). The 1.04-1.07x lead is codegen variance: C/Clang -O2 is 13% slower than C/Gcc -O2 on the same source and ReleaseFast is slower than ReleaseSafe in all five runs. Latent bug outside the measured configuration: runImpl's @intCast of checksum \* 100 + max_flips to u32 panics in ReleaseSafe for n = 2 (value -99); n = 8 is unaffected, and runImpl silently skips n &gt; 16 where C clamps to 32.

## Caveats and trade-offs

Small margin on one benchmark (1.04-1.07x over the best C row across five monthly runs), stable rather than noise, but from codegen differences between equivalent loops, not a Zig language mechanism. Zig/Unchecked (ReleaseFast) is consistently 3-8% slower than the safe ReleaseSafe build, a systematic codegen or layout effect that shows how sensitive this kernel is to compilation details. Zig's production row targets the native CPU (b.standardTargetOptions default) while the C prod rows are generic x86-64 -O2 with hardening, but the -O3 -march=native Fast and Unsafe C/C++ rows are slower (1.137-1.364 s), so flags do not explain the gap; on this test every -O3 C/C++ row is slower than the -O2 C/Gcc row. The Zig loop is written differently from the C loop (decrementing j against the C k2 count) and uses @memcpy. Zig is slower than C on Matmul and several other numeric rows in the same file. Each configuration is timed once per monthly run. LangArena's README calls it a subjective, not peer-reviewed suite whose translations were AI-assisted and reviewed by the author. [retier] Enricher: checksum 135762480 replays (840 calls); the lead is codegen variance (C/Clang -O2 is 13% slower than C/Gcc -O2 on the same source, ReleaseFast slower than ReleaseSafe in all five runs). Latent bug outside the measured configuration: runImpl's @intCast to u32 panics in ReleaseSafe for n = 2 (value -99), and runImpl silently skips n &gt; 16 where C clamps to 32.

The default Zig row keeps bounds and overflow checks enabled and still beats the C builds, but the margin to the best C row is only about 6%.

## Maintenance

Active MIT-licensed suite (41 stars, last commit 2026-10-08, monthly reruns); no harness flaw behind the numbers (C, C++ and Zig time run_all with a monotonic clock after the same 20% untimed warm-up and check the same checksum), but the edge is a 4-7% code-generation effect on one tiny kernel, and the Zig port has a latent ReleaseSafe panic for n = 2 (negative checksum cast to u32) that the n = 8 configuration never hits.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A on the LangArena precedent (Zig Etc::Words and Distance::NGram entries in this wave): public code for every side (zig/src/fannkuchredux.zig, c/src/fannkuchredux.c, cpp/src/fannkuchredux.cpp; workload in run.js), build modes in zig/build.zig, flags in c/Makefile and cpp/Makefile, versions, build commands and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js. The margin is small (1.04-1.07x over the best C row) but present in all five monthly runs checked.
- **Verifier notes:** Every number verified in the results files (2026-10-05 plus four earlier monthly runs); metadata confirmed (MIT, 41 stars, last commit 2026-10-08). Tier raised C to A on the LangArena precedent; same_opt_level set true because the -O3 -march=native C/C++ rows (flag-matched to Zig's native ReleaseSafe) also lose. Shortcomings to record: 1.04-1.07x margin on one benchmark, ReleaseFast slower than ReleaseSafe, codegen variance rather than a language mechanism, native-CPU Zig vs generic -O2 headline C row.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-48 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/tree/master/results>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/Makefile>
  - <https://github.com/kostya/LangArena/tree/master/c/src>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/fannkuchredux.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/fannkuchredux.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/fannkuchredux.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/zig/build.zig>
  - <https://github.com/kostya/LangArena/tree/master/zig/src>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/zig/src/fannkuchredux.zig>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig.zon>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/main.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/benchmark.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/helper.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/fannkuchredux.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/fannkuchredux.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.h>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/fannkuchredux.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/fannkuchredux.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/crystal/main.cr>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://github.com/kostya/LangArena/commits/master/zig/src/fannkuchredux.zig>
  - <https://github.com/kostya/LangArena/commits/master/c/src/fannkuchredux.c>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://github.com/kostya/LangArena/issues/1>
  - <https://github.com/kostya/LangArena/tree/master/crystal>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:zig/kostya/langarena#fannkuchredux`) · [data/wave14/enrich/raw/lang_zig_kostya_langarena_fannkuchredux.json](../../../data/wave14/enrich/raw/lang_zig_kostya_langarena_fannkuchredux.json) (enrichment confidence 0.7)

</details>
