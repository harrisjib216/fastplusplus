# simdjson-go

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟡 stale

> Go port of simdjson's SIMD parser for AVX2 amd64; builds a navigable tape 2.3-16.5x faster than encoding/json's interface{} decode.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | README: 'Compared to Golang's standard package encoding/json, simdjson-go is about 10x faster' and it 'runs on average at about 40% to 60% of the speed of simdjson'. The per-file benchcmp table (default settings, i.e. string copying on) ranges from 2.34x (Numbers, 70.42 -&gt; 165.04 MB/s) to 16.50x (Gsoc_2018, 160.17 -&gt; 2642.88 MB/s), e.g. Twitter 95.17 -&gt; 1072.59 MB/s (11.27x) and Citm_catalog 101.29 -&gt; 1270.02 MB/s (12.54x). The 14 per-file speedups have an arithmetic mean of \~7.5x and a geometric mean of \~6.4x (derived from page data), so the '10x' headline is above the README's own table. Vs json-iterator/go the table shows 3.19x-12.38x per file. |
| **Workload** | encoding/json.Unmarshal and json-iterator (ConfigCompatibleWithStandardLibrary) Unmarshal into interface{}, versus simdjson-go's simdjson.Parse building its internal tape (no Go values materialized), on 14 test files (apache_builds, canada, citm_catalog, github_events, gsoc_2018, instruments, marine_ik, mesh, mesh_pretty, numbers, random, twitter, twitterescaped, update_center). Results are go test -bench output compared with benchcmp, with GOMAXPROCS=32 per the -32 benchmark suffix. Code: benchmarks/benchmarks_test.go. |
| **Metric** | throughput |
| **Compiler and flags** | Go, `go test -bench` with `benchcmp` (compiler version and build flags not stated) |
| **Adoption** | 2.0k stars; used by MinIO |
| **Last commit** | 2025-08-26 |
| **Links** | [repository](https://github.com/minio/simdjson-go) · [benchmark](https://github.com/minio/simdjson-go/blob/master/README.md) |

## Verdict

The README's benchcmp table compares simdjson.Parse building its tape (strings copied, ParsedJson reused) against encoding/json.Unmarshal into interface{} on 14 standard corpus files: speedups run from 2.34x (numbers) to 16.50x (gsoc-2018), with a geometric mean of \~6.4x, so the '10x' headline overstates the table, and the two sides do different work. A maintainer comment on issue #35 (2021-05-17) says the numbers came from an AMD Ryzen 3950 with Go 1.16.2 (GOMAXPROCS=32, and Parse overlaps its two stages on two goroutines for these &gt;8 KB files); the table has not been re-run since.

## Use it when

- Large in-memory documents (over 8 KB, so the two stages overlap) or NDJSON streams on x86-64 servers with AVX2+CLMUL (Intel Haswell or later, AMD Zen or later), where parse throughput is the bottleneck.
- Pulling a few fields out of big, string- or structure-heavy payloads such as event feeds, API dumps or logs without building Go values, using FindElement or Object.ForEach with an onlyKeys filter. This input shape got 6.5-16.5x over encoding/json in the README table (twitter 11.3x, citm_catalog 12.5x, gsoc-2018 16.5x).
- Filtering or rewriting NDJSON: ParseNDStream splits an io.Reader into \~10 MB chunks and parses them on (GOMAXPROCS+1)/2 goroutines, and DeleteElems, the Set\* methods and MarshalJSON let you edit records and write them back out.
- Storing parsed JSON for repeated reads. The Serializer shrank parking-citations-1M to 10.9-17.2% of the JSON size with compression and deserializes at 806-2334 MB/s (README), and it deserializes on any CPU.

## Skip it when

- You need struct binding or a drop-in Unmarshal. It has none, and converting the tape into your own structs or interface{} is extra work that the headline benchmark leaves out. In issue #91 a Nostr client was 5.5x slower than encoding/json (53.1 vs 9.6 ms) until it reused ParsedJson/Object/Array values. After that it was only modestly ahead of easyjson (8.1 vs 9.8 ms).
- arm64 (Graviton, Apple Silicon), 386, gccgo, noasm/appengine builds, or x86 CPUs without AVX2+CLMUL. Parse returns 'Unsupported platform' or 'Host CPU does not meet target specs', with no pure-Go fallback, and a maintainer said an arm64 port 'will probably not be done in the scope of this project' (#51).
- Number-heavy data (GeoJSON coordinates, meshes, numeric arrays): canada, marine_ik, mesh, mesh.pretty and numbers gained only 2.3-3.9x over encoding/json in the README table, because number conversion is scalar strconv.
- Tiny messages, top-level scalars, or one giant array that does not fit in memory. A fresh parser carries \~96 KB of stage-1 index buffers plus a tape pre-sized to about 1.2x the input bytes. Parse rejects top-level null, true, false, numbers and strings (#59). It cannot lazily stream one huge array; only NDJSON streams (#87).
- Untrusted input where strict validation matters. Open issue #96 (2026-07-31, unanswered) reports that \u escapes containing bytes 0x00-0x2F are accepted as digit 0: the digittoval DATA table in parse_string_amd64.s does skip offsets 0x40-0x6F. It also reports that the string-scan bound is passed to the assembly by address, so an unterminated string can be read past the intended window.

## How it is fast

Stage 1 is simdjson's structural-indexing algorithm, translated from C intrinsics to Go assembly with c2goasm: for each 64-byte block it finds odd-length backslash runs, builds the in-string mask with a carry-less-multiply prefix-XOR (VPCLMULQDQ), classifies whitespace and structural characters with AVX2 (an AVX-512 variant is picked at runtime when AVX512F is present), and flattens the bitmask into uint32 incremental offsets. Stage 2 is a goto-based state machine in Go that consumes those offsets and writes a []uint64 tape with skip pointers over objects and arrays; it validates and unescapes strings in AVX2 assembly, and with WithCopyStrings(false) leaves them pointing into the input. For inputs over 8 KB the two stages run concurrently on two goroutines connected by a channel, and reusing the previous ParsedJson keeps each parse to a few dozen allocations. Numbers go through scalar strconv.ParseInt/ParseFloat rather than SIMD, which is why number-heavy files gain the least.

## Compared with alternatives

Over fastjson (valyala), which also parses into its own untyped value, pick simdjson-go for large or NDJSON input read from an io.Reader (fastjson's README says it cannot parse from a Reader, while ParseNDStream parses chunks in parallel) or when you want a compact binary serialized form. Pick Sonic, jsoniter or easyjson instead when you need to decode into Go structs, and Sonic also when you need arm64 (Go 1.20+).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/klauspost/cpuid/v2 v2.2.10, github.com/klauspost/compress v1.18.0 (golang.org/x/sys indirect); no cgo |
| **Minimum toolchain** | Go 1.22 per go.mod; CI tests 1.22.x-1.24.x; gc toolchain only (gccgo cannot build the Go assembly and reports an unsupported CPU) |
| **Platforms** | x86-64 with AVX2 + CLMUL required (an AVX-512F stage-1 path is selected at runtime when available); other GOARCH values compile, but Parse, ParseND and ParseNDStream return an error; Serializer.Deserialize works everywhere |
| **Thread safety** | Mostly not documented. Separate Parse calls with separate ParsedJson values are independent (the repo's nocopy-par benchmark runs one per goroutine). A ParsedJson passed as `reuse` is overwritten. A source comment says a Serializer 'can be reused, but not used concurrently'. |
| **Drop-in for the baseline** | false — different API (a tape plus iterators; no struct Unmarshal). Iter.Interface() and Object.Map() give interface{}/map[string]interface{} results, but they allocate per element and are not part of the benchmarked path. |

## Gotchas

- WithCopyStrings(false) is the fast mode (Twitter 1327 vs 1073 MB/s in the README) but makes tape strings point into your input slice, so the buffer must stay alive and unmodified while the ParsedJson is in use. The default copies strings.
- Always pass the previous \*ParsedJson as `reuse`, since fresh parsers allocate index buffers and a tape every call. ParseND does not attach its internal parser to the returned value (Parse does), so reuse is largely ineffective for ParseND.
- The latest tag, v0.4.5 (2023-03-13), is what `go get` resolves. It lacks later master fixes, including #92 (merged 2025-06-16): Object.ForEach with an onlyKeys filter consumed the next key after skipping a value. Pin a commit pseudo-version if you use that API.
- Parse runs its two stages on two goroutines for inputs over 8 KB, so a per-call MB/s figure can use two cores while encoding/json uses one. Separately, the serializer uses //go:linkname to runtime.memhash, which ties it to Go runtime internals across toolchain upgrades.

## Caveats and trade-offs

The comparison is not like-for-like: simdjson-go only parses into its tape, while encoding/json and json-iterator build full interface{} trees. The README itself says simdjson 'provides different output than traditional unmarshal functions'. No CPU model or Go version is stated, only GOMAXPROCS=32. The README numbers match the WithCopyStrings(true) 'copy' rows, but the current benchmarks/benchmarks_test.go runs simdjson with WithCopyStrings(false). Issue #35 (2021) reported that the earlier published numbers could not be reproduced at HEAD. That led to the current table (PR #36, May 2021), which has not been refreshed since. amd64 only, with AVX2+CLMUL required and no fallback. The last commit was 2025-08-26 (\~13 months ago), so the entry is stale by this pipeline's rule.

Requires AVX2 + CLMUL CPU support with no software fallback (fails closed rather than degrading); pure Go (no cgo) but effectively a from-scratch reimplementation of simdjson's two-stage algorithm, not a wrapper around the C++ library, so it inherits simdjson's tape-based access model rather than idiomatic Go structs.

## Maintenance

Stale (last commit 2025-08-26, last tag v0.4.5 from March 2023; maintainers called it 'purpose built' and done in #86 and have not answered a July 2026 offer, #96, of fixes, \~35% faster parsing and a portable path from the data-bet fork), but it is Apache-2.0 pure Go plus assembly with two small dependencies, so it is easy to vendor or fork, and minio/minio (now archived) pins v0.4.5.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README tables compare directly against encoding/json using public benchmark code (benchmarks/benchmarks_test.go: benchmarkEncodingJson, benchmarkJsoniter, benchmarkSimdJson). However, no CPU model, Go version or build flags are stated; the only environment detail is the -32 GOMAXPROCS suffix. That is first-party with partial methodology, so C.
- **Verifier notes:** The record is accurate: the numbers belong to the encoding/json benchcmp table, and license, stars (2,044) and the stale status all check out. I added the apples-to-oranges caveat (tape parse vs full unmarshal) and a derived mean showing the README's '10x' headline is generous. I did not verify 'used by MinIO' beyond MinIO owning the repo, so I left it unchanged.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/minio/simdjson-go>
  - <https://github.com/minio/simdjson-go/commits/master>
  - <https://github.com/minio/simdjson-go/blob/master/README.md>
  - <https://github.com/minio/simdjson-go/blob/master/benchmarks/benchmarks_test.go>
  - <https://github.com/minio/simdjson-go/blob/master/benchmarks/go.mod>
  - <https://github.com/minio/simdjson-go/blob/master/benchmarks_test.go>
  - <https://github.com/minio/simdjson-go/blob/master/parse_json_amd64_test.go>
  - <https://github.com/minio/simdjson-go/blob/master/simdjson_amd64_test.go>
  - <https://github.com/minio/simdjson-go/commit/762cc41d5a>
  - <https://github.com/minio/simdjson-go/pull/36>
  - <https://github.com/minio/simdjson-go/issues/35>
- **Sources the enricher read:**
  - <https://github.com/minio/simdjson-go>
  - <https://github.com/minio/simdjson-go/blob/master/README.md>
  - <https://github.com/minio/simdjson-go/blob/master/go.mod>
  - <https://github.com/minio/simdjson-go/blob/master/simdjson_amd64.go>
  - <https://github.com/minio/simdjson-go/blob/master/simdjson_other.go>
  - <https://github.com/minio/simdjson-go/blob/master/parse_json_amd64.go>
  - <https://github.com/minio/simdjson-go/blob/master/options.go>
  - <https://github.com/minio/simdjson-go/blob/master/stage1_find_marks_amd64.go>
  - <https://github.com/minio/simdjson-go/blob/master/find_subroutines_amd64.go>
  - <https://github.com/minio/simdjson-go/blob/master/find_quote_mask_and_bits_amd64.s>
  - <https://github.com/minio/simdjson-go/blob/master/stage2_build_tape_amd64.go>
  - <https://github.com/minio/simdjson-go/blob/master/parse_string_amd64.go>
  - <https://github.com/minio/simdjson-go/blob/master/parse_string_amd64.s>
  - <https://github.com/minio/simdjson-go/blob/master/parse_number.go>
  - <https://github.com/minio/simdjson-go/blob/master/parsed_json.go>
  - <https://github.com/minio/simdjson-go/blob/master/parsed_object.go>
  - <https://github.com/minio/simdjson-go/blob/master/parsed_array.go>
  - <https://github.com/minio/simdjson-go/blob/master/parsed_serialize.go>
  - <https://github.com/minio/simdjson-go/blob/master/fuzz_test.go>
  - <https://github.com/minio/simdjson-go/blob/master/benchmarks_test.go>
  - <https://github.com/minio/simdjson-go/blob/master/benchmarks/benchmarks_test.go>
  - <https://github.com/minio/simdjson-go/blob/master/benchmarks/go.mod>
  - <https://github.com/minio/simdjson-go/blob/master/.github/workflows/go.yml>
  - <https://github.com/minio/simdjson-go/commits/master>
  - <https://github.com/minio/simdjson-go/tags>
  - <https://github.com/minio/simdjson-go/releases>
  - <https://github.com/minio/simdjson-go/issues?q=is%3Aissue>
  - <https://github.com/minio/simdjson-go/pulls?q=is%3Apr>
  - <https://github.com/minio/simdjson-go/issues/35>
  - <https://github.com/minio/simdjson-go/issues/38>
  - <https://github.com/minio/simdjson-go/issues/51>
  - <https://github.com/minio/simdjson-go/issues/59>
  - <https://github.com/minio/simdjson-go/issues/69>
  - <https://github.com/minio/simdjson-go/issues/86>
  - <https://github.com/minio/simdjson-go/issues/87>
  - <https://github.com/minio/simdjson-go/issues/91>
  - <https://github.com/minio/simdjson-go/issues/95>
  - <https://github.com/minio/simdjson-go/issues/96>
  - <https://github.com/minio/simdjson-go/pull/36>
  - <https://github.com/minio/simdjson-go/pull/57>
  - <https://github.com/minio/simdjson-go/pull/90>
  - <https://github.com/minio/simdjson-go/pull/92>
  - <https://github.com/data-bet/simdjson-go>
  - <https://github.com/data-bet/simdjson-go/pull/1>
  - <https://github.com/minio/minio>
  - <https://github.com/minio/minio/blob/master/go.mod>
  - <https://github.com/valyala/fastjson/blob/master/README.md>
  - <https://github.com/bytedance/sonic/blob/main/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/minio/simdjson-go`) · [data/wave4/enrich/raw/github_com_minio_simdjson_go.json](../../../data/wave4/enrich/raw/github_com_minio_simdjson_go.json) (enrichment confidence 0.82)

</details>
