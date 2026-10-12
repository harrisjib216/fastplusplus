# rkyv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust zero-copy serialization crate; faster serialize and in-place reads than Rust FlatBuffers, Cap'n Proto, prost and rmp-serde.

| | |
|---|---|
| **Beats** | Cap'n Proto, FlatBuffers, Protocol Buffers (via prost/protobuf crates), MessagePack (via rmp-serde/msgpacker/zerompk) |
| **Claimed result** | On the 'log' dataset (page run 2026-09-10), rkyv serializes in 178.87 µs, against 763.63 µs for FlatBuffers (\~4.3x, derived from page data), 480.15 µs for Cap'n Proto (\~2.7x, derived from page data), 731.23 µs for prost encode and 1.3179 ms for rmp-serde. Unvalidated zero-copy access takes 1.0907 ns against 2.1807 ns for FlatBuffers. Unvalidated read takes 8.3309 µs against 42.209 µs for FlatBuffers; the record's '8.33 µs deserialize' was this read figure. rkyv's full unvalidated deserialize takes 1.2188 ms, against 2.6802 ms for prost decode and 2.3829 ms for rmp-serde. rkyv serialize also beats all four baselines on the other datasets: mesh 141.74 µs (FlatBuffers 371.26 µs), minecraft_savedata 212.50 µs (Cap'n Proto 392.46 µs) and mk48 798.81 µs (Cap'n Proto 2.1159 ms). It is not the fastest Rust crate overall. Its serialize speed relative to the best crate is 54.13% (log), 100% (mesh), 38.61% (minecraft_savedata) and 64.85% (mk48). bitcode leads on log and minecraft_savedata. |
| **Workload** | Criterion benchmarks in rust_serialization_benchmark on four Rust datasets: log (HTTP request logs), mesh (triangle mesh), minecraft_savedata (Minecraft player saves) and mk48 (mk48.io game updates). They measure serialize, deserialize, zero-copy access, read and update times, plus encoded size and compressed size. The baselines are Rust crates: capnp 0.27.0, flatbuffers 25.12.19, prost 0.14.4, protobuf 3.7.2 and 4.36.1, rmp-serde 1.3.1, msgpacker 0.7.1 and zerompk 0.8.0. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9V74 80-Core Processor, 4 vCPUs (2 cores x 2 threads), on a Microsoft Hyper-V VM (GitHub Actions ubuntu-latest runner), x86_64 |
| **Compiler and flags** | rustc 1.100.0-nightly (a36d05efa 2026-09-09), LLVM 23.1.1. `cargo bench` runs with RUSTFLAGS='-C target-cpu=native' (tools/bencher/src/main.rs). Cargo.toml sets [profile.bench] lto = true; opt-level 3 is inherited from release. Criterion harness. |
| **Adoption** | 4.4k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/rkyv/rkyv) · [benchmark](https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md) |

## Verdict

The source is rust_serialization_benchmark's CI run of 2026-09-10: rkyv 0.8.18 against the Rust crates capnp 0.27, flatbuffers 25.12.19, prost 0.14.4 and rmp-serde 1.3.1, built with rustc 1.100.0-nightly (LLVM 23.1.1), -C target-cpu=native and LTO, measured by Criterion on a 4-vCPU AMD EPYC 9V74 GitHub Actions VM. On the log dataset rkyv serialized in 178.87 µs, against 480.15 µs for capnp, 731.23 µs for prost, 763.63 µs for FlatBuffers and 1.318 ms for rmp-serde; it read unvalidated in 8.33 µs against 42.2 µs for FlatBuffers, and fully deserialized in 1.22 ms against 2.68 ms for prost decode. The baselines are Rust ports, not the C++ reference libraries, and the serialize loop reuses a pre-allocated 10 MB AlignedVec.

## Use it when

- Both writer and reader are Rust and you load large read-mostly data (game assets, caches, precomputed indexes, memory-mapped files) where parse time dominates: access is constant-time and reads run in place (log dataset unvalidated read 8.33 µs vs 42.2 µs for Rust FlatBuffers).
- You want to query archived HashMap/BTreeMap/Rc-shared data in place without rebuilding it; rkyv archives these natively, which Cap'n Proto and FlatBuffers do not.
- Serialize-heavy Rust pipelines now using prost, rmp-serde, capnp or flatbuffers: 2.7x to 7.4x faster serialize on the log dataset, and faster on all four datasets.
- Untrusted input that must still be checked: validated access on log costs 274 µs vs 2.14 ms for FlatBuffers validated. For data you trust (checksummed or signed, or your own files), unsafe access_unchecked removes that cost entirely.
- no_std or no-alloc targets: the std and alloc features can be turned off, and CI cross-builds thumbv6m-none-eabi.

## Skip it when

