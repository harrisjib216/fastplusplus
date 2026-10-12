# msgp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Go` · `MIT` · 🟢 active

> Go code generator for MessagePack; about 6-7x lower marshal/unmarshal latency than reflection-based vmihailenco/msgpack on the same wire format.

| | |
|---|---|
| **Beats** | MessagePack |
| **Claimed result** | marshal 134 ns/op vs msgpack (vmihailenco) 921 ns/op (\~6.9x); unmarshal 200 ns/op vs 1216 ns/op (\~6.1x); wire size slightly larger (97 vs 92 bytes) (derived from page data) |
| **Workload** | Marshal/unmarshal of the same fixed struct used across the go_serialization_benchmarks harness, comparing msgp's codegen'd MessagePack implementation against the reflection-based vmihailenco/msgpack implementation of the same wire format. |
| **Metric** | latency |
| **Adoption** | 1.95k stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/tinylib/msgp) · [benchmark](https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js) |

## Verdict

Source: the user-generated go_serialization_benchmarks report (data.js last regenerated 2025-07-04, commit 833ed64040), on a 6-field SmallStruct (two strings, time.Time, int, bool, float64). msgp v1.1.8 took 134 ns/op to marshal (1 alloc, 128 B) and 200 ns/op to unmarshal (2 allocs, 32 B), against 921 ns/op (4 allocs) and 1216 ns/op (3 allocs) for vmihailenco/msgpack v5.3.5 (\~6.9x and \~6.1x). Encoded size is 97 B vs 92 B, and the 5-byte gap matches msgp's 15-byte ext-5 time against a 10-byte standard timestamp (inferred). The run used a fresh buffer each call (MarshalMsg(nil)), with no reuse and no zero-copy. No CPU or Go version is given; the harness go.mod says go 1.22.4, and current msgp v1.6.4 is not measured.

## Use it when

- Go services that read or write MessagePack with a fixed set of Go struct types, where encode/decode shows up in profiles (the shootout shows 134/200 ns vs 921/1216 ns on a 6-field struct).
- You must keep the MessagePack wire format for other languages or stored data, but you want codegen speed instead of switching to protobuf or a Go-only format.
- Hot paths that can reuse one []byte: MarshalMsg appends to the buffer you pass in, and the README says carefully written code can run with zero heap allocations.
- Large objects (over about 2 KB) or streams: the README says the generated io.Reader/io.Writer methods use less memory and, at some size, run faster than the []byte methods.
- TinyGo or microcontroller targets: CI runs TinyGo 0.41.1 tests, and the wiki recommends MarshalMsg/UnmarshalMsg there because they need no extra buffers.

## Skip it when

