# klauspost/crc32 (2025 AVX-512 revival)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-3-Clause` · 🟡 stale

> Fork of Go's hash/crc32 adding an AVX-512 VPCLMULQDQ path that roughly doubles IEEE CRC32 throughput on inputs of 1 KB and up.

| | |
|---|---|
| **Beats** | CRC32 (Go standard library hash/crc32, IEEE polynomial - the same checksum family zlib's crc32() implements) |
| **Claimed result** | 2.09x-2.35x faster than the prior (SSE4/AVX2) implementation for 1KB-32KB inputs using AVX-512; no speedup below \~1KB |
| **Workload** | IEEE CRC32 checksum of buffers from 512B to 32KB, aligned and unaligned, Go benchmark suite |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X 16-Core Processor |
| **Compiler and flags** | Not stated. The README says the library is 'based on Go 1.24' (the source base) and go.mod declares go 1.23.0. The benchmark names (BenchmarkCRC32/...-32) indicate go test -bench with default settings, but no command or toolchain version is given. |
| **Adoption** | 84 stars |
| **Last commit** | 2025-07-22 |
| **Links** | [repository](https://github.com/klauspost/crc32) · [benchmark](https://raw.githubusercontent.com/klauspost/crc32/master/README.md) |

## Verdict

On an AMD Ryzen 9 9950X, go test -bench BenchmarkCRC32 (IEEE, 512 B-32 KB, aligned and offset-by-1 buffers) measured 45.6-48.6 GB/s for the AVX-512 path at 1-32 KB, against 19.9-21.9 GB/s for the stdlib-derived SSE4.1/PCLMULQDQ kernel it replaces (2.09x-2.35x), and 1.00x at 512 B and below. The Go toolchain version and flags are not stated. The author's upstream Go CL on the same CPU reported a similar 2.10x-2.44x.

## Use it when

- Go services on Go 1.23-1.25 that compute IEEE CRC32 (gzip, zip, PNG, Ethernet-style checksums) over buffers of 1 KB or more on x86-64 CPUs with AVX-512 VPCLMULQDQ
- Checksumming large blobs in single calls (file chunks, network payloads, object-store parts), where the author measured 45-48 GB/s against about 20-22 GB/s on a Ryzen 9 9950X
- When you want a pure-Go (no cgo) path that is bit-identical to hash/crc32, with the only change being the import line

## Skip it when

- You build with Go 1.26 or newer: the same AVX-512 IEEE code was merged into the standard library's hash/crc32 (golang/go commit 18dbe5b, present in go1.26.0, absent in go1.25.0), so this package adds nothing but a dependency
- CRC32C (Castagnoli) or Koopman workloads: the Castagnoli AVX-512 kernel ships disabled (an 'if false' guard, with a comment saying it is not significantly faster even on Zen 5), so those polynomials run at stdlib speed
- Short inputs or streaming with small Write calls: the AVX-512 path is chosen per call only when len(p) &gt;= 1024, so 15 B-512 B checksums and sub-1 KB chunked writes see 1.00x
- CPUs without AVX-512 (older x86, arm64, ppc64le, s390x, loong64): you get the stdlib-derived code paths and no speedup
- Code that needs hash.Cloner: the Go 1.25+/1.26 stdlib digest has a Clone() method and this package's digest does not

## How it is fast

It uses carry-less-multiply folding from Intel's 'Fast CRC Computation for Generic Polynomials Using PCLMULQDQ' paper, widened from 128-bit XMM to 512-bit ZMM registers. Each loop iteration folds 64 bytes with two VPCLMULQDQ ops and merges them with a three-way XOR in one VPTERNLOGD. The 512-bit accumulator is then split into four 128-bit lanes and handed to the existing SSE tail and Barrett reduction. Below 1024 bytes it falls back to the stdlib SSE4.1/PCLMULQDQ kernel, and to slicing-by-8 below 64 bytes.

## Compared with alternatives

Pick this when you are in Go, cannot move to Go 1.26 yet, and want CRC32 with no cgo. crc-fast (Rust core with a C API) and corsix/fast-crc32 (C kernels) are the choice for peak GB/s or CRC32C outside Go, and crc32fast is the Rust-native option. Their multi-stream kernels go well beyond this package's single-accumulator AVX-512 loop.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys (v0.34.0, used for CPU feature detection via x/sys/cpu) |
| **Minimum toolchain** | Go 1.23 (go.mod declares go 1.23.0; CI tests 1.23.x and 1.24.x) |
| **Platforms** | any Go target. The AVX-512 speedup needs x86-64 with AVX512F, AVX512VL and AVX512 VPCLMULQDQ. Other targets use stdlib-derived assembly (amd64 SSE4.1/SSE4.2/PCLMULQDQ, arm64, ppc64le, s390x, loong64) or a generic Go fallback. |
| **Thread safety** | Lazy table initialization is guarded by sync.OnceFunc and atomics, so Checksum/Update can be called concurrently. Each hash.Hash32 digest holds mutable state and, as in stdlib, should not be shared across goroutines; the README does not document this. |
| **Drop-in for the baseline** | partial: the README calls it a drop-in and the API and outputs match hash/crc32 for Go 1.23/1.24 code. However, crc32.Table is a distinct type, so tables cannot be shared with hash/crc32, and the Clone() method that stdlib digests gained in Go 1.25 is missing. |

## Gotchas

- The AVX-512 decision is made on each Update/Write call's length, not on the total stream length. A hash.Hash32 fed 512-byte chunks never uses the fast path, so batch writes into 1 KB+ slices.
- The README warns that AVX-512 'may be slower to ramp up' for cold or short bursts, and says the published benchmarks, which run hot back-to-back loops, do not show this.
- CI runs 'go test -tags=noasm', but no source file honors a noasm tag, so there is no build tag to force the portable path on amd64.
- The 2025 rebase onto Go 1.24 source dropped the old gccgo/App Engine build constraints (earlier PRs #8 and #12). Non-gc toolchains are not tested.

## Known shortcomings

- No Go version or flags stated (retiered A to C). The 'old' baseline is Go stdlib's SSE4.1/PCLMULQDQ path, not an AVX2 one; gains need AVX-512 (VPCLMULQDQ). Go-only.
- Superseded: the same AVX-512 IEEE code was merged into Go's stdlib hash/crc32 (golang/go 18dbe5b, shipped in go1.26.0), so it only helps projects pinned to Go 1.23-1.25. The Castagnoli AVX-512 kernel ships disabled (`if false`); a 1 KB gate per Write call means small chunked writes see no gain. Not a full drop-in (distinct Table type, no Clone()).

## Caveats and trade-offs

'Old' is the regular SSE4.1/PCLMULQDQ implementation (the README calls it 'the regular SSE4 implementation'), not AVX2. PR #20's first commit is 'Use latest go src as base', so Old is effectively the Go standard library hash/crc32 code, and New adds AVX-512 on top. AVX-512 turns on only above 1KB, and PR #20 shows \~1.00x at 15B, 40B and 512B. There is no comparison against zlib's C crc32(). The Go toolchain version is unstated.

Go-only drop-in for hash/crc32; AVX-512 only engages above \~1KB inputs; CRC32C (Castagnoli) gains are noted as smaller and not worth the downsides per README

## Maintenance

The last commit and v1.3.0 tag are from 2025-07-22. The same author got the identical change into Go's hash/crc32 two days later (in Go 1.26), so this BSD-3-Clause module now mainly serves projects pinned to Go 1.23-1.25 and is effectively superseded rather than abandoned.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README table (Old vs New MB/s, 2.09x-2.35x at 1kB-32kB) names the CPU (AMD Ryzen 9 9950X), and the benchmark code is public: BenchmarkCRC32 in crc32_test.go. Neither the README nor PR #20 states the Go toolchain version or the go test command and flags. 'Based on Go 1.24' describes the source base, and go.mod declares only go 1.23.0. Under the orchestrator's Go rule that makes these first-party numbers C, not A.
- **Verifier notes:** The numbers match the README and PR #20 exactly. The 'prior (SSE4/AVX2)' wording was wrong: the baseline is the upstream Go stdlib SSE4.1/PCLMULQDQ path. Metadata verified via gh: BSD-3-Clause (Go license), 84 stars, last commit 2025-07-22, stale.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/klauspost/crc32/master/README.md>
  - <https://github.com/klauspost/crc32>
  - <https://github.com/klauspost/crc32/pull/20>
  - <https://raw.githubusercontent.com/klauspost/crc32/master/crc32_test.go>
  - <https://raw.githubusercontent.com/klauspost/crc32/master/go.mod>
  - <https://raw.githubusercontent.com/klauspost/crc32/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/klauspost/crc32>
  - <https://github.com/klauspost/crc32/blob/master/README.md>
  - <https://github.com/klauspost/crc32/blob/master/crc32.go>
  - <https://github.com/klauspost/crc32/blob/master/crc32_amd64.go>
  - <https://github.com/klauspost/crc32/blob/master/crc32_amd64.s>
  - <https://github.com/klauspost/crc32/blob/master/crc32_test.go>
  - <https://github.com/klauspost/crc32/blob/master/crc32_otherarch.go>
  - <https://github.com/klauspost/crc32/blob/master/crc32_generic.go>
  - <https://github.com/klauspost/crc32/blob/master/go.mod>
  - <https://github.com/klauspost/crc32/blob/master/go.sum>
  - <https://github.com/klauspost/crc32/blob/master/.github/workflows/go.yml>
  - <https://github.com/klauspost/crc32/pull/20>
  - <https://github.com/klauspost/crc32/issues>
  - <https://github.com/klauspost/crc32/pulls>
  - <https://github.com/klauspost/crc32/tags>
  - <https://github.com/klauspost/crc32/releases>
  - <https://github.com/golang/go/commit/18dbe5b941>
  - <https://github.com/golang/go/blob/master/src/hash/crc32/crc32_amd64.go>
  - <https://github.com/golang/go/blob/go1.25.0/src/hash/crc32/crc32_amd64.s>
  - <https://github.com/golang/go/blob/go1.26.0/src/hash/crc32/crc32_amd64.s>
  - <https://github.com/golang/go/blob/go1.26.0/src/hash/crc32/crc32.go>
  - <https://github.com/golang/website/blob/master/_content/doc/go1.26.md>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/klauspost/crc32`) · [data/wave7/enrich/raw/github_com_klauspost_crc32.json](../../../data/wave7/enrich/raw/github_com_klauspost_crc32.json) (enrichment confidence 0.85)

</details>
