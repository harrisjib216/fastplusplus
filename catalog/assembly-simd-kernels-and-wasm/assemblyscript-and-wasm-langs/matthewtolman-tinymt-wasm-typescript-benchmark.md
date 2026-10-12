# tinymt-wasm-typescript-benchmark (minimal AssemblyScript TinyMT32)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Study only · `AssemblyScript` · `no license` · 🟢 active

> Benchmark repo: hand-scalarised AssemblyScript TinyMT32 beats a TypeScript port 1.25-1.42x on ints and Emscripten C++ slightly.

| | |
|---|---|
| **Beats** | TypeScript TinyMT32 running in V8 (Node 24.18.0) and C++ TinyMT32 compiled with Emscripten and embind |
| **Claimed result** | Ints x10: AssemblyScript 15,295,751 hz vs TypeScript 12,235,627 (1.25x, derived from page data). Ints x10,000: 21,602 vs 15,175 hz (1.42x, derived). Floats x10,000: AssemblyScript 20,544 hz vs TypeScript 235 hz (about 87x, inflated by per-call ArrayBuffer/DataView allocation in the TypeScript port). Size: minimal AssemblyScript 1,260 bytes (wasm plus JS glue) vs C++ 36,445 vs TypeScript 3,568. The C++/Emscripten rows (14,218,306 and 19,316 hz; 17,688 hz floats) and the README's 'native C++ is 2-4x faster than Wasm' rows are struck: src/cpp/main.cpp never calls seed() (a local 'uint32_t seed = 44983921329;' shadows the function), so the global TinyMT stays all-zero, a fixed point of next_state, and every native u32() returns 0 with the temper branch never taken. |
| **Workload** | TinyMT 32-bit pseudo random generator producing 10 to 10,000 integers or floats per call, four implementations (minimal AssemblyScript, AssemblyScript with arrays, C++ via Emscripten, TypeScript), run with vitest bench on Node 24.18.0; also output size. |
| **Metric** | throughput |
| **Compiler and flags** | AssemblyScript via asc ^0.28.20 with --optimizeLevel 3 --shrinkLevel 2 -b esm --enable simd --enable stringref --enable relaxed-simd --noAssert --converge (the Makefile's separate wasm-opt -O3 rule applies only to hand-written .wat files such as the unused main.wat demo, not to the asc output); C++ via em++ -O3 -Oz -lembind -std=c++20 (the later -Oz wins, so a size-optimised build); vitest bench on Node 24.18.0, TypeScript \~6.0.2; native comparison rows from clang++ -O3 -Oz -flto=thin with nanobench |
| **Adoption** | 0 stars, 5 commits |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark) · [benchmark](https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark) |

## Verdict

First-party vitest bench on Node 24.18.0 (CPU and OS not stated): minimal AssemblyScript 15.30M calls/s vs C++/Emscripten 14.22M vs TypeScript 12.24M at 10 ints per call (1.25x over TypeScript), 21,602 vs 19,316 vs 15,175 hz at 10,000 ints (1.42x); floats at 10,000 per call 20,544 vs 17,688 vs 234.66 hz, an 87x gap caused by the TypeScript port allocating an ArrayBuffer, Uint8Array and DataView per float. Native rows (clang++ -O3 -Oz with nanobench) come from an unseeded all-zero generator and are not comparable.

## Use it when

- As a worked example of how to write AssemblyScript that actually beats V8-JIT TypeScript: scalar locals and globals only, no Array, StaticArray or string.
- When you need a tiny (about 1.3 KB wasm plus glue) seeded TinyMT32 stream in a browser or Node and are willing to copy the pattern rather than the code (no licence).
- When choosing between AssemblyScript and Emscripten for small hot kernels and output size matters: 1,260 bytes vs 36,445 bytes for C++/embind here.
- When a TypeScript hot path converts integer bit patterns to floats through ArrayBuffer/DataView allocations; the float rows show what that allocation costs.

## Skip it when

- As a dependency: there is no licence file, no package and five commits, so it is reference material only.
- If your AssemblyScript code needs arrays or other stdlib types: the Array and StaticArray builds are 3.7-5.1x slower than TypeScript (2.70-3.23M vs 12.24M hz at 10 ints per call, derived from page data) and 4.6-5x larger.
- As proof that Wasm beats JavaScript generally: the integer win is 1.25-1.42x against a TypeScript port that keeps state in a number[] array, and the float win disappears if the TS port reuses one shared typed-array view instead of allocating per call.
- When you need multiple independent streams: state lives in module globals, so each generator needs its own Wasm instance.
- When native code is an option: the README's native rows are 2.4-3.4x faster than the best Wasm build, though see the gotcha on how they were measured.

