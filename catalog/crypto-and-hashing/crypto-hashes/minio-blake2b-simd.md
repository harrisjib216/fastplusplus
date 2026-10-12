# blake2b-simd (Minio)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🔴 abandoned

> Archived Go BLAKE2b with AVX2/AVX/SSSE3 assembly, about 4x its pure-Go fallback and faster than 2016-era Go SHA-256/SHA-512.

| | |
|---|---|
| **Beats** | The package's own pure-Go BLAKE2b fallback (compress_generic.go, derived from dchest/blake2b), labelled 'go.txt' in the benchcmp output. Also compared against Go stdlib crypto/md5, crypto/sha1, crypto/sha256 and crypto/sha512. |
| **Claimed result** | AVX2 is 3.94x faster than the pure-Go path at 128K (233.37 -&gt; 918.93 MB/s); the README calls this 'roughly 4X ... approaching 1GB/sec on a single core'. AVX is 3.28x and SSE 2.85x at 128K, on a MacBook Pro i7. In the comparison benchmark, BLAKE2b-simd runs at 850.64 MB/s vs stdlib SHA-256 at 189.58 MB/s (\~4.5x, derived from page data), SHA-512 at 306.33 MB/s and MD5 at 607.48 MB/s. |
| **Workload** | Size benchmarks hash 64B-128KB buffers on one core on amd64 (AVX2/AVX/SSE assembly vs the pure-Go path). The stdlib comparison benchmark hashes 1 MiB messages, written in 1 KiB chunks. |
| **Metric** | throughput |
| **Adoption** | 255 stars; used internally by Minio for bitrot detection in its erasure-coded object storage |
| **Last commit** | 2016-07-23 |
| **Links** | [repository](https://github.com/minio/blake2b-simd) · [benchmark](http://web.archive.org/web/20181010233948/https://blog.minio.io/accelerating-blake2b-by-4x-using-simd-in-go-assembly-33ef16c8a56b) |

## Verdict

These are first-party 2016 go test benchmarks with an unstated Go version (CI used Go 1.5/1.6). On a Xeon E5-2620 v3 the AVX2 path hashes 128 KiB at 918.93 MB/s versus 233.37 MB/s for the package's own pure-Go path (3.94x). AVX is 3.28x and SSE 2.85x on a 2.7 GHz MacBook Pro i7, with gains of only 1.7-1.9x at 64-128 B. A 1 MiB stdlib comparison on the Xeon gives 850.64 MB/s versus Go SHA-256 at 189.58, SHA-512 at 306.33 and MD5 at 607.48 MB/s, all before Go had SHA-NI or ARMv8 SHA acceleration.

## Use it when

- Legacy Go code that already imports it or dchest/blake2b, on amd64, where you want roughly 1.7x (64 B) to 3.9x (128 KiB) more BLAKE2b throughput with no API change.
- Bulk checksums or bit-rot checks of large buffers (8 KiB and up) on AVX2 x86-64, where the SIMD path is 3-4x the pure-Go path in the README tables.
- You need BLAKE2b's salt, personalization or tree-hashing parameters (as in bt2sum's tree mode). golang.org/x/crypto/blake2b only takes a size and a key.
- Reading or benchmarking a small, self-contained reference for how BLAKE2b maps onto AVX2/SSSE3 in Go assembly.

## Skip it when

