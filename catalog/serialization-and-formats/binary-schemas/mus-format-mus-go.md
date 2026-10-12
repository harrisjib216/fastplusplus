# mus-go

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Go` · `MIT` · 🟢 active

> Go serialization primitives for the tagless MUS binary format; \~3x faster than protobuf-go on small structs, \~6x in unsafe mode.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | marshal 92 ns/op (50 ns/op mus/unsafe_reuse) vs protobuf-go 287 ns/op; unmarshal 122 ns/op (55 ns/op unsafe_reuse) vs 356 ns/op; total 214 ns/op (105 unsafe_reuse) vs 643 ns/op. Roughly 2.9-6.5x faster (marshal 3.1x/5.7x, unmarshal 2.9x/6.5x, total 3.0x/6.1x); wire size 49 vs 51 bytes (derived from page data) |
| **Workload** | Marshal/unmarshal of the same fixed struct used across the go_serialization_benchmarks harness. |
| **Metric** | latency |
| **Adoption** | 145 stars |
| **Last commit** | 2026-05-07 |
| **Links** | [repository](https://github.com/mus-format/mus-go) · [benchmark](https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js) |

## Verdict

alecthomas/go_serialization_benchmarks report (data.js, regenerated 2025-07-04; no CPU listed; harness go.mod says Go 1.22.4) on a SmallStruct of two strings, a time, an int, a bool and a float64: hand-written mus-go v0.3.0 marshals/unmarshals in 92/122 ns/op against protobuf-go v1.34.2's 287/356 ns/op (\~3.1x/2.9x), and the unsafe_reuse variant in 50/55 ns/op (\~5.7x/6.5x) with 0 allocs. The author's own suite (Ryzen 7 PRO 5850U, Go 1.23.5, mus-go v0.6.2) shows a similar gap: 102.9 ns round trip vs 531.7 ns for protobuf and 192.5 ns for vtprotobuf.

## Use it when

- Go-to-Go RPC, IPC, queue or cache payloads where both ends share the same Go types and you control deployment of both.
- Hot paths with small, flat structs where per-message latency and allocations matter: in the report, mus/unsafe_reuse does 50 ns marshal / 55 ns unmarshal with 0 allocs/op in both directions.
- Compact payloads: no per-field tags, and varint keeps small integers to 1 byte (49 B vs protobuf-go's 51 B on the benchmark struct).
- You want validation during unmarshal (length, element, key and value validators), Skip, or partial/out-of-order decoding.
- Object graphs with shared or cyclic pointers, which the pm package preserves (pointer equality survives the round trip).

## Skip it when

- You need field-level schema evolution (old readers ignoring new fields, as Protobuf does): MUS is positional; versioning is by whole-type DTM versions plus migration functions.
- You need interop with the Protobuf/gRPC ecosystem or non-Go peers that already speak Protobuf; the wire format differs.
- Safe mode against other fast Go codecs: in the same report plain mus (214 ns total) trails benc (184) and ties 200sc/bebop (206), and beats gogo/protobuf (281) by only \~1.3x.
- You want a stable API: the project is pre-1.0 (v0.10.2), interfaces changed between minors (issue #10), and SECURITY.md only supports v0.10.x.
- Decoding untrusted input with the default ord slice/map serializers: they allocate make([]T, length) from the encoded length before reading elements unless you configure a length validator.

## How it is fast

The MUS format carries no field tags or type metadata, so the encoder writes values back to back and the decoder reads them positionally against a shared schema, with no tag dispatch and no reflection. Each field picks its own encoding: LEB128 varint (ZigZag for signed), fixed-width little-endian raw, or the unsafe package, which stores numbers with a pointer cast and returns strings that alias the input via unsafe.String (zero copy). A Size pass gives the exact buffer length, so a marshal costs one allocation, or none when the caller reuses a buffer.

## Compared with alternatives

Pick mus-go over benc, gencode and 200sc/bebop (Go) when you can accept unsafe strings and buffer reuse: mus/unsafe_reuse is the fastest non-baseline row in the shared report (105 ns total, 0 allocs) ahead of benc/usafe (121 ns) and gencode/unsafe_reuse (152 ns). In safe mode it has no speed edge over benc or bebop; pick it then for per-field varint/raw choice, validators, Skip, pointer mapping and typed versioning.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/mus-format/common-go, golang.org/x/exp (constraints); test-only: ymz-ncnk/assert, ymz-ncnk/mok; optional: mus-gen-go for code generation |
| **Minimum toolchain** | Go 1.24 (go.mod; mus-gen also requires Go 1.24+) |
| **Platforms** | any Go target (pure Go; README claims 32/64-bit compatibility); unsafe-package numbers use host byte order, so they match the little-endian spec only on little-endian CPUs |
| **Thread safety** | not documented. Core serializers are stateless values (safe to share by construction, per the source); pm serializers mutate shared pointer maps that Wrap resets after each call, so do not use one pm instance concurrently. |
| **Drop-in for the baseline** | no |

## Gotchas

- unsafe numeric Marshal writes through \*(\*T)(unsafe.Pointer(&bs[0])) and bounds-checks only bs[0]: a too-short buffer gives an out-of-bounds write, not the panic the safe packages raise, and bytes come out in host order.
- unsafe.String results alias the input buffer; mutating or reusing that buffer changes the decoded strings (the README warns about this). With buffer reuse, the next Marshal overwrites the previously returned slice.
- In the current main branch, unsafe ByteSlice.Unmarshal still calls make([]byte, length) before returning the aliasing slice, so it is not zero-allocation.
- The benchmark measured mus-go v0.3.0 (function-style API such as ord.MarshalString); v0.10.x uses mus.Serializer[T] values, so the harness code does not compile against current releases as-is.

## Known shortcomings

- The shootout measured v0.3.0 (Go 1.22.4); current v0.10.2 has a different interface-based API and is unmeasured there. Only about 1.3x over gogo/protobuf in safe mode, which also uses unsafe for numbers. Source risks: unsafe numeric Marshal bounds-checks only the first byte (short buffer means out-of-bounds write) and writes host byte order although the spec says little-endian; ord slice/map Unmarshal allocate lengths read from input unless a validator is set. Pre-1.0 with breaking minor versions.

## Caveats and trade-offs

Shared report page (report/data.js, last regenerated 2025-07-04) states no CPU model or Go compiler version, so tier is capped at B. The mus rows are api_kind 'manual' (hand-written serializers built from mus-go primitives), while protobuf-go is codegen. The mus/unsafe_reuse numbers use unsafe string unmarshalling and marshal-buffer reuse.

Manually-defined (de)serializers rather than a schema compiler; unsafe_reuse variant reuses buffers and assumes single-threaded reuse discipline.

## Maintenance

Actively maintained (v0.10.2 released 2026-05-06, last main commit 2026-05-07), MIT-licensed pure Go with CI fuzzing and CodeQL, but pre-1.0 with API changes between minor versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (alecthomas/go_serialization_benchmarks). report/data.js has mus (92/122 ns/op, 49 B), mus/unsafe_reuse (50/55 ns/op) and protobuf-go (287/356 ns/op, 51 B) rows from the same harness. The harness code is public, but the page and README give no CPU model or Go version (the report page says results are user-generated), so it cannot be A.
- **Verifier notes:** All numbers were confirmed against the raw data.js (a WebFetch summary misreported them; raw file checked via gh and raw.githubusercontent). The lower bound of the ratio range was 2.3x, which the page data does not support; corrected to 2.9-6.5x. last_commit on default branch main is 2026-05-07; 2026-05-27 was pushed_at from a non-default branch.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `caveats`
- **Shortcomings recorded by:** Author-maintained suite (Ryzen 7 PRO 5850U, Go 1.23.5, mus-go v0.6.2): 102.9 ns vs protobuf 531.7 ns and vtprotobuf 192.5 ns.
- **Pages the verifier opened:**
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
  - <https://raw.githubusercontent.com/alecthomas/go_serialization_benchmarks/master/report/data.js>
  - <https://github.com/alecthomas/go_serialization_benchmarks>
  - <https://alecthomas.github.io/go_serialization_benchmarks/>
  - <https://github.com/mus-format/mus-go>
- **Sources the enricher read:**
  - <https://github.com/mus-format/mus-go>
  - <https://github.com/mus-format/mus-go/blob/main/README.md>
  - <https://github.com/mus-format/mus-go/blob/main/go.mod>
  - <https://github.com/mus-format/mus-go/blob/main/mus.go>
  - <https://github.com/mus-format/mus-go/blob/main/errs.go>
  - <https://github.com/mus-format/mus-go/blob/main/VERSIONS.md>
  - <https://github.com/mus-format/mus-go/blob/main/USERS.md>
  - <https://github.com/mus-format/mus-go/blob/main/SECURITY.md>
  - <https://github.com/mus-format/mus-go/blob/main/varint/uint.go>
  - <https://github.com/mus-format/mus-go/blob/main/varint/positive_int.go>
  - <https://github.com/mus-format/mus-go/blob/main/ord/string.go>
  - <https://github.com/mus-format/mus-go/blob/main/ord/slice.go>
  - <https://github.com/mus-format/mus-go/blob/main/ord/map.go>
  - <https://github.com/mus-format/mus-go/blob/main/options/slice/options.go>
  - <https://github.com/mus-format/mus-go/blob/main/unsafe/unsafe.go>
  - <https://github.com/mus-format/mus-go/blob/main/unsafe/string.go>
  - <https://github.com/mus-format/mus-go/blob/main/unsafe/byte_slice.go>
  - <https://github.com/mus-format/mus-go/blob/main/unsafe/integer.go>
  - <https://github.com/mus-format/mus-go/blob/main/unsafe/int.go>
  - <https://github.com/mus-format/mus-go/blob/main/raw/integer.go>
  - <https://github.com/mus-format/mus-go/blob/main/pm/pm.go>
  - <https://github.com/mus-format/mus-go/blob/main/pm/ptr.go>
  - <https://github.com/mus-format/mus-go/blob/main/pm/wrapper.go>
  - <https://github.com/mus-format/mus-go/blob/main/typed/typed.go>
  - <https://github.com/mus-format/mus-go/issues?q=is%3Aissue>
  - <https://github.com/mus-format/mus-go/issues/13>
  - <https://github.com/mus-format/mus-go/issues/12>
  - <https://github.com/mus-format/mus-go/issues/4>
  - <https://github.com/mus-format/mus-go/releases>
  - <https://github.com/mus-format/mus-go/commits/main>
  - <https://github.com/mus-format/mus-gen-go>
  - <https://github.com/mus-format/specification>
  - <https://github.com/ymz-ncnk/go-serialization-benchmarks>
  - <https://github.com/ymz-ncnk/go-serialization-benchmarks/blob/main/results/benchmarks.txt>
  - <https://github.com/ymz-ncnk/go-serialization-benchmarks/blob/main/go.mod>
  - <https://github.com/alecthomas/go_serialization_benchmarks>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/go.mod>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/mus/mus.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/mus-format/mus-go`) · [data/wave4/enrich/raw/github_com_mus_format_mus_go.json](../../../data/wave4/enrich/raw/github_com_mus_format_mus_go.json) (enrichment confidence 0.8)

</details>
