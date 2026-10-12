# JSBT (@cheprasov/jsbt)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `TypeScript` · `MIT` · 🟢 active

> Schemaless JS-to-JS binary serializer that keeps object graphs and deduplicates repeated subtrees; much smaller than Protobuf on repetitive data.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | JSBT output is about 48x smaller than Protobuf (64,175 bytes vs 3,108,000 bytes) on a 10,000-object repetitive dataset, via structural deduplication and graph references (verbatim numbers from README benchmarks table) |
| **Workload** | Serializing 10,000 similar/repetitive JavaScript objects (financial/logging-style data with shared structure) and comparing on-wire size across JSON, Protobuf, MsgPack, CBOR, and JSBT |
| **Metric** | memory |
| **Adoption** | 36 stars |
| **Last commit** | 2026-04-05 |
| **Links** | [repository](https://github.com/cheprasov/ts-jsbt) · [benchmark](https://github.com/cheprasov/ts-jsbt#benchmarks) |

## Verdict

The size comparison with Protobuf comes only from README scenario 3: 10,000 repetitive objects encode, uncompressed, to 64,175 bytes with JSBT versus 3,108,000 with Protobuf (about 48x), 3,708,003 with MsgPack, 3,775,603 with CBOR and 4,680,335 with JSON. It was a single run 'on Node.js' with no Node version, hardware, or Protobuf library or schema stated, and the published harness (benchmarks/benchmark1.ts) runs only JSON and JSBT. In that harness's repeated dataset every field depends only on i mod 100 or i mod 3, so just 300 of the 10,000 records are distinct and the rest encode as short copy refs. The 48x therefore mostly measures whole-record dedup, not general compactness.

## Use it when

- Both ends are JS/TS and you control both: Node to Node, Node to browser, Web Workers or worker threads, Electron IPC.
- Payloads are large arrays of records in which many sub-objects or whole records are exact duplicates (logs, market or order-book snapshots, analytics exports). Here dedup can cut wire or storage size by an order of magnitude or more compared with JSON, Protobuf or MsgPack.
- You need to round-trip JS types that JSON drops (Map, Set, Date, BigInt, TypedArrays, undefined, NaN, -0) or object graphs with cycles and shared references, with identity preserved.
- Snapshotting in-memory state (caches, graphs) where size at rest matters more than CPU time spent encoding.
- You want compact binary without maintaining .proto schemas or a codegen step.

## Skip it when

- Cross-language or schema-evolution contracts: the only implementation is TypeScript/JavaScript. Use Protobuf, Avro or Thrift, as the README itself advises.
- Latency- or CPU-bound paths with small or flat messages. On the README's flat-object test JSBT is about 9.6x slower to encode than Protobuf (31.51 vs 3.29 us/op), about 10.7x slower to decode (20.83 vs 1.95 us/op), and also larger (1,398 vs 1,017 bytes).
- Large payloads with few repeats. The encoder keeps every subtree's encoded string as a Map key, so encode time and memory grow with payload size. The README reports about 1,029 ms per encode for its 10,000-object repeated dataset.
- Decoding untrusted input. A copy ref is expanded by re-decoding the referenced byte range, and the code I read has no expansion limit, so a small payload can decode into a very large heap. The README's security notes do not mention this.
- When you need a small decoded heap. Copy refs decode into fresh objects, so structural dedup shrinks only the wire or stored form. Only same-identity (link) refs stay shared after decode.

## How it is fast

The size win comes from two dedup layers in the encoder, which is a form of content-addressed dedup or hash-consing. First, every value gets a ref ID, and a Map keyed by the value itself (object identity, or the value for longer strings, larger integers and floats) emits a short 'link' ref when that value appears again. Second, a Map keyed by each subtree's already-encoded bytes emits a 'copy' ref when an identical subtree was written before, but only if the ref is shorter than the bytes. Everything else is a 1-byte type/length tag followed by minimal little-endian bytes: variable-width integers, trimmed floats and UTF-8 strings. It is not faster: the encoder builds every subtree's encoding as a string and looks it up in a Map, which makes encoding about 10x slower than Protobuf on a flat object.

## Compared with alternatives

Choose JSBT over the catalog's other size-focused entries only when both endpoints are JavaScript and you want no schema plus graph and identity preservation. JSON BinPack gets its size wins from a schema and was the smallest or tied-smallest on 27 documents, and qdf reports wire-size wins over protobuf on 5 batch fixtures; both results are broader than JSBT's single dataset, which favours dedup.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (runtime); devDependencies are the TypeScript, tsup and jest toolchain |
| **Minimum toolchain** | ES2020 runtime (the tsup build targets es2020); TextEncoder is required for string encoding; package.json has no engines field; ships ESM and CJS builds with .d.ts typings |
| **Platforms** | any JS runtime; the README names Node, browsers, Web Workers and Electron |
| **Thread safety** | not documented. encode and decode create fresh state on each call, but class factories are a process-global static set through JSBT.setClassFactories |
| **Drop-in for the baseline** | no |

## Gotchas

- JSBT.encode returns a JS string with one char per byte (0-255), not a Uint8Array, and decode does not accept Uint8Array or ArrayBuffer. Byte output (encodeToBytes) and Uint8Array input exist only in the open, unmerged v1.4.0 PR #2. If the string goes through a UTF-8 path (for example Buffer.byteLength or a text frame), every byte at 0x80 or above becomes 2 bytes, so convert it as latin1/binary.
- Integers beyond Number.MAX_SAFE_INTEGER throw, so use BigInt for them. Local (non-global) symbol keys on objects are not encoded.
- Any object whose constructor.name is not 'Object' is treated as a class instance and serialized through toJSBT(), toJSON() or valueOf(). On decode, a class name with no registered factory comes back as a plain object carrying a non-enumerable __jsbtConstructorName.
- During decode, ByteStream keeps every input byte in a JS number array so that copy refs can re-parse their byte slices. Expect decode-time memory well above the payload size.

## Known shortcomings

- Size-only win on a dataset built to favour deduplication (uncompressed sizes); the published harness runs only JSON and JSBT, so the Protobuf/MsgPack/CBOR rows cannot be reproduced. JSBT encodes about 10x slower than Protobuf on simple objects (31.51 vs 3.29 us/op). The README gives two different JSBT sizes.
- The 48x is mostly record dedup: only 300 of 10,000 benchmark records are distinct. Output is a one-char-per-byte JS string, not a Uint8Array. Copy refs are expanded on decode with no limit, so a small payload could decode into a very large heap. About 34 npm downloads a month.

## Caveats and trade-offs

Author states the benchmarks are 'synthetic and indicative, not absolute' and were 'run on Node.js'; no hardware, Node version, or Protobuf library/schema details given. The public benchmark harness (benchmarks/benchmark1.ts) only compares JSON vs JSBT; the Protobuf, MsgPack and CBOR rows in the README tables have no published harness. The repeated dataset is built to favor deduplication (id i%100, name i%50, one shared scores array, identical tags/meta), and sizes are uncompressed (no gzip/zstd comparison). The win is compactness only, not speed: on the README's simple-flat-object table JSBT encode is 31.51 us/op vs Protobuf 3.29 us/op and decode 20.83 vs 1.95 us/op (roughly 10x slower); the repeated-data table gives timings for JSBT only (encode \~1,029 ms/op, decode \~43 ms/op), not for Protobuf. README is slightly inconsistent on the JSBT size (64,175 bytes / 62.7 KB in the table vs '\~60.5 kb' in the text below it).

JSBT is markedly SLOWER per-operation than Protobuf on simple flat objects (31.51 microseconds/op encode vs Protobuf's 3.29 microseconds/op in the project's own table); the size win only materializes for highly repetitive/graph-shaped data; JS/TS runtime-only, not cross-language like Protobuf

## Maintenance

Actively maintained by one person: v1.3.2 was released 2026-04-05, and an open v1.4.0 PR since 2025-12 adds Uint8Array I/O. It is MIT-licensed with zero runtime dependencies and installable from npm, but adoption is low (36 stars, about 34 npm downloads a month) and there are no independent benchmarks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** README 'Benchmarks' section scenario 3 shows the exact sizes (Protobuf 3,108,000 bytes vs JSBT 64,175 bytes, '48x smaller than Protobuf'), but methodology is only 'run on Node.js', no CPU/Node version, and the public harness benchmarks/benchmark1.ts only runs JSON and JSBT, so the Protobuf/MsgPack/CBOR rows are not reproducible from published code: first-party, partial methodology = C.
- **Verifier notes:** Numbers and repo metadata (MIT, 36 stars, not fork/archived, last commit 2026-04-05, active) all check out. Only the caveats needed tightening: the earlier claim that JSBT is slower than Protobuf 'on the same tables' holds only for the simple-object table, and the Protobuf comparison code is not public.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cheprasov/ts-jsbt#benchmarks>
  - <https://github.com/cheprasov/ts-jsbt>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/benchmarks/benchmark1.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/package.json>
- **Sources the enricher read:**
  - <https://github.com/cheprasov/ts-jsbt>
  - <https://github.com/cheprasov/ts-jsbt#benchmarks>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/specification.md>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/package.json>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/tsconfig.base.json>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/JSBT.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/index.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/encoder/encode.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/encoder/encodeRef.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/encoder/encodeObject.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/encoder/encodeArray.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/encoder/encodeString.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/encoder/encodeClassInstance.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/encoder/options/createEncodeOptions.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/types/IEncodeOptions.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/types/IDecodeOptions.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/decoder/decode.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/decoder/decodeRef.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/decoder/decodeObject.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/reader/ByteStream.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/utils/toChar.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/utils/vars/isClassInstance.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/src/_tests/testCases/jsbt-real-world-data.test.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/benchmarks/benchmark1.ts>
  - <https://github.com/cheprasov/ts-jsbt/blob/master/benchmarks/micro.ts>
  - <https://github.com/cheprasov/ts-jsbt/issues>
  - <https://github.com/cheprasov/ts-jsbt/pulls>
  - <https://github.com/cheprasov/ts-jsbt/pull/2>
  - <https://github.com/cheprasov/ts-jsbt/commits/master>
  - <https://github.com/cheprasov/ts-jsbt/releases>
  - <https://registry.npmjs.org/@cheprasov%2fjsbt>
  - <https://api.npmjs.org/downloads/point/last-month/@cheprasov/jsbt>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/cheprasov/ts-jsbt`) · [data/wave4/enrich/raw/github_com_cheprasov_ts_jsbt.json](../../../data/wave4/enrich/raw/github_com_cheprasov_ts_jsbt.json) (enrichment confidence 0.72)

</details>
