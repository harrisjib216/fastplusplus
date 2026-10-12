# go-simdcsv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> AVX-512 SIMD CSV parser for Go; drop-in encoding/csv replacement, faster only on unquoted data.

| | |
|---|---|
| **Beats** | encoding/csv (Go standard library CSV parser) |
| **Claimed result** | +35% faster (unquoted, 10K and 100K rows), +8% faster (10% quoted, 100K rows), +6% faster (40% quoted, 100K rows); notably -30% slower on all-quoted-fields data |
| **Workload** | ReadAll throughput on synthetic CSV files with varying quote density (unquoted, 10%/40% quoted, all-quoted) at 10K and 100K rows, using AVX-512 SIMD scanning vs Go's encoding/csv |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9R14 with AVX-512 |
| **Compiler and flags** | Go 1.26 with GOEXPERIMENT=simd |
| **Adoption** | 47 stars |
| **Last commit** | 2026-06-14 |
| **Links** | [repository](https://github.com/nnnkkk7/go-simdcsv) · [benchmark](https://github.com/nnnkkk7/go-simdcsv#performance) |

## Verdict

Verifier confirmed the README's ReadAll throughput table (e.g. 228-&gt;309 MB/s unquoted, 10K rows; +35%) against public paired Stdlib/SIMD benchmarks in benchmark_test.go, run with `go test -bench=. -benchmem` on Go 1.26 + GOEXPERIMENT=simd, AMD EPYC 9R14 (AVX-512), via a manually-triggered self-hosted CI workflow; the reported -30% regression applies specifically to the 10K-row all-quoted-fields case.

## Use it when

- Go services that already deploy on amd64 hardware with AVX-512 (AMD Zen4+/EPYC 9x, Intel Skylake-X+)
- Large, mostly-unquoted CSV (logs, numeric exports) at 10K-100K+ row scale, where the README shows +35% ReadAll throughput
- You can pin CI/prod to Go 1.26+ built with the experimental GOEXPERIMENT=simd flag
- You want the raw-bytes path (ParseBytes/ParseBytesStreaming) to skip io.Reader overhead entirely
- You're prototyping or benchmarking SIMD CSV techniques in Go rather than shipping a production dependency

## Skip it when

- Production systems that can't accept a dependency the README itself calls experimental and 'not recommended for production use'
- Any deployment target without AVX-512 F/BW/VL: Apple Silicon/ARM64, pre-Zen4 AMD, pre-Skylake-X Intel, and most hosted CI runners (ubuntu-latest included) — you get the scalar path with no speedup
- Heavily-quoted CSV: the README's own numbers show \~30% slower than encoding/csv on all-quoted 10K-row data due to extra validation passes
- Teams that can't carry an experimental Go toolchain flag (GOEXPERIMENT=simd) through their build pipeline
- Anyone needing a stable API long-term: `simd/archsimd` is called out as unstable across Go releases, and the project is very young (47 stars, first tagged releases only recently)

## How it is fast

It scans input in 64-byte AVX-512 chunks (`scanBuffer`), building bitmasks for quote/comma/CR/LF positions instead of branching byte-by-byte, then derives the in-quotes region with a prefix-XOR computed via PCLMULQDQ carryless multiplication (the simdjson-style structural-character technique) before locating field boundaries and materializing strings. `useAVX512` is checked once at init via a CPU feature test, with an automatic scalar fallback when AVX-512 (F/BW/VL) isn't available.

## Compared with alternatives

It's the only Go-language entry in this category (siblings are .NET/Rust/Python/R/CLI tools) and the closest analog to the Rust `simd-csv` crate's idea applied to Go's encoding/csv. Pick it over cisv/zsv/xan/qsv only when you need an in-process Go library rather than a CLI tool, your data is mostly unquoted, and you can run on AVX-512 hardware with an experimental Go build.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none beyond stdlib and Go's experimental simd/archsimd package |
| **Minimum toolchain** | Go 1.26.4+ built with GOEXPERIMENT=simd |
| **Platforms** | amd64 only for the SIMD path (requires AVX-512 F/BW/VL); falls back to a scalar implementation elsewhere, including arm64/Apple Silicon |
| **Thread safety** | not documented — mirrors encoding/csv, whose Reader/Writer are not documented as safe for concurrent use by multiple goroutines |
| **Drop-in for the baseline** | partial — explain: the Reader/Writer API is a same-name substitute for encoding/csv with all standard options supported, but unlike stdlib it requires Go 1.26+ and an experimental compiler flag (GOEXPERIMENT=simd), and the SIMD code path only activates on AVX-512 hardware |

## Gotchas

- SIMD source files are gated behind the `goexperiment.simd && amd64` build tag, so the fast path only compiles/activates under GOEXPERIMENT=simd on amd64; everywhere else you silently get the scalar implementation
- All-quoted-field CSV is \~30% slower than encoding/csv (10K-row case) — the opposite of the headline speedup
- Published AVX-512 numbers come only from a manually-triggered self-hosted CI workflow (ci-avx512.yml); the default per-PR CI (ubuntu-latest) runs scalar-only and doesn't exercise or verify the SIMD path
- `simd/archsimd` is an experimental Go package the README warns 'may have breaking changes in future Go releases'

## Caveats and trade-offs

Modest speedup (6-35%); the README itself reports a -30% regression on all-quoted fields (10K rows). The SIMD path needs amd64 with AVX-512 (F/BW/VL) and the experimental GOEXPERIMENT=simd in Go 1.26+; elsewhere (most CI runners, pre-Zen4 AMD, pre-Skylake-X Intel, Apple Silicon/ARM64) it falls back to scalar code with no speedup. Published numbers come from a manually triggered self-hosted AVX-512 CI run. Very new/small project.

Explicitly marked experimental, requires bleeding-edge Go 1.26 with an experimental SIMD flag, AMD64-only (falls back to scalar without AVX-512, so no speedup on Apple Silicon or older CPUs), 'not recommended for production use', and is slower than stdlib on heavily-quoted data

## Maintenance

Actively maintained (last commit 2026-06-14, MIT-licensed) but the author labels it experimental and 'not recommended for production use'; at 47 stars it's better treated as a technique to read or vendor selectively than a dependency to adopt outright.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** README Performance table compares go-simdcsv vs encoding/csv ReadAll (228-&gt;309 MB/s etc.) on AMD EPYC 9R14 with Go 1.26 + GOEXPERIMENT=simd, run via `go test -bench=. -benchmem`; benchmark code is public in benchmark_test.go (paired \*_Stdlib / \*_SIMD benchmarks) and the AVX-512 CI workflow (.github/workflows/ci-avx512.yml).
- **Verifier notes:** All numbers match the README table exactly (all-quoted -30% is the 10K-row case only; 10%/40% quoted are 100K-row only). Metadata checked via gh: MIT, 47 stars, last commit 2026-06-14, not a fork or archived.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/nnnkkk7/go-simdcsv>
  - <https://github.com/nnnkkk7/go-simdcsv#performance>
  - <https://github.com/nnnkkk7/go-simdcsv/blob/main/benchmark_test.go>
  - <https://github.com/nnnkkk7/go-simdcsv/blob/main/.github/workflows/ci-avx512.yml>
- **Sources the enricher read:**
  - <https://github.com/nnnkkk7/go-simdcsv>
  - <https://github.com/nnnkkk7/go-simdcsv#performance>
  - <https://github.com/nnnkkk7/go-simdcsv/blob/main/go.mod>
  - <https://github.com/nnnkkk7/go-simdcsv/blob/main/simd_scanner.go>
  - <https://github.com/nnnkkk7/go-simdcsv/blob/main/quote.go>
  - <https://github.com/nnnkkk7/go-simdcsv/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/nnnkkk7/go-simdcsv`) · [data/wave3/enrich/raw/github_com_nnnkkk7_go_simdcsv.json](../../../data/wave3/enrich/raw/github_com_nnnkkk7_go_simdcsv.json) (enrichment confidence 0.78)

</details>
