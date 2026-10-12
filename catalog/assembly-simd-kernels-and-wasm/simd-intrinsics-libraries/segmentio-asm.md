# segmentio/asm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT-0` · 🟡 stale

> Go assembly (avo-generated AVX2) kernels for ASCII case-folding, byte swapping, fixed-size-key sort and base64; 6-13x over the package's pure-Go fallbacks.

| | |
|---|---|
| **Beats** | the package's own pure-Go fallback implementations of the same functions, selected with the purego build tag (Makefile benchcmp target runs go test -bench with -tags purego as 'old' and without it as 'new'); for ascii a table-lookup unrolled EqualFoldString, for bswap an encoding/binary loop, for qsort the package's Go quicksort128 with Hoare partition. Not Go stdlib functions (strings.EqualFold, sort.Slice); no stdlib numbers are published. |
| **Claimed result** | README showcase on an i9-8950HK: ascii EqualFoldString/0512 276 ns to 21 ns (-92.50%, 3.71 GB/s to 49.44 GB/s); bswap Swap64 11.2 us to 0.9 us (-92.06%, 5.83 GB/s to 73.67 GB/s); qsort Sort16/1000000 269 ms to 46 ms (-83.08%, 59.4 MB/s to 351.2 MB/s). |
| **Workload** | SIMD and branchless Go assembly (generated with avo) for ASCII case-insensitive comparison, byte swapping over arrays, quick sort of fixed-size items, base64, memory and sorted-set helpers. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-8950HK CPU @ 2.90GHz, macOS (darwin/amd64) |
| **Compiler and flags** | go test -run _ -count 5 -bench, once with -tags purego and once without, compared with benchstat (Makefile benchcmp target; p=0.008 n=5+5). Go version not stated (showcase committed 2021-09-14; go.mod now says go 1.18). |
| **Adoption** | 928 stars; used in production at Segment |
| **Last commit** | 2023-11-07 |
| **Links** | [repository](https://github.com/segmentio/asm) · [benchmark](https://github.com/segmentio/asm) |

## Verdict

A first-party benchstat snapshot (2021, i9-8950HK, macOS amd64, Go version not stated, n=5) compares each function's assembly build against the same package built with -tags purego: EqualFoldString on 512-byte equal strings 276 ns to 21 ns (about 13x), Swap64 on a 64 KiB buffer 11.2 us to 0.9 us (about 12.6x), and Sort16 on 1,000,000 random 16-byte keys 269 ms to 46 ms (about 5.8x). No Go standard library function (strings.EqualFold, sort.Slice) appears in the published numbers, and the Sort16 gain also comes from a different partition algorithm and the AVX2 byte-swap passes, not only from SIMD compares.

## Use it when

- Go services on amd64 with AVX2 that compare many ASCII header names, keys or tokens case-insensitively, at 16 bytes or more per string
- Converting large big-endian arrays of uint64 (wire formats, Parquet/Arrow-style columns) to little-endian in place
- Sorting millions of fixed-width binary keys (8, 16 or 32-byte IDs, UUIDs, hashes) stored contiguously in a []byte, by memcmp order, with no swap callback
- Hot paths where the inputs are batches of values, since the README says the functions are built for arrays

## Skip it when

- Unicode text: ascii.EqualFold compares non-ASCII bytes exactly, so it disagrees with strings.EqualFold on UTF-8 case pairs
- arm64 or other non-amd64 targets for ascii, bswap and qsort: these packages have amd64 assembly only and fall back to Go (base64 does have arm64 assembly)
- Short strings or single small calls: below 16 bytes EqualFoldString uses its scalar table path, and Go assembly functions are never inlined
- Adversarial or untrusted sort input: qsort is plain median-of-three quicksort with no heapsort fallback, so it is quadratic in the worst case
- Projects that need active maintenance or support for current Go releases: code last changed May 2022 and CI ran only Go 1.17 and 1.18

## How it is fast

EqualFoldString compares 128 bytes per loop with AVX2: it XORs the two inputs, builds a mask of positions where the byte is a letter and differs only in bit 0x20, and checks with one VPMOVMSKB per block, finishing with an overlapping 16-byte tail load. Swap64 uses VPSHUFB over four 32-byte registers per iteration. qsort byte-swaps the buffer once so keys compare as native qwords, then runs a quicksort whose partition is the branchless hybrid Lomuto/Hoare 'distribute' scheme from the reverberate.org bubble-sort post (CMOV plus VPCMPEQQ/VPCMPGTQ over 1 KB of stack scratch), finishing runs of 16-32 items with a branchless two-at-a-time bubble sort (8-byte keys) or an assembly insertion sort (16 and 32-byte keys).

## Compared with alternatives

vek, kelindar/simd and tphakala/simd target numeric float/int vector math in Go; pick segmentio/asm when the hot path is byte-level work such as ASCII case-insensitive comparison, endian swapping, sorting packed fixed-width binary keys or base64.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys (CPU feature detection); avo only in the separate build module for regenerating assembly |
| **Minimum toolchain** | Go 1.17+ (go.mod says go 1.18; v1.1.5 is the last release for Go 1.16) |
| **Platforms** | amd64 with runtime AVX2/AVX/CMOV dispatch for ascii, bswap and qsort; base64 also has arm64 assembly; any other platform uses the pure-Go fallback |
| **Thread safety** | not documented; the functions keep no state, but qsort.Sort and bswap.Swap64 rewrite the caller's buffer in place (Sort byte-swaps the whole buffer and swaps it back at the end) |
| **Drop-in for the baseline** | partial — ascii.EqualFoldString has the strings.EqualFold signature but ASCII-only semantics; base64 mirrors encoding/base64 but only accepts the standard, URL and IMAP alphabets; qsort and bswap have no stdlib equivalent with the same interface |

## Gotchas

- Builds with GO111MODULE=off or some vendored/GOPATH setups fail to link with "undefined reference to github.com/segmentio/asm/cpu.X86" (issues #73 and #81, both open); turning modules on or building with -tags purego avoids it.
- The showcase GB/s figures are inflated by the harness: BenchmarkEqualFoldString calls SetBytes(len(lower)+len(upper)), so 49.44 GB/s counts both 512-byte inputs (about 24.7 GB/s per string); Swap64 runs in place on a 64 KiB buffer that stays in L2, so 73.67 GB/s is cache bandwidth, not memory bandwidth. The time ratios are unaffected.
- The sort benchmarks have more broken rows than the verifier listed: stdlibSort8PartiallySorted allocates make([]int64, size) and then appends the partitions, so copy(data, partiallyOrdered) copies only the zero-filled prefix and the 'partially-sorted' sort.Slice rows sort an all-zero array; the dead partiallyOrdered branch of benchSort fills nothing, sorts each partition as a single element and appends it after the random prefix that copy() actually uses; stdlibSort8 draws keys from [0, size/10) as signed int64, unlike the random bytes BenchmarkSort8 sorts, so the two are not comparable even if published. BenchmarkSort32 (size 0) measures nothing.
- qsort.Sort sorts big-endian byte order, panics if len(data) is not a multiple of size, and drops to the slower Hoare partition whenever a swap callback is passed (the hybrid assembly path needs swap == nil); sizes other than 8, 16, 24 and 32 fall back to sort.Sort with bytes.Compare.

## Known shortcomings

- Baseline is the package's own purego fallback, not the Go standard library; Go version unstated; 2021 laptop snapshots (i9-8950HK); the qsort win mixes SIMD with a different hybrid-partition algorithm; EqualFold is ASCII-only; Go-only, not callable from C++. Harness defects outside the showcased rows: BenchmarkSort32 passes size 0 (times nothing) and the partially-ordered Sort8 setup never runs. MIT-0 without patent grant; last commit 2023-11-07.
- The baseline is only the project's own purego fallback, and the Sort16 gain also comes from a different partition scheme plus AVX2 bswap passes. Harness flaws: BenchmarkEqualFoldString's SetBytes counts both inputs, so 49.44 GB/s is about 24.7 GB/s per string; Swap64 runs on a 64 KiB buffer that stays in L2; stdlibSort8PartiallySorted copies only a zero-filled prefix, so it sorts an all-zero array, the dead partiallyOrdered branch is also broken, and stdlibSort8's keys come from [0, size/10), so it is not comparable to Sort8 (the time ratios are unaffected). Builds under GO111MODULE=off or some vendored setups fail to link on cpu.X86 (#73, #81); the quicksort has no heapsort fallback, so the worst case is quadratic.

## Caveats and trade-offs

Three hand-picked first-party snapshots from 2021 on one laptop CPU (i9-8950HK, darwin/amd64); Go version not stated. The baseline is the project's own pure-Go fallback (purego tag), not the Go standard library; a BenchmarkStdlibSort8 (sort.Slice) exists in qsort/sort_test.go but its numbers are not published. The qsort win mixes SIMD with a different algorithm (hybrid Lomuto/Hoare partition from the reverberate.org blog) that the purego path does not use; qsort assembly is amd64-only. ascii.EqualFold is ASCII-only and not semantically equal to strings.EqualFold. Harness defects outside the showcase: BenchmarkSort32 calls benchSort(count, 0, 32, ...) so element size is 0 and Sort returns immediately (measures nothing), and the 'partially-ordered' Sort8 sub-benchmarks pass order=random so the partial-ordering setup never runs. Go assembly library, not callable from C++. Last commit 2023-11-07 is a licence change (MIT to MIT-0); code last changed 2022-05. MIT-0 gives no explicit patent grant.

Assembly generated by avo through a separate build module; a generic Go implementation is used when no assembly exists for the target platform; qsort works on arrays of fixed-size items.

## Maintenance

Stale: code last changed May 2022, the last commit (Nov 2023, v1.2.1) only relicensed MIT to MIT-0, and 9 issues are open including the cpu.X86 link failure; small, permissively licensed (MIT-0, no patent grant) and pulled in transitively by large Go projects (issue #73 cites a vendored Grafana 8.5 build), so still usable as a dependency or vendored source.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README Showcase (added 2021-09-14) gives benchstat deltas on a named CPU (i9-8950HK) from public benchmark code (ascii/ascii_test.go BenchmarkEqualFoldString, bswap/swap64_test.go BenchmarkSwap64, qsort/sort_test.go BenchmarkSort16) run via the Makefile benchcmp target, but the Go toolchain version is not stated, so it falls short of A; no independent measurement found.
- **Verifier notes:** README numbers match the record exactly (EqualFoldString/0512 276 ns to 21 ns, Swap64 11.2 us to 0.9 us, Sort16/1000000 269 ms to 46 ms). 'old' is the purego build of the same package (baseline is a scalar Go reference, fits the category's scalar-reference baseline). Metadata confirmed on github.com: MIT-0, 928 stars, not archived or a fork, last commit 2023-11-07 (stale). Shortcomings to record: own-fallback baseline only, Go version unstated, degenerate BenchmarkSort32 and never-run partially-ordered setup in qsort benchmarks, Go-only (not C++).
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-50 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/segmentio/asm>
  - <https://github.com/segmentio/asm/commits>
  - <https://github.com/segmentio/asm/commits/main/README.md>
  - <https://github.com/segmentio/asm/tree/main/ascii>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/README.md>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/go.mod>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/ascii/ascii_test.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/ascii/equal_fold.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/ascii/equal_fold_default.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/bswap/swap64.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/bswap/swap64_default.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/bswap/swap64_test.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort_amd64.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort_default.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort_test.go>
- **Sources the enricher read:**
  - <https://github.com/segmentio/asm>
  - <https://github.com/segmentio/asm/commits/main>
  - <https://github.com/segmentio/asm/tags>
  - <https://github.com/segmentio/asm/issues?q=is%3Aissue>
  - <https://github.com/segmentio/asm/issues/81>
  - <https://github.com/segmentio/asm/issues/73>
  - <https://github.com/segmentio/asm/issues/80>
  - <https://github.com/segmentio/asm/issues/50>
  - <https://github.com/segmentio/asm/pull/74>
  - <https://github.com/segmentio/asm/tree/main/base64>
  - <https://github.com/segmentio/asm/tree/main/build>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/README.md>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/go.mod>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/build/go.mod>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/.github/workflows/go.yml>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/cpu/cpu.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/ascii/ascii.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/ascii/ascii_test.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/ascii/equal_fold.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/ascii/equal_fold_default.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/ascii/equal_fold_amd64.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/ascii/equal_fold_amd64.s>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/bswap/swap64.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/bswap/swap64_default.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/bswap/swap64_test.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/bswap/swap64_amd64.s>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort_amd64.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort_amd64.s>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort_default.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort16.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort8.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/generic.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/qsort/sort_test.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/base64/base64.go>
  - <https://raw.githubusercontent.com/segmentio/asm/HEAD/base64/encode_amd64.go>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/segmentio/asm`) · [data/wave13/enrich/raw/github_com_segmentio_asm.json](../../../data/wave13/enrich/raw/github_com_segmentio_asm.json) (enrichment confidence 0.78)

</details>