- New code: the repo is archived, and the Minio maintainers said in 2018 (issues #29-#31) that they had switched to golang.org/x/crypto/blake2b. That package has its own AVX2/AVX/SSE4 assembly and adds BLAKE2Xb and state (un)marshalling.
- Non-amd64 targets such as arm64, Apple M1 or Graviton only get the generic Go code (the NEON request, issue #15, is still open). A 2021 HN user saw Go's hardware-accelerated SHA-1/SHA-256 reach about 2.5 GB/s on an M1, far above this package there.
- Machines without SSSE3 or AVX, such as the SSE2-only Celeron in issue #24, where it ran at the same speed as the cgo codahale/blake2. On an Atom C2750 (issue #11) the SSE path reached only 59 MB/s at 128 KiB.
- Small messages: the gain drops to 1.7-1.9x at 64-128 B, where per-call setup and finalization dominate.
- You need encoding.BinaryMarshaler state snapshots, BLAKE2Xb/XOF output, BLAKE2s, or a tagged, module-aware release. None exist here; pkg.go.dev shows only the pseudo-version v0.0.0-...-3f5f724 from 2016-07-23.

## How it is fast

The BLAKE2b compression function is hand-written in Go assembly. The AVX2 path follows Samuel Neves' blake2-avx2 code: one YMM register holds a whole 4x64-bit row, so each G step works on four columns at once, and VPERMQ does the diagonalize/undiagonalize. The AVX and SSE paths follow the reference BLAKE2 sse/blake2b.c and use two XMM registers per row. The 32/24/16-bit rotations are done with PSHUFB/VPSHUFB byte shuffles, and the 63-bit rotation with add+shift+xor. The loop over 128-byte blocks runs inside the assembly, and the CPU check (CPUID/XGETBV) runs once at package init to pick AVX2, then AVX, then SSSE3, then generic Go.

## Compared with alternatives

It is the only Go entry. blake2b_simd (oconnor663) is the Rust BLAKE2b to use outside Go, and BLAKE3 is much faster if you can change algorithms. Pick this over minio's own sha256-simd only when you need BLAKE2b digests on amd64 rather than SHA-256 compatibility or ARM64 acceleration.

## Integration

| | |
|---|---|
| **Form** | module (go get github.com/minio/blake2b-simd; no go.mod and no tagged releases, so it resolves to a 2016 pseudo-version) or source-drop (about 20 files) |
| **Dependencies** | none (Go standard library only) |
| **Minimum toolchain** | Go gc toolchain. CI tested only Go 1.5/1.6 on Travis and AppVeyor, and support for modern Go is not documented. It uses old-style '// +build' constraints. The .s files are pre-assembled into BYTE sequences, so building does not need asm2plan9s; that tool is only for editing the assembly. |
| **Platforms** | amd64 with runtime dispatch (AVX2 &gt; AVX &gt; SSSE3 &gt; pure Go). Every other architecture gets the pure-Go path. |
| **Thread safety** | not documented. hash.Hash values returned by New/New512/NewMAC hold mutable state (use one per goroutine). Sum512/Sum256 build a local digest on each call. |
| **Drop-in for the baseline** | partial: same API as dchest/blake2b, from which the pure-Go baseline comes, so swapping the import is enough. Against stdlib crypto/sha256 or crypto/sha512 it is only hash.Hash-compatible and gives different digests. |

## Gotchas

- The package name is blake2b but the import path ends in blake2b-simd, and it clashes with golang.org/x/crypto/blake2b. Importing both needs an alias, and the two have different constructor signatures: New512() here versus New512(key) (hash.Hash, error) in x/crypto.
- New(c) writes Size=64 back into the caller's Config when c.Size is 0, and NewMAC panics instead of returning an error for invalid sizes or keys.
- compress_amd64.go has no build constraint, while compress_noasm.go also defines compress under the 'noasm'/'appengine' tags. The documented '-tags noasm' escape hatch therefore looks like it would fail to compile on amd64, as would gccgo (cpuid.go is '!gccgo'). Not tested here.
- The README benchmark names (BenchmarkHash\*) no longer match benchmarks_test.go (BenchmarkSize\*), and nothing in the repo benchmarks it against x/crypto/blake2b. Issue #32 (2018) asking for that comparison is still open.

## Known shortcomings

- Go library, archived; last code change 2016-07-23. Baseline is its own pure-Go fallback and Go stdlib hashes (1 MiB messages), not OpenSSL; no Go version stated. Go's golang.org/x/crypto/blake2b has since gained its own AVX2 assembly.
- MinIO itself moved to golang.org/x/crypto/blake2b in 2018 (#29-#31); never benchmarked against x/crypto/blake2b (#32 open), OpenSSL or libb2. amd64 only: arm64/M1 falls back to pure Go (NEON request #15 open), and SSE2-only CPUs run no faster than codahale's package (#24).

## Caveats and trade-offs

Benchmarks compare only against the package's own pure-Go fallback and Go's stdlib hashes, not against OpenSSL or libb2 BLAKE2b. The stdlib SHA-256 baseline is from the 2016-era Go, before SHA-NI support, so its ratio is inflated compared with modern hardware or toolchains. The repo is archived by GitHub and the last commit on master is 2016-07-23 (pushed_at 2017-11-27). The Go compiler version is not stated for the benchmarks (CI tested Go 1.5/1.6). README benchmark names (BenchmarkHash\*) differ from the current test file (BenchmarkSize\*). All numbers are first-party.

Requires AVX2/AVX/SSE (auto-selects, falls back to generic); Go-assembly implementation increases maintenance burden; BLAKE2b is a different digest/algorithm than SHA-2, not a drop-in replacement where SHA-2 compliance (e.g. FIPS) is required.

## Maintenance

Archived. The last code commit was 2016-07-23, and Minio itself moved to golang.org/x/crypto/blake2b in 2018. It is Apache-2.0, tiny and dependency-free, and pkg.go.dev still lists 314 known importers, so it is safe to vendor but should not be chosen for new work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README shows first-party benchcmp tables comparing the AVX2, AVX and SSE assembly paths against the package's own pure-Go path (AVX2 is 3.94x at 128K on a Xeon E5-2620 v3). It also has a go test -bench=Comparison table against Go stdlib MD5, SHA-1, SHA-256 and SHA-512 (BLAKE2b 850.64 MB/s vs SHA-256 189.58 MB/s). The benchmark code is public (benchmarks_test.go) and the CPU is named, but the Go toolchain version and flags are not stated, so this is C, not A.
- **Verifier notes:** The claimed numbers match the README exactly. The only real metadata fix is last_commit: the commits API gives 2016-07-23, and 2017-11-27 is the repo's pushed_at. The repo is Apache-2.0, archived, not a fork, with 255 stars.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/minio/blake2b-simd/master/README.md>
  - <https://github.com/minio/blake2b-simd>
  - <https://github.com/minio/blake2b-simd/blob/master/benchmarks_test.go>
  - <https://github.com/minio/blake2b-simd/blob/master/.travis.yml>
- **Sources the enricher read:**
  - <https://github.com/minio/blake2b-simd>
  - <https://raw.githubusercontent.com/minio/blake2b-simd/master/README.md>
  - <https://github.com/minio/blake2b-simd/blob/master/blake2b.go>
  - <https://github.com/minio/blake2b-simd/blob/master/compress_amd64.go>
  - <https://github.com/minio/blake2b-simd/blob/master/compress_noasm.go>
  - <https://github.com/minio/blake2b-simd/blob/master/compress_generic.go>
  - <https://github.com/minio/blake2b-simd/blob/master/compressAvx2_amd64.go>
  - <https://github.com/minio/blake2b-simd/blob/master/compressAvx2_amd64.s>
  - <https://github.com/minio/blake2b-simd/blob/master/compressAvx_amd64.go>
  - <https://github.com/minio/blake2b-simd/blob/master/compressAvx_amd64.s>
  - <https://github.com/minio/blake2b-simd/blob/master/compressSse_amd64.go>
  - <https://github.com/minio/blake2b-simd/blob/master/compressSse_amd64.s>
  - <https://github.com/minio/blake2b-simd/blob/master/cpuid.go>
  - <https://github.com/minio/blake2b-simd/blob/master/cpuid_amd64.s>
  - <https://github.com/minio/blake2b-simd/blob/master/cpuid_386.s>
  - <https://github.com/minio/blake2b-simd/blob/master/benchmarks_test.go>
  - <https://github.com/minio/blake2b-simd/blob/master/blake2b_test.go>
  - <https://github.com/minio/blake2b-simd/blob/master/.travis.yml>
  - <https://github.com/minio/blake2b-simd/blob/master/appveyor.yml>
  - <https://github.com/minio/blake2b-simd/issues?q=is%3Aissue>
  - <https://github.com/minio/blake2b-simd/issues/11>
  - <https://github.com/minio/blake2b-simd/issues/15>
  - <https://github.com/minio/blake2b-simd/issues/24>
  - <https://github.com/minio/blake2b-simd/pull/26>
  - <https://github.com/minio/blake2b-simd/issues/27>
  - <https://github.com/minio/blake2b-simd/pull/29>
  - <https://github.com/minio/blake2b-simd/issues/30>
  - <https://github.com/minio/blake2b-simd/issues/31>
  - <https://github.com/minio/blake2b-simd/issues/32>
  - <https://github.com/golang/crypto/tree/master/blake2b>
  - <https://github.com/golang/crypto/blob/master/blake2b/blake2b.go>
  - <https://github.com/golang/crypto/blob/master/blake2b/blake2bAVX2_amd64.go>
  - <https://github.com/dchest/blake2b/blob/master/blake2b.go>
  - <https://pkg.go.dev/github.com/minio/blake2b-simd>
  - <https://pkg.go.dev/github.com/minio/blake2b-simd?tab=importedby>
  - https://hn.algolia.com/api/v1/search?query=minio%20blake2b&tags=(story,comment)
  - <https://news.ycombinator.com/item?id=28382712>
  - https://blog.min.io/accelerating-blake2b-by-4x-using-simd-in-go-assembly/ (redirected to the blog index; post not retrieved)
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/minio/blake2b-simd`) · [data/wave7/enrich/raw/github_com_minio_blake2b_simd.json](../../../data/wave7/enrich/raw/github_com_minio_blake2b_simd.json) (enrichment confidence 0.8)

</details>
