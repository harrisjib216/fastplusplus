# minio/md5-simd (AVX2/AVX-512 multi-lane MD5 in Go assembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (assembly)` · `Apache-2.0 (LICENSE); files derived from Go's crypto/md5 are under BSD-3-Clause (LICENSE.Golang, Copyright 2009 The Go Authors)` · 🟡 stale

> Go package computing 8 (AVX2) or 16 (AVX-512) independent MD5 streams per core; 3-8x crypto/md5 aggregate throughput.

| | |
|---|---|
| **Beats** | Go standard library crypto/md5 |
| **Claimed result** | README benchcmp vs crypto/md5, aggregated multi-stream hashing on 4 vCPUs (c5.xlarge, Xeon Platinum 8124M 3.0 GHz). AVX2: 32KB 2229.22 to 7370.50 MB/s (3.31x), 1MB 2233.56 to 9042.62 MB/s (4.05x), peak 4.09x at 4MB ('up to 4x faster'). AVX512: 32KB 2229.22 to 11605.78 MB/s (5.21x), 128KB 7.23x, 1MB 2233.56 to 16941.95 MB/s (7.59x), 8MB 2182.48 to 17252.88 MB/s (7.91x) ('up to 8x faster'). Single-thread block functions: BenchmarkBlock16 8228.88 MB/s and BenchmarkBlock8 4144.80 MB/s vs BenchmarkCryptoMd5 687.66 MB/s. |
| **Workload** | BenchmarkParallel: aggregate MD5 throughput when many independent streams are hashed at once, per-write block size 32 KB to 8 MB, on a c5.xlarge |
| **Metric** | throughput |
| **Hardware** | AWS EC2 c5.xlarge, Intel Xeon Platinum 8124M @ 3.0 GHz (AVX-512 capable) |
| **Compiler and flags** | Go version and flags not stated; commands that produced the benchcmp inputs are not given |
| **Adoption** | 216 stars |
| **Last commit** | 2025-04-02 |
| **Links** | [repository](https://github.com/minio/md5-simd) · [benchmark](https://github.com/minio/md5-simd) |

## Verdict

First-party README benchcmp of BenchmarkParallel with GOMAXPROCS 4 on an AWS c5.xlarge (Xeon Platinum 8124M, 3.0 GHz), Go version unstated: crypto/md5 (then amd64 scalar assembly, one stream per goroutine) about 2.2 GB/s aggregate versus AVX2 7.4-9.0 GB/s (3.3-4.1x) and AVX-512 11.6-17.3 GB/s (5.2-7.9x) with 16 hashes per server per goroutine, block sizes 32 KB to 8 MB. Those numbers were taken on 2020-04-28 code that did not yet copy caller data (the zero-copy write was a data race fixed a week later at a measured throughput cost), so current-code speedups are not documented.

## Use it when

- A Go server on x86-64 that hashes 16 or more large streams at once (object storage uploads, ETag computation, bulk checksumming) and is CPU-bound on MD5.
- Objects of tens of KB and up, written in multiples of 64 bytes and ideally 32 KB (wrap writers in bufio.NewWriterSize(h, 32&lt;&lt;10) otherwise).
- CPUs with AVX-512F and AVX-512DQ (16 lanes per core); AVX2-only CPUs still get 8 lanes per core using up to two goroutines per server round.
- When MD5 output must stay bit-identical to crypto/md5 (it computes standard MD5, not a tree hash).

## Skip it when

- Single-stream or low-concurrency hashing: the README says one hash on a server runs at about half the throughput, and with 1-2 active streams it falls back to scalar code plus channel and copy overhead.
- Small objects of a few KB: the README itself recommends crypto/md5 there.
- Non-amd64 targets (arm64, riscv64, s390x) or builds with the noasm, appengine or non-gc tags: it silently becomes a crypto/md5 wrapper.
- Long-lived servers that create and close hashers continuously, unless you accept the open lifecycle issues: closed clients leave entries in the server's digest map and issue #35 (throughput collapsing as hashers are created, open since 2023) has no upstream fix.
- When you can change the algorithm: BLAKE3 or other modern hashes with SIMD give single-stream speed too.

## How it is fast

Multi-buffer (multi-lane) SIMD: each 32-bit vector lane carries a separate MD5 state, so the serial dependency chain of one MD5 is replaced by 8 or 16 independent chains per instruction. Message words are loaded across lanes with VPGATHERDD using 32-bit offsets from one shared server buffer (masked per lane); the AVX-512 kernel also keeps intermediate words in the upper 16 ZMM registers, uses VPROLD for rotates and VPTERNLOGD to fuse the round functions. With 1-2 active streams it switches to an avo-generated scalar kernel.

## Compared with alternatives

Pick it over gocrack's md5x8 kernel (password-candidate cracking) when you need a general hash.Hash API for many independent Go streams with arbitrary lengths, and over animetosho/md5-optimisation (a faster single-stream scalar MD5 in C/asm) when your load is many concurrent streams rather than one; if the hash is not fixed to MD5, lukechampine/blake3 or zeebo/blake3 are faster per stream.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/klauspost/cpuid/v2 (runtime CPU feature detection) |
| **Minimum toolchain** | go.mod declares go 1.14; gc compiler only (Go assembly, build tags !noasm,!appengine,gc) |
| **Platforms** | amd64 with AVX2 (8 lanes) or AVX-512F+AVX-512DQ (16 lanes); everything else falls back to crypto/md5 |
| **Thread safety** | Server is meant to be shared by many goroutines (NewHash uses atomics and channels); each Hasher is a hash.Hash for one goroutine, and Hashers and the Server must be Closed |
| **Drop-in for the baseline** | partial: Hashers satisfy hash.Hash, but they must come from a Server and be Closed, and the speedup appears only when many hashers write concurrently |

## Gotchas

- The README benchmark tables were committed on 2020-04-28 (commit 4ef09e8, 'Numbers from final performance measurements'), before issue #12 ('Write operations keeps a reference to data after they return', a data race) was fixed by PR #14 on 2020-05-07. The fix made Write copy caller data into server buffers; PR #14's own runs showed BenchmarkAvx2Parallel dropping to 0.51-0.67x with the first version of the fix (32-core box), later commits clawed back 'most of the lost performance for single server', and the c5.xlarge tables were never re-measured. The AVX-512 loader was also rewritten on 2020-05-08 (32-bit offsets instead of the 64-bit VPGATHERQD pointers the README still describes).
- Hasher lifecycle: in the server loop, a closed client's channel removes it from the client list but never deletes its s.digests entry (only a Reset does), so a long-lived server grows one map entry per closed hasher; un-closed hashers stay registered and each round's fill loop iterates over all registered clients. A maintained fork (soulteary/otterio-kits commit fff98c7, 2026-10-09) patches digest-state release, buffer starvation when writers hold all 48 shared buffers without waking the scheduler, and Close blocking after server exit; upstream has none of this.
- Issue #38 suspects BenchmarkAvx2Parallel's b.SetParallelism((GOMAXPROCS+1)/2) inflates AVX2 results; in Go's testing package each sub-benchmark's runN resets parallelism to 1 and b.Run does not copy it, so that call has no effect on the b.Run sub-benchmarks and AVX2 and AVX-512 both run GOMAXPROCS servers.
- The README's single-thread figures (BenchmarkBlock16 8228.88 MB/s, Block8 4144.80 MB/s vs CryptoMd5 687.66 MB/s) time the bare block function on the same 64 bytes in L1, with no copy, padding or finalization, against a full crypto/md5 Write+Sum; they are an upper bound, not an end-to-end ratio.

## Known shortcomings

- Numbers match (README also has an AVX2 table up to 4.09x); Go version unstated; the baseline crypto/md5 was already scalar amd64 asm (Bevand md5block_amd64.s), so the gain is multi-buffer only; README bench names differ from the current tests. Licence Apache-2.0 plus BSD-3-Clause (LICENSE.Golang). Stale (last commit 2025-04-02).
- The README tables come from commit 4ef09e8 (2020-04-28), before data race #12 ('Write keeps a reference to data after return') was fixed by PR #14 on 2020-05-07, which made Write copy caller data; PR #14's own runs showed the first version of the fix cutting Avx2Parallel to 0.51-0.67x on a 32-core box and later commits recovering 'most' of it for a single server; the c5.xlarge tables were never re-measured. Closed hashers are never deleted from s.digests (the map grows; issue #35 slowdown open). Issue #38's SetParallelism suspicion is wrong (Go's runN resets parallelism to 1 in sub-benchmarks). The Block16/Block8 figures time the bare block function on 64 hot bytes against a full crypto/md5 Write+Sum.

## Caveats and trade-offs

This is multi-buffer throughput: 8 (AVX2) or 16 (AVX512) independent hashes per core. The README says it does not speed up a single MD5 sum, and that one hash on a server runs at about half the throughput, so it helps only servers hashing many large streams at once. When these numbers were taken, the crypto/md5 baseline on amd64 was hand-written scalar assembly (Marc Bevand's md5block_amd64.s, present in Go's release-branch.go1.21 tree), not compiler output. Current Go master has md5 assembly only for riscv64 and s390x. The README's benchmark names (BenchmarkParallel/32KB-4, built with benchcmp from crypto-md5.txt and avx512.txt) do not match the current test functions (BenchmarkCryptoMd5Parallel, BenchmarkAvx2Parallel, BenchmarkAvx512Parallel), so the exact harness revision is not identified. The Go version is unstated. The block benchmark times the raw 64-byte block function on 16 lanes, without padding or finalization, against a full crypto/md5 Write+Sum. Commit #32 (2022) added an option to disable AVX512 on CPUs that throttle. The AVX2 kernel is taken essentially unchanged from igneous-systems/md5vec. [retier] Multi-buffer throughput: 8 (AVX2) or 16 (AVX512) independent hashes per core; the README says it does not speed up a single MD5 sum and that one hash on a server runs at about half the throughput. The README tables were committed on 2020-04-28 (4ef09e8), before issue #12 ('Write operations keeps a reference to data after they return', a data race) was fixed by PR #14 on 2020-05-07, which made Write copy caller data into server buffers; PR #14's own runs showed BenchmarkAvx2Parallel dropping to 0.51-0.67x with the first version of the fix (32-core box) and later commits clawing back 'most of the lost performance for single server'; the c5.xlarge tables were never re-measured. When the numbers were taken, the crypto/md5 baseline on amd64 was Marc Bevand's hand-written md5block_amd64.s; current Go master has md5 assembly only for riscv64 and s390x. Go version, flags and the benchcmp commands are not stated, and the README benchmark names do not match the current test functions. The single-thread Block16/Block8 figures time the bare block function on the same 64 bytes in L1 against a full crypto/md5 Write+Sum (an upper bound). Closed hashers are never deleted from s.digests (one map entry per closed hasher; issue #35 slowdown open; a maintained fork, soulteary/otterio-kits, patches this). Issue #38's suspicion that b.SetParallelism inflates AVX2 is wrong (Go's runN resets parallelism to 1 in sub-benchmarks).

Does not speed up a single hash; it computes 8 (AVX2) or 16 (AVX-512) independent MD5 sums on one core, so it only helps servers that hash many streams concurrently (for example S3 ETag computation). The amd64 assembly uses VPGATHER and AVX-512 instructions; other architectures fall back to stdlib.

## Maintenance

Stale (last upstream commit 2025-04-02, open lifecycle issues #35 and #38) but Apache-2.0 plus BSD-3-Clause for Go-derived files, small, and still a direct dependency of minio-go (v1.1.2); vendor it with the fork's lifecycle fixes in mind and re-benchmark on your own CPU.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives benchcmp tables comparing crypto/md5 with the AVX2 and AVX512 versions, plus block-function numbers, on a named CPU (c5.xlarge, Xeon Platinum 8124M at 3.0 GHz), and the benchmark code is public (md5_test.go, md5_amd64_test.go, block16_amd64_test.go). The Go version is not stated and the README's benchmark names (BenchmarkParallel/\*-4) do not match the current test functions, so the result is first-party with partial methodology: tier C.
- **Verifier notes:** Numbers match the README, and an AVX2 table (up to 4.09x) is also given; the record wrongly said only the AVX512 table has numbers. Shortcomings to record: Go version unstated; the baseline crypto/md5 was scalar assembly at the time, not compiler output; the gain is multi-buffer only (no single-hash speedup); the README harness names differ from the current tests; the repo is stale (last commit 2025-04-02, 216 stars). The license is Apache-2.0 plus BSD-3-Clause for the Go-derived files; both are OSI-approved, so it stays copyable.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-38 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/minio/md5-simd>
  - <https://github.com/minio/md5-simd/commits>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5_test.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5_amd64_test.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/block16_amd64_test.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5-util_amd64_test.go>
  - <https://github.com/minio/md5-simd/blob/master/LICENSE.Golang>
  - <https://github.com/golang/go/tree/master/src/crypto/md5>
  - <https://raw.githubusercontent.com/golang/go/master/src/crypto/md5/md5block_decl.go>
  - <https://raw.githubusercontent.com/golang/go/release-branch.go1.21/src/crypto/md5/md5block_amd64.s>
- **Sources the enricher read:**
  - <https://github.com/minio/md5-simd>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/go.mod>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5-server_amd64.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5-server_fallback.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5-digest_amd64.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/block_amd64.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5-util_amd64.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5_test.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5_amd64_test.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/block16_amd64_test.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5-util_amd64_test.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/block16_amd64.s>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/block8_amd64.s>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5block_amd64.go>
  - <https://raw.githubusercontent.com/minio/md5-simd/HEAD/md5block_amd64.s>
  - <https://github.com/minio/md5-simd/issues?q=is%3Aissue>
  - <https://github.com/minio/md5-simd/issues/38>
  - <https://github.com/minio/md5-simd/issues/35>
  - <https://github.com/minio/md5-simd/issues/33>
  - <https://github.com/minio/md5-simd/issues/12>
  - <https://github.com/minio/md5-simd/pull/14>
  - <https://github.com/minio/md5-simd/commits/master>
  - <https://github.com/minio/md5-simd/commits/master/README.md>
  - <https://github.com/minio/md5-simd/commit/4ef09e8>
  - <https://github.com/soulteary/otterio-kits/commits>
  - <https://github.com/soulteary/otterio-kits/commit/fff98c71b180dd41a2e5fd994927349cbf217d53>
  - <https://raw.githubusercontent.com/golang/go/master/src/testing/benchmark.go>
  - <https://raw.githubusercontent.com/golang/go/release-branch.go1.14/src/testing/benchmark.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/crypto/md5/md5block_decl.go>
  - <https://raw.githubusercontent.com/minio/minio/HEAD/go.mod>
  - <https://raw.githubusercontent.com/minio/minio-go/HEAD/go.mod>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/minio/md5-simd`) · [data/wave13/enrich/raw/github_com_minio_md5_simd.json](../../../data/wave13/enrich/raw/github_com_minio_md5_simd.json) (enrichment confidence 0.8)

</details>
