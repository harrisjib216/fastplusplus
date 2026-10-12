# wincode

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Bincode-1.x-compatible Rust serializer with in-place encoding; serializes 3.5-9.6x faster than the prost, FlatBuffers, capnp and rmp-serde crates on log data.

| | |
|---|---|
| **Beats** | Protobuf, FlatBuffers, Cap'n Proto, MessagePack |
| **Claimed result** | On the 'log' dataset (page run 2026-09-10), wincode 0.6.1 serializes in 137.05 µs. The comparisons are prost 'encode' 731.23 µs (\~5.3x; prost populate+encode is 1.8883 ms), flatbuffers 763.63 µs (\~5.6x), capnp 480.15 µs unpacked (\~3.5x) and rmp-serde (msgpack) 1.3179 ms (\~9.6x). wincode deserializes in 1.4166 ms against 2.6802 ms for prost decode (\~1.9x) and 2.3829 ms for rmp-serde (\~1.7x). The same pattern holds on the other datasets: mesh serialize is 147.88 µs against 371.26 µs for flatbuffers and 5.8939 ms for prost encode. (derived from page data) |
| **Workload** | Serialize/deserialize of the 'log' dataset (small HTTP-request-log-like structs with many strings) in djkoloski/rust_serialization_benchmark. |
| **Metric** | latency |
| **Hardware** | AMD EPYC 9V74 (2 cores / 4 threads visible to the VM), x86_64 |
| **Compiler and flags** | rustc 1.100.0-nightly (a36d05efa 2026-09-09), LLVM 23.1.1; built with `cargo bench` (bench profile, lto = true in Cargo.toml) with RUSTFLAGS='-C target-cpu=native' set by tools/bencher/src/main.rs; criterion harness |
| **Adoption** | 234 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/anza-xyz/wincode) · [benchmark](https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md) |

## Verdict

Data comes from djkoloski/rust_serialization_benchmark (run 2026-09-10, rustc 1.100.0-nightly, LLVM 23.1.1, lto, target-cpu=native, criterion, 2-core/4-thread AMD EPYC 9V74 VM). On the log dataset, wincode 0.6.1 `serialize_into` a pre-sized reused buffer took 137.05 µs, against 731.23 µs for prost 0.14.4 encode, 763.63 µs for flatbuffers 25.12.19, 480.15 µs for unpacked capnp 0.27.0 and 1.3179 ms for rmp-serde 1.3.1. Deserialize took 1.4166 ms vs 2.6802 ms for prost decode and 2.3829 ms for rmp-serde. These are the Rust crates for those formats, not the C++ libraries, and FlatBuffers/capnp have no deserialize row because they are zero-copy.

## Use it when

- You already use the bincode 1.x format (Solana accounts, transactions, on-chain data) and want a faster encoder that writes the same bytes.
- Payloads are mostly fixed-size or POD data: arrays of f32/u64, `[u8; 32]` hashes and signatures, `#[repr(C)]` structs. Sequences become memcpy. On the mesh dataset it deserializes in 144.44 µs vs 10.253 ms for prost decode.
- You want zero-copy borrows (`&[u8]`, `&[u8; N]`, `&PodStruct` via `ZeroCopy::from_bytes`) or in-place mutation of an encoded buffer (`from_bytes_mut`, `deserialize_mut`) without adopting rkyv or FlatBuffers.
- Rust-only services where both ends are Rust types and you can write into a reused, pre-sized buffer with `serialize_into`.
- no_std targets: `std` and `alloc` are optional features.

## Skip it when

- You need a schema/IDL, cross-language readers, or schema evolution (optional/added fields). The Rust type is the schema, as in bincode, and there is no versioning.
- Wire size or bandwidth matters. On log it encodes 1,045,784 bytes vs 703,710 for bitcode, 724,953 for postcard, 784,997 for rmp-serde and 884,628 for prost. The cause is 8-byte fixed lengths on every string. The `VarInt` config shrinks this, but the docs say it hurts speed significantly and disables integer zero-copy.
- Your data is string-heavy and speed is the only goal. bitcode beats it on log (96.821 µs vs 137.05 µs serialize, 1.1452 ms vs 1.4166 ms deserialize), and on minecraft_savedata (82.049 µs vs 132.62 µs serialize).
- You need a stable API. It is pre-1.0 (0.6.1, Aug 2026): 0.5.0 shipped in March 2026 and 0.6.0 in July. The published audits (Neodyme, OtterSec) cover v0.1.2, not the current code.
- Big-endian or non-x86 targets are a priority. Zero-copy of multi-byte integers works only on little-endian, and CI runs on ubuntu-latest (x86-64) only.

