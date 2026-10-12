# json-as

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `AssemblyScript` · `MIT` · 🟢 active

> Schema-compiled JSON (de)serializer for AssemblyScript; on real payloads about 1-1.7x V8's JSON on 1-5 kB inputs, 3-6x on tiny ones.

| | |
|---|---|
| **Beats** | JavaScript built-in JSON.parse / JSON.stringify in V8 (also fast-json-parse and assemblyscript-json) |
| **Claimed result** | Author's default-values charts (v1.5.0 run, commit 0bb47d4, non-default payloads, MB/s): deserialize SWAR 5.5 kB 1,324 vs V8 JSON.parse 1,295 (about 1.0x), 1.1 kB 598 vs 568 (about 1.05x); serialize SIMD 5.5 kB 3,161 vs 1,062 (about 3.0x), 1.1 kB 1,996 vs 696 (about 2.9x) (derived from page data). v1.6.1 rewritten benches: deserialize 5.3 kB 2,122-2,251 vs 1,883 MB/s (about 1.1-1.2x), 1.1 kB 761-765 vs 804 (slower); serialize 4,111-4,942 vs 3,794 (about 1.1-1.3x) and 2,571-2,622 vs 1,580 (about 1.6x). The README's headline charts (deserialize 5,734 vs 1,295 and 1,321 vs 568 MB/s; serialize 7,775 vs 1,062 and 3,818 vs 696; library comparison 5,636 vs 547, v1.6.1 12,946 vs 647) use payloads equal to the benchmark classes' declared defaults and are special-cased by the generated code (no decode, no allocation, constant stores; since v1.6.0 a whole-document default match returns a default-constructed object without parsing). |
| **Workload** | End-to-end JSON deserialize (including allocating the destination object) and serialize throughput in MB/s on small payloads (19 B to 5.5 kB) and nine standard payloads from the yyjson and nativejson-benchmark corpora, with json-as compiled to Wasm by the AssemblyScript compiler (asc) and run in V8. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 7800X3D (8 cores, 96 MB 3D V-Cache), 32 GB RAM, Linux 6.17 (README) |
| **Compiler and flags** | asc (assemblyscript ^0.28.18 in package.json) -O3 --noAssert --uncheckedBehavior always --runtime incremental --enable bulk-memory --exportStart start --exportRuntime (plus --enable simd in SIMD mode), then wasm-opt -O4 -tnh -iit -ifwl -s 0 with bulk-memory/nontrapping-float-to-int/tail-call/sign-ext/mutable-globals enabled (current scripts/run-bench.as.sh); AS modules run under d8 --no-liftoff, JS baselines under d8 --no-liftoff --no-wasm-tier-up --allow-natives-syntax (scripts/run-bench.js.sh); chart footer: v8 15.1.42, commit 0bb47d4, Jul 17 2026. Scripts are read at HEAD; the flags used at 0bb47d4 were not checked. |
| **Adoption** | 113 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/JairusSW/json-as) · [benchmark](https://github.com/JairusSW/json-as) |

## Verdict

First-party d8 benchmarks (asc ^0.28.18 -O3 --noAssert --uncheckedBehavior always plus wasm-opt -O4, Ryzen 7 7800X3D, Linux 6.17). In the README-linked v1.5.0 run (V8 15.1.42, Jul 17 2026) the headline 5,734 vs 1,295 MB/s deserialize and 7,775 vs 1,062 MB/s serialize figures were measured on payloads equal to the classes' compile-time defaults; the same run's non-default variants give 1,324-1,385 vs 1,295 MB/s deserialize and 2,709-3,161 vs 1,062 MB/s serialize at 5.5 kB. The rewritten v1.6.1 run (V8 15.2.20, Oct 3 2026) gives 2,122-2,251 vs 1,883 MB/s deserialize and 4,111-4,942 vs 3,794 MB/s serialize at 5.3 kB, 761-765 vs 804 deserialize and 2,571-2,622 vs 1,580 serialize at 1.1 kB, and 3-6x on 19-52 B inputs, where V8's numbers carry the per-operation eval overhead.

## Use it when

- AssemblyScript services, plugins or smart contracts (WASI, edge runtimes, Wasm VMs) that exchange JSON with a fixed schema; the users listed in the README include Impart Security, Hypermode and several blockchain VMs.
- Serialization-heavy paths: the v1.6.1 chart (Oct 2026, rewritten non-default benches) shows SWAR/SIMD stringify at 2,571-2,622 vs 1,580 MB/s for V8 on a 1.1 kB object (1.6x) and 4,111-4,942 vs 3,794 MB/s on 5.3 kB (1.1-1.3x).
- Small messages (19-108 bytes, tokens, UUIDs, vectors) inside Wasm, where the charts show 3-6x over V8's JSON (an upper bound, because the JS harness adds an eval per operation).
- Proxy, filter or forward workloads that read a few fields and re-emit the rest: lazy fields and the lazy `JSON.Obj` copy untouched source bytes straight through.
- Any AssemblyScript project currently on assemblyscript-json, which the same charts place at 32-43 MB/s versus thousands of MB/s for json-as.

## Skip it when

- JavaScript applications hoping to beat `JSON.parse`: the string must cross the JS/Wasm boundary (a copy the benchmark never pays), and on 1.1 kB payloads json-as deserialize is at parity or slower even inside Wasm (761-765 vs 804 MB/s, v1.6.1 chart).
- Input that is pretty-printed, reordered or carries unknown keys: it falls off the exact tier-1 template to slower tiers, and the transform's own comment puts the scalar slow path at about 5x slower.
- Untrusted input in a build copied from the benchmarks: those use --noAssert, --uncheckedBehavior always and wasm-opt -tnh/-iit; strict validation is opt-in (`JSON_STRICT`), and issue #191 (failure on &gt;1 MiB arrays containing null) is still open.
- Unknown or highly dynamic documents that you read in full: the dynamic `JSON.Obj` path defers work rather than removing it, and the eager struct path needs a declared class.
- Very wide schemas with `@json({ lazy: "auto" })`: the README warns stock Binaryen can crash optimizing the generated code.

## How it is fast

Codegen at build time: key bytes are packed into u64/v128 immediates and matched with direct loads, fields are dispatched by key length, and the tier-1 deserializer is an exact byte template for minified input in declaration order (with whitespace-tolerant, order-independent and scalar slow-path fallbacks). Scanning for quotes and escapes runs in one of three compile-time backends: NAIVE scalar, SWAR (64-bit words) or Wasm SIMD128 (`JSON_MODE`). Serialization writes into one reusable growable buffer (`bs`) with precomputed key bytes, floats go through the xjb64/Schubfach-based xjb-as writer, and string fields whose value is the declared default literal are emitted (or, when parsing, matched) as precomputed constants.

## Compared with alternatives

Pick json-as for JSON inside AssemblyScript (it is the fast option there, far ahead of assemblyscript-json); use as-proto instead when you control both ends and can switch to protobuf, and VectorJSON when the caller is JavaScript code parsing streaming JSON, since json-as only pays off when the data already lives in Wasm memory. It pairs with as-str (same author) for string slicing around the parsed values.

## Integration

| | |
|---|---|
| **Form** | module (npm package of AssemblyScript source plus a required asc transform, `--transform json-as`) |
| **Dependencies** | xjb-as ^0.1.0 (float formatting); AssemblyScript compiler with the bundled transform |
| **Minimum toolchain** | AssemblyScript asc 0.28.x (developed against ^0.28.18; issue #188 tracked a break with 0.28.16); SIMD mode needs --enable simd; mode, cache and strictness are chosen at compile time through environment variables (JSON_MODE, JSON_CACHE, JSON_STRICT, JSON_USE_FAST_PATH) |
| **Platforms** | any WebAssembly host (V8, Bun, Wasmtime, WAVM, wazero and WARP appear in the runtime chart); SIMD mode needs Wasm SIMD128 |
| **Thread safety** | not documented; the library keeps module-global state (the shared output buffer, parse traces and a last-default-source cache), so one Wasm instance should not parse re-entrantly from several threads |
| **Drop-in for the baseline** | partial — same JSON.parse/JSON.stringify names, but only for AssemblyScript code with @json-decorated classes compiled through the transform; it does not replace V8's JSON in JavaScript |

## Gotchas

- Harness flaw behind the headline numbers: the v1.5.0 charts the README links (commit 0bb47d4) used benchmark classes whose declared field defaults equal the payload, and the generated code special-cases string fields that equal their default literal (constant stores on serialize; byte compare plus static-string store, no decode or allocation, on parse). The author's own default-values charts from the same run show the gap: 5.5 kB deserialize SWAR 5,734 (default) vs 1,324 MB/s (non-default) against V8's 1,295; 1.1 kB 1,321 vs 598 against 568; serialize SIMD 7,775 vs 3,161 and 3,818 vs 1,996. So the deserialize gain on 1-5 kB payloads is about 1.0-1.07x, not 2.3-4.4x.
- The library-comparison bars rest on the same artifact: the 5,251-byte multilib payload is byte-identical to the compact JSON of the Repo class defaults (checked at 0bb47d4 and HEAD). Since v1.6.0 `JSON.parse<T>` first checks the whole input against that default JSON and caches the matching source pointer, returning a default-constructed object without parsing; this is how the v1.6.1 library chart reaches 12,946 MB/s vs 647 for V8, while the same run's 5.3 kB overview row is 2,122-2,251 MB/s.
- The JS arm's blackbox runs `(0, eval)("%PerformMicrotaskCheckpoint();")` on every timed operation, while the AS arm does a store and load. Measured here (Node 22.22, V8 12.4, Xeon 2.1 GHz): about 180 ns per call, which took vec3 JSON.parse from 290-334 to 590-608 ns and JSON.stringify from 174-183 to 415-485 ns. On the 5 kB payload it is lost in run-to-run noise. In the 0bb47d4 run the 'Small Payload (108b)' row also compared different documents: a 108 B default-valued SessionStatusResponse in AS against a 44 B SmallJSON in JS. The Alphabet and UUIDv4 serialize rows divide by the quoted length on the AS side and the unquoted length on the JS side (+3.8% and +5.6% for AS).
- Parse speed depends on input layout: the tier-1 template only fires for minified keys in declaration order. The 2026-10-05 fix PR #223 (odd-length key compare) touched only the slow path. The README's FAST_PATH_DESERIALIZE.md link returns 404.

## Known shortcomings

- Chart numbers match but the JS blackbox runs an indirect eval '%PerformMicrotaskCheckpoint();' every operation while the AS blackbox only stores and loads, so the small rows are inflated; typed structs vs generic objects; JSON.Obj bars are lazy; --noAssert and -tnh builds. The odd-key bug fixed 2026-10-04 (PR #223) touches only __DESERIALIZE_SLOW, so no cap.
- Harness flaw behind the headline numbers: the v1.5.0 charts (commit 0bb47d4) benchmarked classes whose field defaults equal the payload, and the generated code special-cases default string literals (no decode, no allocation, constant stores); the author's own default-values charts from the same run show 5.5 kB deserialize SWAR 5,734 (default) vs 1,324 MB/s (non-default) against V8's 1,295, 1.1 kB 1,321 vs 598 against 568, serialize SIMD 7,775 vs 3,161 and 3,818 vs 1,996. The library-comparison payload is byte-identical to the Repo class defaults, and since v1.6.0 a whole-document default match plus source-pointer cache returns the default object without parsing (v1.6.1 library chart 12,946 vs 647 MB/s). The JS arm's blackbox runs an indirect eval per timed op (about 180 ns per call measured on Node 22.22); the 108 B row compared different documents. v1.6.1 rewritten benches: deserialize 5.3 kB 2,122-2,251 vs 1,883 MB/s, 1.1 kB 761-765 vs 804 (slower); serialize 4,111-4,942 vs 3,794 and 2,571-2,622 vs 1,580.

## Caveats and trade-offs

First-party: the benchmark author is the library author. Chart values exist only in images (SVG and PNG on the docs branch, charts/v1.5.0), not in a text table. The JS baseline parses into generic JavaScript objects while json-as parses into typed structs generated at build time, so the work differs. Harness asymmetry: the JS blackbox() in bench/lib/bench.js runs an indirect eval of '%PerformMicrotaskCheckpoint();' on every timed op, while the AS blackbox is a single store/load, which inflates JS per-op time most on the 19-108 byte rows (JS ops there take only about 125-640 ns); the 5.5 kB rows are least affected. Benchmark builds use --noAssert, --uncheckedBehavior always and wasm-opt -tnh/-iit, which drop assertion and trap checks. The JSON.Obj path is lazy by default since v1.5.0 (values parsed on first access, untouched values re-serialized by copying source bytes), so its deserialize and serialize bars (up to 19,968 MB/s) defer work and are not like-for-like; on the 3D Vector row JSON.Obj ties built-in JSON (82 vs 83 MB/s), and the 0 values on the Alphabet and UUIDv4 rows mean no JSON.Obj run, not a loss. In the library chart fast-json-parse wraps JSON.parse, which is why it equals native JSON (547 MB/s). The SIMD mode is slower than SWAR on several deserialize rows (Small Payload 1,089 vs 2,196 MB/s). A key-matching correctness bug (final UTF-16 unit of odd-length keys longer than 4 units not compared) was fixed on 2026-10-04 (PR #223), after the charted run; the fix is in toMemCCheck/toMemCDecl, which only the generated __DESERIALIZE_SLOW fallback uses, and the AS large bench asserts a byte-exact round trip, so the charted fast-path numbers are not capped by it. Charts dated Jul 17 2026 (commit 0bb47d4); main has moved to 1.6.1 since. [retier] First-party: the benchmark author is the library author, and chart values exist only in images. Harness flaw: the v1.5.0 charts (commit 0bb47d4) benchmarked classes whose declared field defaults equal the payload, and the generated code special-cases string fields equal to their default literal (constant stores on serialize; byte compare plus static-string store, no decode or allocation, on parse); the 5,251-byte library-comparison payload is byte-identical to the Repo class defaults (checked at 0bb47d4 and HEAD), and since v1.6.0 JSON.parse&lt;T&gt; first checks the whole input against that default JSON and caches the matching source pointer, returning a default-constructed object without parsing. The JS arm's blackbox runs (0, eval)('%PerformMicrotaskCheckpoint();') on every timed operation while the AS arm does a store and load: about 180 ns per call measured on Node 22.22 (vec3 JSON.parse 290-334 to 590-608 ns), lost in noise only on the 5 kB payload. In the 0bb47d4 run the 'Small Payload (108b)' row compared different documents (108 B in AS vs 44 B in JS), and the Alphabet and UUIDv4 serialize byte counts differ (AS +3.8%, +5.6%). The JS baseline parses into generic objects while json-as parses into typed structs generated at build time; the tier-1 template only fires for minified keys in declaration order. Benchmark builds use --noAssert, --uncheckedBehavior always and wasm-opt. The README's FAST_PATH_DESERIALIZE.md link returns 404.

Typed, schema-driven (struct) API: the build-time transform generates a specialised serializer per @json class, so it only competes with JSON.parse when the schema is known up front; dynamic JSON.Obj path is slower. Needs AssemblyScript toolchain and a Wasm host; builds use --noAssert and --uncheckedBehavior always, which removes bounds and assert checks. SIMD mode needs Wasm SIMD support.

## Maintenance

Actively maintained (v1.6.1 on npm 2026-09-01, last commit 2026-10-05, 113 stars, 1 open issue, MIT) and used in production by several companies; the codec is real and fast, but the README's charts overstate the gain over V8's JSON: re-measure with non-default payloads, and record the corrected figures (and a possible retier) in a retier file.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** The README Performance section compares json-as with V8's built-in JSON.parse/JSON.stringify; the benchmark code is public (assembly/__benches__/\*.bench.ts for AS, bench/\*.bench.ts for JS, driven by scripts/run-bench.as.sh and scripts/run-bench.js.sh), the compiler and flags are in those scripts (asc ^0.28.18 -O3 --noAssert --uncheckedBehavior always, wasm-opt -O4), the engine is d8 v8 15.1.42 and the CPU is a Ryzen 7 7800X3D. All of code, compiler, flags and CPU model are stated, so A, with harness asymmetries documented below.
- **Retiered** A to C: Enricher: the v1.5.0 charts (commit 0bb47d4) used benchmark classes whose field defaults equal the payload, and the generated code special-cases default string literals (no decode, no allocation), so the headline rows measure a degenerate workload (ThreadPool / zero-field precedent); the author's own non-default charts from the same run show parse parity with V8 and about 3x on serialize; the JS blackbox adds an eval per timed op. First-party harness with a degenerate workload: A to C, claim corrected to the non-default and v1.6.1 figures.
- **Verifier notes:** Every claimed figure matches the charts: deserialize SWAR vs built-in JSON 1,321 vs 568 (1.1 kB), 5,734 vs 1,295 (5.5 kB), 2,196 vs 168 (108 B), 1,056 vs 401 MB/s (52 B); serialize SIMD 7,775 vs 1,062 and 3,818 vs 696 MB/s; library chart 5,636 vs 547 MB/s; 3D Vector 356-444 vs 83 and JSON.Obj 82 vs 83. Metadata: MIT, 113 stars, not a fork, last commit 2026-10-05 (active). Shortcomings to record: per-op eval in the JS harness only, typed-struct vs generic-object work, lazy JSON.Obj bars, unchecked builds (--noAssert, -tnh), first-party.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-04 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/JairusSW/json-as>
  - <https://github.com/JairusSW/json-as/commits/main>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/README.md>
  - <https://github.com/JairusSW/json-as/tree/docs/charts/v1.5.0>
  - <https://raw.githubusercontent.com/JairusSW/json-as/refs/heads/docs/charts/v1.5.0/overview-deserialize.png>
  - <https://raw.githubusercontent.com/JairusSW/json-as/refs/heads/docs/charts/v1.5.0/overview-serialize.png>
  - <https://raw.githubusercontent.com/JairusSW/json-as/refs/heads/docs/charts/v1.5.0/library-deserialize.png>
  - <https://raw.githubusercontent.com/JairusSW/json-as/refs/heads/docs/charts/v1.5.0/overview-deserialize.svg>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/scripts/run-bench.as.sh>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/scripts/run-bench.js.sh>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/package.json>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/bench/lib/bench.js>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/bench/large.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/bench/runners/assemblyscript.js>
  - <https://github.com/JairusSW/json-as/tree/main/assembly/__benches__>
  - <https://github.com/JairusSW/json-as/tree/main/assembly/__benches__/lib>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/large.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/lib/bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/transform/src/index.ts>
  - <https://github.com/JairusSW/json-as/pull/223>
  - <https://github.com/JairusSW/json-as/pull/223/files>
- **Sources the enricher read:**
  - <https://github.com/JairusSW/json-as>
  - <https://github.com/JairusSW/json-as/pulls?q=is%3Apr>
  - <https://github.com/JairusSW/json-as/issues?q=is%3Aissue>
  - <https://github.com/JairusSW/json-as/commit/0bb47d4>
  - <https://github.com/JairusSW/json-as/tree/main/bench>
  - <https://github.com/JairusSW/json-as/tree/main/assembly/__benches__/classic>
  - <https://github.com/JairusSW/json-as/tree/main/assembly/__benches__/multilib>
  - <https://github.com/JairusSW/json-as/tree/0bb47d4aaf3b496346de25117af7c33ab0c33e33/scripts>
  - <https://github.com/JairusSW/json-as/tree/docs/charts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/README.md>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/package.json>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/FAST_PATH_DESERIALIZE.md>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/scripts/run-bench.as.sh>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/scripts/run-bench.js.sh>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/bench/lib/bench.js>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/bench/large.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/bench/vec3.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/bench/abc.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/bench/small.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/bench/runners/assemblyscript.js>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/index.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/deserialize/parseMode.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/transform/src/index.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/lib/bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/large.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/small.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/vec3.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/abc.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/token.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/classic/twitter.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/multilib/shared.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/multilib/json-as-struct-deserialize.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/multilib/json-as-struct-deserialize-reuse.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/HEAD/assembly/__benches__/payloads/multilib.json>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/bench/lib/bench.js>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/bench/small.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/bench/medium.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/bench/large.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/bench/token.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/bench/uuidv4.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/bench/vec3.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/bench/abc.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/index.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/transform/src/index.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/scripts/run-bench.as.sh>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/scripts/run-bench.js.sh>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/scripts/build-overview-serialize.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/scripts/build-overview-deserialize.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/scripts/build-default-values.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/scripts/build-library-deserialize.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/lib/bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/lib/nondefault.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/small.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/medium.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/large.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/token.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/uuidv4.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/vec3.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/abc.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/multilib/shared.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/multilib/json-as-struct-deserialize.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/json-as/0bb47d4aaf3b496346de25117af7c33ab0c33e33/assembly/__benches__/payloads/multilib.json>
  - <https://raw.githubusercontent.com/JairusSW/json-as/refs/heads/docs/charts/v1.5.0/overview-deserialize.png>
  - <https://raw.githubusercontent.com/JairusSW/json-as/refs/heads/docs/charts/v1.5.0/default-values-serialize.png>
  - <https://raw.githubusercontent.com/JairusSW/json-as/refs/heads/docs/charts/v1.5.0/default-values-deserialize.png>
  - <https://raw.githubusercontent.com/JairusSW/json-as/refs/heads/docs/charts/v1.6.1/overview-deserialize.png>
  - <https://raw.githubusercontent.com/JairusSW/json-as/refs/heads/docs/charts/v1.6.1/overview-serialize.png>
  - <https://raw.githubusercontent.com/JairusSW/json-as/refs/heads/docs/charts/v1.6.1/library-deserialize.png>
  - <https://registry.npmjs.org/json-as>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jairussw/json-as`) · [data/wave13/enrich/raw/github_com_jairussw_json_as.json](../../../data/wave13/enrich/raw/github_com_jairussw_json_as.json) (enrichment confidence 0.8)

</details>
