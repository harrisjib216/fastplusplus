# rust-phf (compile-time perfect hash maps)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust crates that bake immutable perfect-hash maps and sets into the binary at compile time, removing runtime HashMap construction.

| | |
|---|---|
| **Beats** | std::collections::HashMap (Rust) populated at runtime from statically bundled (code-generated) data |
| **Claimed result** | PR #18 (Turbo87, merged 2021-10-11): with rust-phf generating both lookup tables at build time, Types::new() becomes 'an essentially empty function' that 'now runs in 3ns instead of 300ms' (first-party, no methodology). The Mainmatter post's 'roughly 80% performance improvement' belongs to the earlier code-generation step (PR #17, which still filled HashMaps at runtime), not to rust-phf. For the rust-phf step, the post says only that initialization time dropped to 'essentially zero' and that lookups got faster, with no numbers. |
| **Workload** | Initializing conduit-mime-types' extension-to-MIME-type and MIME-type-to-extension lookup tables (Types::new()). Before PR #18, statically bundled, code-generated data was inserted into two std::collections::HashMap at runtime; JSON parsing had already moved to development time in PR #17. After PR #18, phf_codegen in build.rs emits two compile-time phf maps, so initialization is essentially empty. |
| **Metric** | startup |
| **Adoption** | 2,193 stars; used by conduit-mime-types, a crates.io server dependency according to the 2022 Mainmatter post (the conduit-mime-types repo is now archived) |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/rust-phf/rust-phf) · [benchmark](https://github.com/conduit-rust/conduit-mime-types/pull/18) |

## Verdict

The only rust-phf-specific number is first-party, from conduit-mime-types PR #18 (Tobias Bieniek, merged 2021-10-11). Replacing runtime insertion of bundled MIME data into two std::collections::HashMaps with two phf_codegen-generated static maps made Types::new() run in '3ns instead of 300ms'. No hardware, compiler or methodology is given, and the Criterion bench was deleted in the same PR. It measures initialization moved to build time, not lookup speed; the Mainmatter post's \~80% figure belongs to the earlier non-phf codegen step (PR #17).

## Use it when

- Fixed lookup tables known at build time (keywords, MIME types, HTML entities, charset or Unicode names) that you now fill into a HashMap in lazy_static/OnceLock: init cost and heap allocation drop to zero. In conduit-mime-types, Types::new() went from a reported 300 ms to 3 ns.
- Short-lived processes, CLIs, cold-start-sensitive services, and no_std/embedded targets, where you cannot or do not want to run initializers or allocate. The runtime crate builds with default-features = false.
- Tables generated from data files at build time via phf_codegen in build.rs. Generation cost is paid by the build: the maintainer measured 6.2 ms to solve 10,000 keys with CHD, and hashify's measurements show about 3 s of added build time at 100k keys and 42 s at 1M.
- You need a first-class static map value: iterate entries or keys in fixed order, use OrderedMap/OrderedSet for index order, call get_key for interning, serialize via serde, or key by case-insensitive strings through unicase/uncased.
- Cross-compiled builds: PhfHash is designed to be architecture-independent (portable SipHasher, fixed-endian integer hashing), so tables generated on the host are valid on the target.

## Skip it when

- Hot-path lookups where per-lookup latency matters. Every lookup runs SipHash-1-3 (128-bit) plus a modulo. A 2023 users.rust-lang.org Criterion test at 100 string keys had phf::Map about 10% slower than std HashMap (8.61-8.79 us vs 7.74-7.86 us per 229-lookup batch). A 2025 rust-phf issue (#349) says the crate is 'almost always slower than hashmap' at lookup.
- Small keyword sets, where a plain `match` wins. hashify's README (Apple M5 Max, Rust 1.98) measures match hits at 1.3-2.8 ns vs 8.6-9.7 ns for phf at 9-149 keys. phf only beats match on its 2,125-key set (9.1 ns vs 25.1 ns).
- Keys or values not known when you build, or tables that must change at runtime. Maps are immutable; to add or remove a key you regenerate and recompile.
- Key types outside PhfHash (arbitrary structs, enum keys: open issue #196), or macro keys computed by const expressions (open issue #188, blocked on const traits). Every phf_map! key must use the same literal shape.
- Huge phf_map! invocations in a crate you rebuild often: the proc macro reruns on every compile of that crate. Put big tables in their own crate or generate them with phf_codegen.

## How it is fast

The gain is at startup. The table is solved at build time and stored as `&'static` slices in the binary's read-only data, so nothing is allocated or hashed when the program loads. The default layout is CHD (Compress, Hash, Displace; Belazzougui, Botelho and Dietzfelbinger, ESA 2009): a SipHash-1-3 128-bit hash of the key is split into g, f1 and f2. g picks a bucket (about 3 keys per bucket), and that bucket's stored displacement pair (d1, d2) gives the slot (d2 + f1\*d1 + f2) mod n. One key comparison then decides hit or miss. The experimental `ptrhash` feature switches to a PtrHash-style layout (8-bit pilot per bucket, Lemire multiply-shift range reduction, a remap array for the \~1% spare slots), which the maintainer measured at 26-35% higher lookup throughput than CHD. Neither layout is inherently faster per lookup than std HashMap, because the SipHash cost dominates.

## Compared with alternatives

hashify, the only other Rust entry, looks up keys 4.1-12.6x faster than phf's default layout on its own Apple M5 Max benchmark. Its macros, though, return a lookup result in expression position over byte-slice keys and do not document iteration. Pick rust-phf when you need a named static Map/Set you can iterate, serialize or intern through, tuple keys, Unicode case-insensitive keys, or build.rs generation from data files. For C++ code use frozen, mph or constexpr-phf instead, since rust-phf is Rust-only.

## Integration

| | |
|---|---|
| **Form** | crate (phf runtime + phf_macros proc-macro via the `macros` feature, or phf_codegen as a build-dependency) |
| **Dependencies** | phf -&gt; phf_shared -&gt; siphasher; optional serde, unicase, uncased; `macros` adds phf_macros (syn, quote, proc-macro2, phf_generator -&gt; fastrand); phf_codegen build-dep pulls phf_generator + phf_shared (quote/proc-macro2 optional) |
| **Minimum toolchain** | Rust 1.85 (MSRV, edition 2024) for phf 0.14; the in-repo phf-vs-HashMap lookup bench needs nightly (#[bench]) |
| **Platforms** | Any Rust target including no_std (default-features = false); hashing is made endian/pointer-width independent for cross-compiling; CI runs only on ubuntu-latest (1.85, stable, nightly) |
| **Thread safety** | Not documented explicitly. A Map holds only a u64 seed and `&'static` slices, lookups take &self, and a Rust `static` must be Sync, so concurrent reads need no locks. |
| **Drop-in for the baseline** | partial — read API mirrors HashMap (get/contains_key/Index/iteration) with borrowed lookup keys via PhfEq, but the map must be declared as a static through phf_map! or build.rs codegen, has no insert/remove, and only supports PhfHash key types |

## Gotchas

- phf_map! syntax is picky: integer literals in the first key must carry suffixes (0u32), and all keys must share the first key's expression type. OR patterns (`"+" | "add" => ...`) work in the macros but not in phf_codegen. Per-entry #[cfg] is handled by a decl-macro resolver since 0.14, after issue #356's overflow panic with many cfg'd entries, but a request for cfg support (#449) is still open, so test your case.
- The `ptrhash` feature changes the Map struct's fields (pilots/remap instead of disps). It must be enabled on both the generator (phf_codegen/phf_macros) and the runtime phf crate. Because Cargo unifies features, one build uses one layout.
- phf_codegen writes each value string verbatim as Rust source (you write "\"addition\"" for a &str value). build() panics on duplicate keys. The docs warn that 500+ chained .entry() calls overflow the compiler's stack; loop instead. The generated struct literal fills doc-hidden fields that 'are subject to change at any time', so keep phf and phf_codegen on the same version.
- `MAP[key]` (Index) panics with 'invalid key' on a miss. Use get() on untrusted input.

## Caveats and trade-offs

The numbers are a first-party anecdote from a PR description (3ns vs 300ms for Types::new()) with no hardware, compiler or timing methodology. The comparison moves work from run time to compile time; it does not compare lookup speed. The Mainmatter blog (Tobias Bieniek, 2022-06-23) gives no numbers for the rust-phf step. Its 80% figure is for the earlier codegen step, which does not use rust-phf. There is no comparison against C++ std::unordered_map or gperf; the comparison is Rust-only. The repo has a phf-vs-HashMap/BTreeMap/match microbenchmark (phf_macros_test/benches/bench.rs, nightly #[bench]) but no published results.

Map is immutable once built (must regenerate to add/remove keys); requires a build-time codegen step (phf_codegen) or macro; keys/set must be known at compile time; a separate Rust forum thread (users.rust-lang.org, "Why is phf::Map slower than std HashMap?") reports phf::Map losing to std HashMap for some small/medium key counts at pure lookup time, so the win is mainly on initialization/startup cost rather than guaranteed steady-state lookup latency.

## Maintenance

Actively maintained: 0.14.0 released 2026-06-21 and commits through 2026-09-17. MIT-licensed and very widely used (\~562M crates.io downloads, 1,176 reverse dependencies). The faster ptrhash layout is still marked experimental, and issue #458 proposes further tuning.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The only rust-phf-specific number is first-party, from conduit-mime-types PR #18: Types::new() 'now runs in 3ns instead of 300ms'. The PR gives no hardware, compiler or methodology, and the Criterion bench (benches/load-data.rs) was deleted in that same PR. The gain is implausible (about 10^8x) and the flags are unstated, so the tier is capped at C.
- **Verifier notes:** The record misattributed the Mainmatter '80%' figure to rust-phf; it belongs to the pre-phf codegen step (PR #17). The corrected benchmark_url points to PR #18, which has the only phf-specific number. That number is '3ns instead of 300ms', quoted verbatim. The 300ms unit looks suspicious after PR #17's 80% cut but could not be checked, so it is left as written. The tier stays at C and the metadata (MIT, 2026-09-17, active, not a fork) is confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `workload`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://mainmatter.com/blog/2022/06/23/the-perfect-hash-function/>
  - <https://github.com/conduit-rust/conduit-mime-types/pull/17>
  - <https://github.com/conduit-rust/conduit-mime-types/pull/18>
  - <https://github.com/conduit-rust/conduit-mime-types>
  - <https://github.com/rust-phf/rust-phf>
  - <https://github.com/rust-phf/rust-phf/blob/main/README.md>
  - <https://github.com/rust-phf/rust-phf/blob/main/LICENSE>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_macros_test/benches/bench.rs>
- **Sources the enricher read:**
  - <https://github.com/rust-phf/rust-phf>
  - <https://github.com/rust-phf/rust-phf/blob/main/README.md>
  - <https://github.com/rust-phf/rust-phf/blob/main/Cargo.toml>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf/src/lib.rs>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf/src/map.rs>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf/Cargo.toml>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf/CHANGELOG.md>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_shared/src/lib.rs>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_shared/src/hasher.rs>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_shared/src/ptrhash.rs>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_shared/Cargo.toml>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_shared/README.md>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_generator/src/lib.rs>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_generator/src/ptrhash.rs>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_generator/Cargo.toml>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_generator/README.md>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_generator/benches/benches.rs>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_codegen/src/lib.rs>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_codegen/Cargo.toml>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_macros/Cargo.toml>
  - <https://github.com/rust-phf/rust-phf/blob/main/phf_macros_test/benches/bench.rs>
  - <https://github.com/rust-phf/rust-phf/blob/main/.github/workflows/ci.yml>
  - <https://github.com/rust-phf/rust-phf/blob/main/.github/workflows/benches.yml>
  - <https://github.com/rust-phf/rust-phf/blob/main/.github/SECURITY.md>
  - <https://github.com/rust-phf/rust-phf/issues>
  - <https://github.com/rust-phf/rust-phf/issues/458>
  - <https://github.com/rust-phf/rust-phf/issues/449>
  - <https://github.com/rust-phf/rust-phf/issues/349>
  - <https://github.com/rust-phf/rust-phf/issues/356>
  - <https://github.com/rust-phf/rust-phf/issues/188>
  - <https://github.com/rust-phf/rust-phf/issues/132>
  - <https://github.com/rust-phf/rust-phf/issues/112>
  - <https://github.com/rust-phf/rust-phf/issues/88>
  - <https://github.com/rust-phf/rust-phf/pull/392>
  - <https://github.com/conduit-rust/conduit-mime-types>
  - <https://github.com/conduit-rust/conduit-mime-types/pull/17>
  - <https://github.com/conduit-rust/conduit-mime-types/pull/18>
  - <https://mainmatter.com/blog/2022/06/23/the-perfect-hash-function/>
  - <https://users.rust-lang.org/search.json?q=Why%20is%20phf%3A%3AMap%20slower%20than%20std%20HashMap>
  - <https://users.rust-lang.org/t/why-is-phf-map-slower-than-std-hashmap/97339>
  - <https://github.com/servo/string-cache/pull/307>
  - <https://github.com/stalwartlabs/hashify>
  - <https://crates.io/api/v1/crates/phf>
  - <https://crates.io/api/v1/crates/phf/reverse_dependencies>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/rust-phf/rust-phf`) · [data/wave1-phf/enrich/raw/github_com_rust_phf_rust_phf.json](../../../data/wave1-phf/enrich/raw/github_com_rust_phf_rust_phf.json) (enrichment confidence 0.82)

</details>
