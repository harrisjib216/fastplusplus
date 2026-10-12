# gjson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Go library that reads single values from JSON by dot-path without unmarshalling; 3.2-5.7x lower latency than encoding/json structs.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | Small payload (190B): 402 ns/op vs encoding/json struct 1,300 ns/op (\~3.2x faster); medium (2.4KB): 2,241 vs 9,911 ns/op (\~4.4x); large (24KB): 22,756 vs 130,565 ns/op (\~5.7x faster). ns/op values are verbatim from the page tables; the ratios are derived from page data. |
| **Workload** | Same small/medium/large-payload path-lookup benchmark suite as buger/jsonparser (190B / 2.4KB / 24KB JSON records), run with `go test -bench=. -benchmem -count=5` against encoding/json and four other Go JSON libraries. |
| **Metric** | latency |
| **Hardware** | Apple M4 Max (ARM64, darwin) |
| **Compiler and flags** | go test -bench=. -benchmem -count=5, Go 1.26.3, median of 5 runs; comparison libraries pinned to latest versions as of 2026-07-29 |
| **Adoption** | 15.6k stars |
| **Last commit** | 2026-08-28 |
| **Links** | [repository](https://github.com/tidwall/gjson) · [benchmark](https://github.com/buger/jsonparser#benchmarks) |

## Verdict

The numbers come from buger/jsonparser's suite (Go 1.26.3, Apple M4 Max arm64, median of 5 runs, gjson v1.19.0). gjson GetBytes path lookups took 402 / 2,241 / 22,756 ns/op on 190 B / 2.4 KB / 24 KB records, against 1,300 / 9,911 / 130,565 ns/op for encoding/json unmarshalling into a minimal struct (about 3.2x / 4.4x / 5.7x). The comparison is not like-for-like, because encoding/json decodes the whole document while gjson decodes only the requested fields and skips the rest. gjson's own first-party benchmark (M1 Max, Go 1.22) is consistent: 202.1 ns/op for one path versus 3,219 ns/op for a struct unmarshal.

## Use it when

- You need a few fields from JSON whose schema you don't want to model as Go structs, such as webhooks, third-party API responses or log records.
- The documents range from hundreds of bytes to tens of KB and you read a handful of fields. The measured gain over encoding/json struct unmarshal grew from 3.2x at 190 B to 5.7x at 24 KB.
- The query strings are written by developers and need to filter or reshape: array filters `#(...)`, wildcards, multipaths `{a,b}`, or modifiers such as `@reverse`, `@flatten` and `@keys`.
- You scan newline-delimited JSON with the `..` path prefix or ForEachLine.
- You target arm64 or any other Go platform. gjson is pure Go with no assembly, while simdjson-go needs AVX2+CLMUL on amd64 and has no fallback.

## Skip it when

- You read many unrelated fields from the same document. Every Get and every GetMany path rescans from the start. valyala/fastjson's README says it wins in this case because it parses once, and jsonparser's single-pass EachKey beat gjson on the 2.4 KB payload (1,657 vs 2,241 ns/op).
- You need full decoding into typed structs, or encoding. gjson has no Unmarshal or Marshal; use Sonic, go-json or easyjson instead.
- You have zero-allocation hot paths. GetBytes copies the returned Raw/Str, so fetching a large array subtree allocates its full size (28,672 B/op on the 24 KB payload). buger/jsonparser is 0 B/op and about 1.1x faster there.
- You take untrusted JSON without calling Valid() first. Get does not validate, so malformed input gives unexpected results, and Result.Path panics on some malformed documents (issue #400, open).
- Path strings come from untrusted users. Modifiers are on by default, and open issue #391 reports unbounded recursion on deep nesting and O(N^2) memory amplification through `@dig`. Four earlier DoS CVEs (CVE-2020-35380, -36066, -36067, CVE-2021-42836/42248) were fixed by v1.9.3.

## How it is fast

There is no DOM tree and no reflection. Get walks the input once, left to right, compares each object key with the current path component, and returns at the first match. Non-matching subtrees are skipped by parseSquash, which counts bracket depth using a 256-entry byte-class lookup table in a loop unrolled 8 bytes at a time (plain Go, with no SIMD or assembly). Results are substrings of the input (zero-copy for Get on a string, and unsafe string/[]byte casts avoid copying the input in GetBytes), and only the value being returned gets its string or number decoded.

## Compared with alternatives

Pick gjson over buger/jsonparser when you want the path/query language and typed Result conversions and can accept a few allocations and about 10% more time on large payloads (22,756 vs 20,114 ns/op). Pick it over Sonic, go-json or easyjson when you read a few fields instead of decoding the whole document: in the same suite it beat Sonic on medium (2,241 vs 2,703 ns/op) and large (22,756 vs 41,053) payloads. For many fields per document, valyala/fastjson parses once and also validates.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/tidwall/match v1.1.1, github.com/tidwall/pretty v1.2.0 |
| **Minimum toolchain** | Go 1.23 (go.mod; the All/Keys/Values iterators import the iter package) |
| **Platforms** | any Go target (single-file pure Go, no assembly; uses unsafe for string/[]byte header casts) |
| **Thread safety** | Not documented for Get/Parse, which share no mutable state except the modifier registry. AddModifier is documented as not thread-safe and must run before any other gjson call; issue #173 was a 'concurrent map writes' crash from calling it at runtime. The package-level DisableModifiers and DisableEscapeHTML bools are a data race if assigned while other goroutines read them (issue #401, open). |
| **Drop-in for the baseline** | no |

## Gotchas

- Duplicate keys: Get returns the first occurrence, encoding/json keeps the last, and ForEach yields every occurrence (issue #393, open). Two parsers reading the same input can disagree.
- Numbers are stored as float64. Result.Num and Value() lose precision above 2^53 (issue #351); use Int()/Uint(), which read all 64 bits, or Raw. The scanner also treats tokens starting with i, I or N (NaN/Inf-style) as numbers.
- Memory aliasing: Get on a string returns substrings that keep the whole input alive. GetBytes copies each result, and ParseBytes copies the entire input (it calls Parse(string(json))). To avoid the GetBytes copy, sub-slice the input using result.Index as the README shows.
- Parse on an object or array sets Raw to everything from the opening bracket to the end of the input, trailing bytes included (issue #391). Don't log or echo Raw from a reused buffer.

## Known shortcomings

- Not like-for-like: the encoding/json baseline decodes the whole document into a struct (and gjson's own benchmark adds a []byte copy per baseline iteration). GetBytes copies each result; each Get rescans from the start, so jsonparser EachKey wins on multi-field reads. Open 2026 reports: unbounded recursion and O(N^2) memory via @dig (#391), Result.Path panic on malformed JSON (#400), data race on global flags (#401). No validation in Get; numbers are float64 (integers above 2^53 lose precision).

## Caveats and trade-offs

The numbers come from a competitor's suite, the buger/jsonparser README, which gjson's author did not tune. The methodology is fully documented (Go 1.26.3, Apple M4 Max ARM64, median of 5), and benchmark/go.mod resolves gjson v1.19.0. The benchmarks are not like-for-like: the encoding/json baseline fully unmarshals into a typed struct, while gjson does lazy path lookups (one GetBytes per field) and reads only the requested fields. gjson allocates more than jsonparser (28,672 B/op on the large payload vs 4,432 for encoding/json). The hardware is Apple-silicon ARM64 only. gjson's own README gives a first-party corroboration: GJSONGet 202.1 ns/op vs JSONUnmarshalStruct 3219 ns/op, on an M1 Max with Go 1.22, code at tidwall/gjson-benchmarks.

Path-query API (`gjson.Get(json, "path.to.field")`) rather than struct unmarshalling; large-payload run allocates 28,672 B/op (not zero-allocation, unlike buger/jsonparser) because it builds result values on demand.

## Maintenance

Actively maintained by its original author (last commit 2026-08-28, v1.19.0, 15.6k stars) and MIT-licensed. It is a single-file pure-Go module with two small dependencies that is easy to vendor, but the repo has pull requests disabled and several 2026 bug and security reports (#391, #393, #400, #401) are still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** In the buger/jsonparser README Benchmarks tables, tidwall/gjson and 'encoding/json struct' both run in the same harness. The code is public: benchmark/benchmark_gjson_sonic_test.go (BenchmarkGjsonSmall/Medium/Large) and BenchmarkEncodingJsonStruct\* in benchmark/benchmark_{small,medium,large}_payload_test.go. The page states the command (`go test -bench=. -benchmem -count=5`, median of 5), Go 1.26.3 (matching benchmark/go.mod) and the CPU (Apple M4 Max), so code, compiler, flags and CPU are all present.
- **Verifier notes:** Every number matches gjson's own rows on the jsonparser page, and the metadata checks out: MIT, 15,559 stars, not a fork or archived, last commit 2026-08-28, active. I fixed the speedup label to mark the ratios as derived and set compared_against_cpp_std_directly to false, because the baseline is Go's encoding/json and not a C++ standard library.
- **Fields the verifier corrected:** `claimed_speedup`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/buger/jsonparser#benchmarks>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_gjson_sonic_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_large_payload_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_small_payload_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/go.mod>
  - <https://github.com/tidwall/gjson>
  - <https://github.com/tidwall/gjson#performance>
  - <https://github.com/tidwall/gjson-benchmarks>
- **Sources the enricher read:**
  - <https://github.com/tidwall/gjson>
  - <https://github.com/tidwall/gjson#performance>
  - <https://github.com/tidwall/gjson/blob/master/gjson.go>
  - <https://github.com/tidwall/gjson/blob/master/go.mod>
  - <https://github.com/tidwall/gjson/blob/master/go.sum>
  - <https://github.com/tidwall/gjson/blob/master/SYNTAX.md>
  - <https://github.com/tidwall/gjson/blob/master/.github/workflows/go.yml>
  - <https://github.com/tidwall/gjson/issues/173>
  - <https://github.com/tidwall/gjson/issues/217>
  - <https://github.com/tidwall/gjson/issues/351>
  - <https://github.com/tidwall/gjson/issues/360>
  - <https://github.com/tidwall/gjson/issues/387>
  - <https://github.com/tidwall/gjson/issues/391>
  - <https://github.com/tidwall/gjson/issues/393>
  - <https://github.com/tidwall/gjson/issues/400>
  - <https://github.com/tidwall/gjson/issues/401>
  - <https://github.com/tidwall/gjson-benchmarks>
  - <https://github.com/tidwall/gjson-benchmarks/blob/master/gjson_test.go>
  - <https://github.com/buger/jsonparser#benchmarks>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_gjson_sonic_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark_large_payload_test.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/benchmark.go>
  - <https://github.com/buger/jsonparser/blob/master/benchmark/go.mod>
  - https://api.osv.dev/v1/query (package github.com/tidwall/gjson, ecosystem Go)
  - <https://github.com/minio/simdjson-go>
  - <https://github.com/bytedance/sonic>
  - <https://github.com/valyala/fastjson>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/tidwall/gjson`) · [data/wave4/enrich/raw/github_com_tidwall_gjson.json](../../../data/wave4/enrich/raw/github_com_tidwall_gjson.json) (enrichment confidence 0.85)

</details>
