# streamvbyte-simdgo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🔴 abandoned

> Go port of Stream VByte with avo-generated AVX/AVX2 assembly; decodes uint32 arrays 8-14x faster than encoding/binary Uvarint loops.

| | |
|---|---|
| **Beats** | Go encoding/binary Uvarint/PutUvarint (LEB128 varint), via the repo's util.GetVarint/PutVarint wrappers |
| **Claimed result** | README table: Get8uint32Fast 10095.99 MB/s vs Get8uint32Varint 731.10 MB/s decode (about 13.8x, derived from page data); ReadAllFast Count_1e6 5490.62 MB/s vs ReadAllVarint Count_1e6 695.04 MB/s (about 7.9x, derived from page data); delta variants Get8uint32DeltaFast 7183.20 MB/s vs Get8uint32DeltaVarint 558.46 MB/s. Encode: Put8uint32Fast 8281.18 MB/s vs Put8uint32Varint 1860.67 MB/s. |
| **Workload** | Decoding and encoding uint32 arrays (8 values per call, and streamed counts 1e0 to 1e7) with Stream VByte (AVX/AVX2 assembly) versus Go's standard varint loop. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8700B @ 3.20GHz, darwin/amd64 |
| **Compiler and flags** | Go toolchain, default go test -bench flags; Go version not stated in README (go.mod says go 1.16) |
| **Adoption** | 18 stars |
| **Last commit** | 2021-09-12 |
| **Links** | [repository](https://github.com/thempatel/streamvbyte-simdgo) · [benchmark](https://github.com/thempatel/streamvbyte-simdgo) |

## Verdict

go test -bench output in the README (darwin/amd64, Intel i7-8700B @ 3.20GHz, Go version not stated, go.mod go 1.16): 8-value decode 10095.99 MB/s with AVX versus 731.10 MB/s for an encoding/binary.Uvarint loop (about 13.8x, derived from page data), and stream decode of 1e6 values 5490.62 versus 695.04 MB/s (about 7.9x, derived). The repo's own scalar Stream VByte decoder already reaches about 1659 MB/s, so roughly 2.3x of the gain comes from the format and the rest from SIMD; stream encode gains only about 1.9x (3218.21 vs 1735.08 MB/s at 1e6).

## Use it when

- Go services on amd64 that store or ship large []uint32 (posting lists, IDs, sorted timestamps as deltas) and control the format.
- Bulk decode of thousands to millions of values: README ReadAllFast holds about 5.1-5.7 GB/s from 1e3 to 1e7 values on an i7-8700B.
- Sorted inputs with ReadAllDelta/WriteAllDelta, where the deltas fit in 1-2 bytes and the format then compresses.
- When you want pure Go plus assembly without cgo bindings to lemire/streamvbyte.

## Skip it when

- You must read or write LEB128/protobuf varints: the format is incompatible; see chmike/varint or dennwc/varint for faster Uvarint.
- Non-amd64 targets: by my reading, decode_base.go declares Get8uint32Fast with an int result that does not match the Get8Impl type assigned in decode.go init, and reader_base.go/writer_base.go lack ReadAllDeltaFast/WriteAllDeltaFast, so the packages should not compile on arm64; CI runs only on ubuntu-latest amd64.
- Untrusted or externally sized buffers: the assembly ignores slice lengths, so short input or output slices cause silent out-of-bounds reads or writes rather than Go panics.
- 64-bit integers: only uint32 is supported.
- Production dependency risk: 18 stars, 0 forks, no known importers on pkg.go.dev, last commit 2021-09-12.

## How it is fast

Decoding is a table lookup from each control byte to a PSHUFB mask, then two VPSHUFB shuffles expand 8 packed values into 32 bytes with no per-value branches; delta decoding adds an in-register prefix sum (VPSLLDQ plus VPADDD). Encoding computes control bytes with Lemire's VPMINUB/VPACKUSWB/VPMINSW/VPADDUSW/VPMOVMSKB trick and compacts with VPSHUFB. The assembly is generated with mmcloughlin/avo and chosen at init from golang.org/x/sys/cpu flags (AVX for decode, AVX and AVX2 for encode), with a pure-Go scalar fallback.

## Compared with alternatives

Use it when you need Stream VByte from Go without cgo; from C or C++ use lemire/streamvbyte (the reference, also catalogued), and if the LEB128 format is fixed use chmike/varint or dennwc/varint instead.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys/cpu; github.com/mmcloughlin/avo (imported by the runtime package pkg/shared via asm.go, not only by the generators); github.com/pkg/errors in go.mod |
| **Minimum toolchain** | Go 1.16 (go.mod); uses legacy // +build tags |
| **Platforms** | amd64 with AVX (decode) and AVX2 (encode) for the fast path; scalar fallback on amd64 without them; other architectures advertised but appear not to build |
| **Thread safety** | not documented; functions are stateless apart from read-only lookup tables chosen at init, so concurrent calls on distinct buffers look safe |
| **Drop-in for the baseline** | partial: replaces encoding/binary Uvarint/PutUvarint loops over []uint32 only when you control both encoder and decoder; different wire format and the count must be stored separately |

## Gotchas

- Get8uint32Fast/Put8uint32Fast (and the Asm variants) read 16 bytes at in and at in+len(first group), and write 32 bytes to out, without checking len(in) or len(out); pass at least 16 bytes of slack or use the stream API. The scalar versions panic on short slices instead.
- ReadAllFast holds back the last 3 control bytes on the assumption that each covers 4 data bytes; by my reading, when count%4==1 and the tail values are 1-byte, the last 16-byte load can run up to 3 bytes past len(stream). It stays inside the allocation for streams from WriteAll (which returns a slice of a 4\*count+ctrl buffer), but exactly sized external buffers lack that slack. Not tested here.
- Benchmarks use uniform random uint32, so nearly every value takes 4 bytes in Stream VByte and 5 bytes in LEB128: no compression, constant control bytes, and the varint baseline at its slowest length. MB/s counts 4 bytes per decoded integer.
- The baseline wrapper util.GetVarint loops on pos &lt; len(data) and ignores Uvarint's n&lt;=0 error return, so truncated input loops forever; it is test scaffolding, not library API.

## Known shortcomings

- Non-amd64 build looks broken by reading source (decode_base.go Get8uint32Fast returns int and mismatches Get8Impl; reader_base/writer_base lack ReadAllDeltaFast/WriteAllDeltaFast; CI is amd64 only). The asm Get8/Put8 Fast paths ignore slice lengths, so short slices silently read or write out of bounds. ReadAllFast's tail can read up to 3 bytes past len(stream) when count%4==1 with 1-byte tail values. pkg/shared imports avo at runtime. Benchmark input is uniform random uint32 (4-byte SVB vs 5-byte LEB128, constant controls); scalar SVB alone is 2.3x over Uvarint. util.GetVarint loops forever on truncated input. 0 importers on pkg.go.dev.

## Caveats and trade-offs

Benchmark code is in the repo (pkg/decode, pkg/encode, pkg/stream tests; baseline wrappers in pkg/util/varint.go call encoding/binary Uvarint/PutUvarint) and the README table matches go test output, but the Go version is not stated (go.mod says go 1.16) and the machine is a single macOS i7-8700B. Microbenchmarks on 8 values plus streamed counts. The slow side is Go's own scalar LEB128 varint; the repo's own scalar Stream VByte path (about 1659 MB/s decode) already beats it, so much of the gain is the format, not only SIMD. Encode-side streaming is less impressive: WriteAllFast/Count_1e6 3218.21 MB/s vs WriteAllVarint 1735.08 MB/s (about 1.9x, derived from page data). No comparison to the C reference or other Go SIMD codecs. x86_64 AVX/AVX2 only for the fast path. Last commit 2021-09-12.

Stream VByte format (separate control and data streams), not LEB128 compatible. SIMD path needs x86_64 with AVX/AVX2 (runtime check, scalar fallback). Not usable from C++ directly; the C++ reference is lemire/streamvbyte, which is already catalogued.

## Maintenance

Abandoned since 2021-09-12 (30 commits, v0.4.0, no open issues, no known importers), Apache-2.0 and small enough to vendor if you add length checks and fix the non-amd64 build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README benchmark block (go test -bench output from pkg/decode, pkg/encode, pkg/stream) shows Get8uint32Fast 10095.99 MB/s vs Get8uint32Varint 731.10 MB/s and ReadAllFast/Count_1e6 5490.62 MB/s vs ReadAllVarint/Count_1e6 695.04 MB/s on an Intel i7-8700B; the Varint side is pkg/util/varint.go calling encoding/binary Uvarint/PutUvarint. Benchmark code and CPU are public but the Go toolchain version is not stated, so first-party with partial methodology: C.
- **Verifier notes:** All claimed numbers found verbatim in the README benchmark block. Metadata checked on github.com: Apache-2.0, 18 stars, not a fork, not archived, last commit 2021-09-12 (abandoned, &gt;3 years).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/thempatel/streamvbyte-simdgo>
  - <https://github.com/thempatel/streamvbyte-simdgo/commits>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/README.md>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/go.mod>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/util/varint.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/util/util.go>
- **Sources the enricher read:**
  - <https://github.com/thempatel/streamvbyte-simdgo>
  - <https://github.com/thempatel/streamvbyte-simdgo/tree/main/pkg>
  - <https://github.com/thempatel/streamvbyte-simdgo/tree/main/pkg/decode>
  - <https://github.com/thempatel/streamvbyte-simdgo/tree/main/pkg/encode>
  - <https://github.com/thempatel/streamvbyte-simdgo/tree/main/pkg/shared>
  - <https://github.com/thempatel/streamvbyte-simdgo/tree/main/pkg/stream/reader>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/README.md>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/go.mod>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/Makefile>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/.github/workflows/default.yaml>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/decode/decode.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/decode/decode_amd64.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/decode/decode_amd64.s>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/decode/decode_base.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/decode/decode_test.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/encode/encode.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/encode/encode_amd64.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/encode/encode_amd64.s>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/encode/encode_base.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/shared/asm.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/shared/mode.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/shared/tables.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/stream/reader/reader.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/stream/reader/reader_amd64.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/stream/reader/reader_base.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/stream/reader/reader_test.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/stream/writer/writer.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/stream/writer/writer_amd64.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/stream/writer/writer_base.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/util/util.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/util/varint.go>
  - <https://raw.githubusercontent.com/thempatel/streamvbyte-simdgo/HEAD/pkg/pkg_test.go>
  - <https://pkg.go.dev/github.com/theMPatel/streamvbyte-simdgo/pkg/stream/reader?tab=importedby>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/thempatel/streamvbyte-simdgo`) · [data/wave9/enrich/raw/github_com_thempatel_streamvbyte_simdgo.json](../../../data/wave9/enrich/raw/github_com_thempatel_streamvbyte_simdgo.json) (enrichment confidence 0.75)

</details>
