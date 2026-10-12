# V (clang backend) in LangArena: CLBG::Fannkuchredux

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `V` · `MIT` · 🟢 active

> V's fannkuch-redux in kostya's LangArena, built through clang, runs 1.18x faster than the suite's fastest C build, but loses under gcc.

| | |
|---|---|
| **Beats** | C in the same suite: C/Gcc `make prod` (gcc -O2 with hardening), the -O3 -march=native `Fast` builds, and the suite's other C and C++ build variants (Fast, Unsafe, PGO, mycc, cproc) |
| **Claimed result** | 2026-10-05 run, CLBG::Fannkuchredux runtime in s: V/Clang 0.875 vs C/Gcc 1.036 (best of all gcc and clang C/C++ rows), about 1.18x faster (derived from page data); C/Clang 1.174 (1.34x); C++/Clang++ 1.128; C++/G++ 1.199. Against the -O3 -march=native rows: best -O3 C/C++ row C++/Clang++/Unsafe 1.137 (1.30x), C/Clang/Fast 1.278, C/Gcc/Fast 1.364. Flag-matched pair: V/Clang/Perf (clang -O3 -march=native -flto) 0.912 vs C/Clang/Fast (clang -O3 -march=native) 1.278, about 1.40x (derived). With the GCC backend V loses: V/GCC 1.126 vs C/Gcc 1.036 (about 1.09x slower) and V/GCC/Perf 1.08. Stable in five monthly runs (2026-07-14, 08-14, 09-03, 09-18, 10-05): V/Clang 0.862-0.879 s vs the best gcc or clang C/C++ row, always C/Gcc, at 1.020-1.047 s (1.18-1.20x, derived); V/GCC 1.122-1.133 s, slower than C/Gcc in every run. |
| **Workload** | CLBG fannkuch-redux with n = 8 (8! = 40,320 permutations per call), 700 iterations, checksum 135762480 verified by the suite (run.js); permutation arrays sized 32 ints. Same algorithm in every language: count-array permutation generator, prefix reversal by swaps, checksum and max-flips. Runtime of the benchmark in seconds. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB (result file 2026-10-05-kostya-ms7c37.js) |
| **Compiler and flags** | V 0.5.1 (0c3183c) 'v -enable-globals -cc clang -prod' with clang 22.1.8; V emits C, and -prod adds -O3 and -flto to the C compiler call (v3_prod_c_optimization_flags in vlang/v master vlib/v/driver/driver.v, -O2 only for very large generated units; the 0.5.1 builder itself was not checked), no -march=native. V/Clang/Perf and V/GCC/Perf add -cflags '-O3 -march=native -flto'. C/C++ rows: GCC 16.0.1 20260322 (trunk r16-8246, Ubuntu build) and Clang 22.1.8. 'prod' (c/Makefile CFLAGS_PROD, cpp/Makefile CXXFLAGS_PROD): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections. 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops, with -flto=thin passed only at link time. 'Unsafe': -O3 -march=native -DNDEBUG -pipe -fno-stack-protector -fomit-frame-pointer -ffast-math -fvisibility=hidden -fno-common -fstrict-overflow -fno-trapping-math, with -flto=full only at link time. Because the LTO flags appear only in LDFLAGS, the Fast and Unsafe builds probably get no real LTO (inference from the Makefiles). PGO rows are -O2 plus profile use. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://github.com/kostya/LangArena/blob/master/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

LangArena's 2026-10-05 run on an AMD Ryzen 7 3800X measured each row once over 700 timed calls of fannkuch-redux with n = 8, checksum-gated. V 0.5.1 built with -cc clang -prod (clang 22.1.8, -O3 -flto) took 0.875 s, against 1.036 s for C with gcc 16.0.1 -O2 prod (1.18x, derived from page data), 1.174 s for C with clang -O2 prod (1.34x) and 1.278 s for clang -O3 -march=native C (1.46x). The V/GCC build took 1.126 s, slower than C/Gcc.

## Use it when

- As a data point on how V 0.5.1's generated C compiles under clang on a branchy, permutation-heavy integer kernel, compared with C, C++, Nim, Zig and Rust in one harness with one checksum.
- As a readable, MIT-licensed, bounds-checked V fannkuch-redux (fixed [32]int arrays, no unsafe blocks, no attributes) to copy or port.
- When you already ship V with -cc clang -prod and want evidence that idiomatic, bounds-checked V integer loops need not cost speed against hand-written C.

## Skip it when

- As evidence that V beats C in general: across all 50 LangArena tests in the 2026-10-05 run V/Clang totals 99.3 s against 56.5 s for C/Gcc and 54.3 s for C/Clang, and it beats both C prod rows in only 8 tests.
- With the GCC backend: V/GCC 1.126 s and V/GCC/Perf 1.08 s are both slower than C/Gcc at 1.036 s on this same test.
- If you expect -march=native to help: V/Clang/Perf (0.912 s) is slower than plain V/Clang -prod (0.875 s), and every -O3 -march=native C/C++ row (1.137-1.364 s) is slower than gcc -O2 C (1.036 s). The kernel is sensitive to code generation and layout, so a compiler update can move it either way.
- For production fannkuch or permutation work: n is fixed at 8 (40,320 permutations per call), the code is single-threaded, and V only panics, rather than clamping as the C version does, when n &gt; 32.

