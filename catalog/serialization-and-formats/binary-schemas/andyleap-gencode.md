# gencode

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Go` · `GPL-2.0` · 🔴 abandoned

> Go code generator for a compact schema-driven binary format; marshals \~2.3x and unmarshals \~2.7x faster than protobuf-go.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | Safe variant: marshal 122 ns/op vs protobuf-go 287 ns/op (\~2.35x), unmarshal 132 vs 356 ns/op (\~2.7x). gencode/unsafe_reuse variant (buffer reuse plus unsafe strings; protobuf-go has no like-for-like row): marshal 48 ns/op (\~6x), unmarshal 104 ns/op (\~3.4x) (derived from page data). |
| **Workload** | Marshal/unmarshal of the same fixed struct used across the go_serialization_benchmarks harness. |
| **Metric** | latency |
| **Adoption** | 324 stars |
| **Last commit** | 2017-11-24 |
| **Links** | [repository](https://github.com/andyleap/gencode) · [benchmark](https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js) |

## Verdict

alecthomas/go_serialization_benchmarks measures a struct of two strings, a time.Time, an int, a bool and a float64 in a user-generated report that gives no Go version or CPU. There, gencode marshals in 122 ns/op and unmarshals in 132 ns/op, against 287/356 ns/op for protobuf-go (\~2.3x/\~2.7x), with 3 allocations each; gogo/protobuf on the same page is 115/166 ns/op. The gencode/unsafe_reuse row (reused buffer, -unsafe numeric stores, time as int64) reaches 48/104 ns/op, but protobuf-go has no matching buffer-reuse row.

## Use it when

- Go-to-Go payloads (RPC messages, cache values, on-disk records) where you own both ends and regenerate both from one schema file; there is only a Go backend.
- Small flat structs of ints, floats and short strings where per-message CPU cost matters: about 120-130 ns per marshal/unmarshal on the shootout's 6-field struct, against 287/356 ns for protobuf-go.
- Structs made mostly of fixed-width numbers, where offsets fold to constants: in the author's README run (hardware not stated), an all-fixed 4-field struct deserializes in 20.7 ns/op.
- Length-prefixed message streams over sockets or files: mark the struct `framed` to get Serialize(io.Writer)/Deserialize(io.Reader).
- Messages that can be one of several struct types: a `union` field becomes a Go interface you can type-switch on, with a varint type tag on the wire.

## Skip it when

- Decoding untrusted or possibly truncated bytes. Unmarshal has no bounds checks and panics with 'index out of range' on truncated input (issue #20, open since 2018). Lengths read from the wire go straight into make(), so a hostile length can force a huge allocation.
- Any schema evolution. The format is positional with no field numbers, defaults or unknown-field skipping, so adding, removing or reordering a field breaks existing data and older readers.
- Cross-language use or map-heavy data. There is only a Go backend and no map type; PR #12, which added maps and C++, was never merged.
- Anything that needs a maintained, easy-to-build tool. The last commit was 2017-11-24 and the repo has no go.mod. The generator no longer builds against the current andyleap/parser unless you pin the 2016 version (issue #29). The parser silently accepts a garbage schema (#19), and `[][N]byte` fields produce code that does not compile (#23).
- Wire size against protobuf. On the shootout struct the safe variant encodes to 53 bytes, against 51 for protobuf-go.

## How it is fast

The generator emits straight-line, type-specialized code with no reflection. The wire format is positional: fields are written in declared order with no field numbers or wire-type tags, so there are no tag bytes to write, read or switch on. Marshal runs Size() first and allocates the output once, or reuses the caller's buffer if it is big enough. Offsets of fixed-width fields are folded into constants at generation time (`buf[i+9]`), so a run of fixed fields becomes plain byte stores without advancing the index (the author explains this in issue #24). Ints are written little-endian by byte shifts, or with `-unsafe` as one unaligned native-endian pointer store; strings, slices and `v`-prefixed ints use LEB128 varints, with zigzag encoding for signed varints.

## Compared with alternatives

In the same shootout, colfer (115/123 ns), mus-go (92/122), benc (81/103) and 200sc/bebop (94/112) all beat gencode's 122/132 ns safe path, so pick gencode only for what they lack: tagged unions decoded to Go interfaces, a framed io.Reader/io.Writer API, or time kept with its zone offset (gencode's row is labelled fulltzoffset; mus and benc are labelled no time support). It is also a small, readable reference for how offset folding in a code generator works.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | The generated code imports only the Go standard library (io, time, unsafe) and needs no runtime package. The generator CLI depends on github.com/andyleap/parser, which must be pinned to db5a13a7cd46 from 2016 because the 2021 generics rewrite breaks the build (issue #29), and on github.com/kr/pretty. |
| **Minimum toolchain** | Not documented. The repo predates Go modules and has no go.mod, and issue #23 reports use with go1.11. Building the generator with current Go needs a manual go.mod that pins andyleap/parser. |
| **Platforms** | Default mode runs on any Go target because it uses explicit little-endian byte shifts. With -unsafe, fixed-width ints and floats use unaligned native-endian pointer loads and stores, so the wire format matches the safe mode only on little-endian hosts. PR #11 for big-endian support was never merged. |
| **Thread safety** | Not documented. From the templates, the generated methods touch only the receiver and the buffer passed in, with no package-level state. |
| **Drop-in for the baseline** | no |

## Gotchas

- Unmarshal almost never returns an error. Only nested and framed paths return one (the framed length check returns io.EOF), and other malformed input panics. Wrap decoding of external bytes in recover().
- `-unsafe` changes only fixed-width ints and floats; strings are still copied on unmarshal. The shootout labels its gencode/unsafe_reuse row as unsafe-string with full-tz-offset time. In fact that row's schema stores BirthDay as an int64 UnixNano, and it reuses a 1 KB marshal buffer, so its 48 ns marshal mixes three changes.
- time fields reserve exactly 15 bytes for time.MarshalBinary, and the error from UnmarshalBinary is ignored. Current Go writes 16 bytes when a zone offset has leftover seconds (LMT zones), so those times fail to round-trip without any error.
- Marshal(buf) writes into buf when its capacity is big enough and returns a slice of it, so the next Marshal into the same buffer overwrites earlier output. Size() also runs on every Marshal, which is an extra pass over strings and varints.

## Known shortcomings

- Not safe for untrusted input: Unmarshal has no bounds checks (truncated input panics, #20) and wire lengths go straight into make(). The generator does not build today without pinning andyleap/parser to db5a13a7cd46 (#29). The unsafe_reuse row mixes buffer reuse, unsafe numeric stores and a cheaper time encoding, and strings are still copied. Time values with LMT zone offsets fail to round-trip silently. No schema evolution; colfer, mus-go, benc and 200sc/bebop beat its safe path. Unclear whether GPL-2.0 covers generated code.

## Caveats and trade-offs

The shared report page is user-generated (the page says so; CI only validates, last regenerated 2025-07-04) and gives no CPU model or Go version, so the tier is capped at B. The \~6x marshal figure compares the unsafe_reuse variant with a protobuf-go row that does not reuse buffers, so it is not like-for-like. Against gogo/protobuf on the same page, gencode is slightly slower on marshal (122 vs 115 ns/op) and faster on unmarshal (132 vs 166 ns/op). The shootout uses checked-in generated gencode code; its Makefile generator lines are commented out. GPL-2.0 is copyleft. Unmaintained, last commit 2017-11-24, but still useful as a technique reference.

Codegen-based fixed schema; project has had no commits since 2018 so bug fixes/newer Go features are unlikely; copyleft (GPL-2.0) license may deter some integrations.

## Maintenance

Abandoned since 2017-11-24, and the generator is GPL-2.0 (the project does not say whether that covers generated output). The generated code needs only the standard library, so you can vendor it once the generator is built with a pinned parser dependency, but treat it as a technique reference rather than a live dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** In the same independent go_serialization_benchmarks report, the gencode rows (122/132 ns/op; unsafe_reuse 48/104) sit next to the protobuf-go row (287/356 ns/op). The code is public, but the report is user-generated with no CPU model or Go version, so it cannot be A.
- **Verifier notes:** The numbers match the page. The 2.3-6x range was clarified so the \~6x upper bound is tied to the unsafe_reuse variant. last_commit corrected: 2018-08-13 is the repo's pushed_at date, and the latest commit on master (the only branch) is 2017-11-24. The license (GPL-2.0), 324 stars and abandoned status are correct. The README's own benchmark compares only against GOB, JSON and MSGP, not protobuf.
- **Fields the verifier corrected:** `last_commit`, `claimed_speedup`, `caveats`
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
  - <https://github.com/andyleap/gencode>
- **Sources the enricher read:**
  - <https://github.com/andyleap/gencode>
  - <https://github.com/andyleap/gencode/blob/master/README.md>
  - <https://github.com/andyleap/gencode/blob/master/LICENSE>
  - <https://github.com/andyleap/gencode/blob/master/main.go>
  - <https://github.com/andyleap/gencode/blob/master/doc.go>
  - <https://github.com/andyleap/gencode/blob/master/schema/schema.go>
  - <https://github.com/andyleap/gencode/blob/master/schema/parser.go>
  - <https://github.com/andyleap/gencode/blob/master/backends/golang/init.go>
  - <https://github.com/andyleap/gencode/blob/master/backends/golang/struct.go>
  - <https://github.com/andyleap/gencode/blob/master/backends/golang/type_string.go>
  - <https://github.com/andyleap/gencode/blob/master/backends/golang/type_int.go>
  - <https://github.com/andyleap/gencode/blob/master/backends/golang/type_float.go>
  - <https://github.com/andyleap/gencode/blob/master/backends/golang/type_time.go>
  - <https://github.com/andyleap/gencode/blob/master/backends/golang/type_slice.go>
  - <https://github.com/andyleap/gencode/blob/master/backends/golang/type_union.go>
  - <https://github.com/andyleap/gencode/blob/master/backends/golang/type_struct.go>
  - <https://github.com/andyleap/gencode/blob/master/backends/golang/type_pointer.go>
  - <https://github.com/andyleap/gencode/blob/master/bench/test.schema>
  - <https://github.com/andyleap/gencode/blob/master/bench/fixed.schema>
  - <https://github.com/andyleap/gencode/blob/master/bench/test.schema.gen.go>
  - <https://github.com/andyleap/gencode/blob/master/bench/gencode_test.go>
  - <https://github.com/andyleap/gencode/issues>
  - <https://github.com/andyleap/gencode/issues/1>
  - <https://github.com/andyleap/gencode/issues/5>
  - <https://github.com/andyleap/gencode/issues/19>
  - <https://github.com/andyleap/gencode/issues/20>
  - <https://github.com/andyleap/gencode/issues/22>
  - <https://github.com/andyleap/gencode/issues/23>
  - <https://github.com/andyleap/gencode/issues/24>
  - <https://github.com/andyleap/gencode/issues/27>
  - <https://github.com/andyleap/gencode/issues/29>
  - <https://github.com/andyleap/gencode/pulls>
  - <https://github.com/andyleap/gencode/pull/11>
  - <https://github.com/andyleap/gencode/pull/21>
  - <https://github.com/andyleap/parser>
  - <https://github.com/andyleap/parser/commits/master>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/README.md>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/Makefile>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/benchmarks.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/gencode/gencode.go>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/gencode/gencode.schema>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/gencode/gencode-unsafe.schema>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/internal/serializers/gencode/gencode-unsafe.schema.gen.go>
  - <https://github.com/golang/go/blob/master/src/time/time.go>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/andyleap/gencode`) · [data/wave4/enrich/raw/github_com_andyleap_gencode.json](../../../data/wave4/enrich/raw/github_com_andyleap_gencode.json) (enrichment confidence 0.8)

</details>
