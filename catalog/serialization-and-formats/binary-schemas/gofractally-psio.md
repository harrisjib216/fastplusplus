# psio / pSSZ (successor to fracpack)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> C++23 reflection-driven, SSZ-derived binary format with zero-copy views; author benchmarks show faster encode/decode than libprotobuf, capnp, FlatBuffers, msgpack.

| | |
|---|---|
| **Beats** | Protobuf, Cap'n Proto, FlatBuffers, MessagePack |
| **Claimed result** | Geomean latency ratios vs pssz (format time / pssz time, psio_bench_vs_externals snapshot, &gt;1 means pssz faster). Decode: protobuf 6.36x, capnp 5.38x, msgpack 18.67x, flatbuf 1.23x. Encode: protobuf 43.40x, capnp 81.96x, flatbuf 57.28x, msgpack 33.38x. View: capnp 47.57x, flatbuf 2.29x. Validate: protobuf 48.01x, flatbuf 8.45x, capnp 6.12x, msgpack 28.76x, but the validate column uses psio's own in-tree implementations of those formats, not the canonical libraries. Size: avro 0.56x, msgpack 0.61x, protobuf 0.65x of pssz, so the varint formats are smaller on the wire. Cumulative geomean: protobuf 12.64x, capnp 10.55x, msgpack 10.23x, flatbuf 5.13x. |
| **Workload** | Per-shape geomean of size, encode, decode, validate and view_one latency across reflected struct shapes (Point, NameRecord, FlatRecord, Record, Validator, Order, ValidatorList and bounded variants, plus realistic shapes). Size, encode, decode and view use the canonical libprotobuf, libcapnp, libflatbuffers and msgpack-cxx. Validate always uses psio's own implementations of those formats because the canonical libraries have no comparable validate entry point. |
| **Metric** | throughput |
| **Hardware** | Apple M-series (exact CPU model not specified) |
| **Compiler and flags** | llvm-clang 22.1, -O3 -DNDEBUG |
| **Adoption** | 0 stars; project is a 0.1.0 development/pre-release checkout |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/gofractally/psio) · [benchmark](https://github.com/gofractally/psio/blob/main/docs/format-comparison.md) |

## Verdict

On the author's own psio_bench_vs_externals harness (unspecified Apple M-series, llvm-clang 22.1, -O3 -DNDEBUG, library versions not stated), per-shape geomeans show libprotobuf 6.4x slower than pSSZ to decode and 43x slower to encode, FlatBuffers 1.23x slower to decode and 2.3x slower on a single-field view, and Cap'n Proto 5.4x slower to decode and 48x slower on a view. The comparison is weaker than it looks: the external encode cells include copying a native C++ struct into the library's builder or message, FlatBuffers and capnp 'decode' means materializing a native struct, the validate ratios are against psio's own re-implementations of those formats, and the anchor CSV is not committed.

## Use it when

- C++23 services that exchange existing structs between processes you control, and want to serialize them with no separate IDL or codegen step.
- Read-heavy paths that pull one field out of a validated buffer. The spec's view_one table shows 0.33-0.56 ns for pSSZ, against 0.58-3.46 ns for FlatBuffers and 17-28 ns for Cap'n Proto on the same shapes.
- Content-addressed or signed payloads that need exactly one canonical byte sequence per value (spec §15).
- Bulk arrays of fixed-layout records such as validator or tick lists. Marking the record DWNC and trivially copyable turns encode and decode into a memcpy.
- Small bounded messages, where length_bound annotations shrink offset slots and headers to 1 or 2 bytes.

## Skip it when

- Integer-heavy or sparse payloads where wire size matters most. In the author's table Avro, MessagePack and Protobuf are 0.56-0.65x pSSZ's raw size. The gap narrows to 0.87-0.91x after zstd-1.
- Streaming or incremental parsing. Offsets are container-relative, so the whole container must be in memory before any field can be read.
- Polyglot systems. pSSZ exists only in C++ and Rust: JS/TS has no pSSZ, and no Python, Go or Java port exists. psio's own Protobuf, MessagePack, capnp and FlatBuffers codecs are covered by only two shared fixture records each.
- Production code or code that parses untrusted input today. The library is at 0.1.0 with no tags or releases and no LICENSE file, and it has been verified only on macOS ARM64. Its own release checklist asks for sanitizer and fuzz jobs 'before accepting untrusted inputs'.
- Builds with -fno-exceptions or for WASI guests. The docs say the exception-free profile is incomplete: headers still contain unguarded throws.

## How it is fast

Each record is a fixed region (scalars inline, one offset slot per variable field) followed by a dynamic region, so a field's position is a compile-time constant that a view reads with one load, and a variable field's size comes from the next offset instead of a length prefix. The offset width (1, 2 or 4 bytes) is chosen per type at compile time from length_bound and maxDynamicData annotations. Records marked definitionWillNotChange() (DWNC) drop the extensibility header, and a trivially copyable, unpadded DWNC record (or a vector of them) encodes and decodes as one memcpy. Validation is one bounds check per offset slot, with nesting depth capped at 64.

## Compared with alternatives

Pick pSSZ when both ends run C++ (or Rust) and you want one reflected struct declaration to give zero-copy single-field reads, canonical bytes and append-only schema evolution together, and you can accept a pre-release, unlicensed codebase. Pick hpp-proto if you must stay on the Protobuf wire, and rkyv for a Rust-only zero-copy codebase.

## Integration

| | |
|---|---|
| **Form** | header-only in practice. The psio::psio CMake target compiles a single placeholder stub.cpp. Consume it via add_subdirectory, FetchContent, or find_package(psio 0.1 CONFIG). |
| **Dependencies** | Boost headers (required, for Boost.Preprocessor in the reflection macros) and xxhash (vendored). simdjson is optional and only enables JSON-to-pjson. Benchmarks can optionally use libprotobuf, capnp, flatbuffers, msgpack-cxx, lz4 and zstd. |
| **Minimum toolchain** | C++23 and CMake 3.20+. On macOS the README says to use Homebrew LLVM rather than Apple Clang. Benchmarks used llvm-clang 22.1. GCC and MSVC support is not documented. The Rust crate uses edition 2021, and packaging was checked with Cargo 1.94.1. |
| **Platforms** | Verified only on macOS ARM64; Linux/x86-64 runs are an open release gate. pssz.hpp and pssz_view.hpp memcpy scalars and offsets in host byte order with no byte-swap path, so hosts are effectively limited to little-endian (inferred from source, not stated in the docs). |
| **Thread safety** | not documented. From the source, encode, decode and validate are stateless free functions (tag_invoke CPOs) over caller-owned buffers, and pssz.hpp has no mutable globals. |
| **Drop-in for the baseline** | no |

## Gotchas

- Only validate reports errors. error.hpp says decode and view accessors assume the input has already been validated, so call psio::validate&lt;T&gt;(psio::pssz{}, bytes) on every untrusted buffer first. The 64-level depth cap applies to validate, not to decode.
- The offset width W is derived from the type and never stored on the wire. Changing a length_bound in a way that flips W, or adding definitionWillNotChange() to an existing record, silently breaks bytes that are already stored. Encoding more than maxDynamicData throws codec_exception.
- Unknown trailing fields are silently dropped, strings are not checked for UTF-8 unless you use validate_strict (which also fully decodes), and appending a variant-typed field is not a safe evolution.
- The spec promises single-pass encode, but the C++ encode entry point first runs size_of over the value and then writes into the pre-sized buffer with unchecked memcpy (fast_buf_stream).

## Known shortcomings

- The validate ratios are against psio's own reimplementations of protobuf, flatbuffers and capnp, not the canonical libraries. The C++ core has no LICENSE file (only the Rust and npm manifests declare MIT). Published ratios are latency, measured on an unspecified Apple M-series chip.
- The competitor encode timings include copying a native struct into each library's builder, FlatBuffers/capnp 'decode' builds a full native struct, and the capnp view timing constructs a new reader per call, likely inflating the 43-82x and 47.57x ratios. Decode and view are unchecked (only validate reports errors). Verified only on macOS ARM64; host byte order only; requires C++23, Boost and Homebrew LLVM on macOS.

## Caveats and trade-offs

First-party benchmark. Hardware is given only as 'Apple M-series', and versions of the canonical libraries are not stated. The anchor snapshot CSV (/tmp/psio_bench_snap_xx/perf_20260501T081915Z_4b7ae98.csv) is not committed, although commit 4b7ae98 exists. Validate ratios compare pssz against psio's re-implementations of protobuf, flatbuf and capnp, not the canonical libraries. The prose and table disagree slightly: flatbuf validate is 8.64x in the prose and 8.45x in the table, and ssz cumulative is 1.13 in the prose and 1.10 in the table. The repo has no LICENSE file: the Rust crate and npm package manifests declare MIT, the C++ core has no license, and docs/compatibility.md lists supplying license files as pending. 0 stars; version 0.1.0 is pre-release. fracpack is deprecated in favour of pssz in this repo.

No OSI license file in the repo; benchmark uses psio's own in-repo harness (first-party, not an independent third party) though it links against the real canonical libraries rather than reimplementations; fixed-width offset table design trades wire size for zero-copy random access and O(1) field lookup

## Maintenance

Actively worked on (last push 2026-09-16) but pre-release, so treat it as a reference design rather than a dependency: version 0.1.0, 0 stars, no tags or releases, verified only on macOS ARM64, and no LICENSE file (the Rust and npm manifests declare MIT, while the C++ core declares no license).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** First-party harness (cpp/benchmarks/bench_psio_vs_externals.cpp, adapters under cpp/benchmarks/adapters/) states llvm-clang 22.1 and -O3 -DNDEBUG, but hardware is only 'Apple M-series' with no CPU model, canonical-library versions are not given, and the anchor CSV sits under /tmp and is not committed. There is no independent suite or paper, so this is C, not B.
- **Verifier notes:** The numbers match docs/format-comparison.md exactly, and the benchmark source is public. The only reasons this is not tier A are the missing CPU model and first-party provenance. The record's metric 'throughput' is really latency ratios (ns per op) plus size, and metric is not a correctable field. license stays null because GitHub reports none and there is no LICENSE file, even though the manifests declare MIT.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/gofractally/psio>
  - <https://github.com/gofractally/psio/blob/main/docs/format-comparison.md>
  - <https://github.com/gofractally/psio/blob/main/README.md>
  - <https://github.com/gofractally/psio/blob/main/cpp/benchmarks/CMakeLists.txt>
  - <https://github.com/gofractally/psio/blob/main/cpp/benchmarks/bench_psio_vs_externals.cpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/benchmarks/harness.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/benchmarks/adapters/protobuf_adapter.hpp>
  - <https://github.com/gofractally/psio/blob/main/docs/compatibility.md>
  - <https://github.com/gofractally/psio/blob/main/docs/release-work.md>
  - <https://github.com/gofractally/psio/blob/main/docs/psio-overview.md>
  - <https://github.com/gofractally/psio/blob/main/CMakeLists.txt>
  - <https://github.com/gofractally/psio/blob/main/rust/Cargo.toml>
  - <https://github.com/gofractally/psio/blob/main/rust/psio/Cargo.toml>
  - <https://github.com/gofractally/psio/blob/main/js/package.json>
  - <https://github.com/gofractally/psio/blob/main/cpp/include/psio/pssz.hpp>
  - <https://github.com/gofractally/psio/commit/4b7ae98>
- **Sources the enricher read:**
  - <https://github.com/gofractally/psio>
  - <https://github.com/gofractally/psio/blob/main/README.md>
  - <https://github.com/gofractally/psio/blob/main/docs/format-comparison.md>
  - <https://github.com/gofractally/psio/blob/main/docs/pssz-spec.md>
  - <https://github.com/gofractally/psio/blob/main/docs/psio-overview.md>
  - <https://github.com/gofractally/psio/blob/main/docs/compatibility.md>
  - <https://github.com/gofractally/psio/blob/main/docs/release-work.md>
  - <https://github.com/gofractally/psio/blob/main/CMakeLists.txt>
  - <https://github.com/gofractally/psio/blob/main/cpp/CMakeLists.txt>
  - <https://github.com/gofractally/psio/blob/main/cpp/include/psio/pssz.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/include/psio/pssz_view.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/include/psio/view.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/include/psio/stream.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/include/psio/error.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/include/psio/reflect.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/include/psio/cpo.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/include/psio/detail/unaligned_iter.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/benchmarks/CMakeLists.txt>
  - <https://github.com/gofractally/psio/blob/main/cpp/benchmarks/bench_psio_vs_externals.cpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/benchmarks/harness.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/benchmarks/gen_report.py>
  - <https://github.com/gofractally/psio/blob/main/cpp/benchmarks/shapes.hpp>
  - <https://github.com/gofractally/psio/blob/main/cpp/benchmarks/adapters/protobuf_adapter.hpp>
  - <https://github.com/gofractally/psio/blob/main/examples/consumer/main.cpp>
  - <https://github.com/gofractally/psio/blob/main/rust/psio/Cargo.toml>
  - <https://github.com/gofractally/psio/commits/main>
  - <https://github.com/gofractally/psio/commit/4b7ae98>
  - <https://github.com/gofractally/psio/issues>
  - <https://github.com/gofractally/psio/tags>
  - <https://github.com/gofractally/psio/releases>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/gofractally/psio`) · [data/wave4/enrich/raw/github_com_gofractally_psio.json](../../../data/wave4/enrich/raw/github_com_gofractally_psio.json) (enrichment confidence 0.55)

</details>
