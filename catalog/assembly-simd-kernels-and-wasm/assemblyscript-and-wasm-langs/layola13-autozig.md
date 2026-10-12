# AutoZig

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust + Zig (WASM SIMD128 filter example)` · `Apache-2.0 OR MIT` · 🟢 active

> Rust-to-Zig FFI generator whose WASM demo links a Zig SIMD128 image filter into a Rust module; claims 4.75x over JavaScript.

| | |
|---|---|
| **Beats** | JavaScript image filter in the browser; also Rust compiled to WASM ('Rust Native' row) |
| **Claimed result** | README table (2.1 MB image, filter not named): AutoZig (Zig SIMD) 0.80 ms (2631.84 MB/s), Rust 2.50 ms (842.19 MB/s, '3.13x slower'), JavaScript 3.80 ms (554.07 MB/s, '4.75x slower'); headline '3-5x faster than pure JavaScript, 3x faster than Rust native'. Each figure is one click timed with performance.now, quantized to 0.1 ms. The example README (examples/wasm_filter/README.md) carries a different table for a 1920x1080 8.3 MB image (Zig WASM \~5 ms, pure JS \~25 ms, 'Canvas API' \~15 ms for invert) with a Canvas API row that has no implementation in the repo. |
| **Workload** | Browser demo (examples/wasm_filter/www/index.html): one call of an RGBA filter (invert, grayscale or brightness; the README table does not say which) on a user-uploaded 2.1 MB image, timed with performance.now around a single call with no warm-up or repetition; the wasm rows include wasm-bindgen copy-in and copy-out of the Vec&lt;u8&gt;, the JS row allocates a new Uint8Array |
| **Metric** | latency |
| **Compiler and flags** | Zig -O ReleaseFast -mcpu=mvp+simd128 -fno-stack-protector, target wasm32-freestanding (engine/src/zig_compiler.rs; the example README still says ReleaseSmall); Rust wasm32-unknown-unknown with opt-level "s", lto = true and -C target-feature=+simd128 (examples/wasm_filter/Cargo.toml, .cargo/config.toml), built with wasm-pack --target web; browser and JS engine not stated |
| **Adoption** | 5 stars |
| **Last commit** | 2026-01-15 |
| **Links** | [repository](https://github.com/layola13/autozig) · [benchmark](https://github.com/layola13/autozig) |

## Verdict

One click per implementation in examples/wasm_filter/www/index.html on a user-uploaded image of about 2.1 MiB of RGBA data (throughputs times durations agree), timed with performance.now around a single call that includes wasm-bindgen copy-in and copy-out: Zig SIMD128 0.80 ms, scalar Rust compiled to wasm at opt-level "s" 2.50 ms, scalar JavaScript 3.80 ms; browser, CPU and filter not stated. The table was added in commit 9cf585e (2026-01-09) on the wasm-bindgen version of the example, whose Zig kernels are unchanged at HEAD.

## Use it when

- A Rust project that wants to keep a few hot kernels in Zig (for @Vector SIMD, comptime or existing Zig/C code) and call them through generated wrappers with one cargo build.
- A Rust wasm32 browser module where you want Zig and Rust code statically linked into one .wasm sharing linear memory, with the Zig side built for SIMD128.
- Prototyping Rust-Zig-C three-way interop (the zig-c example) or comparing Zig and Rust codegen for small byte-crunching loops.
- As a worked example of writing WebAssembly SIMD128 byte kernels; the speedup itself is reproducible in Rust with core::arch::wasm32 intrinsics.

## Skip it when

- When you need a correct image filter: the SIMD invert path also inverts the alpha byte (opaque pixels become transparent) and the SIMD brightness path changes alpha, unlike the Rust and JS versions and the example README's 'Alpha channel unchanged'.
- When you need a measured speedup you can trust: every figure is one browser click timed with performance.now, with no browser, CPU or filter named, and the 'Rust native' baseline is scalar size-optimized Rust compiled to wasm, not native Rust or Rust SIMD.
- When the build must be reproducible from the current tree: since commit f419e92 (2026-01-10) the wasm_filter example has no wasm-bindgen dependency, while its page still imports wasm-bindgen glue, so the benchmark has to be rebuilt from 9cf585e or earlier.
- Safety-critical FFI: wrappers for Zig functions declared with raw-pointer parameters are generated as safe pub fn bodies wrapping unsafe calls, so safe Rust can hand Zig a dangling pointer.
- Projects needing a maintained, released dependency: 5 stars, no issues filed, crates.io stuck at 0.1.2 (2026-01-06, 80 downloads) while the repo moved on, and no commits since 2026-01-15.

## How it is fast

The fast row is a hand-written Zig loop over @Vector(16, u8) that lowers to WebAssembly SIMD128 (v128 load, i8x16 sub or saturating add/sub, store), 16 bytes per step, compiled with -O ReleaseFast -mcpu=mvp+simd128. The Rust comparison is a bounds-checked scalar step_by(4) loop built at opt-level "s", and the JavaScript one is a scalar per-byte loop that also allocates a fresh output array, so the gap is SIMD versus scalar code rather than anything Zig-specific. Grayscale is scalar in Zig too.

## Compared with alternatives

Pick AutoZig only for its Rust-Zig build integration; for the WASM speedup itself, wasm-perf (Emscripten SIMD intrinsics vs JS) and tape-sha256 (WASM SIMD SHA-256) publish more careful numbers, and msf/wasmplay compares Zig wasm against C++ on one runtime.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | autozig plus autozig-build as a build-dependency (crates autozig-macro, autozig-engine pulled in); Zig compiler on PATH at build time; tokio and futures for the async and stream features; the WASM demo also needs wasm-pack and wasm-bindgen |
| **Minimum toolchain** | Rust 1.77+, Zig 0.15+ (README; the example README still says 0.11+); browsers with WebAssembly SIMD128 (Chrome 91+, Firefox 89+, Safari 16.4+ per .cargo/config.toml) |
| **Platforms** | Native targets the Zig compiler supports (x86-64, aarch64), wasm32-freestanding with SIMD128, experimental wasm64 (Memory64) in the repo only |
| **Thread safety** | Not documented for generated wrappers; the README requires free callbacks to be Send + Sync, and opaque trait types are !Send and !Sync. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the demo page keeps only the last duration per implementation (perfStats[impl].time) regardless of which filter produced it, and every brightness-slider input event also overwrites it, so the README's relative column can compare different filters across rows; combined with single samples and no warm-up loop (a first click on the JS row includes JIT tiering, and every JS call allocates a fresh 2.1 MB Uint8Array), the 3.13x and 4.75x ratios are not a controlled measurement.
- Correctness: the timed SIMD invert path writes 255 - x to every byte including alpha, and the SIMD brightness path saturates alpha too, so the fast row does not compute the same image as the Rust and JS rows.
- The Zig kernels cast ptr + i to \*@Vector(16, u8) with @alignCast, but the buffer is a Vec&lt;u8&gt; with only byte alignment guaranteed: in ReleaseFast this is unchecked illegal behavior (works on wasm because load alignment is only a hint) and in Debug or ReleaseSafe builds a misaligned buffer would panic.
- Repo and crates.io diverge: crates.io autozig-macro 0.1.2 has no #[autozig_export], which the current example uses; at HEAD #[autozig_export] expands to a #[no_mangle] extern "C" fn taking and returning Vec&lt;u8&gt; by value, which is not FFI-safe and is not what the page's wasm-bindgen import expects.

## Known shortcomings

- Claim overstated: single browser click timings; the Zig SIMD invert also inverts alpha so the timed fast path's output differs from the Rust and JS baselines; the Rust baseline is a scalar bounds-checked loop at opt-level s; the README example table (about 5 vs 25 ms, Canvas API row) has no code. Not a reject because the bug is not the source of the speed.
- Harness flaw: index.html keeps one last perfStats time per implementation whatever filter ran, and brightness-slider events overwrite it, so the README ratio column can mix filters; single clicks with no warm-up. The HEAD demo is broken: f419e92 (2026-01-10) swapped #[wasm_bindgen] for #[autozig_export] (a #[no_mangle] extern 'C' fn taking Vec&lt;u8&gt;) and dropped the wasm-bindgen dependency while the page still imports wasm-bindgen glue; rebuild from 9cf585e, the commit that added the table (kernels unchanged since). The timed SIMD invert path inverts alpha (confirmed), so it computes a different image than the Rust and JS rows; @alignCast to \*@Vector(16, u8) on a byte-aligned Vec is unchecked illegal behaviour in ReleaseFast; safe wrappers generated over raw-pointer parameters are unsound; crates.io 0.1.2 lags the repo; idle since 2026-01-15.

## Caveats and trade-offs

Single-sample browser timings (one click, no warm-up, 0.1 ms timer granularity); browser, hardware and which filter was timed are not stated. The Zig SIMD invert_colors_raw subtracts every byte from 255, including alpha, while the Rust and JS versions and the example README ('Alpha channel unchanged') leave alpha intact, so the timed fast path produces different output (opaque pixels become transparent); the SIMD brightness path likewise changes alpha for negative deltas. A correct masked SIMD version would cost about the same, so the bug does not obviously create the speedup, but the row does not time the specified filter. The 'Rust native' baseline is a bounds-checked scalar step_by(4) loop built at opt-level "s" (size), so the 3x over Rust measures hand-written SIMD128 against a size-optimized scalar loop, not Zig against Rust; the grayscale filter is scalar in Zig too. The example README's second table (8.3 MB, \~5 vs \~25 ms, Canvas API row) has no matching code and looks unmeasured. Trivially vectorizable byte filter; crate autozig 0.1.2 with 80 downloads (crates.io, 14 recent); 5 stars; first-party only. [retier] Single-sample browser timings (one click, no warm-up, 0.1 ms timer granularity); browser, hardware and which filter was timed are not stated. Harness flaw: index.html keeps only the last duration per implementation (perfStats[impl].time) regardless of which filter produced it, and every brightness-slider input event overwrites it, so the README's relative column can compare different filters across rows; a first click on the JS row includes JIT tiering and every JS call allocates a fresh 2.1 MB Uint8Array. The timed Zig SIMD invert path writes 255 - x to every byte including alpha (confirmed), and the SIMD brightness path saturates alpha too, so the fast row does not compute the same image as the Rust and JS rows (a correctly masked version would cost about the same). The 'Rust native' baseline is a bounds-checked scalar loop. The HEAD demo is broken: commit f419e92 (2026-01-10) swapped #[wasm_bindgen] for #[autozig_export] (a #[no_mangle] extern 'C' fn taking and returning Vec&lt;u8&gt; by value, not FFI-safe) and dropped the wasm-bindgen dependency while the page still imports wasm-bindgen glue; rebuild from 9cf585e, the commit that added the table. The Zig kernels @alignCast ptr + i to \*@Vector(16, u8) on a byte-aligned Vec&lt;u8&gt; (unchecked illegal behaviour in ReleaseFast); generated safe wrappers over raw-pointer parameters are unsound; crates.io autozig-macro 0.1.2 lacks #[autozig_export]; idle since 2026-01-15. The example README's second table has a 'Canvas API' row with no implementation in the repo.

Combines Rust (memory and wasm-bindgen glue) with Zig compute kernels in one .wasm; needs the Zig toolchain at build time.

## Maintenance

Dual MIT/Apache-2.0 and small, but effectively a one-author experiment idle since 2026-01-15 with the published crates behind the repo and the benchmarked demo no longer building as committed; treat the image-filter numbers as a SIMD-versus-scalar illustration.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** First-party README table (single browser timings) from the public demo harness examples/wasm_filter/www/index.html and src/lib.rs, with no browser, hardware or iteration count stated, so C; the claim is overstated and the timed SIMD invert path computes a different output from the baselines.
- **Retiered** C to D: Enricher: the demo page keeps one last perfStats time per implementation whatever filter produced it and slider events overwrite it, so the README ratio column can compare different filters; each figure is a single click with no warm-up at 0.1 ms granularity, the timed SIMD path computes a different image (alpha inverted), and the HEAD demo no longer runs. No valid like-for-like measurement: C to D.
- **Verifier notes:** Downgraded for an overstated claim and a correctness flaw in the timed path, tier stays C: the SIMD invert inverts alpha (baselines and the spec do not), Rust baseline is a scalar size-optimized loop, and every figure is one browser click. If the orchestrator reads the README table as the invert filter, D is arguable (timed fast path computes a different image), but the speed itself is not produced by the bug so this is not a reject.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-19 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/layola13/autozig>
  - <https://github.com/layola13/autozig/commits>
  - <https://github.com/layola13/autozig/tree/main/examples/wasm_filter>
  - <https://github.com/layola13/autozig/commits/main/examples/wasm_filter/src/lib.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/README.md>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/README.md>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/src/lib.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/Cargo.toml>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/build.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/build_and_serve.sh>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/www/index.html>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/.cargo/config.toml>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/engine/src/zig_compiler.rs>
  - <https://crates.io/api/v1/crates/autozig>
- **Sources the enricher read:**
  - <https://github.com/layola13/autozig>
  - <https://github.com/layola13/autozig/commits/main>
  - <https://github.com/layola13/autozig/commits/main/examples/wasm_filter>
  - <https://github.com/layola13/autozig/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/README.md>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/macro/src/lib.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/gen/build/src/lib.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/engine/src/zig_compiler.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/README.md>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/src/lib.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/Cargo.toml>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/build.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/build_and_serve.sh>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/www/index.html>
  - <https://raw.githubusercontent.com/layola13/autozig/HEAD/examples/wasm_filter/.cargo/config.toml>
  - <https://raw.githubusercontent.com/layola13/autozig/4e329af/examples/wasm_filter/src/lib.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/4e329af/examples/wasm_filter/Cargo.toml>
  - <https://raw.githubusercontent.com/layola13/autozig/42e4349/examples/wasm_filter/src/lib.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/42e4349/examples/wasm_filter/Cargo.toml>
  - <https://raw.githubusercontent.com/layola13/autozig/9cf585e/examples/wasm_filter/src/lib.rs>
  - <https://raw.githubusercontent.com/layola13/autozig/9cf585e/examples/wasm_filter/Cargo.toml>
  - <https://raw.githubusercontent.com/layola13/autozig/0a096ae/README.md>
  - <https://raw.githubusercontent.com/layola13/autozig/4e329af/README.md>
  - <https://raw.githubusercontent.com/layola13/autozig/9cf585e/README.md>
  - <https://crates.io/api/v1/crates/autozig>
  - <https://crates.io/api/v1/crates/autozig-build>
  - <https://crates.io/api/v1/crates/autozig-macro>
  - <https://crates.io/api/v1/crates/autozig-engine>
  - <https://static.crates.io/crates/autozig-engine/autozig-engine-0.1.2.crate>
  - <https://static.crates.io/crates/autozig-macro/autozig-macro-0.1.2.crate>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/layola13/autozig`) · [data/wave13/enrich/raw/github_com_layola13_autozig.json](../../../data/wave13/enrich/raw/github_com_layola13_autozig.json) (enrichment confidence 0.7)

</details>
