# V (gcc backend) in kostya/benchmarks: Brainfuck bench.b

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `V` · `MIT` · 🟢 active

> kostya's Brainfuck op-tree interpreter ported to V and compiled through gcc; about 10% faster than C++/g++, on bench.b only.

| | |
|---|---|
| **Beats** | C++ (g++ 16.1.0, -std=c++23 -O3 -march=native -flto=auto) 1.097 s; also C/gcc 1.112 s, C/clang 1.136 s and C++/clang++ 1.167 s |
| **Claimed result** | README bench.b table (median s): V/gcc 0.985 vs C++/g++ 1.097 (about 1.11x faster), C/gcc 1.112 (1.13x), C/clang 1.136, C++/clang++ 1.167 (derived from page data). Rust 1.008 and D/ldc2 1.078 are also ahead of C++/g++, while Zig 1.327, Nim/gcc 1.171 and V/clang 1.846 are slower. On mandel.b the C++/g++ row (10.143 s) beats V/gcc (17.865 s). |
| **Workload** | Brainfuck interpreter running bench.b, the suite's first brainfuck sample; the same interpreter design (op tree, tape vector) ported to each language. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E-2324G, Debian forky/sid Docker image, README updated 2026-07-19 |
| **Compiler and flags** | V 0.5.2 `v -prod -no-bounds-checking -prealloc` with the suite's COMMON_FLAGS (-O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries) passed through -cflags; V's builder/cc.v additionally adds -O3 -flto -fno-strict-aliasing -fwrapv -DNDEBUG for gcc -prod, which the hand-written C and C++ builds do not get (enricher correction) |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Adoption** | 2.9k stars (suite repo) |
| **Last commit** | 2026-07-19 |
| **Links** | [repository](https://github.com/kostya/benchmarks) · [benchmark](https://raw.githubusercontent.com/kostya/benchmarks/master/README.md) |

## Verdict

kostya/benchmarks (README UPDATE 2026-07-19, Intel Xeon E-2324G, median of 10 runs, MAD 0.001-0.002 s): bf.v built by V 0.5.2 with -prod -no-bounds-checking -prealloc through gcc 16.1.0 (-O3 -march=native -flto=auto) ran bench.b in 0.985 s. C++/g++ 16.1.0 with libstdc++ and the same suite flags took 1.097 s, so V/gcc is about 1.11x faster (derived from page data); C/gcc took 1.112 s and C++/clang++ (libc++) 1.167 s. On mandel.b the order reverses: V/gcc 17.865 s vs C++/g++ 10.143 s.

## Use it when

- As a data point when choosing V for interpreter-style code: through gcc with -prod, V's output matched or beat hand-written C and C++ on one small dispatch-bound loop (bench.b 0.985 s vs C++/g++ 1.097 s and C/gcc 1.112 s).
- If you already ship V: build with -cc gcc rather than clang for this kind of code (0.985 s vs 1.846 s on the same source).
- Small-footprint batch tools: 2.12 MiB resident against 3.38 MiB for the C++ interpreter, and 41.65 J against 46.21 J.
- Short-lived, single-threaded batch programs where the -prealloc arena (no GC, memory never freed) is acceptable.

## Skip it when

- As a general claim that V beats C++: on the suite's other program, mandel.b, V/gcc takes 17.865 s against 10.143 s for C++/g++ (C++ 1.76x faster), and it also trails C/gcc 12.544 s, Rust 14.460 s and Go 14.540 s.
- With the clang backend: V/clang 1.846 s on bench.b is slower than every C and C++ row (C++/clang++ 1.167 s).
- When you need V's safety defaults: the row was measured with -no-bounds-checking and -prealloc, and per vlib/v/pref, -prealloc switches the build to no GC (gc_mode .no_gc) with a bump-pointer arena.
- Long-running or multi-threaded services: V's docs say -prealloc 'is only suitable to speed up short lived, single-threaded, batch-like programs (like compilers)'.
- Decisions that hinge on a 10% margin: it rests on a single 220-byte program on one machine, and the backend alone moves the same V source by 1.87x.

## How it is fast

Not documented: the README, the source and the commit history give no mechanism, and nothing was built here to check one. The algorithm is the same as bf.cpp, so the gap comes from the C that V hands to gcc and from the extra flags. Untested source-level differences: (1) by V 0.5.2's match.v, a match inside a loop is emitted as an if/else-if chain (tested in the order inc, move, print, loop) rather than a C switch; (2) V -prod on gcc adds -fno-strict-aliasing, -fwrapv and -DNDEBUG on top of the suite flags; (3) V emits the program and its builtins as one C translation unit. Because the same V source runs 1.87x slower through clang (1.846 s) and 1.76x slower than C++ on mandel.b, the bench.b lead looks like a code-generation and layout effect specific to one input and one backend, not a property of the language.

## Compared with alternatives

The catalogued Rust bench.b sibling shows the same roughly 10% lead (1.008 s vs 1.097 s) without a C backend in between, and like V it loses on mandel.b (Rust 14.460 s, V 17.865 s, C++/g++ 10.143 s); prefer the Rust entry as the more robust data point and use this one only if you already write V. For an other-language win over C or C++ that holds beyond one input, the category's ipnsort/driftsort or fd entries carry broader evidence.

## Integration

| | |
|---|---|
| **Form** | source-drop (one V file, brainfuck/bf.v) |
| **Dependencies** | V toolchain plus a C compiler; only vlib os and net (net carries the harness notification) |
| **Minimum toolchain** | V 0.5.2 (7647ce1) and gcc 16.1.0 as measured; flags -prod -no-bounds-checking -prealloc -cc gcc plus -cflags with -O3 -march=native -flto=auto |
| **Platforms** | x86-64 Linux as measured (-march=native, Xeon E-2324G); other targets not tested |
| **Thread safety** | not documented; the program is single-threaded, and V's docs restrict -prealloc to single-threaded batch programs |
| **Drop-in for the baseline** | no |

## Gotchas

- The flags are not identical. V 0.5.2's builder/cc.v adds its own -O3 -flto -fno-strict-aliasing for gcc -prod, plus -fwrapv on Linux and -DNDEBUG, on top of the suite's COMMON_FLAGS. The C++ build has none of these extras, so 'same flags' holds for -O3, -march=native and LTO only.
- Data layout differs. A V Op is two 32-bit ints plus a 32-byte array header (about 40 bytes), and `for op in ops` copies it by value each iteration (V's for.v emits `Op op = ((Op*)ops.data)[i]`). C++ reads a 32-byte Op by const reference, and C uses a 16-byte tagged union. The V tape grows one element per append (`t.tape << 0`), while C++ doubles with resize. None of these differences was measured in isolation.
- The harness does not validate output. xtime.rb and analyze.rb record time, memory and energy only, and nothing compares the printed 'Output checksum' with an expected value; the built-in Hello World self-check is the only correctness guard. The V Printer truncates each cell to u8 before checksumming, where C++ uses the int value; this is equivalent for byte-range output.
- The README Versions table is partly stale (Java 24.0.2, Crystal 1.17.1, Julia 1.11.6, while the Dockerfile of the same commit 5bc68b3 has OpenJDK 26.0.1, Crystal 1.21.0 and Julia 1.12.6), and the README says measurements are taken 'semi-manually'. V 0.5.2, gcc 16 and clang 22 do match the Dockerfile.

## Known shortcomings

- Code, gcc 16.1.0, commands.mk flags and the Xeon E-2324G are public but no mechanism is stated (V is generated C compiled by the same gcc); loses on mandel.b (C++/g++ 1.76x faster) and with V/clang.
- The JSON3.jl enricher found that kostya/benchmarks' 2026-07-19 update re-measured only the Primes table and the environment table: the Json table rows kept their 2025-08-17 values (gcc 14.2.0, clang 19.1.7), so the compiler versions recorded here (gcc 16.1.0, clang 22.1.8) describe the current environment table and may not be the toolchain behind this table's rows; whether this table was re-run on 2026-07-19 was not checked.
- Flags are not identical: V 0.5.2's builder/cc.v adds -fno-strict-aliasing, -fwrapv and -DNDEBUG on gcc -prod on top of the suite's COMMON_FLAGS, and -prealloc sets no GC (pref.v). The mechanism is still unknown (no build): the match inside the loop becomes an if/else-if chain rather than a switch (match.v), and the Op is copied by value per iteration (about 40 B vs 32 B in C++). V/clang takes 1.846 s and mandel.b 17.865 s vs 10.143 s, so the win looks backend and layout specific. The README Versions table is partly stale (Java 24.0.2 vs OpenJDK 26.0.1 in the Dockerfile at the same commit).

## Caveats and trade-offs

Capped at tier C because the source states no mechanism. V compiles to C, so the V/gcc row is GCC 16.1.0 compiling V-generated C with the same COMMON_FLAGS as the hand-written C and C++. The roughly 10% lead is therefore a difference between two C-level programs, not between compilers, and V adds -prealloc (arena allocator) and -no-bounds-checking. The three programs share the op-tree design but differ in detail: the V Op carries a full []Op array header, the C op is a 16-byte tagged union with a tape_get that returns char, and C++ uses std::vector&lt;Op&gt; with a resize-doubling tape. Only the gcc backend wins: V/clang is 1.846 s, slower than every C and C++ row. On the suite's other brainfuck sample, mandel.b, V/gcc takes 17.865 s against C++/g++ 10.143 s (C++ 1.76x faster, derived from page data), so the bench.b result does not generalise. Single machine (Xeon E-2324G), medians with MAD of about 0.001-0.002 s. [retier] Enricher: the flags are not identical; V 0.5.2's builder/cc.v adds -fno-strict-aliasing, -fwrapv and -DNDEBUG on gcc -prod on top of COMMON_FLAGS, and -prealloc sets no GC. The match inside the loop becomes an if/else-if chain rather than a switch (match.v), and the Op is copied by value per iteration (about 40 B vs 32 B in C++). V/clang takes 1.846 s and mandel.b 17.865 s vs 10.143 s, so the win is backend and layout specific.

V emits C that gcc compiles, so this reflects V's generated code through the gcc backend; with -no-bounds-checking and -prealloc the safety defaults are off.

## Maintenance

The suite is active (MIT, 2.9k stars, last update 2026-07-19). bf.v last changed on 2024-11-14 (97a820b, PR #495) in nuald's maintenance passes. It is a copyable reference port, not a library. The C tier (no mechanism) stands, and the mandel.b and clang reversals argue against reading it as a V-over-C++ result.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README bench.b table shows V/gcc 0.985 s against C++/g++ 1.097 s and C/gcc 1.112 s. The suite is public, with code (brainfuck/bf.v, bf.cpp, bf.c), compilers (gcc/g++ 16.1.0, clang 22.1.8, V 0.5.2), flags (common/commands.mk) and CPU (Xeon E-2324G) all stated, so it would otherwise reach A. Spec Part 4 caps a language-level claim with no stated mechanism at C, and neither the README nor the sources say why V wins.
- **Verifier notes:** Numbers, flags, versions and CPU match the README (UPDATE 2026-07-19) and common/commands.mk; both sides use equal -O3 -march=native -flto=auto flags, so same_opt_level=true and same_algorithm=true (the same op-tree interpreter, with minor data-layout differences) hold. Confirmed at C under the spec's no-mechanism cap; the record would be A if a mechanism were shown. Shortcomings to record: no mechanism, V is C compiled by the same gcc, the win reverses on mandel.b (C++/g++ 1.76x faster) and with the clang backend. Metadata checked: MIT, 2.9k stars, last commit 2026-07-19.
- **Fields the verifier corrected:** `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** verifier batch-89 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.v>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.c>
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits/master>
- **Sources the enricher read:**
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits/master/brainfuck/bf.v>
  - <https://github.com/kostya/benchmarks/commits/master/docker/Dockerfile>
  - <https://github.com/kostya/benchmarks/pull/516>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/xtime.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/analyze.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/repeat.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/run.sh>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.v>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bench.b>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/mandel.b>
  - <https://raw.githubusercontent.com/vlang/v/0.5.2/vlib/v/builder/cc.v>
  - <https://raw.githubusercontent.com/vlang/v/0.5.2/vlib/v/gen/c/match.v>
  - <https://raw.githubusercontent.com/vlang/v/0.5.2/vlib/v/gen/c/for.v>
  - <https://raw.githubusercontent.com/vlang/v/0.5.2/vlib/v/pref/pref.v>
  - <https://raw.githubusercontent.com/vlang/v/0.5.2/vlib/v/pref/default.v>
  - <https://raw.githubusercontent.com/vlang/v/0.5.2/vlib/builtin/prealloc.c.v>
  - <https://raw.githubusercontent.com/vlang/v/0.5.2/vlib/builtin/array.v>
  - <https://raw.githubusercontent.com/vlang/v/0.5.2/doc/docs.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:v/kostya/benchmarks#brainfuck-bench-b`) · [data/wave14/enrich/raw/lang_v_kostya_benchmarks_brainfuck_bench_b.json](../../../data/wave14/enrich/raw/lang_v_kostya_benchmarks_brainfuck_bench_b.json) (enrichment confidence 0.62)

</details>
