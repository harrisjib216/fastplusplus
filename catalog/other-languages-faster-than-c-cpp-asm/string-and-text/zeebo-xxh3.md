# zeebo/xxh3 (Go XXH3 with assembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Go` · `BSD-2-Clause` · 🟢 active

> Go port of XXH3 64/128-bit hashing with avo-generated SSE2/AVX2/AVX-512/NEON accumulators; no measured win over C xxHash.

| | |
|---|---|
| **Beats** | xxHash XXH3 (C reference implementation by Cyan4973), not benchmarked in the repository |
| **Claimed result** | none against C: the README tables report Go throughput only, e.g. AMD Ryzen 9 9950X 64-bit hash of 100KB 4.03 us/op (25.4 GB/s) in the plain Rate column (not defined in the README, apparently the non-assembly path), 2.10 us/op (48.7 GB/s) SSE2, 1.07 us/op (96.0 GB/s) AVX2, 685 ns/op (149 GB/s) AVX512; Intel i7-8850H @ 2.60GHz 100KB 13.0 us/op (7.88 GB/s) plain Rate, 4.05 us/op (25.3 GB/s) SSE2, 2.31 us/op (44.3 GB/s) AVX2. |
| **Workload** | XXH3 64-bit and 128-bit hashing of 0 to 100 KB inputs in Go, with SSE2, AVX2, AVX512 (amd64) and NEON (arm64) assembly accumulators; benchmark tables report Go results only |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X and Intel i7-8850H @ 2.60GHz (README benchmark headings) |
| **Compiler and flags** | Go toolchain with assembly accumulators (an avo directory is present in the repo); Go version and build flags not stated |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 587 stars |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/zeebo/xxh3) · [benchmark](https://github.com/zeebo/xxh3) |

## Verdict

Only Go throughput is published: on a Ryzen 9 9950X (README updated 2026-07-23, Go version and flags not stated) a 64-bit hash of 100 KB takes 4.03 us with the scalar Go path, 2.10 us SSE2, 1.07 us AVX2 and 685 ns AVX-512 (149 GB/s); a 2020 i7-8850H table gives 13.0, 4.05 and 2.31 us. No C xxHash timing exists in the repository (internal/compare benchmarks cespare/xxhash, a Go XXH64), so the record shows no win over the C baseline.

## Use it when

- Go services that need fast non-cryptographic hashing (content checksums, dedup keys, sharding, cache keys) without cgo: the 2026 README shows 1.2-3.9 ns per hash for 0-128 byte inputs and 96 GB/s (AVX2) or 149 GB/s (AVX-512) at 100 KB on a Ryzen 9 9950X.
- When Go code must produce the same XXH3 or XXH128 values as C, C++ or Rust peers: the repo's compat tests check Go output against vectors printed by the upstream C library.
- When you need 128-bit XXH3 or seeded XXH3 in Go; cespare/xxhash, the usual Go hash dependency, implements XXH64 only.
- amd64 and arm64 deployments, where the SIMD paths exist; go-simd/xxhash's own measurements put zeebo/xxh3 ahead of it on Apple-silicon arm64 (about 22.9 vs 15.2 GB/s at 64 KiB) and slightly ahead on amd64 at 64 KiB.

## Skip it when

- Inside C or C++ programs: call upstream xxHash directly. Nothing in the repository times the C library, so there is no evidence this port beats it (upstream reports 59.4 GB/s AVX2 and 31.5 GB/s SSE2 on an i7-9700K with Clang 10; the port's i7-8850H table shows 44.3 and 25.3 GB/s on different hardware, which is not a comparison).
- Targets other than amd64 and arm64 (ppc64le, s390x, riscv64, loong64) get only the scalar Go accumulator; go-simd/xxhash measured 10333 MB/s against this package's 4554 MB/s on an IBM z15 at 64 KiB.
- Code that needs XXH3 with a caller-supplied secret, or XXH32/XXH64: only the default secret and seeds are supported.
- Seeded hashing of many 241 B to tens-of-KB inputs: each seeded one-shot call re-derives the 192-byte secret (512 B SSE2: 20.3 vs 11.2 ns unseeded); reuse a NewSeed Hasher instead, or wait for open PR #28.
- Anything adversarial (hash-flooding resistance, integrity against attackers): XXH3 is not a keyed cryptographic hash.

## How it is fast

Inputs up to 240 bytes take XXH3's short paths as straight-line Go with bits.Mul64 128-bit multiply-fold steps and no loops below 129 bytes. Longer inputs run the 8-lane stripe accumulator (acc += lo32(data^secret) \* hi32(data^secret), plus a scramble every 1 KiB block) in avo-generated assembly: SSE2, AVX2 or AVX-512 on amd64, chosen at run time with klauspost/cpuid (AVX-512 only from 1 KiB), and NEON on arm64 (added January 2026); every other GOARCH uses a scalar Go accumulator. Hash and HashString reinterpret the slice or string header through unsafe so no copy or allocation happens per call.

## Compared with alternatives

No hashing library is catalogued in string-and-text (the siblings are parsers, text tools and LangArena rows). Among Go hash packages, pick it over cespare/xxhash when you need XXH3 or XXH128 values, and over go-simd/xxhash on amd64 and arm64, where go-simd's own numbers show zeebo/xxh3 faster; go-simd wins on s390x and other architectures with no SIMD path here.

## Integration

| | |
|---|---|
| **Form** | module (Go package github.com/zeebo/xxh3, plain Go assembly files, no cgo) |
| **Dependencies** | github.com/klauspost/cpuid/v2 (CPU feature detection on amd64); github.com/zeebo/assert for tests only |
| **Minimum toolchain** | Go 1.22 (go.mod); assembly is pre-generated, avo is only needed to regenerate it |
| **Platforms** | amd64 (SSE2 baseline, AVX2 and AVX-512F selected at run time), arm64 (NEON); all other GOARCH values build with the scalar Go path (the Makefile vets 386, arm, windows and darwin targets) |
| **Thread safety** | One-shot functions are pure and safe to call concurrently; Hasher and Hasher128 hold mutable state and, like any hash.Hash, are not documented as safe for concurrent use |
| **Drop-in for the baseline** | partial — produces the same XXH3/XXH128 values as C xxHash v0.8.0+, but through a Go API; it does not replace the C library in C or C++ code |

## Gotchas

- Run-time dispatch always prefers AVX2 over SSE2 and switches to AVX-512 at 1 KiB, yet the README's own Ryzen 9 9950X columns show SSE2 faster than AVX2 at 241 B (7.95 vs 11.3 ns) and 512 B (11.2 vs 14.1 ns) and AVX-512 slower than SSE2 at 1024 B (23.9 vs 20.7 ns). The per-ISA columns come from benchmarks that force each path (withSSE2/withAVX2 overrides in hash64_test.go), so the default path is not the fastest column between 241 B and 1 KiB on that CPU.
- Benchmark harness: the README 'Rate' column above 240 B is the forced scalar Go accumulator (withGeneric in BenchmarkFixed64), not what amd64 users get; every benchmark rehashes one zero-filled buffer, so the 100 KB rows are cache-resident; the Intel i7-8850H tables were last edited on 2020-07-28, before the January 2023 'Improve pure Go speed up to 45%' and May 2023 AVX2/AVX-512 speedups, so they describe older code. Go version and flags are not stated for either machine.
- The streaming Hasher once returned wrong hashes for payloads over 1089 bytes (issue #14, fixed September 2021), and its Write path was rewritten on 2026-09-08 ('Avoid buffered copies for chunked writes'). Reading the new block-bridging code, it keeps more than 64 unprocessed bytes whenever a block has been consumed, as XXH3's final stripe requires, but it is recent code; pin a version and keep a streaming-versus-one-shot test in your own suite.
- Heavy unsafe use: []byte inputs are reinterpreted as string headers and loads use manual pointer arithmetic (open PR #32 moves to unsafe.Add). Loads are explicitly little-endian, so big-endian targets hash correctly; go-simd/xxhash reports millions of differential fuzz runs against this package, s390x included, with zero mismatches.

## Known shortcomings

- No C timing anywhere: _compat.c only generates test vectors and compare_test.go benchmarks cespare/xxhash (Go); any speed comes from avo-generated assembly.
- Enricher: the README Rate column above 240 B is the forced pure-Go path (withGeneric in hash64_test.go), not what amd64 users get; default dispatch prefers AVX2 over SSE2 although the README's own Ryzen 9950X rows show SSE2 faster at 241 and 512 B, and AVX-512 (used from 1 KiB) is slower than SSE2 at 1024 B; the i7-8850H table dates from 2020-07-28, before the 2023 speedups.

## Caveats and trade-offs

The orchestrator's lead said the README compares against the C implementation through cgo; it does not. The README has Go-only tables, internal/compare/compare_test.go benchmarks against cespare/xxhash (a Go XXH64 implementation), and _compat.c plus compat_test.go use the C library only to generate and check test vectors for correctness. No C-versus-Go timing exists in the repository, so this stays a tier D record and does not support a claim against the C baseline. go-simd/xxhash's README compares itself with zeebo/xxh3, also without a C baseline. [retier] Enricher: README Rate above 240 B is the forced pure-Go path; default dispatch prefers AVX2 although SSE2 is faster at 241 and 512 B, and AVX-512 is slower than SSE2 at 1024 B on the README's own Ryzen 9950X rows.

Assembly only for amd64 and arm64 (other platforms use the portable Go path; on the i7-8850H the plain Rate column is 7.88 GB/s at 100KB against 44.3 GB/s in the AVX2 column); a non-zero seed re-derives the 192-byte secret on every call so seeded hashing is slower at small sizes (512 B SSE2: 20.3 against 11.2 ns/op).

## Maintenance

Actively maintained (last commit 2026-09-08, NEON path January 2026, five open PRs including two performance PRs) and BSD-2-Clause; easy to adopt as a Go dependency (gotosocial vendors it), but as a 'faster than C' claim it stays tier D with no measurement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The README tables report Go-only throughput (Ryzen 9 9950X 100KB: 4.03 us/op Rate, 2.10 us/op SSE2, 1.07 us/op AVX2, 685 ns/op AVX512; i7-8850H 100KB: 13.0, 4.05 and 2.31 us/op) with no C timing; no number anywhere in the repository compares against the C xxHash baseline, so the record has no evidence for a win over C.
- **Verifier notes:** Record is accurate: _compat.c only prints XXH3 test vectors from the upstream C library (Makefile builds it with plain gcc), compat_test.go checks Go output against those vectors, and internal/compare/compare_test.go benchmarks against cespare/xxhash (Go XXH64), not C. Even a future win would come from the avo-generated SSE2/AVX2/AVX512/NEON assembly accumulators rather than Go codegen. Shortcomings: no C baseline measured (tier D), Go version and flags unstated; metadata checked (BSD-2-Clause, 587 stars, last commit 2026-09-08, not a fork).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-117 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/zeebo/xxh3>
  - <https://github.com/zeebo/xxh3/commits/master>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/README.md>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/compat_test.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/_compat.c>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/internal/compare/compare_test.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/zeebo/xxh3>
  - <https://github.com/zeebo/xxh3/issues?q=is%3Aissue>
  - <https://github.com/zeebo/xxh3/pulls>
  - <https://github.com/zeebo/xxh3/commits/master>
  - <https://github.com/zeebo/xxh3/commits/master/README.md>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/README.md>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/go.mod>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/Makefile>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/hash64.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/hash64_seed.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/hash128.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/hash128_seed.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/hasher.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/hasher128.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/utils.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/consts.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/accum_generic.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/accum_stubs_amd64.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/accum_stubs_arm64.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/accum_stubs_other.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/hash64_test.go>
  - <https://raw.githubusercontent.com/zeebo/xxh3/HEAD/internal/compare/compare_test.go>
  - <https://raw.githubusercontent.com/go-simd/xxhash/HEAD/README.md>
  - <https://raw.githubusercontent.com/Cyan4973/xxHash/dev/README.md>
  - WebSearch: zeebo/xxh3 Go vs C xxHash XXH3 benchmark comparison cgo
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/zeebo/xxh3`) · [data/wave14/enrich/raw/github_com_zeebo_xxh3.json](../../../data/wave14/enrich/raw/github_com_zeebo_xxh3.json) (enrichment confidence 0.85)

</details>
