# minicbor

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `BlueOak-1.0.0` · 🟢 active

> no_std Rust CBOR codec whose derived encoders serialize 2.6-6.9x faster than rmp-serde (MessagePack); decoding is only on par.

| | |
|---|---|
| **Beats** | MessagePack |
| **Claimed result** | log dataset: minicbor 2.3.0 serialize 405.77 us vs rmp-serde 1.3.1 1.3179 ms (\~3.2x faster, derived from page data); deserialize 2.3448 ms vs 2.3829 ms (on par). Vs prost 0.14.4: \~1.8x vs encode-only 731.23 us, \~4.7x vs populate+encode 1.8883 ms (derived). Vs the common serde CBOR crate ciborium 0.2.2: serialize 3.3751 ms (\~8.3x) and deserialize 10.862 ms (\~4.6x) (derived from page data). |
| **Workload** | Criterion micro-benchmark, 'log' dataset (HTTP request logs, many strings), serialize and deserialize a Rust struct via the rust_serialization_benchmark shootout. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9V74 80-Core Processor, 4 vCPUs, x86_64-unknown-linux-gnu |
| **Compiler and flags** | rustc 1.100.0-nightly (a36d05efa 2026-09-09), LLVM 23.1.1; Criterion via cargo bench, [profile.bench] lto = true |
| **Adoption** | 110 stars |
| **Last commit** | 2026-07-23 |
| **Links** | [repository](https://github.com/twittner/minicbor) · [benchmark](https://github.com/djkoloski/rust_serialization_benchmark) |

## Verdict

Source: djkoloski/rust_serialization_benchmark run of 2026-09-10 (Criterion; rustc 1.100.0-nightly, LLVM 23.1.1, bench profile with LTO; AMD EPYC 9V74, 4 vCPUs, Hyper-V guest). On the log dataset, minicbor 2.3.0 with derived Encode/Decode serialized into a preallocated slice in 405.77 us vs 1.3179 ms for rmp-serde 1.3.1 (\~3.2x), and deserialized in 2.3448 vs 2.3829 ms (a tie). The same run puts it \~8.3x ahead of ciborium 0.2.2 on serialize and \~4.6x on deserialize.

## Use it when

- Encode-heavy paths such as logging, telemetry or snapshots now on rmp-serde. On all four shootout datasets, serialize time drops 2.6x (minecraft_savedata) to 6.9x (mesh), and 3.2x on string-heavy log records.
- You already use CBOR through ciborium. On log it is \~8.3x faster to serialize and \~4.6x faster to deserialize, and the output is \~42% smaller (817,830 vs 1,407,835 bytes) because integer indices replace field names. Against cbor4ii, deserialize is \~1.8x faster and serialize is close (405.77 vs 471.14 us).
- no_std or embedded targets. The core crate has no required dependencies, encodes into a fixed &mut [u8] without allocating, and CI builds it for aarch64-unknown-none.
- Long-lived or cross-language data where you want a standard, self-describing format with protobuf-style evolution: unknown fields are skipped, a missing Option decodes as None, and indices let you rename freely.
- Read paths that can borrow. Decoding into &str or ByteSlice borrows from the input: 1.0694 ms on log vs 2.3448 ms for owned decoding.

## Skip it when

- Decode-dominated workloads. Deserialize ranges from \~13% slower than rmp-serde (minecraft_savedata 2.6924 vs 2.3727 ms) to \~5% faster (mk48), so reads gain nothing.
- You must emit MessagePack, or just want the fastest Rust MessagePack. msgpacker and zerompk beat it on the same log table (serialize \~266-269 us, deserialize 1.81-2.07 ms).
- You need deterministic CBOR (RFC 8949 section 4.2) for hashing or signing. Floats are always written at their declared width and map keys are not sorted; the request is open as issue #58.
- You want to keep plain serde derives. The measured numbers come from the native #[derive(Encode, Decode)] with #[n(i)] on every field, and minicbor-serde's speed is not in this benchmark.
- Your toolchain is older than Rust 1.85 (the crate uses edition 2024; the maintainer declined 2021 support in #50), or your policy only allows MIT/Apache (the maintainer declined relicensing in #6).

## How it is fast

It uses no special algorithm. The derived code calls concrete, type-specific Encoder/Decoder methods (Encoder::str, Decoder::u32) directly, with no serde Serializer/Visitor layer in between. The Encoder writes into a caller-supplied &mut [u8] or Vec&lt;u8&gt; using copy_from_slice/extend_from_slice and allocates nothing. The derive replaces field names with integer indices and by default encodes a struct as a CBOR array where position stands for the index, so no string keys are written or matched; &str and ByteSlice fields decode zero-copy from the input after UTF-8 checking. The benchmark does not show which of these produces the gap over rmp-serde.

## Compared with alternatives

Pick minicbor over postcard (366.95 us serialize on the same log table, about the same speed) or bitcode (96.821 us) when the bytes must be standard CBOR that other languages' decoders can read, with index-based field evolution. If the data never leaves Rust and throughput is the goal, bitcode, serde-zap, wincode and rkyv all post much faster serialize times on the same page.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none required; optional minicbor-derive (a proc-macro built on syn/quote/proc-macro2) via the 'derive' feature, 'half' for f16; minicbor-serde adds serde |
| **Minimum toolchain** | Rust 1.85 (edition 2024). Cargo.toml has no rust-version field, and CI tests only stable and beta. |
| **Platforms** | any; no_std core (CI builds for aarch64-unknown-none); 'alloc' and 'std' features add collections and std types; atomic impls are gated on target_has_atomic |
| **Thread safety** | not documented; Encoder and Decoder are plain per-call values (a writer, or a borrowed slice plus a position) with no global state |
| **Drop-in for the baseline** | no |

## Gotchas

- Every field and variant needs an explicit index. The default array encoding writes a NULL byte for each None and each index gap, so use #[cbor(map)] for sparse types. Non-optional fields can never be removed, and a top-level enum is not forward-compatible: an unknown variant is an error unless the enum sits behind an Option field.
- &[u8] and Vec&lt;u8&gt; encode as CBOR arrays of integers, not byte strings, unless you use ByteSlice/ByteVec or #[cbor(with = "minicbor::bytes")].
- Without the 'alloc' feature, Decoder::skip cannot skip indefinite-length arrays or maps nested inside definite ones. An unknown field of that shape then fails decoding instead of being ignored.
- minicbor-serde's Deserializer reports is_human_readable = false. Serde internally tagged enums holding types such as SocketAddr then fail to round-trip (issue #55, closed as a serde upstream problem).

## Known shortcomings

- Beats rmp-serde (MessagePack) on serialize only (about 3.2x); deserialize is about equal, and msgpacker and zerompk beat minicbor in the same table.
- Only the native derive path with #[n(i)] indices was measured; minicbor-serde (a serde drop-in) was not. Deserialize ranges from 13% slower to 5% faster than rmp-serde. No deterministic CBOR (#58). Needs Rust 1.85. Blue Oak licence (maintainer declined MIT/Apache, #6) reports as NOASSERTION on GitHub, which may trip licence scanners. minicbor-serde breaks internally tagged enums with types like SocketAddr (#55).

## Caveats and trade-offs

Serialize-only win over MessagePack's rmp-serde: deserialize is on par on log and slightly slower on mesh (9.4268 vs 9.2506 ms) and minecraft_savedata (2.6924 vs 2.3727 ms). Other MessagePack crates in the same table (msgpacker 266.04 us, zerompk 269.23 us serialize; 2.0663 / 1.8129 ms deserialize) beat minicbor, so it is faster than the incumbent rmp-serde, not than MessagePack in general. Its clearest win is over ciborium (CBOR). Output is smaller than ciborium's (817830 vs 1407835 bytes on log), so the encodings differ. Licensed Blue Oak Model License 1.0.0, OSI-approved on 2024-01-19; GitHub reports NOASSERTION.

CBOR-based (self-describing, larger than a tight custom binary format); designed for no_std/embedded use; deserialize speed is not clearly ahead of msgpack, only serialize is.

## Maintenance

Actively maintained. Release 2.3.0 shipped 2026-07-23 and the develop branch has commits through 2026-09-26; about 15.6M crates.io downloads and 185 reverse dependencies. Usability is copyable under Blue Oak 1.0.0, an OSI-approved permissive license, but GitHub reports it as NOASSERTION, which may trip license scanners.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Same public shootout (djkoloski/rust_serialization_benchmark: benches/bench.rs, src/bench_minicbor.rs vs src/bench_rmp_serde.rs) with rmp-serde (MessagePack) and ciborium (CBOR) in the same table; rustc 1.100.0-nightly/LLVM 23.1.1, [profile.bench] lto=true, and CPU AMD EPYC 9V74 are all stated, so A holds.
- **Verifier notes:** Numbers match minicbor's and rmp-serde's rows. The record's 'reference' usability was wrong: Blue Oak 1.0.0 is OSI-approved (opensource.org page; SPDX isOsiApproved=true), so usability is copyable. Last commit 2026-07-23, 110 stars, not fork/archived: metadata correct.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `usability`, `caveats`
- **Shortcomings recorded by:** rust_serialization_benchmark (2026-09-10): about 8.3x faster serialize and 4.6x faster deserialize than ciborium, the common Rust CBOR crate (derived from page data).
- **Pages the verifier opened:**
  - <https://github.com/djkoloski/rust_serialization_benchmark>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/tree/master/src>
  - <https://github.com/twittner/minicbor>
  - <https://github.com/twittner/minicbor/blob/master/LICENSE.md>
  - <https://github.com/spdx/license-list-data/blob/main/json/details/BlueOak-1.0.0.json>
  - <https://opensource.org/license/blue-oak-model-license>
- **Sources the enricher read:**
  - <https://github.com/twittner/minicbor>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor/README.md>
  - <https://github.com/twittner/minicbor/blob/develop/Cargo.toml>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor/Cargo.toml>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor-derive/Cargo.toml>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor-serde/Cargo.toml>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor-bench/Cargo.toml>
  - <https://github.com/twittner/minicbor/blob/develop/.github/workflows/develop.yml>
  - <https://github.com/twittner/minicbor/blob/develop/Makefile>
  - <https://github.com/twittner/minicbor/blob/develop/CHANGELOG.md>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor/src/lib.rs>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor/src/encode/encoder.rs>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor/src/encode/write.rs>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor/src/decode/decoder.rs>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor/src/decode.rs>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor/src/bytes.rs>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor-derive/src/lib.rs>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor-serde/src/lib.rs>
  - <https://github.com/twittner/minicbor/blob/develop/minicbor-bench/tests/bench.rs>
  - <https://github.com/twittner/minicbor/issues>
  - <https://github.com/twittner/minicbor/issues/6>
  - <https://github.com/twittner/minicbor/issues/25>
  - <https://github.com/twittner/minicbor/issues/50>
  - <https://github.com/twittner/minicbor/issues/55>
  - <https://github.com/twittner/minicbor/issues/58>
  - <https://github.com/twittner/minicbor/issues/60>
  - <https://github.com/twittner/minicbor/issues/68>
  - <https://github.com/twittner/minicbor/issues/70>
  - <https://github.com/djkoloski/rust_serialization_benchmark>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_minicbor.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_rmp_serde.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_ciborium.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_cbor4ii.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/datasets/log/mod.rs>
  - <https://crates.io/api/v1/crates/minicbor>
  - <https://crates.io/api/v1/crates/minicbor/reverse_dependencies>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/twittner/minicbor`) · [data/wave4/enrich/raw/github_com_twittner_minicbor.json](../../../data/wave4/enrich/raw/github_com_twittner_minicbor.json) (enrichment confidence 0.82)

</details>
