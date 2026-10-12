# segmentio/encoding (encoding/json replacement)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Drop-in encoding/json replacement for Go that swaps reflection for unsafe-pointer codecs; \~1.7x marshal, \~5x unmarshal on typed structs.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | Vs encoding/json v1.16.2 (Go 1.16.2 stdlib), Core i9-8950HK, benchstat n=5+5: Marshal/\*json.codeResponse2 6.40ms -&gt; 3.82ms (-40.29%), Unmarshal 28.1ms -&gt; 5.6ms (-80.21%); speed 303 -&gt; 507 MB/s (+67.47%) marshal and 69.2 -&gt; 349.6 MB/s (+405.42%) unmarshal (\~1.68x marshal, \~5.0x unmarshal, derived from page data); Unmarshal alloc 1.80MB -&gt; 0.02MB (-99.14%) and 76.6k -&gt; 0.1k allocs/op (-99.92%). Vs json-iterator/go v1.1.10: Marshal 6.19ms -&gt; 3.82ms (-38.26%; 313 -&gt; 507 MB/s, +61.91%, \~1.62x derived from page data), Unmarshal 8.52ms -&gt; 5.55ms (-34.84%; 228 -&gt; 350 MB/s, +53.50%, \~1.54x derived from page data). |
| **Workload** | Marshal (Append into a reused buffer) and Unmarshal of the Go stdlib's encoding/json testdata/code.json.gz corpus, loaded into the repo's codeResponse2 struct (json/json_test.go BenchmarkMarshal/BenchmarkUnmarshal, `(Marshal\|Unmarshal)$/codeResponse` subtests), single CPU (-cpu 1), 5 runs per side, compared with benchstat against encoding/json (Go 1.16.2) and json-iterator/go v1.1.10. The numbers were re-run by hand from the `benchmarks` branch in March 2021 (PR #77). The current CI does not produce them: it only benchmarks master against the PR head. |
| **Metric** | throughput |
| **Hardware** | Core i9-8950HK CPU @ 2.90GHz |
| **Compiler and flags** | Go 1.16.2 (the page pins the baseline as encoding/json v1.16.2, which is the Go 1.16.2 stdlib; both implementations are built into one `go test` binary and selected with the harness's -package flag); default gc build flags; run as `go test -v -run '^$' -bench '(Marshal\|Unmarshal)$/codeResponse' -benchmem -cpu 1 -count 5 ./json [-package encoding/json \| -package github.com/json-iterator/go]` (Makefile target bench-simple on the `benchmarks` branch, per PR #77), compared with benchstat |
| **Adoption** | 1.1k stars; used in production at Segment/Twilio |
| **Last commit** | 2026-03-10 |
| **Links** | [repository](https://github.com/segmentio/encoding) · [benchmark](https://github.com/segmentio/encoding/blob/master/README.md) |

## Verdict

On one core of a Core i9-8950HK with Go 1.16.2, encoding the stdlib's code.json testdata from a typed struct took 3.82 ms vs 6.40 ms for encoding/json (\~1.68x), and decoding it took 5.6 ms vs 28.1 ms (\~5.0x) with about 99% fewer bytes and allocations; json-iterator v1.1.10 was \~1.6x slower on marshal and \~1.5x on unmarshal. HTML escaping was off on both sides, the segmentio decode used Parse with ZeroCopy while stdlib copied strings, and the numbers are a March 2021 re-run (PR #77) that has not been refreshed.

## Use it when

- High-volume services that decode JSON into concrete Go structs: the published \~5x unmarshal gain and \~99% allocation cut are on a struct target, and a user in issue #124 measured 1.8 us vs 9.2 us for stdlib on a small typed payload.
- Codebases that want a speedup with no call-site changes and no build step: swap the import path, no code generation, no new API to learn.
- Request-handler code where decoded values do not outlive the input buffer, so Parse(..., ZeroCopy) or Decoder.ZeroCopy() can skip string, Number and RawMessage copies.
- Encode-heavy paths that can call Append into a reused buffer with EscapeHTML and SortMapKeys off (the configuration the benchmark measures); Marshal adds HTML escaping, map-key sorting and a final copy out of a pooled buffer.
- Little-endian 64-bit targets (amd64, arm64), where keyset and base64 get SIMD paths and CI runs the test suite (ubuntu-latest, Go 1.23 and 1.24).

## Skip it when

- Decoding into interface{} or map[string]any: allocation dominates, and issue #124 measured parity with stdlib (6.5 us vs 6.4 us on a 552-byte document); v0.4.0+ also had a map[string]any allocation regression that PR #149 fixed in July 2025.
- Token-level or streaming decoding: Decoder has no Token() or More() methods, cannot step through elements of a large top-level array, and buffers each whole value in memory (32 KiB minimum buffer, doubling).
- Code that depends on exact stdlib output: time.Duration encodes as a quoted duration string instead of int64 nanoseconds (issue #90), Go 1.24 omitzero tags are ignored because only omitempty and string are parsed (issue #148), and error messages differ.
- Big-endian or 32-bit targets: escapeIndex assumes little-endian byte order and emits unescaped quotes and backslashes on s390x (issue #170, open), and TestMarshalEmbeds fails on i386 and armhf (issue #158, open).
- Decisions that need numbers on current Go: the only published head-to-head is Go 1.16.2 from March 2021, stdlib encoding/json has changed since, and CI only compares master against the PR head.

## How it is fast

Each Go type gets a codec of pre-built encode/decode closures that walk the value through unsafe.Pointer field offsets instead of reflect.Value; codecs sit in a copy-on-write map keyed by the type's runtime pointer and loaded through atomic.Pointer. Struct keys are matched with segmentio/asm keyset.Lookup, a SIMD compare (AVX on amd64, ASIMD on arm64) against 16-byte zero-padded field names, used when a struct has at most 32 fields and names are at most 16 bytes; otherwise a Go map is used. String escaping and closing-quote search use SWAR bit tricks on 8-byte words, and an up-front scan of the whole input for printable ASCII and backslashes lets most strings be taken verbatim. Decoding writes straight into typed struct fields, and the ZeroCopy flag (used in the published benchmark) lets strings alias the input buffer instead of allocating.

## Compared with alternatives

Pick it over easyjson when you want no code-generation step, and over Sonic when you want pure Go with no JIT and no Go-version gate (Sonic's README lists Go 1.18-1.27, excludes 1.24.0, and supports only amd64/arm64). Against go-json and json-iterator the only direct evidence is this README's 2021 run (\~1.6x marshal, \~1.5x unmarshal over jsoniter v1.1.10), so benchmark your own types before choosing.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/segmentio/asm v1.1.3 (SIMD keyset, base64, ASCII validation; pulls golang.org/x/sys indirectly). The README's 'no dependencies outside the core runtime' line is out of date per go.mod. |
| **Minimum toolchain** | Go 1.23 (go.mod); CI tests Go 1.23 and 1.24; README says versions outside Go's own support window are unlikely to get fixes |
| **Platforms** | Any Go target through pure-Go fallbacks; SIMD paths on amd64 (AVX) and arm64 (ASIMD); open bugs on big-endian s390x (#170) and 32-bit i386/armhf (#158) |
| **Thread safety** | Package-level Marshal/Unmarshal/Append/Parse are safe for concurrent use: the type-codec cache is a copy-on-write map published through atomic.Pointer. Concurrent use of one Encoder or Decoder is not documented; both hold mutable buffers and state. |
| **Drop-in for the baseline** | partial — same exported API via an import-path swap, but Decoder lacks Token()/More() and array streaming, time.Duration encodes as a string, omitzero is ignored, error text differs, and Encoder.Encode returns nil on the first writer error (issue #139). |

## Gotchas

- ZeroCopy, DontCopyString, DontCopyNumber and DontCopyRawMessage make decoded values alias the input []byte; reusing or mutating that buffer corrupts them. Plain Unmarshal copies, but the README benchmark used ZeroCopy.
- Encoder.Encode shadows the writer error (`if _, err := enc.writer.Write(b); err != nil`), so the failing call returns nil and only the next Encode reports it (issue #139, still in master).
- The internals rely on unsafe pointer arithmetic; issue #134 (open since 2023) reports an intermittent 'fatal error: found pointer to free object' under load that stopped after switching back to stdlib.
- Before v0.5.4 a key with a trailing NUL ("field\u0000") matched struct field "field" because the SIMD keyset zero-pads keys (issue #161, fixed by PR #162 in March 2026); use v0.5.4 or later where exact key matching matters.

## Caveats and trade-offs

First-party numbers from March 2021 (Go 1.16.2, i9-8950HK laptop CPU, PR #77) that have not been refreshed. Both the stdlib and this library have changed since, and the repo now declares go 1.23. The README says the CI compares against the stdlib, but the current .github/workflows/benchmark.yml only compares master with the PR head (ubuntu-latest, Go 1.24). Only one corpus is shown (code.json.gz into codeResponse2). In the harness, segmentio's Unmarshal calls Parse(..., ZeroCopy), so strings alias the input buffer, while the stdlib side calls json.Unmarshal, which copies; zero-copy mode accounts for part of the Unmarshal time and allocation gap. Error messages differ from encoding/json.

Drop-in API-compatible replacement for encoding/json (just change the import path), but relies heavily on unsafe pointer arithmetic instead of reflect, and does not (yet) support streaming decode of JSON arrays the way the stdlib Decoder does.

## Maintenance

Active but slow-moving (latest release v0.5.4 on 2026-03-12, a few master commits per year, 21 open issues including correctness bugs), MIT-licensed, used in production at Segment, and installed as an ordinary Go module.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to A. The benchmark code is public: json/json_test.go has a TestMain -package switch plus BenchmarkMarshal/BenchmarkUnmarshal, and the Makefile bench-simple target on the `benchmarks` branch (the branch PR #77 says the README numbers were re-run from) gives the exact go test flags; its -count 5 matches the n=5+5 in the tables. The README names the CPU (Core i9-8950HK) and pins the baseline as 'encoding/json (v1.16.2)'. That label can only mean the Go 1.16.2 toolchain, because both implementations are compiled into one test binary.
- **Verifier notes:** The A tier depends on reading 'encoding/json (v1.16.2)' as the Go 1.16.2 toolchain. If a literal 'Go X.Y' statement is required, this entry falls back to C. I fixed the json-iterator marshal ratio from \~1.53x to \~1.62x. I also corrected last_commit to the master head, 2026-03-10; the repo's pushed_at of 2026-06-25 comes from the non-default branch cstj/migrate-runs-on-twilio-runners.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/segmentio/encoding>
  - <https://github.com/segmentio/encoding/commits/master>
  - <https://github.com/segmentio/encoding/blob/master/README.md>
  - <https://github.com/segmentio/encoding/blob/master/json/README.md>
  - <https://github.com/segmentio/encoding/blob/master/json/json_test.go>
  - <https://github.com/segmentio/encoding/blob/master/json/golang_bench_test.go>
  - <https://github.com/segmentio/encoding/blob/master/Makefile>
  - <https://github.com/segmentio/encoding/blob/master/benchmarks/Makefile>
  - <https://github.com/segmentio/encoding/blob/master/.github/workflows/benchmark.yml>
  - <https://github.com/segmentio/encoding/blob/master/go.mod>
  - <https://github.com/segmentio/encoding/tree/benchmarks>
  - <https://github.com/segmentio/encoding/blob/benchmarks/Makefile>
  - <https://github.com/segmentio/encoding/blob/benchmarks/json/json_test.go>
  - <https://github.com/segmentio/encoding/blob/benchmarks/go.mod>
  - <https://github.com/segmentio/encoding/commit/2569331ecf>
  - <https://github.com/segmentio/encoding/pull/77>
  - <https://github.com/segmentio/encoding/tree/cstj/migrate-runs-on-twilio-runners>
- **Sources the enricher read:**
  - <https://github.com/segmentio/encoding>
  - <https://github.com/segmentio/encoding/blob/master/README.md>
  - <https://github.com/segmentio/encoding/blob/master/json/README.md>
  - <https://github.com/segmentio/encoding/blob/master/json/json.go>
  - <https://github.com/segmentio/encoding/blob/master/json/codec.go>
  - <https://github.com/segmentio/encoding/blob/master/json/decode.go>
  - <https://github.com/segmentio/encoding/blob/master/json/encode.go>
  - <https://github.com/segmentio/encoding/blob/master/json/parse.go>
  - <https://github.com/segmentio/encoding/blob/master/json/string.go>
  - <https://github.com/segmentio/encoding/blob/master/json/token.go>
  - <https://github.com/segmentio/encoding/blob/master/json/reflect.go>
  - <https://github.com/segmentio/encoding/blob/master/json/reflect_optimize.go>
  - <https://github.com/segmentio/encoding/blob/master/json/json_test.go>
  - <https://github.com/segmentio/encoding/blob/master/ascii/valid_print.go>
  - <https://github.com/segmentio/encoding/blob/master/internal/runtime_reflect/map.go>
  - <https://github.com/segmentio/encoding/blob/master/internal/runtime_reflect/slice.go>
  - <https://github.com/segmentio/encoding/blob/master/go.mod>
  - <https://github.com/segmentio/encoding/blob/master/.github/workflows/benchmark.yml>
  - <https://github.com/segmentio/encoding/blob/master/.github/workflows/test.yml>
  - <https://github.com/segmentio/encoding/blob/master/benchmarks/Makefile>
  - <https://github.com/segmentio/encoding/blob/master/benchmarks/results/encoding-json.log>
  - <https://github.com/segmentio/encoding/blob/master/benchmarks/results/segment-encoding-json.log>
  - <https://github.com/segmentio/encoding/blob/master/benchmarks/results/encoding-json+gzip.txt>
  - <https://github.com/segmentio/encoding/blob/master/benchmarks/results/segment-encoding-json+gzip.txt>
  - <https://github.com/segmentio/encoding/blob/master/benchmarks/results/json-iterator+gzip.txt>
  - <https://github.com/segmentio/encoding/blob/benchmarks/Makefile>
  - <https://github.com/segmentio/encoding/commits/master>
  - <https://github.com/segmentio/encoding/tags>
  - <https://github.com/segmentio/encoding/releases>
  - <https://github.com/segmentio/encoding/issues>
  - <https://github.com/segmentio/encoding/issues/90>
  - <https://github.com/segmentio/encoding/issues/124>
  - <https://github.com/segmentio/encoding/issues/133>
  - <https://github.com/segmentio/encoding/issues/134>
  - <https://github.com/segmentio/encoding/issues/139>
  - <https://github.com/segmentio/encoding/issues/148>
  - <https://github.com/segmentio/encoding/issues/158>
  - <https://github.com/segmentio/encoding/issues/161>
  - <https://github.com/segmentio/encoding/issues/170>
  - <https://github.com/segmentio/encoding/issues/174>
  - <https://github.com/segmentio/encoding/pull/77>
  - <https://github.com/segmentio/encoding/pull/149>
  - <https://github.com/segmentio/encoding/pull/162>
  - <https://github.com/segmentio/asm>
  - <https://github.com/segmentio/asm/blob/main/keyset/keyset.go>
  - <https://github.com/segmentio/asm/blob/main/keyset/keyset_amd64.go>
  - <https://github.com/segmentio/asm/blob/main/build/keyset/keyset_asm.go>
  - <https://github.com/bytedance/sonic>
  - <https://github.com/goccy/go-json>
  - <https://github.com/mailru/easyjson>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/segmentio/encoding`) · [data/wave4/enrich/raw/github_com_segmentio_encoding.json](../../../data/wave4/enrich/raw/github_com_segmentio_encoding.json) (enrichment confidence 0.85)

</details>
