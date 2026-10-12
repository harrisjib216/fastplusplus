# tmthrgd/go-hex (SSE/AVX assembly hex)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (SSE4.1/AVX assembly)` · `BSD-3-Clause` · 🔴 abandoned

> Go hex encode/decode with SSE4.1/AVX assembly; about 19x encoding/hex on encode and 4.6x on decode against current stdlib.

| | |
|---|---|
| **Beats** | Go standard library encoding/hex |
| **Claimed result** | Independent 2026 re-measurement (go-simd/hex README, 1 MiB random buffer, GitHub Actions ubuntu runner): go-hex encode about 19x and decode about 4.57x the current encoding/hex (Go 1.19+ reverseHexTable decoder). README benchmark table (committed 2016-11-11, Go 1.7 era; unknown CPU, GOMAXPROCS 8): Encode/1k 11572.80 vs encoding/hex 451.49 MB/s (25.63x); Decode/1k 6093.43 vs 245.43 MB/s (24.83x); encode 2.08x (15 B) to 31.17x (16k), decode 4.26x (14 B) to 44.70x (128k); Encode/128M 10.49x; Decode/128M 37.56x; the decode rows were measured against Go 1.7's branchy fromHexChar and no longer hold. |
| **Workload** | Hex encode and decode of 14 or 15 bytes up to 128 MB buffers. |
| **Metric** | throughput |
| **Adoption** | 26 stars, 2 forks; archived 2025-09-11 (repo description says '[Abandoned]'); a pinned dependency of go-simd/hex (go.mod), and search results show it vendored in GoToSocial's tree (snippet only) |
| **Last commit** | 2019-09-04 |
| **Links** | [repository](https://github.com/tmthrgd/go-hex) · [benchmark](https://github.com/tmthrgd/go-hex) |

## Verdict

The README table (committed 2016-11-11, unknown CPU, GOMAXPROCS 8, Go 1.7 era since sub-benchmarks appear) compares BenchmarkEncode/Decode against BenchmarkRefEncode/RefDecode on encoding/hex with identical setups: encode 2.08x at 15 B to 31.17x at 16 KiB and 10.49x at 128 MiB; decode 4.26x at 14 B to 44.70x at 128 KiB. A 2026 run by the competing go-simd/hex project (1 MiB random buffer, GitHub Actions AMD EPYC, GOAMD64=v1, median of 6) puts it at 18785 vs 980 MB/s encode (19.2x) and 9566 vs 2095 MB/s decode (4.57x) against current encoding/hex.

## Use it when

- amd64 services that hex-encode a lot of data (hash digests, IDs, bytea columns, logging of binary blobs): encode stays about 19x the current stdlib at 1 MiB in a 2026 third-party run (18785 vs 980 MB/s).
- Bulk hex decoding of trusted or untrusted input on amd64, where it is still about 4.6x the Go 1.19+ table-driven stdlib decoder at 1 MiB (9566 vs 2095 MB/s in the same run).
- Inputs from about 32 bytes up; the 2016 README shows 6x encode at 32 B but only 2.08x at 15 B, where call and tail overhead dominate.
- Code that needs uppercase output or a custom 16-character alphabet without a second pass (EncodeUpper, RawEncode).

## Skip it when

- arm64 (Graviton, Apple Silicon), ppc64le and other non-amd64 targets: decode falls back to the branchy Go 1.7-era fromHexChar switch, which is slower than Go 1.19+ encoding/hex (go-simd/hex measured about 9.7x slower on arm64), and encode is plain scalar.
- Code that relies on stdlib error semantics: odd-length input is rejected before any validation, errors are go-hex's own unexported errLength and InvalidByteError types (errors.Is(err, hex.ErrLength) from encoding/hex never matches), and Decode returns 0 bytes on error while having already written earlier blocks to dst; stdlib returns the count decoded before the error.
- Streaming use: there is no NewEncoder/NewDecoder, Dump/Dumper, AppendEncode or AppendDecode; the author's own issue #2 lists the missing upstream changes and it was never done.
- New projects that can take a maintained dependency: the repo is archived (2025-09-11) and labelled abandoned, with no go.mod; go-simd/hex is a maintained, error-identical alternative with AVX2 kernels that reports 1.37x faster decode than this package on the same CI run.
- AVX2/AVX-512 hardware where you want the last 30%: the 'AVX' path is VEX-encoded 128-bit code, not 256-bit.

## How it is fast

Encode uses Wojciech Mula's nibble-split technique: per 16 input bytes, PSRLW/PAND split high and low nibbles, PUNPCKLBW/PUNPCKHBW interleave them, and PSHUFB looks each nibble up in the alphabet held in a register, giving 32 output characters with no branches. Decode handles 16 characters per iteration: it lower-cases with OR 0x20, validates all lanes with signed PCMPGTB range checks after an 0x80 bias, folds the result to one PMOVMSKB/TEST branch, converts with PSUBB plus a masked 0x27 correction for letters, and packs nibble pairs with PSHUFB, PSLLW and POR into 8 output bytes. Tails under 16 bytes are handled in-register with PINSR/PEXTR sequences, so nothing reads or writes past the slices.

## Compared with alternatives

Pick it over seelabs/nasm (AVX2 NASM hex for fixed 256-bit values, aimed at C++/rippled) when you are in Go and need arbitrary-length buffers with validation; within the catalogued Go assembly entries it is the only hex codec. Against the uncatalogued go-simd/hex it wins only on existing adoption (118 known importers on pkg.go.dev, including go-pg, uptrace/bun and Hyperledger Burrow).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys/cpu (unpinned: the repo has no go.mod) |
| **Minimum toolchain** | Go gc toolchain; Travis tested Go 1.10-1.13; amd64 assembly is Plan 9 syntax with the generator asm_gen.go kept for maintainers only |
| **Platforms** | amd64 with AVX or SSE4.1 for the SIMD paths (Go fallback below SSE4.1 since 14226a5, 2018-11-01); any other Go target via scalar code |
| **Thread safety** | Stateless functions with read-only package tables; safe for concurrent use on distinct buffers (not stated in docs, follows from the code). |
| **Drop-in for the baseline** | partial - Encode/Decode/EncodeToString/DecodeString have the same signatures and identical output on valid input, but error types, partial-result counts and odd-length handling differ, and the streaming and Append APIs are missing |

## Gotchas

- The README decode ratios (24.83x at 1 KiB, 44.70x at 128 KiB, 37.56x at 128 MiB) were measured on 2016-11-11 against Go 1.7's branchy fromHexChar decoder; Go 1.19 replaced it with a reverseHexTable lookup, and the 2026 third-party run shows only 4.57x. Only the encode gap (stdlib encode is still a scalar table loop) has held up, at about 19x.
- In the README the stdlib decode rate falls from about 250 MB/s at 1 KiB and below to 144 MB/s from 16 KiB up while go-hex stays near 6.4 GB/s; this is consistent with the branch predictor memorising the small buffers the benchmark loop repeats (inference, not measured), so the 44x peaks reflect a mispredicting 2016 baseline on random hex.
- The decode benchmarks build their input with an overlapping in-place Encode(src, src[:m]). That yields a valid encoding of random bytes only because the amd64 kernel walks backwards in 16-byte blocks; on the Go fallback (non-amd64 or pre-SSE4.1) the forward loop overwrites unread input and produces an all-digit string after the first two characters, so decode numbers reproduced off amd64 time a degenerate, perfectly predictable input.
- Panics with 'dst buffer is too small' instead of an index error when dst is short, and DecodeString copies the string to a []byte before decoding; the author tried the stdlib's allocation-saving DecodeString change and saw it benchmark slower (issue #2), so the extra allocation stays.

## Known shortcomings

- README numbers (25.63x encode, 24.83x decode at 1k) are from 2016-11-11 with CPU and Go version unstated; an independent 2026 go-simd/hex CI run (competitor, 1 star, EPYC model unstated) against the current stdlib gives encode 19.2x but decode only 4.57x (stdlib Decode now uses reverseHexTable), so the 25-45x decode claim is stale; the non-amd64 fallback is slower than the current stdlib (arm64 decode about 9.7x slower); AVX/SSE4.1 128-bit only; archived 2025-09-11.
- Decode baseline stale: the README 25-45x decode ratios ran against Go 1.7's branchy fromHexChar; the stdlib moved to a reverseHexTable in Go 1.19, and the 2026 third-party run shows 4.57x (encode holds at about 19x). Harness quirk: the decode input comes from an overlapping in-place Encode that is valid only because the amd64 kernel walks backward; the Go fallback produces all-digit input (simulated). The reference decode drops from 250 to 144 MB/s at 16K+ (likely branch-predictor learning on small buffers; inference). Error semantics differ from the stdlib (unexported errLength, returns 0 on error, odd length checked first); the arm64 fallback is slower than the stdlib; 118 known importers (go-pg, uptrace/bun, Hyperledger Burrow).

## Caveats and trade-offs

The README numbers were committed on 2016-11-11 (Go 1.7 era), not about 2017. CPU model, Go version and flags are not given; only GOMAXPROCS 8 can be read from the -8 suffix. The asm was regenerated afterwards without re-running the table (go1.8/go1.10 updates, PEXTRB workaround 77b1f74, AVX/SSE split, pre-SSE4.1 fallback). None of those commits is a correctness fix of the measured path. Current golang/go encoding/hex Decode uses a reverseHexTable lookup, and stdlib throughput has risen since then. The independent go-simd/hex CI run (competitor package, 1 star, CPU model not given) measures only 4.57x for decode and 19.2x for encode at 1 MiB against current stdlib, so the README's 25-45x decode ratios are stale. Only amd64 builds get SIMD: dispatch is on AVX or SSE4.1, not AVX2, so the kernels are 128-bit. Non-amd64, gccgo and appengine builds use hex_other.go, the old Go-Authors scalar code. go-simd/hex reports that path's arm64 decode as about 9.7x slower than its own fallback, which tracks encoding/hex, so it is slower than the stdlib there. The decode benchmark input is built by an overlapping in-place Encode; it is still valid hex and identical for both rows. The repo is archived and called abandoned by its author, so no fixes will come. Licence is BSD-3-Clause. asm_gen.go also carries Wojciech Mula's Simplified BSD (BSD-2) notice, and hex.go/hex_other.go carry the Go Authors' BSD notice, all OSI. [retier] The README numbers were committed on 2016-11-11 (Go 1.7 era); CPU model, Go version and flags are not given. The decode ratios (24.83x to 44.70x) ran against Go 1.7's branchy fromHexChar decoder; Go 1.19 replaced it with a reverseHexTable lookup, and the 2026 independent run shows only about 4.57x, while the encode gap (the stdlib encode is still a scalar table loop) holds at about 19x. In the README the stdlib decode rate falls from about 250 MB/s at 1 KiB and below to 144 MB/s from 16 KiB up while go-hex stays near 6.4 GB/s, consistent with the branch predictor memorising the small buffers the benchmark loop repeats (inference), so the 44x peaks reflect a mispredicting 2016 baseline on random hex. The decode benchmarks build their input with an overlapping in-place Encode(src, src[:m]), valid only because the amd64 kernel walks backwards; on the Go fallback (non-amd64 or pre-SSE4.1) the forward loop overwrites unread input and produces an all-digit string, so decode numbers reproduced off amd64 time a degenerate input. The asm was regenerated afterwards without re-running the table (go1.8/go1.10 updates, PEXTRB workaround 77b1f74, AVX/SSE split, pre-SSE4.1 fallback), none a correctness fix of the measured path. Error semantics differ from the stdlib (unexported errLength, returns 0 on error, odd length checked first); DecodeString copies the string before decoding (issue #2); the arm64 fallback is slower than the stdlib. 118 known importers (go-pg, uptrace/bun, Hyperledger Burrow).

amd64 only with SSE4.1/AVX paths and Go fallback; repository is marked abandoned and read-only.

## Maintenance

Archived 2025-09-11 and labelled abandoned by its author (last code change 2018-11-01, Go fallback for pre-SSE4.1 CPUs), yet BSD-3-Clause (with Wojciech Mula's BSD-2 and the Go Authors' BSD notices), widely imported (118 known importers) and correct on every input byte at every position in its own exhaustive invalid-byte test, so it is safe to keep on amd64 but not worth adopting on arm64.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table against encoding/hex. The benchmark code is public (hex_test.go: BenchmarkEncode/BenchmarkRefEncode and BenchmarkDecode/BenchmarkRefDecode, with identical setups calling ref "encoding/hex"), but no CPU model, Go version or flags are given, so it is tier C. An independent 2026 CI run in go-simd/hex (a competing 1-star package, CPU model not given) corroborates the win, but it is not a well-known suite and does not lift the tier.
- **Verifier notes:** The README numbers match the record. The README itself prints the speedup column, so the ratios are first-party rather than derived. The main shortcoming: the numbers are from 2016 on an unstated CPU and Go version, and a 2026 third-party run (go-simd/hex README, competitor) shows decode is only 4.57x faster than today's encoding/hex, not 25-44x; encode stays about 19x. The non-amd64 fallback is slower than the current stdlib. This is not a duplicate of any catalog entry (no prior go-hex or go-simd/hex record found in data/).
- **Fields the verifier corrected:** `claimed_speedup`, `compared_against_cpp_std_directly`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-39 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tmthrgd/go-hex>
  - <https://github.com/tmthrgd/go-hex/commits>
  - <https://github.com/tmthrgd/go-hex/commits/master>
  - <https://github.com/tmthrgd/go-hex/commits/master/README.md>
  - <https://github.com/tmthrgd/go-hex/commit/77b1f74>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/README.md>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/hex_test.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/hex_amd64.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/hex.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/hex_other.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/asm_gen.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/golang/go/master/src/encoding/hex/hex.go>
  - <https://github.com/go-simd/hex>
  - <https://raw.githubusercontent.com/go-simd/hex/HEAD/README.md>
  - <https://raw.githubusercontent.com/go-simd/hex/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/go-simd/hex/HEAD/go.mod>
- **Sources the enricher read:**
  - <https://github.com/tmthrgd/go-hex>
  - <https://github.com/tmthrgd/go-hex/commits/master>
  - <https://github.com/tmthrgd/go-hex/commit/77b1f74>
  - <https://github.com/tmthrgd/go-hex/issues?q=is%3Aissue>
  - <https://github.com/tmthrgd/go-hex/issues/1>
  - <https://github.com/tmthrgd/go-hex/issues/2>
  - <https://github.com/tmthrgd/go-hex/issues/5>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/README.md>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/hex.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/hex_amd64.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/hex_other.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/hex_test.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/hex_encode_amd64.s>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/hex_decode_amd64.s>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/asm_gen.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-hex/HEAD/.travis.yml>
  - <https://pkg.go.dev/github.com/tmthrgd/go-hex?tab=importedby>
  - <https://raw.githubusercontent.com/go-simd/hex/HEAD/README.md>
  - <https://raw.githubusercontent.com/golang/go/master/src/encoding/hex/hex.go>
  - <https://raw.githubusercontent.com/golang/go/go1.7/src/encoding/hex/hex.go>
  - <https://raw.githubusercontent.com/golang/go/go1.18/src/encoding/hex/hex.go>
  - <https://raw.githubusercontent.com/golang/go/go1.19/src/encoding/hex/hex.go>
  - <https://raw.githubusercontent.com/golang/go/go1.20/src/encoding/hex/hex.go>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/tmthrgd/go-hex`) · [data/wave13/enrich/raw/github_com_tmthrgd_go_hex.json](../../../data/wave13/enrich/raw/github_com_tmthrgd_go_hex.json) (enrichment confidence 0.75)

</details>
