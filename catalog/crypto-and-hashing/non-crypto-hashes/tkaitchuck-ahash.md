# aHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Keyed AES-round Rust hasher for in-memory HashMaps; about 11x faster than SipHash-1-3, claims wins over xxh3/wyhash.

| | |
|---|---|
| **Beats** | xxHash (XXH3 via xxhash-rust) and wyhash; also SipHash-1-3, the Rust std HashMap default |
| **Claimed result** | Page text (verbatim): "AHash is faster than either one [t1ha and XXHash], both with and without AES"; "AHash outperforms wyHash across all input sizes"; "At over 50GB/s aHash is the fastest algorithm to pass the full test suite by more than a factor of 2"; about 10x faster than SipHash. The Google Sheet linked from the page gives time to hash a u64 and a 1 KB string (units not labelled, probably ns): AHash 0.87 / 19.98, XXHash (xxh3) 11.88 / 114.14, WyHash 1.53 / 53.13, SipHash-1-3 9.70 / 219.13, FxHash 0.71 / 121.97. That makes aHash about 13.7x / 5.7x faster than xxh3, 1.76x / 2.66x faster than wyhash, and 11x / 11x faster than SipHash-1-3 (derived from page data). |
| **Workload** | Criterion microbenchmarks that hash a u64 and strings of 1-1023 bytes through Rust's Hasher/BuildHasher trait (compare/tests/compare.rs), compared with SipHash, FxHash, FnvHash, FarmHash, HighwayHash, MetroHash, t1ha, xxh3 and wyhash. The "50GB/s" figure comes from the SMHasher bulk test (smhasher/ahashOutput.txt: 60349 MiB/s average at a nominal "3 ghz") |
| **Metric** | throughput |
| **Compiler and flags** | rustc (version unstated); bench profile in compare/Cargo.toml: opt-level=3, lto='fat', codegen-units=1, debug-assertions=false; Criterion 0.3.3; target-cpu/RUSTFLAGS unstated |
| **Adoption** | 1347 GitHub stars; about 790M crates.io downloads (about 151M recent) and 2051 reverse dependencies. It was hashbrown's default hasher until hashbrown v0.15.0 (2024-10), which switched to foldhash. It was never the Rust std HashMap default, which is SipHash-1-3. |
| **Last commit** | 2025-11-21 |
| **Links** | [repository](https://github.com/tkaitchuck/aHash) · [benchmark](https://github.com/tkaitchuck/aHash/blob/master/compare/readme.md) |

## Verdict

The project's Criterion bench hashes a u64 and a 1 KB string through each crate's Rust BuildHasher with fat LTO; xxh3 goes through xxhash-rust's streaming Xxh3Builder. Its sheet reports aHash 0.87/19.98 against xxh3 11.88/114.14, wyhash 1.53/53.13 and SipHash-1-3 9.70/219.13, with units unlabelled (probably ns) and no rustc version or CPU stated. Independent data backs only the SipHash gap (foldhash's benchmark: 1.23 vs 9.09 ns per u64 on a Xeon 8481C with Rust 1.80.1); rurban SMHasher on a Ryzen 5 3350G puts ahash64 bulk speed at 9.9 GB/s, about half of xxh3 and wyhash.

## Use it when

- Rust HashMap/HashSet with string or byte-slice keys from about 16 bytes to a few KB, where SipHash-1-3 shows up in profiles: the project's FAQ table (i7-6700) has 1 KB strings at 25.4 ns against 254 ns for SipHash-1-3.
- Maps that ingest untrusted keys (request fields, user IDs), where you want per-map random keys rather than an unkeyed hash like FxHash or FNV.
- Builds where you control RUSTFLAGS and can enable -C target-feature=+aes or target-cpu=native on x86-64. The AES path is about 2x faster than the fallback on 1 KB strings (25.4 vs 54.6 ns in the FAQ table).
- Integer keys with structured low bits (multiples of 1024, aligned pointers) where FxHash collapses into a few buckets.
- no_std targets that still need a keyed hasher: turn off std and use compile-time-rng or explicit seeds (RandomState::with_seeds).

