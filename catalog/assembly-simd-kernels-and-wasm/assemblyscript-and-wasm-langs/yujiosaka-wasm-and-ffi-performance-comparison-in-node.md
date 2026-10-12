# wasm-and-ffi-performance-comparison-in-node (Rust WASM Collatz)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟡 stale

> One-commit Node benchmark: a Rust Collatz loop compiled to wasm runs 45.6x faster than a naive JS loop and 6.5x faster than an ffi-napi call.

| | |
|---|---|
| **Beats** | JavaScript Number-based Collatz loop in Node (V8), and the same Rust function built as a native cdylib (cargo build --release, no LTO) called through ffi-napi 4.0.3 |
| **Claimed result** | JS 32,172 ops/sec, FFI 225,918 ops/sec, WASM 1,465,898 ops/sec; WASM is 45.6x JS and 6.5x FFI (derived from page data). |
| **Workload** | Collatz step count for input 670617279 in Node, benchmark.js, comparing a JS function, a Rust FFI addon and Rust compiled with wasm-pack. |
| **Metric** | throughput |
| **Compiler and flags** | WASM: wasm-pack build --target nodejs --release, Cargo release profile lto = true, wasm-bindgen 0.2.92; FFI: cargo build --release (default profile, no LTO) loaded with ffi-napi ^4.0.3 and ref-napi ^3.0.3; benchmark ^2.1.4; Node version not stated |
| **Adoption** | 10 stars, 1 commit |
| **Last commit** | 2024-04-21 |
| **Links** | [repository](https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node) · [benchmark](https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node) |

## Verdict

Author's Benchmark.js run in Node (CPU, OS and Node version not stated) on input 670617279, after one equality check of the step counts: JS 32,172 ops/s (31.1 us per call), Rust via ffi-napi 225,918 ops/s (4.43 us), Rust via wasm-bindgen 1,465,898 ops/s (0.68 us), so wasm is 45.6x JS and 6.5x FFI (derived from page data). The JS gap mostly reflects float64 arithmetic forced by values above 2^31; the FFI gap reflects ffi-napi call overhead.

## Use it when

- As a template for moving a hot integer kernel from Node.js JavaScript into Rust/wasm-bindgen when it needs exact 64-bit integer math that JS can only do with float64 or BigInt.
- Kernels doing roughly a microsecond or more of work per call with scalar arguments, so the BigInt conversions at the JS/wasm boundary are amortised.
- Deciding between ffi-napi and wasm for a small Rust function called at high frequency: with little work per call, wasm's in-process call beats ffi-napi's dynamic marshalling.
- A minimal wasm-pack --target nodejs setup that loads synchronously with require().

## Skip it when

- As evidence that wasm beats native code: the FFI row is dominated by ffi-napi's call path. A Node-API addon (napi-rs, node-addon-api) or a native loop doing many iterations per call was not tested.
- As evidence against well-written JavaScript: the JS kernel was not adapted to float64. For example, testing parity with `n & 1` (ToInt32 keeps parity for any safe integer) avoids the float64 remainder. Not measured.
- Workloads that pass strings, arrays or buffers across the boundary: only one integer in and one integer out was measured.
- Browsers or bundlers: only a --target nodejs build is set up (webpack and @wasm-tool/wasm-pack-plugin are in devDependencies but unused).
- When you need reproducible numbers: no CPU, OS or Node version, one run printed, a single commit and no CI.

## How it is fast

The wasm module runs the loop on 64-bit integers. The JavaScript loop's values climb to 966,616,035,460 (986 steps, 370 of them odd; derived by recomputing the sequence), far beyond the int32/Smi range, so V8 runs the % 2 and / 2 on float64 numbers. That works out to about 31.5 ns per step versus 0.69 ns for wasm. Against FFI, the gain is per-call overhead, not code quality: ffi-napi marshals every call through libffi and ref-napi (its own README warns of 'non-trivial overhead associated with FFI calls'), costing 4.43 us per call versus 0.68 us for the whole wasm call including BigInt conversion.

## Compared with alternatives

Within its category it is the smallest Rust/wasm-bindgen example and the only one with a native-FFI arm, while wasm-perf (Emscripten SIMD matrix multiply, about 23.5x over JS) and JavaScript-vs-WebAssembly-Comparative-Analysis exercise heavier kernels. For a fairer native baseline, iswasmfast (catalogued under wasm-libraries-and-apps) pits wasm against an N-API addon instead of ffi-napi.

## Integration

| | |
|---|---|
| **Form** | source-drop (example repo: a Rust crate built with wasm-pack --target nodejs plus a CommonJS wrapper) |
| **Dependencies** | wasm arm: wasm-bindgen 0.2.92; FFI arm: ffi-napi 4.0.3 and ref-napi 3.0.3 (native node-gyp builds); harness: benchmark 2.1.4, yargs 17.7.2 |
| **Minimum toolchain** | Rust (2021 edition) with wasm-pack, and a Node.js with BigInt and wasm i64 integration; exact versions not documented |
| **Platforms** | any Node.js platform for the wasm arm; the FFI arm needs the cdylib built per OS |
| **Thread safety** | not applicable (pure function, no shared state) |
| **Drop-in for the baseline** | no |

## Gotchas

