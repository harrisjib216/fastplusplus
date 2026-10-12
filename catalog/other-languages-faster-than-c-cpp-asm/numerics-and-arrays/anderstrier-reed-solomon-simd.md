# reed-solomon-simd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT AND BSD-3-Clause` · 🟢 active

> Pure-Rust O(n log n) Leopard-RS erasure coder over GF(2^16) with runtime AVX2/SSSE3/Neon kernels; no measured C/C++ win.

| | |
|---|---|
| **Beats** | catid/leopard (C++) and Intel ISA-L (C) named by the lead but never compared; examples/quick-comparison.rs times reed-solomon-16, reed-solomon-erasure (built with the simd-accel feature, whose GF(2^8) multiply kernel is C SIMD code copied from NicolasT/reedsolomon and compiled through cc), reed-solomon-novelpoly and leopard-codec, but the README publishes no numbers for that run |
| **Claimed result** | No C or C++ comparison. Absolute README numbers (single core AVX2, AMD Ryzen 5 3600, MiB/s or GiB/s over original plus recovery shards): encode 32:32 10.237 GiB/s, 128:128 7.3891 GiB/s, 1024:1024 4.8495 GiB/s, 32768:32768 1.6049 GiB/s; decode (1% loss) 32:32 254.24 MiB/s, 1024:1024 1.3017 GiB/s. README says the crate 'is the fastest in all cases' against the Rust crates reed-solomon-16, reed-solomon-erasure, reed-solomon-novelpoly and leopard-codec on that Ryzen, except decoding with about 42 or fewer recovery shards. |
| **Workload** | Reed-Solomon encode and decode over GF(2^16) with 1024-byte shards, 32:32 up to 57344:8192 original:recovery shard counts, single core AVX2. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 3600 (Zen 2); README adds Apple M1 about the same (+-10%) |
| **Compiler and flags** | cargo bench main (criterion 0.7) and cargo run --release --example quick-comparison; runtime SIMD selection (AVX2, SSSE3, Neon, plain Rust fallback); rustc version and RUSTFLAGS unstated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 100 stars, 23 forks; crates.io 3.1.0, about 2.19M downloads (about 432k recent) |
| **Last commit** | 2025-10-14 |
| **Links** | [repository](https://github.com/AndersTrier/reed-solomon-simd) · [benchmark](https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/README.md) |

## Verdict

First-party criterion benchmark (cargo bench main) on one core of an AMD Ryzen 5 3600 with AVX2, 1024-byte shards, rustc version and flags unstated: encode 10.237 GiB/s at 32:32 falling to 1.6049 GiB/s at 32768:32768, decode with 1% loss 254 MiB/s at 32:32 and 1.30 GiB/s at 1024:1024, all counting original plus recovery bytes. No C or C++ library (Leopard-RS, ISA-L) was measured, so there is no ratio against a C/C++ baseline; the Rust-only 'fastest' claim has no published numbers.

## Use it when

- Rust services that need wide erasure codes (hundreds to tens of thousands of shards) where O(n\*k) GF(2^8) coders slow down sharply, e.g. data availability sampling, distributed storage or FEC over many packets.
- Single-core encode throughput matters: README reports 4.8 GiB/s at 1024:1024 and 10.2 GiB/s at 32:32 with 1024-byte shards on a Ryzen 5 3600 (counting original plus recovery bytes).
- You need more than 256 total shards, which GF(2^8) coders such as reed-solomon-erasure's default ReedSolomon8 or leopard-codec's GF(2^8) mode cannot address.
- x86-64 or AArch64 targets with runtime SIMD selection and a plain-Rust fallback elsewhere; no_std builds are supported since 3.1.0 by disabling the std feature.

## Skip it when

- Small configurations with about 42 or fewer recovery shards when decode speed dominates: the README says other Rust crates decode faster there, and decode throughput at 32:32 is only about 254 MiB/s against 10 GiB/s encode.
- Tiny payloads per process: a one-time table build (under 10 ms per the README) can outweigh the coding work.
- You need errors (corrupted shards) corrected, not just erasures: the crate trusts every shard it is given, so add a per-shard hash (CRC32C, xxHash) yourself; erasure-and-error decoding is an open issue (#20).
- You must interoperate with shards produced by Leopard-RS C++, ISA-L, Jerasure, Backblaze or reed-solomon-erasure: the codeword layout and field differ, and shards whose length is not a multiple of 64 bytes are only compatible from version 3.0.0 on.
- You need a measured advantage over a C or C++ library: no head-to-head with Leopard-RS or ISA-L exists, and the maintainer only expects rough parity with klauspost/reedsolomon's Leopard GF16 mode (Go).

## How it is fast

It implements the Leopard-RS scheme by Christopher Taylor: additive FFT and inverse FFT over GF(2^16) in the Lin-Chung-Han novel polynomial basis, which makes encode and decode O(n log n) in the shard count instead of the O(n\*k) matrix multiply of classic Vandermonde/Cauchy coders, with a fast Walsh-Hadamard transform for the erasure-locator step in decoding. Each 64-byte block of a shard is stored as 32 low bytes then 32 high bytes, so the GF(2^16) multiply-add maps onto PSHUFB/VPSHUFB (or Neon TBL) nibble lookups; the DefaultEngine picks AVX2, SSSE3, Neon or a plain-Rust NoSimd engine at runtime via cpufeatures. Version 3.0.1 claims up to 20% more AVX2 encode throughput from kernel tuning.

## Compared with alternatives

No erasure-coding entry sits in this category (the siblings are BLAS, ODE, FFT and vector-search kernels); against the catalogued klauspost/reedsolomon (Go, GF(2^8) matrix codes plus a Leopard GF16 mode) pick this crate for a pure-Rust dependency with no Go or C toolchain and shard counts in the thousands, and pick klauspost or ISA-L when you need AVX-512/GFNI kernels or small k+m codes with fast decode.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | fixedbitset, once_cell, and cpufeatures on x86, x86-64 and AArch64 (readme-rustdocifier at build time) |
| **Minimum toolchain** | Rust 1.82 (rust-version in Cargo.toml for 3.1.0), edition 2021 |
| **Platforms** | x86 and x86-64 (SSSE3 or AVX2 picked at runtime), AArch64 (Neon), any other target through the plain-Rust NoSimd engine; no AVX-512 or GFNI engine |
| **Thread safety** | Encoder, decoder, DefaultEngine, results and Error are Send and Sync (asserted in the crate's tests); one encoder or decoder instance is used from one thread at a time through &mut methods. |
| **Drop-in for the baseline** | no |

## Gotchas

- README throughput counts original plus recovery bytes (and missing shards for decode), following klauspost/reedsolomon's 'total shard size' convention, so 10.237 GiB/s at 32:32 is about 5.1 GiB/s of input data; halve the 1:1 rows before comparing with Leopard-RS's 'Input=' MB/s figures.
- The 'fastest in all cases' claim comes from examples/quick-comparison.rs, which times each encode and decode once with Instant (no warm-up, no repetition, cold caches and page faults included), times reed-solomon-simd's table init separately and outside encode while leopard-codec's lazy table build falls inside its first timed encode, and runs reed-solomon-erasure GF(2^8) and leopard-codec only up to 128:128; no output of that run is published.
- High-rate and low-rate codecs in the rate module are not interchangeable: data encoded with one must be decoded with the same rate (the crate's own algorithm.md notes they only appear compatible for a single chunk).
- src/algorithm.md is stale: it still says shards must be a multiple of 64 bytes (relaxed to even lengths in 3.0.0) and its rate table (about 75-176 MiB/s) predates the SIMD engines; trust the README table instead.

## Known shortcomings

- No C or C++ number anywhere: quick-comparison.rs runs only Rust crates and publishes no results; reed-solomon-erasure's simd-accel path calls a C SIMD kernel but uses a different algorithm. The crate is a fork of reed-solomon-16 (about 2.19M downloads, active).
- Enricher: examples/quick-comparison.rs behind the README's 'fastest in all cases' times each operation once with one Instant, no warm-up or repeats; its own table init is timed outside encode while leopard-codec's lands in its first timed encode; GF(2^8) rivals run only up to 128:128; no numbers are published. README GiB/s counts original plus recovery bytes, so 32:32 at 10.237 GiB/s is about 5.1 GiB/s of input; src/algorithm.md is stale. The maintainer expects parity with klauspost/reedsolomon's Leopard GF16 (issue #57).

## Caveats and trade-offs

Lead asked for a comparison with catid/leopard (C++) or ISA-L; none in the README, CHANGELOG or examples/quick-comparison.rs. catid/leopard's Benchmarks.md gives MB/s on an unstated 'few year old laptop' with 64 KB pieces, 128:128 Input=1964.98 MB/s encode, which cannot be compared with this crate's 1024-byte-shard Ryzen figures (different shard size, hardware and byte accounting; 'not very rigorous' by its author), so no ratio is derived. The 'fastest' claim is first-party, covers Rust crates only and has no published numbers; the closest thing to a C baseline in it is reed-solomon-erasure with simd-accel (C SIMD GF(2^8) multiply inside a Rust O(n\*k) matrix codec, a different algorithm from this crate's O(n log n) GF(2^16) FFT), so even a run of it would not be a like-for-like language comparison. README says the crate is a fork of Markus Laire's reed-solomon-16 crate, itself based on Leopard-RS (BSD-3-Clause code carried in the LICENSE); not a GitHub fork. One-time table initialisation under 10 ms can dominate tiny inputs; decoding with about 42 or fewer recovery shards is not the fastest even among the Rust crates. A web search found no head-to-head with Leopard C++ or ISA-L. Not a language-level claim: the speed comes from the FFT-based Leopard algorithm plus runtime-selected AVX2/SSSE3/Neon kernels.

O(n log n) Leopard-RS algorithm in GF(2^16): 1 to 32768 original and recovery shards (up to 65535 with limits), shard length must be even; no error detection inside shards; unsafe only for the SSSE3, AVX2 and Neon engines; a fork of reed-solomon-16 by Markus Laire, itself based on catid/leopard (BSD-3-Clause portion).

## Maintenance

Maintained at a slow pace (v3.1.0 on 2025-10-14, last commit that day, issues #71 and #77 open), MIT AND BSD-3-Clause, about 2.19M crates.io downloads; easy to adopt as a crate, but the catalogue entry stays at tier D because the only harness that names competitors is a single-shot timing run with uneven table-init accounting and no published numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The README benchmark table (single core AVX2, Ryzen 5 3600, 1024-byte shards) gives only absolute throughput for this crate; the 'fastest in all cases' statement covers Rust crates run by examples/quick-comparison.rs and publishes no numbers, and no C or C++ (Leopard-RS, ISA-L) figure exists anywhere opened, so there is no measured win over a C/C++ baseline.
- **Verifier notes:** Real, widely used crate (about 2.19M crates.io downloads) but no measured C/C++ comparison; keep at D with shortcoming 'no C or C++ baseline measured; fastest claim covers Rust crates only, unpublished'. Metadata checked: MIT AND BSD-3-Clause (Cargo.toml and LICENSE), last commit 2025-10-14 (v3.1.0), active.
- **Fields the verifier corrected:** `baseline`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-112 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/examples/quick-comparison.rs>
  - <https://github.com/AndersTrier/reed-solomon-simd>
  - <https://github.com/AndersTrier/reed-solomon-simd/commits>
  - <https://raw.githubusercontent.com/rust-rse/reed-solomon-erasure/HEAD/README.md>
  - <https://crates.io/api/v1/crates/reed-solomon-simd>
  - <https://crates.io/api/v1/crates/leopard-codec>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/benches/benchmarks.rs>
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/examples/quick-comparison.rs>
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/src/algorithm.md>
  - <https://raw.githubusercontent.com/AndersTrier/reed-solomon-simd/HEAD/src/engine.rs>
  - <https://github.com/AndersTrier/reed-solomon-simd/issues?q=is%3Aissue>
  - <https://github.com/AndersTrier/reed-solomon-simd/issues/57>
  - <https://github.com/AndersTrier/reed-solomon-simd/issues/14>
  - <https://github.com/AndersTrier/reed-solomon-simd/commits>
  - <https://crates.io/api/v1/crates/reed-solomon-simd>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/anderstrier/reed-solomon-simd`) · [data/wave14/enrich/raw/github_com_anderstrier_reed_solomon_simd.json](../../../data/wave14/enrich/raw/github_com_anderstrier_reed_solomon_simd.json) (enrichment confidence 0.85)

</details>