- Dynamic or unknown payloads (map[string]interface{}, polymorphic interface fields). Generated code gives little here, and interface{} encoding supports only built-ins and types with msgp methods (open issue #235: a []interface{} of tuple structs fails at runtime with 'type not supported').
- You cannot add a `go generate` step, or your types embed structs from other packages. Generation is per file, and embedded structs from another package are ignored (open issue #271).
- You control both ends and want the lowest Go latency and size. In the same harness, benc (81/103 ns, 51 B), mus-go (92/122 ns, 49 B) and colfer (115/123 ns, 51 B) are faster and about half of msgp's 97 B, because map-mode MessagePack writes every field name.
- Untrusted input with default settings. The generated []byte UnmarshalMsg has no array/map size limit unless you add `//msgp:limit` or `limit=n` tags (v1.6.0+). The maintainer says there is no protection against deep recursion in recursive types (issue #411).
- Maps with non-string keys, unless you opt in with the `//msgp:maps` directive (binkeys/shim/autoshim, v1.4.0+). By default msgp decodes only str/bin map keys.

## How it is fast

It generates code ahead of time, so there is no runtime reflection or interface boxing. The generated MarshalMsg first calls msgp.Require(b, Msgsize()) to grow the buffer once to a worst-case size. It then appends values, and the constant bytes (the map header and each MessagePack-encoded field-name key) are pre-encoded at generation time and emitted as literal `append(o, 0x.., ...)` runs. The generated UnmarshalMsg reads each key zero-copy (ReadMapKeyZC) and matches it with a compiled Go `switch` on msgp.UnsafeString(field), so there is no per-key map lookup or key allocation. It reuses the existing capacity of []byte fields. Wire-type dispatch uses a 256-entry prefix-byte table (`sizes [256]bytespec`) that gives type and size in constant time.

## Compared with alternatives

Pick msgp over the Go codegen siblings benc, mus-go, colfer, gencode and 200sc/bebop when the bytes must stay standard MessagePack for interop with other languages or existing data. Those siblings are about 1.1-1.7x faster to marshal and about half the size in the same harness, but they use their own formats. Against the other MessagePack codegen in that report (shamaton/msgpackgen map mode, 242/358 ns), msgp is about 1.8x faster on marshal.

## Integration

| | |
|---|---|
| **Form** | module (Go module: `go tool msgp` code generator plus runtime package github.com/tinylib/msgp/msgp) |
| **Dependencies** | Runtime: github.com/philhofer/fwd v1.2.0. Generator also: golang.org/x/tools v0.22.0 (golang.org/x/mod indirect). |
| **Minimum toolchain** | Go 1.24 (go.mod). CI tests Go 1.24.x, 1.25.x and 1.26.x on ubuntu-latest, plus TinyGo 0.41.1 on x86_64. |
| **Platforms** | Any Go target. Uses `unsafe` for []byte-to-string conversion unless built with the `purego` (or appengine) tag. File helpers use madvise/fallocate on Linux, with fallbacks on other systems. CI runs only on Linux. |
| **Thread safety** | Not documented. The generated MarshalMsg/UnmarshalMsg methods touch only the receiver and the caller's []byte. The README calls \*msgp.Reader/\*msgp.Writer protocol-aware versions of bufio.Reader/Writer, so treat one instance as single-goroutine. |
| **Drop-in for the baseline** | partial: the wire format is MessagePack, and msgp reads existing `msgpack:` struct tags as a fallback. But the API is generated methods, not `msgpack.Marshal(v)` reflection. time.Time defaults to a non-standard extension, and non-string map keys and arbitrary interface{} values need extra directives or do not work. |

## Gotchas

- By default, time.Time is written as msgp's own extension type 5 (15 bytes), not the official MessagePack timestamp (-1). Other implementations will not read it as a timestamp. Add `//msgp:newtime` for cross-language output. Reads accept both types (wiki Type Mapping Rules).
- Types from outside the processed file are assumed to implement the msgp interfaces. If they do not, the generated code fails to compile. Also run the generator on every file that holds referenced types.
- The `zerocopy` field tag (v1.3.0+) makes decoded []byte fields alias the input buffer. Reusing or changing that buffer silently corrupts the decoded values.
- Newer msgp versions can generate different code than older ones (README 'Status'). Regenerate after every upgrade, and do not mix _gen.go files from different generator versions.

## Known shortcomings

- The shootout pins v1.1.8 (current v1.6.4 unmeasured) with a fresh buffer per call. Default time format is msgp's own extension type 5, not the standard -1 timestamp (use //msgp:newtime for cross-language). Generated UnmarshalMsg has no size limits unless //msgp:limit is set, and no depth guard for recursive types. benc, mus-go, colfer and 200sc/bebop are faster and about half the size in the same harness; msgp wins only if you need MessagePack on the wire.

## Caveats and trade-offs

msgp and vmihailenco/msgpack are both MessagePack implementations, so the win is codegen vs reflection over the same wire format, not a new format. The shared report page is user-generated (the page says so; CI only validates, last regenerated 2025-07-04) and gives no CPU model or Go version, so the tier is capped at B. The shootout pins msgp v1.1.8 and vmihailenco/msgpack v5.3.5, while the current msgp release is v1.6.4. Against the other codegen MessagePack entry (shamaton/msgpackgen/map, 242/358 ns/op), msgp is \~1.8x faster (derived from page data).

Requires a `go generate` codegen step tied to struct tags; both implementations produce the same MessagePack wire format so this is a faster implementation of the baseline format rather than a different format beating it.

## Maintenance

Actively maintained (last commit 2026-09-21; v1.6.4 released 2026-04-14 after a run of feature releases in 2025), MIT-licensed, about 1.95k stars. No GitHub security advisories are published, and the README calls the runtime library mostly stable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** The independent go_serialization_benchmarks report shows the msgp row at 134/200 ns/op and 97 B, against the vmihailenco/msgpack row (the incumbent reflection-based Go MessagePack library) at 921/1216 ns/op and 92 B. The code is public, but the report is user-generated with no CPU model or Go version, so it cannot be A.
- **Verifier notes:** All claimed numbers and sizes match the msgp and msgpack rows, and the ratios (\~6.9x, \~6.1x) are correct. Metadata checks out: MIT, 1,951 stars, last commit 2026-09-21, active, not archived or a fork.
- **Fields the verifier corrected:** `caveats`
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
  - <https://github.com/tinylib/msgp>
  - <https://github.com/tinylib/msgp/releases/latest>
- **Sources the enricher read:**
  - <https://github.com/tinylib/msgp>
  - <https://github.com/tinylib/msgp/blob/master/README.md>
  - <https://github.com/tinylib/msgp/blob/master/go.mod>
  - <https://github.com/tinylib/msgp/blob/master/main.go>
  - <https://github.com/tinylib/msgp/blob/master/Makefile>
  - <https://github.com/tinylib/msgp/blob/master/.github/workflows/test.yml>
  - <https://github.com/tinylib/msgp/blob/master/gen/marshal.go>
  - <https://github.com/tinylib/msgp/blob/master/gen/unmarshal.go>
  - <https://github.com/tinylib/msgp/blob/master/parse/directives.go>
  - <https://github.com/tinylib/msgp/blob/master/parse/getast.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/unsafe.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/purego.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/advise_linux.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/elsize.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/elsize_default.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/read_bytes.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/write_bytes.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/size.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/defs.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/extension.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/read.go>
  - <https://github.com/tinylib/msgp/blob/master/msgp/write.go>
  - <https://github.com/tinylib/msgp/releases>
  - <https://github.com/tinylib/msgp/releases/latest>
  - <https://github.com/tinylib/msgp/issues>
  - <https://github.com/tinylib/msgp/issues/235>
  - <https://github.com/tinylib/msgp/issues/271>
  - <https://github.com/tinylib/msgp/issues/411>
  - <https://github.com/tinylib/msgp/pull/389>
  - <https://github.com/tinylib/msgp/pull/419>
  - <https://github.com/tinylib/msgp/security/advisories>
  - <https://github.com/tinylib/msgp/wiki>
  - <https://github.com/tinylib/msgp/wiki/Preprocessor-Directives>
  - <https://github.com/tinylib/msgp/wiki/Using-the-Code-Generator>
  - <https://github.com/tinylib/msgp/wiki/Type-Mapping-Rules>
  - <https://github.com/tinylib/msgp/wiki/Tips-and-Tricks>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/README.md>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/go.mod>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/msgpack_tinylib/msgp.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/msgpack_tinylib/structdef.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/msgpack_vmihailenco/msgpack_vmihailenco.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/commits/master/report/data.js>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/tinylib/msgp`) · [data/wave4/enrich/raw/github_com_tinylib_msgp.json](../../../data/wave4/enrich/raw/github_com_tinylib_msgp.json) (enrichment confidence 0.8)

</details>
