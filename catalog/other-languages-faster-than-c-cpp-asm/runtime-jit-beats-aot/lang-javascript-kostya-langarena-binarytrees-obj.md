# Bun (JavaScriptCore JIT): LangArena Binarytrees::Obj

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `TypeScript/JavaScript` · `MIT` · 🟢 active

> Bun 1.4.2 builds and sums depth-20 object trees 2.2x faster than make_unique C++: an allocator and GC effect.

| | |
|---|---|
| **Beats** | C++ (std::make_unique tree nodes, g++ 16 and clang++ 22) and C (malloc'd nodes); best of the 16 Clang/GCC C/C++ configurations is C++/G++/Fast at 2.098 s |
| **Claimed result** | TypeScript/Bun/JIT 0.973 s and JS/Bun/JIT 1.042 s vs C++/G++ 2.101 s (prod, -O2) and 2.098 s for the best of all 16 C/C++ configurations: about 2.2x and 2.0x faster (derived from page data). Peak RSS about 647 MB for Bun vs about 66 MB for C/Clang. |
| **Workload** | Binarytrees::Obj with depth 20 (a 2^21-1 node tree of individually allocated nodes), built, summed (uint32 checksum 75497436) and, in C/C++, freed per iteration; 30 timed iterations after a warm-up of 20% of the iterations (6), which every language including C/C++ runs. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++: GCC 16.0.1 20260322 (trunk, Ubuntu build) and Clang 22.1.8. Headline 'prod' build is -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer; 'Fast' is -O3 -march=native -mtune=native -DNDEBUG with -flto=thin; 'Unsafe' is -O3 -ffast-math -march=native with -flto=full; 'PGO' builds are -O2 plus profile use (cpp/Makefile, c/Makefile). Excluding the instrumented PGO/Gen runs, all 16 Clang/GCC x C/C++ configurations lose to Bun. Bun 1.4.2 (results file), run as 'bun run /src/typescript/src/index.ts' and 'bun run /src/javascript/index.js', default JIT settings. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated in prose. The suite's own Binarytrees::Arena control (index-based arena, same tree) reverses the result in C/C++, which points at per-node make_unique/malloc cost versus JavaScriptCore's bump allocation and generational GC (agent inference). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

LangArena's 2026-10-05 run on an AMD Ryzen 7 3800X (Linux, Docker) timed 30 depth-20 build-and-sum iterations at 0.973 s for TypeScript/Bun/JIT and 1.042 s for JS/Bun/JIT (Bun 1.4.2), against 2.101 s for C++/G++ (GCC 16.0.1 trunk, -O2 with hardening flags, std::make_unique nodes, glibc malloc), 2.098 s for the best C/C++ configuration (C++/G++/Fast, -O3 -march=native, thin LTO) and 2.482 s for C/Clang 22.1.8: about 2.2x and 2.0x faster (derived from page data).

## Use it when

- Bun services or scripts that build and discard large pointer-linked structures (ASTs, parse trees, document object graphs) per request and are judged on throughput: idiomatic class-per-node code beat idiomatic make_unique C++ by about 2.2x here.
- Choosing a JavaScript runtime for allocation-heavy code: on this test Bun (0.973 s) is about 3.4x faster than Node 26.10 (3.355 s) and Deno (3.21-3.30 s) running the same source.
- Hosts with idle cores and memory headroom, which JavaScriptCore's parallel, mostly concurrent marking and its roughly 650 MB peak heap can use.
- Deciding whether to port such code to C or C++: this result says per-node new/delete through glibc malloc will likely be slower unless the port uses an arena or pool.

## Skip it when

- As evidence that a JIT beats ahead-of-time compilation: AOT Rust compiled to WebAssembly (0.993 s), V/GCC/Perf (0.905 s), Nim/GCC/ARC (1.193 s) and Go/Opt (1.303 s) also beat every C and C++ build, while V8 runs the identical JavaScript at 3.35 s; the C/C++ rows lose to their per-node allocation, not to Bun's code generation.
- Against arena-allocated C or C++: the suite's C index arena grown by realloc (C/Gcc/Fast 0.255 s, 27 MB) is about 3.8x faster than Bun's object tree, and the C++ std::vector arena (0.512-0.685 s) also beats it.
- Memory-constrained deployments: peak RSS was 647.5 MB for TypeScript/Bun against 69.5 MB for C++/G++/Fast and 66.4 MB for C/Clang (about 9-10x).
- Containers with a CPU quota of one core (agent inference): the measured runs had no CPU limit, so JavaScriptCore's GC helper threads could use the other cores of the 8-core CPU while the C/C++ programs ran on one; no single-threaded-GC Bun configuration was measured.
- Other tree representations in JavaScript: Bun's 'arena' variant (an array of per-node objects) is slower, at 1.553 s and 1.28 GB.

## How it is fast

Allocation and reclamation, not JIT code quality. Bun runs JavaScriptCore, whose Riptide collector is non-moving, generational through sticky mark bits, and marks in parallel on up to eight logical CPUs, mostly concurrently with the program (WebKit's Riptide description, read through search snippets), so a dead tree is never traced; the C and C++ versions call malloc or operator new per node and walk the whole tree to free or delete it inside the timer. That works out to about 15.5 ns per node for TypeScript/Bun against 33.4 ns for the best C++ build and 39.5 ns for C/Clang (derived from page data over 62.9M timed nodes). The suite's own controls point at the native allocator rather than at JIT versus AOT: Node 26.10 and Deno run the same JavaScript in 3.21-3.36 s, slower than every C++ build, while the suite's Rust code compiled ahead of time to wasm32-wasip1 and run under Node takes 0.993 s, matching Bun and 2.4x faster than the best native Rust build (2.423 s); 32-bit wasm pointers and a linear-memory allocator versus glibc malloc with 64-bit pointers is the likely difference (agent inference, not measured).

## Compared with alternatives

Among catalogued Binarytrees::Obj rows, HotSpot (0.479 s, the Java entry) is about 2x faster than Bun, so pick Bun only when the code already lives in JavaScript. Against the benchLANG Bun entry (1.24x over C) and the alya-lang Bun entry (1.28x over gcc -O2), this is the strongest Bun binary-trees evidence because it beats 16 C/C++ build configurations and carries Node, Deno and Rust-to-WebAssembly controls on the same machine.

## Integration

| | |
|---|---|
| **Form** | source-drop (the TreeNodeObj class in typescript/src/index.ts or javascript/index.js; nothing links into a C++ program) |
| **Dependencies** | Bun runtime only (1.4.2 as measured); the tree code uses no packages |
| **Minimum toolchain** | Bun 1.4.2 as measured with default flags ('bun run /src/typescript/src/index.ts'); TypeScript/Bun/Compiled (bun build --target=bun) lands at 0.983 s; older Bun versions are not in this results file |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X, 78 GB RAM) inside Docker with a 16 GB memory limit and no CPU limit |
| **Thread safety** | Not applicable: single-threaded workload; JavaScriptCore's GC threads run beside it |
| **Drop-in for the baseline** | no |

## Gotchas

- Parallel GC work is in the wall time but not in the table: benchmarks.rb wraps every run in /usr/bin/time and parses user and system time, but the results file keeps only wall time and peak RSS per test, and docker-compose.yaml sets no CPU limit. Riptide marks on up to eight logical CPUs, so part of Bun's collection cost can run on other cores; for HotSpot the suite's single-threaded SerialGC row cut the margin over C++ from 4.4x to 2.4x, and Bun has no equivalent control row.
- The record's caveat that the harness calls global.gc() after stopping the timer needs refining: Bun's CLI docs list --expose-gc as the flag that exposes gc() on the global object, and the Bun run command passes no flags, so the guarded call most likely does nothing. No explicit collection happens anywhere: warm-up garbage is not cleared before timing, and garbage from the last timed iterations is never collected inside the timer, while C and C++ free every node inside each timed iteration.
- The record's arena comparison needs care: TypeScript's Binarytrees::Arena pushes one {item, left, right} object per node into a growing array, so its 1.553 s is not an arena result. Like for like, the C realloc arena (0.255 s) beats Bun's object tree (0.973 s) by about 3.8x.
- One self-timed measurement per configuration (performance.now() around runAll in TypeScript, steady_clock in C++), with no repeats or variance; the test was selected because a Bun row beats every C/C++ row. Each language's checksum (75497436) is checked, and the C/C++ -O3, LTO, fast-math and PGO builds land between 2.098 and 2.548 s, so the baseline is not crippled by flags.

## Known shortcomings

- Bun 1.4.2 TypeScript harness calls global.gc() after the timer while C and C++ free inside it; the suite's own Arena control reverses the result (C 0.255 s vs Bun 1.553 s); production C/C++ rows are -O2 but the -O3, LTO and PGO builds lose too.
- The win is an allocator and garbage-collector effect, not a JIT one: Node 26.10 (3.355 s) and Deno (3.21-3.30 s) are slower than every C++ build on the same tree, while AOT Rust compiled to wasm32-wasip1 and run under Node (0.993 s) matches Bun, and V (0.905 s), Nim ARC (1.193 s) and Go (1.303 s) also beat C and C++. docker-compose sets no CPU limit and JavaScriptCore's Riptide marks in parallel, the parsed user and system times are not saved, there is no single-threaded-GC Bun control row, the harness's global.gc() is probably a no-op without --expose-gc, and the suite's TypeScript 'Arena' variant is not an arena. The C arena variant (0.255 s) beats Bun by 3.8x.

## Caveats and trade-offs

The win is allocation-strategy specific: in the suite's own Binarytrees::Arena control (index-based arena, same tree) C/Gcc/Fast takes 0.255 s against TypeScript/Bun/JIT 1.553 s, about 6x the other way (derived from page data). The TypeScript harness stops the timer and only then calls global.gc(); garbage from the last trees can be collected outside the timed region, while C frees each tree explicitly and C++ destroys it through unique_ptr destructors inside the timer, and Bun's peak RSS of about 647 MB (vs about 66-70 MB for C/C++) shows several trees' garbage live at once. LangArena calls itself not objective or peer-reviewed and the author says AI tools helped translate the tests. One published measurement per test and configuration (no variance). The headline C/C++ rows are -O2 with hardening flags, but the -O3, LTO, PGO and fast-math variants lose too. The C rows (2.34-2.55 s) are slower than the C++ rows (2.10-2.34 s). Row selected by the search agent as a test where a Bun row beats every C/C++ row; Java/OpenJDK (0.479 s), Kotlin and Scala are faster still and are covered by a separate Java entry. [retier] Enricher: the win is an allocator and GC effect, not a JIT one (Node 26.10 3.355 s and Deno 3.21-3.30 s are slower than every C++ build; AOT Rust as wasm32-wasip1 under Node 0.993 s matches Bun; V 0.905 s, Nim ARC 1.193 s and Go 1.303 s also beat C and C++). docker-compose sets no CPU limit and JavaScriptCore's Riptide marks in parallel, user and system times are parsed but not saved, there is no single-threaded-GC Bun control row, global.gc() is probably a no-op without --expose-gc, and the suite's TypeScript 'Arena' variant is per-node objects in an array, not an arena; the C arena variant (0.255 s) beats Bun by 3.8x.

About 10x the peak memory of the C/C++ versions; needs the Bun runtime.

## Maintenance

Actively maintained MIT suite (last commit 2026-10-08, monthly reruns, 41 stars) with public code, flags and per-configuration results; the tree class is trivial to copy, but the speedup is a property of Bun's runtime that depends on its version and on spare cores, and the author calls the suite subjective, with AI-assisted translations reviewed by hand.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** results/2026-10-05-kostya-ms7c37.js lists Binarytrees::Obj runtimes TypeScript/Bun/JIT 0.973 s, JS/Bun/JIT 1.042 s, C++/G++ 2.101 s, C++/G++/Fast 2.098 s and every C row 2.34-2.55 s on an AMD Ryzen 7 3800X, with compiler versions (GCC 16.0.1 trunk, Clang 22.1.8, Bun 1.4.2) and build commands; the code (cpp/src/binarytrees.cpp, c/src/binarytrees.c, typescript/src/index.ts) and Makefile flags are public.
- **Verifier notes:** All quoted numbers match the 2026-10-05 results file; Bun version is 1.4.2 (not stated in the record). C, C++ and TypeScript implement the same recursive tree build and sum with one allocation per node, so same_algorithm holds; the gain is per-node malloc/free versus JavaScriptCore's bump allocation and GC, and part of the GC cost can fall after the timer while C/C++ free inside it.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/tree/master/cpp>
  - <https://github.com/kostya/LangArena/tree/master/cpp/src>
  - <https://github.com/kostya/LangArena/tree/master/c/src>
  - <https://github.com/kostya/LangArena/tree/master/typescript/src>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/binarytrees.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/binarytrees.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/binarytrees.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/typescript/src/index.ts>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/run.js>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue%20bun>
  - <https://github.com/kostya/LangArena/tree/master/typescript/src>
  - <https://github.com/kostya/LangArena/tree/master/javascript>
  - <https://github.com/kostya/LangArena/tree/master/rust/src>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/test.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker-compose.yaml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/typescript/src/index.ts>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/typescript/package.json>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/typescript/tsconfig.json>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/javascript/index.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/javascript/run>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/binarytrees.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/binarytrees.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/binarytrees.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - https://bun.com/docs/cli/run (WebSearch snippet only)
  - https://webkit.org/blog/7122/ (WebSearch snippet only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:javascript/kostya/langarena#binarytrees-obj`) · [data/wave14/enrich/raw/lang_javascript_kostya_langarena_binarytrees_obj.json](../../../data/wave14/enrich/raw/lang_javascript_kostya_langarena_binarytrees_obj.json) (enrichment confidence 0.75)

</details>
