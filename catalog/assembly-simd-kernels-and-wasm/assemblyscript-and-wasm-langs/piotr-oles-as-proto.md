# as-proto

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `AssemblyScript (TypeScript)` · `MIT` · 🟡 stale

> Protobuf codec generated as AssemblyScript classes inside WebAssembly; encodes about 2.2x faster than protobuf.js but decodes slower.

| | |
|---|---|
| **Beats** | protobuf.js (reflect and static) and google-protobuf in Node.js/V8; also JSON string/buffer |
| **Claimed result** | Encoding: as-proto 1,295,297 ops/sec vs protobuf.js (static) 589,866 and (reflect) 589,073 (about 2.2x, derived from page data). The decoding (889,283 vs 1,375,425 and 1,308,310 ops/sec, as-proto slower) and combined encode+decode (548,291 vs 439,242 and 421,963 ops/sec) rows are struck: at the measured commit a70d19f the generated packed-repeated decoder computed its end as reader.ptr + reader.uint32() (reading ptr before the length varint), so the bench decode stopped one bool early, read the 7th bool byte as a fixed64 tag, skipped the double and the outer float field and read one byte past the buffer under noAssert; those rows timed an incorrect decode. |
| **Workload** | ts-proto's encode/decode/combined benchmark (bench/index.cjs, benchmark.js suite) on one small Test message (string, uint32, nested int32/int64/enum/sint32, repeated bool, double, float), with an as-proto case added that runs inside the wasm module |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 2.2 GHz (MacBook Pro 2015); Node.js version not stated |
| **Compiler and flags** | Build behind the README numbers: initial commit a70d19f (2022-01-04), AssemblyScript asc ^0.19.20, release target with converge false, noAssert; the current bench/data/assembly/asconfig.json (asc ^0.24.1, optimizeLevel 3, shrinkLevel 0, converge, noAssert, incremental runtime, ESM bindings) describes today's bench, which was never re-run. protobuf.js and google-protobuf on Node (version unstated). |
| **Adoption** | 40 stars |
| **Last commit** | 2023-03-24 |
| **Links** | [repository](https://github.com/piotr-oles/as-proto) · [benchmark](https://github.com/piotr-oles/as-proto#performance) |

## Verdict

On a 2015 MacBook Pro (Core i7 2.2 GHz, Node.js version not stated), ts-proto's benchmark.js suite with an added as-proto case encoded one small Test message at 1.30M ops/s inside wasm (asc 0.19-era build, optimizeLevel 3, incremental runtime, noAssert) vs 0.59M for protobuf.js static and reflect (2.2x), decoded at 0.89M vs 1.38M (1.5x slower) and ran encode plus decode at 0.55M vs 0.44M (1.25x). The as-proto rows reuse a message pre-built in wasm and never cross into JavaScript, the payload values differ slightly from protobuf.js's, and the decode and combined rows ran a decoder that misparsed the message's packed bool field.

## Use it when

- An AssemblyScript wasm module (plugin, edge worker, contract or guest) that must encode or decode protobuf itself without calling back into JavaScript.
- Encode-heavy paths with small messages of mostly scalar fields: the author's run shows 1.30M vs 0.59M ops/s for protobuf.js on one small message.
- Both ends are as-proto, or the peer accepts unpacked repeated scalars (as-proto writes proto3 repeated scalars unpacked unless [packed=true] is set).
- Messages that hold only primitives and nested messages, the case where the README says decoding also beats JavaScript.

## Skip it when

- JavaScript or TypeScript application code: the benchmark never crosses the JS-wasm boundary, and in real use every message would have to be marshalled into and out of wasm memory; use protobuf.js there.
- Decode-heavy workloads with strings and repeated fields: protobuf.js decoded 1.38M ops/s against as-proto's 0.89M on the author's run.
- Reading proto3 data from other encoders: proto3 packs repeated scalars by default, but the generator emits the packed decode path only for an explicit [packed=true], so packed data from protobuf.js, google-protobuf or C++ is misread (issue #55; fix PR #56 unmerged).
- Schemas that need oneof (issue #42 open), gRPC services, or reliable cross-package and well-known-type imports (issues #29, #30, #51 open).
- int64/uint64/sint64 fields whose values fall just under a varint byte boundary (see gotchas), or any project that needs an actively maintained codec.

## How it is fast

Encoding is two-pass: a FixedSizer walks the message once, recording the total length and every nested-message and string length in a varlen array, then FixedWriter allocates one exactly sized Uint8Array and writes varints and fixed-width fields with direct store&lt;T&gt; calls, taking each length prefix from the precomputed array, so nothing is backpatched or concatenated (protobuf.js instead builds a linked list of write ops and joins it in finish()). The generated code is monomorphic static calls on typed fields (u32, i64, f64) compiled ahead of time by asc at optimizeLevel 3 with @inline varint helpers and global reused WRITER/READER instances. Decoding allocates AssemblyScript objects, arrays and strings on its incremental GC heap, which the author blames for the decode loss.

## Compared with alternatives

It is the only protobuf codec in this category; pick it over json-as when an AssemblyScript module must speak protobuf rather than JSON, and accept that you are adopting a stale codebase with open decoder bugs.

## Integration

| | |
|---|---|
| **Form** | module (npm source packages: as-proto runtime compiled into your wasm, as-proto-gen protoc plugin) |
| **Dependencies** | protoc for code generation; the AssemblyScript compiler (asc); Node.js 10.4+ or a browser with WebAssembly at runtime |
| **Minimum toolchain** | AssemblyScript 0.23+ (CHANGELOG v0.6.0; the repo pins ^0.24.1); newer asc releases not documented; protoc 3.x (generated headers show 3.20.3 and 3.21.4) |
| **Platforms** | any WebAssembly host that runs asc output (Node.js, browsers, standalone wasm runtimes) |
| **Thread safety** | Not documented; Protobuf.encode and decode use global WRITER and READER singletons, so calls are not reentrant and are unsafe across shared-memory wasm threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark correctness: the README numbers date from the initial commit (a70d19f, 2022-01-04, asc ^0.19.20, release target with converge false) and were never re-run. In that code the generated packed-repeated decoder computed its end as reader.ptr + reader.uint32(), reading ptr before the length varint, so (simulating the 80 encoded bytes) the bench decode stopped one bool early, read the 7th bool byte as a fixed64 tag, skipped the double and the outer float field, and read one byte past the buffer with bounds checks stripped by noAssert. Results were discarded, so the decoding and combined rows time an incorrect decode; the encode row produced correct bytes.
- The same reader.ptr + reader.uint32() end is still on main in the explicit-packed and map-entry decoders, and proto3 default-packed repeated scalars are not recognized at all; issue #55 and fix PR #56 have been open since 2026-02-19.
- FixedSizer.varint64 uses half the correct limits for 5- to 9-byte varints, so 64-bit values in [2^34,2^35), [2^41,2^42), [2^48,2^49), [2^55,2^56) and [2^62,2^63) are sized one byte too long: nested length prefixes overstate by one and the top-level buffer gets a trailing zero byte (an invalid tag 0). Fix PR #57 is unmerged.
- Before v1.2.1 (2023-03-24) the generator marked primitive-only messages @unmanaged, which leaked one object per decode (issue #47); the benchmark's InnerInner was such a class when the README numbers were taken. Release builds with noAssert also remove FixedReader's bounds checks, so truncated or hostile input is read out of bounds silently.

## Known shortcomings

- README numbers match but as-proto loses decode 1.5x to protobuf.js; its cases run on a message pre-built in wasm with no JS-wasm marshalling; payloads differ slightly (enum, int64); the README reflect/static rows predate the current bench/index.cjs; no CPU model or Node version (asc ^0.24.1 -O3).
- Harness flaw: the README numbers come from the initial commit a70d19f (2022-01-04, asc ^0.19.20, converge false) and were never re-run; the old packed-bool decoder computed its end as reader.ptr + reader.uint32(), so the simulated bench decode loses the 7th bool, skips the double and float fields and reads one byte past the buffer under noAssert, which means the decoding and combined rows time an incorrect decode (the encode row is fine); InnerInner was @unmanaged then, leaking one object per decode (#47). Current main still has the same end bug in the explicit-packed and map decoders and cannot read proto3 default-packed data (#55, PR #56 unmerged); FixedSizer.varint64's limits are half the correct values (PR #57 unmerged), so some 64-bit values are sized one byte too long and corrupt output. The record's compiler_and_flags described today's bench, not the build behind the numbers.

## Caveats and trade-offs

Mixed result: wins encoding (about 2.2x) and the combined case (about 1.3x), loses decoding by about 1.5x (889,283 vs 1,375,425 ops/sec for protobuf.js static); the README blames AssemblyScript's simple GC. The as-proto cases encode and decode a message pre-built inside wasm and discard the result, so they include no JS-to-wasm marshalling, while protobuf.js and google-protobuf encode a JS object; this matches as-proto's use from AssemblyScript code but is not a like-for-like JS API comparison. The payloads differ slightly: the AS message uses Enum.ONE (0, a proto3 default that is not written to the wire) and int64 682671883329470464, while bench.json uses enum 1 and int64 649545084044315. The README table has separate protobuf.js reflect and static rows, but the current bench/index.cjs runs only one protobuf.js (static) case, so the published numbers come from an earlier version of the script. Hardware is a 2015 laptop with no CPU model and no Node.js version; first-party only. [retier] Mixed result even where valid: as-proto wins encoding (about 2.2x) while its decoding rows measured a buggy decode and the README blames AssemblyScript's GC for the decode loss. The as-proto cases encode and decode a message pre-built inside wasm and discard the result (no JS-to-wasm marshalling), while protobuf.js and google-protobuf encode a JS object, so this is not a like-for-like JS API comparison; the payloads differ slightly (Enum.ONE is a proto3 default that is not written). The README numbers were never re-run after the initial commit; InnerInner was @unmanaged then, leaking one object per decode (issue #47, fixed in v1.2.1). Current main still has the same end bug in the explicit-packed and map-entry decoders and cannot read proto3 default-packed repeated scalars (issue #55, fix PR #56 open since 2026-02-19); FixedSizer.varint64 uses half the correct limits for 5- to 9-byte varints, so 64-bit values in several ranges are sized one byte too long and corrupt output (fix PR #57 unmerged). Release builds with noAssert remove FixedReader's bounds checks.

Generates AssemblyScript message classes from .proto files; no gRPC definitions. Decoding is slower than protobuf.js on the author's run. AssemblyScript's small GC is the usual limit on allocation-heavy paths.

## Maintenance

Stale since 2023-03-24 (npm as-proto 1.3.0, MIT, small enough to vendor), with three community fix PRs (#56 packed decoding, #57 varint64 sizer, #58 tests) unmerged since February 2026; the record's compiler_and_flags (asc ^0.24.1, converge true) describe today's bench script, not the 2022 build behind the numbers, whose decode and combined rows timed an incorrect decode and should not be relied on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark.js results in the README Performance section, from public code (bench/index.cjs, bench/suite.cjs, bench/data/assembly/static_aspr.ts, asc flags in bench/data/assembly/asconfig.json), but the CPU is given only as 'Intel Core i7 2.2 GHz (MacBook Pro 2015)' with no model and the Node.js version is not stated, so not A.
- **Verifier notes:** Numbers on the README match the record exactly; baseline (protobuf.js and google-protobuf in V8) fits the category's JS-in-V8 baseline. Shortcomings for the orchestrator: decode slower than protobuf.js, in-wasm benchmark without boundary crossing, slightly different payloads, README numbers predate the current bench script, no CPU model or Node version; repo stale since 2023-03-24.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-19 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/piotr-oles/as-proto>
  - <https://github.com/piotr-oles/as-proto/commits>
  - <https://github.com/piotr-oles/as-proto/tree/main/bench>
  - <https://github.com/piotr-oles/as-proto/tree/main/bench/data>
  - <https://github.com/piotr-oles/as-proto/tree/main/bench/data/assembly>
  - <https://github.com/piotr-oles/as-proto/commits/main/bench/index.cjs>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/README.md>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/index.cjs>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/suite.cjs>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/prepare.js>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/package.json>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/assembly/static_aspr.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/assembly/asconfig.json>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/bench.json>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/bench.proto>
- **Sources the enricher read:**
  - <https://github.com/piotr-oles/as-proto>
  - <https://github.com/piotr-oles/as-proto/issues?q=is%3Aissue>
  - <https://github.com/piotr-oles/as-proto/issues/47>
  - <https://github.com/piotr-oles/as-proto/issues/55>
  - <https://github.com/piotr-oles/as-proto/pulls>
  - <https://github.com/piotr-oles/as-proto/pull/49/files>
  - <https://github.com/piotr-oles/as-proto/pull/56/files>
  - <https://github.com/piotr-oles/as-proto/pull/57/files>
  - <https://github.com/piotr-oles/as-proto/commits/main/README.md>
  - <https://github.com/piotr-oles/as-proto/tree/main/packages/as-proto-gen/src>
  - <https://github.com/piotr-oles/as-proto/tree/main/packages/as-proto/assembly>
  - <https://github.com/piotr-oles/as-proto/tree/main/packages/as-proto/assembly/internal>
  - <https://github.com/piotr-oles/as-proto/tree/a70d19f/bench>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/README.md>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/package.json>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/index.cjs>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/suite.cjs>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/prepare.js>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/assembly/static_aspr.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/assembly/asconfig.json>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/bench.json>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/bench.proto>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/assembly/generated/Outer.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/assembly/generated/Test.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/bench/data/assembly/generated/Test/Inner/InnerInner.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/packages/as-proto/package.json>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/packages/as-proto/assembly/Protobuf.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/packages/as-proto/assembly/Reader.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/packages/as-proto/assembly/Writer.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/packages/as-proto/assembly/internal/FixedReader.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/packages/as-proto/assembly/internal/FixedWriter.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/packages/as-proto/assembly/internal/FixedSizer.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/packages/as-proto-gen/src/generate/field.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/HEAD/packages/as-proto-gen/src/generate/message.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/README.md>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/46ab0fb/README.md>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/49e6e2d/README.md>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/c039104/README.md>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/package.json>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/bench/index.js>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/bench/data/bench.json>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/bench/data/static_aspr.js>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/bench/as-proto/asconfig.json>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/bench/as-proto/assembly/static_aspr.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/bench/as-proto/assembly/generated/bench.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/packages/as-proto/assembly/Reader.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/packages/as-proto/assembly/Protobuf.ts>
  - <https://raw.githubusercontent.com/piotr-oles/as-proto/a70d19f/packages/as-proto/assembly/internal/FixedReader.ts>
  - <https://registry.npmjs.org/as-proto>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/piotr-oles/as-proto`) · [data/wave13/enrich/raw/github_com_piotr_oles_as_proto.json](../../../data/wave13/enrich/raw/github_com_piotr_oles_as_proto.json) (enrichment confidence 0.8)

</details>
