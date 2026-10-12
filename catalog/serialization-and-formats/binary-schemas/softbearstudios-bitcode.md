# bitcode

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust-only columnar, bit-packed serializer; on string-heavy logs it encodes 5-14x faster than prost, FlatBuffers, Cap'n Proto, rmp-serde.

| | |
|---|---|
| **Beats** | Protobuf (prost 0.14.4; Google's protobuf 4.36.1-release crate also on the page), FlatBuffers (flatbuffers 25.12.19), Cap'n Proto (capnp 0.27.0), MessagePack (rmp-serde 1.3.1); all are the Rust crates for those formats, not the C++ libraries |
| **Claimed result** | serialize 96.821 µs vs prost(protobuf) 731.23 µs (\~7.6x), flatbuffers 763.63 µs (\~7.9x), capnp 480.15 µs (\~5.0x), rmp-serde(msgpack) 1.3179 ms (\~13.6x); deserialize 1.1452 ms vs prost 2.6802 ms (\~2.3x), rmp-serde 2.3829 ms (\~2.1x); wire size 703,710 vs protobuf 884,628 bytes (derived from page data) |
| **Workload** | Serialize/deserialize of the 'log' dataset (small HTTP-request-log-like structs with many strings) in djkoloski/rust_serialization_benchmark. |
| **Metric** | latency |
| **Hardware** | AMD EPYC 9V74 80-Core Processor, 2 cores / 4 threads visible (Microsoft-hypervisor VM, GitHub-hosted ubuntu-latest runner per .github/workflows/bench.yml), x86_64 |
| **Compiler and flags** | rustc 1.100.0-nightly (a36d05efa 2026-09-09), LLVM 23.1.1; run as `cargo bench` by tools/bencher/src/main.rs with RUSTFLAGS="-C target-cpu=native", and Cargo.toml [profile.bench] sets lto = true (otherwise release-profile defaults, opt-level 3); criterion with default settings |
| **Adoption** | 671 stars; \~10.08M crates.io downloads (\~2.69M recent) |
| **Last commit** | 2026-06-28 |
| **Links** | [repository](https://github.com/SoftbearStudios/bitcode) · [benchmark](https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md) |

## Verdict

Source: djkoloski/rust_serialization_benchmark, README run of 2026-09-10, 'log' dataset. bitcode 0.6.9 serialized in 96.8 µs, against 731 µs for prost 0.14.4 (encode only), 764 µs for FlatBuffers, 480 µs for capnp and 1.32 ms for rmp-serde. It deserialized into owned structs in 1.15 ms, against 2.68 ms for prost decode and 2.38 ms for rmp-serde, and its output was 703,710 B versus 884,628 B for protobuf. The run used rustc 1.100.0-nightly (LLVM 23.1.1) with LTO, -C target-cpu=native and criterion, with bitcode::Buffer reused across iterations, on a 2-core AMD EPYC 9V74 GitHub Actions VM. capnp and FlatBuffers have no owned deserialize, so only encode is directly comparable with them, and the ranking flips on the float-heavy 'mesh' dataset.

## Use it when

- Both ends are Rust and built from the same bitcode major version: game or app netcode (including Rust/WASM clients), IPC, internal caches and save files.
- Many small records full of strings, small ints, enums and bools. bitcode had the fastest serialize of any crate on the page for 'log' (96.8 µs) and 'minecraft_savedata' (82.0 µs).
- Bandwidth or storage matters, with or without compression afterwards. On 'log' it was 703,710 B raw and 227,322 B after zstd, against 884,628 B and 314,959 B for prost; its field-grouped layout is designed to compress well.
- no_std targets that have alloc: std is a default feature you can turn off, and CI checks thumbv6m-none-eabi.
- Decoding size-capped untrusted input: lengths and UTF-8 are validated, memory allocated stays proportional to input size, and CI runs cargo-fuzz.

## Skip it when

- Cross-language or long-lived data. There is no schema and no non-Rust implementation. The format may change at every major version, and there is no schema evolution: with derive, adding a field or an enum variant must be assumed to break old bytes.
- Large arrays of floats or POD structs. On 'mesh', bitcode took 1.23 ms to serialize and 1.26 ms to deserialize. rkyv took 141.7/144.7 µs and wincode 147.9/144.4 µs; FlatBuffers (371 µs) and postcard (413 µs) also serialized faster.
- You need zero-copy random access or partial reads. rkyv, FlatBuffers and Cap'n Proto access a buffer in ns, while bitcode always decodes the whole message, and a streaming API is an open request (issue #6).
- Your policy forbids undefined behavior in dependencies. Release builds on x86, x86_64 and aarch64 read past the end of a slice inside the same page; issue #50 is open and PR #51, which would make this opt-in, is unmerged.
- Recursive types with derive: not supported, and the compiler fails with a layout cycle. Serde models also fail if they use untagged, internally tagged or adjacently tagged enums, skip_serializing_if/default, or serde_json::Value; these panic with 'type changed'.

## How it is fast

The derive builds a struct-of-arrays encoder tree. Every instance of a field, such as every status code across a Vec of log records, goes into its own column, and each column is packed in one pass at the end. Integer columns get the narrowest byte width that fits the column maximum, optionally after subtracting the column minimum (frame-of-reference). Byte columns with a range under 16 are packed 2-8 values per byte (bools 8 per byte). Lengths take one byte with a 255 escape. Strings become one length column plus one concatenated byte blob, UTF-8-checked once with a SIMD ASCII fast path. Decoding validates every column up front in a `populate` pass, so the per-value decode loop has no bounds or error checks. The loops are written as fixed-size chunks for LLVM auto-vectorization, and short slices are copied with an over-reading fixed-size 'wild copy' instead of memcpy (see gotchas).

## Compared with alternatives

Pick bitcode over postcard or serde-zap when both ends are Rust and you want the fastest encode and smallest output on record-shaped data. On 'log' it encoded in 96.8 µs against 366.95 and 135.54 µs, and wrote 703,710 B against 724,953 and 741,295 B. Pick postcard if you need its documented, stable 1.0 wire format; pick rkyv or wincode for float/POD-heavy data or zero-copy access, where on 'mesh' they are about 8x faster than bitcode.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bytemuck (required); bitcode_derive proc-macro (default `derive` feature); optional: serde, arrayvec, glam, rust_decimal, time, uuid |
| **Minimum toolchain** | Rust 1.70 for the published 0.6.9 (crates.io rust_version). An unreleased June 2026 commit on main raised rust-version to 1.88. |
| **Platforms** | Any Rust target with alloc (std optional). CI tests x86_64 and i686 Linux, checks thumbv6m-none-eabi, and runs miri on big-endian powerpc64. The over-reading copy fast path is enabled only in x86, x86_64 and aarch64 release builds. |
| **Thread safety** | Buffer is Send + Sync, but encode/decode take &mut self, so use one Buffer per thread. The free encode/decode functions build fresh encoders and decoders per call. Nothing more is documented. |
| **Drop-in for the baseline** | partial — the serde feature (bitcode::serialize/deserialize) can replace rmp-serde calls on existing serde types, but the bytes are not MessagePack. There is no compatibility with protobuf, FlatBuffers or Cap'n Proto data or schemas. |

## Gotchas

- The 'wild copy' in src/derive/vec.rs reads a fixed [T; N] block past the end of short slices when the read stays inside the same 4 KiB page. The maintainers acknowledge this as UB on the wiki Security page. It is disabled under miri and debug_assertions, so the tests don't exercise the path that ships in release. PR #51 measured str-vec encode about 28% slower without it (98.5 vs 126.3 µs).
- In release builds, Error is a zero-sized type whose message is just 'bitcode error', so you get no hint of which field or column failed. Only debug builds carry a reason string.
- Derive (Encode/Decode) and serde (serialize/deserialize) produce different, incompatible bytes for the same type. For example, the serde path drops the SocketAddrV6 flowinfo and scope_id fields. Pick one path per message type.
- There is no max-allocation knob, so cap the input slice length yourself. The Security wiki warns that enums with very unbalanced variant sizes, and structs whose fields are all #[bitcode(skip)], can make small inputs allocate a lot.

## Known shortcomings

- Release builds on x86/x86_64/aarch64 use deliberate undefined behaviour (unsafe_wild_copy reads past short slices within a page; issue #50 open, opt-in PR #51 unmerged; disabled under miri and debug so tests never cover it); part of the log-dataset win depends on it. On float-heavy mesh, rkyv and wincode are about 8x faster. Derive and serde encodings are mutually incompatible, derive has no schema evolution or recursive types, and there is no decode allocation cap.

## Caveats and trade-offs

Numbers come from one dataset ('log') of a four-dataset suite (README last updated 2026-09-10). On 'mesh', flatbuffers serializes faster than bitcode (371.26 us vs 1.2265 ms). capnp and flatbuffers are zero-copy formats with no owned deserialize on the page. Their access time is in ns, so only serialize is directly comparable for them. The prost figures are encode-only and decode-only; they leave out populate and convert, which favors prost. Unlike protobuf, flatbuffers and capnp, bitcode is Rust-only and not self-describing. Its README also makes a stable format across major versions a non-goal. The run is on a shared 2-core CI VM built with target-cpu=native. Cargo.toml and README say MIT OR Apache-2.0, but the repo holds only LICENSE-MIT; the README's LICENSE-APACHE link points to a file that does not exist.

Uses a custom derive macro and bit-packing (not byte-aligned), so it is not wire-compatible with protobuf/flatbuffers/msgpack/capnp and has a smaller ecosystem/no cross-language schema story.

## Maintenance

Actively maintained: last commit 2026-06-28, latest crates.io release 0.6.9 on 2025-12-18, about 10.1M downloads, and it is an ordinary crates.io dependency. It declares MIT OR Apache-2.0, but the repo ships only LICENSE-MIT.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party suite djkoloski/rust_serialization_benchmark with public code (benches/bench.rs bench_log, src/bench_bitcode.rs, src/bench_prost.rs). The README states the compiler (rustc 1.100.0-nightly a36d05efa, LLVM 23.1.1) and the CPU (AMD EPYC 9V74). Flags are in tools/bencher/src/main.rs (RUSTFLAGS -C target-cpu=native) and Cargo.toml [profile.bench] lto = true, so A holds.
- **Verifier notes:** Every quoted number matches the bitcode row and the baseline rows in the 'log' raw table: 96.821 us / 1.1452 ms / 703710 B; prost 731.23 us encode, 2.6802 ms decode, 884628 B; flatbuffers 763.63 us; capnp 480.15 us; rmp-serde 1.3179 ms / 2.3829 ms. The derived ratios are correct. Fixes: last_commit (2026-06-28 is the newest default-branch commit; 2026-06-29 was pushed_at), license (dual, per Cargo.toml and README), and flags (found in the harness).
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `license`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/rust-toolchain.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/.github/workflows/bench.yml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/tools/bencher/src/main.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/benches/bench.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_prost.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_bitcode.rs>
  - <https://github.com/SoftbearStudios/bitcode>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/Cargo.toml>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/README.md>
  - <https://crates.io/api/v1/crates/bitcode>
- **Sources the enricher read:**
  - <https://github.com/SoftbearStudios/bitcode>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/README.md>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/Cargo.toml>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/.cargo/config.toml>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/.github/workflows/build.yml>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/lib.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/coder.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/error.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/buffer.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/pack_ints.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/pack.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/str.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/length.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/f32.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/fast.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/derive/mod.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/derive/vec.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/src/serde/mod.rs>
  - <https://github.com/SoftbearStudios/bitcode/blob/main/bitcode_derive/src/attribute.rs>
  - <https://github.com/SoftbearStudios/bitcode/issues>
  - <https://github.com/SoftbearStudios/bitcode/issues/50>
  - <https://github.com/SoftbearStudios/bitcode/pull/51>
  - <https://github.com/SoftbearStudios/bitcode/issues/74>
  - <https://github.com/SoftbearStudios/bitcode/issues/52>
  - <https://github.com/SoftbearStudios/bitcode/issues/35>
  - <https://github.com/SoftbearStudios/bitcode/issues/58>
  - <https://github.com/SoftbearStudios/bitcode/issues/121>
  - <https://github.com/SoftbearStudios/bitcode/issues/113>
  - <https://github.com/SoftbearStudios/bitcode/issues/16>
  - <https://github.com/SoftbearStudios/bitcode/issues/21>
  - <https://github.com/SoftbearStudios/bitcode/commits/main>
  - <https://github.com/SoftbearStudios/bitcode/wiki/Security>
  - <https://github.com/SoftbearStudios/bitcode/wiki/Serde>
  - <https://crates.io/api/v1/crates/bitcode>
  - <https://crates.io/api/v1/crates/bitcode/0.6.9/download>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_bitcode.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_prost.rs>
  - <https://github.com/rustsec/advisory-db/tree/main/crates/bitcode>
  - <https://github.com/jamesmunns/postcard/blob/main/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/softbearstudios/bitcode`) · [data/wave4/enrich/raw/github_com_softbearstudios_bitcode.json](../../../data/wave4/enrich/raw/github_com_softbearstudios_bitcode.json) (enrichment confidence 0.86)

</details>
