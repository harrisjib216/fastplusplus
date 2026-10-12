# entropy-map

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Cloudflare's immutable Rust map/set on a fingerprinting MPHF (2.1-2.7 bits/key); its edge over std HashMap is compactness, not lookup speed.

| | |
|---|---|
| **Beats** | Rust std::collections::HashMap / HashSet, tested only in the third-party benches of unmerged PR #6 (with FxHash and with the SipHash DefaultHasher). The README itself claims, without numbers, faster query and construction than the `ph` crate (beling/bsuccinct-rs) and better performance than rkyv::ArchivedHashMap. std::unordered_map is never tested. |
| **Claimed result** | README (first-party, no baseline row): Mphf query time 5-20 ns depending on parameters, number of keys and L1-L3 cache sizes; 2.10-2.71 bits/key. benches/mphf.rs doc comment (N=1M random u64, Mphf&lt;32,8&gt;): 14.372 ms per 1M gets at gamma 1.0 (2.10 bits/key) and 4.5959 ms at gamma 2.0 (2.72 bits/key), i.e. \~14.4 and \~4.6 ns/get (derived from page data). No first-party head-to-head against any baseline. Third-party unmerged PR #6 (result black_box fixed, N=1M u64, hardware unstated): Mphf get 26.267 ms (gamma 1.0) / 19.683 ms (gamma 2.0) per 1M; Set contains 26.454 ms vs std HashSet+FxHash 14.704 ms (\~1.8x slower) and vs std HashSet+DefaultHasher (SipHash) 34.877 ms (\~1.32x faster; \~1.06x at equal hasher, 32.839 ms); u64-&gt;u32 get: new Map 37.293 ms and MapWithDict 45.406 ms vs std HashMap+FxHash 18.518 / 18.921 ms (\~2.0x / \~2.4x slower); archived Map get 41.039 ms vs rkyv ArchivedHashMap 37.373 ms (\~1.1x slower). All ratios derived from page data. |
| **Workload** | First-party: Mphf::get latency and bits/key for Mphf&lt;32,8&gt; over 1M random u64 keys at gamma 1.0 and 2.0 (benches/mphf.rs). The README's 5-20 ns covers the bare MPHF only, not map or set lookups; benches/map_with_dict.rs records 75.814 ms per 1M MapWithDict&lt;u64,u32&gt; gets (\~75.8 ns each, derived). Third-party PR #6: Set::contains and Map/MapWithDict get over 1M random u64 keys with u32 values, against Rust std HashMap/HashSet (FxHash and SipHash DefaultHasher) and rkyv 0.8 ArchivedHashMap. |
| **Metric** | latency |
| **Compiler and flags** | rustc version not stated. Cargo.toml [profile.release], which the bench profile inherits: opt-level=3, lto="fat", codegen-units=1, debug=true. No target-cpu or RUSTFLAGS stated. Third-party PR #6 comments out these release settings, so its numbers use Cargo defaults. |
| **Adoption** | 45 GitHub stars; crates.io v1.2.0 with 839,098 total downloads (213,123 recent); 1 public reverse dependency (simd-lookup). Cloudflare-owned; commit history references internal BOTS/BOTSML tickets. |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/cloudflare/entropy-map) · [benchmark](https://github.com/cloudflare/entropy-map#overview) |

## Verdict

First-party criterion comments only, with no baseline, no CPU and no rustc stated (fat-LTO release profile, Dec 2023, then-default FxHasher, result not black_boxed): on 1M random u64 keys, a bare Mphf&lt;32,8&gt; get takes 14.4 ns at 2.10 bits/key (gamma 1.0) and 4.6 ns at 2.72 bits/key (gamma 2.0), and a MapWithDict&lt;u64,u32&gt; get takes \~75.8 ns. The only head-to-head is unmerged third-party PR #6 (Cargo default profile, hardware unstated): 19.7-26.3 ns per Mphf get, 1.8-2.4x slower than std HashSet/HashMap with FxHash, \~1.3x faster only than std HashSet with SipHash (\~1.06x at equal hasher), \~1.1x slower than rkyv ArchivedHashMap. Neither source measures memory against std, and no C++ baseline exists.

## Use it when

- Large static key sets (built offline or at deploy, rebuilt wholesale) where resident memory or cache footprint matters more than per-lookup nanoseconds: the MPHF index costs 2.10-2.72 bits/key, and the key array has no empty slots or control bytes.
- Many keys mapped to few distinct values (labels, scores, small enums): MapWithDict stores each distinct value once. MapWithDictBitpacked stores fixed-length Vec&lt;u32&gt; feature vectors with small ranges at the minimum bit width per 32-value block.
- Lookup tables shipped as files and read in place with rkyv 0.7: no rehash or deserialization at load, and the first-party benches show archived lookups within \~1-3% of in-memory ones.
- A dense 0..n-1 index for a known key set, to address your own parallel arrays, when every query key is guaranteed to be in the build set (bare Mphf, no key storage).
- Rust services where lookups only need to match std HashMap with the default SipHash (PR #6: Set within \~1.06x at equal hasher), not hashbrown with FxHash.

## Skip it when

- Latency-critical lookups when std HashMap/HashSet with FxHash fits in memory. In PR #6, entropy-map is 1.8x slower for Set contains and 2.0-2.4x slower for u64-&gt;u32 get, and \~1.1x slower than rkyv's ArchivedHashMap.
- Mutable data: there is no insert, remove or entry. Any change means a full single-threaded rebuild (1.2-1.5 s per 1M u64 keys in the repo's bench comments; 13.6 s for 1M keys with S=12 in PR #6).
- Mostly unique or wide values: MapWithDict keeps a full copy of every key plus an 8-byte usize index per key (its own test measures 16.6 bytes/key for u64-&gt;u32), so dictionary packing gains little.
- C++ codebases: it is Rust only, with no C API. For C++, use a C++ MPHF such as PTHash and verify keys yourself.
- Projects on rkyv 0.8 or reading untrusted serialized data: main pins rkyv 0.7.42 (the 0.8 port exists only in unmerged PR #6), and the validation is incomplete (see gotchas).

## How it is fast

The MPHF is FMPHGO, Beling's 'Fingerprinting-based minimal perfect hashing revisited': keys are hashed with WyHash into a bit array of gamma\*n bits per level. A key that lands alone sets its bit, and colliding keys move to the next level. Group optimization splits each level into B-bit groups, tries 2^S seeds per group and keeps the seed with the fewest collisions, so fewer levels are needed (tests at 100k keys: 1.64 average levels at gamma 1.0, 1.06 at gamma 2.0). A query hashes the key once per level until it finds a set bit, then returns rank(bit) from a two-level rank directory (4096/512-bit blocks packed in 16 bytes, \~3.1% overhead, after Kurpicz's rank/select engineering paper). Map and Set then do one equality check against the stored key at that index.

## Compared with alternatives

Pick it over PHast/ph (bsuccinct-rs) or PtrHash when you want a ready-made immutable Rust Map/Set with key verification, value dedup or bit-packing, and rkyv zero-copy archives rather than a bare MPHF. For the MPHF alone, prefer ph (from the author of the FMPHGO paper entropy-map reimplements) or PtrHash: they publish comparative benchmarks, the 2025 MPHF survey ranks PHast first for queries, and entropy-map's claimed edge over ph has no numbers.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bitpacking 0.9, num 0.4, wyhash 0.5; optional rkyv 0.7.42 + bytecheck 0.6 (feature rkyv_derive), serde + serde_bytes (feature serde) |
| **Minimum toolchain** | Rust edition 2021; no rust-version declared. v1.2.0 uses slice::as_chunks, which was stabilized in Rust 1.88, so it needs Rust 1.88+ (inferred). v1.1.0 avoided as_chunks. CI tracks stable. |
| **Platforms** | Any Rust target in principle: pure Rust with no arch intrinsics (bit-packing uses bitpacking's BitPacker1x, which the bitpacking docs call standard bitpacking, not the SSE3/AVX2 packers). CI runs only on ubuntu-latest; an aarch64 rkyv alignment fix is in the history (commit 1f5a988f). |
| **Thread safety** | Not documented. Built structures are immutable Box slices with no interior mutability, so concurrent shared lookups need no locks. Send/Sync follow K and V through Rust's auto traits. |
| **Drop-in for the baseline** | partial — covers only the read side of std HashMap/HashSet: TryFrom&lt;HashMap&gt;/TryFrom&lt;HashSet&gt; plus get/contains_key/contains/len/iter with Borrow-based lookups. No insert/remove/entry/Index/FromIterator, construction is a separate fallible step, and iteration follows MPHF index order. |

## Gotchas

- Bare Mphf::get on a key outside the build set returns None or an arbitrary valid index (its doc comment). Only Map/Set detect non-members, by storing and comparing full keys (maintainer reply in issue #4).
- Construction can fail. gamma &lt; 1.0 returns InvalidGammaParameter. Duplicate keys or colliding 64-bit hashes are never separated (from the code), so from_slice returns MaxLevelsExceeded after 64 levels instead of deduplicating (issue #4 reply: construction fails on unresolvable collisions). B, S and the seed type ST are compile-time checked (ST at most u32).
- The published numbers are stale. The benches/\*.rs result comments date from Dec 2023, when the default hasher was FxHasher (switched to WyHash in commit 4a364b53 before v1.0.0). They also leave the lookup result un-black_boxed, which likely explains the 4.6 ns figure; PR #6 measures 19.7-26.3 ns per Mphf get. benches/set.rs still imports the removed fxhash crate (issue #5).
- Untrusted input is unsafe to load. The MapWithDictBitpacked docs warn that a crafted serde payload can pass deserialization and later panic. The rkyv path relies only on derived CheckBytes while lookups use get_unchecked, so treat archives as trusted. MapWithDictBitpacked requires every Vec&lt;u32&gt; value to have the same length (NotEqualValuesLengths), and the caller passes a buffer of that length to get_values.

## Known shortcomings

- Not faster at lookup: the only head-to-head numbers (unmerged third-party PR #6) show it 1.8-2.4x slower than Rust's std HashMap with FxHash and \~1.1x slower than rkyv ArchivedHashMap. Its win is memory; the README's 5-20 ns figures predate the current default hasher.

## Caveats and trade-offs

First-party numbers are absolute only: the README and the benches/\*.rs doc comments state no CPU, OS, rustc version or baseline row. The README's 5-20 ns is for the bare Mphf::get, not for MapWithDict or Set lookups (\~75.8 ns per MapWithDict get in the repo's own bench comment, derived). The original benches black_box only the key and do not black_box the result. Unmerged third-party PR #6 fixes this and measures 19.7-26.3 ns per Mphf get instead of 4.6-14.4 ns (hardware unstated, fat-LTO profile disabled, so not a like-for-like rerun). benches/set.rs has a std HashSet harness but publishes no results, and it still uses the fxhash crate that was removed from Cargo.toml in 2024-10 (issue #5), so it likely does not build as-is. The claimed wins over the ph crate and rkyv::ArchivedHashMap have no numbers; PR #6 (rkyv 0.8) shows the archived entropy map \~1.1x slower than rkyv ArchivedHashMap, and its author comments that ArchivedHashMap was faster in real usage. Against Rust std, PR #6 shows entropy-map \~1.8-2.4x slower with FxHash and \~1.3x faster only against the default SipHash HashSet (\~1.06x at equal hasher). The real advantage is memory (2.10-2.72 bits/key for the MPHF). No C++ baseline was tested. GitHub reports the license as NOASSERTION because LICENSE is the short Apache-2.0 notice; Cargo.toml declares Apache-2.0.

Immutable map/set only (no post-construction inserts); Rust crate, so C++ use requires an FFI boundary; requires a value dictionary (MapWithDict) for arbitrary values rather than native insert semantics; construction-time vs. query-time tradeoff tunable via a gamma parameter

## Maintenance

Active and Cloudflare-owned: v1.2.0 (serde feature) shipped 2026-09-09, with \~839k crates.io downloads. Outside contributions stall, though: PR #6 (rkyv 0.8, bench fixes) and issue #5 have had no maintainer response since Oct 2025. It is Apache-2.0 and \~2,750 lines of pure Rust (including tests) with three small dependencies, so vendoring is easy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README Overview gives only first-party absolute figures (5-20 ns MPHF query, 2.10-2.71 bits/key). It shows no baseline row, no CPU and no compiler. The public criterion code in benches/mphf.rs records the source runs (N=1M random u64) but has no baseline either. The only head-to-head numbers anywhere are third-party, in unmerged PR #6, with no hardware stated. They show no clear win over std, so C is the ceiling.
- **Verifier notes:** Borderline reject (not-faster): the only head-to-head data (third-party PR #6) show entropy-map slower than Rust std HashMap/HashSet with FxHash and slower than rkyv ArchivedHashMap, faster only against std's default SipHash HashSet, mostly from the hasher. I kept it as a downgrade because the README does claim faster queries than ph and it has 839k crates.io downloads; its real edge is memory, not latency. Metadata checks out: Apache-2.0 (NOASSERTION on GitHub, Apache-2.0 in the LICENSE notice and Cargo.toml), 45 stars, not a fork, not archived, last commit 2026-09-09 (active).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cloudflare/entropy-map>
  - <https://github.com/cloudflare/entropy-map#overview>
  - <https://github.com/cloudflare/entropy-map/commits>
  - <https://github.com/cloudflare/entropy-map/blob/main/README.md>
  - <https://github.com/cloudflare/entropy-map/blob/main/LICENSE>
  - <https://github.com/cloudflare/entropy-map/blob/main/Cargo.toml>
  - <https://github.com/cloudflare/entropy-map/blob/main/Makefile>
  - <https://github.com/cloudflare/entropy-map/blob/main/.github/workflows/ci.yml>
  - <https://github.com/cloudflare/entropy-map/blob/main/benches/mphf.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/benches/map_with_dict.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/benches/map_with_dict_bitpacked.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/benches/set.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/benches/rank.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/examples/mphf.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/examples/set.rs>
  - <https://github.com/cloudflare/entropy-map/commit/b6c87e67>
  - <https://github.com/cloudflare/entropy-map/commit/8f3b19ad>
  - <https://github.com/cloudflare/entropy-map/commit/4a364b53>
  - <https://github.com/cloudflare/entropy-map/releases>
  - <https://github.com/cloudflare/entropy-map/pulls>
  - <https://github.com/cloudflare/entropy-map/pull/1>
  - <https://github.com/cloudflare/entropy-map/pull/6>
  - <https://github.com/cloudflare/entropy-map/pull/6/files>
  - <https://github.com/cloudflare/entropy-map/issues/4>
  - <https://github.com/cloudflare/entropy-map/issues/5>
  - <https://crates.io/crates/entropy-map>
  - <https://crates.io/api/v1/crates/entropy-map>
  - <https://crates.io/api/v1/crates/entropy-map/reverse_dependencies>
  - <https://arxiv.org/pdf/2603.24882>
  - <https://arxiv.org/pdf/2506.06536>
- **Sources the enricher read:**
  - <https://github.com/cloudflare/entropy-map>
  - <https://github.com/cloudflare/entropy-map#overview>
  - <https://github.com/cloudflare/entropy-map/blob/main/README.md>
  - <https://github.com/cloudflare/entropy-map/blob/main/Cargo.toml>
  - <https://github.com/cloudflare/entropy-map/blob/main/LICENSE>
  - <https://github.com/cloudflare/entropy-map/blob/main/Makefile>
  - <https://github.com/cloudflare/entropy-map/blob/main/.github/workflows/ci.yml>
  - <https://github.com/cloudflare/entropy-map/blob/main/src/lib.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/src/mphf.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/src/rank.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/src/set.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/src/map_with_dict.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/src/map_with_dict_bitpacked.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/benches/mphf.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/benches/map_with_dict.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/benches/map_with_dict_bitpacked.rs>
  - <https://github.com/cloudflare/entropy-map/blob/main/benches/set.rs>
  - <https://github.com/cloudflare/entropy-map/blob/v1.1.0/src/mphf.rs>
  - <https://github.com/cloudflare/entropy-map/blob/v1.1.0/src/rank.rs>
  - <https://github.com/cloudflare/entropy-map/blob/aa9b7f34/src/mphf.rs>
  - <https://github.com/cloudflare/entropy-map/blob/8f3b19ad/src/mphf.rs>
  - <https://github.com/cloudflare/entropy-map/commits/main>
  - <https://github.com/cloudflare/entropy-map/commits/main/benches/mphf.rs>
  - <https://github.com/cloudflare/entropy-map/commits/main/benches/map_with_dict.rs>
  - <https://github.com/cloudflare/entropy-map/commit/4a364b53>
  - <https://github.com/cloudflare/entropy-map/commit/7e9e108e>
  - <https://github.com/cloudflare/entropy-map/commit/1f5a988f>
  - <https://github.com/cloudflare/entropy-map/commit/bd8a5026>
  - <https://github.com/cloudflare/entropy-map/releases>
  - <https://github.com/cloudflare/entropy-map/tags>
  - <https://github.com/cloudflare/entropy-map/issues>
  - <https://github.com/cloudflare/entropy-map/pull/6>
  - <https://github.com/cloudflare/entropy-map/pull/6/files>
  - <https://github.com/cloudflare/entropy-map/issues/4>
  - <https://github.com/cloudflare/entropy-map/issues/5>
  - <https://crates.io/api/v1/crates/entropy-map>
  - <https://crates.io/api/v1/crates/entropy-map/reverse_dependencies>
  - <https://blog.rust-lang.org/2025/06/26/Rust-1.88.0/>
  - <https://doc.rust-lang.org/std/primitive.slice.html#method.as_chunks>
  - <https://docs.rs/bitpacking/0.9.2/bitpacking/>
  - <https://arxiv.org/abs/2603.24882>
  - <https://arxiv.org/pdf/2506.06536>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/cloudflare/entropy-map`) · [data/wave1-phf/enrich/raw/github_com_cloudflare_entropy_map.json](../../../data/wave1-phf/enrich/raw/github_com_cloudflare_entropy_map.json) (enrichment confidence 0.75)

</details>
