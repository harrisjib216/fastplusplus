# cespare/xxhash (Go amd64/arm64 assembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go (amd64 and arm64 assembly)` · `MIT` · 🟡 stale

> Go XXH64 with scalar amd64/arm64 assembly; about 1.2-1.4x its own pure-Go build from 16 B up, slower at 4 B.

| | |
|---|---|
| **Beats** | the same package built with the purego tag (Go compiler output for the same XXH64 function) |
| **Claimed result** | README, asm vs purego: 4 B 1.2 vs 1.3 GB/s (asm slower), 16 B 3.5 vs 2.9, 100 B 8.1 vs 6.9, 4 KB 16.7 vs 11.7, 10 MB 17.3 vs 12.0 GB/s (about 1.4x at large inputs, derived). |
| **Workload** | XXH64 Sum64 over inputs from 4 bytes to 10 MB. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8252C, Ubuntu 20.04 |
| **Compiler and flags** | Go 1.19.2; benchstat over `go test -tags purego -benchtime 500ms -count 15 -bench 'Sum64$'` versus the default build |
| **Adoption** | 2.1k stars; widely imported Go module |
| **Last commit** | 2024-07-03 |
| **Links** | [repository](https://github.com/cespare/xxhash) · [benchmark](https://github.com/cespare/xxhash) |

## Verdict

Sum64 throughput from the README, measured with go test -benchtime 500ms -count 15 summarised by benchstat, Go 1.19.2, Ubuntu 20.04, Intel Xeon Platinum 8252C, assembly vs the same package with -tags purego: 1.2 vs 1.3 GB/s at 4 B, 3.5 vs 2.9 at 16 B, 8.1 vs 6.9 at 100 B, 16.7 vs 11.7 at 4 KB and 17.3 vs 12.0 GB/s at 10 MB. A 2024 third-party run with Go 1.22.3 on a Ryzen 7 6800HS (issue #44) shows a smaller 1.12-1.13x at 4 KB and 10 MB.

## Use it when

- Go services hashing byte slices or strings of 16 B and up on amd64 or arm64: cache keys, sharding and consistent hashing, Bloom filters, deduplication, content checksums (it is the hash behind Prometheus, InfluxDB, VictoriaMetrics, Badger, Ristretto and FreeCache per the README).
- You need XXH64 values that match other languages' xxHash (C Cyan4973/xxhash, zstd frame checksums), not a process-local hash.
- Bulk throughput on KB-to-MB buffers, where the README shows 16.7-17.3 GB/s against 11.7-12.0 GB/s for the pure-Go build on a Xeon Platinum 8252C.
- Streaming input or resumable hashing: Digest accepts incremental Writes and serialises its state with MarshalBinary.

## Skip it when

- Tiny keys of about 4 B: the assembly is slower (README 1.2 vs 1.3 GB/s; a 2024 third-party run in issue #44 measured 2.95 vs 2.70 ns per Sum64 call).
- You want XXH3, XXH128 or XXH32: only XXH64 exists here (XXH3 requests #52, #60 and #73 and the XXH32 request #83 are closed without adding them).
- Adversarial keys (hash flooding) or security uses: XXH64 is non-cryptographic and Sum64 always uses seed 0; use a seeded hash (hash/maphash, or a NewWithSeed Digest) or a cryptographic hash.
- Process-local hash tables where any good hash will do: Go's hash/maphash is the natural stdlib alternative, and the README's claim of being much faster than anything in the standard library comes with no numbers.
- Other architectures (386, arm, riscv64, wasm, etc.) or -tags purego builds: you get the pure-Go code, which is the baseline itself.

## How it is fast

No SIMD: XXH64's four independent 64-bit lanes are already instruction-level parallel, and the assembly simply keeps the four accumulators, the input pointer and the prime constants in registers across the 32-byte block loop with no bounds checks (amd64: IMULQ/ROLQ; arm64: LDP paired loads, fused MADD multiply-add, ROR). The gain over Go compiler output comes from register allocation and instruction selection, so it shrinks as the compiler improves; a non-inlinable assembly call costs more than it saves on 4-byte inputs.

## Compared with alternatives

Among the catalogued Go-assembly siblings, lukechampine/blake3, zeebo/blake3 and minio/md5-simd are cryptographic hashes with SIMD and larger gains over their pure-Go fallbacks; pick cespare/xxhash when you need a fast non-cryptographic 64-bit hash that matches the XXH64 spec (C reference: Cyan4973/xxhash), and a BLAKE3 sibling when collision resistance against an attacker matters.

## Integration

| | |
|---|---|
| **Form** | module (Go module github.com/cespare/xxhash/v2; small enough to vendor as source) |
| **Dependencies** | none |
| **Minimum toolchain** | go.mod says go 1.11 (README: Go 1.9.7+/1.10.3+ with minimal module compatibility, or Go 1.11+); CI tests Go 1.21.x and 1.22.x |
| **Platforms** | amd64 and arm64 assembly using baseline instructions only (no CPU feature detection or AVX); pure Go elsewhere, with CI on Linux, macOS and Windows plus 386/arm/arm64 under QEMU |
| **Thread safety** | not documented; Sum64 and Sum64String are pure functions of their input, while a Digest holds mutable state and needs one instance per goroutine or external locking |
| **Drop-in for the baseline** | yes |

## Gotchas

- The asm advantage has narrowed with newer Go releases and differs by CPU: maintainer issue #44 (open, v3 milestone) proposes deleting the amd64 assembly if it stops winning. Third-party numbers there: Ryzen 7 6800HS with Go 1.22.3 (single runs, not benchstat), pure Go vs asm, 10 MB 15.78 vs 17.65 GB/s (1.12x), 4 KB 15.41 vs 17.42 (1.13x), 100 B 7.18 vs 9.14 (1.27x), 16 B 2.76 vs 4.42 (1.60x), 4 B 1.48 vs 1.36 (asm slower); with Go 1.19 (CPU unstated) +46% at 4 KB and +38% at 10 MB. The README's 1.4x is from Go 1.19.2 on one Xeon (derived from page data).
- Benchmark shape: each sub-benchmark hashes one fixed-size, fixed-content buffer in a tight loop (bench_test.go), so branch prediction, cache residency and the tail loops are ideal; mixed-length key streams are not measured. Discarding the result with `_ =` is harmless here because the assembly call cannot be eliminated and the pure-Go Sum64 is too large to inline.
- A zero-valued Digest is not ready for writes: call New or Reset first (open issue #65; PRs #89 and #92 to auto-initialise are unmerged). Sum64 has no seed argument; seeds exist only on Digest, and the seed API is under reconsideration for v3 (#78).
- Slices built with unsafe whose capacity is smaller than their length panic in the pure-Go path's three-index slicing (issue #76: 'slice bounds out of range [::40] with capacity 0', traced to a data race and unsafe conversion in the caller), while the assembly path does not check.

## Known shortcomings

- Gain only 1.2-1.4x over its own purego build; the asm is slower at 4 B; amd64 numbers only; Go 1.19.2 table from 2022.
- Enricher: fixed-size fixed-content inputs only; the gain is narrower on newer Go (issue #44 third-party run on a Ryzen 7 6800HS with Go 1.22.3: 1.12x at 10 MB, 1.13x at 4 KB, asm slower at 4 B) and the maintainer's open #44 proposes dropping the amd64 assembly; the AVX-512 PR #79 is unmerged. Lead: zeebo/xxh3 (Go XXH3 with assembly).

## Caveats and trade-offs

Baseline is the package's own pure-Go code (purego build tag), not C xxHash or any Go standard-library hash. The assembly is slower for 4-byte inputs (1.2 vs 1.3 GB/s) and the gain is about 1.2x at 16-100 B and 1.4x at 4 KB and above (derived from page data). Only amd64 numbers are published (Xeon Platinum 8252C); the arm64 assembly has no numbers. The README claim 'much faster than anything in the Go standard library' has no figures. Table last refreshed in the 2022-12-04 commit 'Update README for arm64 asm; latest benchmarks' with Go 1.19.2; newer Go compilers may narrow the gap. The benchmark discards Sum64's result, which is safe here because the assembly call cannot be eliminated and the pure-Go Sum64 is too large to inline. [retier] Fixed-size fixed-content inputs; gain shrinks to about 1.1x on Go 1.22 per issue #44; maintainer considering removal of the amd64 asm; AVX-512 PR #79 unmerged

Assembly only on amd64 and arm64 (purego fallback elsewhere); XXH64 only, no XXH3.

## Maintenance

Quiet since the 2024-07-03 commit (last tag v2.3.0, 2024-04-04) with seven open PRs, including an unmerged AVX-512 path (#79) that the maintainer will not take at the cost of small-input or non-AVX-512 speed; MIT-licensed, dependency-free, small and widely used, so it is safe to depend on or vendor as is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README Benchmarks table compares the amd64 assembly Sum64 against the same package built with -tags purego, with the exact benchstat/go test commands, Go 1.19.2, Ubuntu 20.04 and an Intel Xeon Platinum 8252C; the benchmark code is public in bench_test.go (BenchmarkSum64 over 4B/16B/100B/4KB/10MB with b.SetBytes). Go has no optimization flags beyond the build tag, so code, toolchain, switches and CPU model are all stated.
- **Verifier notes:** Numbers in claimed_speedup match the README table exactly. Metadata checked on github.com: MIT (LICENSE.txt, Copyright 2016 Caleb Spare), 2.1k stars, 144 forks, not archived or a fork, last commit 2024-07-03 (stale). Main shortcoming: modest 1.2-1.4x gain over its own pure-Go fallback, slower at 4 B, amd64 only.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-36 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/cespare/xxhash>
  - <https://github.com/cespare/xxhash/commits>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/README.md>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/bench_test.go>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/xxhash_test.go>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/xxhash_other.go>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/LICENSE.txt>
- **Sources the enricher read:**
  - <https://github.com/cespare/xxhash>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/README.md>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/bench_test.go>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/xxhash.go>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/xxhash_amd64.s>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/xxhash_arm64.s>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/xxhash_asm.go>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/xxhash_other.go>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/xxhash_safe.go>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/xxhash_unsafe.go>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/xxhash_test.go>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/go.mod>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/cespare/xxhash/HEAD/.github/workflows/test.yml>
  - <https://github.com/cespare/xxhash/commits>
  - <https://github.com/cespare/xxhash/tags>
  - <https://github.com/cespare/xxhash/issues?q=is%3Aissue>
  - <https://github.com/cespare/xxhash/issues/44>
  - <https://github.com/cespare/xxhash/issues/76>
  - <https://github.com/cespare/xxhash/pulls>
  - <https://github.com/cespare/xxhash/pull/79>
  - <https://github.com/cespare/xxhash/pull/85>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/cespare/xxhash`) · [data/wave13/enrich/raw/github_com_cespare_xxhash.json](../../../data/wave13/enrich/raw/github_com_cespare_xxhash.json) (enrichment confidence 0.85)

</details>
