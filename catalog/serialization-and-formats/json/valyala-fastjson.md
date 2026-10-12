# fastjson (valyala)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go schemaless JSON parser/validator with a reusable zero-allocation value tree; \~4-15x faster than encoding/json (2019 numbers).

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | README: 'up to 15x faster than the standard encoding/json'. Parse vs stdjson-map (decode into map[string]interface{}): citm_catalog 918.87 vs 62.19 MB/s (\~14.8x), canada 538.22 vs 33.03 MB/s (\~16.3x), twitter 815.86 vs 55.94 MB/s (\~14.6x) (derived from page data). Parse vs the faster stdjson-struct / stdjson-empty-struct modes: citm 918.87 vs 115.64 MB/s (\~7.9x), canada 538.22 vs 127.11 MB/s (\~4.2x), twitter 815.86 vs 110.05 MB/s (\~7.4x) (derived from page data). Validation: citm_catalog 1025.39 vs 237.48 MB/s (\~4.3x), canada 757.07 vs 265.74 MB/s (\~2.8x), small 493.60 vs 198.83 MB/s (\~2.5x) (derived from page data). |
| **Workload** | Parse/validate six standard JSON corpora (small 190B, medium 2.3KB, large 28KB, canada 2.2MB, citm_catalog 1.7MB, twitter 617KB) single-threaded (GOMAXPROCS=1) with Go's testing/benchmark harness. |
| **Metric** | throughput |
| **Hardware** | linux/amd64 (goos/goarch only); CPU model not stated |
| **Compiler and flags** | Go 1.12, `go test -bench` (GOMAXPROCS=1); no later Go version re-run published |
| **Adoption** | 2.5k stars |
| **Last commit** | 2026-02-21 |
| **Links** | [repository](https://github.com/valyala/fastjson) · [benchmark](https://github.com/valyala/fastjson/blob/master/README.md) |

## Verdict

The maintainer's README benchmark (2019, Go 1.12, linux/amd64, CPU not stated, GOMAXPROCS=1) has fastjson parsing canada/citm/twitter at 538-919 MB/s. encoding/json runs at 33-62 MB/s into map[string]interface{} (\~15-16x slower) and 110-127 MB/s into an empty struct (\~4-8x slower), and Validate beats json.Valid by 2.5-4.3x. The `fastjson` row only parses and checks the root type, so its strings and numbers are never decoded, while stdjson-map builds every value; the numbers have not been re-run on a newer Go.

## Use it when

- Hot-path services (RTB bidders, JSON-RPC, log/metrics ingestion) that read a handful of fields from schemaless or heterogeneous messages and today decode into map[string]interface{}. This is where the README shows the biggest gap (\~15x).
- High message rates of small-to-medium documents (the README fixtures run 190 B-28 KB) where GC pressure matters. With one Parser per goroutine or a ParserPool, steady-state parsing allocates nothing.
- Reading many unrelated fields from one document. It parses once and then does path lookups, where gjson/jsonparser rescan the input for each field (README claim).
- Fast strict validation of untrusted input with Validate/ValidateBytes (2.5-4.3x faster than json.Valid in the README), as long as you cap nesting depth yourself.
- Targets where simdjson-go (needs AVX2+CLMUL) or Sonic (AMD64/ARM64 only) can't run. fastjson is plain Go with no assembly or JIT.

## Skip it when

- You decode into typed structs or marshal Go values. There is no reflection or codegen path, so use encoding/json, a drop-in replacement (go-json, Sonic, segmentio/encoding) or easyjson.
- You need Parse alone to reject invalid JSON. Parser.Parse is lenient and accepts `1.0.1`, `[127.0.0.1]`, raw newlines inside strings, unknown escapes like `\c`, and NaN/Inf (issues #88, #119). Only Validate is strict, and running both costs a second pass.
- Large or streamed documents. Input must be fully in memory (no io.Reader) and is copied into the Parser. The README bounds memory at sizeof(Value) times the input length; that is 80 bytes on 64-bit, computed from the struct layout. Users report OOMs, and 26 GB+ RSS on a 1.4 GB file, for inputs of 25 MB-1.4 GB (#101, #109).
- You emit JSON for strict consumers or for signing. MarshalTo and Arena strings escape special characters with Go's strconv quoting, which can produce `\x14` or `\U000e0067` (invalid JSON) and does not byte-match encoding/json (#86, #90, #38). The fix PRs (#87, #127) are unmerged.
- Objects with thousands of keys that you query repeatedly. Object.Get is a linear scan per lookup, so walk it once with Visit into your own map.

## How it is fast

It is a hand-written, single-pass recursive-descent parser with no reflection and no interface{} boxing. Nodes come from a per-Parser slab ([]Value) that is reset and reused on every Parse, so steady-state parsing of small and medium documents shows 0 allocs/op; encoding/json into a map shows 51 to 392,539. The input is copied once into the Parser's buffer. After that, strings and numbers stay as raw substrings via unsafe string/[]byte casts: strings are unescaped lazily, in place, on first access, and numbers are converted only when a Get\* accessor asks, through the bundled fastfloat fast path (which falls back to strconv). Objects are ordered key/value slices searched linearly, not hash maps.

## Compared with alternatives

Pick it over simdjson-go (needs AVX2+CLMUL, no fallback) or Sonic's lazy ast.Node (JIT on AMD64/ARM64, falls back to encoding/json elsewhere) when you want lazy, schemaless field access from a small pure-Go dependency on any target. If you decode into structs, use go-json, jsoniter, segmentio/encoding or easyjson; fastjson can't.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (stdlib only; ships its own fastfloat subpackage) |
| **Minimum toolchain** | Go 1.24 per go.mod since v1.6.8 (Feb 2026); v1.6.4 and earlier declare Go 1.12, the version the README benchmarks used |
| **Platforms** | Any Go target: pure Go with unsafe string/slice casts and no assembly. The legacy Travis config cross-builds linux, darwin, freebsd and windows, and 32-bit test fixes landed in 2021 (#60). |
| **Thread safety** | Per the godoc, Parser, Scanner, Arena, Value and Object are not goroutine-safe, and getters mutate lazily. Use one per goroutine, or ParserPool/ArenaPool (sync.Pool). |
| **Drop-in for the baseline** | no |

## Gotchas

- Lifetime: every \*Value, \*Object and []byte you get back (GetStringBytes, Visit keys) points into the Parser's buffer and node slab. It becomes invalid on the next Parse or Scanner.Next, or after ParserPool.Put, and Arena values die on Arena.Reset. Copy out anything you keep; the README FAQ blames most crashes on this.
- Reads mutate: Type(), Get\*, StringBytes and Object.Get/Visit unescape strings and keys lazily in place. Sharing a parsed Value across goroutines is therefore a data race even if nobody writes.
- Silent defaults and float rounding: Get\* returns 0/nil/false for missing keys, wrong types or unparsable numbers (GetInt on `1.5` gives 0). fastfloat is not correctly rounded: `8.54E-4` becomes 0.0008539999999999999 and `2.0250405e+07` becomes 20250404.999999996 (#91, #110). Use Int()/Float64() when you need errors, or run strconv.ParseFloat on the raw number text from MarshalTo when you need exact values.
- Depth and String(): Parse caps nesting at a hard-coded MaxDepth=300 (#65 asks for a knob). Validate has no cap and is reported to hang on 100,000 nested `[` (#64; fix PR #128 is open). Value.String() returns the JSON-encoded form with quotes, not the string's content.

## Caveats and trade-offs

The README numbers date from 2019 (Go 1.12, README benchmark commit 2019-03-09) and have not been re-run on modern Go, whose encoding/json has improved since. There is no CPU model, and this is a first-party benchmark only. The \~15x headline is against decoding into map[string]interface{}; against struct or empty-struct decoding the gap is \~4-8x, and for validation \~2.5-4.3x. fastjson does not materialize Go values, and parsed objects must be released before the next Parse.

Zero-copy/zero-allocation parser but not a drop-in replacement API; caller must respect object-lifetime rules (Parser/Arena reuse) or risk misuse; validates JSON (unlike jsonparser/gjson) at some cost vs those libraries; can't parse from io.Reader directly.

## Maintenance

MIT-licensed, zero-dependency and small enough to vendor. Issue #105 calls it feature-complete and maintained by the VictoriaMetrics team, and VictoriaMetrics pins v1.6.10. After no commits from Dec 2022 to Dec 2025, v1.6.8-v1.6.10 (Feb 2026) bumped go.mod to 1.24 and cleared GC-retained references, but the open PRs fixing known parse, escape and precision bugs are still unmerged as of Sep 2026.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks section is first-party and compares directly against encoding/json. The benchmark code is public (parser_timing_test.go, validate_timing_test.go) and Go 1.12 is stated, but the only hardware given is goos linux / goarch amd64, with no CPU model. That makes it C.
- **Verifier notes:** Every quoted number appears verbatim in the README; I only added derived-ratio markers and context. MIT license, 2468 stars, not archived, not a fork, and last commit 2026-02-21 (active) are all confirmed. This is a Go library, so it is in scope only if the list accepts non-C++ entries.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/valyala/fastjson>
  - <https://github.com/valyala/fastjson/blob/master/README.md>
  - <https://github.com/valyala/fastjson/blob/master/parser_timing_test.go>
- **Sources the enricher read:**
  - <https://github.com/valyala/fastjson>
  - <https://github.com/valyala/fastjson/blob/master/README.md>
  - <https://github.com/valyala/fastjson/blob/master/parser.go>
  - <https://github.com/valyala/fastjson/blob/master/validate.go>
  - <https://github.com/valyala/fastjson/blob/master/arena.go>
  - <https://github.com/valyala/fastjson/blob/master/scanner.go>
  - <https://github.com/valyala/fastjson/blob/master/update.go>
  - <https://github.com/valyala/fastjson/blob/master/pool.go>
  - <https://github.com/valyala/fastjson/blob/master/util.go>
  - <https://github.com/valyala/fastjson/blob/master/handy.go>
  - <https://github.com/valyala/fastjson/blob/master/doc.go>
  - <https://github.com/valyala/fastjson/blob/master/go.mod>
  - <https://github.com/valyala/fastjson/blob/master/fuzz.go>
  - <https://github.com/valyala/fastjson/blob/master/.travis.yml>
  - <https://github.com/valyala/fastjson/blob/master/fastfloat/parse.go>
  - <https://github.com/valyala/fastjson/blob/master/parser_timing_test.go>
  - <https://github.com/valyala/fastjson/blob/master/validate_timing_test.go>
  - <https://github.com/valyala/fastjson/commits/master>
  - <https://github.com/valyala/fastjson/tags>
  - <https://github.com/valyala/fastjson/commit/227c53b>
  - <https://github.com/valyala/fastjson/commit/87cb56e>
  - <https://github.com/valyala/fastjson/commit/4c89762>
  - <https://github.com/valyala/fastjson/commit/d652a1b>
  - <https://github.com/valyala/fastjson/issues>
  - <https://github.com/valyala/fastjson/issues/119>
  - <https://github.com/valyala/fastjson/issues/88>
  - <https://github.com/valyala/fastjson/issues/64>
  - <https://github.com/valyala/fastjson/issues/91>
  - <https://github.com/valyala/fastjson/issues/110>
  - <https://github.com/valyala/fastjson/issues/90>
  - <https://github.com/valyala/fastjson/issues/86>
  - <https://github.com/valyala/fastjson/issues/38>
  - <https://github.com/valyala/fastjson/issues/109>
  - <https://github.com/valyala/fastjson/issues/105>
  - <https://github.com/valyala/fastjson/issues/16>
  - <https://github.com/valyala/fastjson/issues/93>
  - <https://github.com/valyala/fastjson/pulls>
  - <https://github.com/valyala/fastjson/pull/118>
  - <https://github.com/valyala/fastjson/pull/101>
  - <https://github.com/valyala/fastjson/pull/122>
  - <https://github.com/VictoriaMetrics/VictoriaMetrics/blob/master/go.mod>
  - <https://github.com/minio/simdjson-go/blob/master/README.md>
  - <https://github.com/bytedance/sonic/blob/main/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/valyala/fastjson`) · [data/wave4/enrich/raw/github_com_valyala_fastjson.json](../../../data/wave4/enrich/raw/github_com_valyala_fastjson.json) (enrichment confidence 0.85)

</details>