## How it is fast

The main idea is in-place initialization. `SchemaRead::read` writes each field straight into a `MaybeUninit<Dst>`, and `serialize` makes one `size_of` pass, allocates once, and writes into the Vec's spare capacity. There are no staging buffers and none of serde's construct-then-move copies. Each type has a compile-time `TypeMeta` (Static size + zero_copy flag). For static-size types and sequences, it opens an `as_trusted_for` window whose bounds are checked once. For padding-free `#[repr(C)]`/transparent structs, byte arrays and (on little-endian targets) integers and floats, a whole slice becomes a single memcpy, or a borrow of the input. Fixed-width integers keep that memcpy path open. The cost is a bigger wire format.

## Compared with alternatives

Choose it over bitcode or postcard when you must stay on the bincode 1.x wire format or want zero-copy/in-place mutation of POD data. bitcode is faster on string-heavy log data and \~33% smaller on the wire. wincode ties it on mk48 (518.04 µs vs 546.49 µs serialize) and is far faster on mesh (147.88 µs vs 1.2265 ms). Against serde-zap, serialize speed is the same on log (137.05 vs 135.54 µs) but wincode deserializes faster (1.4166 vs 1.7212 ms). Choose rkyv when you need to read fields without deserializing at all.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | pastey, thiserror; optional wincode-derive (syn, quote, proc-macro2, darling) via `derive` feature; optional bytes, bv, bumpalo, ecow, indexmap, smallvec, uuid integrations |
| **Minimum toolchain** | Rust 1.89 (edition 2024) |
| **Platforms** | any Rust target; no_std supported; integer/float zero-copy only on little-endian; CI tests only on Linux x86-64 (plus Miri) |
| **Thread safety** | not documented; the API is stateless free functions and traits over caller-owned buffers |
| **Drop-in for the baseline** | partial: no drop-in for Protobuf, FlatBuffers, Cap'n Proto or MessagePack, since the wire format and the no-IDL model differ. It is close to drop-in for bincode 1.x `bincode::serialize` (same bytes) after you swap serde derives for SchemaWrite/SchemaRead. |

## Gotchas