## How it is fast

There is no language-level mechanism. V transpiles to one C file and hands it to the same clang 22.1.8 binary as the C rows: the V and C Clang images both derive from langarena:base_clang, built from the llvm.org 22.1.8 release tarball. V 0.5.1's -prod adds -O3 -flto, and so does -fno-strict-aliasing for gcc only (vlib/v/builder/cc.v at tag 0.5.1). The two sources run the same algorithm with 32-int stack arrays, but they are shaped differently. The C file copies the permutation with a runtime-length memcpy and swaps through a pointer helper. The V file uses plain index loops, and V 0.5.1 wraps every non-literal fixed-array index in builtin__v_fixed_index, a bounds check that panics (vlib/v/gen/c/index.v, vlib/builtin/builtin.c.v), because no @[direct_array_access] or -no-bounds-checking is used. So V wins with bounds checks on. A plausible explanation, inferred from the sources and not measured, is that the checks keep clang from turning the copy and rotate loops into libc memcpy and memmove calls or vectorising tiny-trip-count loops. No assembly or profile is published, and the same V source is slower than C under gcc.

## Compared with alternatives

Compared with the Nim/Clang (0.918 s) and Zig (0.977 s) LangArena Fannkuchredux entries, this has the largest margin over C on this test. Like Nim, though, it is a C-emitting language whose lead depends on clang, while Zig's lead comes from its own LLVM pipeline. Use the Zig row for a non-transpiled comparison, and this one only as a V-on-clang data point.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | V standard library plus the suite's benchmark and helper modules (config from run.js); v.mod also lists srackham.pcre2 for other tests |
| **Minimum toolchain** | V 0.5.1 (release v_linux.zip, build 0c3183c) with clang 22.1.8; flags -enable-globals -cc clang -prod |
| **Platforms** | any platform V supports; results published only for x86-64 Linux (AMD Ryzen 7 3800X, Docker images on Ubuntu 26.04) |
| **Thread safety** | single-threaded; run() mutates the struct's result_val; not documented otherwise |
| **Drop-in for the baseline** | no |

## Gotchas

- This is a backend result, not a V result. Under clang, V's generated C beats hand-written C (0.875 s vs 1.174 s). Under gcc 16, the same V source loses (1.126 s vs 1.036 s), so which C compiler V calls decides the sign. The suite's own v/run script builds with -cc gcc.
- The fair C baseline is C/Gcc prod (gcc -O2 with -fstack-protector-strong and -fno-omit-frame-pointer, 1.036 s), not the -O3 -march=native rows. On this test the hardened -O2 build beats every -O3 C build, and C/Clang/Unsafe (no stack protector, -fomit-frame-pointer) is no faster than clang -O2 prod, so the hardening flags do not explain V's lead.
- The two backends run in different images. The gcc images use Ubuntu's packaged gcc 16 (version string 'Ubuntu 16-20260322-1ubuntu1', a trunk snapshot) and the clang images use the upstream llvm.org 22.1.8 release tarball. V/Clang vs C/Clang, with the same clang binary and the same base image, is therefore the cleanest pair, and V leads it by 1.34x.
- There is one measurement per row per run, with no repeats or variance. The order held in the 2026-09-18 and 2026-10-05 files read here (V/Clang 0.871 and 0.875 s, C/Gcc 1.047 and 1.036 s), and the verifier reports the same order in five monthly runs.

## Known shortcomings

- Clang-only win: under gcc V loses (V/GCC 1.126 s vs C/Gcc 1.036 s); V emits C, so the gap is codegen between two C sources (memcpy and a swap helper vs plain loops); 1.40x on the V/Clang/Perf vs C/Clang/Fast pair, stable over 5 monthly runs of a subjective AI-assisted suite.
- Backend result, not a V result: V/Clang 0.875 s beats C/Gcc 1.036 s in the 2026-09-18 and 2026-10-05 runs (V/Clang and C/Clang images share the same clang 22.1.8 base), but V/GCC (1.126 s) loses to hand-written C and the suite's own v/run script builds with gcc. V 0.5.1 bounds-checks every fixed-array index (builtin__v_fixed_index in gen/c/index.v), so it is not a safety-off win; the gap comes from the shape of the generated C and the mechanism is unproven. Over all 50 tests V/Clang totals 99.3 s against 54-56 s for C. -prod flags at 0.5.1 (builder/cc.v): clang -O3 -flto; gcc adds -fno-strict-aliasing.

## Caveats and trade-offs

