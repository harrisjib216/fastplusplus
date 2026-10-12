# greenpack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Go msgpack2 code generator with versioned, typed field names; \~15% faster writes than gogo/protobuf in author's 2017 benchmark.

| | |
|---|---|
| **Beats** | Protocol Buffers (Go implementations: gogo/protobuf gogofaster, golang/protobuf, DeDiS/protobuf); FlatBuffers Go and Cap'n Proto Go are also in the table |
| **Claimed result** | This claim holds for writes only. GreenPackMarshal takes 129 ns/op with 0 B/op, against 152 ns/op with 64 B/op for GogoprotobufMarshal (\~15% faster, derived from page data). It is also faster than golang/protobuf (GoprotobufMarshal, 500 ns/op), DeDiS/protobuf (ProtobufMarshal, reflection-based, 936 ns/op), FlatBuffers Go (379 ns/op) and Cap'n Proto via glycerine/go-capnproto (498 ns/op). ZebraPack, by the same author, is faster at 120 ns/op. The README's '6% faster reads' does not measure greenpack. It rests on GreenPackUnmarshal (224 ns/op) against GogoprotobufUnmarshal (240 ns/op), but BenchmarkGreenPackUnmarshal calls ZebraPack's ZMarshalMsg/ZUnmarshalMsg, not GreenUnmarshalMsg. That row is therefore a second run of BenchmarkZebraPackUnmarshal, which measured 236 ns/op in the same run. |
| **Workload** | Marshal/Unmarshal microbenchmarks of a fixed struct (name, birthday, phone, siblings, spouse, money) across \~20 Go serialization libraries, using Go's testing/benchmark tool, in the companion go_serialization_benchmarks shootout repo. |
| **Metric** | throughput |
| **Hardware** | 3.1 GHz Intel Core i7 (MacBook Pro 13"); no CPU model number stated |
| **Compiler and flags** | The README header says 'Go 1.8beta2'. The August 2017 commit that added greenpack (de65278) replaced the result tables but left that header from the January 2017 run unchanged, so the Go version of the greenpack run is unconfirmed. The command is go test -bench='.\*' ./ and no other flags are given. |
| **Adoption** | 115 stars |
| **Last commit** | 2026-01-23 |
| **Links** | [repository](https://github.com/glycerine/greenpack) · [benchmark](https://github.com/glycerine/go_serialization_benchmarks#results) |

## Verdict

In the author's 2017 fork of alecthomas/go_serialization_benchmarks (6-field struct, 3.1 GHz Core i7 MacBook Pro 13", Go version unconfirmed; the header says 1.8beta2), GreenPackMarshal took 129 ns/op with 0 allocs, against 152 ns/op with 1 alloc (64 B) for gogo/protobuf's proto.Marshal. greenpack wrote into a reused 512-byte buffer while gogo allocated its output on every call. The 224 vs 240 ns/op read row is invalid because BenchmarkGreenPackUnmarshal calls ZebraPack's ZMarshalMsg/ZUnmarshalMsg.

## Use it when

- Go services whose structs must be readable from Python, R or JS with a stock msgpack library and no generated code or schema file.
- You want the Go struct definition to be the schema: no .proto/IDL, no protoc or C++ toolchain, just `//go:generate greenpack`.
- Write-heavy paths that can reuse an output buffer: MarshalMsg(buf) appends into the caller's slice. The 2017 run measured 129 ns/op and 0 allocs/op for a 6-field struct.
- Schemas that evolve over time: numbered zid fields, `deprecated` tombstones and conflict detection at generate time, plus signed/unsigned integer types that stock msgpack encoders lose.
- Pipelines that need serialization hooks (PreSave/PostLoad, e.g. to flatten trees) or generated MariaDB read/write methods (`-sql mariadb`).

## Skip it when

- Wire size matters. Every key carries the field name, zid and type clue, so the benchmark struct encoded to \~142 bytes, against \~59 for ZebraPack (derived from the MB/s and ns/op columns). Use ZebraPack, `-omit-clue`/`-alltuple`, or protobuf instead.
- You need C++ or other non-Go code generation. None exists; the author points C++ users to generic msgpack libraries (issue #16).
- You are choosing it for faster reads than gogo/protobuf. The only published greenpack read number actually measured ZebraPack, and the author's 2024 CBOR comparison shows greenpack Unmarshal at 322 ns/op with 2 allocs/op.
- Code that relies on generics or shared pointers. Type-parameterized fields are skipped unless you pass `-generics=true`, which the author says is much slower. Automatic pointer dedup has been off by default since v0.529.0 because of unresolved errors, and Marshal/Unmarshal never supported it.
- You need a large-team maintenance guarantee. It is a single-author project; a report that map[int64]map[int8]T writes no data (#12) was closed without a fix.

## How it is fast

It uses reflection-free code generation inherited from tinylib/msgp. Marshal pre-sizes the output with the generated Msgsize() via msgp.Require, then writes each field key as a precomputed msgpack byte literal (`o = append(o, 0xae, 0x4e, ...)`) followed by a type-specific Append\* call into a caller-supplied []byte. Repeated marshals into a reused buffer therefore allocate nothing. Unmarshal reads map keys zero-copy and dispatches through a compiled Go string switch to per-field decoders, mutates existing slices and maps in place, and zeroes missing fields by replaying a msgpack nil through the same switch (a fixed-size NilBitsStack) instead of allocating.

## Compared with alternatives

Pick greenpack over ZebraPack (same author: 120 vs 129 ns/op writes, \~59 vs \~142-byte payload) when other-language consumers must decode with any msgpack library and no schema, because greenpack data is fully self-describing. Pick ZebraPack or Karmem when raw Go speed or wire size matters more, and SBE, Bebop or Apache Fory (C++) for C++-side work, since greenpack has no C++ generator.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | runtime package github.com/glycerine/greenpack/msgp (depends on glycerine/fwd, 4d63.com/tz); the generator also uses golang.org/x/tools and shurcooL/go-goon; goconvey for tests |
| **Minimum toolchain** | Go 1.24.2 (go.mod directive) |
| **Platforms** | any Go target; pure Go, uses unsafe string/slice casts (an appengine build tag provides a no-unsafe variant) |
| **Thread safety** | Not documented. From the source, generated Marshal/Unmarshal keep decode state (NilBitsStack) in locals, while msgp.Writer/Reader are per-stream objects that hold dedup state. |
| **Drop-in for the baseline** | no |

## Gotchas

- `-fast-strings` makes decoded strings alias the input buffer through unsafe, so that buffer must not be reused. In current master, msgp/read_bytes.go ReadStringBytes takes the zero-copy path only when `err != nil`, so successful reads still copy with string(v). Measure allocations yourself before relying on the zero-alloc claim.
- Cross-language readers see extras. time.Time is msgpack extension type 5 (normalized to UTC), not the standard -1 timestamp, and time.Duration is extension 7. EncodeMsg streams also add an "@" struct-name key unless you pass `-no-structnames-onwire`; the MarshalMsg path does not.
- All fields are omitempty by default, so zero values never reach the wire and absent keys decode as zero. The nil-replay stack that implements this is fixed at 8 nested struct levels (MaxNestedStructPointerDepth) and panics beyond that.
- Go module versioning: tags were renamed to v0.xxx.0, and the proxy still reports the old non-module v5.1.2 as @latest. Pin an explicit v0.5xx.0 tag (tags go up to v0.541.0).

## Known shortcomings

- The benchmark's GreenPackUnmarshal row actually calls ZebraPack's ZUnmarshalMsg, so the read-side number is ZebraPack's code, not greenpack's (224 vs 236 ns is run-to-run noise on identical code). The write comparison reuses a 512-byte buffer while gogo proto.Marshal allocates per call.

## Caveats and trade-offs

These are first-party numbers: greenpack's author ran them in his own fork (glycerine/go_serialization_benchmarks, 8 stars, last commit 2017-08-05). The upstream alecthomas suite does not include greenpack. The read comparison is invalid because of a copy-paste bug: BenchmarkGreenPackUnmarshal uses ZebraPack's generated ZMarshalMsg/ZUnmarshalMsg. The throughput columns confirm this: the 'greenpack' unmarshal payload is \~59 bytes, the same as ZebraPack's, while greenpack marshal emits \~142 bytes. Only the write result measures greenpack. The margins are small next to run-to-run noise: the earlier run had ZebraPackUnmarshal at 227 ns/op and Gogoprotobuf at 232 ns/op. Hardware and Go version (2017, Go 1.8-era) are dated. The only baselines are Go protobuf implementations, not C++ protobuf. greenpack itself is still maintained, with a last commit on 2026-01-23.

Pure Go, code-generation based (like msgp/msgpack), msgpack2-compatible wire format for cross-language interoperability. Modest win margin (6-15%) over Protobuf, not a dramatic speedup; author explicitly notes ZebraPack and CapNProto/Gencode can be faster in some cases.

## Maintenance

Actively maintained by its single author (last commit 2026-01-23, tags up to v0.541.0). MIT-licensed, pure Go, and used via go generate, so it is easy to adopt in Go projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** These are first-party numbers. greenpack's author added greenpack to his own 8-star fork of alecthomas/go_serialization_benchmarks in 2017, and the 1.6k-star upstream suite has never included greenpack. The code is public (serialization_benchmarks_test.go), but no flags and no CPU model are given (only '3.1 GHz Intel Core i7'). The Go version is uncertain. The fork is not a well-known independent suite, so B does not apply.
- **Verifier notes:** I downgraded from B to C because the benchmark is first-party and the README's read claim does not hold. BenchmarkGreenPackUnmarshal decodes with ZebraPack's methods, so only the write result (129 vs 152 ns/op against gogoprotobuf) measures greenpack. The record's '936 ns/op Protobuf' figure is DeDiS/protobuf; golang/protobuf is 500 ns/op. Metadata checked: MIT, 115 stars, not a fork, not archived, last commit 2026-01-23 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/glycerine/go_serialization_benchmarks#results>
  - <https://github.com/glycerine/go_serialization_benchmarks>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/serialization_benchmarks_test.go>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/greenpack_gen.go>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/zebrapack_gen.go>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/structdef.go>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/read.speed.txt>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/write.speed.txt>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/Makefile>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/stats>
  - <https://github.com/glycerine/go_serialization_benchmarks/commit/de65278ab53b28618cfbe5d83f717dfef5eba51c>
  - <https://github.com/glycerine/greenpack>
  - <https://github.com/glycerine/greenpack/blob/master/README.md>
  - <https://github.com/alecthomas/go_serialization_benchmarks>
- **Sources the enricher read:**
  - <https://github.com/glycerine/greenpack>
  - <https://github.com/glycerine/greenpack/blob/master/README.md>
  - <https://github.com/glycerine/greenpack/blob/master/go.mod>
  - <https://github.com/glycerine/greenpack/blob/master/cfg/config.go>
  - <https://github.com/glycerine/greenpack/blob/master/gen/marshal.go>
  - <https://github.com/glycerine/greenpack/blob/master/gen/unmarshal.go>
  - <https://github.com/glycerine/greenpack/blob/master/gen/template.go>
  - <https://github.com/glycerine/greenpack/blob/master/gen/encode.go>
  - <https://github.com/glycerine/greenpack/blob/master/msgp/unsafe.go>
  - <https://github.com/glycerine/greenpack/blob/master/msgp/write_bytes.go>
  - <https://github.com/glycerine/greenpack/blob/master/msgp/read_bytes.go>
  - <https://github.com/glycerine/greenpack/blob/master/msgp/nilbits.go>
  - <https://github.com/glycerine/greenpack/blob/master/msgp/dedup.go>
  - <https://github.com/glycerine/greenpack/blob/master/msgp/runtimecfg.go>
  - <https://github.com/glycerine/greenpack/blob/master/msgp/extension.go>
  - <https://github.com/glycerine/greenpack/issues?q=is%3Aissue>
  - <https://github.com/glycerine/greenpack/issues/4>
  - <https://github.com/glycerine/greenpack/issues/8>
  - <https://github.com/glycerine/greenpack/issues/11>
  - <https://github.com/glycerine/greenpack/issues/12>
  - <https://github.com/glycerine/greenpack/issues/16>
  - <https://github.com/glycerine/greenpack/commits/master>
  - <https://github.com/glycerine/greenpack/tags>
  - <https://github.com/glycerine/go_serialization_benchmarks#results>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/serialization_benchmarks_test.go>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/greenpack_gen.go>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/write.speed.txt>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/read.speed.txt>
  - <https://github.com/glycerine/demo_cbor>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/glycerine/greenpack`) · [data/wave4/enrich/raw/github_com_glycerine_greenpack.json](../../../data/wave4/enrich/raw/github_com_glycerine_greenpack.json) (enrichment confidence 0.8)

</details>
