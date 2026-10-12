# zeebo/blake3 (Go BLAKE3 with avo-generated AVX-512, AVX2, SSE4.1, NEON assembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Go BLAKE3 with avo-generated AVX-512, AVX2, SSE4.1, NEON and SVE2 kernels; 6-8x its own pure-Go path on large inputs.

| | |
|---|---|
| **Beats** | The same library built without its assembly (pure Go, compiled by the Go toolchain), plus the upstream Rust blake3 crate (single-threaded) shown in charts |
| **Claimed result** | Contributor benchstat tables (PRs #41, #42, #51, #53, #54; Go 1.26.5, assembly vs BLAKE3_PUREGO=1), 1 MiB input: AVX-512 7.70x and AVX2 6.13x (Xeon 6975P); SVE2 3.65x (Graviton5); NEON 2.12x (Graviton3). README tables (i7-6700K, Feb 2020 code): 64 B 205 ns vs 254 ns (1.24x), 1 KiB 1.01 us vs 1.77 us (1.75x), 512 KiB 131 us vs 883 us (6.7x; the No-ASM row labelled '1024 kib' is a 512 KiB measurement: 524288 B / 883 us = 594 MB/s, derived from page data). |
| **Workload** | BLAKE3 hashing of 64 B to 1024 KiB inputs, full-buffer, incremental and reset modes; x86 on an i7-6700K (AVX2) and arm64 on an Apple M4 (NEON). |
| **Metric** | throughput |
| **Hardware** | PR benchstat tables: AWS Xeon 6975P (AVX-512, AVX2), Graviton5 (SVE2), Graviton3 (NEON). README tables: Intel i7-6700K (x86, 2020) and Apple M4 (NEON, 2026-07-23). |
| **Compiler and flags** | PR tables: Go 1.26.5, go test -bench BenchmarkBLAKE3 -count 6 or 20, baseline with BLAKE3_PUREGO=1 (no assembly). README tables: Go toolchain version not stated. |
| **Adoption** | 498 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/zeebo/blake3) · [benchmark](https://github.com/zeebo/blake3#timing-tables) |

## Verdict

The README compares the assembly build against the same package without assembly on an i7-6700K (Feb 2020, Go version unstated): 4.00 GB/s vs about 595 MB/s for large inputs (about 6.7x, derived) and 205 ns vs 254 ns at 64 B; an Apple M4 NEON table (Jul 2026) shows 2.29 vs 1.05 GB/s at 1 MiB. Newer contributor benchstat runs (BenchmarkBLAKE3 'Entire', Go 1.26.5, n=6, idle AWS instances) give same-run asm vs BLAKE3_PUREGO ratios at 1 MiB of 7.70x for AVX-512 and 6.13x for AVX2 on a Xeon 6975P (4.718 and 3.754 GiB/s vs 627.4 MiB/s), 7.14x for AVX2 on an EPYC 7R13, 3.65x for SVE2 on Graviton5 and 2.12x for NEON on Graviton3 (all derived from PR #41/#42 tables); later PRs lifted AVX-512 to 4.88 GiB/s (Xeon 6975P-C) and 5.50 GiB/s (EPYC 9R45) at 1 MiB without re-measuring pure Go.

## Use it when

- Go services hashing medium to large buffers (4 KiB and up) on x86-64 with AVX2 or AVX-512; contributor benchmarks show 3.5-5.5 GiB/s single-threaded at 64 KiB-1 MiB on current AWS parts
- Content addressing, deduplication or file integrity in Go where you want BLAKE3 output compatibility with the Rust and C implementations without cgo
- Streaming input in small writes: the internal 8 KiB buffer keeps SIMD throughput even when Write is called with tiny slices, unlike the Rust crate which needs large update buffers
- Graviton4/5, Axion or Cobalt 100 arm64 servers, where the SVE2 kernel gave about 3.65x over pure Go at 1 MiB (PR #42, Graviton5)
- As a reference for avo-generated BLAKE3 SIMD kernels when porting the lane layouts to C++ intrinsics (CC0 or MIT licence)

## Skip it when

- C or C++ projects: use the official BLAKE3 C implementation (multi-threadable, hand-written asm) instead of going through cgo
- Hashing many tiny messages: below about 1 KiB the gain over pure Go is only 1.2-1.5x on x86 and zero on arm64, and the README says small inputs are 3-4x slower in rate (about 100 ns absolute) than the Rust crate because of hasher initialisation; use Reset to reuse state
- Very large single files where multithreading matters: it is single-threaded by design (issues #7 and #24 closed), so it cannot match Rust blake3 with rayon on many cores
- arm64 inputs of 2 KiB or less with NEON, or 1 KiB or less with SVE2: there is no arm64 single-block compression kernel, so those sizes run pure Go
- Non-amd64/arm64 targets (386, riscv64, ppc64, s390x, wasm): only the pure Go path exists

## How it is fast

The hasher buffers input into an 8 KiB (eight-chunk) block and hashes whole chunks in parallel SIMD lanes: the AVX2 kernel transposes eight chunks across ymm lanes (a 2-chunk by 4-lane ymm layout for two-chunk inputs since PR #53), the AVX-512 kernel uses a 4-chunk by 4-lane zmm layout and replaces shift-shift-or rotates with a single vprord, NEON does four chunks per pass, and the SVE2 kernel fuses xor and rotate with XAR (emitted as raw WORD encodings because Go's arm64 assembler has no SVE mnemonics). Parent nodes of the Merkle tree are combined in batches of up to eight by a vectorised HashP, single-block compression uses SSE4.1 or AVX-512 on x86, and inputs larger than 8 KiB are hashed in place without copying when the buffer is empty. All assembly is generated by Go programs written with avo (the _asm directory), and CI fails if the checked-in .s files differ from the generators' output.

## Compared with alternatives

Over lukechampine/blake3 when you need arm64 acceleration (NEON/SVE2), a 1-2 chunk fast path, or a streaming Hasher that stays fast on small writes; lukechampine's package also has AVX-512 and AVX2 and is simpler to audit, so compare on your own sizes. Pick cespare/xxhash instead when you only need a fast non-cryptographic checksum.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys (CPU feature detection); zeebo/assert and zeebo/pcg for tests |
| **Minimum toolchain** | Go 1.20 (go.mod directive; CI tests 1.20.x and stable) |
| **Platforms** | amd64 (SSE4.1, AVX2, AVX-512F+VL kernels, chosen at init), arm64 (NEON always, SVE2 when detected); every other GOARCH, and the purego build tag, use pure Go; big-endian tested on s390x |
| **Thread safety** | not documented; a Hasher carries mutable buffer state and follows the hash.Hash convention of one goroutine per instance (Clone gives an independent copy); Sum256/Sum512 allocate their own state per call |
| **Drop-in for the baseline** | partial — the baseline is the same package's pure-Go path, selected with -tags purego or BLAKE3_PUREGO=1; the API is identical, only speed changes |

## Gotchas

- README timing tables are stale and partly mislabelled: the x86 tables date from Feb 2020 code on an i7-6700K, and the No-ASM '1024 kib' row's times and rates agree only for a 512 KiB input (524288 B / 883 us = 594 MB/s, derived from page data), so that row is a 512 KiB measurement; the like-for-like large-input gain is about 6.7x (131 us vs 883 us at 512 KiB), not 3.4x. No AVX-512 or SVE2 numbers appear in the README at all; the current evidence is in PRs #41, #42, #48, #51, #53 and #54.
- Backends are chosen once at package init from x/sys/cpu and the environment: BLAKE3_PUREGO, BLAKE3_DISABLE_AVX512, BLAKE3_DISABLE_AVX2, BLAKE3_DISABLE_SSE41, BLAKE3_DISABLE_SVE2 and BLAKE3_DISABLE_NEON force slower paths, which is useful for A/B tests but a surprise if set in production.
- CI's dispatch job emulates Haswell, Penryn, qemu64, Neoverse N2 and Neoverse V1 under qemu-user but no AVX-512 CPU, so the AVX-512 kernels (the generated hash kernel alone is 2,282 lines, rewritten in Aug 2026) are exercised in CI only when a GitHub runner happens to have AVX-512; the contributor reports local test passes on Xeon 6975P-C and EPYC 9R45.
- The SVE2 kernel works on the low 128 bits (NEON V registers with XAR applied to the matching Z registers), so wider SVE2 implementations gain nothing extra from vector length; the benchmark hashes a hot, all-zero buffer that is reused each iteration, so figures are warm-cache throughput (harmless for the constant-time ARX core, optimistic for cold data).

## Known shortcomings

- First-party with the Go version unstated; the x86 tables come from 2020-02-12 code and the NEON table predates the August 2026 rewrites; no AVX-512 or SVE2 numbers; the 1024 KiB no-assembly row is inconsistent (3.4x by timings, 6.7x by rates). Go-only.
- The README No-ASM '1024 kib' row is a 512 KiB measurement (524288 B / 883 us = 594 MB/s), so the like-for-like large-input gain is about 6.7x, not 3.4x. Contributor PRs #41, #42, #51, #53 and #54 publish benchstat tables (Go 1.26.5, n=6/20, named AWS CPUs, BLAKE3_PUREGO baseline): 1 MiB AVX-512 7.70x and AVX2 6.13x on Xeon 6975P, SVE2 3.65x on Graviton5, NEON 2.12x on Graviton3. CI never exercises AVX-512 dispatch (qemu jobs cover Haswell, Penryn, qemu64 and Neoverse only), arm64 inputs up to 2 KiB run pure Go, and the benchmarks are single-threaded on a hot-cache all-zero buffer.

## Caveats and trade-offs

First-party numbers with an unstated Go version; the author states no attempt at precise measurement. The x86 tables (Small, Large, No ASM) date from 2020-02-12 (git blame) and the code has since been rewritten (AVX-512 backends and a two-chunk ymm layout for the AVX2 path in Aug 2026), and the NEON table (2026-07-23) predates the 2026-08-19 NEON critical-path change, so all published numbers are stale relative to current code (performance work, not correctness fixes). The 1024 KiB no-ASM row is internally inconsistent (883us at 595MB/s implies about 0.5 MiB). The Rust comparison appears only as SVG charts whose numbers were not read; Rust was limited to AVX2 and one thread. The baseline is the same Go code without assembly, not a C or C++ implementation. Go-only library: a C++ project cannot use it without cgo, so its value to the catalog is as a reference for avo-generated BLAKE3 kernels. The README also lists an SVE2 backend not named in the record. [retier] The README x86 tables date from 2020-02-12 code on an i7-6700K and the No-ASM '1024 kib' row is a 512 KiB measurement (6.7x like-for-like, not 3.4x); the NEON table (2026-07-23) predates the 2026-08-19 NEON change. The current numbers come from contributor PRs #41/#42/#51/#53/#54 (BobDu, Aug 2026) as benchstat output in PR descriptions, not from a results file in the repo. CI never exercises AVX-512 dispatch (qemu jobs cover Haswell, Penryn, qemu64 and Neoverse only); arm64 inputs up to 2 KiB run pure Go; benchmarks are single-threaded on a hot-cache all-zero buffer; the baseline is the same library without assembly, not another BLAKE3 implementation.

Go only (not callable from C++ without cgo). Assembly is emitted by Go programs written with avo (the _asm directory), not hand-typed .s files. x86-64 with AVX2/AVX-512/SSE4.1 plus arm64 NEON/SVE2 variants; other targets fall back to pure Go. Does its own internal buffering and is single-threaded, so very small inputs are slower than the Rust crate. LICENSE file is CC0 and LICENSE-MIT is also present.

## Maintenance

Actively maintained (last commit 2026-09-03, a burst of \~25 merged PRs from contributor BobDu in Aug 2026 adding AVX-512 and SVE2), dual CC0-1.0 / MIT licensed, so copyable; tier could rise because PRs #41/#42/#51/#53/#54 publish benchstat tables with Go 1.26.5, the in-repo benchmark, default flags and named CPUs, though they are contributor-run, not independent.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** First-party Go benchmark (bench_test.go BenchmarkBLAKE3, go test -bench) with the CPU named (i7-6700K, Apple M4), but no Go version or build flags are stated and the author says no attempt was made at precise measurement, so it falls short of A; no independent measurement found.
- **Retiered** C to A: Enricher: contributor PRs #41, #42, #51, #53 and #54 publish benchstat tables for the repo's BenchmarkBLAKE3 (Go 1.26.5, n=6/20, named AWS CPUs, BLAKE3_PUREGO baseline), which gives public benchmark code, toolchain, flags and CPU model for the current assembly; the README's 2020 tables stay as the stale first-party figures. C to A.
- **Verifier notes:** Numbers in the record match the README. Main shortcomings: first-party, Go version unstated, x86 tables from Feb 2020 code and NEON table from before Aug 2026 kernel rewrites, no AVX-512/SVE2 measurements, internally inconsistent 1024 KiB no-ASM row (true ratio 3.4x or 6.7x), Go-only. Not a duplicate of the listed BLAKE3-team/BLAKE3 entry (wave 7): independent Go implementation, not a wrapper.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-74 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/zeebo/blake3>
  - <https://github.com/zeebo/blake3#timing-tables>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/README.md>
  - <https://github.com/zeebo/blake3/commits>
  - <https://github.com/zeebo/blake3/commits/master/README.md>
  - <https://github.com/zeebo/blake3/blame/master/README.md>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/bench_test.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/Makefile>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/go.mod>
- **Sources the enricher read:**
  - <https://github.com/zeebo/blake3>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/README.md>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/bench_test.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/Makefile>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/go.mod>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/api.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/blake3.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/digest.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/blake3_test.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/fuzz_test.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/vec_test.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/bench/table.py>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/internal/alg/alg.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/internal/alg/hash/hash.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/internal/alg/compress/compress.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/internal/consts/cpu.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/internal/consts/cpu_purego.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/internal/consts/consts.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/internal/alg/compress/compress_sse41/impl_amd64.s>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/internal/alg/hash/hash_avx2/impl_amd64.s>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/internal/alg/hash/hash_avx512/impl_amd64.s>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/_asm/hash/hash_sve2/emit.go>
  - <https://raw.githubusercontent.com/zeebo/blake3/HEAD/_asm/hash/hash_sve2/g.go>
  - <https://github.com/zeebo/blake3/tree/master/internal/alg>
  - <https://github.com/zeebo/blake3/tree/master/_asm/hash/hash_sve2>
  - <https://github.com/zeebo/blake3/tree/master/.github/workflows>
  - <https://github.com/zeebo/blake3/tree/master/bench>
  - <https://github.com/zeebo/blake3/commits>
  - <https://github.com/zeebo/blake3/commit/69e6ccb>
  - <https://github.com/zeebo/blake3/commit/3863282>
  - <https://github.com/zeebo/blake3/issues?q=is%3Aissue>
  - <https://github.com/zeebo/blake3/issues/5>
  - <https://github.com/zeebo/blake3/issues/9>
  - <https://github.com/zeebo/blake3/issues/12>
  - <https://github.com/zeebo/blake3/pulls>
  - <https://github.com/zeebo/blake3/pulls?q=is%3Apr+is%3Aclosed>
  - <https://github.com/zeebo/blake3/pull/38>
  - <https://github.com/zeebo/blake3/pull/41>
  - <https://github.com/zeebo/blake3/pull/42>
  - <https://github.com/zeebo/blake3/pull/48>
  - <https://github.com/zeebo/blake3/pull/51>
  - <https://github.com/zeebo/blake3/pull/53>
  - <https://github.com/zeebo/blake3/pull/54>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/zeebo/blake3`) · [data/wave13/enrich/raw/github_com_zeebo_blake3.json](../../../data/wave13/enrich/raw/github_com_zeebo_blake3.json) (enrichment confidence 0.85)

</details>
