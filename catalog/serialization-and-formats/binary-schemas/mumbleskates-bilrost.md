# bilrost

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust derive-based, protobuf-like binary encoding (a rewritten prost fork) that encodes and decodes faster than prost.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | log dataset: bilrost 0.1016.1 serialize 396.57 us (encode) / 300.26 us (prepend) vs prost 0.14.4 731.23 us (encode only) / 1.8883 ms (populate + encode): \~2.4x faster vs encode-only, \~6.3x vs populate+encode (derived from page data). Deserialize bilrost 2.1234 ms vs prost 2.6802 ms (decode) / 2.7061 ms (decode + convert): \~1.26x faster (derived from page data). |
| **Workload** | Criterion micro-benchmark, 'log' dataset (HTTP request logs, many strings), serialize and deserialize a Rust struct via the rust_serialization_benchmark shootout. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9V74 80-Core Processor, 4 vCPUs, x86_64-unknown-linux-gnu |
| **Compiler and flags** | rustc 1.100.0-nightly (a36d05efa 2026-09-09), LLVM 23.1.1; Criterion via cargo bench, [profile.bench] lto = true |
| **Adoption** | 47 stars |
| **Last commit** | 2026-08-14 |
| **Links** | [repository](https://github.com/mumbleskates/bilrost) · [benchmark](https://github.com/djkoloski/rust_serialization_benchmark) |

## Verdict

In rust_serialization_benchmark (run 2026-09-10; rustc 1.100.0-nightly with LLVM 23.1.1, fat LTO; AMD EPYC 9V74, 4 vCPUs), bilrost 0.1016.1 encoded the log dataset in 300 µs (prepend) and 397 µs (forward encode). prost 0.14.4's encode-only time was 731 µs, so bilrost was 2.4x and 1.8x faster. It decoded in 2.12 ms vs 2.68 ms (1.26x). prost's 1.89 ms populate+encode figure includes converting into prost-generated types, which bilrost avoids because it derives directly on the native structs; bilrost also leads prost on mesh, minecraft_savedata and mk48 (serialize 1.2-2.4x, deserialize 1.05-1.76x) with 8-18% smaller output.

## Use it when

- Rust-only systems where you own both ends and want protobuf-style schema evolution (numbered fields, unknown fields skipped) without .proto files or generated types.
- Deeply nested or many-field messages, where backward `prepend` encoding helps most: 2.4x faster than prost encode on log and mk48 in the shootout.
- String-heavy payloads you can decode by borrowing: on log, bilrost's borrowed decode is 721 µs vs 2.12 ms owned (\~2.9x). prost has no borrowed decoding in that table.
- You need canonical bytes for hashing, signing or dedup: `#[bilrost(distinguished)]` reports or rejects non-canonical input.
- no_std targets with an allocator (turn off the `std` feature; `hashbrown` feature for maps).

## Skip it when

- Anything that must talk protobuf (gRPC, other languages, existing .proto schemas). The wire format is incompatible, there is no schema DSL, only a Rust implementation exists, and there is no RPC support.
- Throughput matters most and schema evolution does not: on the same log table bitcode (97 µs), savefile (155 µs) and nanoserde (191 µs) serialize 1.6-3.1x faster than bilrost's 300 µs prepend. postcard also decodes faster (1.74 vs 2.12 ms) and its output is smaller (725 KB vs 805 KB).
- You need random access without decoding (zero-copy archives). Bilrost always decodes into structs; see rkyv.
- You want JSON or text output from the same derive. It is not provided; the README says to use a separate tool such as serde.
- Bus-factor concerns: one maintainer with no external backing (issue #5), 47 stars, pre-1.0 versioning with occasional API breaks (0.1016.0 raised the MSRV and removed hidden methods).

## How it is fast

Nested length-prefixed data is written back to front into a rope-like `ReverseBuffer`, so each sub-message's length is known once its bytes exist. That gives single-pass encoding with no repeated length measurement (the README says prost re-measures nested messages). Varints are a 9-byte-max bijective LEB128 variant. Encoding has a 1-byte fast path, then a hard-coded binary search on length feeding a const-generic unrolled writer; decoding uses a fully unrolled slice decoder split into 32-bit pieces. Borrowed decoding skips string allocation, which the README calls often more than half of decode cost, and field order is enforced by tag deltas, so no duplicate or merge handling is needed.

## Compared with alternatives

bitcode, savefile, nanoserde and postcard all beat bilrost on the same log table, so pick bilrost over them when you need tag-numbered, protobuf-style forward/backward compatibility or canonical decoding rather than peak speed. Choose minicbor (similar log serialize speed, slower mesh decode 9.43 vs 5.83 ms) only if you need a standard CBOR wire format.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bytes (required); default features add bilrost-derive (syn 2/3, quote, proc-macro2, eyre, itertools) and thin-vec (detailed-errors); build-dep autocfg; optional arrayvec, bstr, bytestring, chrono, hashbrown, jiff, smallvec, smol_str, time, tinyvec for type support |
| **Minimum toolchain** | Rust 1.68 (edition 2021; CI tests 1.68 and stable); `default-field-values` feature needs syn 3 and an unstable syntax |
| **Platforms** | Pure Rust, no_std + alloc capable. The self-copy prepend optimization turns on automatically only on x86_64. CI runs Ubuntu only; macOS and Windows jobs are commented out. |
| **Thread safety** | Not documented. No global state was seen; messages are your own structs, and ReverseBuffer is a plain owned Vec of boxed chunks, so both are Send/Sync when their contents are. |
| **Drop-in for the baseline** | partial: the API mirrors prost (derive Message, encode/decode into bytes::Buf/BufMut), but the wire format differs from protobuf and there is no .proto codegen, so it only replaces prost where you control every reader and writer |

## Gotchas

- Forward `encode` and backward `prepend`/`encode_fast` perform differently by workload: prepend is 1.9x faster than encode on mk48 but slightly slower on mesh. `encode_fast` returns a possibly non-contiguous ReverseBuffer; use `encode_contiguous`/`into_vec` when you need one slice.
- Collections in messages default to `unpacked` (one field per element); long numeric arrays should use `packed`. Packed and unpacked are not interchangeable on the wire, and oneof variants require packed.
- Distinguished decoding is opt-in and unsupported for floats and HashMap/HashSet (hash collections are not canonical). `u8`/`i8` and `Vec<u8>` byte strings need explicit `varint`/`plainbytes` encodings per the type table.
- Decoding has a fixed recursion limit of 100 nesting levels (the `no-recursion-limit` feature removes it). The crate uses some `unsafe` in its buffers; the `forbid-unsafe` feature swaps in safe code at some cost in speed.

## Known shortcomings

- The 6.3x serialize figure is against prost's populate+encode time; against encode-only it is about 2.4x. bilrost's author is a maintainer of the benchmark suite.
- A fork of prost (per its README, not marked on GitHub). The harness derives bilrost on the benchmark's own structs while prost converts into generated types; fair encode-only margin is 1.8-2.4x, and across datasets 1.2-2.4x serialize and 1.05-1.76x deserialize. bitcode, savefile, nanoserde, wincode and serde-zap serialize faster on log; its case is schema evolution and canonical decoding, not peak speed. One maintainer, pre-1.0, Ubuntu-only CI.

## Caveats and trade-offs

Speedup varies by dataset and by which prost variant is compared: the 6.3x serialize figure is vs prost populate+encode (conversion from the native struct included); vs prost encode-only it is \~2.4x. On 'mesh' bilrost is still ahead (encode 4.2651 ms vs prost encode 5.8939 ms; deserialize 5.8287 ms vs 10.253 ms), so the earlier note that it is not clearly ahead there was wrong. bilrost's author (mumbleskates) is listed as a maintainer of the benchmark suite. Harvested from a shootout, not bilrost's own README.

Wire format is bilrost-specific, not protobuf-compatible; no zero-copy access mode; smaller ecosystem/tooling than protobuf.

## Maintenance

Actively maintained by one author: last default-branch release commit 2026-08-14, 0.1016.1 published to crates.io 2026-08-27, about 148k downloads. Apache-2.0 and easy to adopt. Versioning is pre-1.0, but the author states the wire format is final and that it runs in production at Restate and Graft.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Public third-party shootout (djkoloski/rust_serialization_benchmark: benches/bench.rs, src/bench_bilrost.rs vs src/bench_prost.rs) with prost in the same table; README states rustc 1.100.0-nightly (a36d05efa 2026-09-09), LLVM 23.1.1, CPU AMD EPYC 9V74, and Cargo.toml [profile.bench] lto=true (release-level opt). All code, compiler, flags and CPU are stated, so A holds.
- **Verifier notes:** Numbers match bilrost's and prost's rows on the log table (last updated 2026-09-10). Default-branch last commit is 2026-08-14 (repo pushed_at 2026-09-21 is likely another branch). License Apache-2.0, 47 stars, not fork/archived.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/djkoloski/rust_serialization_benchmark>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/tree/master/src>
  - <https://github.com/djkoloski/rust_serialization_benchmark/tree/master/benches>
  - <https://github.com/mumbleskates/bilrost>
- **Sources the enricher read:**
  - <https://github.com/mumbleskates/bilrost>
  - <https://github.com/mumbleskates/bilrost/blob/bilrost/README.md>
  - <https://github.com/mumbleskates/bilrost/blob/bilrost/Cargo.toml>
  - <https://github.com/mumbleskates/bilrost/blob/bilrost/bilrost-derive/Cargo.toml>
  - <https://github.com/mumbleskates/bilrost/blob/bilrost/CHANGELOG.md>
  - <https://github.com/mumbleskates/bilrost/blob/bilrost/src/buf.rs>
  - <https://github.com/mumbleskates/bilrost/blob/bilrost/src/lib.rs>
  - <https://github.com/mumbleskates/bilrost/blob/bilrost/src/encoding/mod.rs>
  - <https://github.com/mumbleskates/bilrost/blob/bilrost/src/encoding/varint.rs>
  - <https://github.com/mumbleskates/bilrost/blob/bilrost/.github/workflows/ci.yml>
  - <https://github.com/mumbleskates/bilrost/issues/5>
  - <https://github.com/mumbleskates/bilrost/issues>
  - <https://github.com/mumbleskates/bilrost/commits/bilrost>
  - <https://crates.io/api/v1/crates/bilrost>
  - <https://github.com/djkoloski/rust_serialization_benchmark>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_bilrost.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_prost.rs>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/mumbleskates/bilrost`) · [data/wave4/enrich/raw/github_com_mumbleskates_bilrost.json](../../../data/wave4/enrich/raw/github_com_mumbleskates_bilrost.json) (enrichment confidence 0.85)

</details>