## Skip it when

- Anything persisted, sent over the network or compared across machines or builds. The output changes with CPU features, target-cpu flags, stable vs nightly and crate version; issue #236 was closed as intended behaviour.
- Security-relevant hashing (MACs, checksums, content addressing). It is not cryptographic. A key-recovery attack using only collision checks was fixed in 0.8.4 (#163). An open report from 2026-09 (#292) shows a fixed 56-byte pair colliding for about 2^-19.4 of random keys on the AES path, against 2^-64 for an ideal keyed hash.
- Default builds without the aes target feature (baseline x86-64, wasm, 32-bit targets). There is no runtime CPU detection (open #104), so these builds silently get the slower multiply fallback.
- Small integer keys. FxHash is faster on u64 in aHash's own sheet (0.71 vs 0.87). foldhash's benchmark (Xeon 8481C and Apple M2, Rust 1.80.1) has foldhash ahead on most hash-table workloads (geomean 6.21 vs 8.74 ns without target-cpu=native), with aHash winning only medium-to-long strings when AES is on.
- Bulk hashing of large buffers. Independent rurban SMHasher numbers (Ryzen 5 3350G) have ahash64 at 9.9 GB/s against 20.9 GB/s for xxh3 and 22.6 GB/s for wyhash.

## How it is fast

When built with the aes target feature, each 16-byte block goes through one AES decryption round (aesdec) in one lane and an SSSE3 byte shuffle plus 64-bit add in a second lane. Inputs over 64 bytes are consumed 64 bytes per iteration across four independent AES lanes, and finish folds 256 bits of state to 64 with up to three AES rounds. Lengths are dispatched through a branch tree (&lt;=8, 9-16, 17-32, 33-64, &gt;64) that reads overlapping head and tail words instead of looping over bytes. Without AES it falls back to a 'folded multiply' (64x64-&gt;128-bit multiply, then XOR of the two halves); on nightly, min_specialization gives primitive keys a one-multiply hasher.

## Compared with alternatives

Pick aHash over xxHash or wyhash when you are in Rust, hashing short-to-medium HashMap keys that may come from hostile input, and want per-map random keys. aHash's own page says wyhash has fixed strings that reset its state. Pick xxHash (XXH3) or wyhash when you need output that is stable across machines and versions, when you work in C/C++, or for bulk throughput, where rurban SMHasher puts both about 2x ahead of ahash64.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if, zerocopy 0.8, once_cell (most targets); getrandom 0.3 through the default runtime-rng feature; optional const-random, serde, portable-atomic; build dependency version_check |
| **Minimum toolchain** | Rust 1.60 declared (rust-version), but the default runtime-rng feature pulls in getrandom 0.3, which declares Rust 1.63; specialization turns on automatically on nightly |
| **Platforms** | Any Rust target through the fallback, including no_std. The AES path runs on x86/x86-64 and AArch64 only when compiled with the aes target feature; 32-bit ARM also needs nightly plus the nightly-arm-aes feature. |
| **Thread safety** | Not documented explicitly. AHasher and RandomState are plain Clone value types with no interior mutability; global seed setup uses a once_cell OnceBox and an atomic counter, and set_random_source requires Send + Sync. |
| **Drop-in for the baseline** | partial — it is a drop-in BuildHasher for std HashMap/HashSet in place of SipHash-1-3's RandomState. It cannot replace xxHash or wyhash as a content hash, because its output is not stable across platforms, flags or versions. |

## Gotchas

- ahash::RandomState holds four u64 keys (32 bytes), so ahash::HashMap&lt;u32, u32&gt; is 64 bytes against 48 for std's HashMap, according to foldhash's README.
- build.rs turns on min_specialization whenever the compiler is nightly, and there is no opt-out (open #238). The same code therefore takes different paths, and gives different hash values, on stable and nightly.
- The 0.8.12 patch release moved to getrandom 0.3, which broke some wasm/js builds (open #274). The workaround is to disable default features and use compile-time-rng or explicit seeds.
- Users have reported slowdowns between patch releases (0.8.6 to 0.8.7, about 1.6x on an Apple M1 Pro) and with target-cpu=native on AMD Ryzen (open #194 and #190). Pin the version and benchmark on your own hardware.

## Known shortcomings

- Independent rurban SMHasher contradicts the bulk claim (ahash64 9.9 GB/s vs xxh3 20.9 and wyhash 22.6 GB/s); aHash wins only small keys, slightly. hashbrown's default hasher only until v0.15 (2024-10, replaced by foldhash), never std's default; no CPU/rustc stated.
- Claim to beat xxh3/wyhash is contradicted: rurban SMHasher (Ryzen 5 3350G) bulk ahash64 9.9 GB/s vs xxh3 20.9 and wyhash 22.6; foldhash beats aHash on most map workloads, and hashbrown 0.15 switched its default to foldhash. AES path needs the aes target feature at compile time (no runtime detection, #104): a default x86-64 build silently uses the \~2x slower fallback. Output is not stable across CPUs, flags, compiler channel or versions. Open #292 (2026-09): a fixed 56-byte pair collides for \~2^-19.4 of keys on the AES path. Slow maintenance (last commit 2025-11, 35 open issues).

## Caveats and trade-offs

No CPU model or rustc version is stated, and the sheet does not label its time units. Comparisons go through Rust Hasher-trait wrappers, which may penalise streaming hashes such as xxh3 on 1 KB inputs. The independent rurban/SMHasher table (AMD Ryzen 5 3350G) contradicts the bulk-speed claims: ahash64 9862.62 MiB/s against xxh3 20853.74 and wyhash 22640.53. It shows aHash only slightly ahead on small keys (27.32 cycles/hash against 29.46 for xxh3 and 28.91 for wyhash). The "fastest SMHasher-passing algorithm by &gt;2x" claim is stale. Output is not stable across platforms or versions (HashMap use only). FxHash is faster on u64 keys, as the page admits.

Output is not fixed/standardized across hardware and versions, so unsuitable for persisted or transmitted hashes; DOS-resistance relies on per-process random keys.

## Maintenance

Maintained but slow-moving: last release 0.8.12 (May 2025), last commit Nov 2025, 35 open issues including the getrandom breakage and a new collision report; dual MIT/Apache-2.0 and ubiquitous (about 790M crates.io downloads), though hashbrown replaced it with foldhash as its default hasher in 0.15.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark only: the Criterion bench code is public (compare/tests/compare.rs, with the bench profile in compare/Cargo.toml) and the linked Google Sheet gives per-hasher timings, but no CPU model and no rustc version are stated. The one independent suite, rurban/SMHasher, does not back the win: it shows aHash losing about 2x on bulk throughput to xxh3 and wyhash and winning only slightly on small keys, so this cannot be B.
- **Verifier notes:** The quotes in the record match the page word for word. The record understated the evidence: the linked sheet does have tabular numbers. Fixed the license (the repo is dual MIT/Apache-2.0, not just Apache-2.0) and the usage claim, since aHash was hashbrown's default hasher until v0.15 and was never the std default. Independent SMHasher data contradicts the bulk-throughput superiority claim, so tier stays C with a strong caveat.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `license`, `stars_or_usage`, `workload`, `caveats`
- **Shortcomings recorded by:** rurban/smhasher (Ryzen 5 3350G): ahash64 bulk 9.9 GB/s vs xxh3 20.9, wyhash 22.6. foldhash bench (Xeon 8481C): 1.23 vs SipHash-1-3 9.09 ns/u64.
- **Pages the verifier opened:**
  - <https://github.com/tkaitchuck/aHash>
  - <https://github.com/tkaitchuck/aHash/blob/master/compare/readme.md>
  - <https://raw.githubusercontent.com/tkaitchuck/aHash/master/compare/readme.md>
  - <https://docs.google.com/spreadsheets/d/e/2PACX-1vSK7Li2nS-Bur9arAYF9IfT37MP-ohAe1v19lZu5fd9MajI1fSveLAQZyEie4Ea9k5-SWHTff7nL2DW/pub?gid=0&single=true&output=csv>
  - <https://raw.githubusercontent.com/tkaitchuck/aHash/master/compare/Cargo.toml>
  - <https://raw.githubusercontent.com/tkaitchuck/aHash/master/compare/tests/compare.rs>
  - <https://raw.githubusercontent.com/tkaitchuck/aHash/master/Cargo.toml>
  - <https://raw.githubusercontent.com/tkaitchuck/aHash/master/smhasher/ahashOutput.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rust-lang/hashbrown/master/CHANGELOG.md>
  - <https://crates.io/api/v1/crates/ahash>
- **Sources the enricher read:**
  - <https://github.com/tkaitchuck/aHash>
  - <https://github.com/tkaitchuck/aHash/blob/master/README.md>
  - <https://github.com/tkaitchuck/aHash/blob/master/FAQ.md>
  - <https://github.com/tkaitchuck/aHash/blob/master/compare/readme.md>
  - <https://github.com/tkaitchuck/aHash/blob/master/Cargo.toml>
  - <https://github.com/tkaitchuck/aHash/blob/master/build.rs>
  - <https://github.com/tkaitchuck/aHash/blob/master/src/lib.rs>
  - <https://github.com/tkaitchuck/aHash/blob/master/src/aes_hash.rs>
  - <https://github.com/tkaitchuck/aHash/blob/master/src/fallback_hash.rs>
  - <https://github.com/tkaitchuck/aHash/blob/master/src/operations.rs>
  - <https://github.com/tkaitchuck/aHash/blob/master/src/random_state.rs>
  - <https://github.com/tkaitchuck/aHash/blob/master/src/specialize.rs>
  - <https://github.com/tkaitchuck/aHash/blob/master/src/convert.rs>
  - <https://github.com/tkaitchuck/aHash/commits/master>
  - <https://github.com/tkaitchuck/aHash/tags>
  - <https://github.com/tkaitchuck/aHash/issues>
  - <https://github.com/tkaitchuck/aHash/issues/292>
  - <https://github.com/tkaitchuck/aHash/issues/285>
  - <https://github.com/tkaitchuck/aHash/issues/274>
  - <https://github.com/tkaitchuck/aHash/issues/238>
  - <https://github.com/tkaitchuck/aHash/issues/236>
  - <https://github.com/tkaitchuck/aHash/issues/194>
  - <https://github.com/tkaitchuck/aHash/issues/190>
  - <https://github.com/tkaitchuck/aHash/issues/163>
  - <https://github.com/tkaitchuck/aHash/issues/104>
  - <https://raw.githubusercontent.com/tkaitchuck/aHash/master/compare/Cargo.toml>
  - <https://raw.githubusercontent.com/tkaitchuck/aHash/master/compare/tests/compare.rs>
  - <https://raw.githubusercontent.com/tkaitchuck/aHash/master/smhasher/ahashOutput.txt>
  - <https://docs.google.com/spreadsheets/d/e/2PACX-1vSK7Li2nS-Bur9arAYF9IfT37MP-ohAe1v19lZu5fd9MajI1fSveLAQZyEie4Ea9k5-SWHTff7nL2DW/pub?gid=0&single=true&output=csv>
  - <https://crates.io/api/v1/crates/ahash>
  - <https://crates.io/api/v1/crates/ahash/0.8.12/dependencies>
  - <https://crates.io/api/v1/crates/getrandom/versions>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rust-lang/hashbrown/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/orlp/foldhash/master/README.md>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/tkaitchuck/ahash`) · [data/wave7/enrich/raw/github_com_tkaitchuck_ahash.json](../../../data/wave7/enrich/raw/github_com_tkaitchuck_ahash.json) (enrichment confidence 0.82)

</details>
