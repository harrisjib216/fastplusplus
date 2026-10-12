# colfer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Go` · `CC0-1.0` · 🟢 active

> Schema-compiled binary format with generated C11, Go, Java and JavaScript code; beats protobuf-go and protobuf C++ 2-3x on small records.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | marshal 115 ns/op vs protobuf-go 287 ns/op (\~2.5x), unmarshal 123 ns/op vs 356 ns/op (\~2.9x); also far faster than msgpack (921/1216 ns/op) and capnproto (2181/364 ns/op) on marshal (derived from page data) |
| **Workload** | Marshal/unmarshal of a fixed struct (Name, BirthDay, Phone, Siblings, Spouse, Money) in the go_serialization_benchmarks shootout harness. |
| **Metric** | latency |
| **Adoption** | 759 stars |
| **Last commit** | 2026-02-26 |
| **Links** | [repository](https://github.com/pascaldekloe/colfer) · [benchmark](https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js) |

## Verdict

Go: the user-generated alecthomas/go_serialization_benchmarks report (no CPU model or Go version, last regenerated 2025-07-04) shows Colfer at 115 ns/op marshal and 123 ns/op unmarshal for the 6-field SmallStruct, against 287/356 ns/op for google.golang.org/protobuf v1.34.2 and 115/166 ns/op for gogo/protobuf v1.3.2. C: the project wiki reports c/bench/bench.cpp (Google Benchmark, -O3, Apple clang 15.0.0, Apple M1 iMac, libprotoc 24.4 generated C++ with no arena) at 9.19 vs 22.9 ns marshal (\~2.5x) and 18.0 vs 40.8 ns unmarshal (\~2.3x) for a 7-field record with one short string, from a single run with no variance given.

## Use it when

- You control both ends and want one schema shared by C, Go, Java and JavaScript code, with no runtime library to link.
- Hot paths with small, flat records (a few ints, floats and short strings): the project's C benchmark encodes a 7-field record in 9.19 ns and decodes it in 18.0 ns on an Apple M1, against 22.9 ns and 40.8 ns for protobuf C++.
- Go services that can drop protobuf wire compatibility: 115/123 ns/op marshal/unmarshal against 287/356 ns/op for protobuf-go in the go_serialization_benchmarks SmallStruct test.
- Untrusted network or stream input: the parser enforces a serial size cap (default 16 MiB) and a list length cap (default 64Ki), the C parser has an AFL round-trip fuzz harness, and each message ends in 0x7f, so messages can be concatenated.
- C or embedded code that wants plain C11 structs from a code generator instead of linking libprotobuf.

## Skip it when

- You need protobuf wire compatibility, gRPC, reflection or dynamic messages, or a JSON mapping.
- Rolling upgrades where old readers see data from newer writers: v1 readers reject fields they do not know. Forward compatibility exists only on the unreleased v2 branch.
- Schemas that need maps, enums, integer lists, oneof, default values, or more than 127 fields per struct.
- Read-mostly access to large messages: C unmarshal copies every string into its own malloc. In the same C benchmark, FlatBuffers reads the record in 6.69 ns against 18.0 ns for Colfer, though FlatBuffers is slower to build (62.4 ns).
- Go-only hot paths that want the fastest codec: mus-go, benc and 200sc/bebop beat Colfer in the same harness, and gogo/protobuf ties it on marshal (115 ns/op).

## How it is fast

The compiler emits straight-line code specialized for each field, with no reflection, no descriptor tables and no runtime library. Fields must appear in schema order behind a 1-byte header (7-bit field index plus a flag), so unmarshal is one forward pass of `if (header == i)` checks, with no tag-dispatch loop and no unknown-field retention (unknown headers are rejected). Zero values are omitted, and the header flag picks a compact or fixed-width encoding per value (for example, a uint32 below 2^21 is a varint, larger values take 4 fixed big-endian bytes). T_marshal_len computes the exact size first, so marshal is a single pass into a preallocated buffer.

## Compared with alternatives

Pick Colfer over hpp-proto when you do not need protobuf wire compatibility and want the same schema in C, Go, Java and JavaScript; pick hpp-proto to stay protobuf-compatible in C++. In Go-only code, mus-go, benc and 200sc/bebop are faster in the same harness (214, 184 and 206 ns/op total against Colfer's 238), so choose Colfer for its C, Java and JavaScript generators and its parser size limits, not for raw Go speed.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | None for generated code (C: libc only; Go: standard library only). The colf compiler is a Go program (prebuilt releases, go get, Homebrew, or a Maven plugin for Java). Its go.mod also pulls gogo/protobuf and flatbuffers, which its benchmarks use. |
| **Minimum toolchain** | C11 compiler (CI builds with clang -std=c11 -pedantic -Werror; the benchmark uses -std=c17 and C++17); C++ uses the C header, and there is no C++ class API. Compiler module needs go 1.18. CI uses JDK 17 for Java. |
| **Platforms** | Any C11 target with 8-bit bytes (the header has #error otherwise), little- or big-endian (big-endian is detected by macros); Go, JVM/Android, Node.js/browsers. |
| **Thread safety** | Not documented. Generated C functions keep no internal state, but they read the process-wide globals colfer_size_max and colfer_list_max and set errno. |
| **Drop-in for the baseline** | no |

## Gotchas

- Unmarshal writes only the fields present in the serial. If you reuse a struct, absent fields keep stale values, so zero the struct first (C: calloc or memset; Go: \*o = T{}). The Go benchmark harness does this. In C, an uninitialized .len field also makes marshal crash (issue #34).
- C unmarshal mallocs every text, binary, list and nested struct. No free function is generated, malloc results are not checked for NULL, and a mid-message error leaves earlier allocations in the partial struct for the caller to free.
- C T_marshal(o, buf) takes no buffer length. Size buf with T_marshal_len (it returns 0 and sets errno to EFBIG past the limits) or use colfer_size_max. The limits are global variables and the header guard is always COLFER_H, so each program gets one generated C pair. Go MarshalTo panics on a short buffer and fills nil entries of struct lists in the input.
- Schema evolution is append-only: add new fields at the end and never remove fields (rename them to deprecate). C and Go do not validate UTF-8 in text fields. Java maps unsigned types to signed ones, and JavaScript 64-bit integers are limited to about 2^53.

## Known shortcomings

- Against gogo/protobuf on the same Go shootout, marshal is a tie (115 vs 115 ns/op) and unmarshal is only about 1.35x faster. CC0 gives no patent grant.
- Last release v1.8.1 (2020); last maintainer commit 2023-10. v1 readers reject unknown fields, so schemas are append-only. C API hazards: unmarshal does not reset absent fields, every string/list is malloc'd with no generated free and no NULL checks, marshal takes no buffer length, one generated pair per program; no C++ API. In the C bench FlatBuffers reads faster (6.69 vs 18.0 ns). 16th of 54 in the Go harness.

## Caveats and trade-offs

The report page (report/data.js, rendered at alecthomas.github.io/go_serialization_benchmarks, last fully regenerated 2025-07-04 in commit 833ed64) says 'This report is user-generated'. The numbers come from a contributor's local run, not CI (CI only runs --validate). No CPU model or Go version is given, so the tier is capped at B. Numbers cover one struct shape only. The win is against official protobuf-go (google.golang.org/protobuf v1.34.2). Against the codegen gogo/protobuf row on the same page, Colfer ties on marshal (115 vs 115 ns/op) and is \~1.35x faster on unmarshal (123 vs 166 ns/op) (derived from page data). Colfer's own wiki benchmark agrees (Apple M1, go1.20.2, vs gogo/protobuf 1.3.2): marshal 35.08 vs 34.89 ns/op, unmarshal 44.85 vs 60.01 ns/op. CC0-1.0 public-domain dedication: no patent grant.

Requires a schema-first IDL and code generation step; smaller ecosystem/tooling than protobuf; no reflection-based dynamic access.

## Maintenance

Activity is low: the last tagged release is v1.8.1 (2020-06-18), the last maintainer commit is from 2023-10, and community fixes were merged in 2025-11 and 2026-02. The v2 format (forward compatibility; a C preview at 5.63/13.3 ns) sits unreleased on a branch last touched 2024-01. The code is CC0 public domain with no patent grant, and the generated code is small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** The colfer row in the independent alecthomas/go_serialization_benchmarks report (1.6k stars) shows 115/123 ns/op, against 287/356 ns/op for the official protobuf-go row. The code is public (benchmarks.go, internal/serializers/colfer), but the report says it is 'user-generated' and gives no CPU model or Go version, so it cannot be A.
- **Verifier notes:** All claimed numbers match the colfer, protobuf-go, msgpack and capnproto rows. Metadata checks out: CC0-1.0, 759 stars, last commit 2026-02-26, active, not archived or a fork. For the C++-first list: the Colfer wiki also has a first-party C benchmark against protobuf C++ (c/bench/bench.cpp, -O3 in c/bench/Makefile, Apple clang 15.0.0, Apple M1, libprotoc 24.4). It gives marshal 9.19 vs 22.9 ns and unmarshal 18.0 vs 40.8 ns and could support a separate C entry at tier A.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** Colfer's C output against protobuf C++ (project wiki, code in c/bench/bench.cpp, -O3, Apple clang 15, Apple M1): marshal 9.19 vs 22.9 ns, unmarshal 18.0 vs 40.8 ns (about 2.5x and 2.3x, derived from page data). First-party.
- **Pages the verifier opened:**
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
  - <https://alecthomas.github.io/go_serialization_benchmarks/>
  - <https://github.com/alecthomas/go_serialization_benchmarks>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/README.md>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/benchmarks.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/Makefile>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/go.mod>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/.github/workflows/report.yml>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/.github/workflows/go.yml>
  - <https://github.com/alecthomas/go_serialization_benchmarks/commit/833ed64040c12f8c50981530e047bb789ea9d3d5>
  - <https://github.com/pascaldekloe/colfer>
  - <https://github.com/pascaldekloe/colfer/wiki/Benchmark>
  - <https://raw.githubusercontent.com/wiki/pascaldekloe/colfer/Benchmark.md>
  - <https://github.com/pascaldekloe/colfer/blob/master/c/bench/Makefile>
  - <https://github.com/pascaldekloe/colfer/blob/master/go/bench/Makefile>
- **Sources the enricher read:**
  - <https://github.com/pascaldekloe/colfer>
  - <https://github.com/pascaldekloe/colfer/blob/master/README.md>
  - <https://github.com/pascaldekloe/colfer/wiki/Benchmark>
  - <https://raw.githubusercontent.com/wiki/pascaldekloe/colfer/Benchmark.md>
  - <https://github.com/pascaldekloe/colfer/wiki/Spec>
  - <https://raw.githubusercontent.com/wiki/pascaldekloe/colfer/Spec.md>
  - <https://raw.githubusercontent.com/wiki/pascaldekloe/colfer/Home.md>
  - <https://github.com/pascaldekloe/colfer/blob/master/c/bench/bench.cpp>
  - <https://github.com/pascaldekloe/colfer/blob/master/c/bench/Makefile>
  - <https://github.com/pascaldekloe/colfer/blob/master/c/Makefile>
  - <https://github.com/pascaldekloe/colfer/blob/master/c/fuzz/Makefile>
  - <https://github.com/pascaldekloe/colfer/blob/master/c/fuzz/fuzz.c>
  - <https://github.com/pascaldekloe/colfer/blob/master/template/c-header.txt>
  - <https://github.com/pascaldekloe/colfer/blob/master/template/c.txt>
  - <https://github.com/pascaldekloe/colfer/blob/master/template/go.txt>
  - <https://github.com/pascaldekloe/colfer/blob/master/testdata/bench/scheme.colf>
  - <https://github.com/pascaldekloe/colfer/blob/master/testdata/bench/scheme.proto>
  - <https://github.com/pascaldekloe/colfer/blob/master/go/bench/bench_test.go>
  - <https://github.com/pascaldekloe/colfer/blob/master/go.mod>
  - <https://github.com/pascaldekloe/colfer/blob/master/common.mk>
  - <https://github.com/pascaldekloe/colfer/blob/master/Makefile>
  - <https://github.com/pascaldekloe/colfer/blob/master/.github/workflows/ci.yml>
  - <https://github.com/pascaldekloe/colfer/commits/master>
  - <https://github.com/pascaldekloe/colfer/commits/v2>
  - <https://github.com/pascaldekloe/colfer/releases>
  - <https://github.com/pascaldekloe/colfer/tags>
  - <https://github.com/pascaldekloe/colfer/issues?q=is%3Aissue>
  - <https://github.com/pascaldekloe/colfer/issues/10>
  - <https://github.com/pascaldekloe/colfer/issues/11>
  - <https://github.com/pascaldekloe/colfer/issues/16>
  - <https://github.com/pascaldekloe/colfer/issues/34>
  - <https://github.com/pascaldekloe/colfer/issues/47>
  - <https://github.com/pascaldekloe/colfer/issues/52>
  - <https://github.com/pascaldekloe/colfer/issues/82>
  - <https://github.com/alecthomas/go_serialization_benchmarks>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/go.mod>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/colfer/colfer.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/colfer/structdef-colfer.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/colfer/structdef.colf>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/pascaldekloe/colfer`) · [data/wave4/enrich/raw/github_com_pascaldekloe_colfer.json](../../../data/wave4/enrich/raw/github_com_pascaldekloe_colfer.json) (enrichment confidence 0.8)

</details>
