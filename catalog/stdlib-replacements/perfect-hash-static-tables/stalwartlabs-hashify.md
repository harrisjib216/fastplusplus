# hashify

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust proc-macro that compiles fixed byte-string keyword sets into perfect-hash lookups; beats string `match` and the phf crate.

| | |
|---|---|
| **Beats** | switch/if-else chains |
| **Claimed result** | README Performance table (criterion median per lookup, Apple M5 Max, Rust 1.98). Against a plain Rust `match` with one string arm per key, hashify map! is faster on all five real key sets. HTTP methods (9 keys): 0.68 vs 1.34 ns hits, 1.53 vs 1.91 ns random. IMAP commands (26): 0.89 vs 1.73 ns hits, 1.37 vs 2.51 ns random. Sieve keywords (128): 1.77 vs 2.75 ns hits, 1.82 vs 7.54 ns random. Charset names (149): 1.93 vs 2.74 ns hits, 1.97 vs 7.80 ns random. HTML entities (2125): 1.85 vs 25.1 ns hits, 1.84 vs 39.8 ns random. That is about 1.25x-21.6x (derived from page data). The page states that map! is 4.1x-12.6x faster than phf 0.14 with its default CHD layout and 3.2x-8.8x faster than phf with its experimental ptrhash layout. |
| **Workload** | Median per-lookup time (criterion) on real key sets: HTTP methods (9), IMAP commands (26), Sieve keywords (128), charset names (149) and HTML entities (2125). Synthetic sets have 10k and 100k random 3-21-byte strings. 'hits' looks up every key once in list order. 'random' does 4096 pseudo-random lookups, half of them one-bit-off misses. Comparators are a plain Rust `match` (real key sets only), phf 0.14 CHD and phf 0.14 ptrhash (both with SipHash-1-3), and hashify map!/fnc_map!. |
| **Metric** | latency |
| **Hardware** | Apple M5 Max |
| **Compiler and flags** | Rust 1.98 (stated). `cargo bench --bench lookup`, with `cargo bench --bench lookup --features phf/ptrhash -- phf_ptrhash` for the phf ptrhash layout, run under Cargo's default bench profile (opt-level=3). Cargo.toml has no [profile] section and the repo has no .cargo/config. criterion 0.8. The page's opt-level = 3 note applies only to the proc-macro build-time table. |
| **Adoption** | 142 stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/stalwartlabs/hashify) · [benchmark](https://github.com/stalwartlabs/hashify/blob/main/README.md) |

## Verdict

The author's criterion benchmark (benches/lookup.rs, Apple M5 Max, Rust 1.98, default cargo bench profile at opt-level 3) times hashify map! against a Rust `match` with one string arm per key on five real key sets. Results run from 0.68 vs 1.34 ns (9 HTTP methods, hits) to 1.84 vs 39.8 ns (2125 HTML entities, random with half near-misses), about 1.25x-21.6x, plus 4.1x-12.6x over phf 0.14 CHD and 3.2x-8.8x over phf ptrhash; there is no C++ std or gperf comparison, and nobody has reproduced the results independently.

## Use it when

- Rust protocol or format parsers that dispatch on a fixed keyword set known at compile time. The benchmarked sets are HTTP methods, IMAP commands, Sieve keywords, charset names and HTML entities.
- Replacing a string `match` with more than \~100 arms. `match` measured 7.5-7.8 ns per random lookup at 128-149 keys and 25-40 ns at 2125 keys, against about 1.8-2 ns for hashify.
- Replacing phf_map!/phf_set! when the keys are literals. It was 4.1x-12.6x faster than phf 0.14 CHD in the author's benchmark, including the synthetic sets of 10k and 100k keys.
- Miss-heavy input such as tokenizing untrusted text. Half the probes in the random workload are one-bit-off misses, and hashify stays at about 1.0-2.2 ns per lookup.
- no_std, no-alloc or unsafe-forbidding code. The generated code uses only `core` paths, never allocates (tested with a counting allocator) and compiles under #![forbid(unsafe_code)].

## Skip it when

- C or C++ code. It is a Rust proc macro with no C ABI and no standalone code-generator output.
- Keys known only at runtime, built programmatically, or named by `const` items or enum variants. Only literal tokens are accepted ('unsupported key expression', issue #1), and there is no build.rs/codegen API (issue #2 is still open).
- Small sets of up to \~26 keys, where a plain `match` stays within 2x (1.34-2.51 ns) and needs no dependency.
- Very large key sets in a crate you rebuild often. The macro re-runs on every compile, incremental builds included, and 1,000,000 keys add about 24 s (15 s with build-override opt-level 3). A `fnc_map!` with 10,000 arms costs about 4 s of extra LLVM time in release builds.
- Case-insensitive matching beyond ASCII. The `_ignore_case` variants fold only A-Z, and all other bytes must match exactly.

## How it is fast

Keys of up to 16 bytes are packed into two u64 words (the first and last 8 bytes, which can overlap) plus the length. A hit is then confirmed with three integer compares, with no memcmp and no pointer chase. Longer keys go in a second table and are compared 8 bytes at a time. Up to 16 keys become a gperf --switch style decision tree on the length and one byte (or the XOR of two bytes). 17-64 keys get a collision-free power-of-two table with a searched seed (one multiply, a shift and a load). Larger sets get a PtrHash/PHast-style minimal perfect hash with one 8-bit pilot per bucket, found by a cuckoo-like eviction search. The hash is a cheap multiply-and-fold of the key words rather than the SipHash-1-3 that phf uses, and 32-bit targets get separate tables built from a 32-bit hash.

## Compared with alternatives

Every catalogued sibling is C++ (qlibs mph, constexpr-phf, frozen, ConstexprCore/perfect_hash, triehash and the other gperf alternatives), so pick hashify only when the lookup lives in Rust. There it fills the role constexpr-phf or mph fill in C++, and like constexpr-phf it is benchmarked directly against the switch/match baseline; for C++ code, use a sibling.

## Integration

| | |
|---|---|
| **Form** | crate (procedural macro) |
| **Dependencies** | none at runtime; syn 3.0, quote and proc-macro2 at build time |
| **Minimum toolchain** | Rust 1.88 (Cargo.toml rust-version), edition 2024 |
| **Platforms** | any Rust target; no architecture-specific code; 32-bit targets get separate 32-bit-hash tables via cfg(target_pointer_width) |
| **Thread safety** | not documented; the generated lookups only read immutable `static` tables, so any thread can call them |
| **Drop-in for the baseline** | partial — fnc_map! mirrors a string `match` (arms run lazily, and return/?/continue are allowed), but you have to rewrite the match as a macro call over bytes with literal keys; map!/set! replace phf_map!/phf_set! with different syntax |

## Gotchas

- Integer keys are matched against their big-endian bytes (`1u16` matches [0, 1]). `map!` values are stored in a `static`, so they must be constant expressions.
- 0.3.0 (2026-09-23) was a rewrite. The 0.2 `tiny_map!`/`tiny_set!` macros are gone, and the algorithm changed from FNV-1a + PTHash to the current scheme, so 0.2 users have to migrate. Separately, 0.2 releases before 0.2.8 produced non-reproducible builds (issue #4).
- Keep big lookups in their own crate and set `[profile.release.build-override] opt-level = 3`. Cargo compiles proc macros without optimization by default, which slows table construction (24.07 s vs 15.24 s at 1M keys).
- Table construction can fail with the compile error 'failed to resolve hash collision' once its seed and load-factor retries run out. Large or hard key sets may get up to 5% spare slots instead of a strictly minimal table.

## Caveats and trade-offs

The benchmark is first-party and no independent confirmation was found. hashify is a Rust proc-macro crate. Keys must be compile-time literals, and it cannot be called from C/C++. The lookup gains are measured against Rust `match` and the phf crate, not against std::unordered_map or gperf. `match` stays within 2x on the 9- and 26-key sets, and the big wins (13.6x-21.6x, derived) come on the 2125-key table. `match` is not measured on the synthetic sets. Build time: hashify compiles slower than phf at 1,000 keys (0.04 s vs 0.02 s), and the macro re-runs on every compile of the invoking crate. GitHub reports no SPDX license because the texts live in LICENSES/Apache-2.0.txt and LICENSES/MIT.txt. The README links LICENSE-APACHE/LICENSE-MIT files that do not exist, and Cargo.toml declares 'Apache-2.0 OR MIT'. The v0.3 rewrite and the benchmark refresh landed 2026-09-22..24.

Rust-only procedural macro; tables are built at proc-macro expansion time so a large key set adds real build time (up to \~24s for 1,000,000 keys, worse without opt-level=3); cannot rebuild tables at runtime; not usable from C++

## Maintenance

Actively maintained by Stalwart Labs: v0.3.1 reached crates.io on 2026-09-24 under MIT OR Apache-2.0, the crate has \~2.67M downloads and Stalwart's own mail-parser, mail-auth and sieve-rs crates depend on it, but the 0.3 rewrite is only days old and the crate can be reused only from Rust projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Performance table runs hashify against a plain Rust `match` with one string arm per key, which is the switch/if-else baseline, and against the phf 0.14 crate. The benchmark code is public in benches/lookup.rs (criterion; plain_match vs phf_map! vs hashify::map!/fnc_map!). The README states Rust 1.98, an Apple M5 Max and the exact `cargo bench --bench lookup` commands. The flags are Cargo's default bench profile (opt-level=3), because Cargo.toml has no [profile] override and the repo has no .cargo/config.
- **Verifier notes:** The quoted numbers are all on the README. The only numeric fix is that hashify's HTML-entity range is 1.84-1.95 ns (map! random is 1.84), not 1.85-1.95. The claim that hashify beats `match` only on larger sets understated it: hashify wins on every real set. Tier A holds, with flags inferred from Cargo defaults, because the repo has no profile or RUSTFLAGS overrides. The license (MIT OR Apache-2.0), 142 stars, last commit 2026-09-24 and active status all check out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/stalwartlabs/hashify>
  - <https://github.com/stalwartlabs/hashify/blob/main/README.md>
  - <https://github.com/stalwartlabs/hashify/blob/main/Cargo.toml>
  - <https://github.com/stalwartlabs/hashify/blob/main/benches/lookup.rs>
  - <https://github.com/stalwartlabs/hashify/tree/main/LICENSES>
  - <https://github.com/stalwartlabs/hashify/blob/main/LICENSES/Apache-2.0.txt>
  - <https://github.com/stalwartlabs/hashify/blob/main/LICENSES/MIT.txt>
- **Sources the enricher read:**
  - <https://github.com/stalwartlabs/hashify>
  - <https://github.com/stalwartlabs/hashify/blob/main/README.md>
  - <https://github.com/stalwartlabs/hashify/blob/main/Cargo.toml>
  - <https://github.com/stalwartlabs/hashify/blob/main/src/lib.rs>
  - <https://github.com/stalwartlabs/hashify/blob/main/src/lookup/mod.rs>
  - <https://github.com/stalwartlabs/hashify/blob/main/src/lookup/hasher.rs>
  - <https://github.com/stalwartlabs/hashify/blob/main/src/lookup/builder.rs>
  - <https://github.com/stalwartlabs/hashify/blob/main/src/lookup/switch.rs>
  - <https://github.com/stalwartlabs/hashify/blob/main/benches/lookup.rs>
  - <https://github.com/stalwartlabs/hashify/blob/main/examples/build_time.rs>
  - <https://github.com/stalwartlabs/hashify/blob/main/tests/strict.rs>
  - <https://github.com/stalwartlabs/hashify/blob/main/tests/allocations.rs>
  - <https://github.com/stalwartlabs/hashify/blob/main/tests/no_prelude.rs>
  - <https://github.com/stalwartlabs/hashify/blob/main/tests/lookups.rs>
  - <https://github.com/stalwartlabs/hashify/blob/74bd8a2/README.md>
  - <https://github.com/stalwartlabs/hashify/commits/main>
  - <https://github.com/stalwartlabs/hashify/issues/1>
  - <https://github.com/stalwartlabs/hashify/issues/2>
  - <https://github.com/stalwartlabs/hashify/issues/3>
  - <https://github.com/stalwartlabs/hashify/issues/4>
  - <https://crates.io/api/v1/crates/hashify>
  - <https://crates.io/api/v1/crates/hashify/reverse_dependencies>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/stalwartlabs/hashify`) · [data/wave1-phf/enrich/raw/github_com_stalwartlabs_hashify.json](../../../data/wave1-phf/enrich/raw/github_com_stalwartlabs_hashify.json) (enrichment confidence 0.85)

</details>
