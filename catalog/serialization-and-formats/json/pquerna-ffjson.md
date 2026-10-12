# ffjson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🔴 abandoned

> Go code generator that emits static per-struct MarshalJSON/UnmarshalJSON methods to replace encoding/json's reflection-based codec.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | 1.91x faster than encoding/json on the goser benchmark; 2.11x faster than encoding/json on the go.stripe benchmark |
| **Workload** | Marshal/unmarshal of a Cloudflare log-line struct (goser benchmark) and a Stripe-Customer-like nested struct (go.stripe benchmark) using Go benchmarks. |
| **Metric** | throughput |
| **Adoption** | 2,991 stars |
| **Last commit** | 2019-09-30 |
| **Links** | [repository](https://github.com/pquerna/ffjson) · [benchmark](https://paul.querna.org/articles/2014/03/31/ffjson-faster-json-in-go/) |

## Verdict

The README claims 2-3x over encoding/json for both marshal and unmarshal but gives no Go version, CPU or results table. First-party `make bench` code exists (tests/goser, tests/go.stripe). The 2014 launch post reports marshal-only gains of 1.91x (goser) and 2.11x (go.stripe) with no Go version or hardware. The independent go1.6 (Feb 2016, CPU not stated) table in the easyjson README gives single-goroutine ratios derived from page data: unmarshal 3.0x (regular) and 1.8x (small), marshal 1.1-1.7x, rising to about 2x with ffjson.Pool.

## Use it when

- An existing GOPATH-era Go codebase (Go 1.10-1.12, the versions CI covered) that already commits \*_ffjson.go files and regenerates them through go:generate.
- Unmarshal-heavy services decoding medium-sized documents into structs of concrete fields (strings, numbers, nested structs that also have ffjson code). The go1.6 table in the easyjson README shows about 3x over encoding/json on a 9 kB tweet payload.
- Single-goroutine marshaling of kilobyte-plus payloads when you can call ffjson.Marshal and return buffers with ffjson.Pool. The same table shows about 1.6-2x over encoding/json there.
- You need a transparent speedup behind the standard json.Marshaler/json.Unmarshaler interfaces, and you can accept a codegen step but no runtime dependency outside the Go standard library.

## Skip it when

- New projects. The last commit was in 2019, there are no tags or releases, and the repo root has no go.mod. The easyjson README says easyjson, which uses the same marshal codegen approach, unmarshals 2-3x faster than ffjson.
- Structs with interface fields, custom marshalers, maps with complex values, inline struct types, or slices of slices/maps. These fall back to encoding/json (inline structs, slices of slices and slices of maps only in the decoder), and the README warns that interface fallbacks may be slower than json.Marshal.
- Small payloads marshaled concurrently. In the easyjson go1.6 table, ffjson without Pool reached 62 MB/s on 80-byte payloads against 124 MB/s for encoding/json (about 0.5x). With Pool on \~500 kB payloads it reached 131 against 289 MB/s.
- Allocation-sensitive code paths. The same table records 153 allocs/op for ffjson against 9 for encoding/json when marshaling the regular payload. Issue #256 (2019) measured 1044 vs 1052 ns/op and 7 vs 4 allocs/op against encoding/json.
- Modern Go toolchains without re-benchmarking first. Every published number is from 2014-2016 or the 2019 issue #256, before later encoding/json work. Open issue #260 reports that `make test` fails on Go 1.16.

## How it is fast

Codegen runs in two stages. It parses the file with go/ast, writes a temporary 'inception' main that imports the package, and runs it with `go run -a`. That program reflects over the real types and renders straight-line Go code, so reflection happens at generate time, not per call. The marshal code writes pre-quoted, pre-escaped field names as constants and merges adjacent constant writes. It formats numbers with fflib's own FormatBits2/AppendFloat and writes into power-of-two sync.Pool buffers (64 B to 512 KB). The unmarshal code drives a hand-written lexer derived from yajl, which uses 256-entry byte lookup tables for whitespace and string scanning. The generated state machine matches keys with a switch on the first byte plus bytes.Equal, falls back to case-insensitive fold functions, jumps to per-field handlers with goto, and skips unknown keys.

## Compared with alternatives

Every catalogued sibling (Cista++, struct_pack, YAS, bitsery, FBE, ser20, SerialXML, simdjson's experimental_json_builder) is a C++ library. Pick ffjson only when the codebase is Go and must keep encoding/json-compatible JSON. Even then, easyjson (not catalogued) claims faster unmarshal and better concurrency with the same codegen model.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Go standard library only; generated files import github.com/pquerna/ffjson/fflib/v1 at runtime) |
| **Minimum toolchain** | Go 1.3+ for sync.Pool buffer pooling (a build-tagged stub covers older versions). CI tested Go 1.10.x/1.11.x and fuzzed on 1.12.x. No root go.mod; module import-path detection via `go list` was added in Aug 2019. |
| **Platforms** | any Go target (pure Go, no unsafe, no assembly) |
| **Thread safety** | Generated methods and ffjson.Marshal/Unmarshal keep no shared state beyond the sync.Pool buffers. ffjson.Encoder and ffjson.Decoder must not be used by more than one goroutine at a time (doc comments). |
| **Drop-in for the baseline** | partial — the generated methods satisfy json.Marshaler/json.Unmarshaler, so json.Marshal callers speed up unchanged. Full gains need ffjson.Marshal/Unmarshal, which bypass encoding/json's output checks, plus a codegen step whenever a struct changes. |

## Gotchas

- The generated methods have pointer receivers (`func (j *T) MarshalJSON`), and ffjson.Marshal type-asserts its argument. Passing a struct value instead of &v silently falls back to encoding/json. Issue #256's 'ffjson is slower' benchmark called ffjson.Marshal(d) on a value.
- Encoder.SetEscapeHTML only configures the wrapped encoding/json encoder. The fast path's WriteJson always escapes &lt;, &gt;, & and U+2028/U+2029.
- Output is not always byte-identical to encoding/json. Open issue #202 reports `{ "a":...}` with a leading space when the last field is omitempty and empty. Open issue #257 reports a nil-pointer panic when unmarshaling \*time.Time slice elements.
- Codegen needs the package to compile. It creates an ffjson-inception\* temp directory next to the input file, and struct types referenced across files must be generated in dependency order (README Tip 5). After ffjson.Pool(buf), do not touch buf, because other goroutines may reuse it.

## Known shortcomings

- The independent go1.6 table in the easyjson README shows only 1.1-1.7x single-goroutine marshal, and ffjson is slower than encoding/json for concurrent marshal without Pool (62 vs 124 MB/s) with far more allocations (153 vs 9 allocs/op). Passing a struct value instead of a pointer silently falls back to encoding/json. SetEscapeHTML only affects the fallback. Open bugs #202, #257, #260; no go.mod, CI covered only Go 1.10-1.12; easyjson unmarshals 2-3x faster.

## Caveats and trade-offs

The README says only '2x to 3x' faster than encoding/json. It gives no results table, Go version, or hardware. Benchmark code does exist: tests/goser and tests/go.stripe each have BenchmarkMarshalJSON/BenchmarkFFMarshalJSON/BenchmarkUnmarshalJSON/BenchmarkFFUnmarshalJSON, run by 'make bench'. The 2014 launch blog post gives 1.91x (goser) and 2.11x (go.stripe) for Marshal only, because Unmarshal did not exist yet. It states no Go version or hardware. A third-party table in the easyjson README (go1.6, Feb 2016, no CPU stated) measures ffjson against encoding/json. Unmarshal: 66 vs 22 MB/s regular (\~3.0x) and 17.6 vs 9.7 MB/s small (\~1.8x). Marshal: 122 vs 75 (\~1.6x), 36 vs 32 (\~1.1x) and 134 vs 80 MB/s large (\~1.7x). Those ratios are derived from page data, so marshal gains were below the README's 2-3x there. ffjson falls back to encoding/json for interface members, custom marshalers, complex map values, and some nested slices/inline structs. The README warns that with interfaces it 'may even become slower than using json.Marshal directly'. The last commit on master is 2019-09-30 (repo pushed_at 2023-09-21 has no matching commit on any branch), so all numbers predate many encoding/json improvements.

Requires a code-generation step (the ffjson tool generates MarshalJSON/UnmarshalJSON per struct) instead of runtime reflection, adding a build step and generated-code maintenance burden; larger binary size from generated code.

## Maintenance

Abandoned since the last master commit on 2019-09-30 (59 open issues, no tagged release), but Apache-2.0, pure Go with no dependencies and easy to vendor; last CI-tested toolchains were Go 1.10-1.12.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's Performance Status section says MarshalJSON and UnmarshalJSON are each '2x to 3x' faster than encoding/json. It gives no Go version, CPU, or results table. The repo does contain benchmark code against encoding/json: tests/goser/goser_test.go, tests/go.stripe/stripe_test.go, and the Makefile 'bench' target. That makes this first-party evidence with partial methodology, so it is tier C, not A or B.
- **Verifier notes:** The benchmark URL (README) matches the claimed_speedup exactly. The record's last_commit (2023-09-21) was the repo pushed_at timestamp, but the actual last commit on master is 2019-09-30, and no branch, tag, or release is newer. The record said there was no benchmark code, which is wrong, so caveats are corrected. Metadata checked: Apache-2.0, not archived, not a fork. The status stays abandoned.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pquerna/ffjson#readme>
  - <https://github.com/pquerna/ffjson>
  - <https://github.com/pquerna/ffjson/blob/master/Makefile>
  - <https://github.com/pquerna/ffjson/tree/master/tests>
  - <https://github.com/pquerna/ffjson/blob/master/tests/goser/goser_test.go>
  - <https://github.com/pquerna/ffjson/blob/master/tests/go.stripe/stripe_test.go>
  - <https://github.com/pquerna/ffjson/blob/master/tests/bench.cmd>
  - <https://journal.paul.querna.org/articles/2014/03/31/ffjson-faster-json-in-go/>
  - <https://paul.querna.org/articles/2014/03/31/ffjson-faster-json-in-go/>
  - <https://github.com/mailru/easyjson#readme>
  - <https://github.com/alecthomas/go_serialization_benchmarks>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/benchmarks.go>
- **Sources the enricher read:**
  - <https://github.com/pquerna/ffjson>
  - <https://github.com/pquerna/ffjson#readme>
  - <https://github.com/pquerna/ffjson/blob/master/Makefile>
  - <https://github.com/pquerna/ffjson/blob/master/.travis.yml>
  - <https://github.com/pquerna/ffjson/blob/master/ffjson.go>
  - <https://github.com/pquerna/ffjson/blob/master/ffjson/marshal.go>
  - <https://github.com/pquerna/ffjson/blob/master/ffjson/pool.go>
  - <https://github.com/pquerna/ffjson/blob/master/ffjson/encoder.go>
  - <https://github.com/pquerna/ffjson/blob/master/ffjson/decoder.go>
  - <https://github.com/pquerna/ffjson/blob/master/generator/generator.go>
  - <https://github.com/pquerna/ffjson/blob/master/generator/inceptionmain.go>
  - <https://github.com/pquerna/ffjson/blob/master/inception/inception.go>
  - <https://github.com/pquerna/ffjson/blob/master/inception/reflect.go>
  - <https://github.com/pquerna/ffjson/blob/master/inception/encoder.go>
  - <https://github.com/pquerna/ffjson/blob/master/inception/decoder.go>
  - <https://github.com/pquerna/ffjson/blob/master/inception/decoder_tpl.go>
  - <https://github.com/pquerna/ffjson/blob/master/fflib/v1/buffer_pool.go>
  - <https://github.com/pquerna/ffjson/blob/master/fflib/v1/buffer_nopool.go>
  - <https://github.com/pquerna/ffjson/blob/master/fflib/v1/lexer.go>
  - <https://github.com/pquerna/ffjson/blob/master/fflib/v1/reader.go>
  - <https://github.com/pquerna/ffjson/blob/master/fflib/v1/reader_scan_generic.go>
  - <https://github.com/pquerna/ffjson/blob/master/fflib/v1/jsonstring.go>
  - <https://github.com/pquerna/ffjson/blob/master/fflib/v1/iota.go>
  - <https://github.com/pquerna/ffjson/blob/master/fflib/v1/fold.go>
  - <https://github.com/pquerna/ffjson/blob/master/tests/goser/goser_test.go>
  - <https://github.com/pquerna/ffjson/blob/master/tests/bench.cmd>
  - <https://github.com/pquerna/ffjson/commits/master>
  - <https://github.com/pquerna/ffjson/commit/3b68c53>
  - <https://github.com/pquerna/ffjson/issues/136>
  - <https://github.com/pquerna/ffjson/issues/202>
  - <https://github.com/pquerna/ffjson/issues/246>
  - <https://github.com/pquerna/ffjson/issues/256>
  - <https://github.com/pquerna/ffjson/issues/257>
  - <https://github.com/pquerna/ffjson/issues/260>
  - <https://github.com/mailru/easyjson#readme>
  - <https://paul.querna.org/articles/2014/03/31/ffjson-faster-json-in-go/>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/pquerna/ffjson`) · [data/wave4/enrich/raw/github_com_pquerna_ffjson.json](../../../data/wave4/enrich/raw/github_com_pquerna_ffjson.json) (enrichment confidence 0.6)

</details>
