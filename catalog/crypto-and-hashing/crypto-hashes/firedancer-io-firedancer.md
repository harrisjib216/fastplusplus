# Firedancer fd_sha256 batch (AVX-512 / AVX2 / SHA-NI)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Firedancer's 8- and 16-lane multi-buffer SHA-256 kernels in C; about 2x the Rust sha2 crate on AVX-512 x86.

| | |
|---|---|
| **Beats** | single-buffer SHA-256: Rust sha2 crate (serial, hardware-accelerated) in the only numeric comparison found; no OpenSSL comparison found |
| **Claimed result** | Versus sha2 serial, same session (ratios derived from page data): AMD Zen 5 avx512-16 12.55 us/batch (5393 MB/s) vs 27.71 us (2443 MB/s), about 2.2x; AMD Zen 4 EPYC 9B14 avx512-16 22.51 us (3006 MB/s) vs 43.71 us (1548 MB/s), about 1.9x; Xeon Platinum 8581C avx512-16 21.82 us (3102 MB/s) vs 49.18 us (1376 MB/s), about 2.25x; Xeon 6985P-C avx512-16 16.89 us (4006 MB/s) vs 36.87 us (1835 MB/s), about 2.2x. Not faster on AMD Zen 3 EPYC 7B13: avx-8 45.87 us (1476 MB/s) vs sha2 42.66 us (1587 MB/s), about 0.93x. The crate author's tape-sha256 beat Firedancer by 60% on Zen 5 but was 2-12% slower on the Intel parts. |
| **Workload** | Third-party harness (tape-sha256 merkle_leaves bench): one Solana erasure batch of 64 independent messages, each a 26-byte prefix plus about 1 KiB payload (67,680 bytes per batch), one thread pinned to one physical core, best of 15 rounds of 50 iterations; the Firedancer harness builds prefix\|\|leaf outside the timed region. Firedancer built from source on the test machine. |
| **Metric** | throughput |
| **Hardware** | AMD Zen 5 (family 0x1a, model not captured); EPYC 9B14 (GCP c3d); EPYC 7B13 (GCP c2d); Xeon Platinum 8581C (GCP c4); Xeon 6985P-C (GCP c4-standard-8-lssd) |
| **Compiler and flags** | Firedancer 'built from source on the machine being tested' with a machine profile that exports the AVX-512 symbol (e.g. build/linux/gcc/zen5); compiler version and flags otherwise not stated |
| **Adoption** | 1.5k stars; Jump Crypto's Solana validator |
| **Last commit** | 2026-10-12 |
| **Links** | [repository](https://github.com/firedancer-io/firedancer) · [benchmark](https://github.com/spool-labs/sha256/blob/main/BENCHMARKS.md) |

## Verdict

In tape-sha256's merkle_leaves bench (64 messages of about 1.05 KiB, one pinned core, best of 15 rounds of 50 iterations), Firedancer's 16-lane AVX-512 kernel ran 12.55 vs 27.71 us per batch on Zen 5, 22.51 vs 43.71 on EPYC 9B14, 21.82 vs 49.18 on Xeon 8581C and 16.89 vs 36.87 on Xeon 6985P-C against the Rust sha2 0.10.9 crate hashing one message at a time with SHA-NI (about 1.9-2.25x, derived from page data), while the 8-lane AVX2 kernel lost on EPYC 7B13 (45.87 vs 42.66 us). Firedancer was built by the rival crate's author from source with unstated compiler version and flags, and no OpenSSL comparison exists.

## Use it when

- Hashing many independent, similar-sized messages per call on an AVX-512 x86 server, such as Merkle-tree leaves (Solana's 64-shred erasure sets of about 1 KiB each), where it measured about 1.9-2.25x the serial Rust sha2 crate on Zen 4, Zen 5, Emerald Rapids and Granite Rapids.
- Advancing 16 or more independent SHA-256 chains (Proof of History style) with fd_sha256_hash_32_repeated_batch, which the header says has higher throughput than the scalar path at fd_sha256_simd_lane_min lanes and above.
- C or C++ codebases on Linux x86-64 that can vendor Apache-2.0 code and want a batch hasher without pulling in isa-l_crypto's job-manager API.
- Throughput-bound pipelines where per-message latency does not matter (the header warns individual latency can be about 8x worse in the SIMD repeated-hash path).

## Skip it when

- Single messages or small batches: batches under 5-6 messages fall back to SHA-NI or scalar code, so there is no gain over OpenSSL or any SHA-NI hasher.
- Zen 1-3 (AVX2 only): the 8-lane AVX path measured 0.93x the serial sha2 crate on an EPYC 7B13, and Firedancer's own header disables the AVX batch implementation when built with -mtune=znver1/2/3.
- Non-x86 targets: there is no AArch64 or RISC-V batch kernel; those builds use the per-message reference batch path.
- Messages split across buffers (prefix plus payload): each message must be one contiguous (pointer, size) region, so a domain-separation prefix forces a copy that tape-sha256's prefixed API avoids.
- Projects that cannot take on Firedancer's build: the code depends on fd_util and the util/simd headers and is selected by Firedancer machine profiles, not a standalone package.

## How it is fast

Multi-buffer (lane-per-message) SHA-256: up to 8 messages run in the AVX2 lanes (fd_sha256_batch_avx.c) or 16 in the AVX-512 lanes (fd_sha256_batch_avx512.c), so one SIMD instruction advances the compression function of every message at once. Message blocks are loaded in place and transposed (transpose_16x16 / 2x8x8), the padded tail blocks are prepared in a scratch area up front, and the AVX-512 kernel uses vprold rotates and, since PR #11442 (merged 2026-09-13), vpternlogd to fold each round's boolean functions into 4 instead of 12 logic ops. Batches below 5 (AVX-512) or 6 (AVX2) messages fall back to narrower kernels or per-message SHA-NI.

## Compared with alternatives

Pick it over tape-sha256 on Intel AVX-512 parts, where the rival's own runs show Firedancer 2-12% faster, and over isa-l_crypto sha256_mb when you want a synchronous batch call in plain C rather than a job manager; pick tape-sha256 on Zen 3-5 and Apple silicon, and hashtree when the workload is a fixed-shape 64-byte-pair Merkle tree.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Firedancer's fd_util (logging, bit helpers) and util/simd/fd_avx.h and fd_avx512.h headers; built with Firedancer's GNU make machine profiles (config/machine/\*.mk) |
| **Minimum toolchain** | GCC 8 is Firedancer's stated minimum (config/machine/linux_gcc_zen2.mk); clang profiles also exist; Linux only, kernel 4.18 or newer to build the project |
| **Platforms** | x86-64 with AVX2 (8-lane) or AVX-512 (16-lane) for the batch kernels; SHA-NI, Arm SHA2 and RISC-V scalar-crypto cores for single-message hashing; generic C elsewhere |
| **Thread safety** | Not documented beyond object ownership; each fd_sha256_t or fd_sha256_batch_t is caller-owned state with no locking, so use one per thread |
| **Drop-in for the baseline** | partial — the one-shot fd_sha256_hash and incremental API replace a single-buffer SHA-256 call, but the speedup needs the batch init/add/fini API with many independent messages |

## Gotchas

- Harness flaw in the only comparison: tape-sha256's merkle_leaves bench calls the internal kernels fd_sha256_private_batch_avx and fd_sha256_private_batch_avx512 directly, bypassing the header dispatch that disables the AVX batch path under -mtune=znver1/2/3; the Zen 3 0.93x row therefore times a kernel Firedancer itself does not select on that CPU (its real API would hash per message with SHA-NI there).
- The same harness gates isa-l_crypto's output against sha2 before timing but never checks the Firedancer kernel's digests, so a mis-wired FFI would go unnoticed; Firedancer's own test_sha256.c (extended in PR #11442) checks the batch path against fd_sha256_hash at every size up to 4096 in every lane.
- The measured Firedancer build predates PR #11442 (merged 2026-09-13; the Zen 5 run is dated 2026-08-08): that PR reports Zen 4 leaf hashing of a 64-shred FEC set going from 2.92 to 3.53 GB/s, so current Firedancer is likely faster than the published rows (first-party, cross-run figure).
- fd_sha256_batch_add does no input validation; output regions must not overlap each other or any message, inputs must stay valid until fini or abort, and abort leaves the outputs in an unspecified state.

## Known shortcomings

- The only numbers come from the rival tape-sha256 BENCHMARKS.md, against the Rust sha2 crate rather than OpenSSL; the batch kernel is slower than serial SHA-NI on Zen 3 (0.93x).
- Enricher: the tape-sha256 harness calls the internal kernels fd_sha256_private_batch_avx and _avx512 directly, skipping the header dispatch; fd_sha256.h turns the AVX batch path off under -mtune=znver1/2/3, so the Zen 3 0.93x row times a kernel Firedancer never picks on that CPU, and the harness checks isa-l digests against sha2 but never Firedancer's. The measured build predates Firedancer PR #11442 (2026-09-13), which reports Zen 4 FEC-set leaf hashing going from 2.92 to 3.53 GB/s. The batch API needs one contiguous (ptr, sz) per message.

## Caveats and trade-offs

The repo itself carries no baseline numbers: src/ballet/sha256/test_sha256.c --bench prints only Gbps 'Ethernet equiv throughput / core' for incremental, streamlined and batched modes (14 and 1472 byte payloads) with no OpenSSL or other baseline row (its only OpenSSL mention is a comment on generating a test vector). The only comparison is from the rival tape-sha256 crate (BENCHMARKS.md in https://github.com/spool-labs/sha256, the crate's real repository; the crates.io repository field https://github.com/spool-labs/tape-sha256 returns 404), against the Rust sha2 0.10.9 crate (which uses SHA-NI on x86 via runtime detection) rather than OpenSSL, with Firedancer built by the benchmark author, who competes with it, using unstated compiler version and flags. The harness hoists the prefix||leaf concatenation for Firedancer out of the timed region and checks every reference entry point against sha2 before timing. Batch hashing needs independent messages. Zen 5 CPU model not captured. Zen 3 (avx-8 only, 0.93x) shows the AVX batch path is not always faster than serial SHA-NI, and on Zen 4 the AVX-512 path is only about 1.9x. [retier] Enricher: tape-sha256's harness calls fd_sha256_private_batch_avx and _avx512 directly, skipping the header dispatch that disables the AVX batch path under -mtune=znver1/2/3, so the Zen 3 0.93x row times a kernel Firedancer never selects there; Firedancer digests are not checked in that harness; the measured build predates PR #11442 (Zen 4 leaf hashing 2.92 to 3.53 GB/s).

src/ballet/sha256 has fd_sha256_batch_avx.c (8 lanes) and fd_sha256_batch_avx512.c (16 lanes) for independent messages, plus fd_sha256_hash_32_repeated_batch for PoH-style chains; the batch API needs contiguous messages and falls back to SHA-NI or scalar for small batches. Depends on Firedancer's util headers (fd_util, simd/fd_avx512.h), so extraction means vendoring part of the tree. The scalar core fd_sha256_core_ref is derived from OpenSSL's OPENSSL_SMALL_FOOTPRINT SHA-256 (Apache-2.0).

## Maintenance

Actively developed (batch kernel and bmtree changes merged in September 2026) and Apache-2.0, but the SHA-256 kernels live inside a large validator tree, so reuse means vendoring src/ballet/sha256 plus parts of src/util.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The only comparison is the rival tape-sha256 crate's BENCHMARKS.md (bench code benches/merkle_leaves.rs public, CPU models given for four of five x86 machines) against the Rust sha2 crate; rustc/gcc versions and Firedancer build flags are not stated, and the measurer competes with Firedancer, so not A and not an independent well-known suite.
- **Verifier notes:** Numbers and derived ratios match BENCHMARKS.md exactly (Zen 5 12.55 vs 27.71 us; 9B14 22.51 vs 43.71; 7B13 45.87 vs 42.66; 8581C 21.82 vs 49.18; 6985P-C 16.89 vs 36.87). benchmark_url moved from the crates.io tarball to the GitHub BENCHMARKS.md (same commit 5e72f67). Shortcomings: no first-party comparison, rival-run harness, baseline is Rust sha2 not OpenSSL, slower than serial SHA-NI on Zen 3; last commit 2026-10-12, 1.5k stars, Apache-2.0 confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 7 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/firedancer-io/firedancer>
  - <https://github.com/firedancer-io/firedancer/commits>
  - <https://raw.githubusercontent.com/firedancer-io/firedancer/HEAD/src/ballet/sha256/test_sha256.c>
  - <https://crates.io/api/v1/crates/tape-sha256/0.2.1/download>
  - <https://github.com/spool-labs/sha256>
- **Sources the enricher read:**
  - <https://github.com/firedancer-io/firedancer>
  - <https://github.com/firedancer-io/firedancer/issues?q=sha256>
  - <https://github.com/firedancer-io/firedancer/pull/11442>
  - <https://raw.githubusercontent.com/firedancer-io/firedancer/HEAD/README.md>
  - <https://raw.githubusercontent.com/firedancer-io/firedancer/HEAD/config/machine/linux_gcc_zen2.mk>
  - <https://raw.githubusercontent.com/firedancer-io/firedancer/HEAD/src/ballet/sha256/fd_sha256.h>
  - <https://raw.githubusercontent.com/firedancer-io/firedancer/HEAD/src/ballet/sha256/fd_sha256.c>
  - <https://raw.githubusercontent.com/firedancer-io/firedancer/HEAD/src/ballet/sha256/fd_sha256_batch_avx.c>
  - <https://raw.githubusercontent.com/firedancer-io/firedancer/HEAD/src/ballet/sha256/fd_sha256_batch_avx512.c>
  - <https://raw.githubusercontent.com/firedancer-io/firedancer/HEAD/src/ballet/sha256/test_sha256.c>
  - <https://raw.githubusercontent.com/firedancer-io/firedancer/HEAD/src/ballet/sha256/Local.mk>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/merkle_leaves.rs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/README.md>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/Cargo.toml>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/firedancer-io/firedancer`) · [data/wave7/enrich/raw/github_com_firedancer_io_firedancer.json](../../../data/wave7/enrich/raw/github_com_firedancer_io_firedancer.json) (enrichment confidence 0.6)

</details>
