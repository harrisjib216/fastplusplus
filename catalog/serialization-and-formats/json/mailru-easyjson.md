# easyjson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Go codegen tool producing reflection-free struct JSON marshalers; README (2016) shows \~2.8x marshal, \~5.7x unmarshal vs encoding/json.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | 'easyjson is roughly 5-6 times faster than the standard encoding/json for unmarshaling, and 3-4 times faster for non-concurrent marshaling. Concurrent marshaling is 6-7x faster if marshaling to a writer' (verbatim from README). Table (MB/s, derived from page data): unmarshal regular 125 vs 22 (\~5.7x), small 67 vs 9.7 (\~6.9x); one-goroutine marshal regular 213 vs 75 (\~2.8x), to a writer 263 vs 75 (\~3.5x), small 125 vs 32 (\~3.9x), large 212 vs 80 (\~2.7x); concurrent marshal regular 792 vs 252 (\~3.1x), to a writer 1748 vs 252 (\~6.9x), large to a writer 2134 vs 289 (\~7.4x) |
| **Workload** | Marshal/unmarshal of a 13KB Twitter-search-style JSON document (9KB minified), an 80-byte small-request case, and a \~500KB large-request case (50 concatenated samples), using easyjson's codegen'd marshalers |
| **Metric** | throughput |
| **Adoption** | 4.9k stars |
| **Last commit** | 2026-03-14 |
| **Links** | [repository](https://github.com/mailru/easyjson) · [benchmark](https://github.com/mailru/easyjson/blob/master/README.md#benchmarks) |

## Verdict

The README tables set encoding/json against easyjson-generated code on a 13 KB Twitter search response, an 80-byte fragment and a \~500 KB 50-copy struct: unmarshal 125 vs 22 MB/s (\~5.7x); single-goroutine marshal 213 vs 75 MB/s (\~2.8x), or 263 MB/s (\~3.5x) when easyjson writes to a discard writer, compared with std json.Marshal rather than json.Encoder. No CPU or flags are given, and the only Go version stated is go1.6 for the 2016 ffjson/codec runs. In the HEAD benchmark code, the concurrent 'regular' easyjson marshal credits the 13,024-byte whitespace-included input file per op while encoding/json is credited its \~9 KB output, which would inflate that 792 vs 252 MB/s (\~3.1x) ratio by about 1.4x.

## Use it when

- High-QPS Go services that encode and decode a fixed set of known structs (API request/response types), where you control the build and can commit generated \*_easyjson.go files.
- Responses written straight to an http.ResponseWriter or io.Writer (MarshalToHTTPResponseWriter/MarshalToWriter). The README's largest gains are in writer mode: 263 vs 75 MB/s single-goroutine, 1748 vs 252 MB/s concurrent.
- Frequent small messages where allocations dominate. The README's 80-byte unmarshal is 3 allocs/128 B vs 14 allocs/720 B for encoding/json, and writer-mode marshal of the 13 KB doc is 8 allocs/742 B vs 9 allocs/23 KB.
- Payloads with repeated low-cardinality string values (the `intern` tag deduplicates them) or short-lived decoded objects (the `nocopy` tag skips string copies).
- Pure-Go deployments on any GOARCH, including environments that forbid unsafe (App Engine disables it automatically, or build with `easyjson_nounsafe`).

## Skip it when

- Generic struct types: codegen fails or emits uncompilable code (issue #369, open since 2022; #414 'cannot use generic type ... without instantiation'). Types in `package main` are also unsupported, because the generator must import the package through a `go run` bootstrap.
- When output or behavior must match encoding/json exactly. Map keys come out in Go map iteration order, not sorted (#292), so output is not byte-stable. Object keys match case-sensitively. Floats use strconv 'g' formatting, so 1e6 comes out as `1e+06` (#425). []byte fields accept only base64, not integer arrays (#434).
- Large or unbounded input you want to stream: jlexer works only on an in-memory []byte, and UnmarshalFromReader ReadAlls the whole body. The README says there is no true streaming encode either.
- Strict validation of untrusted input: string tokens are scanned only for their closing quote, so control characters and invalid UTF-8 in strings are not rejected on decode. The README says full validation is not done.
- Dynamic data (`interface{}`/`map[string]interface{}` fields): the generated encoder falls back to encoding/json.Marshal for interface values that have no marshaler, so those parts get no speedup.

## How it is fast

Ahead-of-time code generation gives each struct straight-line encode/decode code. JSON field prefixes such as `,"name":` are baked in as string constants, and decoding picks a field with a Go `switch` on the key, so nothing uses reflection or looks up a field cache at runtime. Decoding goes through jlexer, a pull tokenizer driven by generated code that already knows which type comes next. It finds string ends with bytes.IndexByte and turns keys into strings with an unsafe zero-copy []byte-to-string cast. Encoding appends into a chain of chunks (128 B growing to 32 KB; chunks of 512 B or more are recycled per size class through sync.Pool), and DumpTo writes that chain out as net.Buffers without first joining it into one slice, which is why writer mode posts the best numbers.

## Compared with alternatives

Pick easyjson over go-json, jsoniter or Sonic when you can add a codegen step and want reflection-free, pure-Go marshalers with the fewest allocations on known structs, especially when writing straight to an http.ResponseWriter. Pick go-json (its README lists itself as fully encoding/json-compatible and easyjson as not) or jsoniter when you need an import swap with no generated files, generic types, or byte-identical encoding/json behavior. The sibling ratios come from different benchmarks, so don't compare them directly.

## Integration

| | |
|---|---|
| **Form** | module (Go package plus an `easyjson` codegen CLI that writes \*_easyjson.go source files) |
| **Dependencies** | github.com/josharian/intern (runtime); a full Go toolchain at generation time (generator shells out to `go run`) |
| **Minimum toolchain** | Go 1.20 per go.mod; CI tests only Go 1.23 |
| **Platforms** | any Go target (pure Go; unsafe is optional). CI runs only on ubuntu-latest; the arm64 CI job is commented out |
| **Thread safety** | Not formally documented. Each call builds its own jlexer.Lexer/jwriter.Writer and only the sync.Pool-backed chunk pool is shared, so concurrent calls on distinct values are safe; the README's concurrent benchmarks rely on this. buffer.Init() must run before any marshaling. |
| **Drop-in for the baseline** | partial — the generated MarshalJSON/UnmarshalJSON satisfy json.Marshaler/json.Unmarshaler, so existing json.Marshal calls keep working. Most of the speedup, though, needs a codegen step plus calls to easyjson.Marshal/Unmarshal, and keys, map order and float formatting differ from encoding/json. |

## Gotchas

- Calling the stdlib json.Marshal/json.Unmarshal on generated types goes through MarshalJSON/UnmarshalJSON. The README warns this carries a 'significant performance penalty' compared with easyjson.Marshal/Unmarshal, so switch the call sites.
- With the `nocopy` tag, decoded strings point into the input buffer through an unsafe cast. Reusing or mutating that []byte (for example a pooled read buffer) silently corrupts them, and one retained string keeps the whole input alive.
- Marshaling a struct whose embedded struct pointer is nil panics (#368, open). The decoder always allocates embedded pointer fields with new().
- Current code differs from the 2016 README. SkipRecursive now runs encoding/json's json.Valid on skipped unknown fields and RawMessage subtrees, so passing large raw sub-documents through pays for stdlib validation (#387). Issue #359 reports that since Go 1.17, DumpTo/MarshalToWriter no longer returns chunks to the pool, and that code is unchanged at HEAD. Re-benchmark on your own Go version.

## Known shortcomings

- The README's concurrent marshal figure (\~3.1x) is inflated by about 1.4x: the benchmark credits easyjson with the 13,024-byte input size per op but encoding/json with its \~9 KB output. The 'to a writer' rows compare against json.Marshal rather than json.Encoder.

## Caveats and trade-offs

The README does give exact MB/s, allocs/op and B/op tables, not only rounded ranges. No CPU model is stated. The only Go version mentioned is go1.6, and it is attached to the ffjson (2016-02-04) and go/codec (2016-03-04) result runs, so the tables are from 2016 and do not reflect later encoding/json improvements. Non-concurrent marshaling without a writer is \~2.7-2.8x on the regular and large payloads, below the prose '3-4x'. Results use easyjson's default mode, which uses unsafe.

Requires an ahead-of-time codegen step (easyjson -all file.go), so it is not a drop-in import swap like go-json/sonic; default fast path uses unsafe

## Maintenance

Maintained but slow-moving: v0.9.2 (2026-03-14, added omitzero) followed v0.9.1 (2025-09), with \~100 open issues/PRs including 2022-era generics support; MIT, pure Go, and easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Benchmarks' section compares easyjson directly with encoding/json ('standard' rows) in MB/s tables, and the benchmark code is public (benchmark/default_test.go, benchmark/easyjson_test.go, run via make). No CPU model and no Go version or flags are given for the standard/easyjson rows, so it is first-party with partial methodology: tier C.
- **Verifier notes:** Claim quote is verbatim and matches the README tables. Metadata checks out (MIT, not archived/fork, 4,917 stars, last commit 2026-03-14, active). Go project, not C++.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mailru/easyjson>
  - <https://github.com/mailru/easyjson/blob/master/README.md#benchmarks>
  - <https://github.com/mailru/easyjson/tree/master/benchmark>
  - <https://github.com/mailru/easyjson/blob/master/Makefile>
  - <https://github.com/mailru/easyjson/commits>
- **Sources the enricher read:**
  - <https://github.com/mailru/easyjson>
  - <https://github.com/mailru/easyjson/blob/master/README.md#benchmarks>
  - <https://github.com/mailru/easyjson/blob/master/go.mod>
  - <https://github.com/mailru/easyjson/blob/master/helpers.go>
  - <https://github.com/mailru/easyjson/blob/master/jlexer/lexer.go>
  - <https://github.com/mailru/easyjson/blob/master/jlexer/bytestostr.go>
  - <https://github.com/mailru/easyjson/blob/master/jlexer/bytestostr_nounsafe.go>
  - <https://github.com/mailru/easyjson/blob/master/jwriter/writer.go>
  - <https://github.com/mailru/easyjson/blob/master/buffer/pool.go>
  - <https://github.com/mailru/easyjson/blob/master/gen/decoder.go>
  - <https://github.com/mailru/easyjson/blob/master/gen/encoder.go>
  - <https://github.com/mailru/easyjson/blob/master/bootstrap/bootstrap.go>
  - <https://github.com/mailru/easyjson/blob/master/easyjson/main.go>
  - <https://github.com/mailru/easyjson/blob/master/parser/parser.go>
  - <https://github.com/mailru/easyjson/blob/master/parser/pkgpath.go>
  - <https://github.com/mailru/easyjson/blob/master/Makefile>
  - <https://github.com/mailru/easyjson/blob/master/.github/workflows/easyjson.yml>
  - <https://github.com/mailru/easyjson/tree/master/benchmark>
  - <https://github.com/mailru/easyjson/blob/master/benchmark/go.mod>
  - <https://github.com/mailru/easyjson/blob/master/benchmark/Makefile>
  - <https://github.com/mailru/easyjson/blob/master/benchmark/default_test.go>
  - <https://github.com/mailru/easyjson/blob/master/benchmark/easyjson_test.go>
  - <https://github.com/mailru/easyjson/blob/master/benchmark/data.go>
  - <https://github.com/mailru/easyjson/blob/master/benchmark/data_var.go>
  - <https://github.com/mailru/easyjson/blob/master/benchmark/example.json>
  - <https://github.com/mailru/easyjson/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/mailru/easyjson/issues/292>
  - <https://github.com/mailru/easyjson/issues/369>
  - <https://github.com/mailru/easyjson/issues/434>
  - <https://github.com/mailru/easyjson/issues/387>
  - <https://github.com/mailru/easyjson/issues/380>
  - <https://github.com/mailru/easyjson/issues/359>
  - <https://github.com/mailru/easyjson/issues/426>
  - <https://github.com/mailru/easyjson/issues/374>
  - <https://github.com/mailru/easyjson/issues/368>
  - <https://github.com/mailru/easyjson/issues/414>
  - <https://github.com/mailru/easyjson/issues/394>
  - <https://github.com/mailru/easyjson/issues/318>
  - <https://github.com/mailru/easyjson/issues/425>
  - <https://github.com/mailru/easyjson/issues/382>
  - <https://github.com/mailru/easyjson/issues/237>
  - <https://github.com/mailru/easyjson/commits/master>
  - <https://github.com/mailru/easyjson/tags>
  - <https://github.com/mailru/easyjson/releases>
  - <https://github.com/mailru/easyjson/security/advisories>
  - <https://pkg.go.dev/vuln/list?q=github.com/mailru/easyjson>
  - <https://github.com/goccy/go-json>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/mailru/easyjson`) · [data/wave4/enrich/raw/github_com_mailru_easyjson.json](../../../data/wave4/enrich/raw/github_com_mailru_easyjson.json) (enrichment confidence 0.82)

</details>
