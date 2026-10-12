# PtrHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust minimal perfect hash with 8-bit pilots (PTHash descendant); queries 2.7-3.8x faster than BBHash, \~7.6x faster than CMPH CHD.

| | |
|---|---|
| **Beats** | BBHash and CMPH (CHD) in the arXiv 2506.06536 survey; PTHash and PHOBIC (plus CMPH CHD) in the SEA 2025 paper arXiv 2502.15539 |
| **Claimed result** | Survey arXiv 2506.06536v3, Table 6 (100M random string keys, single-threaded). PtrHash with lambda=3.0, linear, vec uses 2.990 bits/key, queries in 45 ns and builds in 141 ns/key. PtrHash with lambda=4.0, cubic, EF uses 2.118 bits/key, queries in 47 ns and builds in 358 ns/key. BBHash gamma=5.0 (6.870 bits/key) queries in 127 ns and builds in 157 ns/key. BBHash gamma=1.5 (3.293 bits/key) queries in 173 ns and builds in 273 ns/key. CMPH CHD lambda=4 (2.166 bits/key) queries in 356 ns and builds in 1,522 ns/key. PtrHash queries are about 2.7x-3.8x faster than BBHash and 7.6x-7.9x faster than CHD. Fast PtrHash builds 1.1x-1.9x faster than BBHash, and CHD builds 4.3x-10.8x slower than PtrHash (derived from page data). SEA 2025 paper arXiv 2502.15539v2, Table 2 (300M string keys, 6 threads): default PtrHash (2.40 bits/key) queries in 37 ns and 23 ns streaming. The fastest PTHash config (C-C) takes 77 ns, which gives the paper's stated 2.1x and 3.3x. CMPH CHD takes 542 ns, about 14.6x slower than default PtrHash (derived from page data). Paper Table 1 (1e9 integer keys): the MPHF for-loop query takes 12.5-14.2 ns only with the fast parameters (2.76-3.00 bits/key). It takes 20.0-21.7 ns with the default or compact parameters (2.09-2.62 bits/key). Streaming takes 8.6-9.7 ns in all configurations, and 8.6-8.8 ns with the Vec or CacheLineEF remap. |
| **Workload** | Survey Table 6: 100M random strings of length 10-50, single-threaded construction, then 100M queries, via MPHF-Experiments tableSurvey. SEA 2025 paper Table 2: 300M random strings of length 10-50 via MPHF-Experiments, 6-thread construction where supported. SEA 2025 paper Table 1: 1e9 random 64-bit integer keys hashed with FxHash, for-loop and prefetched streaming queries. |
| **Metric** | throughput |
| **Hardware** | Survey: Intel Core i7-11700 (8 cores, 16 threads), pinned to its 2.5 GHz base clock, Rocky Linux 9.5, Linux 5.14.0. SEA paper: Intel Core i7-10750H, 6 cores, hyper-threading disabled, frequency pinned to 2.6 GHz, 64 GiB DDR4-3200. |
| **Compiler and flags** | Survey: GNU C++ 14.2.0 with -O3 -march=native (CMake Release), and Rust 1.85.0 in release mode with target-cpu=native. PtrHash is linked from the ptr_hash crate pinned at =1.1.0 through a Rust staticlib FFI contender. SEA paper: no compiler version is stated. The PtrHash repo builds with -C target-cpu=native (.cargo/config.toml on master) and a release profile with lto=thin. |
| **Adoption** | 106 stars |
| **Last commit** | 2026-08-28 |
| **Links** | [repository](https://github.com/RagnarGrootKoerkamp/PtrHash) · [benchmark](https://arxiv.org/abs/2506.06536) |

## Verdict

The survey (arXiv 2506.06536v3, Table 6) linked ptr_hash 1.1.0 as a Rust staticlib (Rust 1.85, target-cpu=native) and ran it against C++ BBHash and CMPH CHD (GCC 14.2, -O3 -march=native). The run used 100M random 10-50-byte strings, single-threaded, on an i7-11700 pinned at 2.5 GHz. PtrHash queried in 45-47 ns vs 127-173 ns for BBHash and 356 ns for CHD, and built in 141-358 ns/key vs 157-273 and 1,522 ns/key. The author's SEA 2025 paper (300M strings, 6 threads, i7-10750H at 2.6 GHz, compiler not stated) reports 37 ns (23 ns streaming) vs 77 ns for the fastest PTHash config; no source compares against std::unordered_map.

## Use it when

- Static key sets from \~1M to 10^9+ keys (the docs say it was tested up to 10^11) that are queried far more often than rebuilt, e.g. k-mer indexes, string-to-id dictionaries, or dense value arrays indexed by key.
- Throughput-bound bulk lookups you can stream: on 1e9 integer keys, `index_stream` reaches 8.6-9.7 ns/key, vs 12.5-21.7 ns/key for a plain for-loop (SEA paper Table 1).
- Tables much larger than L3, where cache misses dominate: the survey measured 1.0 L1 miss per query, vs 4.0-7.4 for BBHash and 11.4 for CHD.
- You want fast construction without giving up query speed: 141 ns/key single-threaded at 2.99 bits/key (survey Table 6), or 27 ns/key on 6 threads (SEA Table 2).
- Rust codebases, or C++ projects willing to link a Rust staticlib behind a small extern "C" shim, as MPHF-Experiments does.

## Skip it when

- Space is the priority: at 2.1-3.0 bits/key it is well above Consensus-RecSplit (1.58), SIMDRecSplit (1.81) and PHast (1.85-2.0) in survey Table 6.
- You need membership tests or a mutable set: it has no insert/delete and no key storage. Any change means a full rebuild, and rejecting non-members needs a separate key or fingerprint array.
- Pure C++ builds that cannot take a Rust toolchain. There is no C/C++ API. The only C++ port (bassiounix/PtrHash-cc, 3 stars) is an 'as is' rewrite for an LLVM libc RFC; its README says GPLv2 but GitHub detects no license file, and it has no benchmarks.
- Small sets with the compact config: at 10,000 keys, survey Table 7 shows the cubic/EF config taking 44,300 ns/key to build (the linear/vec config takes 147 ns/key). The README warns that small inputs carry relatively large constant space overhead.
- You need reproducible builds: construction is not deterministic (issue #36 is open; `build_part` uses an unseeded `fastrand::Rng`), so rebuilding the same keys reassigns indices.

## How it is fast

It is a PTHash/PHOBIC-style bucket-placement MPHF. Keys hash into buckets, and each bucket stores a 'pilot' whose hash is XORed into the key hash to choose a slot. PtrHash limits pilots to 0..255 and stores them as a plain `Vec<u8>`, with no compact, dictionary or Elias-Fano decoding. When no pilot fits, construction uses cuckoo-style hash-and-evict. The result is that most queries cost one cache-line read plus a few multiply-high range reductions (Lemire's fastrange). With alpha=0.99, the \~1% of slots at or above n are remapped through a plain vector or CacheLineEF, which packs 44 Elias-Fano values into one cache line. `index_stream` hashes keys ahead and software-prefetches pilots 32 iterations early, which the paper shows saturates per-core memory bandwidth. Construction radix-sorts hashes and fills cache-sized parts.

## Compared with alternatives

Pick PtrHash over PTHash when query latency and build speed matter and Rust is acceptable: 45 vs 76 ns/query and 141 vs 516 ns/key build in survey Table 6, or 37 vs 77 ns in SEA Table 2. Prefer PHast/PHast+ (also Rust) for slightly faster queries at \~2 bits/key (38-44 ns, 1.85-2.07 bits/key), and SIMDRecSplit or Consensus-RecSplit when getting below 2 bits/key justifies 5x+ slower queries.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bitvec, itertools, rand 0.10, rand_chacha, rayon, rdst (radix sort), fastrand, tempfile, mem_dbg, colored, log, fxhash, xxhash-rust, prefetch-index; default features add sucds (Elias-Fano) and cacheline-ef; optional: gxhash (StringHash), epserde (zero-copy/mmap serialization), extra hashers |
| **Minimum toolchain** | Stable Rust. No MSRV is declared (crates.io rust_version is unset), but the rand 0.10 dependency needs Rust 1.85 (edition 2024). There is no C/C++ API. |
| **Platforms** | x86-64 and aarch64 are built and tested in CI. i686 and armv7 are cross-built only, with --no-default-features (sucds is 64-bit-only and gxhash needs AES). The repo's .cargo/config.toml sets target-cpu=native. Prefetch uses SSE on x86 or PRFM on aarch64 and is a no-op elsewhere. The paper's CacheLineEF lookup uses BMI2 PDEP, which it calls very slow on AMD Zen 2. |
| **Thread safety** | Not documented. The built structure is immutable and queried through &self, so read-only sharing across threads is the natural model. Construction parallelizes internally with rayon. |
| **Drop-in for the baseline** | partial: it fills the same keys-to-[0,n) MPHF role as BBHash, CHD or PTHash, but it is a Rust crate with its own API and serialization format (epserde), and C++ callers need an FFI layer |

## Gotchas

- `index_stream` returns an Iterator whose `next()` is `unimplemented!()`. Only fold-based consumers work (`sum`, `for_each`, `fold`); a plain `for` loop over it panics.
- `new()` panics after 10 failed global seeds; use `try_new()` to get an `Option`. Duplicate keys always fail because duplicate hashes are rejected. `new_from_par_iter` discards the build result, so a failed build is not reported. Regular integer keys broke earlier FxHash-based versions (#19, #21): use `StrongerIntHash` for structured integers, and `StringHash128` for more than 10^9 string keys.
- The paper's 'Default' config (lambda=3.5, cubic, CacheLineEF, 2.40 bits/key) is now `default_balanced()`, and the crate's `PtrHashParams::default()` is the paper's 'fast' config (\~3.0 bits/key). Sharding requires SINGLE_PART=false (`CompactPtrHash`). Setting `params.sharding` on the default single-part types panics in `init`, and the repo's own examples/string_keys.rs does exactly that.
- Before 2.1.0, safe `index()` could read past the remap array for a key outside the build set (#35). `Packed::index` impls still use `get_unchecked` inside safe fns, and epserde deserialization is `unsafe`. The maintainer says zero-copy CacheLineEF deserialization has alignment issues.

## Caveats and trade-offs

PtrHash is a Rust crate with no C/C++ API. C++ use needs FFI, as MPHF-Experiments does. Neither source compares against std::unordered_map. The survey measured ptr_hash 1.1.0, and the current crate is 2.1.1. In survey Table 6, PHast and PHast+ (Rust) query slightly faster than PtrHash (38-44 ns vs 45-47 ns) at about 1.85-2.07 bits/key, so PtrHash is not the fastest-query MPHF there. Compact PtrHash builds slower than BBHash gamma=1.5 single-threaded (358 vs 273 ns/key). The paper's 2.1x and 3.3x are measured against the fastest PTHash configuration. Its 12 ns / 8 ns integer-key figures skip string hashing, and the 12 ns for-loop needs about 3 bits/key. The README large-input table was run at 3.6 GHz, not the paper's pinned 2.6 GHz. The previous caveat was wrong: the paper never says BBHash/CMPH-style methods are omitted as not competitive. SEA Table 2 includes CMPH's CHD and the fingerprinting methods FMPH, FMPHGO and FiPS. The survey is an arXiv preprint (v3, 2026-02-05) with no journal reference.

Rust implementation; an unofficial, ambiguously-licensed C++ port exists (bassiounix/PtrHash-cc, made for an LLVM libc RFC) but has no independent benchmarks; CompactPtrHash trades \~2x slower construction for smaller size; needs sharding for keys that don't fit in RAM

## Maintenance

Actively maintained by a responsive single author: v2.1.1 shipped 2026-08-27 and the last commit is 2026-08-28. It is MIT-licensed with \~62k crates.io downloads. The 1.x to 2.x break changed type aliases and parameter names and invalidated old on-disk structures, and the benchmarked 1.1.0 predates 2.x. Issue #40 reports 2.x's default_compact building 1.6-1.9x slower at 1M keys because it uses fewer parts.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A. The SEA 2025 paper (arXiv 2502.15539v2) alone stays B because it never states a compiler version. Tier A comes from the survey arXiv 2506.06536v3 (Lehmann, Mueller, Pagh, Pibiri, Sanders, Vigna, Walzer; Sec. 9 and Table 6), which runs PtrHash against BBHash and CMPH's CHD. It states GNU C++ 14.2.0 -O3 -march=native, Rust 1.85.0 in release mode with target-cpu=native, and an Intel i7-11700. The code is public in ByteHamster/MPHF-Experiments: src/tableSurvey.cpp, scripts/tableSurvey.sh, contenders/bucketplacement/RustPtrHashContender.cpp with rust/src/ptr_hash_contender.rs, contenders/fingerprinting/BBHashContender.cpp, and contenders/bucketplacement/ChdContender.h, which wraps cmph.
- **Verifier notes:** Every number in the original claim appears in arXiv 2502.15539. The 12 ns for-loop figure was attached to 2.0-3.0 bits/key, but it holds only at about 3 bits/key, and the text is now fixed. The bogus caveat about omitted baselines is replaced. Metadata (MIT, 106 stars, last commit 2026-08-28, active, not a fork) all checks out via gh.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2502.15539>
  - <http://export.arxiv.org/api/query?id_list=2502.15539>
  - <https://arxiv.org/pdf/2502.15539v2>
  - <https://arxiv.org/pdf/2502.15539v1>
  - <https://arxiv.org/abs/2506.06536>
  - <https://arxiv.org/pdf/2506.06536v3>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/readme.md>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/Cargo.toml>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/.cargo/config.toml>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/justfile>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/tree/evals/examples>
  - <https://github.com/RagnarGrootKoerkamp/mphf-experiments>
  - <https://github.com/RagnarGrootKoerkamp/mphf-experiments/blob/main/CMakeLists.txt>
  - <https://github.com/RagnarGrootKoerkamp/mphf-experiments/blob/main/benchmark/CmphContender.h>
  - <https://github.com/RagnarGrootKoerkamp/mphf-experiments/blob/main/spack.yaml>
  - <https://github.com/RagnarGrootKoerkamp/mphf-experiments/blob/main/Dockerfile>
  - <https://github.com/ByteHamster/MPHF-Experiments>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/src/tableSurvey.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/scripts/tableSurvey.sh>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/bucketplacement/ChdContender.h>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/bucketplacement/ChdContender.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/rust/src/ptr_hash_contender.rs>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/rust/Cargo.toml>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/RagnarGrootKoerkamp/PtrHash>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/readme.md>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/Cargo.toml>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/CHANGELOG.md>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/.cargo/config.toml>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/.github/workflows/ci.yml>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/src/lib.rs>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/src/hash.rs>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/src/build.rs>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/src/sort_buckets.rs>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/src/shard.rs>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/src/pack.rs>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/src/bucket_fn.rs>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/src/reduce.rs>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/blob/master/examples/string_keys.rs>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues?q=is%3Aissue>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/40>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/36>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/35>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/33>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/37>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/24>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/23>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/22>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/21>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/20>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/19>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/16>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/issues/6>
  - <https://github.com/RagnarGrootKoerkamp/PtrHash/pull/39>
  - <https://github.com/RagnarGrootKoerkamp/prefetch-index/blob/master/src/lib.rs>
  - <https://arxiv.org/html/2506.06536v3>
  - <https://arxiv.org/pdf/2506.06536v3>
  - <https://arxiv.org/abs/2502.15539>
  - <https://arxiv.org/pdf/2502.15539v2>
  - <https://crates.io/api/v1/crates/ptr_hash/versions>
  - <https://crates.io/api/v1/crates/prefetch-index>
  - <https://crates.io/api/v1/crates/rand/0.10.2>
  - <https://github.com/bassiounix/PtrHash-cc>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/rust/src/ptr_hash_contender.rs>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/rust/Cargo.toml>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/ragnargrootkoerkamp/ptrhash`) · [data/wave1-phf/enrich/raw/github_com_ragnargrootkoerkamp_ptrhash.json](../../../data/wave1-phf/enrich/raw/github_com_ragnargrootkoerkamp_ptrhash.json) (enrichment confidence 0.82)

</details>
