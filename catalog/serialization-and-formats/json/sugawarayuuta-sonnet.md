# sonnet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-3-Clause` · 🟡 stale

> Pure-Go rewrite of encoding/json with the same API; decodes typed structs about 4x faster than the stdlib in author benchmarks.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | Unmarshal canada_geometry: 271 MB/s vs encoding/json 62 MB/s (result.txt: 271.30 vs 62.63 MB/s, \~4.3x); citm_catalog: 511 vs 112 MB/s (511.58 vs 112.56 MB/s, \~4.5x). MB/s verbatim from the page charts and result/result.txt; ratios derived from page data. |
| **Workload** | Unmarshal canada.json-style geometry (canada_geometry, many floats) and citm_catalog.json into Go values, measured in MB/s, alongside encoding/json, sonic, goccy/go-json, json-iterator/go, easyjson, segmentio/encoding, valyala/fastjson and minio/simdjson-go. |
| **Metric** | throughput |
| **Hardware** | Intel Core i3-10110U @ 2.10GHz, linux/amd64, GOMAXPROCS=4 (per result/result.txt) |
| **Compiler and flags** | Go toolchain version not stated (go.mod declares go 1.21.1); standard go test -bench benchmarks, no flags stated |
| **Adoption** | 302 stars |
| **Last commit** | 2023-10-04 |
| **Links** | [repository](https://github.com/sugawarayuuta/sonnet) · [benchmark](https://github.com/sugawarayuuta/benchmark) |

## Verdict

The author's own go test -bench run (one run per case, no benchstat; Intel Core i3-10110U, linux/amd64, GOMAXPROCS=4; Go version not stated, and the benchmark's go.mod says go 1.21.1) decoded canada_geometry into a typed struct at 271 MB/s vs 62.6 MB/s for encoding/json (about 4.3x) and citm_catalog at 512 vs 113 MB/s (about 4.5x), allocating 4.7x and 2x fewer bytes. The same run's simdjson-go and fastjson rows only parse and do not bind to structs, so they are not comparable, and sonnet's marshal gains over the stdlib were only 1.1-1.6x.

## Use it when

- Decoding float-heavy documents into typed Go structs, such as GeoJSON coordinates or numeric arrays: 271 vs 63 MB/s on canada_geometry, behind only sonic in the author's run.
- Workloads where GC pressure matters: it allocated the fewest bytes of any struct-binding decoder in the author's run (143 KB vs 669 KB for the stdlib and 648 KB for sonic on canada_geometry; 705 KB vs 1.44 MB and 2.6 MB on citm_catalog).
- Builds that forbid unsafe, assembly, JIT or generated code but still want a 2-4x faster Unmarshal on 64-bit targets.
- Code that already uses encoding/json's Unmarshal, Decoder and Marshal with struct tags, where you can pin or vendor a specific commit.

## Skip it when

