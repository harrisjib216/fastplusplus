# sha256mb

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Go multi-buffer SHA-256 for batches of 33-byte pubkeys; its 4-lane ARMv8 kernel runs \~2.6x faster than crypto/sha256.Sum256 on M3.

| | |
|---|---|
| **Beats** | Go standard library crypto/sha256 (sha256.Sum256 called once per message; this is the package's 'scalar' backend) |
| **Claimed result** | \~2.6x faster than scalar crypto/sha256 on Apple M3 (57.6M vs 21.6M hashes/s at n=6144; 2.57-2.67x across thermal states); README smoke table gives scalar = 21,550,000 hashes/s, 711.8 MB/s at the same batch size |
| **Workload** | Batched SHA-256 over n=6144 independent 33-byte compressed secp256k1 public keys (64-byte stride), GOMAXPROCS=1, arm64 hardware-SHA (sha2x4) backend vs scalar crypto/sha256 |
| **Metric** | throughput |
| **Hardware** | Apple M3 |
| **Compiler and flags** | Go 1.22.5, GOMAXPROCS=1, go test -bench -benchmem -count=8, median of runs |
| **Adoption** | 0 stars |
| **Last commit** | 2026-05-31 |
| **Links** | [repository](https://github.com/Asylian21/sha256mb) · [benchmark](https://github.com/Asylian21/sha256mb/blob/main/PERFORMANCE.md) |

## Verdict

The test hashed 6,144 random 33-byte messages at a 64-byte stride on an Apple M3 with Go 1.22.5 and GOMAXPROCS=1 (`BenchmarkHash33`, -count=8, median). The 4-lane `sha2x4` kernel reached 57.58M hashes/s (106.7 µs per call); the scalar backend, a plain loop over stdlib `crypto/sha256.Sum256` that already uses the ARMv8 SHA2 instructions, reached 21.55M (285.1 µs), about 2.6x (2.57-2.67x across thermal states). This is one author's local run; no other CPU, batch size or Go version has published ratios, and no comparison of HASH160 against btcutil is given.

## Use it when

- Bitcoin/secp256k1 tooling on arm64 that hashes large batches of compressed public keys: address indexing, HASH160 derivation, key-space research.
- arm64 hosts with the ARMv8 SHA-256 extension. Apple M-series is assumed to have it; Linux and BSD arm64 are gated on HWCAP. Only Apple M3 was actually benchmarked.
- Throughput-bound loops with batches in the hundreds to thousands; the published point is n=6144 on one core. Calls are zero-allocation and goroutine-safe, so you can shard batches across cores.
- Replacing a hot `for` loop of `sha256.Sum256` over fixed 33-byte slices at a stride of 33 bytes or more, when bit-identical output matters. It is tested against the stdlib oracle with fuzzing, race tests and poisoned inter-message padding.

## Skip it when

- amd64 or any non-arm64 target: no SIMD backend exists yet (AVX-512/SHA-NI are only planned), so it runs the stdlib scalar loop and gives no speedup.
- Any message length other than exactly 33 bytes, streaming input, or code that expects `hash.Hash`: none of these are supported.
- Tiny batches: n below 4 and the remainder after the last full group of 4 go through the scalar path, and no small-n numbers are published.
- Dependencies that must be mature and reviewed: 0 stars, one author, three commits all on 2026-05-31 and nothing since, and only v0.1.0. The single measurement is a local Apple M3 laptop run on Go 1.22.5; other CPUs and Go versions are not measured.

## How it is fast

The ARMv8 SHA256H/H2/SU0/SU1 instructions are latency-bound, so a single message leaves the crypto pipeline idle. The generated assembly runs four independent messages as register-disjoint streams in lockstep, emitting each round group for all four lanes back-to-back so the out-of-order core overlaps them (multi-buffer or interleaved hashing). Every message is exactly 33 bytes, so each fits one pre-padded block: the padding bit and the 264-bit length are constant schedule words, and there is no generic padding, buffering or finalize code. The project publishes no ablation that separates the interleaving gain from the per-call `Sum256` overhead it also removes.

## Compared with alternatives

In Go on arm64 with many fixed 33-byte pubkeys, pick it over minio/sha256-simd: sha256-simd speeds up general single-stream hashing but has no batched fixed-length API. hashtree, Intel ISA-L multi-buffer SHA and Gueron's j-lanes/S-HASH use the same many-messages idea from C, with the catalogued numbers measured on x86, so prefer them on amd64, where sha256mb has no SIMD path.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys (arm64 HWCAP detection outside Darwin). The hash160mb subpackage adds github.com/Asylian21/ripemd160-asm (same author, 0 stars). The module also requires golang.org/x/crypto. |
| **Minimum toolchain** | Go 1.22 (go.mod; toolchain go1.22.5; CI runs 1.22.x) |
| **Platforms** | The fast path needs arm64 with the ARMv8 SHA-256 extension (assumed on darwin/arm64, HWCAP-gated elsewhere). Every other GOARCH builds and runs the scalar crypto/sha256 loop. CI runs ubuntu amd64, ubuntu-24.04-arm and macos-14 arm64, and cross-compiles for 386 and ppc64le. |
| **Thread safety** | Hash33 and FromPubkeys33 are documented safe for concurrent use and are tested under -race. Hash33 keeps no state; FromPubkeys33 reuses a pooled per-goroutine scratch buffer after a one-time warm-up. |
| **Drop-in for the baseline** | partial — it replaces a loop of sha256.Sum256 over fixed 33-byte messages with one batched call and identical output, but it is not a hash.Hash and rejects every other length. |

## Gotchas

- Programmer errors panic instead of returning errors: n &lt; 0, stride &lt; 33, or a short src or dst.
- The backend is chosen once at package init, and GOSHA256MB_FORCE can pin it. Unknown or unsupported values silently fall back to scalar, so check Backend() and Lanes() before trusting a benchmark.
- On darwin/arm64 the SHA2 extension is assumed unconditionally, because x/sys/cpu reports no ARM64 flags there. Other arm64 platforms use HWCAP.
- In hash160mb, the staged default grows its pooled digest buffer to the largest n ever used and keeps it. The fused kernel (GOHASH160MB_FORCE=fused) ties staged single-threaded and is about 3% slower at 8 threads.

## Known shortcomings

- Go library; wins only on arm64 (amd64 runs scalar code). Baseline is a crypto/sha256 loop over independent messages; needs many messages in flight.
- Fixed 33-byte messages only (not a hash.Hash); fewer than 4 messages and the tail run scalar. One M3 laptop run (Go 1.22.5, n=6144 only), no small-n numbers. 0 stars, 3 commits (all 2026-05-31), v0.1.0 only.

## Caveats and trade-offs

This is a very new single-author project with 0 stars and no independent verification. The numbers come from the author's local smoke benchmark. The workload is narrow: fixed 33-byte messages. The win is arm64-only, because amd64 has no SIMD backend yet and runs scalar crypto/sha256, so there is no speedup on x86. The stdlib baseline itself already uses the ARMv8 SHA-2 instructions on Apple Silicon, so the gain comes from 4-way multi-buffer interleaving, not from hardware SHA versus software SHA.

Only the arm64 backend is vectorized (ARMv8 SHA256H/H2/SU0/SU1 4-lane interleave); amd64 has no SIMD backend yet and runs scalar. Requires a batched, fixed-33-byte-message workload (compressed pubkeys) to see the win; a single ad-hoc SHA-256 call gets no speedup.

## Maintenance

The catalog marks it active, but it was released as v0.1.0 on 2026-05-31 in three commits and nothing has landed since. MIT-licensed and small enough to vendor (a few Go files plus a generated arm64 assembly kernel), but unproven: 0 stars, single author, no amd64 kernel.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** PERFORMANCE.md and the README compare the sha2x4 backend with the scalar backend, which is literally a loop over Go stdlib crypto/sha256.Sum256 (scalar.go). The numbers are 57.58M vs 21.55M hashes/s at n=6144, about 2.6x, and 2.57-2.67x across thermal states. Benchmark code is public (bench_test.go BenchmarkHash33), and Go 1.22.5, GOMAXPROCS=1, -count=8 median and Apple M3 are all stated.
- **Verifier notes:** All numbers match the README and PERFORMANCE.md. The last commit was 2026-05-31, about 4 months ago, so I changed maintenance_status to active. The MIT license and 0 stars are confirmed by the GitHub API.
- **Fields the verifier corrected:** `maintenance_status`, `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Asylian21/sha256mb>
  - <https://github.com/Asylian21/sha256mb/blob/main/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/Asylian21/sha256mb/main/README.md>
  - <https://raw.githubusercontent.com/Asylian21/sha256mb/main/scalar.go>
  - <https://raw.githubusercontent.com/Asylian21/sha256mb/main/bench_test.go>
  - <https://raw.githubusercontent.com/Asylian21/sha256mb/main/go.mod>
- **Sources the enricher read:**
  - <https://github.com/Asylian21/sha256mb>
  - <https://github.com/Asylian21/sha256mb/blob/main/README.md>
  - <https://github.com/Asylian21/sha256mb/blob/main/PERFORMANCE.md>
  - <https://github.com/Asylian21/sha256mb/blob/main/SPEC.md>
  - <https://github.com/Asylian21/sha256mb/blob/main/CHANGELOG.md>
  - <https://github.com/Asylian21/sha256mb/blob/main/go.mod>
  - <https://github.com/Asylian21/sha256mb/blob/main/scalar.go>
  - <https://github.com/Asylian21/sha256mb/blob/main/sha256mb.go>
  - <https://github.com/Asylian21/sha256mb/blob/main/cpu.go>
  - <https://github.com/Asylian21/sha256mb/blob/main/feature_arm64_darwin.go>
  - <https://github.com/Asylian21/sha256mb/blob/main/feature_arm64_hwcap.go>
  - <https://github.com/Asylian21/sha256mb/blob/main/block_arm64.go>
  - <https://github.com/Asylian21/sha256mb/blob/main/block_arm64.s>
  - <https://github.com/Asylian21/sha256mb/blob/main/backend_generic.go>
  - <https://github.com/Asylian21/sha256mb/blob/main/bench_test.go>
  - <https://github.com/Asylian21/sha256mb/blob/main/internal/shagen/main.go>
  - <https://github.com/Asylian21/sha256mb/blob/main/hash160mb/hash160mb.go>
  - <https://github.com/Asylian21/sha256mb/blob/main/.github/workflows/ci.yml>
  - <https://github.com/Asylian21/sha256mb/tags>
  - <https://github.com/Asylian21/sha256mb/commits/main>
  - <https://github.com/Asylian21/sha256mb/actions>
  - <https://github.com/Asylian21/ripemd160-asm>
  - <https://raw.githubusercontent.com/golang/go/go1.22.5/src/crypto/sha256/sha256block_arm64.go>
  - <https://pkg.go.dev/github.com/Asylian21/sha256mb>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/asylian21/sha256mb`) · [data/wave7/enrich/raw/github_com_asylian21_sha256mb.json](../../../data/wave7/enrich/raw/github_com_asylian21_sha256mb.json) (enrichment confidence 0.6)

</details>
