# Intel ISA-L Crypto (multi-buffer SHA)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Intel's SIMD multi-buffer SHA/MD5/SM3 hashing library; beats single-buffer SHA-256 throughput when many independent buffers are in flight.

| | |
|---|---|
| **Beats** | The best-known single-buffer SHA-256 of 2012. The whitepaper cites Intel's own 'Fast SHA-256 Implementations on Intel Architecture Processors' (Guilford, Yap, Gopal, May 2012; ref [4]). OpenSSL is not named. |
| **Claimed result** | \~5 cycles/byte for Multi-Hash SHA-256 on a 1 MB buffer, 'over 2X faster than the best known SHA-256 single buffer implementations' (Executive Summary). The Results section says SHA256x4 Multi-Hash gives a '\~2.6X performance gain over the best SHA256 algorithm computation' at 1 MB, and MD5 Multi-Hash (x8) gives '\~4.4X'. |
| **Workload** | Multi-Hash SHA-256 (SHA256x4) of a single 1 MB buffer on one core with Hyper-Threading and Turbo Boost off. SHA256x4 is a tree-mode extension that interleaves one buffer across 4 SIMD lanes and then hashes the lane digests, so its output is not a standard SHA-256 digest. Timing is rdtsc cycles/byte, using the trimmed mean of many runs. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-2600 (Sandy Bridge), single core with Intel HT Technology, Turbo Boost off |
| **Adoption** | 302 stars |
| **Last commit** | 2026-07-23 |
| **Links** | [repository](https://github.com/intel/isa-l_crypto) · [benchmark](https://raw.githubusercontent.com/wiki/intel/isa-l_crypto/pdf/multi-hash-paper.pdf) |

## Verdict

Intel's own July 2012 whitepaper reports that SHA256x4 Multi-Hash (a non-standard 4-segment tree mode) hashed a 1 MB buffer at about 5 cycles/byte on one core of a Sandy Bridge Core i7-2600 with Turbo off. That was about 2.6x faster than Intel's best single-buffer SHA-256 of the day (not OpenSSL), and MD5 x8 was about 4.4x faster. The paper gives no compiler, flags or code version, the shipped mh_sha256 uses 16 segments rather than 4, and nothing is published for the standard-digest sha256_mb or against SHA-NI hardware.

## Use it when

- Storage, dedup or object-store pipelines that checksum many independent chunks or objects at the same time (Ceph and SPDK vendor it as a git submodule).
- You can keep at least a lane-width of jobs in flight (4 for SSE, 8 for AVX2, 16 for AVX-512) and can handle jobs completing out of order.
- AVX-512 x86 servers that regularly have more than 6 SHA-256 jobs active at once. Below that the manager falls back to SHA-NI single-buffer code anyway.
- Legacy MD5/SHA-1 checksumming of many streams, where the dependency chain leaves scalar code furthest behind (the whitepaper reports its largest gain, \~4.4x, for MD5 x8).
- mh_sha256, only in a closed system such as dedup fingerprints where both producer and verifier use Multi-Hash and buffers are 1 KB or larger.

## Skip it when

- Hashing one stream at a time with submit-then-flush. Users measured it slower than OpenSSL: 3.36 s vs 2.48 s for 1 GB of SHA-256 (issue #111) and 466 vs 787 MB/s for single-buffer MD5 (issue #45). The maintainer's answer is to keep multiple jobs in flight.
- You need a fast standard SHA-256 of one large buffer. mh_sha256 digests are not interoperable, and on x86 mh_sha256 dispatches only SSE/AVX/AVX2/AVX-512 (no SHA-NI path).
- Small messages with Multi-Hash. The whitepaper says the gains diminish for buffers below about 1 KB, and the maintainers say it needs blocks of about 1 KB.
- macOS or Apple Silicon. They are not in CI (Linux x86-64/arm64/RISC-V and Windows are), and past issues report build failures on M1 (#86) and on macOS x86 (#88).
- You need a certified or general-purpose crypto API. The README says it cannot achieve CMVP certification as a standalone module, and it has no HMAC, SHA-3 or BLAKE.

## How it is fast

It uses multi-buffer SIMD hashing: each vector lane runs the SHA-256 compression function on a different message, giving 4 messages per pass with SSE/AVX, 8 with AVX2 and 16 with AVX-512, and an out-of-order job scheduler keeps the lanes filled. On CPUs with SHA extensions the manager switches to SHA-NI x1/x2 kernels when few lanes are busy (thresholds are 4 lanes on the SSE path and 6 on the AVX-512 path; a source comment says 'shani is faster than sse sha256_mb'). Multi-Hash applies the same lane trick to a single buffer: it interleaves the buffer word by word into 16 segments, hashes them in parallel, then hashes the concatenated segment digests (a two-level tree hash). The kernels are hand-written NASM/gas assembly, chosen at runtime by CPUID dispatch.

## Compared with alternatives

Pick it over BLAKE3 or KangarooTwelve when the digest must stay standard SHA-256/SHA-1/MD5 because of a fixed protocol or on-disk format, and you have many independent buffers to batch. If you control the hash choice and need one big buffer hashed fast, BLAKE3 or K12 fits better. The j-lanes and S-HASH entries describe the same multi-lane ideas as papers; this is Intel's maintained, shipping C/asm implementation, and sha256-simd is the Go-ecosystem counterpart.

## Integration

| | |
|---|---|
| **Form** | static lib / shared lib (autotools, Makefile.unx, nmake on Windows; CMake experimental) |
| **Dependencies** | None at runtime beyond libc. The build needs NASM on x86-64 (gas on aarch64/RISC-V). OpenSSL is used only by the tests, perf harnesses and examples. |
| **Minimum toolchain** | x86-64: NASM 2.14.01+ with GCC, Clang, ICC or MSVC 2019+. aarch64: gas 2.34+ and GCC 8+ (older gas needs --disable-sve2). RISC-V RVV: gas 2.39+ and GCC 12.1+. |
| **Platforms** | x86-64 (SSE4 minimum for SIMD paths; AVX/AVX2/AVX-512/SHA-NI chosen at runtime), aarch64 (crypto extensions, SVE2), RISC-V 64 (RVV), and a portable C base elsewhere. 32-bit x86 was removed in v2.26. |
| **Thread safety** | Not documented. Managers and contexts are plain caller-owned structs with no internal locking, so use one manager per thread. Re-submitting a context that is still in flight returns ISAL_HASH_CTX_ERROR_ALREADY_PROCESSING. |
| **Drop-in for the baseline** | partial — sha256_mb produces standard SHA-256 digests but needs an asynchronous submit/flush batching API and returns host-order uint32 words; mh_sha256 has a synchronous init/update/finalize API but produces a different, non-standard digest |

## Gotchas

- SHA-1/SHA-256 results come back as uint32 words in host order, so you must byte-swap them on little-endian to get the canonical digest, while MD5 comes back already byte-ordered (issue #121).
- A context cannot be re-submitted until submit() or flush() hands it back, and contexts return out of order. Submitting LAST straight after FIRST without flushing looked like a wrong-hash bug to one user (#156). Redundant flush() calls are safe.
- The manager must be 16-byte aligned (the tests use posix_memalign). A misaligned manager crashed the AVX2 flush under MSVC (#122). The mh_sha256 context is about 3.7 KB, and the header advises heap allocation.
- Each submit/update call takes a uint32 length (under 4 GB per call). -flto needs -fno-strict-aliasing or tests can fail (#162, #165). The non-isal_-prefixed API has been deprecated since v2.25.

## Known shortcomings

- The cited paper covers Multi-Hash (a non-standard x4 digest), not the multi-buffer API; the \~2.6x baseline is Intel's own SHA-256 code, not OpenSSL. The repo ships sha256_mb_vs_ossl_perf.c but publishes no results. Gains need many independent buffers in flight.
- Only performance source is Intel's 2012 whitepaper on Sandy Bridge (pre-SHA-NI) for the non-standard SHA256x4 Multi-Hash; the standard sha256_mb API has no published numbers. Users report single-stream use slower than OpenSSL (#111: 1 GB SHA-256 3.36 s vs 2.48 s; #45: MD5 466 vs 787 MB/s), and the source itself notes SHA-NI beats SSE sha256_mb. SIMD lanes only help with &gt;4 (SSE) / &gt;6 (AVX-512) jobs in flight; x86 mh_sha256 has no SHA-NI path. Async submit/flush API with out-of-order completion, host-order digest words, 16-byte manager alignment, &lt;4 GB per submit. Not standalone CMVP; no HMAC or SHA-3.

## Caveats and trade-offs

The only published performance source is Intel's own July 2012 Multi-Hash whitepaper, run on a Core i7-2600 that predates SHA-NI. Its baseline is Intel's best-known single-buffer SHA-256 code (ref [4]), not OpenSSL, and it states no compiler or flags. It measures Multi-Hash, a tree-mode SHA-256 variant whose digest is not interoperable with standard SHA-256, in a 4-lane (SHA256x4) layout. The shipped mh_sha256 uses 16 segments (ISAL_HASH_SEGS 16), so the paper's figures do not describe the current code. The library's standard-digest multi-buffer SHA-256 (sha256_mb) has no published numbers. The repo does ship OpenSSL head-to-head perf harnesses (sha256_mb/sha256_mb_vs_ossl_perf.c, sha1_mb/sha1_mb_vs_ossl_perf.c) but commits no results. No modern comparison against OpenSSL with SHA extensions was found.

Only accelerates throughput when multiple independent buffers can be scheduled concurrently; needs application-level batching (not a transparent single-call speedup); requires NASM/gas for the hand-written SIMD kernels.

## Maintenance

Actively maintained by Intel: v2.26.1 was released 2026-06-12, the last commit is 2026-07-23, and CI covers x86-64 Linux/Windows, arm64 and RISC-V. It is BSD-3-Clause and vendored by Ceph and SPDK, but it is an assembly-heavy built library rather than a file you can copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** This is a first-party Intel whitepaper from July 2012. It states the CPU (Core i7-2600, HT on, Turbo off) and the timing method (rdtsc, 1 MB buffer, trimmed mean). It gives no compiler or flags, and the benchmarked code is neither identified nor public. It compares against Intel's own best single-buffer SHA-256, so it is C.
- **Verifier notes:** The quoted numbers match the whitepaper verbatim, and the repo README links it as the Multi-Hash spec. The record mixed up multi-buffer (standard digests over many buffers) with Multi-Hash (a non-standard single-buffer tree mode); the workload and caveats are fixed. last_commit is the committer date (2026-07-23); 2026-07-15 is the author date. GitHub reports the license as NOASSERTION, but the root LICENSE file is BSD-3-Clause (it carries an SPDX line). The usage claims in stars_or_usage were not checked.
- **Fields the verifier corrected:** `baseline`, `workload`, `claimed_speedup`, `hardware`, `last_commit`, `caveats`
- **Shortcomings recorded by:** GitHub #111: 1 GB SHA-256 single stream 3.36 s vs OpenSSL 2.48 s; #45: MD5 466 vs OpenSSL 787 MB/s.
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wiki/intel/isa-l_crypto/pdf/multi-hash-paper.pdf>
  - <https://github.com/intel/isa-l_crypto>
  - <https://github.com/intel/isa-l_crypto/blob/master/LICENSE>
  - <https://github.com/intel/isa-l_crypto/blob/master/README.md>
  - <https://github.com/intel/isa-l_crypto/blob/master/sha256_mb/sha256_mb_vs_ossl_perf.c>
  - <https://github.com/intel/isa-l_crypto/blob/master/include/isa-l_crypto/mh_sha256.h>
  - <https://github.com/intel/isa-l_crypto/blob/master/Release_notes.txt>
  - <https://github.com/intel/isa-l_crypto/wiki>
- **Sources the enricher read:**
  - <https://github.com/intel/isa-l_crypto>
  - <https://github.com/intel/isa-l_crypto/blob/master/README.md>
  - <https://github.com/intel/isa-l_crypto/blob/master/Release_notes.txt>
  - <https://github.com/intel/isa-l_crypto/blob/master/FIPS.md>
  - <https://github.com/intel/isa-l_crypto/blob/master/LICENSE>
  - <https://github.com/intel/isa-l_crypto/blob/master/include/isa-l_crypto/sha256_mb.h>
  - <https://github.com/intel/isa-l_crypto/blob/master/include/isa-l_crypto/multi_buffer.h>
  - <https://github.com/intel/isa-l_crypto/blob/master/include/isa-l_crypto/mh_sha256.h>
  - <https://github.com/intel/isa-l_crypto/blob/master/include/multibinary.asm>
  - <https://github.com/intel/isa-l_crypto/blob/master/sha256_mb/sha256_multibinary.asm>
  - <https://github.com/intel/isa-l_crypto/blob/master/sha256_mb/sha256_job.asm>
  - <https://github.com/intel/isa-l_crypto/blob/master/sha256_mb/sha256_ctx_sse_ni.c>
  - <https://github.com/intel/isa-l_crypto/blob/master/sha256_mb/sha256_mb_mgr_flush_avx512_ni.asm>
  - <https://github.com/intel/isa-l_crypto/blob/master/sha256_mb/sha256_mb_mgr_submit_sse_ni.asm>
  - <https://github.com/intel/isa-l_crypto/blob/master/sha256_mb/sha256_mb_mgr_flush_sse_ni.asm>
  - <https://github.com/intel/isa-l_crypto/blob/master/sha256_mb/sha256_mb_vs_ossl_perf.c>
  - <https://github.com/intel/isa-l_crypto/blob/master/mh_sha256/mh_sha256_multibinary.asm>
  - <https://github.com/intel/isa-l_crypto/blob/master/mh_sha256/mh_sha256_perf.c>
  - <https://github.com/intel/isa-l_crypto/blob/master/examples/saturation_test/README.txt>
  - <https://github.com/intel/isa-l_crypto/blob/master/examples/saturation_test/isal_multithread_perf.h>
  - <https://github.com/intel/isa-l_crypto/blob/master/.github/workflows/ci.yml>
  - <https://github.com/intel/isa-l_crypto/releases>
  - <https://github.com/intel/isa-l_crypto/issues>
  - <https://github.com/intel/isa-l_crypto/issues/111>
  - <https://github.com/intel/isa-l_crypto/issues/45>
  - <https://github.com/intel/isa-l_crypto/issues/156>
  - <https://github.com/intel/isa-l_crypto/issues/162>
  - <https://github.com/intel/isa-l_crypto/issues/174>
  - <https://github.com/intel/isa-l_crypto/issues/175>
  - <https://github.com/intel/isa-l_crypto/issues/164>
  - <https://github.com/intel/isa-l_crypto/issues/102>
  - <https://github.com/intel/isa-l_crypto/issues/122>
  - <https://github.com/intel/isa-l_crypto/issues/121>
  - <https://github.com/intel/isa-l_crypto/issues/113>
  - <https://github.com/intel/isa-l_crypto/issues/46>
  - <https://github.com/intel/isa-l_crypto/issues/86>
  - <https://github.com/intel/isa-l_crypto/issues/88>
  - <https://github.com/intel/isa-l_crypto/security/advisories>
  - <https://raw.githubusercontent.com/wiki/intel/isa-l_crypto/pdf/multi-hash-paper.pdf>
  - <https://github.com/ceph/ceph/blob/main/.gitmodules>
  - <https://github.com/spdk/spdk/blob/master/.gitmodules>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/intel/isa-l_crypto`) · [data/wave7/enrich/raw/github_com_intel_isa_l_crypto.json](../../../data/wave7/enrich/raw/github_com_intel_isa_l_crypto.json) (enrichment confidence 0.8)

</details>
