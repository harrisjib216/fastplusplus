# savefile

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust derive-based, versioned binary format for saving structs to disk; serializes 4.7-41x faster than prost.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | rust_serialization_benchmark README (last updated 2026-09-10), savefile 0.20.5 vs protobuf/prost 0.14.4. log: serialize 154.62 us vs prost encode 731.23 us (\~4.7x) or populate+encode 1.8883 ms (\~12.2x); deserialize 1.6639 ms vs prost decode 2.6802 ms (\~1.6x). mesh: serialize 142.33 us vs prost encode 5.8939 ms (\~41x) or populate+encode 6.3456 ms (\~44.6x); deserialize 142.38 us vs prost decode 10.253 ms (\~72x). minecraft_savedata: serialize 135.67 us vs encode 1.0006 ms (\~7.4x); deserialize 1.5679 ms vs decode 2.6936 ms (\~1.7x). mk48: serialize 581.79 us vs encode 4.5619 ms (\~7.8x); deserialize 2.3372 ms vs decode 6.7080 ms (\~2.9x). All ratios derived from page data. |
| **Workload** | Criterion micro-benchmark, 'log' and 'mesh' datasets, serialize/deserialize a Rust struct via the rust_serialization_benchmark shootout. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9V74 80-Core Processor, 4 vCPUs, x86_64-unknown-linux-gnu |
| **Compiler and flags** | rustc 1.100.0-nightly (a36d05efa 2026-09-09), LLVM 23.1.1; cargo bench (Criterion) with [profile.bench] lto = true (release opt-level) |
| **Adoption** | 109 stars |
| **Last commit** | 2026-07-13 |
| **Links** | [repository](https://github.com/avl/savefile) · [benchmark](https://github.com/djkoloski/rust_serialization_benchmark) |

## Verdict

Source: djkoloski/rust_serialization_benchmark, Criterion run of 2026-09-10 with rustc 1.100.0-nightly/LLVM 23.1.1 and lto = true, on a 4-vCPU AMD EPYC 9V74. It compares savefile 0.20.5 (save_noschema/load_noschema into a Vec/Cursor) with prost 0.14.4, the Rust protobuf crate, not C++ libprotobuf. Savefile serializes 4.7x (log), 7.4x (minecraft_savedata), 7.8x (mk48) and 41x (mesh) faster than prost encode. It deserializes 1.6x, 1.7x, 2.9x and 72x faster respectively. The mesh numbers come from memcpy of POD arrays and do not carry over to string-heavy data.

## Use it when

- Saving large in-memory Rust state to disk (game saves, caches, editor/project files) when newer builds must still load files written by older builds.
- Data dominated by Vec&lt;T&gt; of padding-free POD structs or primitives (meshes, point clouds, integer tables). These take the memcpy path: 6 MB mesh in \~142 us each way. A user in issue #125 reports it is 'orders of magnitude' faster than bitcode for gigabyte-scale Vec-of-integer data.
- The same Rust program writes and reads on little-endian hosts (x86-64, aarch64), and you want serialize throughput more than compact output.
- You want the schema stored with the data and checked on load (the default save/load), so a mismatch produces a detailed error rather than garbage.

## Skip it when

- Cross-language interchange, RPC or a network wire format. The format is Rust-only with no IDL, and the author says there will never be other backends. Use protobuf or one of the Rust wire formats instead.
- Untrusted input. The author has said files are treated as 'trusted' (issue #12), and length prefixes are unbounded unless you enable the `size_sanity_checks` feature (see gotchas).
- Size-sensitive data made of strings or small integers. Fixed-width ints and 64-bit length prefixes produce 1,045,800 B on the shootout's log dataset, against 884,628 B for prost and 703,710 B for bitcode.
- Zero-copy or borrowed deserialization. It cannot deserialize types that hold references (issue #18; shown as '†' in the shootout), so every String is allocated. Use rkyv for zero-copy access.
- Forward compatibility (an old binary reading a newer file), shared or cyclic object graphs, trait objects, or big-endian targets. None of these are supported. Objects reachable by two paths are written twice.

## How it is fast

The format mostly mirrors memory: fixed-width little-endian primitives and u64 length prefixes. There are no varints, field tags or field numbers. The derive macro generates a `Packed` impl that uses offset_of!/size_of to check whether a type's fields are contiguous, in declaration order and free of padding. If they are, a struct is written with a single write_all of its memory region. A Vec&lt;T&gt; of such a type is written as a length plus one memcpy of its buffer, and read back by allocating the buffer and calling read_exact into it. Types that fail the check use generated per-field code built on byteorder. That is why mesh (a Vec of f32 triangles) runs at close to memcpy speed, while string-heavy data is limited by String allocation.

## Compared with alternatives

On the same shootout, wincode posts nearly identical times and sizes and also supports borrowed decoding. bitcode gives much smaller output (703,710 B vs 1,045,800 B on log) and faster log deserialize, but is \~8.6x slower on mesh serialize (1.2265 ms vs 142.33 us). rkyv gives zero-copy access. Pick savefile when what you need is on-disk files with schema versioning built into the derive (added, removed and retyped fields, plus a stored schema that is checked on load) and memcpy-speed handling of large POD arrays.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | Always required: byteorder, memoffset. Enabled by default: savefile-derive (syn/quote/proc-macro2), indexmap, arrayvec, smallvec, bit-vec, bit-set, parking_lot, chrono. Optional: bzip2 (`compression`), ring + rand (`encryption`), serde, nalgebra, egui types. |
| **Minimum toolchain** | Rust 1.82 (rust-version in Cargo.toml; CI builds 1.82, stable and nightly). On nightly compilers, build.rs turns on the `nightly` feature, which uses specialization for better introspection. |
| **Platforms** | Any Rust target in principle. The format is little-endian. I found no endianness guard on the primitive Packed impls used by the memcpy fast path, and the bit-vec features deliberately fail to compile on big-endian, so treat big-endian as unsupported. |
| **Thread safety** | Not documented. The save/load functions take &mut Write/&mut Read and keep only per-call Serializer/Deserializer state; I found no global state. |
| **Drop-in for the baseline** | no |

## Gotchas

- The fast path is used only when a type has no padding at all, including trailing padding, and its fields sit in declaration order. repr(C) alone is not enough, and the docs say to add manual pad fields. Enums need #[repr(u8/u16/u32)] and variants of equal size. Otherwise savefile silently falls back to per-field code; #[savefile_require_fast] turns bad alignment into a compile error, but some other disqualifiers are only detected at runtime.
- Corrupt or hostile files are a real risk. In the packed Vec&lt;T&gt; path, `elem_size * num_elems` is computed without an overflow check and a failed allocation panics. Bytes are read raw into Vec&lt;bool&gt;/Vec&lt;char&gt; without validation, although a scalar char is validated. The optional `size_sanity_checks` feature caps strings and non-packed Vecs at 1,000,000.
- Versioning is manual. You bump one global version, tag every added or removed field, and keep removed fields as Removed&lt;T&gt;. The docs warn that 'If this is messed up, data corruption is likely.' save_noschema/load_noschema (the variant the benchmark uses) skip the schema check that would catch such a mismatch.
- The crate is pre-1.0 and has broken APIs and formats before: 0.17 needed an upgrade guide, and an 0.17 beta corrupted 0.16 files (issue #44, fixed before release). Before 0.20.3, save_file/save_file_compressed/save_file_noschema did not flush their BufWriter, so write errors could go unreported.

## Known shortcomings

- Treats files as trusted (author, #12): the packed Vec&lt;T&gt; path has no overflow check on elem_size\*num_elems, Vec&lt;bool&gt;/Vec&lt;char&gt; bytes are not validated, and length limits need the optional size_sanity_checks feature. The shootout used save_noschema/load_noschema, not the default schema-checking path. Big-endian effectively unsupported. wincode posts nearly identical times and sizes; savefile's distinguishing feature is built-in schema versioning.

## Caveats and trade-offs

Rust-only format, not wire-compatible or cross-language like protobuf. The baselines are Rust protobuf crates (prost 0.14.4; Google's protobuf 4.36.1 Rust crate is also on the page and is usually slower than prost), not C++ libprotobuf. The claim's log ratio uses prost 'populate + encode'; against plain encode the gain is \~4.7x. The mesh result (\~6 MB in \~142 us, close to memcpy speed) comes from savefile bulk-copying POD arrays, so the 41-72x mesh gain does not carry over to other data. On string-heavy data (log, minecraft_savedata) deserialize wins only \~1.6-1.7x.

Designed for save-game/disk persistence with schema-versioning support baked into the derive macro, not a network wire-format competitor to protobuf; not zero-copy.

## Maintenance

Active and maintained by its author: 0.20.5 was released 2026-07-13, with \~197k crates.io downloads and CI covering nightly, stable, Rust 1.82 and Miri. Cargo.toml declares a dual MIT/Apache-2.0 license, but the repo ships only LICENSE-MIT. The crate is pre-1.0 and has a history of breaking API and format changes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party shootout (djkoloski/rust_serialization_benchmark, code in benches/bench.rs + src/) whose README states rustc 1.100.0-nightly (a36d05efa 2026-09-09)/LLVM 23.1.1 and AMD EPYC 9V74. Cargo.toml [profile.bench] sets lto = true, so the flags are stated. savefile 0.20.5 and prost 0.14.4 (protobuf) rows both appear with the quoted numbers.
- **Verifier notes:** Every quoted number matches savefile's and prost's rows in the shootout README. I rewrote claimed_speedup to show encode-only and populate+encode side by side and to add the other two datasets, because the original picked the most favourable prost variant for the log dataset. Metadata checked with gh: MIT, 109 stars, not a fork, last commit 2026-07-13, active.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/djkoloski/rust_serialization_benchmark>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/avl/savefile>
- **Sources the enricher read:**
  - <https://github.com/avl/savefile>
  - <https://github.com/avl/savefile/blob/master/README.md>
  - <https://github.com/avl/savefile/blob/master/savefile/src/lib.rs>
  - <https://github.com/avl/savefile/blob/master/savefile-derive/src/lib.rs>
  - <https://github.com/avl/savefile/blob/master/savefile/Cargo.toml>
  - <https://github.com/avl/savefile/blob/master/savefile-derive/Cargo.toml>
  - <https://github.com/avl/savefile/blob/master/Cargo.toml>
  - <https://github.com/avl/savefile/blob/master/savefile/build.rs>
  - <https://github.com/avl/savefile/blob/master/.github/workflows/rust.yml>
  - <https://github.com/avl/savefile/blob/master/CHANGELOG.md>
  - <https://github.com/avl/savefile/blob/master/savefile-test/fuzz/fuzz_targets/fuzz_target_1.rs>
  - <https://github.com/avl/savefile/issues>
  - <https://github.com/avl/savefile/issues/12>
  - <https://github.com/avl/savefile/issues/25>
  - <https://github.com/avl/savefile/issues/44>
  - <https://github.com/avl/savefile/issues/76>
  - <https://github.com/avl/savefile/issues/125>
  - <https://github.com/avl/savefile/pulls>
  - <https://github.com/avl/savefile/commits/master>
  - <https://github.com/djkoloski/rust_serialization_benchmark>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_savefile.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/datasets/mesh/mod.rs>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://crates.io/api/v1/crates/savefile>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/avl/savefile`) · [data/wave4/enrich/raw/github_com_avl_savefile.json](../../../data/wave4/enrich/raw/github_com_avl_savefile.json) (enrichment confidence 0.82)

</details>