- Untrusted or high-precision numeric input while issue #14 stays open. Floats with 20 or more significant digits decode to wrong values because the mantissa overflow check misses wraparound (33208771559017222000 comes out as about 1.476e19), float32 max 3.4028235e+38 is rejected, and extreme exponents can panic Lemire64 with an index out of range.
- 32-bit targets: GOARCH=arm fails to compile because a constant 1&lt;&lt;'&gt;' overflows int in compact.go (issue #13).
- When raw speed matters most on amd64: sonic beat sonnet on every one of the six unmarshal files in sonnet's own benchmark, and goccy/go-json and segmentio/encoding beat it on citm_catalog and golang_source.
- String-heavy or non-ASCII payloads: string_unicode unmarshal ran at 396 MB/s vs 2401 for sonic, 1861 for easyjson and 886 for goccy/go-json.
- Marshal-heavy services or anything that needs an active maintainer: encode gains are only 1.1-1.6x over the stdlib, and there have been no commits, tags or releases since 2023-10-04.

## How it is fast

It builds one decoder closure per reflect.Type, caches it in a copy-on-write map, and decodes in a single pass straight from the input bytes. Scanning works on 8 bytes at a time with SWAR (SIMD-within-a-register) bit tricks. That covers skipping whitespace, finding quote, backslash and control bytes inside strings, and testing and converting 8 ASCII digits in one step (Lemire's digit test plus a multiply-and-shift digit parser). Floats go through a Go port of the Eisel-Lemire algorithm from fast_double_parser, with an exact fast path for powers of ten up to 22, which is why float-heavy input speeds up the most. Struct keys are looked up in a per-struct perfect hash table (a 32-bit wyhash-style hash, with random seeds retried until no two fields collide), and read buffers are reused through size-classed sync.Pools.

## Compared with alternatives

Pick it over Sonic when you want pure Go with no unsafe and the smallest allocations, and can accept about 25-30% lower unmarshal throughput (271 vs 367 MB/s on canada, 512 vs 726 on citm). Sonnet's author says Sonic uses unsafe, skips UTF-8 validation and trades platform compatibility for speed. Pick it over goccy/go-json or segmentio/encoding mainly for float-heavy structs, where it was about 1.6-1.8x faster than both, because both beat it on citm_catalog and golang_source.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (standard library only; go.mod has no requires) |
| **Minimum toolchain** | Go 1.21 (go.mod 'go 1.21.0'; imports the stdlib slices package) |
| **Platforms** | 64-bit GOARCH only in practice. It is pure Go with no unsafe or asm, so it does not depend on CPU features, but 32-bit builds (GOARCH=arm GOARM=7) fail to compile (issue #13). |
| **Thread safety** | Not documented. The code suggests package-level Marshal and Unmarshal are safe to call concurrently: the per-type codec cache is a copy-on-write map behind atomic.Pointer, and each struct's scratch buffer is guarded by an atomic CAS. As in encoding/json, each Decoder or Encoder serves one stream. |
| **Drop-in for the baseline** | partial: it has the same function and method names and behavior, so you only change the import path, but Number and the error types belong to sonnet. A field typed encoding/json.Number is treated as a plain string, so it is marshaled quoted and fails to unmarshal from a JSON number. errors.As against \*json.SyntaxError won't match, and error messages start with 'sonnet:'. |

## Gotchas

- Struct keys are matched by their 32-bit seeded hash alone, and the key bytes are never compared. An unknown key that collides with a field's hash is decoded into that field and also gets past DisallowUnknownFields. This is rare because seeds are random per struct type, but it is not stdlib behavior.
- Unmarshal skips the up-front validity scan (checkValid) that encoding/json runs, so a syntax error late in the input can leave the destination partly filled where the stdlib would leave it untouched (inferred from the code).
- UseNumber stores sonnet.Number, not json.Number, in interface{} values, so existing type assertions on json.Number stop matching.
- The rudderlabs/sonnet fork fixes issue #14 by sending every float through strconv.ParseFloat. That removes the Eisel-Lemire fast path, which is most of the canada_geometry speedup, so expect the fork to be slower on float-heavy input.

## Known shortcomings

- Floats with 20+ significant digits decode to wrong values and the float32 maximum is rejected (#14, open); a panic on extreme exponents looks reachable (source reading). 32-bit builds fail (#13). Not a full drop-in: its own Number type and error types. Struct keys are matched only by a 32-bit seeded hash, so a colliding unknown key decodes into a field and bypasses DisallowUnknownFields. No up-front validation; no releases, last commit 2023-10. sonic beats it on every file.

## Caveats and trade-offs

The benchmark repo is maintained by sonnet's author and is not an independent third party. The Go toolchain version and the benchmark command and flags are not stated. The sonnet README still says the benchmark shows an old version, but the benchmark's go.mod pins sonnet at its latest commit (239c7b6e, 2023-10-04), so that note looks stale. Marshal gains are much smaller (e.g. canada_geometry 156 vs 140 MB/s), and sonic, simdjson-go and segmentio beat sonnet on several unmarshal files.

Reimplements JSON decoding from scratch (does not call encoding/json internally, unlike some 'fast' wrappers); on some workloads (e.g. canada_geometry) it is still slower than bytedance/sonic and minio/simdjson-go, so not the overall fastest.

## Maintenance

Stale: there have been no commits since 2023-10-04 and there is no tagged release (only the pseudo-version v0.0.0-20231004000330-239c7b6e4ce8), and a float-correctness bug and a 32-bit build failure are still open. It is BSD-3-Clause, uses only the standard library and has about 22 source files, so vendoring and patching it (or taking the rudderlabs fork's float fix) is practical.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's own sugawarayuuta/benchmark README charts (from result/result.txt, code in benchmark_test.go) show sonnet unmarshal at 271 MB/s vs encoding/json 62 MB/s on canada_geometry and 511 vs 112 MB/s on citm_catalog. result.txt names the CPU (Intel Core i3-10110U), but no Go toolchain version beyond the go.mod 'go 1.21.1' directive and no build flags or command are stated. That is first-party with partial methodology, so C.
- **Verifier notes:** Both claimed unmarshal figures match the README charts and result.txt. The CPU model was available in result/result.txt, so hardware was filled in, but the Go version and flags are still missing, so it stays at C. Metadata checks out: BSD-3-Clause, 302 stars, last commit 2023-10-04 (stale), not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** sonnet benchmark (result.txt): fewest bytes allocated of any struct-binding decoder, e.g. 143 KB vs 669 KB for encoding/json on canada_geometry.
- **Pages the verifier opened:**
  - <https://github.com/sugawarayuuta/benchmark>
  - <https://github.com/sugawarayuuta/benchmark/blob/main/result/result.txt>
  - <https://github.com/sugawarayuuta/benchmark/blob/main/go.mod>
  - <https://github.com/sugawarayuuta/benchmark/blob/main/benchmark_test.go>
  - <https://github.com/sugawarayuuta/benchmark/blob/main/result/result.go>
  - <https://github.com/sugawarayuuta/sonnet>
- **Sources the enricher read:**
  - <https://github.com/sugawarayuuta/sonnet>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/README.md>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/go.mod>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/decoder.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/reader.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/struct.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/fields.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/perf.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/cache.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/compat.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/any.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/compact.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/encoder.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/writer.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/token.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/decoder_test.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/encoder_test.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/internal/arith/arith.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/internal/arith/float.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/internal/arith/table.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/internal/mem/mem.go>
  - <https://github.com/sugawarayuuta/sonnet/blob/main/internal/mem/circ.go>
  - <https://github.com/sugawarayuuta/sonnet/commits/main>
  - <https://github.com/sugawarayuuta/sonnet/tags>
  - <https://github.com/sugawarayuuta/sonnet/releases>
  - <https://github.com/sugawarayuuta/sonnet/issues>
  - <https://github.com/sugawarayuuta/sonnet/pulls>
  - <https://github.com/sugawarayuuta/sonnet/issues/2>
  - <https://github.com/sugawarayuuta/sonnet/issues/7>
  - <https://github.com/sugawarayuuta/sonnet/issues/8>
  - <https://github.com/sugawarayuuta/sonnet/issues/12>
  - <https://github.com/sugawarayuuta/sonnet/issues/13>
  - <https://github.com/sugawarayuuta/sonnet/issues/14>
  - <https://github.com/sugawarayuuta/benchmark>
  - <https://github.com/sugawarayuuta/benchmark/blob/main/go.mod>
  - <https://github.com/sugawarayuuta/benchmark/blob/main/result/result.txt>
  - <https://github.com/sugawarayuuta/benchmark/blob/main/benchmark_test.go>
  - <https://github.com/sugawarayuuta/benchmark/blob/main/testdata.go>
  - <https://github.com/sugawarayuuta/benchmark/commits/main>
  - <https://github.com/rudderlabs/sonnet>
  - <https://github.com/rudderlabs/sonnet/commit/7713358c>
  - <https://github.com/golang/go/blob/master/src/encoding/json/decode.go>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/sugawarayuuta/sonnet`) · [data/wave4/enrich/raw/github_com_sugawarayuuta_sonnet.json](../../../data/wave4/enrich/raw/github_com_sugawarayuuta_sonnet.json) (enrichment confidence 0.8)

</details>
