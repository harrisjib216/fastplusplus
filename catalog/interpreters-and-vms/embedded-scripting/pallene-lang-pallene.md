# Pallene

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Lua (compiler) emitting C` · `MIT` · 🟢 active

> Typed Lua dialect compiled ahead of time to C Lua modules; about 12x faster than Lua 5.4 on an integer n-queens loop.

| | |
|---|---|
| **Beats** | PUC-Rio Lua 5.4 interpreter (the Lua 5.4 bundled with Pallene in 2020); LuaJIT and C in the same post |
| **Claimed result** | Klausmeier blog (2020): n-queens Pallene 0.32 s (0.31 s with compiler optimization flags) vs Lua 5.4 3.92 s (about 12x, derived from page data; the post says 13x) and vs LuaJIT 0.58 s (about 1.8x, derived from page data), C -O3 0.2 s; array loop Pallene 0.14 s vs Lua 5.4 0.72 s (about 5x, derived from page data), but LuaJIT 0.07 s is 2x faster than Pallene there. Paper (SBLP 2018 / SCP 2020, search snippets only): around ten times faster than Lua on Sieve and Queens, comparable to LuaJIT; more than three times faster than LuaJIT and the Lua-C API on binary search; LuaJIT substantially faster only on Matmul (NaN-boxing gives 8-byte floats vs 16 bytes in Lua and Pallene). |
| **Workload** | Independent blog: n-queens counter xdamcnt2 (N up to 12, non-recursive, code in github.com/eklausme/c) and an array-of-records float update loop (N=4000, S=1000), each in Pallene, Lua and C. Paper (snippet only): binarytrees, binsearch, centroid, conway, matmul, queen, sieve and others from the repo benchmarks directory. |
| **Metric** | throughput |
| **Hardware** | AMD FX-8120 eight-core, 3.1 GHz max (blog); paper hardware unknown |
| **Compiler and flags** | gcc 9.3.0 on Arch Linux 5.6.6; the C reference built with -march=native -O3; Pallene and Lua 5.4 build flags not stated (a second Pallene run 'with compiler optimization flags' does not name them) |
| **Adoption** | 839 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/pallene-lang/pallene) · [benchmark](https://eklausmeier.goip.de/blog/2020/05-14-performance-comparison-pallene-vs-lua-5-1-5-2-5-3-5-4-vs-c) |

## Verdict

Elmar Klausmeier's independent 2020 post (AMD FX-8120, Arch Linux, gcc 9.3.0) timed n-queens counting for N=1..12 at 0.32 s in Pallene vs 3.92 s in Pallene's bundled Lua 5.4 (about 12x), 0.58 s in LuaJIT and 0.2 s in C at -O3, and an array-of-records float loop (N=4000, S=1000) at 0.14 s vs 0.72 s for Lua 5.4 (about 5x) but 0.07 s for LuaJIT (ratios derived from page data). Single runs with a 2020 Pallene; Pallene and Lua build flags are not stated, and the peer-reviewed paper numbers were only visible as snippets.

## Use it when

- A Lua 5.4 host (game, tool, server) where you build and ship the interpreter yourself and need a few integer- or loop-heavy functions about 5-12x faster without writing Lua-C API code.
- Replacing hand-written C modules whose main cost is marshalling through the Lua-C API, since Pallene manipulates Lua tables directly.
- Projects that must stay on PUC-Rio Lua 5.4 semantics (64-bit integers, 5.4 syntax) where LuaJIT is not an option.
- Code you want to keep runnable as plain Lua: removing the types gives the same program, and --emit-lua automates it.

## Skip it when

- Hosts that run stock system Lua, LuaJIT or any Lua other than the bundled 5.4.7 build: generated modules call internal Lua symbols that only Pallene's patched build exports.
- Float-array or record-array numeric kernels: on the independent array-of-records loop LuaJIT took 0.07 s vs 0.14 s for Pallene, and the paper reports LuaJIT substantially faster on Matmul.
- String-heavy code or code that leans on the standard library: an open issue reports slow string performance (#505), and only string.char, string.sub and a set of float-only math functions are compiled builtins.
- Hosts that run several Lua states, especially across threads (Lua Lanes): generated code uses function-level 'static int cache' slots, flagged as a possible multi-VM problem in open issue #552 with no maintainer reply.
- Production code where a crash is unacceptable: open bug reports include a segfault with disappearing array elements that does not occur under --emit-lua (#507, 2021), a LUAI_ASSERT crash (#562) and undetected uninitialised variables (#650).

## How it is fast

Static types let the compiler keep integers and floats unboxed in C locals and read and write table array parts and fields directly through Lua's internal data structures instead of the stack-based Lua-C API, with run-time type checks only where a value enters from Lua or from an untyped container. The generated C is then optimised by the system C compiler (CFLAGS are honoured). Per the SBLP 2018 / SCP 2020 paper (quoted in the benchmark post) Pallene keeps Lua's 16-byte tagged values, so LuaJIT's 8-byte NaN-boxed floats still win on float-array code such as Matmul.

## Compared with alternatives

Pick Pallene when you are staying inside a Lua 5.4 program and want typed hot functions that work on ordinary Lua tables; pick a faster VM such as LuaJIT Remake (Deegen, a Lua 5.1 interpreter about 185% faster than PUC Lua 5.1 per its README) when you want every script sped up without rewriting, and Daslang or Terra when the hot code can live in a separate statically typed language rather than in typed Lua.

## Integration

| | |
|---|---|
| **Form** | compiler (pallenec) that emits C and builds .so Lua extension modules |
| **Dependencies** | A C compiler; Pallene's bundled Lua 5.4.7 built with its expose-internal-apis patch (installed as plua/pluac and the pallene-lua launcher); lpeg, argparse and pallene-tracer, all built and installed by make install |
| **Minimum toolchain** | C99 compiler (the dev build script uses -std=c99); Lua 5.4.7 exactly |
| **Platforms** | Unix-like systems producing .so modules; other platforms not documented (open issue #516 asks for a cross-platform replacement for c_compiler.lua) |
| **Thread safety** | not documented; generated modules keep function-level static lookup caches (issue #552) |
| **Drop-in for the baseline** | no |

## Gotchas

- Modules load only in Pallene's own Lua: the build applies deps/lua/patches/expose-internal-apis.patch to Lua 5.4.7, which exports the internal LUAI_FUNC symbols, adds luaL_checkcoreversion (it errors on any other release number) and luaV_strcmp, and the manual says Pallene 'is only compatible with a specific release version of the interpreter'. The blog's 'Lua 5.4' baseline is this bundled interpreter.
- Harness notes on the Klausmeier post: each figure is a single run timed with the shell's time command; the Lua baseline xdamcnt2.lua defines configOkay and solve as globals, so every hot call in PUC Lua pays a global-table lookup that Pallene's direct C call avoids, which favours Pallene somewhat; the Pallene driver, the C array program and all Pallene/Lua build flags are unpublished; the post's own figures are slightly inconsistent (text says Lua 5.4 took 0.75 s on the array loop, its table says 0.72 s; 3.92 s / 0.32 s is 12.25x, not the 13x stated).
- Typing is strict at run time: integer and float are distinct (local x: float = 0 is a type error), arrays cannot hold nil, reading a missing element of a typed array raises a run-time error instead of returning nil, and the math builtins reject integer arguments.
- Speed depends on how the generated C reaches GCC: issue #651 reports a 36% matmul slowdown with GCC 15.1.1 -O3 from merely moving a CheckGC() call, and issue #564 says Pallene's loop checks block C compiler optimisations.

## Known shortcomings

- Upgraded C to B on Elmar Klausmeier's independent 2020 post (eklausme/c code, AMD FX-8120, gcc 9.3.0: n-queens 0.32 s vs Lua 5.4 3.92 s; array loop 0.14 vs 0.72 s) where LuaJIT is still 2x faster on the array loop; flags unstated, 2020 version, the SBLP and SCP paper numbers are snippet only (PUC-Rio hosts blocked). Typed Lua subset compiled ahead of time.
- Enricher: modules load only in Pallene's patched Lua 5.4.7 (the patch exports internal symbols and adds a version check), so they fail on stock Lua and LuaJIT. The Klausmeier harness is single 'time' runs with the Lua baseline's hot functions defined as globals (favours Pallene), the Pallene driver and build flags are unpublished, and the post's numbers are slightly inconsistent (0.75 vs 0.72 s; '13x' where 3.92/0.32 gives 12.25x). Open bugs: segfault #507, LUAI_ASSERT crash #562, static cache shared across Lua states #552, 36% matmul codegen slowdown #651.

## Caveats and trade-offs

Independent numbers are from one 2020 blog post on two small programs with a 2020 Pallene (older syntax) and an AMD FX-8120; Pallene and Lua flags unstated. LuaJIT beats Pallene 2x on the array-of-records loop and, per the paper snippets, on Matmul. The peer-reviewed papers (inf.puc-rio.br, ScienceDirect, ReadKong mirror) and the 2020 PhD thesis are EGRESS_BLOCKED here, so paper numbers are snippet only. The README gives no figures and the repo benchmarks directory has code (benchmarks/run, benchlib.lua) but no results. Pallene is a Lua companion language compiled to C Lua modules, not a C/C++ library.

Statically typed, ahead-of-time compiled sister language of Lua (README); output is a C extension module, so a C compiler is needed at build time and the code is loaded through require; it is a companion for hot paths, not a replacement interpreter.

## Maintenance

Actively developed research compiler (described in PUC-Rio papers) (last commit 2026-09-30, new issues filed in October 2026), MIT-licensed and installed from source with make install; maintainers enforce a strict no-LLM/no-AI contribution policy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B: an independent measurement by Elmar Klausmeier (blog post of 14 May 2020, read via its GitHub Pages source eklausme/eklausme.github.io) times Pallene against Lua 5.4, Lua 5.1-5.3, LuaJIT and C on an AMD FX-8120 with gcc 9.3.0, with the n-queens code public in eklausme/c (xdamcnt2.pln/.lua/.c) and the array program inline; not A because Pallene and Lua build flags are not stated. The peer-reviewed SBLP 2018 / SCP 2020 papers also report the win but could only be seen as search snippets.
- **Verifier notes:** Upgrade to B on the Klausmeier independent measurement (blog mirror at raw.githubusercontent.com/eklausme/eklausme.github.io, code in eklausme/c). Shortcomings to record: LuaJIT faster on array loop and Matmul, flags unstated, 2020 version, paper numbers snippet only. Metadata (839 stars, MIT, last commit 2026-09-30) confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pallene-lang/pallene>
  - <https://github.com/pallene-lang/pallene/commits/master>
  - <https://github.com/pallene-lang/pallene/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/benchmarks/run>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/README.md>
  - <https://github.com/orgs/pallene-lang/repositories>
  - <https://github.com/eklausme/eklausme.github.io>
  - <https://raw.githubusercontent.com/eklausme/eklausme.github.io/HEAD/blog/2020/05-14-performance-comparison-pallene-vs-lua-5-1-5-2-5-3-5-4-vs-c/index.html>
  - <https://raw.githubusercontent.com/eklausme/c/master/xdamcnt2.pln>
  - <https://raw.githubusercontent.com/eklausme/c/master/xdamcnt2.lua>
  - <https://raw.githubusercontent.com/eklausme/c/master/xdamcnt2.c>
- **Sources the enricher read:**
  - <https://github.com/pallene-lang/pallene>
  - <https://github.com/pallene-lang/pallene/commits/master>
  - <https://github.com/pallene-lang/pallene/commit/622c5c1>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/README.md>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/doc/manual.md>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/Makefile>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/configure>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/build>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/benchmarks/run>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/benchmarks/benchlib.lua>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/deps/lua/upstream/src/lua.h>
  - <https://raw.githubusercontent.com/pallene-lang/pallene/HEAD/deps/lua/patches/expose-internal-apis.patch>
  - <https://github.com/pallene-lang/pallene/issues>
  - <https://github.com/pallene-lang/pallene/issues/507>
  - <https://github.com/pallene-lang/pallene/issues/552>
  - <https://github.com/pallene-lang/pallene/issues/651>
  - <https://raw.githubusercontent.com/eklausme/eklausme.github.io/HEAD/blog/2020/05-14-performance-comparison-pallene-vs-lua-5-1-5-2-5-3-5-4-vs-c/index.html>
  - <https://github.com/eklausme/c>
  - <https://raw.githubusercontent.com/eklausme/c/master/xdamcnt2.pln>
  - <https://raw.githubusercontent.com/eklausme/c/master/xdamcnt2.lua>
  - <https://raw.githubusercontent.com/eklausme/c/master/xdamcnt2.c>
  - WebSearch results for '"Pallene: A companion language for Lua" pdf github' (paper links on inf.puc-rio.br, ScienceDirect, ReadKong; not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/pallene-lang/pallene`) · [data/wave12/enrich/raw/github_com_pallene_lang_pallene.json](../../../data/wave12/enrich/raw/github_com_pallene_lang_pallene.json) (enrichment confidence 0.75)

</details>
