# QuickPHF

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0 OR Zlib` · 🟡 stale

> Rust PTHash-based static maps/sets generated at build time; \~2x faster lookups and 10x+ faster generation than phf.

| | |
|---|---|
| **Beats** | phf (rust-phf) static compile-time hash maps |
| **Claimed result** | quickphf/README.md: "About twice as fast as phf at lookup, and more than 10 times faster at construction"; "quickphf is about twice as fast as phf at lookup, with RawPhfMap being faster than PhfMap, especially for larger hash maps." quickphf_codegen/README.md: "about 10 times faster than with phf. It can generate a 1,000,000 entry map in about 300 ms." Approximate values read from the lookup.png and generate.png charts (derived from page data): lookup at 1M keys is phf::Map \~153 ns vs PhfMap \~86 ns (\~1.8x) vs RawPhfMap \~32 ns (\~4.8x); at &lt;=1k keys it is \~23 vs \~11 vs \~10 ns (\~2.1x for PhfMap). Construction at 1M keys is phf \~6.2 s vs quickphf \~0.26 s (\~24x), and at 500k keys \~1.9 s vs \~0.13 s (\~15x). The construction ratio grows with key count. |
| **Workload** | Static compile-time maps built with the PTHash perfect-hash algorithm. benchmarks/build.rs generates u64-&gt;u64 maps (quickphf PhfMap and RawPhfMap, and phf::Map via phf_codegen) from seeded random u64 keys at 11 sizes from 5 to 1,000,000. lookup.rs (divan) times batches of 1000 random existing-key get() calls on each map. generate.rs times perfect-hash construction only (quickphf_codegen::phf::generate_phf vs phf_generator::generate_hash) at the same sizes. |
| **Metric** | latency |
| **Compiler and flags** | rustc version not stated; benchmarks/Cargo.toml [profile.bench] opt-level = 3, lto = true; divan 0.1 harness |
| **Adoption** | 25 stars |
| **Last commit** | 2023-11-22 |
| **Links** | [repository](https://github.com/dtrifuno/quickphf) · [benchmark](https://github.com/dtrifuno/quickphf/blob/main/quickphf/README.md) |

## Verdict

The author ran divan benchmarks (bench profile opt-level=3 with LTO; rustc, CPU and OS not stated) on random u64-&gt;u64 maps of 5 to 1M entries against phf 0.11.2's default CHD layout. The PNG charts show lookups at about 10 vs 23 ns per lookup up to 1k keys, and at 1M keys about 86 ns (PhfMap) and 32 ns (RawPhfMap) vs 153 ns. The PHF search alone takes about 0.26 s vs 6.2 s at 1M keys. The charts date from the 2023 initial commit, the committed lookup.rs no longer compiles, and because the query iterator is lazy, RNG calls and a random read from the key vector fall inside the timed loop.

## Use it when

- Rust code that already uses phf::Map or phf::Set for a build-time-known table (IDs, codes, config or protocol lookups) where lookup latency matters. The author's u64-&gt;u64 benchmark shows about 2x over phf 0.11.
- Large generated tables (100k-1M entries) where phf's build step is slow. The author's chart puts the PHF search for 1M keys at about 0.26 s versus about 6.2 s for phf, not counting rustc time on the generated source.
- Lookups whose keys are guaranteed members (validated upstream, or a closed input set). RawPhfMap skips the stored-key compare and the key storage, and was charted at about 32 ns versus 153 ns for phf at 1M u64 keys.
- no_std, embedded or forbid(unsafe) codebases. The runtime crate is #![no_std], contains no unsafe code, never allocates, and tables are &'static slices.
- Memory-tight static tables. Overhead is one u16 pilot per bucket plus one u32 per spare slot, which the README describes as less than a byte per entry. My arithmetic from phf.rs gives about 0.7 B/key at 1M keys, rising above 1 B/key for maps of about 10 keys.

## Skip it when

- Cross-compiling where the build host and the target differ in endianness, or in pointer width when keys are usize/isize. Tables are built with core::hash::Hash through wyhash, and the README warns this is not portable. phf's PhfHash is explicitly architecture-independent.
- You want inline literal maps through a macro (phf_map!, lute map!, hashify map!). quickphf only has the build.rs codegen path that writes out source.
- Maps that can be queried with arbitrary or untrusted keys through RawPhfMap. A missing key silently returns some other entry's value, so use PhfMap for those.
- You need an actively maintained crate or evidence beyond integer keys. It is at 0.1.x with no commits since Nov 2023, only u64 keys were benchmarked (no strings), and the comparison was against phf 0.11.2, not phf 0.14's experimental ptrhash layout.
- Tables that change at runtime or have multi-million entries. Maps are immutable, every change means regenerating and recompiling, and the codegen source notes that rustc cannot handle static maps of more than a few million entries.

## How it is fast

It implements the PTHash minimal perfect hash (arXiv 2104.10402). Each key is hashed once with wyhash. bucket = h mod B, with about (1.5+0.2\*log2 n)\*n/log2 n buckets. Each bucket stores a 16-bit pilot, and the slot is (h XOR pilot\*K) mod m at a 0.97-0.99 load factor. Slots at or beyond n are redirected through a small u32 `free` array, which makes the table minimal. Both modulo operations use quickdiv's libdivide-style precomputed divisors instead of hardware division. phf's default CHD layout (per phf_shared) uses 128-bit SipHash-1-3, a pair of u32 displacements per bucket, and plain `%`, so quickphf's lookup path is shorter and its bucket table smaller. Construction sorts buckets largest-first, brute-forces a pilot in 0..=65535 for each bucket, and reseeds if that fails.

## Compared with alternatives

Choose it over lute when a table exceeds lute's 65,535-entry cap or needs RawPhfMap's keyless storage. Choose it over hashify when keys are typed values such as u64, tuples or custom types generated from data in build.rs, rather than literals written into a macro and looked up as byte slices. Stay with lute, hashify or phf 0.14 if you need portable hashing, macros or active maintenance.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | quickphf (runtime): quickdiv 0.1.1 and wyhash 0.5.0 (which pulls in rand_core 0.6). quickphf_codegen, used as a build-dependency: quickdiv and quickphf. |
| **Minimum toolchain** | Rust 1.56 (declared MSRV, edition 2021; CI runs `cargo +1.56.0 check`) |
| **Platforms** | Any target: pure safe Rust, no_std runtime, no arch-specific code. The build host and the target must share endianness, and also pointer width if keys are usize/isize. |
| **Thread safety** | Immutable static data with no interior mutability. The types are Sync when K and V are (unit tests assert Sync for u64 instantiations), so concurrent reads are safe. |
| **Drop-in for the baseline** | partial — the lookup API is close to phf::Map/Set and to read-only HashMap/HashSet. You must still switch generation to quickphf_codegen in build.rs (there is no phf_map! equivalent), make key and value types implement ConstInstantiable and std Hash instead of phf's traits, and do without an Index impl and without IntoIterator on &PhfMap. |

## Gotchas

- PhfSet::get and PhfSet::contains take &K with no Borrow&lt;Q&gt; bound, so a PhfSet&lt;&'static str&gt; cannot be queried with a &String or any other non-'static &str. PhfMap does accept Borrow. The fix (PR #4) has been open and unmerged since Feb 2024.
- The build.rs example in the README does not compile as written: it calls `fs::File` without importing `fs`, and `write!(&mut file, code)` has no format string. Use `write!(file, "{}", code)` or `fs::write(path, code.to_string())`, which is what benchmarks/build.rs does.
- ConstInstantiable is implemented only for integer primitives, bool, char, &str, (), tuples of up to 4 elements, Option and Result. It has no impl for arrays, slices, byte strings, String or floats, so values of those types need a newtype (orphan rule). The array/slice impl (PR #5) is unmerged.
- Codegen panics on duplicate keys. RawPhfMap::get panics on an empty map.

## Caveats and trade-offs

The benchmark harness is public (benchmarks/benches/lookup.rs and generate.rs, divan, bench profile opt-level=3 with LTO). The CPU model, OS and rustc version are not stated, and results appear only as PNG charts with no text or CSV. Both charts date from the initial commit (e8d22e2, 2023-10-16). The current lookup.rs was changed by PR #1 (096658a, 2023-11-16) and is missing semicolons after `let mut rng = fastrand::Rng::with_seed(SEED)`, so it does not compile unmodified. CI does not catch this because benchmarks/ is excluded from the workspace. The lookup chart is labelled in ns, but each divan iteration runs 1000 lookups, so the per-lookup normalization is undocumented. The construction benchmark measures only the build-time PHF parameter search, not runtime cost. Only random u64 keys are benchmarked, with no string keys. The baseline is the phf crate (the Rust analogue of gperf-style static tables), not std::collections::HashMap.

no_std, forbids unsafe code; RawPhfMap does not store keys (returns arbitrary answer on invalid query, so caller must guarantee key validity); requires build-time codegen via the separate quickphf_codegen crate.

## Maintenance

Stale: the last commit was 2023-11-22, the runtime crate is still 0.1.0 (2023-10-16, about 3.4k downloads), and three community PRs have been open since early 2024. The code is small, safe Rust under MIT/Apache-2.0/Zlib, so it is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The project's own divan benchmarks (benchmarks/benches/lookup.rs and benchmarks/benches/generate.rs, against phf 0.11.2) are public, and benchmarks/Cargo.toml sets the bench profile to opt-level=3 with lto=true. No rustc version, CPU model or OS is stated, results exist only as PNG charts, and no independent or peer-reviewed comparison was found, so the tier is C.
- **Verifier notes:** The record's benchmark_url (the root README.md) has no performance text. The quoted claim and the lookup chart are in quickphf/README.md, and the construction claim and chart are in quickphf_codegen/README.md, so benchmark_url was re-pointed. The last commit on main is 2023-11-22 (b9a6abd); 2024-02-10 is only the repo's pushed_at date, and the project remains stale. Other checks: 25 stars, not a fork, not archived. crates.io shows about 3.4k total downloads for quickphf and about 4.0k for quickphf_codegen. The license is triple MIT/Apache-2.0/Zlib per Cargo.toml and the LICENSE files (the GitHub spdx field shows only Apache-2.0).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `last_commit`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dtrifuno/quickphf>
  - <https://github.com/dtrifuno/quickphf/blob/main/README.md>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf/README.md>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf_codegen/README.md>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/Cargo.toml>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/build.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/src/lib.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/benches/lookup.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/benches/generate.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/lookup.png>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/generate.png>
  - <https://github.com/dtrifuno/quickphf/blob/main/.github/workflows/check.yml>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf/Cargo.toml>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf_codegen/Cargo.toml>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf_codegen/CHANGELOG.md>
  - <https://github.com/dtrifuno/quickphf/commit/096658a>
  - <https://crates.io/api/v1/crates/quickphf>
  - <https://crates.io/api/v1/crates/quickphf_codegen>
- **Sources the enricher read:**
  - <https://github.com/dtrifuno/quickphf>
  - <https://github.com/dtrifuno/quickphf/blob/main/README.md>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf/README.md>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf_codegen/README.md>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf/src/lib.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf/src/shared.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf/src/map.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf/src/raw_map.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf/src/set.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf/Cargo.toml>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf_codegen/Cargo.toml>
  - <https://github.com/dtrifuno/quickphf/blob/main/Cargo.toml>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf_codegen/src/lib.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf_codegen/src/phf.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf_codegen/src/const_instantiable.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/quickphf_codegen/CHANGELOG.md>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/Cargo.toml>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/build.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/src/lib.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/benches/lookup.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/benches/generate.rs>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/lookup.png>
  - <https://github.com/dtrifuno/quickphf/blob/main/benchmarks/generate.png>
  - <https://github.com/dtrifuno/quickphf/blob/main/.github/workflows/check.yml>
  - <https://github.com/dtrifuno/quickphf/commit/096658a>
  - <https://github.com/dtrifuno/quickphf/commits/main>
  - <https://github.com/dtrifuno/quickphf/issues/2>
  - <https://github.com/dtrifuno/quickphf/pull/1>
  - <https://github.com/dtrifuno/quickphf/pull/3>
  - <https://github.com/dtrifuno/quickphf/pull/4>
  - <https://github.com/dtrifuno/quickphf/pull/5>
  - <https://crates.io/api/v1/crates/quickphf>
  - <https://crates.io/api/v1/crates/quickphf_codegen>
  - <https://crates.io/api/v1/crates/phf>
  - <https://github.com/rust-phf/rust-phf>
  - <https://github.com/rust-phf/rust-phf/blob/master/phf_shared/src/lib.rs>
  - <https://github.com/rust-phf/rust-phf/blob/master/phf_shared/src/ptrhash.rs>
  - <https://github.com/eldruin/wyhash-rs/blob/v0.5.0/Cargo.toml>
  - <https://github.com/eldruin/wyhash-rs/blob/v0.5.0/src/traits.rs>
  - <https://github.com/eldruin/wyhash-rs/blob/v0.5.0/src/lib.rs>
  - <https://github.com/dtrifuno/quickdiv>
  - <https://github.com/astral4/lute>
  - <https://github.com/astral4/lute/blob/main/BENCHMARKS.md>
  - <https://github.com/stalwartlabs/hashify>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/dtrifuno/quickphf`) · [data/wave1-phf/enrich/raw/github_com_dtrifuno_quickphf.json](../../../data/wave1-phf/enrich/raw/github_com_dtrifuno_quickphf.json) (enrichment confidence 0.8)

</details>
