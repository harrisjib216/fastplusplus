# benc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Go` · `MIT` · 🟡 stale

> Pure-Go raw binary serializer with optional schema codegen; hand-written benc code runs \~3.5x faster than protobuf-go on small structs.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | go_serialization_benchmarks report, SmallStruct. benc marshals in 81 ns/op (80 for benc/usafe), against 287 ns/op for protobuf-go (\~3.5x). It unmarshals in 103 ns/op (41 ns/op for benc/usafe with unsafe string aliasing), against 356 ns/op (\~3.5x; \~8.7x unsafe). Against gogo/protobuf (115/166 ns/op) the margin is \~1.4x marshal and \~1.6x unmarshal. (derived from page data) |
| **Workload** | Marshal/unmarshal of goserbench.SmallStruct (Name, BirthDay, Phone, Siblings, Spouse, Money) in the go_serialization_benchmarks harness. The serializer is hand-written field-by-field code on benc's std primitives (api_kind 'manual'), not bencgen-generated code. |
| **Metric** | latency |
| **Adoption** | 42 stars |
| **Last commit** | 2025-05-17 |
| **Links** | [repository](https://github.com/deneonet/benc) · [benchmark](https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js) |

## Verdict

The source is alecthomas/go_serialization_benchmarks: a user-generated report regenerated in one run by its maintainer, with CPU model and Go version not stated. The suite pins benc v1.0.2, protobuf-go v1.34.2 and gogo v1.3.2. There, hand-written benc code for a 6-field struct (BirthDay stored as UnixNano int64) marshals in 81 ns vs 287 ns for protobuf-go and unmarshals in 103 vs 356 ns (\~3.5x each), and both produce 51 bytes. The unsafe-string variant unmarshals in 41 ns with 0 allocs. The margin over gogo/protobuf is \~1.4x/1.6x, and the suite's own hand-rolled baseline (73/90 ns) is faster than benc.

## Use it when

- Go-to-Go only (both writer and reader are your code) with small flat records, e.g. WAL/queue entries, cache values, KV-store values. Grafana's walqueue depends on benc.
- Hot marshal/unmarshal paths where you are willing to hand-write field-by-field encode/decode against bstd primitives, which is the exact path benchmarked at \~81/103 ns vs protobuf-go's 287/356 ns.
- Decode paths where the input buffer outlives the decoded struct, so the unsafe-string decoder (41 ns/op, 0 allocs in the report) can alias strings into it.
- Go-only messages that need simple schema evolution (remove a field and reserve its ID), where bencgen's breaking-changes detector is enough and you don't need protobuf interop.

## Skip it when

- Cross-language or protobuf-interop traffic: bencgen's only --lang is `go`, and the wire format is benc's own.
- Long-lived persisted data that must survive library upgrades. v1.1.8 silently changed the encoding of fixed-width signed ints (issue #13, open, no maintainer reply), and go.mod retracts four earlier releases for bugs.
- Untrusted input. The repo has no fuzz tests. UnmarshalSlice/UnmarshalMap allocate whatever length the varint says. Skipping a reserved container loops `for b[n] != 1 || b[n+1] != 1` without a bounds check, so truncated data can panic.
- When you expect the bencgen path to match the headline numbers: the report measured hand-written v1.0.2 std code. The tagged codegen format adds 2-3 tag bytes per field plus a HandleCompatibility check on decode, and it is not benchmarked.
- When gogo/protobuf-level speed is already enough: against gogo (115/166 ns) the margin drops to \~1.4x/1.6x, and gogo keeps protobuf compatibility.

## How it is fast

There is no reflection and no per-field interface dispatch. The caller computes the exact size with Size\* functions, allocates one buffer, and each field is written by an offset-threaded function `(n int, b []byte, v) int` that does manual little-endian byte stores behind Go bounds-check-elimination hints (`_ = u[7]`). Fixed-width ints and floats are written as raw 2/4/8 bytes, and lengths use LEB128 varints. In the std format there are no field tags or wire types to parse, so decoding just reads sequentially. The unsafe string variants alias the input buffer through `unsafe.String`, which makes unmarshal zero-allocation.

## Compared with alternatives

Against mus-go (also hand-written Go primitives), benc's safe path is a bit faster in the same report (184 vs 214 ns total), but mus/unsafe_reuse beats benc/usafe (105 vs 121 ns). Pick benc if you also want an optional schema/codegen layer with reserved IDs. Against schema-first colfer (238 ns total) and 200sc/bebop (206 ns), benc's measured edge applies only if you hand-write the code, because its own codegen path is unbenchmarked.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/exp (constraints only); the bencgen CLI is needed only for the schema path |
| **Minimum toolchain** | Go 1.22 (go.mod `go 1.22`; std uses range-over-int; CI runs Go 1.22) |
| **Platforms** | any GOARCH (pure Go; a 32-bit build bug, issue #6, was fixed in v1.1.0); CI tests only ubuntu-latest |
| **Thread safety** | Not documented. bstd functions are stateless over caller-owned buffers. benc.BufPool uses sync.Pool but returns a slice of a buffer it has already Put back, so copy the result before the next BufPool.Marshal on any goroutine. |
| **Drop-in for the baseline** | no |

## Gotchas

- Wire break inside v1.1.x: v1.1.8 dropped ZigZag from MarshalInt64/Int32/Int16, so data written by v1.1.7 decodes wrong (int64 values come back doubled, issue #13). grafana/walqueue pins v1.1.7 with a replace directive for this reason.
- The benchmarked code is benc v1.0.2 (Nov 2023; root package plus `bunsafe`, uint16 string-length prefixes, zigzag fixed ints). Its API and wire format differ from the current std package, and the current release is not in the report.
- Marshal\* functions panic if the buffer is too small, so always size first with Size\*. Unsafe strings and UnmarshalBytesCropped alias the source buffer, so mutating or reusing it corrupts the decoded values.
- Slices and maps end with a 4-byte 0x01010101 sentinel. SkipSlice/SkipMap, used when skipping reserved fields, scan for that pattern instead of using the length, so element data that contains it (e.g. four consecutive `true` bools) ends the skip early.

## Known shortcomings

- The shootout measured v1.0.2 (2023), whose API and wire format differ from the current v1.1.8; the current release and its codegen path are unmeasured. Open wire-compatibility bug: v1.1.8 dropped ZigZag from fixed-width signed ints, so v1.1.7 data decodes wrong (#13, no reply; grafana/walqueue pins v1.1.7). Source hazards: BufPool.Marshal returns a slice of a buffer already returned to sync.Pool, slice/map skipping scans for a 4-byte marker, truncated input can panic; no fuzz tests. Only about 1.4-1.6x over gogo/protobuf.

## Caveats and trade-offs

Same shared report page: CPU model and Go version are not stated (the report says it is user-generated), capping the tier at B. The benchmarked serializer is hand-written primitive calls (api_kind 'manual'), close to the suite's own hand-rolled 'baseline' row (163 ns/op total vs benc 184). It is not the schema/codegen path with forward/backward compatibility that benc advertises. The 41 ns/op unmarshal uses unsafe string aliasing. Low star count means limited validation beyond this one shootout.

Manual/generated encode-decode functions rather than reflection; small, low-visibility project so API stability/support is uncertain.

## Maintenance

Stale: the last commit and release (v1.1.8) are from 2025-05-17, and an open wire-compatibility bug (#13, Aug 2025) has no maintainer response. It is MIT-licensed pure Go with the core std layer in one file, so pinning v1.1.7 or vendoring is practical.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** The benc and benc/usafe rows sit in alecthomas/go_serialization_benchmarks report/data.js, a well-known independent suite (1,624 stars), next to protobuf-go and gogo/protobuf. benc's author added the entry (PR #125), but the current report was regenerated in one run by maintainer matheusd (PR #178, 2025-07-04). The code is public (internal/serializers/benc/benc.go), but no CPU model or Go version is stated, so it is not A.
- **Verifier notes:** Every number matches the benc and benc/usafe rows in data.js; the row is spelled 'benc/usafe' on the page. The comparison is not like-for-like: manual encoding vs protobuf-go codegen, and the gogo/protobuf margin is much smaller. Metadata checked: MIT, 42 stars, not a fork, not archived, last commit 2025-05-17 (\~16 months ago, so stale is correct).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
  - <https://alecthomas.github.io/go_serialization_benchmarks>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/README.md>
  - <https://github.com/alecthomas/go_serialization_benchmarks/pull/178>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/benc/benc.go>
  - <https://github.com/deneonet/benc>
  - <https://github.com/deneonet/benc/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/deneonet/benc>
  - <https://github.com/deneonet/benc/blob/main/README.md>
  - <https://github.com/deneonet/benc/blob/main/std/README.md>
  - <https://github.com/deneonet/benc/blob/main/std/bstd.go>
  - <https://github.com/deneonet/benc/blob/main/std/bstd_test.go>
  - <https://github.com/deneonet/benc/blob/main/cmd/bencgen/README.md>
  - <https://github.com/deneonet/benc/blob/main/impl/gen/README.md>
  - <https://github.com/deneonet/benc/blob/main/impl/gen/bencgen.go>
  - <https://github.com/deneonet/benc/blob/main/idv/README.md>
  - <https://github.com/deneonet/benc/blob/main/SECURITY.md>
  - <https://github.com/deneonet/benc/blob/main/go.mod>
  - <https://github.com/deneonet/benc/blob/main/benc.go>
  - <https://github.com/deneonet/benc/blob/main/benc_test.go>
  - <https://github.com/deneonet/benc/blob/main/testing/person/person.go>
  - <https://github.com/deneonet/benc/blob/main/testing/person/person_test.go>
  - <https://github.com/deneonet/benc/blob/main/testing/schemas/person.benc>
  - <https://github.com/deneonet/benc/blob/main/testing/schemas/person2.benc>
  - <https://github.com/deneonet/benc/blob/main/.github/workflows/go.yml>
  - <https://github.com/deneonet/benc/tags>
  - <https://github.com/deneonet/benc/releases>
  - <https://github.com/deneonet/benc/commits/main>
  - <https://github.com/deneonet/benc/issues>
  - <https://github.com/deneonet/benc/issues/13>
  - <https://github.com/deneonet/benc/issues/12>
  - <https://github.com/deneonet/benc/issues/6>
  - <https://github.com/deneonet/benc/issues/3>
  - <https://github.com/deneonet/benc/issues/1>
  - <https://github.com/deneonet/benc/compare/v1.1.7...v1.1.8>
  - <https://github.com/deneonet/benc/tree/v1.0.2>
  - <https://github.com/deneonet/benc/blob/v1.0.2/go.mod>
  - <https://github.com/deneonet/benc/blob/v1.0.2/bstd.go>
  - <https://github.com/deneonet/benc/blob/v1.0.2/bpre/bpre.go>
  - <https://github.com/deneonet/benc/blob/v1.0.2/bunsafe/bunsafe.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/benc/benc.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/go.mod>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/README.md>
  - <https://github.com/grafana/walqueue/blob/HEAD/go.mod>
  - <https://github.com/grafana/walqueue/pull/49>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/deneonet/benc`) · [data/wave4/enrich/raw/github_com_deneonet_benc.json](../../../data/wave4/enrich/raw/github_com_deneonet_benc.json) (enrichment confidence 0.8)

</details>
