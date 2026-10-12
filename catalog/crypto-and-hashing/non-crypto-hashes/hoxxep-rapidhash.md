# rapidhash (Rust port)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust rapidhash (wyhash successor): portable 64-bit hasher, faster than XXH64/wyhash and faster than XXH3 up to about 4 KB inputs.

| | |
|---|---|
| **Beats** | xxHash (XXH64, XXH3-64, via the Rust twox-hash 2.1.1 crate) and wyhash (Rust wyhash crate 0.6.0) |
| **Claimed result** | README: 'significant throughput improvement over wyhash and foldhash'; 'places second to gxhash on some benchmarks'. Raw-throughput charts, derived from page data (SVG chart geometry), Xeon 8488c portable: u64 \~1166 M items/s rapidhash-f vs \~1133 wyhash, \~739 xxhash64, \~48 xxhash3_64 (Hasher trait). 4 KB: \~30.5 vs \~25.0 GB/s (xxhash3_64). 64 KB: \~31.6 vs \~32.2 GB/s (xxhash3_64 slightly ahead), \~15.0 xxhash64, \~19.3 wyhash. On AMD EPYC 9R14, xxhash3_64 beats rapidhash-f from 4 KB up (\~36.4 vs \~30.1 GB/s at 4 KB; \~51.4 vs \~31.1 GB/s at 64 KB). Rapidhash leads xxhash3_64 on M1 Max at 64 KB (\~45.9 vs \~36.8 GB/s) and beats xxhash64 and wyhash everywhere. |
| **Workload** | Raw hashing throughput vs input size (2 B to 4 KB, 64 KB, u64) across rapidhash-f/q, xxhash3_64, xxhash64, wyhash, foldhash, metrohash, rustc-hash, ahash, t1ha, farmhash, seahash, highwayhash, fxhash, SipHash default and gxhash (native only), all through std::hash::BuildHasher/Hasher. Plus the foldhash suite (hashonly/lookupmiss/lookuphit/setbuild on u32/u64/pairs/ipv4/ipv6/strings/accesslog/kilobyte blobs) vs foldhash/fxhash/ahash/siphash/gxhash. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max, AWS Graviton3, AMD EPYC 9R14, Intel Xeon 8488c (separate runs, each stated) |
| **Compiler and flags** | rustc (version not stated) via cargo criterion; workspace [profile.bench] opt-level=3, lto="fat", codegen-units=1, incremental=false; portable runs without RUSTFLAGS, native runs with RUSTFLAGS="-C target-cpu=native" (docs/run_benchmarks.sh) |
| **Adoption** | 278 stars; used by Fuchsia OS, Turso DB, metrics-rs, alloy-primitives |
| **Last commit** | 2026-07-03 |
| **Links** | [repository](https://github.com/hoxxep/rapidhash) · [benchmark](https://github.com/hoxxep/rapidhash/blob/master/docs/bench_hash_x86_64_intel_xeon_8488c.svg) |

## Verdict

The author ran cargo criterion benchmarks (opt-level 3, fat LTO, codegen-units=1, rustc version not stated), portable and with target-cpu=native, on M1 Max, Graviton3, EPYC 9R14 and Xeon 8488C, against Rust crates (twox-hash XXH3-64/XXH64 driven through the Hasher trait, wyhash, foldhash, gxhash, and others). The SVG-derived Xeon 8488C portable figures, which are approximate, are about 30.5 vs 25.0 GB/s over XXH3-64 at 4 KB and about 31.6 vs 32.2 at 64 KB, while XXH3 wins from 4 KB up on EPYC 9R14. The foldhash-suite geometric mean is 4.52 vs 4.95 for foldhash-f and 20.24 for SipHash.

## Use it when

- HashMap/HashSet keys that are short strings, UUIDs, URLs or mixed structs. In the Xeon 8488C foldhash suite, hash-only strenglishword costs 1.75 vs 3.54 for foldhash-f and 9.51 for SipHash (lower is better).
- Replacing Rust's default SipHash-1-3 when you only need minimal HashDoS resistance: suite geometric mean 4.52 vs 20.24 for SipHash on Xeon 8488C (portable build).
- Libraries and apps that must build on any target without AES-NI/NEON or target-cpu flags (x86-64, aarch64, 32-bit, wasm, no_std), where gxhash will not compile.
- Stable, cross-language digests (for example, Rust and C++ services agreeing on a key hash) via `rapidhash::v3`, including streaming and `Read`-based file hashing.
- Input sizes from a few bytes to about 4 KB, where it beats the twox-hash XXH3-64 and XXH64 and wyhash crates in the author's charts.

## Skip it when

- Bulk hashing of large buffers on x86, especially AMD. In the author's own EPYC 9R14 chart, XXH3-64 wins from 4 KB up (about 51.4 vs 31.1 GB/s at 64 KB), and on Xeon 8488C the two tie at 64 KB. Use XXH3 or gxhash for checksumming large blobs.
- Keys chosen by an attacker who can observe outputs or timings. The README calls it only 'minimally DoS resistant', and seed-independent collisions can be built for inputs over 16 bytes when the secrets are known, which is the case for C++-compatible default secrets. Use SipHash there.
- Anything that persists, shares or compares RapidHasher/RandomState outputs across processes, platforms or crate versions. That output may change in minor releases, and 32-bit targets take a different multiply path.
- Pure small-integer keys where FxHash is acceptable: fxhash is faster on u32/u64 hash-only (0.53 vs 0.66). But fxhash falls apart on high-bit-only u64 keys (46.99 vs 2.15 lookup-hit), so rapidhash is the safer default.
- Cryptographic uses of any kind (MACs, content addressing against adversaries, signatures).

## How it is fast

The core step is the wyhash-family folded multiply (MUM): a 64x64-&gt;128-bit multiply whose low and high halves are XORed (`rapid_mix`), one per 16 input bytes. Inputs of 16 bytes or less take two overlapping unaligned reads and a single multiply-finish. Inputs of 17-48 bytes stay on a short path. Inputs over 400 bytes go to an out-of-line cold path that runs 7 independent multiply lanes over 224-byte blocks for instruction-level parallelism. The Rust hasher also buffers integer writes in a 128-bit 'sponge', a construction borrowed from foldhash, so a tuple of small ints costs one mix. It relies on `#[inline(always)]` hot paths, `#[cold]`/`#[inline(never)]` long paths and bounds-check elision.

## Compared with alternatives

Over foldhash when string-heavy keys dominate (roughly 2x on short strings in the suite) or when you also need stable/streaming hashes. Over gxhash when you cannot guarantee AES instructions or target-cpu=native. Over aHash when you want portable output (suite geomean 4.52 vs 6.33). Over wyhash, whose mixing it shares, because it is faster on medium and large inputs (about 31.6 vs 19.3 GB/s at 64 KB on Xeon 8488C). Prefer xxHash XXH3 for multi-KB bulk hashing on x86.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rustversion (always); optional getrandom 0.3/0.4 (getrandom_03/getrandom_04 features) and rand_core 0.9 (deprecated rng feature) |
| **Minimum toolchain** | Rust 1.71.0 (MSRV); optional `nightly` feature for write_str/likely hints |
| **Platforms** | any. no_std capable and needs no SIMD/AES. Tuned for x86-64 and aarch64. 32-bit and wasm use an XOR-approximated 128-bit multiply for the in-memory hasher; wasm uses a 'COMPACT' loop. |
| **Thread safety** | Not documented explicitly. RapidHasher is a small Copy value (seed, &secrets, u128 sponge) with no shared mutable state. Under std, RandomState seeding uses a thread-local counter; v4.5.0/4.5.1 fixed duplicate seeds across recycled thread stacks and on std-without-atomics targets. |
| **Drop-in for the baseline** | partial — as a HashMap BuildHasher it replaces twox-hash's BuildHasherDefault&lt;XxHash3_64/XxHash64&gt; or wyhash's builder with a one-line type change, but it is a different algorithm: it cannot reproduce stored XXH3/XXH64 digests or interoperate with C xxHash. |

## Gotchas

- Two output contracts: only `rapidhash::v1/v2/v3` functions are guaranteed stable (and C++-compatible only with `RapidSecrets::seed_cpp`/DEFAULT_RAPID_SECRETS); `fast`/`quality` hashers may change output in any minor release.
- `fast::` skips the final avalanche mix. Use `quality::` when statistical quality matters, such as HyperLogLog, MinHash or low-bit bucketing.
- Without the `std` feature, RandomState seeds only from the stack address (ASLR). On wasm32-unknown-unknown, HashDoS resistance needs `getrandom_04` plus getrandom's wasm_js backend.
- 4.0.0 changed rapidhash_v3 micro/nano output for 5-7 byte inputs, following the C++ V3 re-release. Hashes persisted by 3.x for those lengths do not match.

## Known shortcomings

- No rustc version or flags stated; figures read from SVG charts are approximate. Baselines are Rust ports (twox-hash, wyhash crate), not the C originals. XXH3 wins large inputs on x86 (EPYC 64 KB: \~51 vs \~31 GB/s; Xeon about a tie).
- Only minimal DoS resistance: collisions are constructible when the secrets are known. The `fast`/`quality` hasher outputs may change between minor versions and across platforms; only the v1/v2/v3 algorithms are stable. XXH3 baseline is used through Rust's Hasher trait.

## Caveats and trade-offs

The linked .txt tables only compare against foldhash/fxhash/ahash/siphash; the xxHash and wyhash comparison is only in the SVG charts. The baselines are Rust ports (twox-hash, wyhash crate), not reference C xxHash. XXH3 is driven through the streaming Hasher trait, which inflates its small-input cost. XXH3 matches or beats rapidhash on large inputs on x86 (EPYC 9R14 from 4 KB up; Xeon 8488c at 64 KB). No rustc version is stated. Crate is dual-licensed MIT OR Apache-2.0 (GitHub shows only Apache-2.0).

Rust-only; portable (no AES/vector requirement) unlike gxhash which edges it out but needs AES-NI/NEON.

## Maintenance

Actively maintained: v4.5.1 released 2026-07-03, about 39.5M crates.io downloads (23.5M recent), fuzzed and cross-tested against the C++ reference. It is dual MIT/Apache-2.0 and a one-maintainer project, with a planned 5.0 that removes deprecated features and `Copy` on state types.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The benchmark code is public: rapidhash-bench/benches/bench/basic.rs (twox_hash::XxHash64 and XxHash3_64, and the wyhash crate), realworld/main.rs, docs/run_benchmarks.sh and docs/generate_charts.py. Flags are stated: the workspace [profile.bench] sets opt-level=3, lto=fat and codegen-units=1, and native runs add RUSTFLAGS=-C target-cpu=native. The CPUs are named. No rustc version is stated anywhere in the repo, so this is first-party with partial methodology: C, not A.
- **Verifier notes:** The original benchmark_url (Xeon 8488c .txt) has no xxHash or wyhash column. The corrected URL (the matching SVG) does compare against them, so page_compares_against_baseline is judged on the SVG. The SVG has no &lt;text&gt; glyphs; I read the values from the matplotlib bar/line geometry against the axis ticks, so they are approximate. 'Beats xxhash64/xxhash3_64' is overstated: it holds for small and medium inputs and for xxhash64, but XXH3 wins on large inputs on AMD. Stars 278 and the Fuchsia/Turso/metrics/alloy users are confirmed on the README.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `license`, `last_commit`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/hoxxep/rapidhash/blob/master/docs/bench_hash_x86_64_intel_xeon_8488c.txt>
  - <https://github.com/hoxxep/rapidhash/blob/master/docs/bench_hash_x86_64_intel_xeon_8488c.svg>
  - <https://github.com/hoxxep/rapidhash/blob/master/docs/bench_hash_x86_64_intel_xeon_8488c_native.svg>
  - <https://github.com/hoxxep/rapidhash/blob/master/docs/bench_hash_x86_64_amd_epyc_9R14.svg>
  - <https://github.com/hoxxep/rapidhash/blob/master/docs/bench_hash_aarch64_apple_m1_max.svg>
  - <https://github.com/hoxxep/rapidhash/blob/master/docs/bench_hash_aarch64_apple_m1_max_native.svg>
  - <https://github.com/hoxxep/rapidhash>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/README.md>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/docs/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/docs/generate_charts.py>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/Cargo.toml>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/rapidhash/Cargo.toml>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/rapidhash-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/rapidhash-bench/benches/bench/basic.rs>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/rapidhash-bench/benches/bench/main.rs>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/CHANGELOG.md>
  - <https://api.github.com/repos/hoxxep/rapidhash>
  - <https://api.github.com/repos/hoxxep/rapidhash/commits?per_page=1>
  - <https://api.github.com/repos/hoxxep/rapidhash/git/trees/master?recursive=1>
- **Sources the enricher read:**
  - <https://github.com/hoxxep/rapidhash>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/README.md>
  - <https://api.github.com/repos/hoxxep/rapidhash>
  - <https://api.github.com/repos/hoxxep/rapidhash/commits?per_page=5>
  - <https://api.github.com/repos/hoxxep/rapidhash/releases?per_page=5>
  - <https://api.github.com/repos/hoxxep/rapidhash/git/trees/HEAD?recursive=1>
  - <https://github.com/hoxxep/rapidhash/blob/master/Cargo.toml>
  - <https://github.com/hoxxep/rapidhash/blob/master/CHANGELOG.md>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/Cargo.toml>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/src/lib.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/src/fast.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/src/quality.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/src/util/mix.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/src/inner/mix_np.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/src/inner/rapid_hasher.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/src/inner/rapid_const.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/src/inner/seeding.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/src/v3/mod.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash/src/v3/rapid_const.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/rapidhash-bench/benches/bench/basic.rs>
  - <https://github.com/hoxxep/rapidhash/blob/master/docs/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/docs/bench_hash_x86_64_intel_xeon_8488c.txt>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/docs/bench_hash_x86_64_intel_xeon_8488c.svg>
  - <https://github.com/hoxxep/rapidhash/issues>
  - <https://github.com/hoxxep/rapidhash/issues/90>
  - <https://github.com/hoxxep/rapidhash/issues/46>
  - <https://github.com/hoxxep/rapidhash/issues/59>
  - <https://crates.io/api/v1/crates/rapidhash>
  - <https://liams.website/articles/seed-independent-collisions-on-wyhash-and-rapidhash>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/hoxxep/rapidhash`) · [data/wave7/enrich/raw/github_com_hoxxep_rapidhash.json](../../../data/wave7/enrich/raw/github_com_hoxxep_rapidhash.json) (enrichment confidence 0.8)

</details>
