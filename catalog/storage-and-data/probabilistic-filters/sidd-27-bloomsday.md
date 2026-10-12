# Bloomsday (blocked/split-block Bloom filter, Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT (declared in Cargo.toml; no separate LICENSE file detected by GitHub)` · 🟢 active

> Safe-Rust Parquet-style split-block Bloom filter whose inlined, auto-vectorized lookups ran \~2.3x faster than sbbf-rs in its own benchmark.

| | |
|---|---|
| **Beats** | Bloom filter (sbbf-rs Split Block Bloom Filter crate) |
| **Claimed result** | Times are per Criterion iteration of 1,000 lookups (README table). Negative lookups: \~1.17 µs for bloomsday vs \~2.81 µs for sbbf-rs. Positive lookups: \~1.26 µs vs \~2.93 µs. The README headline says '\~2.3x faster than sbbf-rs'. Per row, that is \~2.4x for negative and \~2.3x for positive lookups, or roughly 1.2 ns vs 2.8 ns per lookup (derived from page data). |
| **Workload** | The README says 1,000,000 items at a 0.01 false-positive rate. The bench present when the table was written (first commit 3e3c423a, 2026-02-04) built both filters from 1M xxh64 hashes of random 16-character strings. Each Criterion iteration timed 1,000 pre-hashed negative lookups and 1,000 positive lookups. The current benches/comparison.rs (since commit ea15abbb) uses only 10,000 random u64 hashes, which is a cache-resident \~12.5 KB filter. So `cargo bench` at HEAD no longer reproduces the README setup. Both filters are sized the same way: ceil(-ln p / ln^2 2) = 10 bits per key, in 256-bit blocks. |
| **Metric** | latency |
| **Compiler and flags** | Rust (rustc version not stated), Criterion 0.7, edition 2024. The repo's .cargo/config.toml applies rustflags to `cargo bench`. When the README table was written they were `-C target-feature=+avx2,+fma -C target-cpu=haswell`. They were changed to `target-cpu=native` in commit ea15abbb. The README does not say which configuration produced the published numbers. |
| **Adoption** | 14 stars |
| **Last commit** | 2026-02-06 |
| **Links** | [repository](https://github.com/sidd-27/Bloomsday) · [benchmark](https://github.com/sidd-27/Bloomsday#performance) |

## Verdict

The README's Criterion table (CPU and rustc not stated; repo flags at the time were +avx2,+fma with target-cpu=haswell) times 1,000 pre-hashed xxh64 lookups into a 1M-key filter at 10 bits/key (\~1.25 MB). Negative lookups took \~1.17 µs and positive \~1.26 µs, vs \~2.81 and \~2.93 µs for sbbf-rs 0.2.8 called through its dyn-dispatched FilterFn, or about 1.2 vs 2.8 ns per lookup. Each iteration repeats the same 1,000 hashes, so only about 32 KB of blocks is touched and stays cache-hot; the table also predates the bench's shrink to 10k keys and the switch to bounds-checked code, so `cargo bench` at HEAD does not reproduce it.

## Use it when

- Hot-loop membership probes on pre-computed 64-bit hashes, such as join or scan pre-filters and dedup checks, where the probe loop can be inlined and each probe should touch one 32-byte block.
- x86-64 binaries you build yourself with AVX2 enabled (`-C target-cpu=native` or `-C target-feature=+avx2`) for known server hardware.
- You want sbbf-rs's split-block bit layout (a given hash sets the same bits in the same block) behind a safe, owning Rust API instead of unsafe calls on a raw buffer.
- FPR targets around 1%: the 10 bits/key it picks there gives about 1.26% FPR according to the Parquet spec's table.
- You are willing to vendor about 110 lines of safe code or pin a git dependency, because nothing is published on crates.io.

## Skip it when

- Portable binaries built for baseline x86-64 or for ARM. The README warns that without AVX2-class target features the code may fall back to scalar. sbbf-rs detects AVX2/SSE4.1 at runtime and also ships NEON and WASM kernels.
- Tight FPR targets. Sizing uses the classic ceil(-ln p / ln^2 2) bits/key, which undersizes a split-block filter. Per the Parquet spec, a 0.01% request gets 20 bits/key, which is about 0.04% (4x over), and a 10% request gets 5 bits/key, which is about 18%.
- Concurrent writers (insert takes &mut self and there is no atomic variant), or any need for deletion, counting, union, or Parquet-compatible serialized bitsets.
- no_std or embedded targets: it requires std, while sbbf-rs supports no_std.
- Production dependencies that need a track record. It has one author and 9 commits over three days in February 2026, with no CI, no LICENSE file and no crates.io release.

## How it is fast

The filter math is the same as sbbf-rs. A multiply-shift fastrange of the top 32 hash bits picks a 32-byte block, and eight salted multiplies of the low 32 bits each pick one bit per word, so a probe touches a single block within one cache line. The difference is code generation. bloomsday's probe is an `#[inline(always)]` safe iterator fold that LLVM can inline into the caller's loop and auto-vectorize (the README cites vpand/vpor/vpsllv under AVX2). sbbf-rs selects an AVX2, SSE4.1 or fallback kernel at runtime and calls it through a `&'static dyn` trait object, which the compiler cannot inline. The measured gap therefore reflects dispatch and inlining overhead rather than a better filter layout.

## Compared with alternatives

Pick it over fastbloom (on crates.io, works with any hasher, and has AtomicBloomFilter for concurrent inserts) only when you specifically want the Parquet/sbbf-rs split-block layout for pre-hashed u64 keys and can build with AVX2; bloomsday once wrote a fastbloom comparison but removed it without publishing results. For a static key set where memory matters, xorf or pleat need fewer bits per key.

## Integration

| | |
|---|---|
| **Form** | crate (git-only, not on crates.io; the README's `bloomsday = "0.1.0"` line does not resolve); small enough to source-drop |
| **Dependencies** | xxhash-rust 0.8 (xxh32/xxh64/xxh3 features enabled, only xxh64 used); optional serde 1.0 behind the `serde` feature; requires std |
| **Minimum toolchain** | Rust 1.85+ (edition 2024); no rust-version/MSRV declared |
| **Platforms** | Pure safe Rust, so any std target compiles. Performance depends on auto-vectorization with AVX2-class target features. The repo's .cargo/config.toml (`+avx2,+fma`, `target-cpu=native`) applies only to cargo runs inside the repo, not to crates that depend on it, so downstream users must set their own flags. Only x86 AVX2 speed is claimed; ARM/NEON behavior is not documented. |
| **Thread safety** | Not documented. From the API: inserts take &mut self and lookups take &self, and the struct is a plain Vec with no interior mutability. Read-only lookups through shared references from many threads should be fine (auto Send/Sync, inferred), but concurrent inserts need external locking. |
| **Drop-in for the baseline** | partial — it uses the same SBBF algorithm, salts and block mapping as sbbf-rs, but the API differs. bloomsday is an owning safe struct, while sbbf-rs is unsafe FilterFn calls on a caller-allocated, 64-byte-aligned buffer. insert returns nothing, where sbbf-rs's insert returns whether the hash was already present. There is no raw-buffer access, so filter bytes cannot be exchanged with sbbf-rs or Parquet. |

## Gotchas

- The key API hashes through Rust's std `Hash` trait. Its docs say the data fed to a Hasher is not portable across platforms and, for most std types, not stable across compiler versions. A filter serialized after `insert_key` may not match after a rebuild or on another platform. Use `insert_hash` with a stable hash of your own for anything you persist.
- The README table predates the 2026-02-06 'safety first' commit. That commit replaced `get_unchecked` with checked indexing in both hot paths, adding a bounds check per probe, and the numbers were not re-measured afterwards.
- An invalid fpr (&lt;= 0 or &gt;= 1) silently falls back to 10 bits/key instead of returning an error. `new(0, _)` still allocates one block.
- Despite the 'cache-line' naming, blocks are 32 bytes (half a 64-byte line), with 32-byte alignment. serde output is the struct's own shape (word arrays plus num_blocks and seed), not the Parquet bitset format.

## Known shortcomings

- The \~2.3-2.4x is derived from README numbers on a 10k-entry bench (not 1M); sbbf-rs is called through dynamic dispatch per lookup; the fastbloom comparison was dropped and never published; not on crates.io; no CPU model.
- Uses the same SBBF math as sbbf-rs (same salts and fastrange mapping), so the 2.3x comes from sbbf-rs's dynamic dispatch vs bloomsday's inlining, not a better layout. The bench repeats the same 1k hashes (\~32 KB stays cache-hot) and predates a bounds-check commit and a shrink to 10k keys, so HEAD does not reproduce it. Its sizing undersizes an SBBF (per the Parquet spec a 0.01% request gets \~0.04%, 10% gets \~18%).
- The repo's AVX2 flags in .cargo/config.toml do not reach downstream crates (no runtime dispatch); the key API uses std Hash, which is not portable, so persisted filters can mismatch across builds/platforms. Not on crates.io, no LICENSE file, no CI; 9 commits over 3 days in 2026-02.

## Caveats and trade-offs

The baseline is one specific Rust SBBF crate (sbbf-rs 0.2.8), not a hand-optimized C/C++ Bloom filter. The bench calls sbbf-rs through FilterFn, which holds a `&'static dyn FilterImpl`. That means one virtual call per lookup, while bloomsday's may_match_hash is inlined into the loop. Part of the gap is likely dispatch overhead rather than the filter layout. No CPU model is stated. The current bench uses a 10k-entry filter, not the README's 1M. A fastbloom comparison was added to the bench (commit bcd7cb84) and later removed (2de41178), and its results were never published. MIT is declared only in Cargo.toml: there is no LICENSE text file and GitHub detects no license. The README's `bloomsday = "0.1.0"` install line does not work, because the crate is not on crates.io. The project is only days old (all commits 2026-02-04 to 2026-02-06).

100% safe Rust (no unsafe blocks); relies on compiler auto-vectorization instead of explicit SIMD intrinsics, so performance is sensitive to build flags; single-author, very new project.

## Maintenance

Listed as active, but all 9 commits landed 2026-02-04 to 2026-02-06 with nothing since; it has 14 stars, no issues and no CI, and MIT is declared only in Cargo.toml, so treat it as a small, safe, copyable reference to vendor rather than a maintained dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** These are first-party Criterion numbers from the README table. The benchmark code is public (benches/comparison.rs), and the repo's .cargo/config.toml pins the AVX2 rustflags. But no CPU model or rustc version is stated, and the current bench no longer matches the README's 1M-item setup, so it falls short of A.
- **Verifier notes:** The README numbers match the record. The record's doubt about flags was misplaced: the repo's .cargo/config.toml hardcodes the AVX2 rustflags, so `cargo bench` applies them. The real problems are elsewhere: the current bench shrank to 10k entries, and the sbbf-rs wrapper pays a dyn-dispatch call per lookup. License handling follows the existing precedent of treating a Cargo.toml-only MIT as copyable.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/sidd-27/Bloomsday>
  - <https://github.com/sidd-27/Bloomsday#performance>
  - <https://github.com/sidd-27/Bloomsday/blob/master/benches/comparison.rs>
  - <https://github.com/sidd-27/Bloomsday/blob/master/.cargo/config.toml>
  - <https://github.com/sidd-27/Bloomsday/blob/master/Cargo.toml>
  - <https://github.com/sidd-27/Bloomsday/blob/master/src/lib.rs>
  - <https://github.com/sidd-27/Bloomsday/commits/master>
  - <https://github.com/sidd-27/Bloomsday/blob/3e3c423a/benches/comparison.rs>
  - <https://github.com/sidd-27/Bloomsday/blob/bcd7cb84/benches/comparison.rs>
  - <https://github.com/sidd-27/Bloomsday/blob/bcd7cb84/README.md>
  - <https://github.com/ozgrakkurt/sbbf-rs/blob/HEAD/src/lib.rs>
  - <https://crates.io/api/v1/crates/sbbf-rs>
  - <https://crates.io/api/v1/crates/bloomsday>
- **Sources the enricher read:**
  - <https://github.com/sidd-27/Bloomsday>
  - <https://github.com/sidd-27/Bloomsday#performance>
  - <https://github.com/sidd-27/Bloomsday/blob/master/src/lib.rs>
  - <https://github.com/sidd-27/Bloomsday/blob/master/Cargo.toml>
  - <https://github.com/sidd-27/Bloomsday/blob/master/.cargo/config.toml>
  - <https://github.com/sidd-27/Bloomsday/blob/master/benches/comparison.rs>
  - <https://github.com/sidd-27/Bloomsday/commits/master>
  - <https://github.com/sidd-27/Bloomsday/commit/11f16a91>
  - <https://github.com/sidd-27/Bloomsday/commit/2de41178>
  - <https://github.com/sidd-27/Bloomsday/blob/3e3c423a/src/lib.rs>
  - <https://github.com/sidd-27/Bloomsday/blob/3e3c423a/benches/comparison.rs>
  - <https://github.com/sidd-27/Bloomsday/blob/3e3c423a/.cargo/config.toml>
  - <https://github.com/sidd-27/Bloomsday/blob/3e3c423a/README.md>
  - <https://github.com/sidd-27/Bloomsday/blob/d7565a26/README.md>
  - <https://github.com/sidd-27/Bloomsday/blob/6dda3d50/README.md>
  - <https://github.com/sidd-27/Bloomsday/blob/bcd7cb84/README.md>
  - <https://github.com/sidd-27/Bloomsday/blob/bcd7cb84/benches/comparison.rs>
  - <https://github.com/sidd-27/Bloomsday/blob/ea15abbb/README.md>
  - <https://github.com/sidd-27/Bloomsday/blob/2de41178/README.md>
  - <https://github.com/sidd-27/Bloomsday/issues>
  - <https://crates.io/api/v1/crates/bloomsday>
  - <https://crates.io/api/v1/crates/sbbf-rs>
  - <https://github.com/ozgrakkurt/sbbf-rs>
  - <https://github.com/ozgrakkurt/sbbf-rs/blob/HEAD/src/lib.rs>
  - <https://github.com/ozgrakkurt/sbbf-rs/blob/HEAD/src/arch/mod.rs>
  - <https://github.com/ozgrakkurt/sbbf-rs/blob/HEAD/src/arch/x86.rs>
  - <https://raw.githubusercontent.com/apache/parquet-format/master/BloomFilter.md>
  - <https://doc.rust-lang.org/std/hash/trait.Hash.html>
  - <https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/>
  - <https://doc.rust-lang.org/cargo/reference/config.html>
  - <https://github.com/tomtomwombat/fastbloom>
  - <https://hn.algolia.com/api/v1/search?query=bloomsday%20bloom%20filter&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/sidd-27/bloomsday`) · [data/wave6/enrich/raw/github_com_sidd_27_bloomsday.json](../../../data/wave6/enrich/raw/github_com_sidd_27_bloomsday.json) (enrichment confidence 0.8)

</details>
