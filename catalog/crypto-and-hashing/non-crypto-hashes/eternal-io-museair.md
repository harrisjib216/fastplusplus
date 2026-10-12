# MuseAir

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT OR Apache-2.0 for the Rust crate (Cargo.toml, README); CC0-1.0 for the algorithm and the museair.cpp reference (README)` · 🟢 active

> Portable wide-multiply Rust hash: about 1.9-2.2x XXH64 and 1.1-1.3x wyhash on bulk data; XXH3 is faster in SMHasher3.

| | |
|---|---|
| **Beats** | xxHash (XxHash64) and wyhash |
| **Claimed result** | Bulk throughput at 4.0 GHz on a Ryzen 7 5700G (GiB/s, 256 KiB input): MuseAir-BFast 32.333 and MuseAir 28.055 vs xxh-64 14.760 and wyhash-v4.2 24.667. That is \~2.19x / \~1.90x vs XXH64 and \~1.31x / \~1.14x vs wyhash (derived from page data); rapidhash-v3 reaches 29.839. The small-key latency data (plot-bench-smallkeys.py) has no XXH64 or wyhash; there, standard MuseAir is slower than rapidhash-v3 for 0-16-byte keys (e.g. 3.7631 vs 2.7634 ns at 0 B) and faster for 17-32 bytes. Independent SMHasher3 (MuseAir v0.3): MuseAir.bfast 8.64 and MuseAir 7.19 bytes/cycle bulk vs XXH-64 3.99 and wyhash 6.98, and 26.28 / 28.45 vs 52.60 / 29.31 avg cycles for 1-32 B. |
| **Workload** | Criterion benches (benches/hashes.rs). Bulk throughput from 256 B to 256 KiB vs wyhash-v4.2(.protected), rapidhash-v3(.protected), komihash-v5.10, seahash-v4 and xxh-64 (twox-hash 2.1.2 XxHash64). Small-key latency from 0 to 32 B vs rapidhash-v3(.protected) and rust-fxhash64 only. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5700G desktop, frequency locked at 4.0 GHz |
| **Adoption** | 94 stars |
| **Last commit** | 2026-07-17 |
| **Links** | [repository](https://github.com/eternal-io/museair) · [benchmark](https://github.com/eternal-io/museair/blob/master/results/plot-bench-bulkdata.py) |

## Verdict

The first-party Criterion bench (benches/hashes.rs) ran on a Ryzen 7 5700G locked at 4.0 GHz, with no rustc version stated and no custom Cargo profile (so no LTO). At 256 KiB it measured BFast at 32.33 and Standard at 28.06 GiB/s, against 14.76 for XXH64 via the Rust twox-hash 2.1.2 crate (about 2.2x and 1.9x) and 24.67 for wyhash-v4.2 via wyhash-final4 (about 1.31x and 1.14x). At 256 B the figures are 18.7 and 16.9 against 10.7 and 17.7. Independent SMHasher3 data for v0.3 (hardware not stated in its summary) points the same way, 8.64/7.19 bytes/cycle against 3.99 for XXH-64 and 6.98 for wyhash, but has XXH3-64 at 12.82.

## Use it when

- Persisted checksums or content keys that must match across platforms (file formats, protocols, dedup) where you would otherwise use XXH64. At 256 KiB on a Ryzen 7 5700G at 4.0 GHz it runs 28.06 (Standard) or 32.33 (BFast) GiB/s against 14.76 for XXH64.
- Portable or no_std Rust targets where AES/SIMD hashes (gxhash, aHash's AES path) are not an option, or where you want compile-time hashing (const fn) and zero unsafe code.
- Keys of 17-32 bytes. There BFast takes about 4.27-4.52 ns against about 5.3 ns for rapidhash-v3 in the first-party bench, and SMHasher3 (v0.3) puts its 1-32 byte average at 26.28 cycles against 30.69 for XXH3-64 and 29.31 for wyhash.
- Checksums with a public or fixed seed, where blinding multiplication (a zero multiplicand wiping state) is a concern with wyhash/rapidhash. The Standard variant is designed to be immune, and BFast limits the damage to the most recent 8 bytes.
- Cheap 128-bit output: MuseAir-128 matches the 64-bit version in bulk (28.07 vs 28.06 GiB/s at 256 KiB).

## Skip it when

- Hash tables fed untrusted keys on servers. There is a single seed and no secret, and the author says it is unsuitable for direct server use and points to foldhash/aHash (Rust) or wyhash/rapidhash (C/C++). A fixed 32-byte pair collides for about 2^-17.45 of random seeds on v2 (issue #4), and the author has said he will not investigate v2 further.
- Maximum bulk throughput on SIMD/AES hardware. SMHasher3 has XXH3-64 at 12.82 bytes/cycle and gxhash-64 at 19.14, against 8.64 for MuseAir-BFast (v0.3).
- Tiny keys (16 bytes or less). rapidhash-v3 takes 2.76-3.02 ns there, against 3.26-3.76 ns for MuseAir and 3.01-3.51 ns for BFast.
- C/C++ projects. There is no standalone C/C++ library: museair.cpp is an SMHasher3 plug-in that needs SMHasher3's headers, and the third-party museair-cpp port predates v2.
- Anything that needs a track record. It has 94 stars, about 24k downloads and a single author; the algorithm went v0.3 -&gt; v1 (3 days) -&gt; v2 in July 2026, and every crate version before 0.6.0 is yanked.

## How it is fast

The core primitive is the 64x64-&gt;128-bit wide multiply used by wyhash, rapidhash and komihash, arranged as a 'circular accumulator'. Six u64 state words consume 96-byte chunks: each adjacent pair of words absorbs two input words and is multiplied, and the high half of each product feeds the next word, wrapping around. That costs one multiply and about three XORs per 16 bytes, and the six multiplies are independent enough for instruction-level parallelism without splitting the input into separate lanes. BFast overwrites state words with the product halves and unrolls two chunks per iteration. Standard subtracts the products into the state instead, so a zero product cannot erase it, at a cost of about 13% bulk speed (28.06 vs 32.33 GiB/s). Inputs of 32 bytes or less take a branch-light short path (three to five multiplies for the 64-bit hash).

## Compared with alternatives

Pick MuseAir over wyhash or rapidhash when you need a portable, persisted checksum with a public seed: Standard is built to resist blinding multiplication, and BFast still edges rapidhash-v3 in bulk (32.33 vs 29.84 GiB/s at 256 KiB). Choose xxHash (XXH3) or gxhash for raw bulk speed on SIMD/AES hardware and foldhash or aHash for Rust HashMaps. If you want MuseAir itself, use this crate rather than the museair-cpp port, which was last pushed in Feb 2026, before v2 existed.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (the default std feature is optional) |
| **Minimum toolchain** | Rust 1.77.0 (declared rust-version; MSRV bumps are treated as breaking changes) |
| **Platforms** | any Rust target; pure scalar code with no target features. Performance assumes a fast 64x64-&gt;128 multiply ('most 64-bit architectures'); 32-bit performance is not documented. |
| **Thread safety** | Not documented. The crate is #![forbid(unsafe_code)], the one-shot functions are pure const fns, and the incremental hashers are plain Clone structs with no shared state. |
| **Drop-in for the baseline** | partial — it replaces XXH64/wyhash one-shot and streaming calls (seeded byte slice in, u64/u128 out, streaming equals one-shot), but hash values differ and it is Rust-only. It provides no BuildHasher for std HashMap: CommonHasher implements Default but not core::hash::Hasher. |

## Gotchas

- Only algorithm v2 (crate 0.6.0, 2026-07-13) is supported. The SMHasher3 upstream entry that most people cite (250/250 pass) measures the deprecated v0.3, which has seed-independent collisions with probability 1 (#3, #4). The 252/252 SMHasher3 pass for v2 comes from the author's own logs in results/.
- 64-bit bfast::hash with a fixed seed: for 9-16 byte inputs there is always a fixed 8-byte prefix that makes bytes 9-16 irrelevant. The README says to use bfast::hash128_folded instead.
- The 64-bit seed is spread into the long-input state by masking (seed & 0xAAAA..., seed & 0x5555...) rather than mixed in. orlp called this weak against side-channel seed recovery (#3), and a 40-byte pair collides for all 2^32 seeds whose 0xAAAA... bits are zero (#4).
- The docs note that the incremental Hasher is slower than in-memory hashers when used behind std's Hasher trait, and you must write your own BuildHasher to use it in a HashMap.

## Known shortcomings

- Small-key benchmark omits XXH64 and wyhash; SMHasher3 tested v0.3, not current v2. Numbers are in plot-bench-\*.py scripts: BFast 32.33 / Std 28.06 GiB/s vs wyhash 24.67, XXH64 14.76.
- XXH3 beats it in SMHasher3 bulk (12.82 vs 8.64 bytes/cycle); slower than rapidhash at 16 bytes and below. SMHasher3 upstream carries deprecated v0.3, which has probability-1 seed-independent collisions (#3/#4); the v2 pass is self-run only, and a fixed 32-byte pair still collides for \~2^-17.45 of seeds; author says no further hardening. No BuildHasher; no standalone C/C++ (museair.cpp is an SMHasher3 plug-in). rustc/flags not stated.

## Caveats and trade-offs

There are no LICENSE files in the repo, so GitHub reports none; licensing is declared in the README and Cargo.toml. The CC0 part has no patent grant. The rustc version and flags for the first-party bench are not stated. The numbers are plain text in results/plot-bench-\*.py, not only in the PNGs. The independent SMHasher3 entries test MuseAir v0.3, not the current v2 algorithm. XXH3-64 is faster in bulk on SMHasher3 (12.82 bytes/cycle); the baseline here is legacy XXH64, benchmarked via a Rust port.

No secondary secret/keying (only an initial seed), so less DOS-resistant than keyed hashes; author recommends wyhash/rapidhash instead for pure C/C++ use.

## Maintenance

The algorithm was finalized as v2 in July 2026 (last commit 2026-07-17), with output promised stable but no further hardening planned. The crate is dual MIT/Apache-2.0 (declared, with no LICENSE files in the repo) and the algorithm and museair.cpp are CC0. It is a single \~1,200-line file with zero dependencies, easy to vendor; 5 crates depend on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The first-party Criterion bench (benches/hashes.rs) is public and the CPU is stated (Ryzen 7 5700G locked at 4.0 GHz), but the rustc version and flags are not, so it is C on its own. B holds because the independent SMHasher3 results show MuseAir.bfast/MuseAir at 8.64/7.19 bytes/cycle bulk vs XXH-64 at 3.99 and wyhash at 6.98 (MuseAir v0.3 there, not the current v2).
- **Verifier notes:** The record's benchmark_url returned 404 because the default branch is master, not main. The claim that 'exact ratios are only visible in chart images' is wrong: the plotting scripts embed the numbers as text. Last commit (2026-07-17), stars (94) and hardware all check out.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `license`, `usability`, `caveats`
- **Shortcomings recorded by:** plot-bench scripts: BFast 32.33, Std 28.06 GiB/s vs wyhash 24.67, XXH-64 14.76 (bulk).; SMHasher3: MuseAir 8.64 vs XXH3 12.82 bytes/cycle bulk.
- **Pages the verifier opened:**
  - <https://github.com/eternal-io/museair>
  - <https://github.com/eternal-io/museair/blob/main/benches/hashes.rs>
  - <https://github.com/eternal-io/museair/blob/master/benches/hashes.rs>
  - <https://github.com/eternal-io/museair/blob/master/results/plot-bench-bulkdata.py>
  - <https://github.com/eternal-io/museair/blob/master/results/plot-bench-smallkeys.py>
  - <https://github.com/eternal-io/museair/blob/master/results/extract.py>
  - <https://github.com/eternal-io/museair/blob/master/results/v2_64b.log>
  - <https://github.com/eternal-io/museair/blob/master/Cargo.toml>
  - <https://github.com/eternal-io/museair/blob/master/CHANGELOG.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/SpeedAll.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/MuseAir.txt>
- **Sources the enricher read:**
  - <https://github.com/eternal-io/museair>
  - <https://github.com/eternal-io/museair/blob/master/README.md>
  - <https://github.com/eternal-io/museair/blob/master/CRATES.IO-README.md>
  - <https://github.com/eternal-io/museair/blob/master/Cargo.toml>
  - <https://github.com/eternal-io/museair/blob/master/CHANGELOG.md>
  - <https://github.com/eternal-io/museair/blob/master/src/lib.rs>
  - <https://github.com/eternal-io/museair/blob/master/museair.cpp>
  - <https://github.com/eternal-io/museair/blob/master/benches/hashes.rs>
  - <https://github.com/eternal-io/museair/blob/master/results/plot-bench-bulkdata.py>
  - <https://github.com/eternal-io/museair/blob/master/results/plot-bench-smallkeys.py>
  - <https://github.com/eternal-io/museair/blob/master/results/extract.py>
  - <https://github.com/eternal-io/museair/blob/master/results/v2_64b.log>
  - <https://github.com/eternal-io/museair/blob/master/results/v2_bfast_64b.log>
  - <https://github.com/eternal-io/museair/commits/master>
  - <https://github.com/eternal-io/museair/tags>
  - <https://github.com/eternal-io/museair/issues>
  - <https://github.com/eternal-io/museair/issues/2>
  - <https://github.com/eternal-io/museair/issues/3>
  - <https://github.com/eternal-io/museair/issues/4>
  - <https://crates.io/api/v1/crates/museair>
  - <https://crates.io/api/v1/crates/museair/reverse_dependencies>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/MuseAir.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/eternal-io/museair`) · [data/wave7/enrich/raw/github_com_eternal_io_museair.json](../../../data/wave7/enrich/raw/github_com_eternal_io_museair.json) (enrichment confidence 0.8)

</details>
