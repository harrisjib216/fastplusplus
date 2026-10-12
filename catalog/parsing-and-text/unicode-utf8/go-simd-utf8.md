# go-simd/utf8

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Pure-Go SIMD UTF-8 validator and rune counter, byte-identical to unicode/utf8, faster on non-ASCII text.

| | |
|---|---|
| **Beats** | Go standard library unicode/utf8 package |
| **Claimed result** | BENCHMARKS.md, Apple M4 Max NEON: Valid ASCII 1.21x-2.21x; Valid multibyte-mixed 1.90x-9.0x (1 MiB: 3.87 vs 0.43 GB/s); RuneCount 3.58x-8.7x vs unicode/utf8. amd64 AVX2 GitHub Actions EPYC runner: Valid ASCII 2.06x-3.65x, Valid mixed 3.66x-19.74x (1 MiB: 5196 vs 263 MB/s), RuneCount 4.81x-21.08x. Separately, the README reports Valid 19.07x on EPYC 7763 (5940 vs 312 MB/s, \~1 MiB mixed buffer) and IBM z15 s390x results of 1.96x (ASCII 16 KiB), 1.73x (ASCII 1 MiB), 10.4x (mixed 1 MiB) and 9.5x (RuneCount 1 MiB). The README's \~4.6x RuneCount figure came from a QEMU-hosted x86 VM, not native hardware. |
| **Workload** | Valid (UTF-8 validation, Lemire-Keiser lookup algorithm) and RuneCount on printable-ASCII and multibyte-mixed (a/e-acute/lambda/CJK/emoji) buffers, 64 B-1 MiB, single core, BenchmarkParity\* harness vs unicode/utf8. Run on Apple M4 Max NEON and a GitHub Actions AMD EPYC AVX2 runner (BENCHMARKS.md); IBM z15 s390x results are in the README. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max (arm64 NEON, macOS); GitHub Actions ubuntu-latest AMD EPYC runner (7763 or 9V74 depending on run, AVX2, no AVX-512); IBM z15 (s390x, VXE2, real hardware, 2026-07-03, per README) |
| **Compiler and flags** | Go 1.26.4 (M4 Max arm64 and z15 runs); Go 'stable' via setup-go on the amd64 CI runner; GOAMD64=v1 on amd64; go test -bench=Parity -benchtime=0.3s -count=3 (arm64), -count=6 (amd64, s390x) |
| **Adoption** | 0 stars; new project with CI-driven, reproducible cross-architecture benchmark suite (.github/workflows/bench.yml) |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/go-simd/utf8) · [benchmark](https://github.com/go-simd/utf8/blob/main/BENCHMARKS.md) |

## Verdict

On a native GitHub Actions AMD EPYC runner (AVX2, GOAMD64=v1, Go stable) using the BenchmarkParity\* harness against Go stdlib unicode/utf8, mixed-UTF-8 Valid throughput reaches 19.74x stdlib (5196 vs 263 MB/s at 1 MiB) and RuneCount reaches 21.08x; on an Apple M4 Max (NEON, Go 1.26.4) the same harness shows 1.21x-2.21x on ASCII, 1.90x-9.0x on mixed Valid, and 3.58x-8.7x on RuneCount; a separate real-hardware IBM z15 (s390x, go1.26.4) run shows 1.73x-1.96x on ASCII and 9.5x-10.4x on mixed/RuneCount. ppc64le figures are llvm-mca cycle-model estimates, not measured runs.

## Use it when

- Non-ASCII or mixed-script UTF-8 (2/3/4-byte runes) on amd64 or arm64, where measured wins are 1.9x-21x
- Throughput-bound batch validation or rune counting of buffers roughly 1 KiB-1 MiB
- Need exact stdlib-compatible semantics (identical bool/int, even on malformed input) with no calling-code changes
- Running on amd64 (SSE4.1/AVX2) or Apple Silicon arm64 (NEON), the two kernels with native-hardware benchmarks and fuzzing
- s390x (z13+) workloads: the only other kernel measured on real hardware (IBM z15), 1.7x-10.4x

## Skip it when

- ppc64le deployments where you need proven real-silicon numbers: those figures are llvm-mca static estimates, not measurements
- loong64/riscv64 targets, which still just call unicode/utf8 with ordinary function-call overhead (no SIMD kernel)
- Hot paths that call ValidString/RuneCountInString specifically: both are plain aliases to stdlib, no SIMD benefit
- Anything requiring a track record: 0 GitHub stars, first NEON kernel landed only 2026-06-22, ppc64le/s390x pre-scan fixes as recent as this year
- Teams uncomfortable with generated assembly (go-asmgen) and per-arch .s files as a maintenance surface

## How it is fast

Implements Lemire & Keiser's 'Validating UTF-8 In Less Than One Instruction Per Byte' nibble-lookup algorithm (PSHUFB/VTBL byte classification, PALIGNR/VEXT to shift in the previous block, PTEST error accumulator), generated via go-asmgen, replacing stdlib's byte-at-a-time DFA with one-pass block validation. RuneCount piggybacks on an already-validated block and mask-and-POPCNTs continuation bytes instead of decoding runes individually. A dedicated ASCII pre-scan (group-of-4 PMOVMSKB on amd64, a 64-byte-unrolled high-bit test on NEON/s390x) short-circuits pure-ASCII input to a memory-bandwidth scan, fixing an earlier 5-8x regression the full validator had against stdlib's own ASCII fast path.

## Compared with alternatives

Versus stuartcarnie/go-simd — the only other pure-Go SIMD UTF-8 validator and also Lemire-based — this package edges it \~3.5% on native AVX2 CI, adds NEON/VSX/s390x kernels and a RuneCount fast path the 2018 stuartcarnie repo lacks (which also predates go.mod and has no explicit root license), and is actively maintained; the other siblings (simdutf8, SimdUnicode, utf8_range, etc.) target Rust/.NET/C++ ecosystems, so this is the pick specifically for Go code that must stay pure-Go (no cgo).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys (CPU feature detection); test-only: github.com/stuartcarnie/go-simd (benchmark comparator), github.com/stretchr/testify |
| **Minimum toolchain** | Go 1.26.4 (go.mod requires `go 1.26.4`) |
| **Platforms** | amd64 (SSE2/SSSE3/SSE4.1 baseline, AVX2 runtime-dispatched), arm64 (NEON), ppc64le (VSX/AltiVec, qemu-validated only, no native perf data), s390x (vector facility, validated on real z15); loong64/riscv64 fall back to scalar unicode/utf8 |
| **Thread safety** | not documented; Valid/RuneCount are pure functions with no package-level mutable state visible in utf8.go, so ordinary concurrent-read use appears safe but is not explicitly guaranteed |
| **Drop-in for the baseline** | partial — Valid and RuneCount are true drop-ins (same signature, byte-identical output including on invalid input); ValidString and RuneCountInString exist for API parity but literally forward to unicode/utf8 with no SIMD path |

## Gotchas

- All-ASCII input on amd64 and s390x used to be 5-8x slower than stdlib before the ASCII pre-scan landed (fixed in current main, but shows the failure mode the design has to guard against)
- ppc64le has no GitHub-hosted runner; it is cross-compiled and tested under qemu only, so 'native perf pending' per the README
- ValidString/RuneCountInString get zero speedup — they're pass-throughs, not SIMD-accelerated
- Package is very new (0 stars, single open issue is Renovate's dependency dashboard) with no external adopters found

## Caveats and trade-offs

Very new, low-usage project (0 stars), so treat this as an early-stage result. The amd64 numbers come from a shared GitHub Actions runner whose EPYC part varies between runs: absolute MB/s is noisy, but same-job ratios are valid. The pure-ASCII path regressed 5-8x vs stdlib on amd64, and ran at 0.13x on s390x, until a recent ASCII pre-scan fix; the arm64 NEON kernel was only added on 2026-06-22. The README's 4.6x RuneCount figure was measured under QEMU. ppc64le figures are llvm-mca estimates, not measurements.

Pure-ASCII input is actually slower per-cycle than stdlib without a pre-scan short-circuit (mitigated by an ASCII fast path achieving 1.7-2.0x); ppc64le numbers are LLVM-mca cycle-model estimates, not measured on real silicon.

## Maintenance

Active (last commit 2026-09-08), BSD-3-Clause, and small enough (about a dozen Go/asm files) to vendor or fork, but has zero stars and its NEON/ASCII-prescan fixes are only weeks to months old — an early-stage result, not a battle-tested one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** BENCHMARKS.md compares directly against Go stdlib unicode/utf8 using public code (bench_parity_test.go, BenchmarkParity\*). It states Apple M4 Max, Go 1.26.4, `-benchtime=0.3s -count=3` and gives the exact reproduce command, which meets tier A. The amd64 section runs on a GitHub Actions EPYC runner (GOAMD64=v1, Go 'stable', -count=6). The README adds an IBM z15 run (go1.26.4, -count=6).
- **Verifier notes:** The record's specific numbers (19.07x, 5940/312 MB/s, z15 ratios, 4.6x) are in README.md#performance, not in the cited BENCHMARKS.md. BENCHMARKS.md has newer and generally larger ratios (up to 21x on amd64, up to 9x on an M4 Max), so I rewrote claimed_speedup from it rather than downgrading. Metadata matches: BSD-3-Clause, 0 stars, last commit 2026-09-08, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/go-simd/utf8/blob/main/BENCHMARKS.md>
  - <https://github.com/go-simd/utf8>
  - <https://github.com/go-simd/utf8/blob/main/README.md>
  - <https://github.com/go-simd/utf8/blob/main/bench_parity_test.go>
  - <https://github.com/go-simd/utf8/blob/main/.github/workflows/bench.yml>
  - <https://github.com/go-simd/utf8/blob/main/.github/workflows/bench-amd64.yml>
- **Sources the enricher read:**
  - <https://github.com/go-simd/utf8>
  - <https://github.com/go-simd/utf8/blob/main/README.md>
  - <https://github.com/go-simd/utf8/blob/main/BENCHMARKS.md>
  - <https://github.com/go-simd/utf8/blob/main/go.mod>
  - <https://github.com/go-simd/utf8/blob/main/utf8.go>
  - <https://github.com/go-simd/utf8/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/go-simd/utf8`) · [data/wave3/enrich/raw/github_com_go_simd_utf8.json](../../../data/wave3/enrich/raw/github_com_go_simd_utf8.json) (enrichment confidence 0.68)

</details>
