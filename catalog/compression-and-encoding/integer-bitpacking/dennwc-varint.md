# dennwc/varint

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Fully unrolled Go LEB128/protobuf varint decoder, roughly 1.3x-2.9x faster per call than encoding/binary.Uvarint on Go 1.17.3.

| | |
|---|---|
| **Beats** | Go encoding/binary.Uvarint |
| **Claimed result** | README benchstat: Uvarint/1 3.46 to 2.64 ns/op (-23.73%), Uvarint/4 8.04 to 3.54 ns/op (-55.97%), Uvarint/8_large 14.1 to 4.89 ns/op (-65.43%); UvarintSize/5 4.29 to 0.57 ns/op (-86.71%). |
| **Workload** | Decoding protobuf-style varints of 1 to 9 bytes, plus UvarintSize, per call in ns/op. |
| **Metric** | latency |
| **Adoption** | 20 stars |
| **Last commit** | 2026-05-01 |
| **Links** | [repository](https://github.com/dennwc/varint) · [benchmark](https://github.com/dennwc/varint) |

## Verdict

The README benchcmp table compares this package's Uvarint against binary.Uvarint for 1-9-byte values decoded repeatedly from 'exact' and 16-byte buffers. Per call it drops from 3.46 to 2.64 ns (1 byte) and from 14.1 to 4.89 ns (8 bytes, large buffer). UvarintSize runs in 0.43-1.00 ns versus 1.71-6.64 ns for a loop. Per the 2021-11-19 commit the numbers come from Go 1.17.3 with GOMAXPROCS 8; CPU model not stated.

## Use it when

- Go code that decodes many individual varints in a hand-written protobuf, LEB128 or log-format parser, where binary.Uvarint shows up in profiles.
- Buffers that usually have 10 or more bytes left past the varint (streams, large messages), which hit the bounds-check-free path; the README's _large rows show the biggest gains there.
- Size precomputation before encoding (UvarintSize), e.g. to size a buffer exactly before marshalling.
- Protobuf key parsing where you want field number and wire type validated in the same pass (ProtoTag).

## Skip it when

- Bulk integer arrays where you control the format: block codecs (Stream VByte, SIMD bit packing, FastPFor) decode orders of magnitude more integers per second than any per-value LEB128 decoder.
- C++ projects: this is Go only, and the catalog's C++/Rust siblings (varint-simd, MaskedVByte, Stream VByte) are the relevant options.
- When you also need a faster encoder or signed/zigzag varints; the package only decodes unsigned values and computes sizes.
- If you need speedup figures for a current Go toolchain: the README table was produced with Go 1.17.3 (2021), CI still pins Go 1.17.x, and nobody has re-measured on newer compilers.

## How it is fast

The decode loop is fully unrolled into ten byte steps, each with an early return. When the input slice is at least 10 bytes long, one up-front length test lets the Go compiler drop the per-byte bounds checks. Shorter slices take a second unrolled path that checks the length at each step. UvarintSize replaces the shift-and-count loop with a small binary tree of comparisons against precomputed MaxValN constants.

## Compared with alternatives

Pick it over chmike/varint when you only need a drop-in faster binary.Uvarint with identical error semantics plus a protobuf tag helper; chmike/varint covers encoding as well and publishes a dated i5-11400 table. Pick streamvbyte-simdgo instead when you can change the wire format to a block codec and want throughput rather than per-value latency.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (standard library only in tests) |
| **Minimum toolchain** | Go 1.17 (go.mod; CI runs 1.17.x on ubuntu-20.04) |
| **Platforms** | any Go target; pure Go, no assembly; a 2021 commit fixed protobuf tag decoding on 32-bit architectures |
| **Thread safety** | Stateless pure functions; safe for concurrent use (not stated in docs, follows from the code). |
| **Drop-in for the baseline** | partial: Uvarint has the same signature and the same return values as binary.Uvarint, including -11 for reads past 10 bytes (tests compare both on short, overflow and long buffers), but there is no PutUvarint, Varint, ReadUvarint or io.ByteReader variant. |

## Gotchas

- Before commit 44109b0 (2021-11-16) an overflowing input made Uvarint scan the rest of the buffer and return -(11+j); it now stops at 10 bytes and returns -11, matching Go 1.17's fix for golang/go#41185. Pin a version from November 2021 or later.
- ProtoTag decodes at most 9 bytes and returns an int64 field number without checking protobuf's 2^29-1 limit. It rejects field 0 only in the 1-byte form, so an overlong encoding such as 0x81 0x00 returns num 0 with n 2. Callers still need a range check.
- The README calls this an encoding/decoding package, but the only encoder-side helper is UvarintSize.
- The benchmarks decode a single constant value in a loop, so branch prediction is perfect. The UvarintSize 'old' column has no stdlib counterpart (encoding/binary has no size function); the test file's loop version (uvarintSizeLoop) appears to be what it measured.

## Known shortcomings

- Go, not C++. No CPU or Go version given; the README table is likely from about 2019.
- README table is Go 1.17.3 (commit 68362ad, 2021-11-19); CPU not stated and never re-measured on newer Go (CI pins 1.17.x). Decoder source is correct (same return values as binary.Uvarint); pre-44109b0 overflow scanned the whole buffer, now stops at 10 bytes. No encoder and no signed varint despite the README. ProtoTag accepts overlong field 0 and skips the 2^29-1 field limit. The UvarintSize 'old' column is not the stdlib. Constant-input microbench.

## Caveats and trade-offs

README shows only a benchcmp diff (old = binary.Uvarint, new = this package); CPU model and Go version are not stated (the -8 suffix is GOMAXPROCS). The table likely dates from around 2019 (copyright year), so the standard library baseline may have improved in later Go releases. Per-integer microbenchmark, not bulk throughput. Plain protobuf varint decoder, a marginal fit for the bitpacking category.

Same LEB128/protobuf wire format as the standard library, so it is a drop-in decoder; scalar code, no bulk or SIMD path. Go only.

## Maintenance

Small (about 200 lines of decode logic), MIT-licensed and easy to vendor; untouched from 2021 until a 2026-05-01 commit that only adds tests, so treat it as finished rather than actively developed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README benchcmp table compares the library against binary.Uvarint, and the benchmark code is public (BenchmarkUvarint and BenchmarkUvarintStdlib in varint_test.go), but the CPU model and Go version are not stated, so first-party C.
- **Verifier notes:** All quoted numbers match the README. Metadata confirmed: MIT, 20 stars, last commit 2026-05-01 (a test-coverage commit; the previous one was 2021-11-19), active.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/dennwc/varint>
  - <https://github.com/dennwc/varint/commits>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/README.md>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/varint_test.go>
- **Sources the enricher read:**
  - <https://github.com/dennwc/varint>
  - <https://github.com/dennwc/varint/commits>
  - <https://github.com/dennwc/varint/issues?q=is%3Aissue>
  - <https://github.com/dennwc/varint/tree/master/.github/workflows>
  - <https://github.com/dennwc/varint/commit/68362ad>
  - <https://github.com/dennwc/varint/commit/44109b0>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/README.md>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/go.mod>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/varint.go>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/varint_test.go>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/proto.go>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/proto_test.go>
  - <https://raw.githubusercontent.com/dennwc/varint/HEAD/.github/workflows/ci.yml>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/dennwc/varint`) · [data/wave9/enrich/raw/github_com_dennwc_varint.json](../../../data/wave9/enrich/raw/github_com_dennwc_varint.json) (enrichment confidence 0.75)

</details>
