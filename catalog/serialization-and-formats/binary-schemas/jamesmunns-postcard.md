# postcard

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> no_std serde binary format for Rust; serializes \~2x faster than prost/flatbuffers, \~3.6x faster than rmp-serde on log records.

| | |
|---|---|
| **Beats** | Protobuf (prost 0.14.4; Google's protobuf 4.36.1-release crate also on the page), FlatBuffers (flatbuffers 25.12.19), Cap'n Proto (capnp 0.27.0), MessagePack (rmp-serde 1.3.1); all are the Rust crates for those formats, not the C++ libraries |
| **Claimed result** | serialize 366.95 µs vs prost(protobuf) 731.23 µs (\~2.0x), flatbuffers 763.63 µs (\~2.1x), capnp 480.15 µs (\~1.3x), rmp-serde(msgpack) 1.3179 ms (\~3.6x); deserialize 1.7399 ms vs prost 2.6802 ms (\~1.5x), rmp-serde 2.3829 ms (\~1.4x) (derived from page data) |
| **Workload** | Serialize/deserialize of the 'log' dataset (small HTTP-request-log-like structs with many strings) in djkoloski/rust_serialization_benchmark. |
| **Metric** | latency |
| **Hardware** | AMD EPYC 9V74 80-Core Processor, 2 cores / 4 threads visible (Microsoft-hypervisor VM, GitHub-hosted ubuntu-latest runner per .github/workflows/bench.yml), x86_64 |
| **Compiler and flags** | rustc 1.100.0-nightly (a36d05efa 2026-09-09), LLVM 23.1.1; run as `cargo bench` by tools/bencher/src/main.rs with RUSTFLAGS="-C target-cpu=native", and Cargo.toml [profile.bench] sets lto = true (otherwise release-profile defaults, opt-level 3); criterion with default settings |
| **Adoption** | 1.53k stars (1,532); \~66.1M crates.io downloads (\~25.3M recent) |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/jamesmunns/postcard) · [benchmark](https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md) |

## Verdict

In djkoloski/rust_serialization_benchmark (run 2026-09-10; rustc 1.100.0-nightly, LTO, target-cpu=native, criterion; 2-vCPU AMD EPYC 9V74 GitHub runner VM), postcard 1.1.3 serialized the 'log' dataset into a preallocated slice in 366.95 us. The Rust-crate baselines took 731.23 us for prost encode (\~2.0x), 763.63 us for flatbuffers (\~2.1x), 480.15 us for capnp (\~1.3x) and 1.3179 ms for rmp-serde (\~3.6x). Owned deserialize took 1.7399 ms, against 2.6802 ms for prost decode (\~1.5x) and 2.3829 ms for rmp-serde (\~1.4x). Postcard also beats prost on the other three datasets, but flatbuffers serializes 'mesh' faster (371 vs 413 us).

## Use it when

- Rust-to-Rust messages between firmware and a host (no_std microcontroller to desktop or server) where both sides share one crate of serde types.
- Small records with many short strings and small integers. On the 'log' dataset it serialized in about half prost's encode time, and its output was \~18% smaller (724,953 vs 884,628 bytes).
- Serial, USB or radio links that need framing and integrity: the COBS and CRC32 flavors apply while serializing, and the slice or heapless outputs need no heap.
- Reads where borrowing strings and bytes from the input is acceptable. The borrowed deserialize of 'log' took 577 us, against 1.74 ms for owned types.
- Serde codebases that want to replace a self-describing format such as MessagePack (rmp-serde) with a smaller, faster format that has a written spec and a v1 stability promise.

## Skip it when

- Cross-language interop. There is no IDL, so every other language needs a hand-written implementation of the spec. Protobuf, FlatBuffers or Cap'n Proto are the safer choice there.
- Evolving schemas. The format is not self-describing, so adding, removing or reordering fields breaks readers of the old layout, and the spec leaves compatibility to users.
- Maximum CPU throughput on servers. On the same 'log' run, bitcode (96.8 us), serde-zap (135.5 us) and wincode (137.1 us) serialize 2.7-3.8x faster. On the float-heavy 'mesh' dataset, postcard deserializes in 5.22 ms, against 1.26 ms for bitcode and 144 us for wincode.
- Random access into large buffers without decoding. Postcard always decodes the whole message; rkyv, FlatBuffers and Cap'n Proto offer zero-copy access instead.
- Types that depend on self-describing serde features. deserialize_any returns WontImplement, and the Deserializer docs call internally tagged enums incompatible.

