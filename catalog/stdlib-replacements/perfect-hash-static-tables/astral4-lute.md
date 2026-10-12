# lute

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust no_std perfect-hash immutable Map/Set (up to 65,535 keys) with 1.9x-16.9x lower query time than phf.

| | |
|---|---|
| **Beats** | phf (rust-phf) static compile-time hash maps |
| **Claimed result** | Query (derived from page data: values read from the SVG plot marker coordinates against the labeled log-scale axes; lute 0.1.0 vs phf 0.14.0; u64, short-string and long shared-prefix-string keys; n=1..65535; hits and misses): Median isolated per-query latency is 1.9x-9.8x lower than phf. On the Ryzen 9 9950X the range is 2.6x-9.8x, e.g. u64 n=2048 hit \~1.73 ns vs \~8.04 ns and long strings n=65535 hit \~11.4 ns vs \~30.6 ns. On the Apple M1 Pro the range is 1.9x-9.7x. Median amortized time per query is 1.9x-16.9x lower (9950X 2.6x-10.4x; M1 Pro 1.9x-16.9x, largest for u64 at n&lt;=10). Lute is faster than phf at every plotted point in both query charts. Construction (the PHF-search time only) is mixed. Lute is 2.7x-8.3x faster at n=1-4 (up to \~10.5x for u64 n=8) and about even to \~2.3x faster for u64 sets with n&gt;=4096. It is slower at many other sizes, e.g. about 0.5x-0.8x of phf's speed for short strings at n=128-16384 on the 9950X. The worst spike is \~120x slower (long strings, n=9, 9950X: \~44.9 us vs \~0.37 us). |
| **Workload** | Immutable maps/sets for fixed collections of up to 65535 entries, which can be built at compile time with macros or build-script codegen. BENCHMARKS.md has plots for three key types: u64, short strings and long shared-prefix strings. The plotted sizes are n=1..65535 (25 sizes). The plots cover PHF-search construction time, median isolated per-query latency (#[inline(never)]) and median amortized time per query (a shuffled all-hit or all-miss stream), all vs the phf crate. In the benchmark, the phf maps are built at runtime to mirror what phf_codegen emits. |
| **Metric** | latency |
| **Hardware** | Apple M1 Pro (8-core); AMD Ryzen 9 9950X |
| **Compiler and flags** | cargo bench with the divan harness and the default bench profile. The rustc version and RUSTFLAGS are not stated; the workspace MSRV is rust-version 1.88. |
| **Adoption** | 4 stars |
| **Last commit** | 2026-08-18 |
| **Links** | [repository](https://github.com/astral4/lute) · [benchmark](https://github.com/astral4/lute/blob/main/BENCHMARKS.md) |

## Verdict

The author ran divan benchmarks on an Apple M1 Pro and an AMD Ryzen 9 9950X (rustc version and flags not stated), comparing lute 0.1.x with phf 0.14 maps assembled at runtime from phf_generator output. Keys were u64, short strings and 78-byte shared-prefix strings at n=1-65,535. Values read from the SVG plots show median isolated lookups 1.9x-9.8x faster than phf and amortized per-query time 1.9x-16.9x faster at every plotted point (e.g. u64 n=2048 hit \~1.73 ns vs \~8.04 ns on the 9950X), while PHF search time ranges from \~10x faster to \~120x slower. The plotted code replays queries in key-generation order (shuffling was added later), and the plots predate the main branch's pilot/packed rewrite.

## Use it when

- Read-only lookup tables known ahead of time (keywords, opcode/MIME/unit tables, u64 ID sets) where you use phf today and query latency matters: the author's plots show lute faster than phf at every plotted size from 1 to 65,535 keys.
- Tiny tables of about 2-10 keys, where the gap is widest (up to \~16.9x lower amortized time per u64 query on the M1 Pro) because the lookup skips the displacement table entirely.
- Miss-heavy membership tests such as 'is this token reserved?': a miss costs one hash plus one comparison, and lute beat phf on all-miss streams as well as all-hit streams.
- no_std (+alloc) targets that need a table in a `static` or `const`, built by a proc macro or build.rs with no runtime construction cost.
- Keys that are tuples, arrays, ranges, chars, byte strings or C strings (all accepted as literals by map!/set!), or any `Hash + Eq` type when the map is built at runtime or emitted from build.rs with a databake `Bake` impl.

## Skip it when

- More than 65,535 entries: this is a hard limit (u16 indices). Runtime construction panics and the macros emit a compile error.
- Build-time or startup construction speed is the priority. PHF search is not reliably faster than phf: about 0.5x-0.8x of phf's speed for short strings at n=128-16,384 on the 9950X, and \~120x slower for long strings at n=9 (\~44.9 us vs \~0.37 us). The 0.1.x 'direct' strategy for n&lt;=10 tries up to 65,536 seeds and rehashes every key on each try.
- Cross-compiled tables whose keys contain usize/isize, arrays/slices, byte strings, C strings or multibyte-integer arrays, because their hashes depend on pointer width or endianness. map!/set! add a const assertion that fails the build, but build.rs codegen output (bake.rs) has no such guard, so a mismatched target silently returns None for present keys.
- You need insertion, mutation, or ordered/sorted iteration: maps are immutable and iteration order is unspecified.
- You need proven maturity: one author, 4 stars, 39 crates.io downloads, no independent reproduction, and the main branch has an unreleased algorithm rewrite whose performance has no published plots.

## How it is fast

In the benchmarked 0.1.x release, each query hashes the key once with foldhash, a fast non-cryptographic hasher, where phf_shared uses 128-bit SipHash-1-3. One-entry maps use a linear scan. Maps of up to 10 keys use a 'direct' single-seed perfect hash that needs one multiply-shift (fastrange) and no displacement table. Larger maps use CHD (compress-hash-displace) with a (u16, u16) displacement pair per \~4 keys and a division-free 'fastmod' reduction with a precomputed multiplier, where phf uses `%`. The unreleased main branch replaces this with a PTHash/PtrHash-style scheme: a 16-bit pilot per bucket of \~3 keys, power-of-two bucket selection by shift, and \~1% slack slots remapped back. For n&lt;=12 it uses a 'packed' 16-slot table indexed by one bit window of the hash. Every lookup ends in exactly one key comparison, so a miss costs about the same as a hit.

## Compared with alternatives

Compared with QuickPHF (README: about 2x phf on lookups and more than 10x faster construction), pick lute when per-query latency matters more than table-generation time, or when you want runtime, proc-macro and build.rs construction from one API with tuple/array/range literal keys. Pick QuickPHF when fast build-time generation matters. Pick hashify for pure string-keyed `match` replacement. There are no head-to-head numbers between lute and either sibling.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | foldhash (always); rand_core + rand_xoshiro with the default `construct` feature (0.1.x also pulls hashbrown for duplicate detection); databake + proc-macro-crate with `codegen`; the lute_macros proc-macro crate (syn, quote, proc-macro2, proc-macro-crate) with `macros` |
| **Minimum toolchain** | Rust 1.88 (edition 2024, rust-version = 1.88) |
| **Platforms** | any Rust target; no_std but requires alloc; no SIMD or architecture-specific code in lute_core |
| **Thread safety** | Not documented. Maps are immutable after construction, and the benchmark harness requires `Map<K, usize>: Sync` (satisfied for u64 and String keys), so concurrent reads work when K and V are Sync. |
| **Drop-in for the baseline** | partial — same role and similar get/contains_key/Index API, but different types and macros (lute::Map, map!/set!, Map::to_tokens in build.rs), keys use std Hash + Eq instead of phf's PhfHash, and declarations must be rewritten. |

## Gotchas

- map!/set! accept only literal-shaped keys. Integer keys need a type suffix (`2u32`, not `2`), and floats, named constants, enum variants and custom structs are rejected. Use build.rs codegen for those.
- Runtime construction (From/FromIterator) panics instead of returning a Result. It panics on duplicate keys, on more than 65,535 entries, or when no perfect hash is found within 256 seeds (for example when `Hash` is inconsistent with `Eq`).
- Generated tables are not stable across breaking versions. The main branch already changed `from_baked_parts` from displacement pairs to a pilots/packed `BakedStrategy`, so regenerate any generated code you committed after upgrading.
- The main-branch lookup uses unsafe `get_unchecked` for pilot, remap and entry indexing and relies on const-time validation in `from_baked_parts`. The released 0.1.1 lookup uses bounds-checked indexing.

## Caveats and trade-offs

The numbers exist only as SVG plots, with the text converted to glyph paths. The values in claimed_speedup were read from the plot marker coordinates, so they are approximate. The rustc version and flags are not stated. The plots are dated 2026-06-22 (lute 0.1.0/0.1.1, phf 0.14.0) and match the benchmark code at commit d7f32c21a0. Since then, the unreleased HEAD has replaced CHD displacement with a PTHash/PtrHash-style pilot table and a 'packed' strategy and changed the benchmark sizes, so the plots do not reflect HEAD. HEAD also adds a hashbrown comparison, which has no published plots. Construction time is not a win over phf. GitHub reports only Apache-2.0, but Cargo.toml and the README declare MIT OR Apache-2.0, and both LICENSE files are present. The project is first-party with 4 stars, and the results have not been reproduced independently.

Limited to at most 65535 entries; keys must hash identically across build and target platforms (pointer width and endianness sensitive) when using compile-time-embedded maps, which affects cross-compilation portability.

## Maintenance

Active single-author project (last commit 2026-08-18; 0.1.1 on crates.io since 2026-06-22; no issues filed). It is MIT OR Apache-2.0 and a small pure-Rust workspace that is easy to vendor, but main holds an unreleased algorithm rewrite, so pin 0.1.1 unless you have re-benchmarked HEAD.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Benchmark code is public (crates/lute/benches/common/mod.rs, lute.rs and phf.rs at commit d7f32c21a0, using divan), and BENCHMARKS.md names both CPUs. The rustc version and flags are not stated, so this is first-party with partial methodology: C.
- **Verifier notes:** The record said the plot numbers could not be extracted. I recovered them by rendering the six SVGs and reading the marker coordinates on the labeled log axes, calibrated to the 1 ns/10 ns and 10 ns/100 ns gridlines. Lute wins on every query point by 1.9x-16.9x, while construction is mixed. Tier C holds because the toolchain and flags are missing. Metadata is correct: license MIT OR Apache-2.0, 4 stars, last commit 2026-08-18, active, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/astral4/lute>
  - <https://github.com/astral4/lute/blob/main/BENCHMARKS.md>
  - <https://github.com/astral4/lute/blob/main/README.md>
  - <https://github.com/astral4/lute/blob/main/Cargo.toml>
  - <https://github.com/astral4/lute/blob/main/CHANGELOG.md>
  - <https://github.com/astral4/lute/blob/main/crates/lute/Cargo.toml>
  - <https://github.com/astral4/lute/blob/main/crates/lute/benches/common/mod.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute/benches/common_construct/mod.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute/benches/lute.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute/benches/phf.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute/benches/hashbrown.rs>
  - <https://github.com/astral4/lute/blob/main/plots/construct-search_9950x.svg>
  - <https://github.com/astral4/lute/blob/main/plots/construct-search_m1.svg>
  - <https://github.com/astral4/lute/blob/main/plots/query-amortized_9950x.svg>
  - <https://github.com/astral4/lute/blob/main/plots/query-amortized_m1.svg>
  - <https://github.com/astral4/lute/blob/main/plots/query-isolated_9950x.svg>
  - <https://github.com/astral4/lute/blob/main/plots/query-isolated_m1.svg>
  - <https://github.com/astral4/lute/blob/d7f32c21a0/crates/lute/benches/common/mod.rs>
  - <https://github.com/astral4/lute/blob/d7f32c21a0/crates/lute/benches/lute.rs>
  - <https://github.com/astral4/lute/blob/d7f32c21a0/crates/lute/benches/phf.rs>
  - <https://github.com/astral4/lute/commits/main>
- **Sources the enricher read:**
  - <https://github.com/astral4/lute>
  - <https://github.com/astral4/lute/blob/main/README.md>
  - <https://github.com/astral4/lute/blob/main/BENCHMARKS.md>
  - <https://github.com/astral4/lute/blob/main/CHANGELOG.md>
  - <https://github.com/astral4/lute/blob/main/Cargo.toml>
  - <https://github.com/astral4/lute/blob/main/crates/lute/Cargo.toml>
  - <https://github.com/astral4/lute/blob/main/crates/lute_core/Cargo.toml>
  - <https://github.com/astral4/lute/blob/main/crates/lute_macros/Cargo.toml>
  - <https://github.com/astral4/lute/blob/main/crates/lute/src/lib.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute_core/src/lib.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute_core/src/kernel.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute_core/src/strategy.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute_core/src/map.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute_core/src/construct/mod.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute_core/src/construct/pilots.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute_core/src/construct/packed.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute_core/src/bake.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute_macros/src/lib.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute/benches/common/mod.rs>
  - <https://github.com/astral4/lute/blob/main/crates/lute/benches/hashbrown.rs>
  - <https://github.com/astral4/lute/blob/v0.1.1/crates/lute_core/Cargo.toml>
  - <https://github.com/astral4/lute/blob/v0.1.1/crates/lute_core/src/lib.rs>
  - <https://github.com/astral4/lute/blob/v0.1.1/crates/lute_core/src/kernel.rs>
  - <https://github.com/astral4/lute/blob/v0.1.1/crates/lute_core/src/construct.rs>
  - <https://github.com/astral4/lute/blob/v0.1.1/crates/lute_core/src/map.rs>
  - <https://github.com/astral4/lute/blob/v0.1.1/crates/lute/benches/common/mod.rs>
  - <https://github.com/astral4/lute/blob/v0.1.1/crates/lute/benches/lute.rs>
  - <https://github.com/astral4/lute/blob/v0.1.1/crates/lute/benches/phf.rs>
  - <https://github.com/astral4/lute/blob/d7f32c21a0/crates/lute/benches/common/mod.rs>
  - <https://github.com/astral4/lute/compare/d7f32c21a0...c5b06710e1>
  - <https://github.com/astral4/lute/commits/main>
  - <https://github.com/astral4/lute/tags>
  - <https://github.com/astral4/lute/issues>
  - <https://github.com/rust-phf/rust-phf/blob/HEAD/phf_shared/src/lib.rs>
  - <https://github.com/rust-phf/rust-phf/blob/HEAD/phf_generator/src/lib.rs>
  - <https://crates.io/api/v1/crates/lute>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/astral4/lute`) · [data/wave1-phf/enrich/raw/github_com_astral4_lute.json](../../../data/wave1-phf/enrich/raw/github_com_astral4_lute.json) (enrichment confidence 0.75)

</details>
