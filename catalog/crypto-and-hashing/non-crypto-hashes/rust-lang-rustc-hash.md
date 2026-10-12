# rustc-hash (FxHash)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> rustc's own tiny multiply-based hasher and FxHashMap/FxHashSet aliases. Much faster than std SipHash-1-3 on integer-heavy keys, but not DoS-resistant.

| | |
|---|---|
| **Beats** | SipHash-1-3 (Rust std DefaultHasher, the default hasher of std::collections::HashMap/HashSet) |
| **Claimed result** | Switching rustc's FxHashMap/FxHashSet from FxHasher back to std's DefaultHasher (SipHash-1-3, with the #69152 improvements) regressed every rustc-perf `check` benchmark by 3.9% to 84.7%. Examples: deeply-nested-check avg 63.6% (max 84.7%), syn-check avg 38.7%, helloworld-check avg 23.3%, token-stream-stress-check avg 5.9%. Measured locally in Feb 2020 on the pre-2.0 Firefox-derived FxHash. The Rust Performance Book summarizes this as 'slowdowns ranging from 4-84%'. |
| **Workload** | Hashing inside rustc's internal hash maps/sets (integers, composite multi-integer keys, short strings/slices), measured as end-to-end rustc compile time on rustc-perf `check` benchmarks |
| **Metric** | throughput |
| **Adoption** | 597 stars; \~828M all-time crates.io downloads (\~225M recent); internal hasher (FxHashMap/FxHashSet) throughout the rustc compiler |
| **Last commit** | 2026-07-18 |
| **Links** | [repository](https://github.com/rust-lang/rustc-hash) · [benchmark](https://github.com/rust-lang/rust/issues/69153#issuecomment-589338446) |

## Verdict

In Feb 2020 rustc maintainer N. Nethercote rebuilt rustc with every FxHashMap/FxHashSet switched to std's DefaultHasher (SipHash-1-3) and ran rustc-perf locally. Every `check` benchmark regressed by 3.9%-84.7% (per-benchmark averages 5.9%-63.6%). That baseline included his proposed SipHasher integer speedups (rust PR #69152), which were never merged. Against unpatched std he reported check-clean slowdowns of 4.3%-128.6%. Hardware, compiler flags and the rustc-perf metric were not stated. The test used the old Firefox-derived FxHash. The current 2.x algorithm was only shown to be 'slightly better' for rustc (rust-timer perf runs), with no standalone numbers.

## Use it when

- Hash maps/sets in compilers, analyzers, graph code or ECS-style code keyed by integers, IDs, pointers/interned handles or small tuples of them, where profiling shows hashing is hot.
- Internal tables whose keys are never controlled by an attacker (build tools, offline batch jobs, single-user CLIs).
- When you want deterministic iteration order within one build and platform and no per-map seed (FxBuildHasher is zero-sized, so the map carries no hasher state).
- no_std or embedded targets that need a tiny dependency-free Hasher (disable default features).
- Workloads shaped like rustc's own. In rustc profiling cited in PR #37, the four most common hash-call shapes, each 1-3 integer writes, made up about 74% of calls.

## Skip it when

- Any map keyed by untrusted input (network, user-supplied strings). It has no HashDoS resistance, and the hash is linear, so colliding keys are easy to construct, even by accident.
- Building one large map by inserting keys in another Fx map's iteration order, as in serde/bincode deserialization or cloning via iteration. Issue #45 (open since 2.0; a 2026 comment says it still bites) reports about 8-9x slowdowns at 10M u64 keys, and random seeding does not help because the hash is linear in the seed.
- Very large tables of low-entropy keys such as aligned pointers. The fixed rotate only spreads entropy well up to about 2^26 buckets. In 2.0 the rotate of 20 caused a roughly 3x rustc compile-time blowup on one large project (rust#135477), which 2.1.1 only mitigated.
- When you need hash values that are stable across crate versions or targets. 2.x changed the output in minor releases (issue #58), and 32-bit, sparc64 and wasm64 use a different byte-hash path (issue #73).
- String-heavy or long-key workloads, where general-purpose hashers are a better fit. Even for integer keys, Nethercote's microbenchmark showed std HashMap (with his unmerged SipHash patch) slightly ahead of the old FxHashMap, because it had fewer collisions.

## How it is fast

Each integer write is one add and one multiply, `hash = (hash + x) * K`, with K a Steele–Vigna MCG multiplier. This makes a polynomial hash over the Hasher's write calls. finish() is a single rotate_left(26) (15 on 32-bit), which moves the well-mixed high bits of the product into the low bits hashbrown uses as its bucket index. Byte strings and slices are first compressed to one u64 by a small wyhash-style routine: 16-byte chunks go through a 64x64-&gt;128 folded multiply (lo ^ hi) in two independent lanes. There is no per-map state and all functions are small #[inline] code. A single-integer key costs roughly one multiply plus a rotate, against SipHash-1-3's multi-word state setup and rounds.

## Compared with alternatives

Choose rustc-hash over foldhash (same designer; per-map random seed, stronger finalizer, geometric mean 6.21 vs SipHash's 28.70 on its Xeon suite) when keys are trusted integers or pointers and you want the fewest instructions per hash, a zero-sized hasher and deterministic output. Choose foldhash or aHash (keyed, AES-accelerated, some DoS resistance) when keys are strings, externally supplied, or bulk-reinserted between maps. xxHash, rapidhash and wyhash are byte-stream hashers rather than Rust Hasher-trait integer mixers, so they are not direct substitutes here.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none by default; optional rand 0.9 (feature `rand`) |
| **Minimum toolchain** | Rust 1.77 (rust-version in Cargo.toml since 2.1.2), edition 2021; `nightly` feature needs a nightly compiler |
| **Platforms** | any; fast 64x64-&gt;128 multiply path on 64-bit targets such as x86-64 and aarch64; 32-bit decomposed fallback on 32-bit targets, sparc64 and wasm64 without wide-arithmetic. CI covers Linux/macOS/Windows plus Miri on x86_64, i686, mips and mips64 (big-endian). |
| **Thread safety** | Same as std HashMap, since the aliases are std types. FxHasher and FxBuildHasher hold only plain integers. FxRandomState draws its seed from a thread-local, then increments it for each new map. |
| **Drop-in for the baseline** | partial — FxHashMap&lt;K,V&gt; is std HashMap&lt;K,V,FxBuildHasher&gt;, so the full API works. However, HashMap::new()/with_capacity() exist only for RandomState, so you construct with FxHashMap::default() or with_capacity_and_hasher(n, Default::default()). The type is also not interchangeable with HashMap&lt;K,V&gt; in public signatures. |

## Gotchas

- The default seed is 0, so hashing 0 gives 0 and leading zero writes vanish: (0u64, x) hashes the same as x alone. The polynomial structure also gives easy wrapping collisions: (a, b) and (a+1, b-K) collide.
- The `nightly` feature makes write_length_prefix a no-op for speed. As the source comment says, nested collections of non-byte-slice elements then lose prefix-freeness and can collide when only the split point differs.
- The name is historical. 2.x is Orson Peters' polynomial hash, not the Firefox rotate-xor-multiply FxHash, so older quality critiques and benchmarks (aHash's compare page, foldhash's `fxhash` column, which uses the separate fxhash 0.2.1 crate) do not describe it exactly.
- The repo has no benchmarks by design: benchmarks PR #50 was closed because rustc-perf is the only yardstick. 1.2.0 was yanked for no_std breakage.

## Known shortcomings

- Only numbers are first-party and old: rust-lang/rust#69153 (Feb 2020) shows every rustc-perf benchmark slower without FxHash (4.3-128.6% vs std SipHash; the often-quoted 3.9-84.7% used an unmerged patched SipHash), measured on the pre-2.0 algorithm with no CPU, flags or metric stated. Not DoS-resistant; weak on some key distributions (rustc-specific tuning).
- Linear hash: open #45 shows reinserting keys in another Fx map's iteration order is \~8-9x slower (10M keys) and seeding does not help. 2.0's rotate-20 caused a \~3x rustc blow-up (rust#135477); 2.1.1's rotate-26 mitigates only up to \~2^26 entries. Output not stable across versions or targets; no benchmarks in the repo.

## Caveats and trade-offs

The numbers are first-party end-to-end rustc-perf compile-time results that a rustc/rustc-hash maintainer measured locally in Feb 2020. Hardware, compiler flags and the exact metric are not stated. They cover the old Firefox-derived FxHash. The current 2.x hasher (Orson Peters' polynomial hash with rotation finalizer and wyhash-style string compression) is described only as 'slightly better performance for rustc' in the CHANGELOG, and 2.0 caused a large-hashmap regression in rustc that 2.1.1 mitigated. In the same comment, std HashMap was slightly faster than FxHashMap on an integer-key microbenchmark (fewer collisions). FxHash is not HashDoS-resistant. The repo has no benchmark code (benchmarks PR #50 was closed unmerged).

Not DoS-resistant (unsuitable for untrusted-input hash maps, unlike SipHash); current algorithm is a polynomial hash with a wyhash-inspired string compression step, not the original 'FxHash' bit-mix despite the crate keeping that name for compatibility.

## Maintenance

Actively maintained under the rust-lang org (2.1.3 released 2026-07, last commit 2026-07-18). It is dual Apache-2.0/MIT with no unsafe code and no default dependencies, so it is trivial to depend on or vendor. Its design goals are strictly 'whatever makes rustc faster', not general-purpose quality or output stability.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Tier upgraded from D to C. The repo has no numbers, but a rust-lang/rust issue comment by rustc-hash maintainer N. Nethercote gives first-party rustc-perf results: switching rustc from FxHasher back to std DefaultHasher (SipHash-1-3) regressed every `check` benchmark by 3.9%-84.7%. Hardware, compiler flags and metric are not stated, and the measurement is of the pre-2.0 algorithm, so it cannot go above C.
- **Verifier notes:** The repo README has no numbers. The real numbers page is the rust-lang/rust #69153 comment, which the Rust Performance Book hashing chapter cites. GitHub detects only Apache-2.0, but Cargo.toml says 'Apache-2.0 OR MIT' and both LICENSE files are present, so the license is corrected. last_commit 2026-07-18, active status, the 597 stars and the 827M+ downloads were all checked and are correct.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `workload`, `license`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** rust-lang/rust#69153 (Feb 2020, same author): rustc-perf check-clean builds 4.3-128.6% slower with std SipHash-1-3 than with FxHash (3.9-84.7% against a patched SipHash from #69152 that was never merged).
- **Pages the verifier opened:**
  - <https://github.com/rust-lang/rustc-hash>
  - <https://github.com/rust-lang/rustc-hash/blob/main/README.md>
  - <https://github.com/rust-lang/rustc-hash/blob/main/Cargo.toml>
  - <https://github.com/rust-lang/rustc-hash/blob/main/CHANGELOG.md>
  - <https://github.com/rust-lang/rustc-hash/pull/37>
  - <https://github.com/rust-lang/rustc-hash/pull/50>
  - <https://github.com/rust-lang/rust/issues/69153#issuecomment-589338446>
  - <https://raw.githubusercontent.com/nnethercote/perf-book/master/src/hashing.md>
  - <https://crates.io/api/v1/crates/rustc-hash>
  - <https://raw.githubusercontent.com/tkaitchuck/aHash/master/compare/readme.md>
- **Sources the enricher read:**
  - <https://github.com/rust-lang/rustc-hash>
  - <https://github.com/rust-lang/rustc-hash/blob/main/README.md>
  - <https://github.com/rust-lang/rustc-hash/blob/main/Cargo.toml>
  - <https://github.com/rust-lang/rustc-hash/blob/main/CHANGELOG.md>
  - <https://github.com/rust-lang/rustc-hash/blob/main/src/lib.rs>
  - <https://github.com/rust-lang/rustc-hash/blob/main/src/random_state.rs>
  - <https://github.com/rust-lang/rustc-hash/blob/main/src/seeded_state.rs>
  - <https://github.com/rust-lang/rustc-hash/blob/main/.github/workflows/rust.yml>
  - <https://github.com/rust-lang/rustc-hash/issues>
  - <https://github.com/rust-lang/rustc-hash/issues/14>
  - <https://github.com/rust-lang/rustc-hash/issues/17>
  - <https://github.com/rust-lang/rustc-hash/issues/26>
  - <https://github.com/rust-lang/rustc-hash/issues/45>
  - <https://github.com/rust-lang/rustc-hash/issues/58>
  - <https://github.com/rust-lang/rustc-hash/issues/59>
  - <https://github.com/rust-lang/rustc-hash/issues/68>
  - <https://github.com/rust-lang/rustc-hash/issues/73>
  - <https://github.com/rust-lang/rustc-hash/pull/37>
  - <https://github.com/rust-lang/rustc-hash/pull/50>
  - <https://github.com/rust-lang/rustc-hash/pull/55>
  - <https://github.com/rust-lang/rust/issues/69153>
  - <https://github.com/rust-lang/rust/issues/69153#issuecomment-589338446>
  - <https://github.com/rust-lang/rust/pull/69152>
  - <https://github.com/rust-lang/rust/issues/135477>
  - <https://github.com/rust-lang/rust/issues/135477#issuecomment-2614419872>
  - <https://github.com/rust-lang/rust/pull/136605>
  - <https://raw.githubusercontent.com/rust-lang/rust/master/library/std/src/collections/hash/map.rs>
  - <https://raw.githubusercontent.com/nnethercote/perf-book/master/src/hashing.md>
  - <https://nnethercote.github.io/2021/12/08/a-brutally-effective-hash-function-in-rust.html>
  - <https://raw.githubusercontent.com/tkaitchuck/aHash/master/compare/readme.md>
  - <https://github.com/orlp/foldhash/blob/master/README.md>
  - <https://crates.io/api/v1/crates/rustc-hash>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/rust-lang/rustc-hash`) · [data/wave7/enrich/raw/github_com_rust_lang_rustc_hash.json](../../../data/wave7/enrich/raw/github_com_rust_lang_rustc_hash.json) (enrichment confidence 0.8)

</details>
