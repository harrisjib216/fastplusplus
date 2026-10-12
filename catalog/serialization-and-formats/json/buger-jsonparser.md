# jsonparser (buger)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Zero-allocation, path-based JSON field extractor for Go; 3-6.5x faster than encoding/json struct unmarshal on the project's benchmarks.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | Large payload (24KB): 20,114 ns/op vs encoding/json struct 130,565 ns/op, '6.5x faster than encoding/json' (verbatim from page), with 0 B/op and 0 allocs/op vs 4,432 B/op and 147 allocs/op. Small payload (190B), EachKey: 227 vs 1,300 ns/op (\~5.7x faster, derived from page data). Medium (2.4KB): EachKey 1,657 and Get 3,141 vs 9,911 ns/op (\~6.0x and \~3.2x, derived from page data). |
| **Workload** | Schema-less field extraction from small (190B HTTP log), medium (2.4KB Clearbit-style), and large (24KB Discourse-API-style) JSON payloads, benchmarked with `go test -bench=. -benchmem -count=5` against encoding/json, gjson, sonic, ffjson and easyjson. |
| **Metric** | latency |
| **Hardware** | Apple M4 Max (ARM64, darwin) |
| **Compiler and flags** | go test -bench=. -benchmem -count=5, Go 1.26.3, median of 5 runs; comparison libraries pinned to latest versions as of 2026-07-29 |
| **Adoption** | 5.7k stars |
| **Last commit** | 2026-08-21 |
| **Links** | [repository](https://github.com/buger/jsonparser) · [benchmark](https://github.com/buger/jsonparser#benchmarks) |

## Verdict

In the project's own benchmarks (Go 1.26.3, Apple M4 Max arm64, median of 5 `go test -bench` runs), reading username, id and slug from each array element of a 24KB Discourse-style payload took 20,114 ns/op with 0 allocations. encoding/json, unmarshalling into a minimal struct, took 130,565 ns/op with 147 allocations, a 6.5x gap. EachKey was about 5.7x faster on a 190B log record and about 6.0x faster on a 2.4KB record. The comparison is not like-for-like: jsonparser leaves values as undecoded []byte (the 0 B/op EachKey rows match the benchmark variants whose ParseString calls are commented out), while encoding/json builds Go strings.

## Use it when

- Pulling a few fields out of JSON whose schema is large, unknown or unstable (third-party API responses, log records), where defining structs for encoding/json is the cost you want to avoid.
- GC-sensitive hot paths: Get and EachKey measured 0 B/op on all three benchmark payloads, versus 416-4,432 B/op for encoding/json struct unmarshal.
- Reading several fields from one document with EachKey: one pass over the 2.4KB payload took 1,657 ns versus 9,911 ns for encoding/json, and it also beat gjson (2,241), easyjson (2,368) and sonic (2,703).
- Arrays of records where you need one or two fields per element: EachArray plus Get on the 24KB payload took 20,114 ns versus 130,565 ns for encoding/json.
- Multi-GB JSON files: ReaderParser reads from an io.Reader in 64 KiB chunks with a bounded sliding window (64 MiB by default) instead of loading the whole document.

## Skip it when

- You need most of the document as typed Go structs. There is no Unmarshal, and struct-binding libraries such as sonic (an encoding/json drop-in) or easyjson (code generation) fit that job better.
- You need validation. Get stops at the first match and never checks the rest of the input, and getType labels any token starting with a digit or '-' as Number without checking its format.
- Your code calls Get separately for each field on medium documents: on the 2.4KB benchmark Get (3,141 ns) was slower than gjson, easyjson and sonic, and only EachKey led.
- You need decoded Go strings for most values. Get returns raw bytes with JSON escapes intact, and GetString/ParseString unescape but allocate, a cost the 0-alloc headline numbers leave out.
- Your main job is writing or editing JSON. There is no encoder, and the README marks Set and Delete as experimental.

## How it is fast

It never builds a tree. searchKeys walks the bytes once, tracks only nesting depth, compares keys in place, skips non-matching objects and arrays whole with a brace/bracket counter (blockEnd), and returns as soon as the path matches. String ends are found with an 8-byte SWAR (SIMD-within-a-register) scan for quote/backslash, and the hot loops use gjson's single-comparison fast skip (byte &gt; 0x5C) over non-structural bytes. Values are sub-slices of the input, key comparison uses unsafe []byte-to-string casts, and escaped keys are unescaped into a 64-byte stack buffer, so extraction allocates nothing; EachKey matches all requested paths in one scan instead of rescanning per Get.

## Compared with alternatives

Pick it over gjson when allocations matter or you read many paths at once: in the repo's benchmarks jsonparser allocates 0 B/op everywhere against gjson's 64-28,672 B/op, and EachKey beats gjson on the small and medium payloads, though gjson's per-path Get is faster than jsonparser's Get at 2.4KB. Pick it over Sonic or easyjson only when you want a few fields rather than a typed struct, because those decode whole documents into structs.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (standard library only; go.mod has no require lines) |
| **Minimum toolchain** | go.mod declares Go 1.13; CI runs Go 1.25; the published benchmarks used Go 1.26.3 |
| **Platforms** | Any Go target: pure Go with no assembly files. Unsafe string/[]byte casts are the default, with a safe fallback under the appengine/tinygo build tags. The published benchmarks are arm64 only (Apple M4 Max). |
| **Thread safety** | Not documented for the package-level functions. They keep no mutable package state (only read-only error values, literal byte slices and an escape table), so concurrent reads of a shared buffer appear safe. ReaderParser is documented as not safe for concurrent use and allows one operation per stream. |
| **Drop-in for the baseline** | no |

## Gotchas

- Returned []byte values alias the input buffer. Capacity is clipped, so an append will not overwrite the input, but copy the values before you reuse or mutate the buffer. GetUnsafeString returns a string that stays valid only while the buffer lives and does not handle escapes.
- Keys inside arrays are not searched unless you address the element with "[n]" or iterate with EachArray. When a key is duplicated, the first occurrence wins because searchKeys returns on the first match.
- Use v1.5.1 or later. The v1.5.1 changelog fixes a stringEnd backslash scan that walked the rest of the document (128 us to 22 us on the 24KB payload). Versions up to v1.1.1 have denial-of-service advisories: CVE-2020-10675, CVE-2020-35381 and CVE-2026-32285, the last fixed in v1.1.2.
- Seven releases (v1.3.0 to v1.6.1) shipped between 2026-07-27 and 2026-07-30 and added many APIs. Open issue #288 (filed 2026-08-04) reports that `go test` fails at HEAD on amd64 Linux (TestOracleSetPr286Regression) and that this blocks Debian packaging.

## Known shortcomings

- The zero-allocation README rows are the 'Manual' variants that never build Go strings, while encoding/json does. Comparison libraries are pinned to 2018-2019 versions despite the README's 'latest' claim. go test fails at HEAD on amd64 Linux (#288, no reply). Seven releases in four days (2026-07); pin v1.5.1+ (fixes a full-document scan) and note CVE-2026-32285 fixed in v1.1.2. Benchmarks are Apple M4 Max only; Get does not validate the rest of the input.

## Caveats and trade-offs

The benchmark is first-party (the project's own repo), but the methodology (hardware, Go version, run count) is fully stated, so it is treated as Tier A. The numbers are Apple-silicon ARM64, not the x86 hardware most servers run. The comparison is not like-for-like: encoding/json fully unmarshals into a typed struct, while jsonparser scans bytes and extracts only the requested fields. The result depends on the API used: on the medium payload, Get (3,141 ns/op) is slower than gjson (2,241), easyjson (2,368) and sonic (2,703), and only EachKey (1,657) leads. On the small payload, EachObject (205 ns/op) allocates 64 B/op.

No reflection/struct binding by default (path-based `Get`/`EachKey`/`EachObject` API instead of Unmarshal-into-struct), so migrating from encoding/json requires rewriting access code; returns []byte slices into the original buffer rather than copies unless told otherwise.

## Maintenance

Active (last commit 2026-08-21), MIT-licensed, standard-library-only and a single package, so it is easy to vendor. Still, pin a version and run your own tests, given the July 2026 burst of seven releases and the open report of failing tests at HEAD (#288).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Benchmarks section compares jsonparser with 'encoding/json struct' on the 190B, 2.4KB and 24KB payloads. The code is public: BenchmarkJsonParser\* and BenchmarkEncodingJsonStruct\* in benchmark/benchmark_{small,medium,large}_payload_test.go. The command (`go test -bench=. -benchmem -count=5`, median of 5), Go 1.26.3 (benchmark/go.mod: go 1.26.3) and the CPU (Apple M4 Max) are stated. The numbers are first-party, but full methodology meets tier A.
- **Verifier notes:** Every figure appears in the README tables. The 6.5x large-payload figure is the page's own claim, and I relabelled the small-payload \~5.7x as derived. Metadata is correct: MIT, 5,657 stars, not a fork or archived, last commit 2026-08-21, active. I set compared_against_cpp_std_directly to false, because the baseline is Go's encoding/json.
- **Fields the verifier corrected:** `claimed_speedup`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/buger/jsonparser#benchmarks>
  - <https://github.com/buger/jsonparser>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_large_payload_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_small_payload_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_gjson_sonic_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/go.mod>
- **Sources the enricher read:**
  - <https://github.com/buger/jsonparser>
  - <https://github.com/buger/jsonparser#benchmarks>
  - <https://github.com/buger/jsonparser/blob/master/parser.go>
  - <https://github.com/buger/jsonparser/blob/master/bytes.go>
  - <https://github.com/buger/jsonparser/blob/master/bytes_safe.go>
  - <https://github.com/buger/jsonparser/blob/master/bytes_unsafe.go>
  - <https://github.com/buger/jsonparser/blob/master/config.go>
  - <https://github.com/buger/jsonparser/blob/master/reader_parser.go>
  - <https://github.com/buger/jsonparser/blob/master/escape.go>
  - <https://github.com/buger/jsonparser/blob/master/path_compiler.go>
  - <https://github.com/buger/jsonparser/blob/master/wildcard.go>
  - <https://github.com/buger/jsonparser/blob/master/append.go>
  - <https://github.com/buger/jsonparser/blob/master/aliases.go>
  - <https://github.com/buger/jsonparser/blob/master/go.mod>
  - <https://github.com/buger/jsonparser/blob/master/CHANGELOG.md>
  - <https://github.com/buger/jsonparser/blob/master/docs/proof-gap-root-cause.md>
  - <https://github.com/buger/jsonparser/blob/master/.github/workflows/reqproof.yml>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/go.mod>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/go.sum>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_small_payload_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_medium_payload_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_large_payload_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_gjson_sonic_test.go>
  - <https://github.com/buger/jsonparser/issues/288>
  - <https://github.com/buger/jsonparser/issues>
  - <https://github.com/buger/jsonparser/releases>
  - <https://github.com/buger/jsonparser/tags>
  - <https://github.com/buger/jsonparser/commits/master>
  - <https://github.com/advisories/GHSA-6g7g-w4f8-9c9x>
  - <https://github.com/advisories/GHSA-8vrw-m3j9-j27c>
  - <https://github.com/advisories/GHSA-rmh2-65xw-9m6q>
  - <https://github.com/mailru/easyjson/tags>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/buger/jsonparser`) · [data/wave4/enrich/raw/github_com_buger_jsonparser.json](../../../data/wave4/enrich/raw/github_com_buger_jsonparser.json) (enrichment confidence 0.85)

</details>
