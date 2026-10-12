# foldhash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Zlib` · 🟢 active

> Seeded folded-multiply Rust hasher for in-memory HashMaps; about 4.6x lower geometric-mean time per op than SipHash-1-3.

| | |
|---|---|
| **Beats** | SipHash-1-3 (Rust std::collections::HashMap's default hasher) |
| **Claimed result** | geometric mean of 6.21 (foldhash-f) vs 28.70 (siphash) on Xeon 8481c summary table; foldhash consistently faster than SipHash-1-3 across the full suite |
| **Workload** | Per-op time (hashonly/lookupmiss/lookuphit/setbuild) over \~18 key types (u32/u64/pairs/ipv4/ipv6/strings/uuids/byte strings) vs aHash, fxhash, SipHash-1-3. |
| **Metric** | throughput |
| **Hardware** | 2023 Apple M2, 2023 Intel Xeon Platinum 8481C |
| **Compiler and flags** | stable Rust 1.80.1, tested with and without `-C target-cpu=native` on the Intel machine |
| **Adoption** | 373 stars |
| **Last commit** | 2026-06-29 |
| **Links** | [repository](https://github.com/orlp/foldhash) · [benchmark](https://github.com/orlp/foldhash#performance) |

## Verdict

The author's Criterion suite times one hash, a lookup miss, a lookup hit, or an insert into a 1,000-entry set, in ns per op. It covers 16 key distributions and compares foldhash 0.1.x with SipHash-1-3 (std RandomState), aHash 0.8.11 and fxhash 0.2.1 on stable Rust 1.80.1. Geometric means were 6.21 vs 28.70 ns on a Xeon Platinum 8481C, 6.00 vs 29.49 with target-cpu=native, and 4.41 vs 21.94 on an Apple M2, with SipHash last on almost every row. The only outside run is rapidhash's use of the same suite, which gives foldhash-f 4.83 vs 22.17 for SipHash on an M1 Max.

## Use it when

- Rust HashMap/HashSet keyed by integers, tuples or short strings where SipHash-1-3 shows up in profiles. On the Xeon 8481C table, a u64 lookup hit is 3.04 ns against 12.65 ns, and an English-word lookup hit is 8.62 ns against 21.35 ns.
- Byte-string keys of 1 KB and up on builds without AES target features. Without target-cpu=native on the Xeon, hashing a 1 KB key takes 39.70 ns, against 86.00 ns for aHash and 280.74 ns for SipHash.
- Integer keys where only the high bits vary (IDs shifted left, aligned addresses), where FxHash collapses. On the Xeon, a u64hibits lookup hit is 3.05 ns for foldhash and 58.47 ns for fxhash.
- HyperLogLog, MinHash or other algorithms that need every output bit unbiased. Use foldhash::quality: the README says it passes SMHasher3 without failures, and on the Xeon it adds about 13% to the geometric mean (7.01 vs 6.21).
- no_std, embedded or dependency-averse crates. It has zero dependencies and declares Rust 1.60 as its MSRV.

## Skip it when

- Tables fed by an interactive attacker who can observe timing or iteration order. The README says it makes no HashDoS claim against such attackers, and its seeds come from ASLR addresses, the clock and an allocator address, not the OS RNG.
- Anything persisted, sent over the network or compared across machines. Output is unspecified across versions and platforms; FixedState gives different values on armv7 than on x86-64/aarch64 (issue #43), and byte loads use native endianness.
- Plain random integer keys when you control the key distribution. FxHash is faster there (u64 hash only: 0.67 vs 0.79 ns on the Xeon, 0.41 vs 0.60 ns on the M2).
- x86-64 builds with target-cpu=native that mostly hash medium or long strings. aHash's AES path wins there: 1 KB hash-only is 32.57 vs 40.56 ns, and URL-string lookups are 15.46 vs 17.42 ns.
- When you want the fastest Rust in-memory hasher. rapidhash's own run of this benchmark suite (Apple M1 Max) gives rapidhash-f a geometric mean of 4.29 against 4.83 for foldhash-f, with most of the gain on strings.

## How it is fast

Every mixing step is one folded multiply: a 64x64-&gt;128-bit multiply whose two halves are XORed together, with each operand first XORed with a secret. Integer writes are packed into a 128-bit sponge, so one multiply absorbs up to 128 bits of u8-u64 fields. Strings of 16 bytes or less take one multiply over overlapping head and tail words. Longer strings take an out-of-line path with 2, 4 or 6 independent lanes (above 128 or 256 bytes) to hide multiply latency. The per-map state is an 8-byte seed plus a zero-sized handle to a global seed, so a HashMap&lt;u32, u32&gt; is 40 bytes against 48 with std's RandomState.

## Compared with alternatives

Against aHash: foldhash has no dependencies, a smaller map (40 vs 64 bytes for HashMap&lt;u32, u32&gt;) and is faster unless you build with AES and hash long strings. Against rapidhash (Rust port): it is slightly slower on strings but is hashbrown's default and has a lower MSRV. Pick xxHash or wyhash whenever the hash must be stable across machines or versions, which foldhash explicitly is not.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (the std feature is on by default; nightly is optional) |
| **Minimum toolchain** | Rust 1.60 (rust-version in Cargo.toml for 0.2.0), edition 2021. The optional nightly feature needs a nightly compiler for hasher_prefixfree_extras. |
| **Platforms** | Any Rust target, including no_std with default features off. The native 64x64-&gt;128 multiply is used on 64-bit targets other than sparc64/wasm64, and on wasm with wide-arithmetic. Other targets use a four-multiply 32-bit approximation. Targets without 8-bit atomics fall back to a fixed global seed. |
| **Thread safety** | Not documented as a guarantee. In the source, hashers and BuildHashers are plain values (Clone, no longer Copy since 0.2.0). The global seed is set up once behind an atomic spin-lock, and per-map seeds come from a thread-local counter mixed with the stack address. |
| **Drop-in for the baseline** | partial — it is a drop-in BuildHasher for std HashMap/HashSet (swap the S parameter or import foldhash::HashMap). You lose std's keyed SipHash HashDoS protection, and HashMap::new() only compiles once HashMapExt is imported. |

## Gotchas

- Per-map seeds can repeat. Open issue #47 reports only 4 unique seeds across 1,024 fresh threads on an M1 Max, because OS thread reuse puts the stack address in the same place. The author called it legitimate; the fix PR #48 is still open.
- Some fixed key pairs collide far more often than a 64-bit hash should. With 8-byte keys, all-zero vs all-0xFF collide for about 1 in 2^26.6 random seeds in both the fast and quality variants (issue #50; the author accepted the finding). The same issue shows 1u8/1u32/1u64 and (7u32, 9u32) vs a u64 hashing identically, because finish() ignores the sponge length. The author treats cross-type collisions as out of scope.
- FixedState uses one seed for every map, which is trivially HashDoS-able. The docs warn it can go quadratic when you move entries from one map into another with the same fixed seed.
- The README numbers come from the 0.1.x code (Rust 1.80.1, aHash 0.8.11). 0.2.0 (2025-08) reworked short- and long-string hashing, and bench.rs now includes rapidhash, but the published tables were not re-run.

## Known shortcomings

- Rust-only. Headline gain is against SipHash-1-3 (Rust std HashMap default, a keyed DoS-resistant hash); foldhash is non-cryptographic with only minimal DoS resistance.
- README benchmark is from the 0.1.x era and was not re-run after 0.2.0; the only outside run of the same suite (by rapidhash) has rapidhash faster (geomean 4.29 vs 4.83). Seed comes from ASLR/time, not the OS RNG; open #47: only 4 of 1024 seeds unique on reused threads; #50: 8 zero bytes vs 8 0xFF bytes collide at \~2^-26.6. Loses to fxhash on plain integers and to aHash (AES) on long strings.

## Caveats and trade-offs

Baseline compared is Rust's own default hasher (SipHash-1-3), not xxHash/wyhash/CityHash/C++ std::hash; recorded honestly with baseline_in_list=false per rules.

Not DOS-resistant by cryptographic proof (still has fixed random state per-process); quality variant (foldhash-q) trades some speed for avalanche properties.

## Maintenance

Active but low-churn: 0.2.0 shipped 2025-08-23, the last commit was 2026-06-29, and 7 issues are open including the thread-seeding bug. Zlib-licensed with zero dependencies, about 606M crates.io downloads, and pulled in as hashbrown's default hasher.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Performance section runs foldhash against SipHash-1-3 (std::hash::RandomState) plus aHash and fxhash. The code is public in benches/bench.rs (criterion), with tools/extract-bench-results.py and tools/format-bench-results.py for the tables. The README states stable Rust 1.80.1, runs with and without -C target-cpu=native, and the CPUs (2023 Apple M2, Intel Xeon Platinum 8481C). The Xeon 8481c geometric mean is 6.21 for foldhash-f vs 28.70 for siphash, exactly as in the record.
- **Verifier notes:** Numbers verified. SipHash-1-3 is last on almost every row (avg_rank 4.97 of 5); units are ns per op. Other geometric means: 6.00 vs 29.49 on Xeon with native, 4.41 vs 21.94 on M2. The record's last_commit (2026-07-03) is the repo's pushed_at; the newest commit on master is 2026-06-29. The current bench.rs has since added rapidhash, so the code has moved on from the README run.
- **Fields the verifier corrected:** `last_commit`
- **Shortcomings recorded by:** README: Xeon geomean 6.21 vs SipHash 28.70 (Rust 1.80.1, benches/bench.rs).; rapidhash's run of foldhash's suite: rapidhash geomean 4.29 vs foldhash 4.83 (lower is faster).
- **Pages the verifier opened:**
  - <https://github.com/orlp/foldhash#performance>
  - <https://github.com/orlp/foldhash>
  - <https://raw.githubusercontent.com/orlp/foldhash/master/README.md>
  - <https://raw.githubusercontent.com/orlp/foldhash/master/Cargo.toml>
  - <https://raw.githubusercontent.com/orlp/foldhash/master/benches/bench.rs>
  - <https://api.github.com/repos/orlp/foldhash>
  - <https://api.github.com/repos/orlp/foldhash/commits?per_page=1>
  - <https://api.github.com/repos/orlp/foldhash/git/trees/master?recursive=1>
- **Sources the enricher read:**
  - <https://github.com/orlp/foldhash>
  - <https://github.com/orlp/foldhash#performance>
  - <https://github.com/orlp/foldhash/blob/master/README.md>
  - <https://github.com/orlp/foldhash/blob/master/Cargo.toml>
  - <https://github.com/orlp/foldhash/blob/master/src/lib.rs>
  - <https://github.com/orlp/foldhash/blob/master/src/fast.rs>
  - <https://github.com/orlp/foldhash/blob/master/src/quality.rs>
  - <https://github.com/orlp/foldhash/blob/master/src/seed.rs>
  - <https://github.com/orlp/foldhash/blob/master/src/convenience.rs>
  - <https://github.com/orlp/foldhash/blob/master/benches/bench.rs>
  - <https://api.github.com/repos/orlp/foldhash>
  - <https://api.github.com/repos/orlp/foldhash/git/trees/HEAD?recursive=1>
  - <https://api.github.com/repos/orlp/foldhash/commits?per_page=15>
  - <https://github.com/orlp/foldhash/issues>
  - <https://github.com/orlp/foldhash/pulls>
  - <https://github.com/orlp/foldhash/issues/50>
  - <https://github.com/orlp/foldhash/issues/47>
  - <https://github.com/orlp/foldhash/issues/45>
  - <https://github.com/orlp/foldhash/issues/43>
  - <https://github.com/orlp/foldhash/issues/41>
  - <https://gist.github.com/orlp/1271ad5b8b775c651cc55773888858eb>
  - <https://crates.io/api/v1/crates/foldhash>
  - <https://raw.githubusercontent.com/rust-lang/hashbrown/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/README.md>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/orlp/foldhash`) · [data/wave7/enrich/raw/github_com_orlp_foldhash.json](../../../data/wave7/enrich/raw/github_com_orlp_foldhash.json) (enrichment confidence 0.85)

</details>