## How it is fast

The format carries no field tags, field names or struct lengths. A struct is its fields concatenated in declaration order. Integers wider than 8 bits are 7-bit-per-byte little-endian varints (LEB128-style, zigzag for signed), floats are raw little-endian bytes, and strings and sequences are a varint length followed by the bytes. Serialization is a plain serde walk: the Slice flavor writes through a raw-pointer cursor with one bounds check per push or memcpy. Deserialization reads from a borrowed slice cursor, so &str and &[u8] fields can borrow the input without copying. The README ranks CPU time last among its goals, after memory, code size and developer time, so the speed comes from the minimal format rather than from SIMD or special tuning.

## Compared with alternatives

Pick postcard when its embedded-first features matter (no_std with slice or heapless output, COBS/CRC framing flavors) or when you want its written, v1-stable wire spec. Its 'log' output is also compact: 724,953 bytes, against 703,710 for bitcode, 741,295 for serde-zap and 1,045,784 for wincode. If raw server-side CPU time is the goal, bitcode, serde-zap and wincode serialize the same dataset 2.7-3.8x faster, and rkyv gives zero-copy access.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | serde (default-features off) and cobs 0.3. The default feature heapless-cas pulls in heapless 0.7. Optional: embedded-io 0.4/0.6, crc, defmt, postcard-derive (MaxSize), nalgebra 0.33, enum-map 3. |
| **Minimum toolchain** | Not documented: there is no rust-version in Cargo.toml or on crates.io. Edition 2021 implies Rust 1.56 or newer. CI builds on stable and uses nightly only for the docs build. |
| **Platforms** | Any Rust target, including no_std. CI tests on x86-64 Linux and runs check/clippy builds for thumbv7em-none-eabi and riscv32i-unknown-none-elf (no atomics). usize is handled for 16-, 32- and 64-bit pointer widths. |
| **Thread safety** | Not documented. Each call builds its own Serializer/Deserializer, which owns its flavor and has no global state, so concurrent calls on separate buffers are independent. |
| **Drop-in for the baseline** | partial — Rust code that already derives serde (for example with rmp-serde) only swaps the calls (to_allocvec/from_bytes), but the wire format is incompatible. Replacing prost, flatbuffers or capnp means dropping their IDL-generated types for serde-derived Rust structs. |

## Gotchas

