# ZebraPack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Go code generator for a msgpack2 format with integer field keys; marshals \~1.3-4x faster than Go protobuf libraries

| | |
|---|---|
| **Beats** | Protocol Buffers (golang/protobuf, gogo/protobuf, DeDiS/protobuf), Cap'n Proto (glycerine/go-capnproto v1, zombiezen capnproto2), FlatBuffers |
| **Claimed result** | Fork README, sorted by write speed: ZebraPackMarshal 120 ns/op, 0 B/op, is the fastest marshal in the table. Against the others: GogoprotobufMarshal 152 ns/op (\~1.27x), FlatBufferMarshal 379 ns/op (\~3.2x), CapNProtoMarshal (glycerine/go-capnproto v1) 498 ns/op (\~4.2x), GoprotobufMarshal (golang/protobuf) 500 ns/op (\~4.2x), ProtobufMarshal (DeDiS/protobuf, reflection-based, not Google's) 936 ns/op (\~7.8x). Ratios derived from page data. Read side: ZebraPackUnmarshal 236 ns/op ties FlatBuffers (236) and is slower than Gencode (196), CapNProto v1 (210) and GreenPack (224). It is \~3.0x faster than Goprotobuf (701, derived from page data). |
| **Workload** | The glycerine fork of alecthomas/go_serialization_benchmarks (serialization_benchmarks_test.go): go test -bench Marshal/Unmarshal of a 6-field struct A (Name, BirthDay, Phone, Siblings, Spouse, Money), picked at random from 1000 pre-generated values, across \~19 Go serializers. The ZebraPack marshal appends into a pre-allocated 512-byte buffer that is reused on every call. |
| **Metric** | throughput |
| **Hardware** | 3.1 GHz Intel Core i7 (MacBook Pro 13"); exact CPU model unstated |
| **Compiler and flags** | Go 1.8beta2 per the README header. That header predates the Aug-2017 re-run that added GreenPack and produced the current table, so it may be stale. Command: go test -bench='.\*'; no other flags stated. |
| **Adoption** | 171 stars |
| **Last commit** | 2018-11-07 |
| **Links** | [repository](https://github.com/glycerine/zebrapack) · [benchmark](https://github.com/glycerine/go_serialization_benchmarks#results) |

## Verdict

These numbers come from the author's own fork of alecthomas/go_serialization_benchmarks, run around 2017 (header says Go 1.8beta2) on a 3.1 GHz Core i7 MacBook Pro 13". ZebraPack marshals a 6-field struct in 120 ns/op with 0 allocs, against 152 ns for gogoprotobuf (\~1.27x), 379 ns for FlatBuffers, 498 ns for go-capnproto v1 and 500 ns for golang/protobuf (\~4.2x); unmarshal is 236 ns against 701 ns for golang/protobuf (\~3x). The comparison favours ZebraPack: it reuses a 512-byte buffer and one target struct and uses zero-copy strings, while the protobuf benchmarks allocate on every call. The table's 'GreenPack' unmarshal row actually calls ZebraPack's ZUnmarshalMsg, so its 224 vs 236 ns gap is run-to-run noise on identical code.

## Use it when

- Go-to-Go messaging or RPC with small, flat structs where write throughput and zero allocations matter (6-field struct: 120 ns/op marshal, 0 allocs)
- You want your existing Go structs to be the schema, with no .proto/.capnp IDL and no protoc or C++ toolchain to maintain
- Consumers in dynamic languages already have msgpack2 decoders and can load a separately shipped schema to turn integer keys back into field names
- Decode-process-discard pipelines where input buffers are not reused while decoded values are still alive, so `-fast-strings` zero-copy is safe
- Maintaining a legacy codebase that already emits ZebraPack data

## Skip it when

- New projects: the author's own repo description points to greenpack as the more recent alternative, and ZebraPack has had no commits since 2018-11-07
- Read-heavy workloads: unmarshal (236 ns) only ties FlatBuffers (236) and gogoprotobuf (240), and is slower than Gencode (196) and go-capnproto v1 (210) in the same table
- You need protobuf wire compatibility, gRPC tooling, or generated code for languages other than Go; other languages must adapt a msgpack2 library and load the schema themselves
- Your protocol needs to tell a zero value from an absent field, or needs required fields: zero-valued fields are left off the wire and decode as zero
- Deeply nested structs: the decoder's nil-tracking stack is fixed at 8 levels (MaxNestedStructPointerDepth) and panics if you go past it

## How it is fast

The generated encoders use no reflection and call msgp.Append\* directly. They append into the caller's buffer, which is pre-sized once from an upper-bound Msgsize, so marshaling allocates nothing. Each field key is a single byte (0x0-0x5 in the benchmark struct) instead of a string, so encoding writes fewer bytes and decoding switches on an integer instead of comparing strings. Decoding fills an existing struct in place. With `-fast-strings`, strings are unsafe casts that point into the input buffer (UnsafeZeroCopy), which removes the string allocations. The benchmark also used `-no-structnames-onwire`, which drops the struct-name field that ZebraPack otherwise writes under key -1 on every struct.

## Compared with alternatives

Against greenpack (same author, maintained into 2026, 129 ns marshal in the same table), ZebraPack gives a smaller wire and a \~7% write edge. The cost is that data is no longer self-describing (greenpack keeps name+zid+type in field names) and the project is abandoned, so for new Go code pick greenpack. Pick ZebraPack over zero-copy formats such as Karmem or FlatBuffers only when you need msgpack2 wire compatibility and Go structs as the schema.

## Integration

| | |
|---|---|
| **Form** | module (Go code-generator binary run via go generate, plus the runtime package github.com/glycerine/zebrapack/msgp that generated code imports) |
| **Dependencies** | runtime: github.com/philhofer/fwd; generator: golang.org/x/tools (go/loader, imports). There is no go.mod file (GOPATH-era). |
| **Minimum toolchain** | Not documented. The benchmarks ran on Go 1.8beta2, and Travis CI targeted Go 1.x and tip in 2017. Builds on current Go releases were not checked. |
| **Platforms** | Any Go target in principle. CI covered amd64 and 386. The unsafe string casts sit behind a !appengine build tag, and a safe appengine fallback file exists. |
| **Thread safety** | Not documented. The generated Marshal/Unmarshal methods keep decoder state in locals and touch only the receiver and the buffer passed in, so separate values can be used concurrently. Using one value from several goroutines needs external locking. |
| **Drop-in for the baseline** | no |

## Gotchas

- Every field behaves as if it were omitempty: zero values are never written, so a decoder cannot tell 0/""/false from a missing field. The author confirmed this was deliberate in issue #10.
- `-fast-strings` makes decoded strings point into the input []byte. If you reuse or mutate that buffer, strings you already decoded change silently. Copy them if you need them to outlive the buffer.
- The published numbers depend on `-fast-strings -no-structnames-onwire`. By default the generator is not zero-copy and writes each struct's name under key -1, which costs time and bytes.
- Non-pointer struct-valued fields were encoded incorrectly (inner fields dropped) until the final commit on 2018-11-07 (issue #10). Older vendored copies need that fix; the reporter's workaround was to use pointer fields.

## Caveats and trade-offs

First-party numbers: ZebraPack's author ran them in his own fork of alecthomas/go_serialization_benchmarks, and the upstream suite (1.6k stars) never added ZebraPack. The table is from 2017, and its 'Go 1.8beta2' header may be stale. The author's own README says the read ranking 'varies occasionally run-by-run'. The marshal lead is small against gogoprotobuf (\~1.27x). ZebraPack marshals into a reused pre-allocated buffer while goprotobuf and DeDiS allocate per call. The 'Protobuf' row is DeDiS reflection-based protobuf, and 'CapNProto' is the author's own go-capnproto v1. The repo points to GreenPack (same author) as 'a more recent alternative'. No commits since 2018-11-07 (&gt;3 years), so abandoned.

Author's own README says use greenpack instead now ('a more recent alternative'). Go-only, code-generation based like msgp, msgpack2-compatible wire format for other-language interop.

## Maintenance

Abandoned since 2018-11-07 and superseded by the author's greenpack. It is MIT-licensed and the runtime msgp package is small enough to vendor, but it has no go.mod, so treat it as legacy code rather than a new dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The results table sits in glycerine/go_serialization_benchmarks, a personal fork (8 stars) where ZebraPack's author added ZebraPack and ran the numbers himself (commits 2016-2017 by Jason E. Aten). The upstream alecthomas suite never included ZebraPack, so these are first-party numbers, not an independent suite. The code is public (serialization_benchmarks_test.go) and Go 1.8beta2 is stated, but the CPU is only '3.1 GHz Intel Core i7' with no model, so it is not A.
- **Verifier notes:** Every number in the record appears on the page in ZebraPack's rows. Tier lowered from B to C because the shootout run was the author's own, not an independent suite. Two row names were misattributed: 'ProtobufMarshal' is DeDiS/protobuf, not Google protobuf, and the gogoprotobuf margin (\~1.27x) was omitted. Metadata (MIT, 171 stars, last commit 2018-11-07, not archived, not a fork) is confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/glycerine/zebrapack>
  - <https://github.com/glycerine/go_serialization_benchmarks#results>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/serialization_benchmarks_test.go>
  - <https://github.com/glycerine/go_serialization_benchmarks/commit/de65278ab53b28618cfbe5d83f717dfef5eba51c>
  - <https://github.com/glycerine/go_serialization_benchmarks/compare/master...glycerine:go_serialization_benchmarks:master>
  - <https://github.com/alecthomas/go_serialization_benchmarks>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
- **Sources the enricher read:**
  - <https://github.com/glycerine/zebrapack>
  - <https://github.com/glycerine/zebrapack/blob/master/README.md>
  - <https://github.com/glycerine/zebrapack/blob/master/cfg/config.go>
  - <https://github.com/glycerine/zebrapack/blob/master/main.go>
  - <https://github.com/glycerine/zebrapack/blob/master/gen/unmarshal.go>
  - <https://github.com/glycerine/zebrapack/blob/master/gen/marshal.go>
  - <https://github.com/glycerine/zebrapack/blob/master/gen/spec.go>
  - <https://github.com/glycerine/zebrapack/blob/master/gen/templateZid.go>
  - <https://github.com/glycerine/zebrapack/blob/master/msgp/runtimecfg.go>
  - <https://github.com/glycerine/zebrapack/blob/master/msgp/unsafe.go>
  - <https://github.com/glycerine/zebrapack/blob/master/msgp/nilbits.go>
  - <https://github.com/glycerine/zebrapack/blob/master/msgp/read.go>
  - <https://github.com/glycerine/zebrapack/blob/master/msgp/write.go>
  - <https://github.com/glycerine/zebrapack/blob/master/msgp/file.go>
  - <https://github.com/glycerine/zebrapack/blob/master/msgp/advise_linux.go>
  - <https://github.com/glycerine/zebrapack/blob/master/msgp/circular.go>
  - <https://github.com/glycerine/zebrapack/blob/master/parse/getast.go>
  - <https://github.com/glycerine/zebrapack/blob/master/printer/print.go>
  - <https://github.com/glycerine/zebrapack/blob/master/zebra/zebra.go>
  - <https://github.com/glycerine/zebrapack/blob/master/.travis.yml>
  - <https://github.com/glycerine/zebrapack/blob/master/Makefile>
  - <https://github.com/glycerine/zebrapack/issues?q=is%3Aissue>
  - <https://github.com/glycerine/zebrapack/pulls?q=is%3Apr>
  - <https://github.com/glycerine/zebrapack/issues/10>
  - <https://github.com/glycerine/zebrapack/issues/7>
  - <https://github.com/glycerine/zebrapack/commits/master>
  - <https://github.com/glycerine/go_serialization_benchmarks#results>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/serialization_benchmarks_test.go>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/structdef.go>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/zebrapack_gen.go>
  - <https://github.com/glycerine/go_serialization_benchmarks/blob/master/greenpack_gen.go>
  - <https://github.com/glycerine/greenpack>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/glycerine/zebrapack`) · [data/wave4/enrich/raw/github_com_glycerine_zebrapack.json](../../../data/wave4/enrich/raw/github_com_glycerine_zebrapack.json) (enrichment confidence 0.8)

</details>
