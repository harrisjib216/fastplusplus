# stdx-go ChaCha20 (Go simd/archsimd)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT (per LICENSE.txt and GitHub detection); the README contradicts this, saying 'The code is licensed under AGPL-3.0 (see LICENSE.txt)'` · 🟢 active

> Go ChaCha20 stream cipher written with experimental simd/archsimd (AVX2/AVX-512/NEON); claims 7.5x over x/crypto's scalar amd64 path.

| | |
|---|---|
| **Beats** | golang.org/x/crypto/chacha20 (the Go project's x/crypto module, not the std library proper). It is pure-Go scalar on amd64: the package has assembly only for arm64, ppc64x, s390x and loong64. |
| **Claimed result** | amd64: up to 7.5x at 1 MB (7,517.67 MB/s simd vs 1,005.23 MB/s stdlib) (derived from page data, headline '7.5x faster'); arm64: no gain, \~97% of stdlib speed (1,349.27 vs 1,390.28 MB/s at 1 MB) |
| **Workload** | ChaCha20 keystream/encrypt throughput at 64 B-1 MB inputs, single core, amd64 (AVX2/AVX-512) and arm64 (NEON) |
| **Metric** | throughput |
| **Hardware** | amd64: AMD EPYC Zen5 family (model unspecified); arm64: host CPU unspecified |
| **Compiler and flags** | Go 1.27 (per go.mod). GOAMD64=v4 GOEXPERIMENT=simd on amd64 and GOEXPERIMENT=simd on arm64, as reported from the blog (not re-verified). Run with `go test -bench=. -benchmem` on chacha20/bench_test.go. |
| **Adoption** | 3 stars |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/skerkour/stdx-go/tree/main/chacha20) · [benchmark](https://kerkour.com/golang-chacha20-encryption-simd-archsimd) |

## Verdict

The author's blog reports XORKeyStream on 1 MB at 7,517.67 MB/s against 1,005.23 MB/s for golang.org/x/crypto/chacha20 (about 7.5x). The CPU is named only as an AMD EPYC Zen5-family part, with Go 1.27, GOEXPERIMENT=simd and GOAMD64=v4. On an unnamed arm64 host the result is 1,349.27 against 1,390.28 MB/s, i.e. no gain. These page numbers were not re-verified because kerkour.com was not fetched, but the public bench_test.go matches the described setup: 64 B to 1 MB, with a fresh cipher per iteration for both sides. The amd64 baseline is x/crypto's pure-Go scalar fallback. Nothing was compared against OpenSSL, libsodium or existing SIMD Go ChaCha20 code such as aead/chacha20 (AVX2 assembly), which stdx-go itself vendors as crypto/chacha.

## Use it when

- Pure-Go (no cgo) code on amd64 that XORs large ChaCha20 keystreams, roughly 4 KiB and up, where the 8- and 16-block batches are fully used. Examples: bulk file or stream encryption.
- AVX-512 x86 servers such as Zen4/Zen5, where the 16-block path engages for inputs over 256 bytes. The 7.5x headline at 1 MB was measured on an AMD EPYC Zen5-family CPU.
- Building your own ChaCha20-based construction when you can pin Go 1.27+ with GOEXPERIMENT=simd. The repo's own ChaCha20-BLAKE3 Go port does exactly this.
- Protocols that need the original DJB ChaCha20 (64-bit counter, 8-byte nonce), which x/crypto/chacha20 does not expose.

## Skip it when

- Production or security-sensitive code. The author calls the code not production-ready, the repo README says 'NOT SAFE FOR PUBLIC USE', and there are no tagged releases.
- arm64 (Graviton, Apple silicon). x/crypto already has NEON assembly there, and the author's own numbers put this package at about 97% of x/crypto's speed.
- When you need authenticated encryption. There is no ChaCha20-Poly1305 or XChaCha20 here, so use golang.org/x/crypto/chacha20poly1305 or one of the AEAD siblings.
- Builds that must stay on stable Go without experiments. simd/archsimd is still experimental in Go 1.27, and the release notes say its API is 'not yet considered stable', so a later Go release can break this code.
- Messages of 64 bytes or less. They take the portable scalar path on every architecture, and no gain is documented for them.

## How it is fast

It generates many blocks at once with SIMD, written in Go's experimental simd/archsimd intrinsics rather than assembly. On amd64, the AVX-512 path computes 16 blocks (1 KiB) per iteration in a word-sliced layout, using VPROLVD rotates and a two-stage in-register transpose. The AVX2 path computes 8 blocks (512 B) in the column-major layout of the classic chachaAVX2_amd64.s: VPSHUFB byte shuffles do the 16- and 8-bit rotations, and the transpose is fused into the stores. arm64 uses a 4-block NEON path with VTBL rotations. The large amd64 gain exists mainly because x/crypto/chacha20 ships no amd64 assembly, so this is 8- to 16-way SIMD measured against one-block-at-a-time scalar Go.

## Compared with alternatives

All catalogued siblings are C or Rust AEADs (chacha20poly1305-simd, libaegis, the Rust ChaCha20-BLAKE3 and others), so pick this only when you need a raw ChaCha20 keystream in pure Go on amd64 without cgo. For an authenticated Go construction from the same author, use the repo's crypto/chacha20blake3, which wraps this package; for a standardized AEAD, stay with x/crypto/chacha20poly1305 or a sibling.

## Integration

| | |
|---|---|
| **Form** | module (package github.com/skerkour/stdx-go/chacha20 inside the multi-package stdx-go module); vendoring the 7 non-test source files as a source-drop is more practical |
| **Dependencies** | Standard library plus the experimental simd/archsimd package (GOEXPERIMENT=simd). Tests and benchmarks also import golang.org/x/crypto/chacha20. Requiring the module pulls in stdx-go's go.mod, which has 25 direct requirements (pgx, minio-go, quic-go, wazero and others), though the chacha20 package itself imports none of them. |
| **Minimum toolchain** | Go 1.27 (per go.mod), with GOEXPERIMENT=simd on amd64 and arm64. The blog run also used GOAMD64=v4; that detail was not re-verified. |
| **Platforms** | amd64: runtime dispatch picks AVX-512 for inputs over 256 B, AVX2 for inputs over 64 B, and scalar otherwise. arm64: NEON for inputs over 64 B. Every other GOARCH uses portable scalar Go. |
| **Thread safety** | Not documented. A Cipher is mutable stream state (the counter plus up to 63 bytes of buffered keystream), so use one instance per goroutine, as with x/crypto. |
| **Drop-in for the baseline** | partial — it implements cipher.Stream, and its tests check output against x/crypto/chacha20. But the constructors differ (NewIetf(key [32]byte, nonce [12]byte) returns a value with no error, versus NewUnauthenticatedCipher(key, nonce []byte) (\*Cipher, error)), there is no 24-byte XChaCha20 nonce, and SetCounter takes a uint64 and allows rollback. |

## Gotchas

- The amd64 and arm64 backend files import simd/archsimd with no goexperiment.simd build tag; only chacha20_test.go has one. Without GOEXPERIMENT=simd, the package should therefore fail to compile on those architectures instead of falling back to the scalar code.
- SetCounter lets you move the counter backward, while x/crypto's SetCounter panics on rollback to prevent accidental keystream reuse. Here, misuse silently reuses keystream.
- The tail of each call is always padded to a full SIMD batch. A 257-byte input on an AVX-512 CPU still computes 16 blocks (1 KiB) of keystream, and 65-511 bytes on AVX2 still computes 8 blocks, so gains at mid sizes are smaller than the 1 MB headline.
- The license is ambiguous: LICENSE.txt and GitHub say MIT, but the README says 'licensed under AGPL-3.0'. Settle this before vendoring.

## Known shortcomings

- The 7.5x is SIMD against x/crypto/chacha20's pure-Go scalar code on amd64 (no assembly there); on arm64, where x/crypto has NEON assembly, there is no gain. Only the author's blog with a CPU family, no model (retiered B to C). README says 'NOT SAFE FOR PUBLIC USE'; license conflict (LICENSE.txt MIT vs README AGPL-3.0).
- Needs Go 1.27 with the experimental GOEXPERIMENT=simd (unstable API); backend files lack the goexperiment build tag, so it likely does not build without it. Raw keystream only; SetCounter allows counter rollback (x/crypto panics); tail padded to a full 8/16-block batch. Untagged, 3 stars.

## Caveats and trade-offs

This is a first-party blog benchmark by the library's author. The CPU is named only as a family ('AMD EPYC Zen5'), and the arm64 host is not named. On amd64 the baseline golang.org/x/crypto/chacha20 has no SIMD assembly (pure-Go scalar code), so the 7.5x is SIMD against scalar code. On arm64, where x/crypto does have NEON assembly, the SIMD version shows no gain. It is not benchmarked against OpenSSL or libsodium. The package lives in a grab-bag repo that the README labels 'NOT SAFE FOR PUBLIC USE', and it needs the experimental GOEXPERIMENT=simd with Go 1.27. The license is conflicting: LICENSE.txt is MIT, but the README says AGPL-3.0.

Relies on Go's experimental `simd`/`simd/archsimd` packages (GOEXPERIMENT=simd), not part of stable Go; author explicitly marks the code 'NOT production-ready'; implements raw ChaCha20 only, not the ChaCha20-Poly1305 AEAD; arm64 SIMD path gives no real speedup over stdlib

## Maintenance

Actively developed: 15 commits to the chacha20 path from 2026-07-23 to 2026-08-24. It is untagged, has 3 stars, is self-described as not production-ready and depends on an experimental Go feature; it is small enough to vendor for experiments once the MIT-versus-AGPL license question is settled.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** These are first-party numbers from the author's own blog. The benchmark code is public (chacha20/bench_test.go, which runs golang.org/x/crypto/chacha20 against the SIMD version at 64 B to 1 MB), but the CPU is named only as a family, not a model. Nothing is peer-reviewed or independent, so tier B does not apply; this is C.
- **Verifier notes:** I did not fetch kerkour.com (the site asks not to be scraped), so the page numbers (7,517.67 vs 1,005.23 MB/s; 1,349.27 vs 1,390.28 MB/s) are not verified. HN item 49362187 carries the '7.5x faster encryption in Go' headline, and the repo bench confirms the x/crypto baseline and the input sizes. Metadata checked: MIT per GitHub, 3 stars, not a fork, last commit 2026-08-25 (the chacha20 path was last touched 2026-08-24).
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/skerkour/stdx-go>
  - <https://github.com/skerkour/stdx-go/tree/main/chacha20>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/bench_test.go>
  - <https://github.com/skerkour/stdx-go/blob/main/README.md>
  - <https://github.com/skerkour/stdx-go/blob/main/LICENSE.txt>
  - <https://github.com/skerkour/stdx-go/blob/main/go.mod>
  - <https://github.com/golang/crypto/tree/master/chacha20>
  - <https://hn.algolia.com/api/v1/items/49362187>
- **Sources the enricher read:**
  - <https://github.com/skerkour/stdx-go>
  - <https://github.com/skerkour/stdx-go/tree/main/chacha20>
  - <https://github.com/skerkour/stdx-go/blob/main/README.md>
  - <https://github.com/skerkour/stdx-go/blob/main/LICENSE.txt>
  - <https://github.com/skerkour/stdx-go/blob/main/go.mod>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/chacha20.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/chacha20_amd64.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/chacha20_avx512.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/chacha20_arm64.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/chacha20_generic.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/chacha20_simd.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/hchacha20.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/bench_test.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/chacha20_test.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/chacha20_ietf_test.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/chacha20_djb_test.go>
  - <https://github.com/skerkour/stdx-go/blob/main/chacha20/chacha20_djb_amd64_test.go>
  - <https://github.com/skerkour/stdx-go/blob/main/crypto/chacha20blake3/chacha20_blake3.go>
  - <https://github.com/skerkour/stdx-go/commits/main/chacha20>
  - <https://github.com/skerkour/stdx-go/issues>
  - <https://github.com/skerkour/stdx-go/tags>
  - <https://github.com/golang/crypto/tree/master/chacha20>
  - <https://github.com/golang/crypto/blob/master/chacha20/chacha_generic.go>
  - <https://github.com/golang/crypto/blob/master/chacha20/chacha_noasm.go>
  - <https://hn.algolia.com/api/v1/items/49362187>
  - <https://hn.algolia.com/api/v1/search?query=chacha20%20simd%20go&tags=story>
  - <https://go.dev/doc/go1.27>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/skerkour/stdx-go`) · [data/wave7/enrich/raw/github_com_skerkour_stdx_go.json](../../../data/wave7/enrich/raw/github_com_skerkour_stdx_go.json) (enrichment confidence 0.65)

</details>