- Every sequence has a default 4 MiB preallocation limit. Deserializing a larger `Vec` (e.g. 4 MiB + 1 byte of `Vec<u8>`) fails with `PreallocationSizeLimit` where bincode succeeds (issues #51, #90). Raise it through `Configuration` or `UseIntLen<_, N>`. The overall deserialization size limit is off by default.
- `serialize_into` is not transactional. Dynamic types can leave a partial prefix in the destination buffer, and only static-size types are length-checked up front (issue #418, 'as intended'). Check `serialized_size` first when writing into fixed buffers.
- `SchemaWrite`/`SchemaRead` are `unsafe` traits. A wrong manual `TYPE_META` (Static size or zero_copy) or a `pod_wrapper!` on a type with padding or invalid bit patterns is UB. Several unsoundness reports (#79-#82, #89) and an uninitialized-memory leak in `Cursor<Vec>` writers (#306, fixed May 2026) have been closed.
- The `tag`/`tag_encoding` enum attributes and `UseIntLen` break bincode byte-compatibility. Trailing bytes are accepted by default.

## Known shortcomings

- bitcode beats it on the log and minecraft_savedata datasets (serialize and deserialize). Deserialization caps each sequence at 4 MiB by default, so large Vecs fail where bincode succeeds (#51, #90). Audits cover v0.1.2; current 0.6.1 is pre-1.0 with breaking minor releases. CI is Linux x86-64 only and zero-copy multi-byte integers need little-endian targets.

## Caveats and trade-offs

The headline numbers come from one dataset ('log') of a multi-dataset benchmark. wincode is not the fastest row: bitcode serializes log in 96.821 µs and deserializes it in 1.1452 ms. FlatBuffers and capnp have no deserialize figures on the page (†) because they are zero-copy formats. wincode is newer and less used outside the Solana ecosystem than postcard or bitcode. The benchmark host is a 2-core/4-thread Hyper-V VM.

Maintained by Anza (Solana) for Solana-specific bincode-like encoding; wire is not length-optimized (largest wire size of the compared crates at 1,045,784 bytes), trading size for speed; implicit Rust-type schema, no IDL.

## Maintenance

Actively maintained by Anza (last master commit 2026-09-17, releases every few weeks), Apache-2.0, \~5.9M crates.io downloads and 196 reverse dependencies, mostly Solana crates; pre-1.0, so expect breaking minor releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The auto-generated README (last updated 2026-09-10) has wincode 0.6.1, prost 0.14.4, flatbuffers 25.12.19, capnp 0.27.0 and rmp-serde 1.3.1 rows in the same run. It states the compiler (rustc 1.100.0-nightly a36d05efa 2026-09-09, LLVM 23.1.1) and the CPU (AMD EPYC 9V74). The flags are in public code: tools/bencher/src/main.rs runs `cargo bench` with RUSTFLAGS='-C target-cpu=native', and Cargo.toml sets [profile.bench] lto = true. The benchmark code is benches/bench.rs with src/bench_wincode.rs, src/bench_prost.rs, src/bench_flatbuffers.rs, src/bench_capnp.rs and src/bench_rmp_serde.rs.
- **Verifier notes:** Every number in the record matches the log Raw data table in wincode's row. The prost figures are the 'encode'/'decode' variants. Flags are in the harness code, so the record's 'flags not itemized' was replaced. Metadata checked: Apache-2.0, 234 stars, not a fork, not archived. The last commit on default branch master is 2026-09-17; the record's 2026-09-23 is pushed_at, from a dependabot branch.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/tools/bencher/src/main.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/tree/master/src>
  - <https://github.com/djkoloski/rust_serialization_benchmark/tree/master/benches>
  - <https://github.com/anza-xyz/wincode>
  - <https://github.com/anza-xyz/wincode/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/anza-xyz/wincode>
  - <https://github.com/anza-xyz/wincode/blob/master/README.md>
  - <https://github.com/anza-xyz/wincode/blob/master/Cargo.toml>
  - <https://github.com/anza-xyz/wincode/blob/master/rust-toolchain.toml>
  - <https://github.com/anza-xyz/wincode/blob/master/.cargo/config.toml>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/Cargo.toml>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/src/lib.rs>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/src/config/mod.rs>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/src/config/serde.rs>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/src/schema/mod.rs>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/src/schema/containers.rs>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/src/schema/impls.rs>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/src/schema/int_encoding.rs>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/src/io/mod.rs>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/src/len.rs>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode/src/serde.rs>
  - <https://github.com/anza-xyz/wincode/blob/master/wincode-derive/Cargo.toml>
  - <https://github.com/anza-xyz/wincode/blob/master/.github/workflows/ci.yml>
  - <https://github.com/anza-xyz/wincode/issues>
  - <https://github.com/anza-xyz/wincode/issues/51>
  - <https://github.com/anza-xyz/wincode/issues/59>
  - <https://github.com/anza-xyz/wincode/issues/90>
  - <https://github.com/anza-xyz/wincode/issues/199>
  - <https://github.com/anza-xyz/wincode/issues/306>
  - <https://github.com/anza-xyz/wincode/issues/417>
  - <https://github.com/anza-xyz/wincode/issues/418>
  - <https://github.com/anza-xyz/wincode/commits/master>
  - <https://crates.io/api/v1/crates/wincode>
  - <https://crates.io/api/v1/crates/wincode/reverse_dependencies>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_wincode.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_prost.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_bitcode.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_rmp_serde.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/datasets/log/mod.rs>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/anza-xyz/wincode`) · [data/wave4/enrich/raw/github_com_anza_xyz_wincode.json](../../../data/wave4/enrich/raw/github_com_anza_xyz_wincode.json) (enrichment confidence 0.85)

</details>
