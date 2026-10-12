# nanoserde

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Zero-dependency Rust derive serializer whose schemaless binary format encodes \~3.8x and decodes \~1.6x faster than prost on logs.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | log dataset: nanoserde 0.2.1 serialize 190.59 us vs prost 0.14.4 731.23 us encode-only (\~3.8x) / 1.8883 ms populate+encode (\~9.9x); deserialize 1.6898 ms vs prost decode 2.6802 ms (\~1.6x) (ratios derived from page data). It also beats prost on the other datasets, e.g. mesh deserialize 824.47 us vs 10.253 ms. |
| **Workload** | Criterion micro-benchmark, 'log' dataset (HTTP request logs, many strings), serialize and deserialize a Rust struct via the rust_serialization_benchmark shootout. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9V74 80-Core Processor, 4 vCPUs, x86_64-unknown-linux-gnu |
| **Compiler and flags** | rustc 1.100.0-nightly (a36d05efa 2026-09-09), LLVM 23.1.1; Criterion via cargo bench, [profile.bench] lto = true |
| **Adoption** | 911 stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/not-fl3/nanoserde) · [benchmark](https://github.com/djkoloski/rust_serialization_benchmark) |

## Verdict

The numbers come from djkoloski's rust_serialization_benchmark: Criterion, run 2026-09-10, rustc 1.100.0-nightly with LLVM 23.1.1, lto = true, on a 4-vCPU AMD EPYC 9V74 VM. On the log set nanoserde 0.2.1 serialized in 190.59 us against prost 0.14.4's 731.23 us encode-only (\~3.8x; \~9.9x against populate+encode) and deserialized in 1.6898 ms against 2.6802 ms (\~1.6x). It also beat prost on mesh (1.3246 ms vs 5.8939 ms serialize, 824.47 us vs 10.253 ms deserialize), minecraft_savedata and mk48; all of these compare Rust crates, not C++ libprotobuf.

## Use it when

- Rust-to-Rust messages or save files where both sides build from the same struct definitions and you want 3.8-6.5x faster encoding than prost without a .proto step (log 190.59 us vs 731.23 us; minecraft_savedata 165.05 us vs 1.0006 ms; mk48 701.90 us vs 4.5619 ms).
- Game, wasm32 or small-binary projects where compile time and dependency count matter. The only dependency is nanoserde's own proc-macro crate, and CI builds wasm32-unknown-unknown, Windows (MSVC and GNU), macOS x86_64 and Linux.
- no_std + alloc targets: turning off the default std feature builds the crate as no_std, without the HashMap/HashSet/SystemTime impls.
- Records full of strings and structs (logs, player saves) where you also want JSON or RON from the same small dependency, and decode times around 1.5-1.7 ms on these datasets are acceptable.

## Skip it when

- Cross-language or long-lived data. Fields are positional with no tags, enum variants are u16 indices in declaration order, and the binary format does not support #[nserde(default)]. Adding, removing or reordering a field or variant makes previously written bytes unreadable.
- Bulk numeric arrays or byte blobs. Vec&lt;T&gt; is encoded element by element, with no memcpy path for Vec&lt;u8&gt; or Vec&lt;f32&gt;. On the mesh dataset it serializes in 1.3246 ms, against 147.88 us for wincode and 142.33 us for savefile, and deserializes in 824.47 us against about 144 us.
- Size-sensitive links. Fixed-width integers and 8-byte length prefixes make its log output 18% larger than prost's (1,045,784 vs 884,628 B) and about 1.5-1.9x larger than bitcode's on log and mk48 (703,710 B; 1,812,404 vs 971,318 B). Varint lengths (issue #97) would need a breaking major release.
- Untrusted input. Vec, HashSet and HashMap decoding call with_capacity(len) with a length read from the input before checking that enough bytes remain. A crafted length prefix can therefore force a huge allocation (abort) or a capacity-overflow panic. This comes from reading the source; no fuzzing or advisory was found.
- Zero-copy or streaming I/O. There is no borrowed (&str/&[u8]) decoding (the shootout marks Borrow as unsupported), and there is no io::Read/io::Write API: issue #23 is open, and the maintainers declined the change in #103.

## How it is fast

There is no intermediate data model like serde's Serializer/Visitor layer. Each derive is a hand-written token parser that emits straight-line code calling ser_bin/de_bin on every field in declaration order. The wire format is the plain struct layout: integers and floats are fixed-width little-endian bytes appended with extend_from_slice, strings and collections get a u64 length prefix, Option is a 1-byte tag, and enum variants are a u16 index. There are no field tags, no varints and no pass to compute the size first. Decoding is a bounds-checked cursor (offset: &mut usize) over the input slice. That removes protobuf's per-field tag and varint work, at the cost of larger output than varint formats and no schema evolution.

## Compared with alternatives

Pick nanoserde over wincode, savefile or bitcode when a dependency-free build tree and binary+JSON+RON in one crate matter more than the last 30-40% of speed. On log, wincode serializes in 137.05 us and deserializes in 1.4166 ms at the same output size (1,045,784 B), savefile serializes in 154.62 us, and bitcode is both faster (96.821 us / 1.1452 ms) and 33% smaller. For numeric arrays pick wincode or savefile; if you need schema evolution, stay on a tagged format.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none beyond its own nanoserde-derive proc-macro crate (no syn/quote/proc_macro2) |
| **Minimum toolchain** | Rust 1.81 (rust-version in Cargo.toml), edition 2021; CI tests the no_std configuration on nightly only |
| **Platforms** | any; the format is explicitly little-endian. CI builds x86_64 Linux, x86_64 Windows (MSVC and GNU), x86_64 macOS and wasm32-unknown-unknown, but runs tests only on x86_64 Linux |
| **Thread safety** | not documented; the binary API is stateless functions over &self and &[u8] with no global state (from source) |
| **Drop-in for the baseline** | no |

## Gotchas

- Decoding is lenient: any non-zero byte decodes as bool true, and any Option tag other than 1 decodes as None, so corrupted input can be accepted instead of rejected.
- usize and all lengths are written as u64. On 32-bit targets such as wasm32 the decoded value is cast with 'as usize', which silently truncates anything above u32::MAX.
- An unknown enum discriminant is reported at offset 0 rather than its real position. Derive parse failures show up as proc-macro panics (unimplemented!) instead of errors pointing at the source.
- crates.io is still at 0.2.1 (2025-03-22), the benchmarked version; master is at 0.2.2 and holds later fixes, such as the UnknownDiscriminant error and compile errors on unknown #[nserde] attributes, that are not published. nanoserde-derive is MIT-only while nanoserde is MIT OR Apache-2.0, and the published derive crate ships without a license file (issue #156).

## Known shortcomings

- The 9.9x serialize figure is against prost's populate+encode time; against encode-only it is about 3.8x. wincode is faster in the same table.
- No schema evolution (positional fields, enum variants as declaration-order u16), so not a protobuf replacement; output is 18% larger than prost on log. Vec&lt;T&gt; of numbers is encoded element by element, about 9x slower than wincode and savefile on mesh. Decoders preallocate lengths read from input before bounds checks (crafted input can abort or panic; source reading). Lenient bool/Option decoding; u64 lengths truncate on 32-bit targets. nanoserde-derive is MIT-only and ships without a licence file (#156).

## Caveats and trade-offs

The 9.9x serialize figure is vs prost populate+encode; vs prost encode-only it is \~3.8x. nanoserde's binary output size on log (1045784 bytes) matches wincode and bin-proto, not borsh (885780). Faster plain struct-layout encoders exist in the same table (wincode 137.05 us serialize / 1.4166 ms deserialize on log). This is a no-schema struct encoding, not a distinct schema language.

Zero-dependency, minimal-feature serde-alternative aimed at small binaries and fast compile time (originated for game/wasm projects), not schema-evolution-aware like protobuf.

## Maintenance

Actively maintained (commits through September 2026, 911 stars, \~1.7M crates.io downloads), dual MIT/Apache-2.0 and small enough to vendor. However, the last crates.io release is 0.2.1 from March 2025, and the maintainer says they prioritize 'simple + no dependency + safe over as fast as possible'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Same public shootout (djkoloski/rust_serialization_benchmark: benches/bench.rs, src/bench_nanoserde.rs vs src/bench_prost.rs) with prost in the same table; rustc 1.100.0-nightly/LLVM 23.1.1, [profile.bench] lto=true, and CPU AMD EPYC 9V74 are all stated, so A holds.
- **Verifier notes:** Numbers match nanoserde's and prost's rows. License is dual MIT OR Apache-2.0 (Cargo.toml plus LICENSE-MIT and LICENSE-APACHE); GitHub shows only Apache-2.0. 911 stars, last commit 2026-09-19, not fork/archived: rest of metadata correct.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/djkoloski/rust_serialization_benchmark>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/tree/master/src>
  - <https://github.com/not-fl3/nanoserde>
  - <https://github.com/not-fl3/nanoserde/blob/master/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/not-fl3/nanoserde>
  - <https://github.com/not-fl3/nanoserde/blob/master/README.md>
  - <https://github.com/not-fl3/nanoserde/blob/master/Cargo.toml>
  - <https://github.com/not-fl3/nanoserde/blob/master/derive/Cargo.toml>
  - <https://github.com/not-fl3/nanoserde/blob/master/src/lib.rs>
  - <https://github.com/not-fl3/nanoserde/blob/master/src/serde_bin.rs>
  - <https://github.com/not-fl3/nanoserde/blob/master/derive/src/serde_bin.rs>
  - <https://github.com/not-fl3/nanoserde/blob/master/derive/src/parse.rs>
  - <https://github.com/not-fl3/nanoserde/blob/master/.github/workflows/rust.yml>
  - <https://github.com/not-fl3/nanoserde/commits/master>
  - <https://github.com/not-fl3/nanoserde/issues>
  - <https://github.com/not-fl3/nanoserde/issues/97>
  - <https://github.com/not-fl3/nanoserde/issues/38>
  - <https://github.com/not-fl3/nanoserde/issues/103>
  - <https://github.com/not-fl3/nanoserde/issues/51>
  - <https://github.com/not-fl3/nanoserde/issues/156>
  - <https://github.com/not-fl3/nanoserde/issues/165>
  - <https://github.com/not-fl3/nanoserde/issues/79>
  - <https://github.com/djkoloski/rust_serialization_benchmark>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/Cargo.toml>
  - <https://github.com/djkoloski/rust_serialization_benchmark/blob/master/src/bench_nanoserde.rs>
  - <https://crates.io/api/v1/crates/nanoserde>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/not-fl3/nanoserde`) · [data/wave4/enrich/raw/github_com_not_fl3_nanoserde.json](../../../data/wave4/enrich/raw/github_com_not_fl3_nanoserde.json) (enrichment confidence 0.8)

</details>
