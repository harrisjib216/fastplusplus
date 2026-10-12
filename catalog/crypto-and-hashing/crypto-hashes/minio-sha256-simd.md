# sha256-simd (minio)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🔴 abandoned

> Go SHA-256 using SHA-NI, ARMv8 SHA2 and 16-lane AVX-512; once beat crypto/sha256, now only its multi-buffer mode might.

| | |
|---|---|
| **Beats** | Go crypto/sha256 (stdlib) |
| **Claimed result** | Against Go crypto/sha256 (the README's 'golang' column), the ARM64 path on a 1.2GHz Cortex-A53 (Pine64) is 8.38x at 8B, 57.75x at 1KB, 95.11x at 8KB and 105.49x at 1MB (638.23 vs 6.05 MB/s). That Go version predates stdlib ARM64 SHA2 support. The x86 figures are package-internal: AVX512 3498.20 vs its own AVX2 path 448.62 MB/s (7.80x, BenchmarkHash5M, 3.0GHz Xeon Platinum 8124M), and SHA Extensions 1975.17 vs its own AVX2 path 514.40 MB/s (3.84x, BenchmarkHash5M, 3.7GHz Ryzen 7 2700X per the README Performance table). |
| **Workload** | Single-core SHA256 hashing of 8B-10MB buffers (the Performance table uses &gt;1MB blocks): the package's ARM64 path against Go crypto/sha256 on a Cortex-A53, and its AVX512 and SHA-Ext paths against its own AVX2 path on x86. |
| **Metric** | throughput |
| **Hardware** | 3.0 GHz Intel Xeon Platinum 8124M (AVX512); 3.7 GHz AMD Ryzen 7 2700X (SHA Extensions); 1.2 GHz ARM Cortex-A53 (Pine64). The Celeron J3455 is only named as a SHA-Ext-capable CPU, not as a benchmark host. |
| **Adoption** | 1.0k stars; used in the MinIO object storage server for multipart-upload integrity checks |
| **Last commit** | 2023-02-22 |
| **Links** | [repository](https://github.com/minio/sha256-simd) · [benchmark](https://github.com/minio/sha256-simd/blob/master/README.md) |

## Verdict

The only comparison with Go crypto/sha256 is an ARM64 benchcmp on a 1.2 GHz Cortex-A53 (Pine64), using an unstated Go version that predates the stdlib's ARMv8 SHA2 code: 638.23 vs 6.05 MB/s at 1 MB (105x) and 8.38x at 8 bytes. The x86 figures (AVX-512 3498 MB/s on a 3.0 GHz Xeon Platinum 8124M, 7.8x, which is multi-buffer throughput across 16 lanes on one core; SHA-NI 1975 MB/s on a Ryzen 7 2700X, 3.84x) are measured against the package's own since-deleted AVX2 path, with no Go version or flags given.

## Use it when

- amd64 servers with AVX-512 (F/DQ/BW/VL) that hash many independent, similar-length, MB-scale messages concurrently, e.g. object-store multipart parts or dedupe chunks, and can route them through a shared Avx512Server. This is the one mode with no stdlib equivalent.
- Batch or Merkle-style hashing on AVX-512 hardware, but only after benchmarking Avx512Server against current crypto/sha256 yourself, since no such comparison has been published.
- Builds stuck on Go toolchains older than 1.21 running on SHA-NI CPUs (the README names AMD Ryzen and Intel Celeron J3455), where the stdlib's amd64 code lacks SHA-NI.

## Skip it when

- New()/Sum256 on Go 1.21+ amd64 or any recent Go on arm64. The stdlib uses the same instructions, and in issue #76 (Go 1.25.5, Apple M1 Max) it ties or wins at every size from 64 B up (1084 vs 793 MB/s at 64 B, 2414 vs 2352 MB/s at 1 MB). The maintainer's advice is 'just use stdlib unless you use NewAvx512Server'.
- CPUs without SHA-NI or ARMv8 SHA2. New() then just returns crypto/sha256, but Sum256 runs the package's pure-Go block function rather than the stdlib's assembly, because the SSSE3/AVX/AVX2 code was removed in 2021 (#57; #58 reported a one-third throughput drop on an i7-3770K).
- Small messages or single streams on the AVX-512 path. The README says messages under \~1 MB are better served by the regular hash because of scheduling overhead, and all 16 lanes need concurrent messages of similar length to pay off.
- Latency-sensitive services that make large single Write calls. The SHA-NI/ARM assembly processes the whole buffer without preemption, and PR #77 (closed unmerged, Aug 2026) measured a 29 ms GC stop-the-world pause for a 64 MiB Write, which crypto/sha256 avoids by feeding at most 64 KiB per call.
- FIPS/BoringCrypto builds: in #64, goboringcrypto did not recognize the package's hash and hmac.New panicked.

## How it is fast

The x86 path uses the Intel SHA Extensions (SHA256RNDS2-based rounds, contributed by Kristofer Peterson), and the ARM path uses the ARMv8 Cryptography Extensions instructions sha256h/sha256h2/sha256su0/sha256su1. The AVX-512 path is a port of intel-ipsec-mb's sha256_x16_avx512. It transposes 16 independent 64-byte message blocks across 16 ZMM registers and runs the rounds for all 16 messages at once (multi-buffer hashing), while a Go channel scheduler fills lanes and masks off lanes that run out of data. The older SSSE3/AVX/AVX2 paths (after Guilford et al.) were deleted in 2021 because the pure-Go code had become faster.

## Compared with alternatives

The catalogued siblings are Gueron's j-lanes and S-HASH (simultaneous multi-message) SHA-256 papers, benchmarked against OpenSSL and catalogued without a code repository. Pick this when you want that multi-buffer idea as working Go code that yields standard per-message SHA-256 digests; j-lanes' tree-hashing mode yields different digests.

## Integration

| | |
|---|---|
| **Form** | module (Go package github.com/minio/sha256-simd) |
| **Dependencies** | github.com/klauspost/cpuid/v2 (v2.2.3); golang.org/x/sys (indirect) |
| **Minimum toolchain** | go.mod declares Go 1.17; CI last tested Go 1.18-1.20; assembly only with the gc compiler (gccgo, appengine and the noasm tag fall back to pure Go) |
| **Platforms** | amd64 (SHA-NI; the AVX-512 server needs AVX512F/DQ/BW/VL), arm64 (ARMv8 SHA2, detected via cpuid or /proc/cpuinfo on Linux); other architectures build with the pure-Go fallback |
| **Thread safety** | A digest is not safe for concurrent use, as with any hash.Hash. One Avx512Server is meant to be shared, with each goroutine holding its own NewAvx512(server) digest (maintainer in #73); the server itself runs as a single goroutine. |
| **Drop-in for the baseline** | partial — New(), Sum256, Size, BlockSize and stdlib-compatible MarshalBinary/UnmarshalBinary mirror crypto/sha256, but there is no New224/Sum224, and the AVX-512 speedup needs the separate amd64-only NewAvx512Server/NewAvx512 API |

## Gotchas

- NewAvx512Server does not check the CPU. Without AVX-512 the process dies with SIGILL (#35). The package's AVX-512 feature flag is unexported, so the caller must detect AVX-512 itself and also use amd64 build tags, because the function is undefined on other architectures (#73).
- Each Avx512Server starts a goroutine that never exits (there is no Close) and, while idle, loops on a 1 µs time.After timer.
- Avx512Digest.Write passes slices, including the digest's own 64-byte carry buffer, to the server goroutine without copying and can return before they are hashed. The tests only use fresh, 64-byte-aligned buffers, so reusing a buffer or making unaligned writes before Sum looks unsafe from the source.
- Unlike crypto/sha256, an Avx512Digest is finalized by Sum: later Writes return an error until Reset, and a second Sum returns the cached result.

## Known shortcomings

- Go library. x86 7.8x / 3.84x ratios are against its own AVX2 code, not Go's stdlib; the only stdlib comparison is ARM64 against an old Go. Go's stdlib now has arm64 SHA2 and SHA-NI paths and matches or beats this package on M1 (issue #76).
- Go's stdlib caught up (SHA-NI since Go 1.21, ties or wins on M1 per #76); the maintainer says to use the stdlib unless you need NewAvx512Server; the AVX2 path was deleted in 2021 (#57). On CPUs without SHA extensions Sum256 runs pure-Go generic code, slower than stdlib asm. Non-preemptible asm causes \~29 ms GC stop-the-world on 64 MiB writes. AVX-512 server has no CPU check (SIGILL, #35), leaks a polling goroutine and does not copy caller slices. MinIO itself no longer depends on it.

## Caveats and trade-offs

The Go stdlib has since caught up. crypto/sha256 gained an optimized arm64 (SHA2-instruction) implementation in a 2017-11-14 commit and a SHA-NI amd64 implementation in a 2023-03-31 commit. Issue #76 (Dec 2025) shows Go 1.25.5 stdlib matching or slightly beating the package's ARM path on an Apple M1 Max. The remaining edge is the AVX512 16-lane multi-buffer path, which is ported from Intel intel-ipsec-mb, needs an explicit Avx512Server and many concurrent goroutines, and is slower for messages under 1MB. It was never benchmarked against modern stdlib SHA-NI. The x86 README numbers are against the package's own AVX2 path, not the stdlib. No commits since 2023-02-22 (about 3.6 years), so it is flagged abandoned.

AVX512 mode requires explicit multi-buffer scheduling (Avx512Server/channels) and only pays off with many concurrent \~5MB-sized SHA256 calls; no benefit for small or single messages; Go-only, not callable from C++.

## Maintenance

Flagged abandoned: no commits since 2023-02-22, a 2026 PR fixing GC pauses was closed unmerged, maintainers have told users since 2021 to prefer the stdlib except for the AVX-512 server, and MinIO's own current go.mod no longer lists it. It is Apache-2.0 and small, so vendoring just the AVX-512 server is feasible.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README benchcmp tables are first-party. The only direct comparison with Go crypto/sha256 is the ARM64 table (Pine64 Cortex-A53); the x86 AVX512 and SHA-Ext figures are against the package's own AVX2 path. The benchmark code is public (sha256_test.go BenchmarkHash, which now includes a GoStdlib comparator), but no Go version or flags are given, so it is C.
- **Verifier notes:** Metadata verified: Apache-2.0, not archived, not a fork, 1,040 stars, last commit 2023-02-22, so abandoned is correct. The headline x86 speedups are not against the baseline, so I rewrote the claim to lead with the real stdlib comparison (ARM64) and to flag that the stdlib has since overtaken it. The tier stays C.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/minio/sha256-simd>
  - <https://github.com/minio/sha256-simd/blob/master/README.md>
  - <https://github.com/minio/sha256-simd/pull/37#issuecomment-451607827>
  - <https://github.com/minio/sha256-simd/issues/76>
  - <https://github.com/minio/sha256-simd/blob/master/sha256_test.go>
  - <https://github.com/golang/go/commits/master/src/crypto/sha256/sha256block_arm64.s>
- **Sources the enricher read:**
  - <https://github.com/minio/sha256-simd>
  - <https://github.com/minio/sha256-simd/blob/master/README.md>
  - <https://github.com/minio/sha256-simd/tree/master>
  - <https://github.com/minio/sha256-simd/blob/master/go.mod>
  - <https://github.com/minio/sha256-simd/blob/master/sha256.go>
  - <https://github.com/minio/sha256-simd/blob/master/cpuid_other.go>
  - <https://github.com/minio/sha256-simd/blob/master/sha256block_amd64.go>
  - <https://github.com/minio/sha256-simd/blob/master/sha256block_amd64.s>
  - <https://github.com/minio/sha256-simd/blob/master/sha256block_arm64.go>
  - <https://github.com/minio/sha256-simd/blob/master/sha256block_other.go>
  - <https://github.com/minio/sha256-simd/blob/master/sha256blockAvx512_amd64.go>
  - <https://github.com/minio/sha256-simd/blob/master/sha256blockAvx512_amd64_test.go>
  - <https://github.com/minio/sha256-simd/blob/master/sha256block_amd64_test.go>
  - <https://github.com/minio/sha256-simd/blob/master/sha256_test.go>
  - <https://github.com/minio/sha256-simd/blob/master/.github/workflows/go.yml>
  - <https://github.com/minio/sha256-simd/commits/master>
  - <https://github.com/minio/sha256-simd/issues?q=is%3Aissue+OR+is%3Apr>
  - <https://github.com/minio/sha256-simd/issues/35>
  - <https://github.com/minio/sha256-simd/pull/49>
  - <https://github.com/minio/sha256-simd/pull/57>
  - <https://github.com/minio/sha256-simd/issues/58>
  - <https://github.com/minio/sha256-simd/issues/64>
  - <https://github.com/minio/sha256-simd/issues/65>
  - <https://github.com/minio/sha256-simd/issues/73>
  - <https://github.com/minio/sha256-simd/issues/76>
  - <https://github.com/minio/sha256-simd/pull/77>
  - <https://github.com/golang/go/commit/7b8a7f8272fd1941a199af1adb334bd9996e8909>
  - <https://github.com/golang/go/commits/master/src/crypto/sha256/sha256block_amd64.s>
  - <https://go.dev/doc/go1.21>
  - <https://raw.githubusercontent.com/minio/minio/master/go.mod>
  - <https://raw.githubusercontent.com/minio/minio-go/master/go.mod>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/minio/sha256-simd`) · [data/wave7/enrich/raw/github_com_minio_sha256_simd.json](../../../data/wave7/enrich/raw/github_com_minio_sha256_simd.json) (enrichment confidence 0.8)

</details>
