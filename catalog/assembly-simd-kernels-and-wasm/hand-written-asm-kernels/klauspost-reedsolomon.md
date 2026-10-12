# klauspost/reedsolomon (Go AVX2/AVX512/GFNI/NEON/SVE assembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (amd64, arm64 and other assembly)` · `MIT` · 🟢 active

> Go Reed-Solomon erasure coder with generated SSSE3/AVX2/AVX-512/GFNI, NEON/SVE and ppc64le kernels; 5-19x its own pure-Go path.

| | |
|---|---|
| **Beats** | the library's own pure-Go Galois-field code path (generic Go compiler output) |
| **Claimed result** | README Performance table, encode MB/s with 1 MB shards and 32 threads, Go / SSSE3 / AVX2 / GFNI: 5+2 40,690 / 97,827 / 202,283 / 241,747; 8+8 14,244 / 62,412 / 128,343 / 271,680; 10+4 17,999 / 80,093 / 152,673 / 273,628; 50+20 3,520 / 24,184 / 44,734 / 47,706. AVX2 over pure Go is 4.97x (5+2), 9.01x (8+8), 8.48x (10+4) and 12.7x (50+20); GFNI over pure Go is 5.94x to 19.1x (derived from page data). The README says GFNI with AVX512 is 'up to 2x over AVX2'. A separate ppc64le table shows 8.03x to 9.36x for the Galois kernels, old vs new (no hardware named). |
| **Workload** | Reed-Solomon encoding of 1 MB shards with 32 threads for 5+2, 8+8, 10+4 and 50+20 data+parity shards. |
| **Metric** | throughput |
| **Hardware** | x86 CPU model not named; the ARM64 NEON numbers are from an EC2 m6g.16xlarge (Graviton2) |
| **Compiler and flags** | Go version not stated |
| **Adoption** | 2.1k stars; widely used Go erasure-coding library |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/klauspost/reedsolomon) · [benchmark](https://github.com/klauspost/reedsolomon) |

## Verdict

The README Performance table, refreshed in PR #336 (2026-04-21), encodes 1 MB random shards with GOMAXPROCS 32 on an unnamed x86 CPU with an unstated Go version: pure Go 3.5-40.7 GB/s versus AVX2 44.7-202 GB/s (4.97x for 5+2 up to 12.7x for 50+20) and AVX-512 GFNI 47.7-274 GB/s (5.94x to 19.1x), with throughput counted over data plus parity bytes (ratios derived from page data). Per-call goroutine caps (8 for AVX2, 4 for GFNI, about 2x GOMAXPROCS for pure Go) mean the SIMD columns used fewer cores than the baseline.

## Use it when

- Go storage or transport code (object stores, backup, FEC over UDP) that needs k+m erasure coding with k+m up to 256 and shards of tens of KB or more, where it runs at tens to hundreds of GB/s per encoder.
- amd64 servers with AVX2, and especially AVX-512 plus GFNI, where the GFNI kernels reach 241-274 GB/s on the README's 5+2, 8+8 and 10+4 rows.
- arm64 servers (Graviton, Kunpeng, Apple) via generated NEON and SVE kernels, and ppc64le via its own assembly (about 9x over pure Go in the README).
- Very wide codes (hundreds to 65,536 shards) via the Leopard GF16 mode, or 20+ shards via WithLeopardGF(true) when encode speed matters more than reconstruction speed.
- When byte compatibility with Backblaze JavaReedSolomon, reed-solomon-erasure (Rust) or the Jerasure matrix layout is required.

## Skip it when

- C or C++ projects: this is a Go package with Go-ABI assembly; the README links reedsolomon-c (a compatible C port) but makes no comparison with Intel ISA-L (intel/isa-l, catalogued separately), the usual C baseline.
- Platforms without its assembly (riscv64, s390x, wasm, 386) or builds with -tags=noasm: these run the pure-Go table path, which for fewer than 20 total shards lazily builds a 32 MiB two-byte multiplication table (mulTable16, 256 x 65536 uint16).
- Reconstruction-heavy Leopard workloads: Leopard GF16 encodes 5.6-27 GB/s but recovers only 1.2-3.2 GB/s in the README table, and the reconstruction-matrix cost cannot be cached at high shard counts.
- Data-integrity detection: the encoder cannot tell which shard is corrupt; callers must hash each shard and pass known-bad ones as nil.
- Short-lived encoders: New() builds matrices and pools, and issue #319 (Kunpeng-920) showed a 33% throughput drop with one encoder per call under heavy concurrency; the maintainer says encoders are meant to be reused.

## How it is fast

The x86 kernels use the split-nibble table method from 'Screaming Fast Galois Field Arithmetic' (two 16-entry tables applied with PSHUFB/VPSHUFB), and on AVX-512/AVX GFNI CPUs a GF2P8AFFINEQB 8x8 bit-matrix per coefficient instead of table lookups. avo programs in _gen generate one fused kernel per (inputs x outputs) shape up to 10x10 (mulAvxTwo_10x4_64, mulGFNI_..., mulNeon_10x10), so every input block is loaded once and all parity outputs stay in registers; larger shapes are tiled in 10x10 blocks sized to L1/L2 (perRound from cpuid cache sizes). CPU features are detected at run time through klauspost/cpuid, and the Leopard mode replaces O(k\*m) matrix multiplication with additive FFTs.

## Compared with alternatives

The Go-assembly siblings (cespare/xxhash, lukechampine/blake3, zeebo/blake3, go-and, pospop, minio/md5-simd) solve hashing, bitwise and popcount problems; pick this one when a Go program needs erasure coding, where it is the de facto SIMD implementation. Like those siblings its headline ratio is asm versus the same package's pure-Go path, not versus a C library such as ISA-L.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/klauspost/cpuid/v2 (golang.org/x/sys indirect); avo only to regenerate the amd64 assembly (_gen module) |
| **Minimum toolchain** | Go 1.24 (go.mod go 1.24); CI tests Go 1.24.x, 1.25.x and 1.26.x |
| **Platforms** | amd64 (SSE2/SSSE3/AVX2/AVX-512/GFNI, runtime dispatch), arm64 (NEON, SVE), ppc64le (assembly); pure Go elsewhere (CI runs 386 tests). CI covers Linux, macOS, Windows and ubuntu-24.04-arm. |
| **Thread safety** | Not stated in the README or Encoder doc; the repo's BenchmarkParallel and the maintainer's reply in issue #319 share one encoder across goroutines, and the inversion cache is guarded by an RWMutex. Encode itself fans out to internal goroutines (WithMaxGoroutines, WithAutoGoroutines). |
| **Drop-in for the baseline** | partial: the pure-Go path is the same package with SIMD switched off (WithAVX2(false) and similar), so the speedup is automatic; it does not replace other erasure-coding libraries unless their matrix layout matches (Backblaze, Jerasure and custom matrices are supported). |

## Gotchas

- Harness asymmetry behind the README table: New() caps the goroutines that split one Encode call at codeGenMaxGoroutines = 8 when the AVX2 code-gen path is usable and at gfniCodeGenMaxGoroutines = 4 when GFNI is, while the pure-Go and SSSE3 paths get maxGoroutines sized by WithAutoGoroutines (rounded up to a multiple of GOMAXPROCS and usually 2x GOMAXPROCS, so 64 at the table's 32 threads). So '32 threads' describes GOMAXPROCS, not the workers each column used, and the per-core gain of AVX2/GFNI over pure Go is larger than the 5-19x wall-clock ratios. This favours the baseline, so the claim is not inflated, but the columns are not equal-thread comparisons.
- Methodology gaps: no CPU model, Go version or command line is given (README benchmark names carry a -32 GOMAXPROCS suffix and a New() comment tunes a switchover 'for Zen5', but neither names the test CPU); MB/s counts data plus parity bytes, so data throughput is lower by k/(k+m); the same 7-70 MB of buffers are re-encoded in place, so the 5+2, 8+8 and 10+4 rows may be cache-resident on a large-L3 part while 50+20 (70 MB) is memory-bound, which fits GFNI gaining only 7% over AVX2 there. The README also does not say whether the AVX2 column disabled the separate AVX+GFNI path (-no-avx-gfni).
- Several releases were retracted or patched for crashes, not wrong output: v1.11.6 slice-bounds panic in codeSomeShardsAVXP (issue #240), v1.12.2 Graviton4 build (PR #283), a ReconstructSome segfault from PR #267 fixed in PR #303 (issue #302), an arm64 NEON out-of-bounds read in mulNeon_10x10 fixed in v1.13.3 (#329), a SIGILL on GFNI CPUs without AVX-512 fixed in v1.13.2 (#325), and a GFNI-on-non-GFNI-CPU test crash reported by Debian fixed in v1.14.2 (#343/#344).
- The checked-in amd64 assembly cannot currently be regenerated from scratch (issue #346, open: deleting galois_gen_amd64.s breaks go generate), and -tags=nopshufb (the README's patent mitigation) removes the PSHUFB kernels, so CPUs without GFNI fall back to the pure-Go path with its 32 MiB table.

## Known shortcomings

- README numbers match but the x86 CPU and Go version are unstated and the baseline is the library's own pure-Go path (no ISA-L comparison); asm is generated by avo in _gen. Tables refreshed by PR #336 on 2026-04-21.
- Harness asymmetry that favours the baseline: New() caps workers per Encode at 8 for the AVX2 code-gen path (codeGenMaxGoroutines) and 4 for GFNI (gfniCodeGenMaxGoroutines) while pure Go and SSSE3 get about 2x GOMAXPROCS (64 at '32 threads'), so the columns are not equal-thread and the per-core gain is larger than the 5-19x shown. No CPU, Go version or command line; MB/s counts data plus parity; 50+20 (70 MB) is likely memory-bound (GFNI only 7% over AVX2); the README never says whether the AVX2 column disabled avx-gfni. History holds crash fixes and retracted releases (#240, #302, #328, #325, #343) but no wrong-parity bug; issue #346: galois_gen_amd64.s cannot be regenerated from scratch; the pure-Go fallback builds a 32 MiB mulTable16.

## Caveats and trade-offs

The README names no x86 CPU model (a GFNI+AVX512 column implies an AVX-512 GFNI-capable part) and no Go version, and it does not give the benchmark/main.go command line or flags used for each column; the 'Go' column is assumed to be the run with all SIMD toggles off. The baseline is the library's own pure-Go table-lookup path, not Intel ISA-L or a C library, and the README has no ISA-L comparison. PR #336 (2026-04-21) refreshed the Performance, Leopard and Reconstruct tables together, so the tables come from one update and not mixed releases. The amd64 assembly is emitted by avo-based generators in _gen (gen.go, gf8.go, gf16.go; avo v0.6.0), and the arm64 SVE code is produced by translation tools, so the kernels are hand-designed but generated, not hand-typed .s files. The ARM64 NEON section gives only absolute single-core MB/s on Graviton2, with no pure-Go comparison. The README carries a patent warning about erasure-coding lawsuits and offers a -tags=nopshufb build that removes the PSHUFB paths.

Per-ISA Go assembly (SSSE3, AVX2, AVX512, GFNI, NEON, SVE); runtime CPU dispatch with pure-Go fallback; larger binary.

## Maintenance

Actively maintained (v1.14.2 released in August 2026, last commit 2026-09-25, CI on three Go versions and four OS targets) and MIT-licensed; widely used, with a history of crash fixes and retracted releases but no reported wrong-parity bug in the issues reviewed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance table (1 MB shards, 32 threads) compares the pure-Go path against SSSE3, AVX2 and GFNI paths, and every number in the record matches it. The benchmark tool is public (benchmark/main.go, with -ssse3/-avx2/-avx512/-gfni toggles), but the README names no x86 CPU model, no Go version and no command line, so the result is first-party with partial methodology: tier C.
- **Verifier notes:** Numbers match the README exactly and the repo is active (last commit 2026-09-25, 2.1k stars, MIT, not a fork or archived). Shortcomings to record: x86 CPU model and Go version unstated; the baseline is the library's own pure-Go path, not ISA-L or C; the README does not give the command line for its benchmark tool; the assembly is generated by avo programs. The record's 'tables may mix releases' caveat is outdated because PR #336 refreshed them all on 2026-04-21.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-38 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/klauspost/reedsolomon>
  - <https://github.com/klauspost/reedsolomon/commits>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/README.md>
  - <https://github.com/klauspost/reedsolomon/pull/336>
  - <https://github.com/klauspost/reedsolomon/tree/master/benchmark>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/benchmark/main.go>
  - <https://github.com/klauspost/reedsolomon/tree/master/_gen>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/_gen/go.mod>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/go.mod>
- **Sources the enricher read:**
  - <https://github.com/klauspost/reedsolomon>
  - <https://github.com/klauspost/reedsolomon/commits>
  - <https://github.com/klauspost/reedsolomon/releases>
  - <https://github.com/klauspost/reedsolomon/issues?q=is%3Aissue>
  - <https://github.com/klauspost/reedsolomon/pull/336>
  - <https://github.com/klauspost/reedsolomon/pull/283>
  - <https://github.com/klauspost/reedsolomon/issues/240>
  - <https://github.com/klauspost/reedsolomon/issues/284>
  - <https://github.com/klauspost/reedsolomon/issues/302>
  - <https://github.com/klauspost/reedsolomon/issues/319>
  - <https://github.com/klauspost/reedsolomon/issues/328>
  - <https://github.com/klauspost/reedsolomon/issues/343>
  - <https://github.com/klauspost/reedsolomon/issues/346>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/README.md>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/go.mod>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/benchmark/main.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/reedsolomon.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/reedsolomon_test.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/options.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/galois.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/galois_amd64.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/galois_noasm.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/galois_nopshufb_amd64.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/galois_gen_nopshufb_amd64.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/galois_gen_switch_amd64.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/galois_arm64.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/inversion_tree.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/leopard8.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/unsafe.go>
  - <https://raw.githubusercontent.com/klauspost/reedsolomon/HEAD/.github/workflows/go.yml>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/klauspost/reedsolomon`) · [data/wave13/enrich/raw/github_com_klauspost_reedsolomon.json](../../../data/wave13/enrich/raw/github_com_klauspost_reedsolomon.json) (enrichment confidence 0.82)

</details>
