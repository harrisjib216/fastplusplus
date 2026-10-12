# chmike/varint

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-3-Clause` · 🟡 stale

> Go prefix-code varint for uint64; about 2x faster than encoding/binary Uvarint for values above 35 bits.

| | |
|---|---|
| **Beats** | Go encoding/binary PutUvarint/Uvarint (LEB128) |
| **Claimed result** | docs/data.txt (i5-11400, go test -bench): encode at 63 bits 2.992 ns/op versus 5.051 ns/op for binary.PutUvarint (about 1.7x, derived from page data); decode at 63 bits 2.754 versus 5.510 ns/op (about 2.0x, derived from page data); encode+decode round trip at 63 bits 5.726 versus 8.256 ns/op. At 7 bits encode is a tie (0.6907 versus 0.6875 ns/op) and decode is slower than Uvarint (1.154 versus 0.9654 ns/op); the gap opens above 35 bits. |
| **Workload** | Encoding and decoding single unsigned integers of 7 to 63 bits with a big-endian prefix-code varint, ns/op. |
| **Metric** | latency |
| **Hardware** | 11th Gen Intel(R) Core(TM) i5-11400 @ 2.60GHz, Linux amd64 (from docs/data.txt header) |
| **Adoption** | 15 stars |
| **Last commit** | 2023-10-07 |
| **Links** | [repository](https://github.com/chmike/varint) · [benchmark](https://github.com/chmike/varint/blob/master/docs/data.txt) |

## Verdict

First-party go test -bench output on an 11th Gen Intel Core i5-11400 (Linux amd64, Go version not stated) compares Encode/Decode with binary.PutUvarint/Uvarint, one fixed value per bit width: at 63 bits encode is 2.992 versus 5.051 ns/op and decode 2.754 versus 5.510 ns/op (about 1.7x and 2.0x, derived from page data); at 7 bits encode ties and decode is about 20% slower.

## Use it when

- Go code that defines its own binary format and stores many uint64 values above about 2^35 (timestamps in ns, 64-bit ids, hashes), where encode drops from 5.05 to 2.99 ns and decode from 5.51 to 2.75 ns at 63 bits on an i5-11400.
- Read-mostly formats where a 9-byte maximum (versus 10 for LEB128) and a length readable from the first byte are useful, for example to skip fields without decoding.
- Callers that want non-panicking encode/decode with a 0-length error signal instead of binary.PutUvarint's panic on short buffers.
- As a reference design for a prefix varint in C or C++; the 150-line source is BSD-3-Clause and straightforward to port.

## Skip it when

- Data that must interoperate with LEB128 (protobuf, Go encoding/binary Uvarint, DWARF, WebAssembly): the byte layout differs.
- Mostly small values: at 7 bits decode is slower than binary.Uvarint (1.154 versus 0.9654 ns) and encode at 14-35 bits is level or slightly slower, so the gain exists only above about 35 bits.
- Bulk integer arrays: it handles one value per call with no SIMD; block codecs such as Stream VByte or FastPFor in the catalogue are orders of magnitude faster per integer.
- Signed integers: no zigzag helper is provided, only uint64.
- Projects that need an active upstream: 12 commits, last one 2023-10-07, no releases.

## How it is fast

Length is known from the first byte, so decoding is one switch on the header byte followed by straight-line shifts and ORs with no per-byte continuation loop (unlike LEB128's 7-bit groups). Encoding picks the length with a range switch, ORs in the header bits and byte-swaps with math/bits.ReverseBytes16/32/64 before storing bytes. Values below 128 take an inlinable fast path in Encode; Decode is not inlined.

## Compared with alternatives

Choose it over dennwc/varint when you control the format and your values are mostly large (dennwc keeps LEB128 compatibility and gains at small sizes too); choose streamvbyte-simdgo or Stream VByte for arrays of 32-bit values rather than one-off uint64 fields.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (math/bits from the Go standard library) |
| **Minimum toolchain** | Go 1.17 (go.mod) |
| **Platforms** | any Go target; pure Go, no assembly |
| **Thread safety** | Encode and Decode are pure functions with no shared state; safe for concurrent use on distinct buffers. |
| **Drop-in for the baseline** | partial: same call shape as binary.PutUvarint/Uvarint (with different error semantics), but an incompatible wire format, so only for new data |

## Gotchas

- The README's decoding example is wrong: it calls varint.Decod and binds the results as 'l, v', while Decode returns (value, length); copying it will not compile and, once fixed, swaps the variables.
- Decode accepts non-minimal encodings (for example 0x80 0x05 decodes to 5), so the same value can have several byte representations; do not hash or compare encoded bytes for equality without re-encoding.
- The benchmark encodes one constant value per sub-benchmark (always the same branch), which the README itself says favours this code; and it uses a buffer whose length is rand.Int()%1010, so a run with a length under 9 would make Encode a silent no-op.
- Tests check one bit pattern (0xAAAA...) per width plus the empty buffer; there is no fuzzing or truncated-value test beyond length 0.

## Known shortcomings

- Go, not C++. 7-bit decode is slower than the stdlib (1.154 vs 0.9654 ns/op); the author warns the benchmark favours its own code through branch prediction.
- README Decode example is wrong (varint.Decod, return order swapped). Decode accepts non-minimal encodings. The benchmark uses one constant value per width and a buffer length of rand.Int()%1010, so a length under 9 makes Encode a no-op. Tests cover one bit pattern per width, no fuzzing. Wire format is not LEB128. Go 1.17, stale since 2023-10-07.

## Caveats and trade-offs

Go version not stated. Win is limited to values over about 35 bits; at 7 bits decode is about 20% slower than the standard library (not inlined), and encode at 14-35 bits is slightly slower. The README itself warns that the benchmark advantages chmike/varint through branch prediction because each run encodes values of a single magnitude. Uses a different wire format (big-endian prefix code), so it is not a drop-in replacement for LEB128 data. Marginal fit for the bitpacking category.

Different wire format (prefix code, most significant byte first), incompatible with LEB128 and protobuf; the speedup appears mainly for large values. Go only.

## Maintenance

Stale since 2023-10-07 (15 stars, no open issues, no releases), but BSD-3-Clause and a single small file, so easy to vendor or port.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/data.txt is raw `go test -bench=.` output with the CPU model (i5-11400) comparing Encode/Decode against BenchmarkStdEncode/StdDecode (encoding/binary), and the benchmark code is public in varint_test.go; the Go version is not stated and the author warns the benchmark favours his code, so first-party C.
- **Verifier notes:** All quoted numbers match docs/data.txt exactly. Metadata (BSD-3-Clause, 15 stars, last commit 2023-10-07, stale) confirmed. Claim corrected to add decode numbers and the 7-bit decode loss.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party docs/data.txt
- **Pages the verifier opened:**
  - <https://github.com/chmike/varint>
  - <https://github.com/chmike/varint/commits>
  - <https://github.com/chmike/varint/blob/master/docs/data.txt>
  - <https://raw.githubusercontent.com/chmike/varint/HEAD/docs/data.txt>
  - <https://raw.githubusercontent.com/chmike/varint/HEAD/README.md>
  - <https://raw.githubusercontent.com/chmike/varint/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/chmike/varint/HEAD/varint_test.go>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/chmike/varint/HEAD/README.md>
  - <https://raw.githubusercontent.com/chmike/varint/HEAD/varint.go>
  - <https://raw.githubusercontent.com/chmike/varint/HEAD/varint_test.go>
  - <https://raw.githubusercontent.com/chmike/varint/HEAD/docs/data.txt>
  - <https://raw.githubusercontent.com/chmike/varint/HEAD/go.mod>
  - <https://raw.githubusercontent.com/chmike/varint/HEAD/LICENSE>
  - <https://github.com/chmike/varint>
  - <https://github.com/chmike/varint/issues?q=is%3Aissue>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/chmike/varint`) · [data/wave9/enrich/raw/github_com_chmike_varint.json](../../../data/wave9/enrich/raw/github_com_chmike_varint.json) (enrichment confidence 0.8)

</details>
