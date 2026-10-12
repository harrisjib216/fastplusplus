# jz (dy/jz)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `JavaScript` · `MIT` · 🟢 active

> Ahead-of-time compiler from a static JavaScript subset to WebAssembly; about 2.3x faster than V8 running the same numeric kernels.

| | |
|---|---|
| **Beats** | V8 (Node.js) running the same JavaScript, plus AssemblyScript |
| **Claimed result** | README: 'Faster than V8 and AssemblyScript on almost every kernel we measure, about 2x on average'. bench/README.md aggregate geomean table (JZ/target, lab rows excluded): V8 (node) 0.42x, AssemblyScript 0.45x speed. Committed bench/results.json (Apple M4 Max, Node v25.9.0, dated 2026-09-30): geometric mean of per-case median time ratios jz/V8 0.425 over 53 non-lab checksum-ok cases (faster on 52), 0.443 over 55 when the watr/jessie self-compile lab rows are included (about 2.3x faster); jz/AssemblyScript 0.448 over 50 cases (faster on 44); jz run under wasmtime 0.498 of V8 over 52 cases (derived from page data). |
| **Workload** | Numeric JavaScript kernels (DSP, audio, image, hashing, parsing, simulation; 63 cases, 55 with parity against V8) compiled ahead of time to WebAssembly by jz and run on Node's V8 Wasm engine, versus the same source as raw JS on Node/V8. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max (darwin/arm64) |
| **Compiler and flags** | From bench/results.json meta: V8 = node v25.9.0 running node run-v8.mjs &lt;case&gt;.js; AssemblyScript 0.28.19 = asc &lt;case&gt;.as.ts -O3 (--runtime stub per bench README); jz 0.9.2 = compile(src, { optimize: 'speed' }) run on node's V8 Wasm engine; native references clang 19.1.6 -O3 -march=native -ffp-contract=off and rustc -C opt-level=3 -C target-cpu=native. Each case does 5 warm-up runs and reports the median of 21 timed runs. |
| **Adoption** | 174 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/dy/jz) · [benchmark](https://github.com/dy/jz/blob/main/bench/README.md) |

## Verdict

On an Apple M4 Max (Node v25.9.0, clang 19.1.6, asc 0.28.19, jz 0.9.2), the project's own harness (5 warm-up runs, median of 21) gives jz-compiled Wasm on V8 a geometric-mean time ratio of 0.425 versus the same JS on V8 over 53 non-lab cases with matching checksums (faster on 52) and 0.448 versus AssemblyScript -O3 over 50 cases; jz under wasmtime is 0.498 of V8 over 52 cases. The kernels are author-chosen numeric workloads, most V8 rows are from an older unidentified run, and the dataset is flagged partial.

## Use it when

- Numeric typed-array kernels written in JavaScript (DSP filters, audio synthesis, image convolution and blur, small matrix math, hashing, parsers) where you want a 2-10x speedup without rewriting in Rust or C.
- Shipping the same kernel to browsers and Node and to wasmtime or other WASI hosts from one JavaScript source (`--host wasi`).
- Audio worklets and other real-time paths: `memory: { fixed: [...] }` proves at compile time that the named exports never allocate, grow memory or call the host.
- Code you want to keep as plain JavaScript: removing the build step leaves source that still runs in any JS engine.

## Skip it when

- Dynamic JavaScript (eval, Proxy, Reflect, monkey-patching, prototype mutation, Intl, Temporal, DOM): rejected or left on slow dynamic paths.
- Long-lived, allocation-heavy object graphs: there is no GC; what a call keeps lives until `memory.reset()`, replaced state is never freed and WeakMap/WeakRef hold strongly.
- Code that needs exact JavaScript semantics: float sums may be reassociated (last digits differ), Math functions differ from V8 by up to 49 ulp, BigInt is 64-bit wrapping, compile-time constant chains use exact rationals, and bitwise operators on operands of 2^63 or more give -1 or 0.
- Large real libraries: the bench's flagship whole-library case (web-audio-api, about 120 modules) runs 11.6x slower than V8 and fails its checksum in the committed results, and the self-compile rows (watr, jessie) lose to V8.
- Production systems needing a stable ABI: pre-1.0, raw Wasm ABI not stable across versions, and the compiler changes many times a day (5,258 commits).

## How it is fast

Whole-program AOT analysis: type inference from literals, typed arrays and loop counters, fixed object layouts resolved at compile time, direct calls instead of dynamic dispatch, i32 narrowing of integer chains, and closure lowering, so the emitted Wasm has none of V8's type guards, hidden-class checks or GC barriers. Loops are vectorized to Wasm SIMD (v128) where possible, and from optimize level 2 float sum reductions are split into lanes (reassociated). Per-call arena rewinding replaces garbage collection.

## Compared with alternatives

Its siblings are Wasm engines (Wasmtime, WAMR, wasm3, Wasmi) and compilers from other source languages (wasm2c, AssemblyScript is its own baseline); pick jz when the source is JavaScript and you want it compiled to Wasm rather than run in a JIT or in an interpreter shipped inside Wasm (Javy, ComponentizeJS with weval). For C, C++ or Rust sources, compile them with their own toolchains and SIMD enabled.

## Integration

| | |
|---|---|
| **Form** | npm module (`jz` 0.9.2, ESM) with CLI; output is a .wasm module plus the optional `jz/interop` runtime |
| **Dependencies** | subscript ^10.8.1 and watr ^5.11.9 (compiler only); the emitted module needs only `jz/interop` for value marshalling, or nothing for raw numeric exports |
| **Minimum toolchain** | Node with ES modules (no `engines` field declared); the output uses Wasm SIMD and tail calls by default (`optimize: { simd: false, tailCall: false }` or `--no-simd`/`--no-tail-call` for engines without them) |
| **Platforms** | Any Wasm engine with SIMD and tail calls (V8 in Node and browsers, wasmtime via `--host wasi`); wasm32 only (4 GiB memory, 2^31-1 array elements) |
| **Thread safety** | One instance is single-threaded; `memory: { shared: true }` compiles for threads and lowers Atomics to Wasm atomics, but strings, objects and Symbols stay local to their instance, and fixed-memory scratch storage belongs to one instance |
| **Drop-in for the baseline** | partial — the same .js source runs in V8 and compiles with jz, but only inside the supported subset, with the documented semantic differences, and callers go through `instantiate()`/exports instead of importing the module directly |

## Gotchas

- Harness flaw: in the committed bench/results.json, 54 of the 61 V8 rows carry no `measuredAt` provenance (carried from an earlier, unidentified run) while the jz rows were measured at e36aab3b; the partial-refresh anchor check re-measured only c-wasm on mat4 and fft and AssemblyScript on synth, never a V8 row, and the host recorded 25,065 MB swap and load average 7.92.
- The V8 baseline is the slowest JS JIT in the table (Deno, also V8, is close): Node v25.9.0 takes 1.22x the time of Bun and 1.25x that of JavaScriptCore by geomean over 57 cases, and more than 1.5x on 13-16 of them (mat4 8,498 vs 2,495 us on Bun; dispatch 8,797 vs 2,363 us), so jz's geomean ratio is 0.55 against Bun and 0.56 against JSC rather than 0.44 against V8 (derived from page data). Cases whose checksum fails drop out of every geomean, including webaudio, where jz is 11.6x slower than V8.
- Some of the biggest wins rely on float reassociation ('Float sums in lanes' from optimize level 2) that neither V8 nor the strict clang reference (-ffp-contract=off, no -ffast-math) may do: dotprod runs 148 us under jz vs 891 us native C vs 2,055 us V8, and its inputs are integer-valued so the reassociated sum cannot change the checksum. checksumF64 hashes only the low 32-bit word of every 128th f64 (for mat4, only out[0]), so parity checks are sparse.
- The README's cross-language claim (C, Rust and Zig compiled to Wasm about 2x behind jz) compares SIMD-less builds: bench.mjs builds c-wasm, rust-wasm and zig-wasm with no simd128 target feature while jz emits v128 by default. The bench README prose is also stale against results.json: it says native clang leads by 1.2x and V8 wins the deopt probes, but the committed data gives jz/native 0.96 over 50 cases and jz ahead of V8 on dispatch, shapes, wordcount, immutable and strbuild.

## Known shortcomings

- Kernels chosen by the author with a partial, mixed-vintage dataset (bench/results.json: 0.443 over 55 cases, 0.448 vs AssemblyScript, 0.498 under wasmtime; the page aggregate leaves out the lab rows at 0.42x V8); the host swap of 25,065 MB exceeds the project's own 4,096 MB gate, and V8 still wins the self-compile and deopt-probe rows. JavaScript-to-Wasm compiler.
- Enricher audit of bench/results.json: 54 of 61 V8 rows carry no measuredAt provenance and the anchor check never re-ran a V8 row; the host had 25,065 MB swap and load1 7.92. Node V8 is the slowest JIT in the harness (geomean 1.22x Bun's time, 1.25x JSC's), so jz vs Bun is 0.55 and vs JSC 0.56 (derived from page data). Rival c-wasm, rust-wasm and zig-wasm targets were built without simd128. The large wins rely on float reassociation (dotprod jz 148 us vs native C 891 us vs V8 2,055 us); integer inputs hide this from the checksum, and checksumF64 samples only every 128th f64. DIFF rows leave the geomean, including webaudio where jz is 11.6x slower than V8 with wrong output.

## Caveats and trade-offs

Compares compiled-to-Wasm code against V8 running the same JS on numeric kernels chosen by the author, with the project's own harness; ratios here are geometric means from results.json rows with parity 'ok' (the bench page jz.js.org was not opened). V8 loses mostly because of dynamic-typing overhead the JS subset removes, not because Wasm is a faster VM; V8 still wins the self-compile lab rows (watr, jessie) and the dynamic-JS deopt probes. results.json is flagged partial: mixed vintages (most jz rows measured at commit e36aab3b, most V8 rows carried from an earlier run) with timing anchors passing within 10%, but the host reported 25,065 MB swap use, above the project's own 4,096 MB claims-gate limit, so the project's own release gate would not accept this snapshot as release evidence. AssemblyScript ports use unchecked() array access while jz keeps bounds checks. Native clang -O3 still leads jz by about 1.2x geomean. The harness records a per-case verdict and treats rows within 1.05x as a tie. [retier] Compares compiled-to-Wasm code against V8 running the same JS on numeric kernels chosen by the author, with the project's own harness. Committed bench/results.json gives jz/native-C 0.96 over 50 cases and jz faster than V8 on the dispatch, shapes, wordcount, immutable and strbuild probes; the README prose claiming native clang leads 1.2x and V8 wins the deopt probes is stale. Node V8 is the slowest JIT in the harness (Bun and JSC about 1.2x faster), rivals were built without simd128, and the large wins rely on float reassociation.

Compiles a statically analyzable JavaScript subset: no GC (bump allocator), no eval or Proxy, fixed object shapes, regexes at build time, 32-bit array indices, 64-bit wrapping BigInt. Pre-1.0.

## Maintenance

Very active (commits daily up to 2026-10-06, 174 stars, 1 open issue) and MIT-licensed, but pre-1.0 and experimental with an unstable Wasm ABI; usable today for self-contained numeric kernels if you pin the version and re-test on upgrade.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (bench/&lt;case&gt;/&lt;case&gt;.js run by bench/bench.mjs, 5 warm-up runs then median of 21 timed runs, checksum-verified), and bench/results.json meta states CPU (Apple M4 Max), versions (node v25.9.0, clang 19.1.6, asc 0.28.19, jz 0.9.2) and every target's invocation and flags; the bench README's aggregate table gives jz/V8 0.42x and jz/AssemblyScript 0.45x.
- **Verifier notes:** Numbers reproduce exactly from bench/results.json (0.443 over 55, 0.448 over 50, wasmtime lane 0.498 over 52); the page's own aggregate excludes lab rows (0.42x V8). Shortcomings: author-chosen kernels, partial mixed-vintage dataset on a host above the project's own swap limit, V8 still faster on self-compile and deopt-probe rows.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** independent re-run with simd128-enabled rivals and full-output checksums
- **Pages the verifier opened:**
  - <https://github.com/dy/jz>
  - <https://github.com/dy/jz/commits/main>
  - <https://github.com/dy/jz/tree/main/bench>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/README.md>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/results.json>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/biquad/biquad.js>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/dy/jz>
  - <https://github.com/dy/jz/commits/main>
  - <https://github.com/dy/jz/issues>
  - <https://github.com/dy/jz/issues?q=is%3Aissue+is%3Aclosed>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/README.md>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/results.json>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/bench.mjs>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/_lib/benchlib.js>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/_lib/run-v8.mjs>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/biquad/biquad.js>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/dotprod/dotprod.js>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/dotprod/dotprod.c>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/mat4/mat4.js>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/bench/mat4/mat4.c>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/package.json>
  - <https://raw.githubusercontent.com/dy/jz/HEAD/LICENSE>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/dy/jz`) · [data/wave12/enrich/raw/github_com_dy_jz.json](../../../data/wave12/enrich/raw/github_com_dy_jz.json) (enrichment confidence 0.75)

</details>