- Return types differ: the wasm wrapper returns a BigInt and the JS version a Number. The harness's correctness check uses loose assert.equal (986 == 986n), which hides this; a strict check would fail, and callers must convert.
- The README's five reasons why wasm beats FFI (runtime symbol resolution, better inlining, the linear memory model) are not measured, and the first is wrong for this code: ffi.Library() resolves collatz_steps once at load in ffi/collatz.js, so the per-call cost is libffi/ref-napi argument and return marshalling.
- The FFI arm declares ['int64', ['int64']] over a signed i64 Rust function with assert!(n &gt; 0), while the wasm arm is u64. The FFI wrapper does no input check of its own (only benchmark.js validates via yargs), so passing 0 makes Rust panic inside an extern "C" function, which Rust 1.81 and later turn into a process abort. The wasm arm traps instead.
- The FFI baseline rests on ffi-napi 4.0.3 (released March 2021; last repository commit March 2022). A modern FFI module such as Koffi, which claims low overhead relative to Node-API, was not compared.

## Known shortcomings

- No CPU or Node version; JavaScript is forced into float64 math (values reach 9.7e11); the 6.5x over FFI is ffi-napi call overhead, not native code.
- The harness's loose assert.equal hides that the wasm path returns a BigInt and JS a Number (986 == 986n). The README's 'runtime symbol resolution' explanation is wrong (ffi.Library resolves once), the FFI arm has no input check so 0 makes the Rust extern "C" function panic (process abort on Rust 1.81+), ffi-napi 4.0.3 has had no release since 2021, and the JS slowdown is float64 math on values up to 966,616,035,460 (a faster n & 1 parity test was not measured).

## Caveats and trade-offs

Single-commit toy benchmark; no CPU, OS or Node version stated. The Collatz sequence for 670617279 takes 986 steps and peaks near 9.7e11, above the int32 range, so the JS version runs float64 % and / on heap numbers while the Rust version uses u64 integer ops, which probably explains much of the 45x gap. The 6.5x WASM-over-FFI result measures ffi-napi's per-call marshalling overhead (about 4.4 us per call versus about 0.7 us for the whole WASM call), not native versus WASM code quality; a N-API addon or an in-process native loop would be expected to beat WASM. The wasm wrapper converts the Number argument to BigInt on every call and returns a BigInt. Results are checked for equal step counts before timing. README gives speculative reasons for the win without profiling. [retier] Single-commit toy benchmark; no CPU, OS or Node version stated. The Collatz sequence for 670617279 takes 986 steps and peaks at 966,616,035,460, above int32, so the JS version runs float64 % and / while Rust uses u64 integer ops (a faster n & 1 parity test was not measured). The wasm path returns a BigInt and JS a Number; the harness's loose assert.equal (986 == 986n) hides it. The 6.5x WASM-over-FFI result measures ffi-napi's per-call marshalling (about 4.4 us per call vs about 0.7 us for the whole WASM call), not native versus WASM code; the README's 'runtime symbol resolution' explanation is wrong (ffi.Library resolves once). The FFI arm has no input check, so 0 panics inside extern "C" (process abort on Rust 1.81+); ffi-napi 4.0.3 has had no release since 2021.

Needs a Rust toolchain and wasm-pack; each call crosses the JS/Wasm boundary with a u64 (BigInt) argument; result only holds for a tight integer loop.

## Maintenance

Single commit on 2024-04-21, 10 stars, MIT; a frozen demo rather than a maintained project, fine to copy as a wasm-pack template, but its FFI arm depends on ffi-napi, which has had no release since 2021.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark.js (benchmark.js suite) with public code and build commands, but no CPU, OS or Node version stated: C.
- **Verifier notes:** README numbers match (JS 32,172, FFI 225,918, WASM 1,465,898 ops/sec; 45.6x and 6.5x derived correctly). MIT, 10 stars, 1 commit dated 2024-04-21, stale. Shortcomings: no hardware/runtime version, JS kernel forced into float64 math by the input size, FFI baseline dominated by ffi-napi call overhead.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-68 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node>
  - <https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/commits>
  - <https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/tree/main/wasm>
  - <https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/tree/main/ffi>
  - <https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/tree/main/js>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/README.md>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/benchmark.js>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/package.json>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/js/collatz.js>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/wasm/collatz.js>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/ffi/collatz.js>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/ffi/Cargo.toml>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/ffi/src/lib.rs>
- **Sources the enricher read:**
  - <https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node>
  - <https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/commits/main>
  - <https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/tree/main/.github>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/README.md>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/benchmark.js>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/package.json>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/package-lock.json>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/js/collatz.js>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/wasm/collatz.js>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/wasm/Cargo.lock>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/ffi/collatz.js>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/ffi/Cargo.toml>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/ffi/Cargo.lock>
  - <https://raw.githubusercontent.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node/HEAD/ffi/src/lib.rs>
  - <https://github.com/node-ffi-napi/node-ffi-napi>
  - <https://github.com/node-ffi-napi/node-ffi-napi/commits/master>
  - <https://github.com/Koromix/koffi>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/yujiosaka/wasm-and-ffi-performance-comparison-in-node`) · [data/wave13/enrich/raw/github_com_yujiosaka_wasm_and_ffi_performance_comparison_in_node.json](../../../data/wave13/enrich/raw/github_com_yujiosaka_wasm_and_ffi_performance_comparison_in_node.json) (enrichment confidence 0.75)

</details>
