# tinyrand (obsidiandynamics/tinyrand, Rust no_std PRNGs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🔴 abandoned

> Dependency-free no_std Rust crate with Wyrand, Xorshift and SplitMix-style PRNGs; README shows about 2x fastrand and 6x rand's ChaCha12.

| | |
|---|---|
| **Beats** | Rust rand crate (ChaCha12 StdRng) and the fastrand crate (Wyrand) |
| **Claimed result** | rand ChaCha12 2.4 GB/s; tinyrand SplitMix 6.5; tinyrand Xorshift 6.7; fastrand Wyrand 7.5; tinyrand Wyrand 14.6. README TL;DR: tinyrand is 2x faster than fastrand and 6x faster than rand. |
| **Workload** | README bandwidth table in GB/s for generating random numbers with each crate and algorithm. |
| **Metric** | throughput |
| **Adoption** | 16 stars |
| **Last commit** | 2022-12-15 |
| **Links** | [repository](https://github.com/obsidiandynamics/tinyrand) · [benchmark](https://github.com/obsidiandynamics/tinyrand) |

## Verdict

The README table lists bandwidth in GB/s: rand ChaCha12 (thread_rng) 2.4, tinyrand SplitMix 6.5, Xorshift 6.7, fastrand Wyrand 7.5 and tinyrand Wyrand 14.6, with no CPU, toolchain, flags, date or formula for GB/s. The public criterion bench (cri_rand.rs; criterion 0.3.6, rand 0.8.5, fastrand 1.8.0) times single calls, but its fastrand row times a bounded u64(0..u64::MAX) call while the tinyrand rows time raw next_u64, and the rand row is a reseeding CSPRNG. The only same-algorithm comparison, Wyrand 14.6 versus 7.5 GB/s (about 1.9x, derived from page data), is therefore partly a call-shape difference rather than generator speed.

## Use it when

- no_std or bare-metal Rust (microcontrollers, kernels) that needs fast non-cryptographic u64s or bounded integers without a heap.
- Unit tests that must force random branches: the tinyrand-alloc Mock lets a test script next_u128, next_bool and next_lim results and count invocations.
- Jitter, randomized backoff, games and simulations where a 64-bit Weyl-sequence generator (Wyrand) is good enough and you want one tiny dependency-free crate.
- Per-thread generators in std code via tinyrand-std's thread_rand, seeded from the system clock.

## Skip it when

- Anything security-sensitive: the README says none of the generators is cryptographically secure and points to rand for a CSPRNG.
- You need floats or distributions: the Rand trait has no f64 method and no normal, exponential or shuffle helpers (issue #2 asks how to make floats); signed-integer ranges are not implemented either.
- Code built on the rand ecosystem: it does not implement rand_core::RngCore, so rand's distributions, SliceRandom and seeding helpers cannot use it directly.
- Long or parallel simulations with Xorshift: its state recurrence has period 2^48-1, not 2^64-1 (see gotchas); use Wyrand or a larger-state generator.
- C++ projects: Rust only, with no C ABI.

## How it is fast

Each generator is a single u64 with an #[inline(always)] next_u64; the default Wyrand step is a Weyl increment (0xA0761D6478BD642F), one 64x64-to-128-bit multiply and an xor fold. Bounded integers up to 64 bits use Lemire's multiply-shift method with a rarely taken rejection loop (credited in the README); ranges wider than 64 bits fall back to modulo with rejection. There is no buffering, reseeding or cryptographic work, which is where most of the gap to rand's ChaCha12 thread_rng comes from.

## Compared with alternatives

Pick tinyrand over simd-rand when you draw one value at a time, need no_std or bounded integers and mocks; pick simd-rand for bulk u64 fills, where its portable Xoshiro256+X8 path reports 8.52 Gelem/s and the AVX-512 path is faster still. For C or C++ code the same Wyrand idea is available in lemire/testingRNG, which also benchmarks it against lehmer64 and PCG.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (tinyrand); optional companion crates tinyrand-std and tinyrand-alloc |
| **Minimum toolchain** | Rust 2021 edition; lib.rs uses inline format arguments (Rust 1.58+, inferred); no rust-version declared; CI pinned to Rust 1.66.0 |
| **Platforms** | any (no_std, no architecture-specific code; next_usize is defined for 16/32/64/128-bit pointer widths; CI tests x86-64 and i686-unknown-linux-gnu via cross) |
| **Thread safety** | Generators are plain u64 structs mutated through &mut self with no internal synchronization; give each thread its own instance or use tinyrand-std's thread-local thread_rand. |
| **Drop-in for the baseline** | no |

## Gotchas

- Default::default() uses a constant seed (0 for Wyrand, 1 for Xorshift and SplitMix), so every run repeats the same sequence unless you seed it (README warns); issue #1 (2023) reports the README examples always returning 0 and was closed with no visible reply.
- Xorshift is not textbook xorshift64: it saves the state after the &lt;&lt;13 and &gt;&gt;7 steps and applies &lt;&lt;17 only to the output. A GF(2) analysis run this session gives a characteristic polynomial with factors of degree 8, 8 and 48, so ordinary seeds cycle after 2^48-1 outputs (about 2.8e14, roughly 4 days at the README's 6.7 GB/s) instead of 2^64-1, and 65,535 nonzero seeds (for example 0x1e250d05b6eea0) cycle after 51 or 255 steps; no seed in 1..2^20 hits those short cycles.
- SplitMix is not Steele/Lea/Flood SplitMix64: it has no Weyl increment and iterates x -&gt; (x ^ x&gt;&gt;32) \* 0xff51afd7ed558ccd mod 2^64 (a bijection with 0 as a fixed point, which seed() avoids), so its period depends on the seed and is not guaranteed; constants and shifts differ from the splitmix64.c reference (0x9e3779b97f4a7c15 increment, shifts 30/27/31).
- next_u16 and next_u32 return the low bits of next_u64, and next_lim, next_range and Probability::new panic (assert!) on a zero limit, an empty range or p outside [0, 1]; there is no fallible API.

## Known shortcomings

- Tier C: README table from the public Criterion bench (tinyrand/benches/cri_rand.rs) with no CPU or toolchain; the fastrand row calls the bounded u64(0..u64::MAX) while tinyrand calls next_u64, so the comparison is not like for like.
- Its Xorshift saves state before the &lt;&lt;17 step; the enricher's GF(2) check (Berlekamp-Massey plus factoring, confirmed by matrix power) gives period 2^48-1, not 2^64-1, and 65,535 seeds cycle at 51 or 255 steps (e.g. 0x1e250d05b6eea0). Its 'SplitMix' is not SplitMix64 (no Weyl increment, iterated bijection, period not guaranteed). No floats, no rand_core implementation, constant default seed; issue #1 'Always resulting in 0' closed with no reply. The only like-for-like benchmark row is Wyrand vs Wyrand (14.6 vs 7.5 GB/s); the fastrand row times the bounded u64(0..u64::MAX).

## Caveats and trade-offs

Rust only, not callable from C++. README table gives no CPU, compiler, flags or benchmark command and is undated; it does not say how GB/s was derived. Benchmark code is public: tinyrand/benches/cri_rand.rs (criterion 0.3.6, dev-deps rand 0.8.5 and fastrand 1.8.0) and iai_rand.rs. In cri_rand.rs the rand row uses thread_rng().next_u64() (ChaCha12 CSPRNG with reseeding) and the fastrand row calls rand.u64(0..u64::MAX), a bounded-range call, while tinyrand rows call next_u64(); if the table came from this bench, the fastrand comparison is not like-for-like. The 6x figure compares a non-cryptographic PRNG with a CSPRNG; the closest like-for-like gap is 14.6 versus 7.5 GB/s for Wyrand (about 2x).

no_std and heap-free, suitable for microcontrollers; ships Xorshift, SplitMix and Wyrand only; not cryptographically secure; README includes its own statistical test suite and Dieharder results.

## Maintenance

Abandoned since late 2022 (crate 0.5.0 published 2022-09-12, about 92k total downloads per crates.io, CI pinned to Rust 1.66.0), but MIT, dependency-free and small enough to vendor; prefer Wyrand and avoid the Xorshift and SplitMix variants.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance table matches the record exactly (rand ChaCha12 2.4, tinyrand SplitMix 6.5, Xorshift 6.7, fastrand Wyrand 7.5, tinyrand Wyrand 14.6 GB/s). Public criterion bench code exists (tinyrand/benches/cri_rand.rs) comparing against rand thread_rng and fastrand, but no CPU, toolchain or flags are given for the table, so first-party C.
- **Verifier notes:** Stars 16, forks 2, 77 commits, last commit 2022-12-15 ('Set toolchain to 1.66.0'), abandoned; MIT confirmed (Cargo.toml and sidebar). Numbers verified verbatim; the fastrand bench call shape is a methodology caveat, not invalid evidence.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/obsidiandynamics/tinyrand>
  - <https://github.com/obsidiandynamics/tinyrand/commits>
  - <https://github.com/obsidiandynamics/tinyrand/tree/master/tinyrand>
  - <https://github.com/obsidiandynamics/tinyrand/tree/master/tinyrand/benches>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/README.md>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand/benches/cri_rand.rs>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/obsidiandynamics/tinyrand>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/README.md>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand/Cargo.toml>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand/benches/cri_rand.rs>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand/benches/iai_rand.rs>
  - <https://github.com/obsidiandynamics/tinyrand/tree/master/tinyrand/src>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand/src/lib.rs>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand/src/wyrand.rs>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand/src/xorshift.rs>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand/src/splitmix.rs>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand/src/duration.rs>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand-std/src/lib.rs>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand-std/src/clock_seed.rs>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/tinyrand-std/Cargo.toml>
  - <https://raw.githubusercontent.com/obsidiandynamics/tinyrand/HEAD/.github/workflows/master.yml>
  - <https://github.com/obsidiandynamics/tinyrand/issues?q=is%3Aissue>
  - <https://github.com/obsidiandynamics/tinyrand/issues/1>
  - <https://github.com/obsidiandynamics/tinyrand/issues/2>
  - <https://crates.io/api/v1/crates/tinyrand>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/src/splitmix64.c>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/obsidiandynamics/tinyrand`) · [data/wave8/enrich/raw/github_com_obsidiandynamics_tinyrand.json](../../../data/wave8/enrich/raw/github_com_obsidiandynamics_tinyrand.json) (enrichment confidence 0.8)

</details>
