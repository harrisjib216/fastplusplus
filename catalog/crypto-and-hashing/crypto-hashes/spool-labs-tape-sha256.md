# tape-sha256

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Pure-Rust multi-buffer SHA-256 for batches and hash chains; 2-3.5x the serial sha2 crate on x86 batch hashing.

| | |
|---|---|
| **Beats** | sha2 crate (serial SHA-256); also OpenSSL SHA-256 via Node.js node:crypto, and C batch hashers Firedancer fd_sha256 and isa-l_crypto sha256_mb |
| **Claimed result** | BENCHMARKS.md summary vs sha2 0.10.9: AMD Zen 5 3.5x (avx512-2x16), Zen 4 2.1x (shani-x4), Zen 3 2.1x, Intel Emerald / Granite Rapids 2.0-2.1x, Apple M-series 6.8x but only against the sha2 software path (sha2 0.10 uses software SHA-256 on aarch64 unless its asm feature is enabled); Zen 5 7.82 us/batch (8654 MB/s) vs sha2 27.71 us (2443 MB/s). Versus C implementations: 60% faster than Firedancer and 39% faster than the best isa-l_crypto result on Zen 5, about 8% faster than Firedancer on Zen 4, about 2.2x on Zen 3, but 2-12% slower than Firedancer on Intel Emerald Rapids / Granite Rapids in measured runs. Hash chains: 7.3 ns/link at 32 chains vs sha2 45.4 ns on Zen 5 (page says 6.0x); on Apple, against sha2 with its asm feature (27.7 ns), the best is 14.5 ns, about 1.9x (derived from page data). OpenSSL: benches/wasm/README.md says the native neon-sha2-x4 batch (about 16 us; BENCHMARKS.md lists 16.25 us) is 2.7x faster than node:crypto (OpenSSL), whose crypto.hash one-shot took 42.89 us/batch (1578 MB/s) on an M4 Max (unpinned, read as ratios). |
| **Workload** | Batch of 64 independent messages (26-byte prefix plus about 1 KiB payload, 67,680 bytes per batch, one Solana erasure batch of Merkle leaves), one thread pinned to one core, best of 15 rounds of 50 iterations; also hash chains in ns per link and Merkle commitments. |
| **Metric** | throughput |
| **Hardware** | AMD Zen 5 (family 0x1a, model not captured, 2026-08-08); EPYC 9B14 (GCP c3d); EPYC 7B13 (GCP c2d); Xeon Platinum 8581C (GCP c4); Xeon 6985P-C (GCP c4-standard-8-lssd); Apple M-series (M4 Max per the wasm README) |
| **Compiler and flags** | Rust 1.89+ (rust-version) cargo bench, release profile; RUSTFLAGS not stated for native rows (notes that -C target-cpu=native made the Zen 5 interlaced kernel 8-14% slower); wasm rows built with -C target-feature=+simd128; Firedancer and isa-l_crypto built from source with unstated flags |
| **Adoption** | 1 star, 0 forks, 13 commits on GitHub (spool-labs/sha256); crates.io: 470 downloads (0.1.0 361, 0.2.1 109), versions 0.1.0 (2026-07-27) and 0.2.1 (2026-08-11) |
| **Last commit** | 2026-08-11 |
| **Links** | [repository](https://github.com/spool-labs/sha256) · [benchmark](https://github.com/spool-labs/sha256/blob/main/BENCHMARKS.md) |

## Verdict

First-party cargo bench merkle_leaves: 64 Solana-style leaves (26-byte prefix plus 1019 or 1044 bytes, 67,680 bytes per batch) on one pinned core, best of 15x50 iterations; the dispatched kernel beat serial sha2 0.10.9 (which uses SHA-NI on x86) by 3.5x on an unidentified Zen 5 (7.82 vs 27.71 us), 2.1x on EPYC 9B14 and 7B13, and 2.0-2.1x on Xeon 8581C and 6985P-C. The Apple 6.8x is against sha2's software path, because sha2 0.10.9 only uses ARMv8 SHA2 on aarch64 with its asm feature (confirmed in its src/sha256.rs); against hardware sha2 the Apple chain gain is about 1.9x (14.5 vs 27.7 ns/link). rustc version and RUSTFLAGS were not recorded.

## Use it when

- Merkle leaf levels in Rust where dozens of similar-length messages (about 1 KiB Solana shreds, 4 KiB blob slices) are hashed at once: 64 leaves took 7.82 us vs 27.71 us for sha2 on Zen 5, about 2.1x on Zen 4/Zen 3 and Intel Xeon.
- Domain-separated leaves (prefix || body) where avoiding the concatenation copy matters; hash_many_prefixed reads prefix and body from separate slices.
- Verifying or replaying many independent hash chains (proof-of-history entries): 32 chains reached 7.3 ns/link vs 45.4 ns for sha2 on Zen 5.
- Pure-Rust builds that cannot link C batch hashers (Firedancer fd_sha256, isa-l_crypto) but want comparable or better throughput on AMD, and an aarch64 batch path (neon-sha2-x4) that Firedancer lacks.
- Throughput-oriented services that can split a batch across the two idle SMT siblings of one core (1.15-1.48x measured; caller pins the threads).

## Skip it when

- One large message or streaming input: no incremental API and a single message gets no multi-buffer speedup; use sha2, rscrypto or OpenSSL.
- Few messages per call or widely mixed lengths: lanes idle until the longest message in a group finishes and the driver does not sort by length, while the benchmark workload was chosen so all 64 messages have the same block count.
- Intel Emerald Rapids / Granite Rapids when Firedancer's batch hasher is already available: Firedancer was 2-12% faster in wall time there.
- Browser WebAssembly with batched messages of about 1 KiB: the project's own measurements show WebCrypto slightly faster than the simd128 backend.
- Where a mature, audited hash implementation is required: pre-1.0, first commit 2026-07-26, 13 commits, 1 GitHub star, every SIMD backend is unsafe code, and no fuzzing, miri or sanitizer runs are documented.

## How it is fast

Multi-buffer SIMD: messages are transposed so each SIMD lane runs one message's SHA-256 compression in lockstep (8 lanes AVX2, 16 lanes AVX-512, 4 lanes NEON or wasm simd128); on Zen 5 the avx512-2x16 kernel interleaves two 16-lane compressions so one fills the other's dependency stalls. Where hardware SHA units exist (x86 SHA-NI, ARMv8 SHA2) it instead keeps four independent hardware streams in flight (shani-x4, neon-sha2-x4) to hide sha256rnds2 latency. Per-family dispatch picks the kernel by measurement (Zen 5 interlace, Zen 4 and Zen 3 SHA-NI x4, Intel single-wave AVX-512), prefixes are read in place rather than copied, and a batch remainder of 1-12 messages is routed to SHA-NI instead of a mostly empty 16-lane group.

## Compared with alternatives

Pick it over Firedancer fd_sha256 batch or Intel ISA-L Crypto when you are in Rust and want no C build, need aarch64 or wasm, hash prefixed leaves without copying, or run on AMD (it measured 60% faster than Firedancer and 39% faster than isa-l_crypto on Zen 5); keep Firedancer on Intel Xeon where it led by 2-12%. Pick hashtree instead for fixed 64-byte Merkle pair hashing from C, and rscrypto or sha2 for single-message or streaming SHA-256.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (sha2, rand and ed25519-dalek are dev-dependencies only; Firedancer and isa-l_crypto are linked only under benchmark features) |
| **Minimum toolchain** | Rust 1.89 (rust-version), edition 2021, stable |
| **Platforms** | x86-64 with runtime dispatch over AVX-512F+BW, SHA-NI and AVX2; aarch64 with ARMv8 SHA2 extensions or NEON; wasm32 with simd128 (selected at build time, -C target-feature=+simd128); portable scalar fallback elsewhere |
| **Thread safety** | Entry points are stateless and may be called concurrently on disjoint inputs and outputs; the kernel choice is resolved once and cached in a OnceLock. The crate never spawns or pins threads. |
| **Drop-in for the baseline** | partial — produces bit-identical SHA-256 digests, but replaces per-message Sha256::new/update/finalize with batch calls over slices; no Digest trait or streaming interface |

## Gotchas

- The scalar, avx2, avx512 and neon Cargo features pin a kernel at build time and fault on CPUs lacking it; -C target-cpu=native made the Zen 5 interlaced kernel 8-14% slower, so re-benchmark before adding it.
- Output slices must have exactly one digest per message or the call panics; a batch is processed in input order in groups of the lane width, so mixed lengths waste lanes until the longest message in each group finishes.
- Harness gap: BENCHMARKS.md says every reference entry point is checked against sha2 before timing, but in benches/merkle_leaves.rs and benches/blob_group.rs only the isa-l_crypto rows are gated; the Firedancer rows are timed without a digest check (a wiring error there would affect the Firedancer comparison, not tape's own numbers, which tests/differential.rs checks against sha2).
- Headline numbers are best-case: best of 15 rounds of 50 iterations over the same cache-resident 67,680-byte batch, and the Zen 5 7.82 us is the best of three pinned invocations (7.82, 8.30, 8.34 us); the Zen 5 machine is unidentified, and the dispatch comment in src/lib.rs cites 12.7 us for the same kernel on an EPYC 9B45. AVX-512 kernels are not guaranteed to run in CI (GitHub-hosted ubuntu and macOS runners only).

## Known shortcomings

- First-party with rustc version and RUSTFLAGS unstated; the Apple 6.8x is against sha2's software path (hardware-to-hardware about 1.9x on chains); the OpenSSL comparison through node:crypto is cross-run; 2-12% slower than Firedancer on Intel. The listed repository URL returns 404; the code lives at spool-labs/sha256 (same commit 5e72f67).
- Enricher: BENCHMARKS.md says every reference entry point is checked against sha2 before timing, but only the isa-l_crypto rows are gated in the benches; the Firedancer rows are timed unchecked (tape's own kernels are checked by tests/differential.rs). Best-case framing: 64 equal-block-count messages, cache-hot batch, best of 15x50; the Zen 5 7.82 us is the best of three runs on an unidentified CPU (src/lib.rs gives 12.7 us for the same kernel on an EPYC 9B45); the driver does not sort by length, so mixed-length batches leave lanes idle. sha2 0.10.9 uses its aarch64 hardware path only with the asm feature, so the Apple 6.8x is against software sha2. CI runs on GitHub-hosted runners only with no guaranteed AVX-512 coverage and no miri or sanitizers.

## Caveats and trade-offs

The crates.io repository field (https://github.com/spool-labs/tape-sha256) returns 404; the code lives at https://github.com/spool-labs/sha256 (README names the crate tape-sha256; head commit 5e72f67 'minor cleanup' of 2026-08-11 matches the crate's .cargo_vcs_info.json), so repo_url should be overridden to that repository. First-party measurements by the author, and the main baseline is the Rust sha2 crate, not OpenSSL. On x86 sha2 0.10.9 uses SHA-NI by runtime detection, so those ratios are against a hardware-accelerated serial baseline; on Apple the 6.8x batch figure is against the sha2 software path (the crate's asm feature, available here only as the sha2-asm-bench bench feature, was off), so the hardware-to-hardware Apple gain is much smaller (hash chains: 14.5 vs 27.7 ns, about 1.9x). The only OpenSSL comparison is through Node.js (per-call JS overhead included, M4 Max unpinned, native batch number from a different document than the node:crypto number, so cross-run). Same-machine paired runs, but rustc version, RUSTFLAGS and the Zen 5 and Apple CPU models are not captured; -C target-cpu=native made the Zen 5 kernel 8-14% slower. Does not win everywhere: 2-12% slower than Firedancer on Intel Emerald / Granite Rapids; the Firedancer harness builds prefix||leaf outside the timed region while tape reads prefix and body from separate slices. Results are single-core batch hashing, not application speedups (the README also cites 14-21% faster Agave shred recovery, unverified). Tests cross-check every backend against the sha2 crate. Very young project (first commit 2026-07-26), 1 GitHub star.

Pure Rust (stable, no C dependency) multi-buffer SHA-256: hash_many, hash_many_prefixed, hash_pairs for independent messages (SIMD lane per message) and hash_chain / hash_chains for iterated 32-byte hashing (Solana proof-of-history). Runtime dispatch over AVX-512, AVX2, SHA-NI, ARM SHA-2, NEON, WebAssembly simd128 and portable fallbacks. No streaming single-message API, so a single large message gets no speedup; pre-1.0. WebCrypto beats the wasm build for batched \~1 KB messages in Chrome.

## Maintenance

Active but very young (13 commits from 2026-07-26 to 2026-08-11, crate 0.2.1 with 470 downloads, no issues filed), Apache-2.0 pure Rust with no dependencies and copyable; the code lives at github.com/spool-labs/sha256 because the crate's repository link 404s, SECURITY.md still names 0.1.x as the supported line, and the benchmark harness times Firedancer rows without the sha2 check its documentation claims.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party BENCHMARKS.md with public bench code (benches/merkle_leaves.rs, poh_chain.rs, blob_group.rs) and CPU models for four machines, but the rustc version and RUSTFLAGS are not stated and the Zen 5 and Apple CPU models are not captured, so it falls short of A.
- **Verifier notes:** Real repo found: https://github.com/spool-labs/sha256 (record repo_url 404s; please override repo_url). Numbers match BENCHMARKS.md; harness reviewed (sha2 baseline is plain Sha256::new/update/finalize per leaf, black_box on outputs, reference entry points checked against sha2). Shortcomings: first-party only, compiler version/flags unstated, Apple 6.8x is against sha2's software path, OpenSSL comparison cross-run via Node, slower than Firedancer on Intel.
- **Fields the verifier corrected:** `benchmark_url`, `last_commit`, `stars_or_usage`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 7 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://crates.io/api/v1/crates/tape-sha256/0.2.1/download>
  - <https://crates.io/api/v1/crates/tape-sha256>
  - <https://github.com/spool-labs/tape-sha256>
  - <https://github.com/spool-labs>
  - <https://github.com/spool-labs/sha256>
  - <https://github.com/spool-labs/sha256/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/README.md>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/README.md>
  - https://static.crates.io/crates/tape-sha256/tape-sha256-0.2.1.crate (src/lib.rs, src/batch.rs, benches/merkle_leaves.rs, benches/poh_chain.rs, benches/blob_group.rs, tests/differential.rs, build.rs, SECURITY.md, .github/workflows/ci.yml, .cargo_vcs_info.json)
  - https://static.crates.io/crates/sha2/sha2-0.10.9.crate (src/sha256.rs backend selection)
  - <https://crates.io/api/v1/crates/tape-sha256>
  - <https://github.com/spool-labs/sha256>
  - <https://github.com/spool-labs/sha256/issues?q=is%3Aissue>
  - <https://github.com/spool-labs/sha256/commits>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/spool-labs/tape-sha256`) · [data/wave7/enrich/raw/github_com_spool_labs_tape_sha256.json](../../../data/wave7/enrich/raw/github_com_spool_labs_tape_sha256.json) (enrichment confidence 0.72)

</details>