- Some serde attributes break it (tracking issue #125, open). serde(flatten) and serde(skip_serializing_if) break round-trips. serde(skip) on an enum variant that is not last silently shifts the discriminants. deserialize_any, deserialize_identifier and deserialize_ignored_any return Error::WontImplement.
- Sequences and maps must report their exact length up front, or serialization fails with SerializeSeqLengthUnknown. collect_str runs the Display impl twice: once to count the length and once to write.
- The default features pull in heapless 0.7 with 'cas', which triggers the RUSTSEC-2023-0089 atomic-polyfill 'unmaintained' warning (#223). heapless 0.9 support is on main but unreleased; the latest crates.io release is 1.1.3 from 2025-07-24 (#296).
- Untrusted input: panic-freedom is not guaranteed and no fuzzing is documented (#48, open since 2021). A corrupted length prefix no longer drives a huge Vec preallocation, because the sequence size_hint is capped by the bytes remaining. A usize above u32::MAX sent from a 64-bit target fails to decode on a 32-bit one.

## Known shortcomings

- bitcode, serde-zap and wincode serialize the log dataset 2.7-3.8x faster on the same page, and on mesh postcard deserializes in 5.22 ms vs 144 us for wincode. Latest release 1.1.3 (2025-07) lags main; the default heapless-cas feature triggers RUSTSEC-2023-0089. No documented fuzzing and no panic-freedom guarantee on malformed input; flatten and skip_serializing_if break round-trips.

## Caveats and trade-offs

Numbers come from one dataset ('log') of a four-dataset suite (README last updated 2026-09-10). On 'mesh', flatbuffers serializes faster than postcard (371.26 us vs 412.78 us). The margin over capnp serialize on 'log' is small (\~1.3x). capnp and flatbuffers are zero-copy formats with no owned deserialize on the page, so only serialize is comparable for them. The prost figures are encode-only and decode-only, which favors prost. The postcard README itself makes no speed claim; its design goals put memory and code size ahead of CPU time. The format is non-self-describing and has no schema evolution, though the wire format has been stable and documented since v1.0. The run is on a shared 2-core CI VM built with target-cpu=native. GitHub's detector reports Apache-2.0, but the crate is dual MIT OR Apache-2.0, with both license files in the repo.

Designed for embedded/no_std use via serde; schema is implicit in the Rust type (no IDL), so cross-language use requires reimplementing the format elsewhere; not self-describing.

## Maintenance

The repo is actively developed (last commit 2026-09-21, with postcard2 and schema-ng work under way), but the last postcard release is 1.1.3 from July 2025. It is a dual MIT/Apache-2.0 crate with about 66M downloads that you add as an ordinary Cargo dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party suite djkoloski/rust_serialization_benchmark with public code (benches/bench.rs bench_log, src/bench_postcard.rs, src/bench_prost.rs). The README states the compiler (rustc 1.100.0-nightly a36d05efa, LLVM 23.1.1) and the CPU (AMD EPYC 9V74). Flags are in tools/bencher/src/main.rs (RUSTFLAGS -C target-cpu=native) and Cargo.toml [profile.bench] lto = true, so A holds.
- **Verifier notes:** All quoted numbers match the postcard row (366.95 us / 1.7399 ms) and the baseline rows in the 'log' raw table. The derived ratios check out: 2.0x, 2.1x, 1.3x and 3.6x for serialize; 1.5x and 1.4x for deserialize. Fixes: license set to the dual SPDX expression (per source/postcard/Cargo.toml and README), plus flags and hardware detail.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `license`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/rust-toolchain.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/.github/workflows/bench.yml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/tools/bencher/src/main.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/benches/bench.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_prost.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_postcard.rs>
  - <https://github.com/jamesmunns/postcard>
  - <https://github.com/jamesmunns/postcard/blob/main/README.md>
  - <https://github.com/jamesmunns/postcard/blob/main/Cargo.toml>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard/Cargo.toml>
  - <https://crates.io/api/v1/crates/postcard>
- **Sources the enricher read:**
  - <https://github.com/jamesmunns/postcard>
  - <https://github.com/jamesmunns/postcard/blob/main/README.md>
  - <https://github.com/jamesmunns/postcard/blob/main/Cargo.toml>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard/Cargo.toml>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard/src/lib.rs>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard/src/varint.rs>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard/src/ser/serializer.rs>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard/src/ser/flavors.rs>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard/src/de/deserializer.rs>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard/src/de/flavors.rs>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard/src/error.rs>
  - <https://github.com/jamesmunns/postcard/blob/main/spec/src/wire-format.md>
  - <https://github.com/jamesmunns/postcard/blob/main/.github/workflows/ci.yml>
  - <https://github.com/jamesmunns/postcard/blob/main/ci.sh>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard2/README.md>
  - <https://github.com/jamesmunns/postcard/blob/main/source/postcard2/Cargo.toml>
  - <https://github.com/jamesmunns/postcard/commits/main>
  - <https://github.com/jamesmunns/postcard/tags>
  - <https://github.com/jamesmunns/postcard/issues>
  - <https://github.com/jamesmunns/postcard/issues/125>
  - <https://github.com/jamesmunns/postcard/issues/135>
  - <https://github.com/jamesmunns/postcard/issues/223>
  - <https://github.com/jamesmunns/postcard/issues/48>
  - <https://github.com/jamesmunns/postcard/issues/296>
  - <https://github.com/jamesmunns/postcard/issues/114>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_postcard.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://crates.io/api/v1/crates/postcard>
  - <https://crates.io/api/v1/crates/postcard2>
  - <https://docs.rs/postcard/1.1.3/src/postcard/de/flavors.rs.html>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/jamesmunns/postcard`) · [data/wave4/enrich/raw/github_com_jamesmunns_postcard.json](../../../data/wave4/enrich/raw/github_com_jamesmunns_postcard.json) (enrichment confidence 0.85)

</details>