## How it is fast

The fast build keeps TinyMT's 128-bit state in four u32 Wasm globals instead of an array, so nextState/temper compile to straight-line i32 ops with no linear-memory loads, bounds checks or runtime library, and the module is 591 bytes. Float output uses a single f32 reinterpret of the bit pattern (reinterpret&lt;f32&gt;) where the TypeScript port allocates an ArrayBuffer, Uint8Array and DataView per call, which is the whole source of the 44-87x float gap.

## Compared with alternatives

Pick it over xoroshiro128starstar (an AssemblyScript PRNG measured at about 1.10x Math.random) or superfasthash (about 1.21x over its JS twin) only as a teaching reference for what AssemblyScript style wins and loses, since it measures one algorithm across AssemblyScript, Emscripten C++ and TypeScript side by side; for a usable seeded PRNG package take a licensed sibling.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | AssemblyScript compiler (asc ^0.28.20) for the Wasm build; Emscripten for the C++ contender; vitest ^5 for the bench |
| **Minimum toolchain** | AssemblyScript 0.28 (asc), Node 24.18.0 as tested; C++20 for the C++ contender (std::bit_cast) |
| **Platforms** | any Wasm engine (Node, browsers); the build enables simd, relaxed-simd and stringref features although the generator uses none of them |
| **Thread safety** | Not thread-safe: one global state per Wasm instance; not documented |
| **Drop-in for the baseline** | partial: same seed/int/float shape and same output sequence as the TypeScript port (both pass the reference TinyMT vectors), but AssemblyScript int() returns a signed i32, so callers must apply &gt;&gt;&gt; 0 to get the unsigned value |

## Gotchas

- Harness flaw behind the native rows: src/cpp/main.cpp declares a local 'uint32_t seed = 44983921329;' that shadows the seed() function and never calls it, so the global TinyMT inst stays all-zero; that is a fixed point of next_state, so every native u32() returns 0 and f32() returns 0.0f. The README's 'native C++ is 2-4x faster than Wasm' rows therefore time a degenerate generator (temper branch always untaken), not the seeded workload the Wasm and TypeScript rows run. The native build also uses -O3 -Oz, so -Oz applies.
- Exported int() is typed i32, so roughly half of the outputs come back negative in JavaScript; the repo's own Wasm test needs int() &gt;&gt;&gt; 0 to match the reference values, while the TypeScript and C++/embind versions return unsigned numbers.
- Uneven contenders: the C++ build is size-optimised (em++ -O3 -Oz, last flag wins) and every call crosses an embind JS invoker plus an indirect call, while AssemblyScript exports are called directly; the TypeScript port stores its state in a number[] array while the winning AssemblyScript build uses four scalar globals (the array-based AssemblyScript builds lose to TypeScript 3.7-5.1x). The bench callbacks also discard return values, leaving V8 free to drop the TypeScript tempering step (not checked).
- The README's native x10,000 table prints 19,315.69 hz for AssemblyScript, which is the C++/Emscripten figure (AssemblyScript measured 21,602.44), and the committed C++ artifacts (tinymt.wasm 12,350 bytes, tinymt.js 25,519 bytes) do not match the size table (12,143 and 24,302).

## Known shortcomings

- No CPU or OS and no licence (reference); the TypeScript float path allocates on every call and the C++ baseline is built -Oz and called through embind.
- Harness flaw: src/cpp/main.cpp never calls seed() (a local 'uint32_t seed = 44983921329;' shadows the function), so the global TinyMT stays all-zero, a fixed point of next_state, and every native u32() returns 0; the README's 'native C++ 2-4x faster than Wasm' rows time a degenerate generator, and the C++/Emscripten contender is the same build. The exported int() returns a signed i32; the TypeScript port keeps its state in a number[] while the winning AssemblyScript build uses four scalar globals (array-based AssemblyScript builds lose to TypeScript 3.7-5.1x); the committed C++ artifacts (12,350 and 25,519 bytes) do not match the size table.

## Caveats and trade-offs

