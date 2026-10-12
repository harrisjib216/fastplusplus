# serde-zap

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Serde-trait binary serializer for Rust; serializes string-heavy logs \~5.4x faster than prost, \~9.7x faster than rmp-serde.

| | |
|---|---|
| **Beats** | Protobuf (prost 0.14.4; Google's protobuf 4.36.1-release crate also on the page), FlatBuffers (flatbuffers 25.12.19), Cap'n Proto (capnp 0.27.0), MessagePack (rmp-serde 1.3.1); all are the Rust crates for those formats, not the C++ libraries |
| **Claimed result** | serialize 135.54 µs vs prost(protobuf) 731.23 µs (\~5.4x), flatbuffers 763.63 µs (\~5.6x), capnp 480.15 µs (\~3.5x), rmp-serde(msgpack) 1.3179 ms (\~9.7x); deserialize 1.7212 ms vs prost 2.6802 ms (\~1.6x) (derived from page data) |
| **Workload** | Serialize/deserialize of the 'log' dataset (small HTTP-request-log-like structs with many strings) in djkoloski/rust_serialization_benchmark. |
| **Metric** | latency |
| **Hardware** | AMD EPYC 9V74 80-Core Processor, 2 cores / 4 threads visible (Microsoft-hypervisor VM, GitHub-hosted ubuntu-latest runner per .github/workflows/bench.yml), x86_64 |
| **Compiler and flags** | rustc 1.100.0-nightly (a36d05efa 2026-09-09), LLVM 23.1.1; run as `cargo bench` by tools/bencher/src/main.rs with RUSTFLAGS="-C target-cpu=native", and Cargo.toml [profile.bench] sets lto = true (otherwise release-profile defaults, opt-level 3); criterion with default settings |
| **Adoption** | 3 stars; 515 crates.io downloads (first published 2026-07-31) |
| **Last commit** | 2026-08-02 |
| **Links** | [repository](https://github.com/xangelix/serde-zap) · [benchmark](https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md) |

## Verdict

On the rust_serialization_benchmark page run of 2026-09-10, the 'log' dataset holds small, string-heavy HTTP request logs. serde-zap 0.1.1 serialized it into a preallocated buffer in 135.54 µs, against 731.23 µs for prost's encode-only step (\~5.4x), 763.63 µs for FlatBuffers, 480.15 µs for Cap'n Proto and 1.3179 ms for rmp-serde. Owned deserialization took 1.7212 ms, against 2.6802 ms for prost decode-only (\~1.6x). All entries are Rust crates, built with rustc 1.100.0-nightly (LLVM 23.1.1), lto = true and -C target-cpu=native. They were measured with criterion defaults on a 2-core/4-thread AMD EPYC 9V74 GitHub runner VM. The serde-zap author contributed the harness module (PR #151), and a suite maintainer reviewed it.

## Use it when

- Rust-to-Rust messages, caches or IPC where the types already derive serde and you want faster serialization without new derive traits. On 'log' it serializes in 135.54 µs, against 366.95 µs for postcard on the same page.
- Serialize-heavy streams of small, string-heavy records (logs, events, game state) written into a reused buffer with to_slice. This is the path the benchmark measures.
- no_std or embedded targets: to_slice and from_bytes need no allocator (--no-default-features).
- Readers that keep the input buffer alive and can borrow &str/&[u8] fields zero-copy (log borrow: 446.09 µs, against 577.43 µs for postcard).
- Large Vec&lt;f32&gt; or other plain-old-data vectors where you can opt into pod_vec's single bulk memcpy. The benchmark harness does not exercise this path.

## Skip it when

- Cross-language interop, gRPC or schema evolution. Adding, removing or reordering fields breaks existing data, and there is no IDL. Stay with Protobuf, FlatBuffers or Cap'n Proto.
- Persistent storage. The README says the wire format is not stable before 1.0, and the crate is at 0.1.1 with 3 stars, 515 downloads and no dependents on crates.io.
- Random or partial access without decoding. On the same page, FlatBuffers, Cap'n Proto and rkyv access fields in nanoseconds, while serde-zap must decode the whole message.
- Workloads bound by deserialization or by float arrays, if you can leave serde's traits. On 'log', bitcode deserializes in 1.1452 ms and wincode in 1.4166 ms, against serde-zap's 1.7212 ms. On 'mesh', FlatBuffers (371.26 µs), wincode (147.88 µs) and rkyv (141.74 µs) all serialize faster than serde-zap (412.92 µs).
- Streaming protocols: from_reader reads to EOF before it decodes, and there is no incremental decoder and no built-in framing.

## How it is fast

Integers use bincode's tagged-prefix varint: values up to 250 take one byte, and larger values take a tag byte (251-254) and then a fixed-width little-endian integer. Decoding is one branch and one unaligned load, with no per-byte LEB128 loop. The reader and the writer are both raw-pointer cursors. Each read is one bounds check against an end pointer, and the Writer trait's reserve/commit puts varints and strings of up to 250 bytes straight into the output with one capacity check and one memcpy. Structs are bare field concatenations with no tags, names or offset tables, &str/&[u8] decode zero-copy from the input, and the error type is a 1-byte fieldless enum, so Result stays small on the #[inline(always)] hot paths.

## Compared with alternatives

postcard also goes through serde's traits. Pick serde-zap over postcard when serialization time dominates (log 135.54 vs 366.95 µs, mk48 612.11 µs vs 1.5531 ms) and you can accept a younger format with no stability promise; deserialization is about a tie (1.7212 vs 1.7399 ms). bitcode is faster in every timing column on the same page and wincode in most, but both need their own derive traits, so pick serde-zap mainly to keep plain serde derives.

## Integration

| | |
|---|---|
| **Form** | crate (serde-zap on crates.io; #![no_std] with the features alloc and std, both on by default) |
| **Dependencies** | serde 1 (default-features = false) only; zstd is a dev-dependency |
| **Minimum toolchain** | Not declared (Cargo.toml has no rust-version). Edition 2024 needs Rust 1.85+. The source uses let-chains (stream.rs) and usize::is_multiple_of (pod_vec.rs), which by our reading need Rust 1.88+. CI builds only on a pinned nightly (nightly-2026-07-15), so stable builds are not tested. |
| **Platforms** | Any target that serde supports: pure Rust with no SIMD or arch-specific code, and no_std-capable. pod_vec's bulk-copy path runs only on little-endian hosts. The benchmark covers only x86_64 Linux, and CI (tests, Miri, 90 s libFuzzer runs) runs on Linux. |
| **Thread safety** | Not documented. The API is free functions that keep state per call and use no globals, so concurrent calls on separate buffers do not interact. |
| **Drop-in for the baseline** | no |

## Gotchas

- Because the format does not describe itself, some serde features fail at runtime. deserialize_any, deserialize_identifier and deserialize_ignored_any return Error::NotSupported, which breaks untagged and internally tagged enums. #[serde(flatten)] serializes through a map of unknown length, which returns Error::SeqLengthUnknown. #[serde(skip_serializing_if)] writes data that the same type cannot read back.
- Errors are a fieldless enum. Custom serde messages collapse to Error::Custom, and there is no byte offset, so malformed input is hard to diagnose. from_bytes ignores trailing bytes; use take_from_bytes to get the remainder.
- pod_vec needs you to write `unsafe impl Pod` correctly (repr(C), no padding, every bit pattern valid). Its data cannot be read by the stock Vec path. By our reading of the source, the bytes also depend on host endianness: little-endian hosts write a byte-length prefix plus raw memory, while big-endian hosts write an element-count prefix plus per-element encoding. So do not move pod_vec data between LE and BE machines, even though a code comment says the bytes are identical.
- The benchmark times to_slice into a preallocated 10 MB buffer. to_vec also pays for Vec growth plus a final shrink_to_fit reallocation, and the page does not time that. full_vec caps its preallocated element count at the remaining input bytes, but the allocation can still be size_of::&lt;T&gt;() times the input size.

## Known shortcomings

- Low notability (3 stars, about 500 crates.io downloads, first published 2026-07-31). Wire format not stable before 1.0; not self-describing and no schema evolution.
- bitcode beats it in every timing column and wincode in most; its niche is the fastest serializer through plain serde traits, and postcard ties it on mesh. pod_vec may not be portable between little- and big-endian hosts (source reading). No declared MSRV (needs about Rust 1.88); CI builds only on a pinned nightly. Untagged/internally tagged enums, flatten and skip_serializing_if break round-trips.

## Caveats and trade-offs

Very new and barely used: 3 stars, 515 downloads, first release 2026-07-31. Its README says the wire format is not yet stable before 1.0. Numbers come from one dataset ('log') of a four-dataset suite (README last updated 2026-09-10). On 'mesh', flatbuffers serializes faster (371.26 us vs 412.92 us). capnp and flatbuffers are zero-copy formats with no owned deserialize on the page. The prost figures are encode-only and decode-only, which favors prost. The serde-zap README's own tables come from an older run (2026-08-02, EPYC 7763) and differ from the current page. The format is non-self-describing and has no schema evolution. The run is on a shared 2-core CI VM built with target-cpu=native.

Very small/new project (3 stars) with a serde-based zero-copy-ish design; limited real-world adoption and API stability track record.

## Maintenance

A young crate from one author: first release 2026-07-31, last commit and 0.1.1 release 2026-08-02, and no issues, PRs or dependents on crates.io yet. It is dual MIT/Apache-2.0, depends only on serde and has ten small source files, so it is easy to pin or vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party suite djkoloski/rust_serialization_benchmark with public code (benches/bench.rs bench_log, src/bench_serde_zap.rs, src/bench_prost.rs). The README states the compiler (rustc 1.100.0-nightly a36d05efa, LLVM 23.1.1) and the CPU (AMD EPYC 9V74). Flags are in tools/bencher/src/main.rs (RUSTFLAGS -C target-cpu=native) and Cargo.toml [profile.bench] lto = true, so A holds.
- **Verifier notes:** All quoted numbers match the serde-zap 0.1.1 row (135.54 us / 1.7212 ms) and the baseline rows in the 'log' raw table. The derived ratios (5.4x, 5.6x, 3.5x, 9.7x; 1.6x) are correct. License fixed to dual MIT OR Apache-2.0 (Cargo.toml, README, and LICENSE-MIT plus LICENSE-APACHE); GitHub detects only the Apache LICENSE file. Keep, tagged low-notability: the evidence is tier A from an independent suite.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `license`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/rust-toolchain.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/.github/workflows/bench.yml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/tools/bencher/src/main.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/benches/bench.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_prost.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_serde_zap.rs>
  - <https://github.com/xangelix/serde-zap>
  - <https://github.com/xangelix/serde-zap/blob/main/README.md>
  - <https://github.com/xangelix/serde-zap/blob/main/Cargo.toml>
  - <https://github.com/xangelix/serde-zap/blob/main/LICENSE>
  - <https://crates.io/api/v1/crates/serde-zap>
- **Sources the enricher read:**
  - <https://github.com/xangelix/serde-zap>
  - <https://github.com/xangelix/serde-zap/blob/main/README.md>
  - <https://github.com/xangelix/serde-zap/blob/main/Cargo.toml>
  - <https://github.com/xangelix/serde-zap/blob/main/rust-toolchain.toml>
  - <https://github.com/xangelix/serde-zap/blob/main/CHANGELOG.md>
  - <https://github.com/xangelix/serde-zap/blob/main/src/lib.rs>
  - <https://github.com/xangelix/serde-zap/blob/main/src/varint.rs>
  - <https://github.com/xangelix/serde-zap/blob/main/src/read.rs>
  - <https://github.com/xangelix/serde-zap/blob/main/src/write.rs>
  - <https://github.com/xangelix/serde-zap/blob/main/src/error.rs>
  - <https://github.com/xangelix/serde-zap/blob/main/src/ser.rs>
  - <https://github.com/xangelix/serde-zap/blob/main/src/de.rs>
  - <https://github.com/xangelix/serde-zap/blob/main/src/stream.rs>
  - <https://github.com/xangelix/serde-zap/blob/main/src/pod_vec.rs>
  - <https://github.com/xangelix/serde-zap/blob/main/src/full_vec.rs>
  - <https://github.com/xangelix/serde-zap/blob/main/.github/workflows/ci.yml>
  - <https://github.com/xangelix/serde-zap/blob/main/ci/rust_serialization_benchmark.patch>
  - <https://github.com/xangelix/serde-zap/blob/main/fuzz/fuzz_targets/from_bytes.rs>
  - <https://github.com/xangelix/serde-zap/issues?q=is%3Aissue>
  - <https://github.com/xangelix/serde-zap/pulls?q=is%3Apr>
  - <https://crates.io/api/v1/crates/serde-zap>
  - <https://crates.io/api/v1/crates/serde-zap/reverse_dependencies>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_serde_zap.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_prost.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/benches/bench.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/CONTRIBUTING.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark/pull/151>
  - <https://github.com/djkoloski/rust_serialization_benchmark/commits/master/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/xangelix/serde-zap`) · [data/wave4/enrich/raw/github_com_xangelix_serde_zap.json](../../../data/wave4/enrich/raw/github_com_xangelix_serde_zap.json) (enrichment confidence 0.8)

</details>
