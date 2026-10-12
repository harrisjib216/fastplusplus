# fast_rsync (Dropbox, Rust SIMD rsync algorithm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟡 stale

> Rust librsync-compatible signature, delta and patch library; SIMD multi-buffer MD4 makes signatures about 5.5x faster than librsync.

| | |
|---|---|
| **Beats** | librsync (C), legacy MD4 signatures, called through the goffrie/librsync-rs bindings (whole::signature_with_options, whole::delta, whole::patch). The README numbers (commit 'Update README.md with newer benchmarks', 2020-03-01; v0.1.1) used librsync-rs rev ab9c427, which builds mbrt/librsync aed9ab6, a pre-2.0.1 librsync 2.0.x snapshot whose NEWS still lists 2.0.1 as unreleased. That snapshot has search.c and no hashtable.c. |
| **Claimed result** | Signature of 4 MiB: fast_rsync 1.0696 ms (3.6519 GiB/s) vs librsync 5.8521 ms (683.51 MiB/s), about 5.5x (derived from page data); the README says 6X on this AVX2 CPU and about 3-4X on SSE2-only CPUs. Delta with a 64 KB edit: 7.0596 ms vs 7.4649 ms, about 1.06x (derived from page data). Delta on random data: 38.317 ms vs 42.758 ms, about 1.12x (derived from page data). Pathological delta on 16384 bytes: 6.2550 ms vs 50.185 ms, about 8.0x (derived from page data); the 4 MiB pathological run is listed only for fast_rsync (32.986 ms) because it was too slow for librsync. Apply: 284.20 us vs 400.30 us, about 1.41x (derived from page data). |
| **Workload** | Criterion benchmarks in benches/rsync_bench.rs on random data. Signature: 4 MiB buffer, block_size 4096, strong hash truncated to 8 bytes. Delta: a 4 MiB buffer with a 64 KiB random edit, a fully random 4 MiB buffer, and a pathological case (old data all 0x00, new data all 0x80; 16 KiB for both libraries, 4 MiB for fast_rsync only). Each delta iteration rebuilds the signature index on both sides. Apply: applying the 64 KiB-edit delta to a 4 MiB buffer. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6820HQ @ 2.70 GHz (AVX2), described by the authors as a noisy laptop |
| **Compiler and flags** | Not stated in the README. When the numbers were taken (v0.1.1), rust-toolchain pinned nightly-2020-01-31 with packed_simd. They were run with cargo bench under the default bench profile: opt-level 3, no LTO, no target-cpu, with AVX2 or SSE2 picked at run time. The librsync C sources are compiled by librsync-sys/build.rs through the gcc crate (cc in today's pin), with NDEBUG and no -march. These crates pass the cargo opt-level to the C compiler, so -O3 under the bench profile (inferred from the build scripts; the authors do not state it). C compiler and version not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README: SIMD operations (AVX2 gives the 6X on signatures) for the rolling checksum and MD4; delta rows are bound by single-block MD4 and by hash-map lookups where Rust's built-in HashMap gives 'a slight advantage'; pathological inputs are detected instead of degrading. |
| **Adoption** | 686 stars; on crates.io as fast_rsync |
| **Last commit** | 2024-04-18 |
| **Links** | [repository](https://github.com/dropbox/fast_rsync) · [benchmark](https://raw.githubusercontent.com/dropbox/fast_rsync/master/README.md) |

## Verdict

Dropbox's criterion benchmark (benches/rsync_bench.rs, random data, 4 MiB, block 4096, 8-byte MD4) on a noisy i7-6820HQ laptop in 2020: signature 1.07 ms vs 5.85 ms for librsync, a pre-2.0.1 snapshot called through librsync-rs (about 5.5x, AVX2). Delta 7.06 vs 7.46 ms with a 64 KiB edit and 38.3 vs 42.8 ms on fully random data. The pathological 16 KiB delta is 6.26 vs 50.2 ms and apply is 284 vs 400 us. The Rust toolchain was nightly-2020-01-31, and the C compiler and flags are not stated.

## Use it when

- Computing rsync signatures of large in-memory buffers on x86-64 with AVX2 (about 5.5x over librsync in the README) or SSE2-only and aarch64 machines (README: about 3-4x with SSE2)
- A sync service or client in Rust that must interoperate with librsync peers using MD4 signatures (rdiff-style signature, delta, patch)
- Servers that receive deltas from untrusted parties: apply_limited caps output size and rejects out-of-bounds or zero-length copies, and the apply path is fuzzed against librsync
- Inputs where many windows share one weak checksum (runs of constant bytes, repetitive data), where librsync recomputes MD4 at every offset

## Skip it when

- You need BLAKE2 signatures (README calls MD4 the legacy format) or any collision-resistant matching: MD4 is broken, so every reconstructed file must be checked with a separate strong hash
- Files that do not fit in memory: input must be a &[u8]; issue #29 (open) asks for BufReader input and there is no streaming input API
- You only need delta or patch speed: the README's realistic delta rows are 6% and 12% faster and apply is 1.4x, measured against a 2017-era librsync snapshot that later releases sped up
- Diffing against signatures from untrusted peers without validating them first (see gotchas: block_size 0 is not rejected)
- You want maintained software or tuning guidance: last commit 2024-04-18, no default SignatureOptions (issue #28 open)

## How it is fast

Signature generation hashes many independent blocks at once with multi-buffer SIMD MD4 (md4_many: SSE2 and AVX2 on x86 and NEON on aarch64, picked at run time by feature detection). The rsync rolling checksum (the Adler-style rollsum with a 31 offset) is rewritten as a weighted sum so the compiler can vectorise it, and it is compiled once per feature level. diff() indexes the signature in a two-level map: a std HashMap keyed by the rollsum with an xxhash-style avalanche hasher, holding a single-entry map of truncated MD4 to block index. After 1024 failed strong-hash checks on one rollsum value it stops checking that value, so inputs with many weak-sum collisions do not degrade.

## Compared with alternatives

No catalogued sibling does rsync-style delta transfer. cpz (FUC) and crabz speed up local copying and compression, whereas fast_rsync is for when the receiver already holds an older copy and transfer size or signature throughput is the bottleneck.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | arrayref (runtime); librsync-rs, criterion, quickcheck and rand only for tests and benches |
| **Minimum toolchain** | Rust edition 2018; no rust-version declared; the repo pins Rust 1.76.0 for development and CI; stable Rust since v0.1.4 (2022) dropped packed_simd |
| **Platforms** | any Rust target; SIMD paths on x86 and x86-64 (SSE2, AVX2, runtime detection, no target-cpu needed) and aarch64 (NEON); scalar fallback elsewhere; CI runs i686 and emulated aarch64 |
| **Thread safety** | not documented; the API is pure functions over borrowed slices with no global mutable state other than CPU feature detection |
| **Drop-in for the baseline** | partial: wire-compatible with librsync MD4 signatures and deltas, but a different Rust API (whole in-memory buffers, no streaming jobs, no BLAKE2, no rdiff CLI) |

## Gotchas

- Signature::deserialize and diff() never check block_size &gt; 0 (only Signature::calculate asserts it). Reading src/diff.rs, a deserialized signature with block_size 0 makes diff() panic on a usize underflow or slice index, and a crafted one (a weak sum of 0 with crypto_hash_size 0) loops forever. The honggfuzz target (fuzz/src/bin/fuzz.rs) fuzzes only apply_limited, so diff on untrusted signatures is unfuzzed. Validate block_size and crypto_hash_size before calling diff (found by reading the code, not run).
- crypto_hash_size may be 0 to 16, and only the truncated MD4 decides a match. Small values or a hostile peer can produce deltas that apply cleanly but rebuild the wrong data. apply() without a limit can expand a tiny delta into a huge output, so use apply_limited.
- The pathological 8x row measures different work, not faster code. 4096 bytes of 0x00 and of 0x80 have equal rollsums, so all 12,289 offsets of the 16 KiB input collide. fast_rsync computes MD4 for 1024 of them before blacklisting the weak sum, while librsync computes it for all 12,289. Both deltas are all-literal here, but on real data the blacklist can miss a genuine match that appears after 1024 false hits on the same weak sum, which makes the delta larger.
- Harness notes: in the 2020 rows (derived from page data, assuming MD4 dominates both pathological runs), fast_rsync's single-block MD4 ran at about 0.67 GB/s against about 1.0 GB/s for librsync, so SIMD helps only signatures. The signature benchmark drops the fast_rsync result without black_box, whereas the librsync closure returns its output. The 3.65 GiB/s figure is plausible for 8-lane MD4, so nothing suggests the work was optimised away.

## Known shortcomings

- Stale baseline: the README numbers (2020-03-01) ran against the pre-2.0.1 librsync snapshot mbrt/librsync aed9ab6, before librsync's hashtable rewrite, bloom filter and delta speedups; delta wins only 6% and 12%; the pathological 8x is collision blacklisting (MAX_CRC_COLLISIONS 1024), a different behaviour; the win is hand-written multi-buffer SIMD MD4, not Rust; no compiler named (opt levels inferred from build scripts).
- By code reading: Signature::deserialize and diff() never check block_size &gt; 0, so an untrusted signature with block_size 0 makes diff() panic or loop forever; fuzz/src/bin/fuzz.rs fuzzes only apply_limited. The pathological 8x is 1,024 versus 12,289 MD4 calls (blacklist), not faster code; single-block MD4 ran about 0.67 GB/s against about 1.0 GB/s for librsync (derived), so SIMD helps signatures only. The signature closure skips black_box; numbers still plausible.

## Caveats and trade-offs

Stale baseline: the README numbers date from 2020-03-01 and were measured against a pre-2.0.1 librsync snapshot (mbrt/librsync aed9ab6). librsync 2.0.1 (2017-10-17) added an open-addressing hashtable that 'significantly speeds up delta operations' and fixed degenerate behaviour with many duplicate blocks. 2.3.1 added a bloom filter (deltas 20-50% faster) and 2.3.3 made deltas another 5-15% faster (librsync NEWS.md). So the 6% and 12% delta wins may not hold against librsync 2.3.x; this was not measured. The numbers also predate fast_rsync's own 2021 hashmap changes and its 2022 switch from packed_simd to intrinsics, and were not re-run. The pathological rows show different behaviour, not only speed. 4096 bytes of 0x00 and of 0x80 give equal 16-bit rollsum halves (derived), so every offset collides. fast_rsync blacklists a weak checksum after 1024 collisions (MAX_CRC_COLLISIONS in src/diff.rs) and may emit literal data where librsync keeps searching. Only the signature step is a large win; the two realistic delta rows are 6% and 12% and apply is 1.4x. The librsync side also runs through Rust Read/Write stream bindings, which adds a small copy overhead. The win is hand-written SIMD in a library, not a Rust-language effect. Results come from one noisy laptop. No commits since 2024-04-18. [retier] Signature::deserialize and diff() never check block_size &gt; 0, so an untrusted signature with block_size 0 makes diff() panic or loop forever (the fuzzer covers only apply_limited). The pathological 8x is 1,024 versus 12,289 MD4 calls (blacklist), not faster code; single-block MD4 ran about 0.67 GB/s against about 1.0 GB/s for librsync, so SIMD helps signatures only.

Only the legacy MD4 signature format is supported, not BLAKE2, and MD4 is insecure, so every applied delta must be verified with another hash. SIMD on x86, x86-64 and aarch64 with runtime detection. In-memory buffers only.

## Maintenance

Stale (last commit 2024-04-18, 0.2.0 released 2023-03-31) but Apache-2.0, small, tested for librsync interoperability and widely pulled (about 634k crates.io downloads in the last 90 days); the README numbers predate the 2021-2022 hashmap and SIMD-intrinsics rewrites and were never re-run against librsync 2.3.x. Code reading shows diff() does not validate block_size from a deserialized signature (panic or hang), and that path is not fuzzed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The benchmark code is public (benches/rsync_bench.rs, criterion) and the CPU is named (i7-6820HQ), but the README names no compiler or flags. At measurement time the repo pinned Rust nightly-2020-01-31 and built librsync with the gcc crate, with no C compiler named. These are first-party numbers from a single noisy laptop, so tier C.
- **Verifier notes:** All README numbers match. Main shortcomings to record: a stale pre-2.0.1 librsync baseline (later librsync releases sped up deltas a lot and fixed degenerate cases); delta wins are marginal; the pathological 8x reflects different behaviour; the numbers predate the 2021-2022 code changes; first-party, single laptop. same_opt_level is set true because both sides build at cargo opt-level 3 and the gcc/cc crate passes -O3 to librsync, inferred from the build scripts (compiler versions unknown). same_algorithm stays true for the signature format, since fast_rsync signatures feed librsync delta in the harness.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-98 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/README.md>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/benches/rsync_bench.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/Cargo.toml>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/rust-toolchain>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/md4/mod.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/crc.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/signature.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/diff.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/v0.1.1/Cargo.toml>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/v0.1.1/rust-toolchain>
  - <https://github.com/dropbox/fast_rsync>
  - <https://github.com/dropbox/fast_rsync/commits/master>
  - <https://github.com/dropbox/fast_rsync/commits/master/README.md>
  - <https://github.com/dropbox/fast_rsync/pull/6/files>
  - <https://github.com/dropbox/fast_rsync/tree/master/src>
  - <https://raw.githubusercontent.com/goffrie/librsync-rs/e2e4b06022d889e020c439f2dc92ea2fec0e483e/librsync-sys/build.rs>
  - <https://raw.githubusercontent.com/goffrie/librsync-rs/e2e4b06022d889e020c439f2dc92ea2fec0e483e/librsync-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/goffrie/librsync-rs/ab9c427b5b20624fe533ad0247fe0f9c3460245e/librsync-sys/build.rs>
  - <https://github.com/goffrie/librsync-rs/tree/ab9c427b5b20624fe533ad0247fe0f9c3460245e/librsync-sys>
  - <https://raw.githubusercontent.com/mbrt/librsync/aed9ab606bb5127f6b05df6f2c9fbcf48788a467/NEWS.md>
  - <https://raw.githubusercontent.com/mbrt/librsync/aed9ab606bb5127f6b05df6f2c9fbcf48788a467/CMakeLists.txt>
  - <https://raw.githubusercontent.com/librsync/librsync/master/NEWS.md>
  - <https://raw.githubusercontent.com/goffrie/librsync/HEAD/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/dropbox/fast_rsync>
  - <https://github.com/dropbox/fast_rsync/commits/master>
  - <https://github.com/dropbox/fast_rsync/issues?q=is%3Aissue>
  - <https://github.com/dropbox/fast_rsync/tree/master/fuzz/src/bin>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/README.md>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/Cargo.toml>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/rust-toolchain>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/benches/rsync_bench.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/lib.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/diff.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/signature.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/patch.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/crc.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/md4/mod.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/hasher.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/hashmap_variant.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/src/tests.rs>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/fuzz/Cargo.toml>
  - <https://raw.githubusercontent.com/dropbox/fast_rsync/master/fuzz/src/bin/fuzz.rs>
  - <https://crates.io/api/v1/crates/fast_rsync>
  - <https://crates.io/api/v1/crates/fast_rsync/reverse_dependencies>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/dropbox/fast_rsync`) · [data/wave14/enrich/raw/github_com_dropbox_fast_rsync.json](../../../data/wave14/enrich/raw/github_com_dropbox_fast_rsync.json) (enrichment confidence 0.8)

</details>