Single-author benchmark repo with no stated CPU or OS; no licence file, so code is reference only. Float comparison is inflated because the TypeScript temperConv allocates an ArrayBuffer, a Uint8Array and a DataView on every call (the author says so; a shared typed-array view would remove the allocation), where Wasm has a single reinterpret instruction. The C++ contender is size-optimised (-Oz overrides -O3) and every call goes through an embind-generated JS invoker, while the AssemblyScript exports are called directly, so the 1.08-1.12x AssemblyScript-over-C++ margin probably includes call-boundary overhead rather than codegen. The integer comparison is the fairer one (1.25-1.42x over TypeScript). Native x86 C++ is 2.4-3.4x faster than the best Wasm row on the same page. The README's native table at x10,000 lists 19,315.69 hz for AssemblyScript, which is the C++/Emscripten number (copy error). Evidence for AssemblyScript (already catalogued) rather than a library of its own. [retier] Single-author benchmark repo with no stated CPU or OS; no licence file, so the code is reference only. Harness flaw: the C++ driver never seeds its generator (see claim), so the C++/Emscripten and native rows time a degenerate all-zero generator and are struck; the C++ build is also size-optimised (em++ -O3 -Oz, last flag wins) and every call crosses an embind JS invoker. The float comparison is inflated because the TypeScript temperConv allocates an ArrayBuffer, a Uint8Array and a DataView on every call; the integer comparison (1.25-1.42x over TypeScript) is the fairer one. The TypeScript port stores its state in a number[] while the winning AssemblyScript build uses four scalar globals (array-based AssemblyScript builds lose to TypeScript 3.7-5.1x); the bench callbacks discard return values. Exported int() is typed i32, so about half of the outputs come back negative in JavaScript. The README's native x10,000 table prints the C++ figure (19,315.69 hz) in the AssemblyScript row, and the committed C++ artifacts (12,350 and 25,519 bytes) do not match the size table.

Fastest build uses only i32/u32 locals (the 128-bit state is unrolled into four variables, no arrays or strings); the same AssemblyScript with Array or StaticArray is 4-5x slower than TypeScript (2.7M hz vs 12.2M hz for ints x10) and 3.5-6x larger, so the win needs hand-restricted code. Native C++ is 2-4x faster than every Wasm build.

## Maintenance

Five commits on 2026-09-21/22, 0 stars, no licence and no issues; reference only, useful as a write-up rather than as code to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party vitest bench (src/tinymt.bench.ts) with public code and stated asc/em++ flags and Node 24.18.0, but no CPU model or OS anywhere, so not A; single-author repo, no independent measurement.
- **Verifier notes:** All claimed numbers (ints x10 and x10,000, floats x10,000 87x, sizes 1,260/3,568/36,445 bytes) match the README and the derived ratios are correct. Record wrongly said the AssemblyScript output also went through wasm-opt -O3; corrected. Shortcomings: no CPU/OS, no licence, TypeScript float path allocates per call, C++ baseline -Oz plus embind call overhead.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-68 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark>
  - <https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark/commits>
  - <https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark/tree/main/src>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/Makefile>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/package.json>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/tinymt.bench.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/rnd/tinymt.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/wasm/tinymt.asm.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/cpp/tinymt.cpp>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/cpp/main.cpp>
- **Sources the enricher read:**
  - <https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark>
  - <https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark/commits>
  - <https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark/issues>
  - <https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark/tree/main/src>
  - <https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark/tree/main/src/wasm>
  - <https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark/tree/main/src/cpp>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/Makefile>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/package.json>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/tsconfig.json>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/vitest.config.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/tinymt.bench.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/rnd/tinymt.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/rnd/tinymt.test.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/wasm/tinymt.asm.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/wasm/tinymtArrays.asm.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/wasm/tinymtStaticArrays.asm.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/wasm/tinymt.test.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/wasm/tinymt.js>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/wasm/.gitignore>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/cpp/tinymt.cpp>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/cpp/main.cpp>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/cpp/tinymt.test.ts>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/cpp/tinymt.js>
  - <https://raw.githubusercontent.com/matthewtolman/tinymt-wasm-typescript-benchmark/HEAD/src/cpp/tinymt.wasm>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/matthewtolman/tinymt-wasm-typescript-benchmark`) · [data/wave13/enrich/raw/github_com_matthewtolman_tinymt_wasm_typescript_benchmark.json](../../../data/wave13/enrich/raw/github_com_matthewtolman_tinymt_wasm_typescript_benchmark.json) (enrichment confidence 0.6)

</details>