- Any non-Rust producer or consumer, C++ included: there is no C API, and the project's own feature matrix lists cross-language support as 'no'.
- You need schema evolution or forward/backward compatibility: the feature matrix says no. Archives stay readable only if the Rust type, the format-control features and a semver-compatible rkyv version are all unchanged. Versioning is manual, for example the AsBox wrapper trick in examples/backwards_compat.rs.
- Wire size or bandwidth is the bottleneck: the log buffer is 1,011,488 B, against 703,710 B for bitcode, 784,997 B for rmp-serde and 884,628 B for prost. Unset fields, padding and pointers all take space.
- You only need the fastest Rust round-trip into native types: bitcode beats rkyv on log serialize (96.8 µs vs 178.9 µs), on minecraft_savedata serialize (82.0 µs vs 212.5 µs) and on log deserialize (1.145 ms vs 1.219 ms).
- Very large archives on the default 32-bit relative pointers: one user hit an 'out of range integral type conversion' panic at about 1.2 GB (issue #657). The fix is the pointer_width_64 feature, which changes the wire format.

## How it is fast

Total zero-copy deserialization: the archived bytes are the in-memory representation, and internal references are relative pointers (RelPtr, a 32-bit offset from the pointer's own address by default). Access is therefore a pointer offset plus a cast (1.09 ns on every dataset), and it works on read-only memory-mapped buffers. Serialization is a single write-forward pass that places leaves first and the root last, using per-type resolvers and a reusable scratch arena instead of per-object heap allocations. Collections are archived as ready-to-query structures: a SwissTable hash map (SSE2/NEON group probing, target-independent FxHash) and a B-tree. The optional bytecheck validation is a separate upfront pass that checks bounds and subtree ranges without allocating.

## Compared with alternatives

Pick rkyv when both ends are Rust and you want zero-copy access to ordinary Rust types (Vec, String, HashMap, BTreeMap, Rc) without maintaining an IDL. Pick YaFF or ProtoCache (C++ flat formats for Protobuf schemas) or the multi-language Apache Fory when C++ or another language must read the data, or when you need schema evolution.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | munge, ptr_meta, rancor, rend and rkyv_derive (a proc-macro using syn 3) are always pulled in. The default bytecheck feature adds bytecheck; the alloc feature adds hashbrown 0.17. Optional integrations cover arrayvec, bytes, hashbrown, indexmap, smallvec, smol_str, thin-vec, tinyvec, triomphe and uuid. |
| **Minimum toolchain** | Rust 1.81 (rust-version in Cargo.toml), edition 2021; CI tests stable, beta and nightly |
| **Platforms** | Any Rust target. CI tests x86_64 Linux, aarch64 macOS and x86_64 Windows, and cross-builds i686, i586, armv7, aarch64 Linux and thumbv6m-none-eabi. The hash-table SIMD path uses SSE2 on x86/x86_64 and NEON on little-endian aarch64, with a generic fallback everywhere else. |
| **Thread safety** | No thread-safety guarantees are documented beyond Rust's type system. With std, the built-in scratch arena used by to_bytes is thread-local. Without std but with atomics, it is one global arena shared by all threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline access and read figures (1.09 ns, 8.33 µs) come from unsafe access_unchecked, which skips all validation. Running it on untrusted bytes is undefined behavior; use access/from_bytes with the bytecheck feature for untrusted data.
- Alignment and placement: the default format is aligned, so buffers need proper alignment (AlignedVec, or 16-byte alignment is usually enough). access also expects the root object to end exactly at the end of the buffer, so a length prefix or trailing bytes break it.
- Endianness, alignment and pointer-width features change the wire format for the whole dependency graph. As a 0.x crate, archives are only compatible across semver-compatible releases (0.7 and 0.8 cannot read each other).
- Safety history: RUSTSEC-2026-0233, -0234 and -0235 covered use-after-free and out-of-bounds reads that crafted archives triggered through the safe validated APIs; all three were patched in 0.8.17. Still open: #685 (a validated IndexMap/IndexSet can panic on lookup, a denial-of-service risk) and soundness reports #696/#697 about safe custom trait impls. rkyv_dyn (trait objects) is commented out of the workspace and pinned at 0.8.0-rc.1.

## Caveats and trade-offs

The benchmark repo (rust_serialization_benchmark) is maintained by rkyv's author (djkoloski) with other volunteers, so it is not fully independent. It is public, reproducible and covers about 27 crates. The baselines are the Rust implementations of each format (capnp, flatbuffers, prost/protobuf, rmp-serde crates), not the C++ reference libraries. CI regenerates the README on a shared cloud VM, so the figures drift between runs; these are from the 2026-09-10 run. The fastest access, read and deserialize figures use unsafe unvalidated APIs. Validated access on log costs 274.32 µs, against 2.1354 ms for FlatBuffers validated. The original 'rkyv is faster than...' blog post domain is dead or redirected. Relative performance varies by dataset.

Rust-only, no official C API, so not directly usable from C++ (qualifies under the 'non-C++ implementations welcome' rule). Zero-copy access model requires careful handling of untrusted input (validation feature adds cost, shown separately in the 'validated upfront with error' benchmark rows). Not a schema/IDL system like Cap'n Proto/FlatBuffers/Protobuf — Rust-type-driven instead.

## Maintenance

Actively maintained by its original author: 0.8.18 shipped on crates.io 2026-08-05, commits continue through 2026-09-25, and the crate has about 161M downloads. It is MIT-licensed and used as a normal Cargo dependency; require &gt;=0.8.17 for untrusted input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README (last updated 2026-09-10) includes rows for the capnp 0.27.0, flatbuffers 25.12.19, prost 0.14.4/protobuf and rmp-serde/msgpacker/zerompk crates. It states the compiler (rustc 1.100.0-nightly, LLVM 23.1.1) and the CPU (AMD EPYC 9V74). The flags are in the public code: tools/bencher/src/main.rs runs `cargo bench` with RUSTFLAGS='-C target-cpu=native', and Cargo.toml sets [profile.bench] lto = true. The benchmark code is benches/bench.rs with src/bench_rkyv.rs, src/bench_flatbuffers.rs, src/bench_capnp.rs, src/bench_prost.rs and src/bench_rmp_serde.rs.
- **Verifier notes:** I confirmed Tier A. The log, mesh, minecraft_savedata and mk48 figures all match the auto-generated README tables. I fixed one mislabel: the '8.33 µs vs 42.2 µs deserialize' pair is the zero-copy Read column, and the real unvalidated deserialize figure is 1.2188 ms. Metadata checked: MIT, 4,362 stars, not a fork, not archived, last commit 2026-09-25.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/rust-toolchain.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/.github/workflows/bench.yml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/tools/bencher/src/main.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_rkyv.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_flatbuffers.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_capnp.rs>
  - <https://github.com/rkyv/rkyv>
  - <https://github.com/rkyv/rkyv/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/rkyv/rkyv>
  - <https://github.com/rkyv/rkyv/blob/main/README.md>
  - <https://github.com/rkyv/rkyv/blob/main/Cargo.toml>
  - <https://github.com/rkyv/rkyv/blob/main/rkyv/Cargo.toml>
  - <https://github.com/rkyv/rkyv/blob/main/SECURITY.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/faq.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/feature-comparison.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/motivation.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/architecture/relative-pointers.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/architecture/serialize.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/architecture/archive.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/format.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/format/alignment.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/validation.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/zero-copy-deserialization.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/allocation-tracking.md>
  - <https://github.com/rkyv/rkyv/blob/main/book_src/shared-pointers.md>
  - <https://github.com/rkyv/rkyv/blob/main/rkyv/src/lib.rs>
  - <https://github.com/rkyv/rkyv/blob/main/rkyv/src/simd/mod.rs>
  - <https://github.com/rkyv/rkyv/blob/main/rkyv/src/rel_ptr.rs>
  - <https://github.com/rkyv/rkyv/blob/main/rkyv/src/collections/swiss_table/table.rs>
  - <https://github.com/rkyv/rkyv/blob/main/rkyv/src/api/high/mod.rs>
  - <https://github.com/rkyv/rkyv/blob/main/rkyv/src/util/alloc/arena.rs>
  - <https://github.com/rkyv/rkyv/blob/main/rkyv/src/util/mod.rs>
  - <https://github.com/rkyv/rkyv/blob/main/rkyv/examples/backwards_compat.rs>
  - <https://github.com/rkyv/rkyv/blob/main/.github/workflows/ci.yml>
  - <https://github.com/rkyv/rkyv/releases>
  - <https://github.com/rkyv/rkyv/commits/main>
  - <https://github.com/rkyv/rkyv/security/advisories>
  - <https://github.com/rkyv/rkyv/issues?q=label%3Abug>
  - <https://github.com/rkyv/rkyv/issues?q=label%3A%22known+issue%22>
  - <https://github.com/rkyv/rkyv/issues/542>
  - <https://github.com/rkyv/rkyv/issues/657>
  - <https://github.com/rkyv/rkyv/issues/663>
  - <https://github.com/rkyv/rkyv/issues/664>
  - <https://github.com/rkyv/rkyv/issues/685>
  - <https://github.com/rkyv/rkyv/issues/696>
  - <https://github.com/rkyv/rkyv/issues/697>
  - <https://rustsec.org/packages/rkyv.html>
  - <https://rustsec.org/advisories/RUSTSEC-2026-0233.html>
  - <https://rustsec.org/advisories/RUSTSEC-2026-0234.html>
  - <https://rustsec.org/advisories/RUSTSEC-2026-0235.html>
  - <https://crates.io/api/v1/crates/rkyv>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/README.md>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_rkyv.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/yandex/yaff>
  - <https://github.com/PeterRK/protocache>
  - <https://github.com/aeron-io/simple-binary-encoding>
  - <https://github.com/apache/fory>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/rkyv/rkyv`) · [data/wave4/enrich/raw/github_com_rkyv_rkyv.json](../../../data/wave4/enrich/raw/github_com_rkyv_rkyv.json) (enrichment confidence 0.88)

</details>
