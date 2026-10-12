# zaw (Zero-Allocation WASM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig and Rust (WebAssembly) with TypeScript host` · `Apache-2.0` · 🟢 active

> Fixed-buffer JS-to-WASM call protocol (TypeScript host, Zig/Rust modules); 3.3-6.9x faster than wasm-bindgen on 100+ element typed-array calls.

| | |
|---|---|
| **Beats** | Plain JavaScript loop and Rust wasm-bindgen |
| **Claimed result** | XOR Int32Array (copy in, XOR, read out), zaw Rust build vs plain JavaScript loop: 6.03x at 100 elements, 11.39x at 1,000, 12.80x at 10,000, 13.75x at 100,000; vs Rust wasm-bindgen: 6.20x, 6.88x, 3.32x, 4.32x. zaw Zig build vs JavaScript: 6.0x, 9.7x, 9.9x, 10.0x; vs wasm-bindgen 6.2x, 5.9x, 2.6x, 3.1x (derived from page data). At 10 elements plain JS is 1.66x faster than zaw Rust and 1.67x faster than zaw Zig. Transfer Out Float64Array: zaw 4.3x to 10.65x faster than wasm-bindgen; Transfer In Float64Array: wasm-bindgen 1.03x to 1.22x faster than zaw up to 10,000 elements. 4x4 Float32 matrix multiply: zaw 1.23x (batch 1) to 24.35x (batch 1000) faster than JS. |
| **Workload** | XOR of a scalar into an Int32Array passed in and out of WebAssembly, for 10 to 100,000 elements, measured with vitest bench. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X3D 16-Core Processor (docs/benchmarks.md); Node/browser version not stated |
| **Compiler and flags** | Zig: zig build -Doptimize=ReleaseFast, wasm32-freestanding with +simd128, then wasm-opt -O4 --enable-simd --enable-bulk-memory (scripts/build-zig.sh, examples/wasm-zig/build.zig). Rust (zaw): cargo build --release with opt-level 3, LTO, codegen-units 1, panic=abort, RUSTFLAGS +simd128, then wasm-opt -O4 --enable-simd (scripts/build-rust.sh, examples/wasm-rust/Cargo.toml). wasm-bindgen baseline: wasm-pack build --target web with +simd128. Toolchain versions of the benchmark run not stated: docs/benchmarks.md was last updated 2026-02-17, before the 2026-05-24 'Upgrade to zig 16' commit, so the Zig 0.16.0 badge does not describe the measured build; Rust is unpinned 'stable'; Node/V8 version not stated. |
| **Adoption** | 74 stars |
| **Last commit** | 2026-05-24 |
| **Links** | [repository](https://github.com/stylearcade/zaw) · [benchmark](https://github.com/stylearcade/zaw/blob/main/docs/benchmarks.md) |

## Verdict

docs/benchmarks.md is one first-party vitest bench run in Node on an AMD Ryzen 9 9950X3D (Node, Zig and Rust versions not stated, run before the 2026-05-24 Zig 0.16 upgrade): XOR of a scalar into an Int32Array, zaw's Rust build vs a plain JS loop 6.0x at 100 elements up to 13.75x at 100,000 and vs wasm-bindgen 3.3x to 6.9x; JS wins at 10 elements; zaw's Zig build reaches 6-10x vs JS. Release builds used wasm-opt -O4 with simd128 for zaw, and wasm-pack's defaults with simd128 for the wasm-bindgen baseline.

## Use it when

- Offloading individual numeric kernels from a TypeScript/JavaScript app to Zig or Rust WASM when calls pass or return typed arrays of about 100 elements or more
- Hot paths that return arrays from WASM: the repo's Transfer Out Float64Array bench is 4.3x to 10.7x faster than wasm-bindgen from 10 to 100,000 elements
- Batched small operations (for example many 4x4 matrix multiplies per call) where wasm-bindgen's per-call Vec allocation dominates: 1.7x to 4.0x faster than wasm-bindgen at batch 10 to 1000
- Teams that want error messages, panic text and logging from WASM without adopting wasm-bindgen or the Component Model

## Skip it when

- Tiny inputs: at 10 elements plain JavaScript was 1.66x faster than zaw's Rust build and 1.67x faster than its Zig build in the repo's own XOR bench
- Input-heavy calls with a scalar result: in Transfer In Float64Array wasm-bindgen was 1.03x to 1.22x faster than zaw up to 10,000 elements
- Strings, structs, closures, DOM or JS object interop: only numeric scalars, numeric arrays and UTF-8 byte strings are supported, so wasm-bindgen or web-sys is still the tool there
- Results larger than the fixed channel sizes chosen at instantiation (the benchmarks use 1,000,000 bytes each way); the module traps or panics on overflow rather than growing
- Code that needs a stable API: npm 0.0.5, crate 0.0.3, Zig package 0.0.1, Go host 'coming later', single company maintainer

## How it is fast

There is no per-call allocation on either side: input arrays are copied with one TypedArray.set into a preallocated, 8-byte-aligned channel; the module reads them as slices in place and writes results into a slice of the output channel; the host returns a subarray view of that channel instead of copying the result out. wasm-bindgen, by contrast, mallocs the input in WASM, and returning a Vec allocates on the WASM side and copies into a new JS typed array. Bindings are generated once per arity with new Function and cached views are rebuilt only when memory.buffer changes after memory.grow. The example kernels use simd128 (Zig auto-vectorises, Rust shares one kernel crate with the wasm-bindgen build).

## Compared with alternatives

Pick zaw over the catalogued wasm-bindgen entry when the hot path is a numeric kernel called often with typed arrays of 100+ elements, especially when it returns arrays; keep wasm-bindgen (and web-sys) for DOM work, strings and rich types. The other siblings (hash-wasm, DuckDB-Wasm, Loro, tfjs-backend-wasm and the like) are finished WASM libraries, not interop layers; zaw is a way to build such a library's call boundary.

## Integration

| | |
|---|---|
| **Form** | module (npm zaw for the host) plus crate (Rust) or Zig package for the WASM side |
| **Dependencies** | none at runtime; the build examples use wasm-opt (Binaryen) and wasm2wat, and the wasm-bindgen baseline needs wasm-pack |
| **Minimum toolchain** | Zig 0.16.0 on main (benchmarks predate that upgrade); Rust stable with target wasm32-unknown-unknown and -C link-arg=--import-memory; a JS runtime with WebAssembly SIMD for the simd128 example builds; a host that allows new Function |
| **Platforms** | any WebAssembly host where the TypeScript host can create a WebAssembly.Memory and pass it as env.memory (Node, browsers); the module must import its memory |
| **Thread safety** | Not documented. Each instance owns a single input and a single output channel, so calls are serialised and a returned array is only valid until the next call on that instance; use one instance per worker. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetries behind the headline ratios: the JS XOR baseline allocates a fresh zero-filled Int32Array on every call and the JS 4x4 matmul baseline makes two slice() copies plus a new Float32Array per matrix and discards the results, while zaw returns a reused subarray view; the JS loop works out to about 6.1 ns per element at 100 elements and 1.3 ns at 100,000 versus zaw Rust's 0.095 ns (derived from page data), so the up-to-14x and 20-24x figures mostly measure JS allocation, not compute. All numbers are one Node run via vitest bench (Node version not stated, no browser runs).
- Returned arrays are views into the output channel: the next call on the same instance overwrites them and a later memory.grow detaches them, so copy (slice) anything you keep, which gives back part of the advantage over wasm-bindgen.
- The TypeScript host builds bindings with new Function, which fails where string code generation is blocked (a Content-Security-Policy without 'unsafe-eval', and runtimes such as Cloudflare Workers).
- Low-level defects in the module-side channel code: the Rust Channel holds five overlapping &mut slices of one buffer created with unsafe from_raw_parts_mut (aliasing undefined behaviour under Rust's rules, though it works with current compilers), and Zig's checkOffset tests offset &gt;= capacity, so a payload that exactly fills a channel panics with 'Channel out of bounds' (the Rust side uses &gt;).

## Known shortcomings

- The JavaScript baselines create a new typed array on every call while zaw returns a reused view into WASM memory, so the 20-24x matmul ratios are inflated; the record's numbers are the Rust build (the Zig build is 6-10x over JavaScript, derived); Node/V8 and toolchain versions unstated; benchmarks.md (2026-02-17) predates the Zig 0.16 upgrade; wasm-bindgen is faster on Transfer In.
- The headline 14x vs JS and 20-24x matmul mostly measure JS allocation: the JS XOR baseline allocates a fresh zero-filled Int32Array per call and the matmul baseline does two slice() copies plus a new Float32Array per matrix, while zaw returns a reused subarray view (the JS loop works out to about 6.1 ns per element at 100 and 1.3 ns at 100,000 vs zaw's 0.095 ns, derived). One Node run only, Node version unstated. Code defects: the Rust Channel holds five overlapping &mut slices (aliasing UB); Zig's checkOffset uses &gt;=, so an exact-fit payload panics; the host builds bindings with new Function (breaks under CSP and in Workers).

## Caveats and trade-offs

Micro-benchmarks of interop overhead, first-party. Harness asymmetries: the JS XOR baseline allocates a fresh Int32Array per call, while zaw returns a subarray view into the WASM output buffer (implementations/host-typescript/src/conduit.ts readInt32Elements) that the next call overwrites, so a caller that keeps the result must copy it and the 'zero-allocation' gain partly comes from not materializing output; the JS 4x4 matmul baseline does two slice() copies plus a new Float32Array per matrix, which inflates the 20-24x matmul ratios. The wasm-bindgen comparison is fair on kernel (both call the same shared::xor_array_i32), the difference being Vec allocation and copy-out. In 'Transfer In Float64Array' wasm-bindgen is faster than zaw up to 10,000 elements. Toolchain and Node versions of the run are not stated, and the published numbers predate the Zig 0.16 upgrade.

It is an interop protocol, not an algorithm library; wins only when data is large enough to amortise the call (not at 10 elements) and the author picks the cheapest possible kernel to expose interop cost.

## Maintenance

Active (last commit 2026-05-24, two closed issues, one open PR) and Apache-2.0, but pre-1.0 (npm 0.0.5, crate 0.0.3) from one company; the protocol is small enough to vendor or reimplement, and the benchmark should be re-run in your target browser before trusting the ratios.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party vitest bench output (examples/host-typescript/__tests__/example.bench.ts, results in docs/benchmarks.md) with CPU model (AMD Ryzen 9 9950X3D) and public build flags (scripts/build-zig.sh, scripts/build-rust.sh), but the Node/V8 version that runs the JS baseline and the wasm, and the Zig/Rust toolchain versions of the run, are not stated, so it falls short of A.
- **Verifier notes:** Numbers match docs/benchmarks.md; the record's figures are the zaw Rust build's row (the Zig build is 6-10x vs JS). Kernels really compute the XOR in both zaw builds and the wasm-bindgen baseline; no invalid evidence, but the JS baselines pay per-call typed-array allocation that zaw avoids by returning a reused view. Metadata confirmed: Apache-2.0, 74 stars, last commit 2026-05-24, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-91 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/stylearcade/zaw>
  - <https://github.com/stylearcade/zaw/commits/main>
  - <https://github.com/stylearcade/zaw/commits/main/docs/benchmarks.md>
  - <https://github.com/stylearcade/zaw/tree/main/examples>
  - <https://github.com/stylearcade/zaw/tree/main/examples/wasm-rust/api_zaw>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/README.md>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/host-typescript/__tests__/example.bench.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/host-typescript/host.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/implementations/host-typescript/src/conduit.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/wasm-zig/main.zig>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/wasm-zig/build.zig>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/wasm-rust/Cargo.toml>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/wasm-rust/api_zaw/lib.rs>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/wasm-rust/api_bindgen/lib.rs>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/utils/index.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/scripts/build-zig.sh>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/scripts/build-rust.sh>
- **Sources the enricher read:**
  - <https://github.com/stylearcade/zaw>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/README.md>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/docs/getting-started.md>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/docs/protocol-conduit.md>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/docs/protocol-interop.md>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/host-typescript/__tests__/example.bench.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/host-typescript/host.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/utils/index.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/wasm-rust/api_zaw/lib.rs>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/wasm-rust/api_bindgen/lib.rs>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/wasm-zig/main.zig>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/examples/wasm-zig/build.zig>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/implementations/host-typescript/src/index.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/implementations/host-typescript/src/interop.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/implementations/host-typescript/src/binding.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/implementations/host-typescript/src/conduit.ts>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/implementations/host-typescript/package.json>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/implementations/wasm-rust/conduit/mod.rs>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/implementations/wasm-zig/src/conduit.zig>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/implementations/wasm-zig/src/conduit/conduit.zig>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/scripts/build-zig.sh>
  - <https://raw.githubusercontent.com/stylearcade/zaw/HEAD/scripts/build-rust.sh>
  - <https://github.com/stylearcade/zaw/tree/main/implementations/wasm-zig>
  - <https://github.com/stylearcade/zaw/tree/main/implementations/wasm-zig/src>
  - <https://github.com/stylearcade/zaw/tree/main/implementations/wasm-rust>
  - <https://github.com/stylearcade/zaw/tree/main/implementations/wasm-rust/conduit>
  - <https://github.com/stylearcade/zaw/issues?q=is%3Aissue>
  - <https://github.com/stylearcade/zaw/issues/17>
  - <https://github.com/stylearcade/zaw/issues/18>
  - <https://crates.io/api/v1/crates/zaw>
  - <https://registry.npmjs.org/zaw>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/stylearcade/zaw`) · [data/wave13/enrich/raw/github_com_stylearcade_zaw.json](../../../data/wave13/enrich/raw/github_com_stylearcade_zaw.json) (enrichment confidence 0.75)

</details>
