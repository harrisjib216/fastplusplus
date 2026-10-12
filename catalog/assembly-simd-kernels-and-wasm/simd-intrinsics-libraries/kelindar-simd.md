# kelindar/simd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Go package of clang auto-vectorised Sum/Min/Max and element-wise Add/Sub/Mul/Div kernels, 2-80x over scalar Go loops.

| | |
|---|---|
| **Beats** | generic pure-Go implementation inside the same package |
| **Claimed result** | README tables on an i7-13700K: uint8 sum 16384 elements 52.57x, uint8 min 4096 55.02x, uint16 min 16384 84.12x, uint32 sum 16384 10.07x, uint32 add 16384 5.06x, uint8 div 4096 1.19x, uint16 div 16384 0.79x (slower). An Apple M3 Pro table is also given. |
| **Workload** | Element-wise add/sub/mul/div and sum/min/max reductions on uint8..uint64, int8..int64, float32 and float64 slices of 256, 4096 and 16384 elements filled with the repeating pattern (i % 100) + 1; the baseline is the package's own generic scalar Go loop (selected by setting hardware=false), the fast path is clang auto-vectorized C translated to Plan9 assembly (AVX2 on amd64, NEON on arm64). |
| **Metric** | throughput |
| **Hardware** | 13th Gen Intel Core i7-13700K (Windows, amd64) and Apple M3 Pro (darwin, arm64) |
| **Compiler and flags** | Go version for the README runs not stated (go.mod declares go 1.18; CI uses Go 1.25); assembly generated from C by gocc (clang) with -O3 and --arch avx2 / neon / apple per codegen/generate.sh; default go test -bench settings; the SPEEDUP column is base-mode ns/op divided by simd-mode ns/op from runBenchmark in simd_test.go |
| **Adoption** | 34 stars |
| **Last commit** | 2026-03-07 |
| **Links** | [repository](https://github.com/kelindar/simd) · [benchmark](https://github.com/kelindar/simd) |

## Verdict

The README's SPEEDUP column is the package's own generic Go loop (hardware=false) divided by the assembly path on the same call, on 256-, 4096- and 16384-element slices filled with (i % 100) + 1, measured on an i7-13700K under Windows and an Apple M3 Pro with an unstated Go version. On the i7-13700K uint8 Sum at 16384 elements runs 58.88 ns (52.57x), uint16 Min 110.94 ns (84.12x), uint32 Add 1975.68 ns (5.06x), uint64 Min 1.96x and integer Div 0.69x to 1.20x.

## Use it when

- Go code that sums, mins, maxes or adds whole slices of 8-, 16- or 32-bit integers or float32, where the README shows 10-80x on 256-16384 elements (i7-13700K and Apple M3 Pro).
- L1/L2-resident batches (a few KB to a few hundred KB) inside analytics or columnar loops, on amd64 with AVX2 or on arm64.
- When you want an MIT-licensed, dependency-light package (klauspost/cpuid only) with an automatic pure-Go fallback for other architectures.
- Float32 element-wise work: division about 5x on the i7-13700K, add 4.95x there and 7.39x on the M3 Pro at 16384 elements.

## Skip it when

- Integer division of any width: the README shows 0.69x to 1.2x, slower than scalar Go for int8 and for uint16 at 16384 elements.
- When float sums must match a sequential loop bit for bit: the vectorised float32/float64 Sum reorders the additions (four vaddps accumulators), so rounding differs from the Go fallback on real data.
- Slices with 2^31 or more elements: the C loops use 'i &lt; (int)size' and the assembly tests the 32-bit size register, so a 2 GiB-plus slice is silently processed as empty or truncated.
- Untrusted or mismatched slice lengths: the asm path uses len(dst) for input1 and input2 without checks and takes &input[0], so shorter inputs are read out of bounds and an empty slice panics (the Go fallback returns 0 for an empty Sum).
- []int, []uint or named element types through the generic Sum/Min/Max: the type switch only matches the ten fixed-width slice types, so these fall back to the scalar loop.

## How it is fast

Each kernel is a plain C loop marked '#pragma clang loop vectorize(enable) interleave(enable)', compiled by clang -O3 and translated to Go Plan9 assembly with kelindar/gocc, so the speed comes from LLVM's loop vectoriser rather than hand-written intrinsics. On amd64 the uint8 sum, for example, runs four 32-byte vpaddb accumulators per 128-byte iteration and finishes with vpsadbw; float32 sum likewise keeps four vaddps accumulators. Go's own compiler does not auto-vectorise, which is why reductions and narrow integer types show 10-80x; 64-bit integer min/max (about 2x) and all integer division (lane-by-lane idiv, 0.7-1.2x) gain little or lose.

## Compared with alternatives

Pick it over vek when you need integer types (int8 to uint64) on both amd64 and arm64 rather than vek's wider float32/float64 math set, and over tphakala/simd when a tiny Sum/Min/Max/Add API is enough and you do not need its hand-written fused kernels; segmentio/asm covers different functions (ASCII, bswap, sorting) and does not overlap.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/klauspost/cpuid/v2 (runtime AVX2/FMA3 detection); testify for tests only |
| **Minimum toolchain** | Go 1.18 (go.mod); CI runs Go 1.25. Regenerating the assembly needs clang and kelindar/gocc, whose versions are not documented (open issue #7). |
| **Platforms** | amd64 with AVX2 and FMA3; arm64 (NEON, separate darwin/Apple build); pure-Go fallback on every other GOARCH or with -tags noasm |
| **Thread safety** | Functions are stateless and safe to call concurrently on disjoint dst slices; the package-level 'hardware' switch is a plain variable that only the tests toggle. Otherwise not documented. |
| **Drop-in for the baseline** | partial — same results as its own generic Go loops for integer types on valid inputs, but not for empty slices (panic), mismatched lengths (out-of-bounds reads), slices of 2^31+ elements, or float sums (different rounding). |

## Gotchas

- Length handling differs between paths: Add/Sub/Mul/Div pass len(dst) to the assembly without checking input1/input2, while the Go fallback loops over len(input1) and panics on a short dst or input2; Sum/Min/Max on an empty slice panic on &input[0] in the asm path.
- The C kernels loop with 'for (int i = 0; i &lt; (int)size; ...)' and the amd64 assembly opens with 'test edx, edx; jle', so for slices of 2^31 elements or more the fast path returns 0 or processes only the low 32 bits of the length, with no error.
- Test gaps rather than benchmark flaws: the equality tests use one 70-element vector, shorter than one 128-byte unrolled AVX2 iteration of the 8-bit kernels, so their main vector loop is only exercised by benchmarks that assert NotZero; and input1 and input2 are identical (pattern (i % 100) + 1), so Sub (all zeros) and Div (all ones) tests cannot catch swapped operands. The integer-valued data also sums exactly in float32, hiding the reordered float summation.
- Before PR #6 (2026-03-07) the amd64 assembly clobbered the BP frame pointer without restoring it (issue #5, possible crashes during stack unwinding); the regenerated assembly now pushes and pops rbp, and the README tables were regenerated in the same commit, so use a commit from 2026-03-07 or later (there are no tagged releases).

## Known shortcomings

- Go version unstated; rows above 50x (max 84.12x) are against a scalar Go loop and division is 0.69-0.79x in several rows; the SIMD path has no length checks (an empty slice panics, short inputs read out of bounds). Go-only.
- Correctness bug: the C kernels loop with (int)size and the amd64 assembly opens with 'test edx, edx; jle', so slices of 2^31 or more elements are silently skipped or truncated. Float Sum is reassociated over 4 vaddps accumulators; tests use one 70-element vector with identical input1 and input2, so swapped Sub/Div operands cannot be caught; the BP clobber (issue #5) was fixed in PR #6 on 2026-03-07; integer Div is 0.69-1.20x.

## Caveats and trade-offs

Many rows exceed 50x (uint16 min 16384 84.12x, int8 min/max 16384 about 68.7x on the i7-13700K; uint8 max 4096 65.16x on the M3 Pro) against a hand-written scalar Go loop, not slices.Min or the min/max builtins; Go's compiler does not auto-vectorize, so the ratio mostly measures clang vectorization versus scalar Go, on L1/L2-resident data. Division gives about 1x and is slower in several rows (uint16 div 16384 0.79x, int8 div 0.69x to 0.71x on the i7-13700K). The SIMD path takes &input[0] without length checks, so an empty slice panics, and Add/Sub/Mul/Div pass len(dst) to the assembly without checking input1/input2, so shorter inputs are read out of bounds. Capped at C because the Go version is not stated.

AVX2 on amd64 and NEON on arm64 only; generic Go fallback otherwise; README lists reductions (Sum, Min, Max) and element-wise Add, Sub, Mul, Div; the Div rows show about 1x.

## Maintenance

Active but small (13 commits, 34 stars, last commit 2026-03-07 regenerating all assembly and fixing the frame-pointer ABI bug), MIT-licensed and copyable; one open issue asks for reproducible codegen because generate.sh ships with its gocc lines commented out.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Go benchmark (bench_test.go plus runBenchmark in simd_test.go, which times the same call with hardware=false and hardware=true) with CPU models stated (i7-13700K, Apple M3 Pro), but the Go version used for the README runs is not stated and many rows exceed 50x against a scalar Go loop, so it is capped at C.
- **Verifier notes:** All seven claimed figures appear verbatim in the README i7-13700K table; the README tables were regenerated in the 2026-03-07 commit (15bded0) together with the assembly. Baseline is the library's own scalar fallback, which matches the category's 'scalar reference' baseline only loosely (Go, not C/C++). Metadata confirmed: MIT, 34 stars, 5 forks, 13 commits, last commit 2026-03-07.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-58 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/kelindar/simd>
  - <https://github.com/kelindar/simd/commits>
  - <https://github.com/kelindar/simd/commits/main>
  - <https://github.com/kelindar/simd/commit/15bded05f2450aa595f2d3d8bb30424b6da3d7ad>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/bench_test.go>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/simd_test.go>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/simd.go>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/simd_funcs.go>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/go.mod>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/codegen/generate.sh>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/codegen/README.md>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/.github/workflows/test.yml>
- **Sources the enricher read:**
  - <https://github.com/kelindar/simd>
  - <https://github.com/kelindar/simd/commits/main>
  - <https://github.com/kelindar/simd/tree/main/codegen>
  - <https://github.com/kelindar/simd/issues?q=is%3Aissue>
  - <https://github.com/kelindar/simd/issues/5>
  - <https://github.com/kelindar/simd/issues/7>
  - <https://github.com/kelindar/simd/pulls?q=is%3Apr>
  - <https://github.com/kelindar/simd/pull/6>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/go.mod>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/simd.go>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/simd_funcs.go>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/simd_stub.go>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/simd_avx2_amd64.go>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/simd_avx2_amd64.s>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/bench_test.go>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/simd_test.go>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/codegen/generate.sh>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/codegen/README.md>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/codegen/simd_avx2_amd64.c>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/codegen/simd_neon_arm64.c>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/codegen/simd_apple_arm64.c>
  - <https://raw.githubusercontent.com/kelindar/simd/HEAD/.github/workflows/test.yml>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/kelindar/simd`) · [data/wave13/enrich/raw/github_com_kelindar_simd.json](../../../data/wave13/enrich/raw/github_com_kelindar_simd.json) (enrichment confidence 0.85)

</details>