V is a C transpiler, so this is V-generated C against hand-written C, both compiled by clang or gcc; the win appears only with clang (V/Clang 0.875 s vs C/Clang 1.174 s) and reverses with gcc (V/GCC 1.126 s vs C/Gcc 1.036 s), which points to codegen differences between two equivalent C sources (runtime-length memcpy and a pointer swap helper in the C file, plain loops in V) rather than a language advantage. The headline C 'prod' rows are -O2 with hardening and V -prod is -O3 -flto, but the flag-matched V/Clang/Perf vs C/Clang/Fast pair (both clang -O3 -march=native) still shows 1.40x; note that on this test every -O3 -march=native C/C++ row is slower than the -O2 C/Gcc row, so the -O3 rows are not the strongest C baseline. One benchmark only: V is slower than C elsewhere in the same file (Nbody 1.86 s vs 1.465 s). Gossamer (0.913 s), Nim/Clang (0.918 s) and Zig (0.977 s) also beat the C rows here. Each configuration is timed once per monthly run; the lead is stable across five runs. LangArena's README calls it a subjective, not peer-reviewed suite whose translations were AI-assisted and reviewed by the author. [retier] Enricher: V/Clang and C/Clang images build on the same clang 22.1.8 base and the win holds in the 2026-09-18 and 2026-10-05 runs, but only under clang (V/GCC 1.126 s loses; the suite's own v/run script builds with gcc). V 0.5.1 bounds-checks every fixed-array index (builtin__v_fixed_index in gen/c/index.v), so it is not a safety-off win; the mechanism is unproven. Over all 50 tests V/Clang totals 99.3 s against 54-56 s for C.

V transpiles to C and relies on the system C compiler; the V toolchain is young and less portable than gcc or clang. Benchmarks are written in the suite's safe, idiomatic style.

## Maintenance

Active suite (MIT, 41 stars, 16 forks, 622 commits, monthly result files through 2026-10-05). The V file is small and copyable, but its lead over C is a clang code-generation artefact that has held over five runs without an explanation, so treat it as a toolchain snapshot.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A on the LangArena precedent (Etc::Words, Template::Parse, Distance::NGram entries in this wave): public code for every side (v/fannkuchredux.v, c/src/fannkuchredux.c, cpp/src/fannkuchredux.cpp; workload n=8, 700 iterations, checksum in run.js), C/C++ flags in c/Makefile and cpp/Makefile, the V build command, compiler versions and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js. The same algorithm runs on both sides and the lead holds in all five monthly runs checked, so the record's 'no stated mechanism' cap is not a tier rule.
- **Verifier notes:** Every number verified in the results files (2026-10-05 plus four earlier monthly runs); metadata confirmed (MIT, 41 stars, last commit 2026-10-08, not a fork). Tier raised C to A on the LangArena precedent; same_opt_level set true via the flag-matched V/Clang/Perf vs C/Clang/Fast pair. Shortcomings to record: clang-only win that reverses under gcc (V/GCC 1.09x slower than C/Gcc), V emits C so the gap is source-shape codegen not a language mechanism, single benchmark, -O3 C rows slower than -O2 on this test.
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
  - <https://raw.githubusercontent.com/kostya/LangArena/master/v/fannkuchredux.v>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/v/v.mod>
  - <https://github.com/kostya/LangArena/tree/master/v>
  - <https://github.com/vlang/v/tree/master/vlib/v>
  - <https://github.com/vlang/v/tree/master/vlib/v/driver>
  - <https://raw.githubusercontent.com/vlang/v/HEAD/vlib/v/driver/driver.v>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/tree/master/v>
  - <https://github.com/kostya/LangArena/commits/master/v>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue+fannkuch+OR+vlang+OR+%22V%2FClang%22>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/xtime.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/docker-compose.yaml>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/build-docker.sh>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/docker/base>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/docker/base_clang>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/docker/base_gcc>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/docker/v_clang>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/docker/v_gcc>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/v/fannkuchredux.v>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/v/benchmark.v>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/v/base_benchmark.v>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/v/main.v>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/v/run>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/v/test>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/v/v.mod>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/fannkuchredux.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/fannkuchredux.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/fannkuchredux.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/zig/src/fannkuchredux.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/vlang/v/0.5.1/doc/docs.md>
  - <https://raw.githubusercontent.com/vlang/v/0.5.1/vlib/v/builder/cc.v>
  - <https://raw.githubusercontent.com/vlang/v/0.5.1/vlib/v/gen/c/index.v>
  - <https://raw.githubusercontent.com/vlang/v/0.5.1/vlib/builtin/builtin.c.v>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:v/kostya/langarena#fannkuchredux`) · [data/wave14/enrich/raw/lang_v_kostya_langarena_fannkuchredux.json](../../../data/wave14/enrich/raw/lang_v_kostya_langarena_fannkuchredux.json) (enrichment confidence 0.75)

</details>
