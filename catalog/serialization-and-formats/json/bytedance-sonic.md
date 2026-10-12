# Sonic

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> ByteDance's JIT- and SIMD-accelerated Go JSON library; about 1.9-3.4x the throughput of encoding/json on amd64.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | BenchmarkEncoder_Generic_Sonic 32393 ns/op vs StdLib 106322 ns/op (\~3.3x); BenchmarkDecoder_Generic_Sonic 66812 ns/op vs StdLib 124260 ns/op (\~1.9x); BenchmarkDecoder_Binding_Sonic 32557 ns/op vs StdLib 111437 ns/op (\~3.4x); BenchmarkEncoder_Parallel_Binding_Sonic 8810.09 MB/s vs StdLib 3486.49 MB/s (\~2.5x), or 10785.23 MB/s (\~3.1x) with Sonic_Fast options (derived from page data) |
| **Workload** | Generic and struct-binding encode/decode of a 13KB/300+key/6-layer JSON document, single-threaded and parallel Go benchmarks, plus small (400B) and large (635KB Twitter) payload variants |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i9-9880H CPU @ 2.30GHz, darwin/amd64 |
| **Compiler and flags** | go1.17.1; scripts/bench.sh: SONIC_NO_ASYNC_GC=1 go test -benchmem -run=^\$ -benchtime=100000x -bench '^(BenchmarkEncoder_.\*\|BenchmarkDecoder_.\*)\$' |
| **Adoption** | 9.6k stars |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/bytedance/sonic) · [benchmark](https://github.com/bytedance/sonic/blob/main/README.md#benchmarks) |

## Verdict

The README's 13 KB, 300+ key document was benchmarked with std-equivalent options (encode: SortMapKeys|EscapeHTML|CompactMarshaler; decode: CopyString) on Go 1.17.1, darwin/amd64, Intel i9-9880H, using scripts/bench.sh with -benchtime=100000x. Sonic ran generic encode 3.3x, generic decode 1.9x and struct decode 3.4x faster than encoding/json, and parallel struct encode 2.5x. The 3.1x parallel figure uses the Fast path, which skips sorting and escaping, so it is not a like-for-like comparison. An independent 2026 run (sonic v1.15.4, i7-6820HQ, 39.9 MB SEC corpus) found about 1.8-2.0x over encoding/json.

## Use it when

- Long-running amd64 Linux/macOS/Windows services where JSON takes a large share of CPU. The JIT compile cost is paid once per type and then amortized.
- Generic interface{}/map[string]any payloads. On the README's 13 KB document with std-equivalent options, generic decode is 1.9x and generic encode 3.3x encoding/json.
- Struct binding on medium-to-large documents on amd64. Binding decode is 3.4x std on the 13 KB document, and 594 vs 102 MB/s on the 635 KB Twitter file (README chart).
- Reading or patching a few fields of a large document without a full decode (ast.Get/Set, GetByPath). The README shows GetOne at 3,276 ns/op vs gjson at 9,431, and SetOne at 9,571 vs sjson at 36,456.
- High-concurrency encoders. In the README, parallel struct encode with std options reaches 8,810 MB/s vs 3,486 MB/s for encoding/json.

## Skip it when

- arm64 servers (Graviton, Ampere, Apple silicon). arm64 has no JIT: decoding uses the interpreted 'optdec' decoder and encoding uses a VM. Maintainers say schema-typed encode is weaker there, and users report cases slower than encoding/json (issues #785, #786).
- Code that must match encoding/json byte for byte or in error-state behaviour. The Go 1.27 compatibility doc lists open ConfigStd gaps. Examples: map values are merged instead of replaced, and the JIT decoder writes fields before a later syntax error. The ',string' number grammar differs, and MarshalJSON errors are not wrapped in \*json.MarshalerError.
- Short-lived CLIs, serverless cold starts, or latency-sensitive first requests over many or very deep types. JIT compilation happens on first use: issue #138 measured a 3.5 s first Marshal/Unmarshal on a very deep struct. The README warns that huge schemas can cause request timeouts or OOM unless you call PretouchMany first.
- Teams that adopt a new Go release on day one, or that run old or exotic CPUs. Sonic depends on private runtime layouts (moduledata, map iterator), and Go 1.24.0 is unsupported. On go1.28+, non-amd64/arm64 targets, or arm64 with Go below 1.20, Sonic silently becomes encoding/json. Issue #983 (open) reports SIGILL in the SSE path on a Core 2 Quad CPU without PCLMULQDQ.
- Memory-tight struct decoding. In the README, binding decode allocates 28,302 B/op vs 10,576 B/op for encoding/json. Pooled encode buffers can stay large under high QPS when large and small documents are mixed (issue #614).

## How it is fast

On first use of each Go type, Sonic JIT-compiles a codec for that type from its reflected schema, using golang-asm on amd64. The codec is cached in an open-addressing hash with RCU and uses a register-based internal call convention. This avoids the reflection and interface/function-call overhead that limits encoding/json and jsoniter-style codecs. The hot kernels (string scan/quote/unquote, f64toa/i64toa, number parsing, skipping, UTF-8 validation) are written in C, compiled with Clang, and translated to Plan 9 assembly by asm2asm. At runtime, cpuid picks the AVX2 or SSE build (NEON on arm64), and SIMD is combined with scalar code for short inputs. The ast package parses lazily and uses SIMD skipping, so a partial Get or Set parses only the path it needs.

## Compared with alternatives

Pick Sonic over go-json and jsoniter on amd64 when payloads are generic (interface{}/map) or large. In the README, generic decode takes 66.8 µs vs 88.6 µs for go-json and 91.3 µs for jsoniter, and large binding decode runs at 594 vs 88 MB/s for go-json. Prefer go-json for small or medium struct-binding decode and on arm64: it matches or beats Sonic's std mode in the README (28.7 vs 32.6 µs) and in tegridy-benchie at 1-4 threads. Prefer easyjson when code generation is acceptable and you want no runtime JIT.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/bytedance/sonic/loader, github.com/bytedance/gopkg, github.com/cloudwego/base64x, github.com/klauspost/cpuid/v2, github.com/twitchyliquid64/golang-asm, golang.org/x/arch (no cgo; the native kernels ship as pre-generated Go assembly) |
| **Minimum toolchain** | Go 1.18 (go.mod); the README lists Go 1.18-1.27 as supported; Go 1.24.0 is excluded unless you build with -ldflags=-checklinkname=0; arm64 needs Go 1.20+; Go 1.28+ currently falls back to encoding/json |
| **Platforms** | amd64 (JIT, AVX2 or SSE kernels chosen by cpuid; SONIC_MODE=noavx forces SSE) and arm64 (NEON kernels, no JIT, Go 1.20+), on Linux, macOS and Windows; all other targets fall back to encoding/json |
| **Thread safety** | Top-level Marshal/Unmarshal and frozen Config APIs are used concurrently (the README has parallel benchmarks, and the codec cache is described as concurrent-safe with open addressing and RCU). ast.Node is not safe for concurrent reads because it loads lazily; call LoadAll() or use the ConcurrentRead search option first. Crashes during concurrent first-time JIT decodes (#912 on Go 1.24+, #985 on Go 1.27.1 amd64) were closed in Aug-Sep 2026. |
| **Drop-in for the baseline** | partial — same Marshal/Unmarshal/Valid signatures and a ConfigStd preset, but ConfigDefault skips HTML escaping and map-key sorting, and decoded strings alias the input buffer. The public Decoder lacks Token/InputOffset, and ConfigStd still has documented edge-case differences (see when_not_to_use). |

## Gotchas

- Decoded strings without escapes point into the source buffer (CopyString is off in ConfigDefault). Caching the decoded objects keeps the whole JSON buffer alive; the README estimates 20-80% extra memory. Enable CopyString or ConfigStd for long-lived data.
- Fallback is silent. On an unsupported arch, an unsupported Go version (go1.28+ today), or arm64 with Go below 1.20, you get encoding/json with Sonic's API, and Pretouch does nothing. Check sonic.APIKind == sonic.UseSonicJSON in CI or at startup.
- Validation shortcuts: when skipping unknown fields, the SIMD path does not check escape sequences in long strings, so ConfigStd accepts invalid escapes such as '\0' (#938, open). NoValidateJSONSkip and NoValidateJSONMarshaler (in ConfigFastest) turn off more checks. Decoding into float32 can round differently from encoding/json (#884, open).
- Always pass a pointer when you marshal an ast.Node through encoding/json. Also call PretouchMany at init for large or deep types, and tune option.WithCompileMaxInlineDepth or WithCompileRecursiveDepth if JIT compilation is slow.

## Caveats and trade-offs

The README benchmark uses an old Go toolchain (1.17.1) on one Mac laptop, and current sonic requires Go 1.18-1.27. The \*_Fast rows drop SortMapKeys/EscapeHTML (NoQuoteTextMarshaler), so they are not like-for-like with encoding/json. The std-option Sonic rows are the fair comparison. Sonic is JIT/assembly-based for amd64 and arm64 (arm64 needs go1.20+). On unsupported environments it falls back to encoding/json. A third-party real-workload shootout (mihailnica10/tegridy-benchie RESULTS.md, 2026-09-23, 0 stars, single commit, sonic v1.15.4, go.mod go 1.27.1, i7-6820HQ) corroborates a \~1.8-2.0x native win over encoding/json on a 39.9MB SEC company-facts corpus. Its figures are 86.1 vs 44.5 MB/s at 1 thread, 180.2 vs 100.7 at 4 threads, and 260.0 vs 128.8 at 8 threads, and \~1.7x via Bun FFI (73.2 vs 42.5 MB/s) (derived). In that shootout sonic trails goccy/go-json at 1-4 threads.

JIT + SIMD based, so has extra startup/warm-up and binary-size overhead; amd64/arm64 only; HTML-escaping and key-sort defaults differ from encoding/json

## Maintenance

Actively maintained by ByteDance/CloudWeGo: v1.15.4 was released 2026-09-11 and Go 1.27 support landed July 2026. The Apache-2.0 module is easy to adopt, but every new Go release needs a matching Sonic update because it depends on private runtime internals.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Benchmarks block runs Sonic against encoding/json (StdLib rows) and states goversion 1.17.1 and the CPU (i9-9880H, darwin/amd64). The code is public: encoder/encoder_test.go, decoder/decoder_test.go, and external_jsonlib_test/benchmark_test/\*, driven by scripts/bench.sh with go test -benchmem -benchtime=100000x. With code, compiler, flags and CPU all stated, the tier is A.
- **Verifier notes:** The README numbers match exactly, and the Generic Sonic encoder benchmark uses std-equivalent options (SortMapKeys|EscapeHTML). The claimed_speedup now adds the fair parallel-binding figure (\~2.5x) next to the Fast-mode \~3.1x. I corrected last_commit to the committer date of the newest main commit (f1003e1, 2026-09-10); pushed_at of 2026-09-11 reflects other branches. The '\~2.0x' tegridy figure was slightly high and now reads \~1.8-2.0x.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bytedance/sonic>
  - <https://github.com/bytedance/sonic/blob/main/README.md#benchmarks>
  - <https://github.com/bytedance/sonic/blob/main/scripts/bench.sh>
  - <https://github.com/bytedance/sonic/blob/main/encoder/encoder_test.go>
  - <https://github.com/bytedance/sonic/blob/main/decoder/decoder_test.go>
  - <https://github.com/bytedance/sonic/blob/main/external_jsonlib_test/benchmark_test/encoder_test.go>
  - <https://github.com/bytedance/sonic/blob/main/external_jsonlib_test/benchmark_test/decoder_test.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/decoders.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/bench.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/parser.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/go.mod>
- **Sources the enricher read:**
  - <https://github.com/bytedance/sonic>
  - <https://github.com/bytedance/sonic/blob/main/README.md#benchmarks>
  - <https://github.com/bytedance/sonic/blob/main/docs/INTRODUCTION.md>
  - <https://github.com/bytedance/sonic/blob/main/docs/sonic-go127-compatibility.md>
  - <https://github.com/bytedance/sonic/blob/main/docs/imgs/bench-small.png>
  - <https://github.com/bytedance/sonic/blob/main/docs/imgs/bench-large.png>
  - <https://github.com/bytedance/sonic/blob/main/go.mod>
  - <https://github.com/bytedance/sonic/blob/main/api.go>
  - <https://github.com/bytedance/sonic/blob/main/compat.go>
  - <https://github.com/bytedance/sonic/blob/main/internal/decoder/api/decoder_amd64.go>
  - <https://github.com/bytedance/sonic/blob/main/internal/decoder/api/decoder_arm64.go>
  - <https://github.com/bytedance/sonic/blob/main/internal/envs/decode.go>
  - <https://github.com/bytedance/sonic/blob/main/internal/encoder/encoder.go>
  - <https://github.com/bytedance/sonic/blob/main/internal/encoder/vars/const.go>
  - <https://github.com/bytedance/sonic/blob/main/internal/encoder/pools_compt.go>
  - <https://github.com/bytedance/sonic/blob/main/internal/cpu/features.go>
  - <https://github.com/bytedance/sonic/blob/main/internal/native/dispatch_amd64.go>
  - <https://github.com/bytedance/sonic/blob/main/scripts/bench.sh>
  - <https://github.com/bytedance/sonic/blob/main/encoder/encoder_test.go>
  - <https://github.com/bytedance/sonic/blob/main/decoder/decoder_test.go>
  - <https://github.com/bytedance/sonic/blob/main/decoder/testdata_test.go>
  - <https://github.com/bytedance/sonic/releases>
  - <https://github.com/bytedance/sonic/commits/main>
  - <https://github.com/bytedance/sonic/issues>
  - <https://github.com/bytedance/sonic/issues/983>
  - <https://github.com/bytedance/sonic/issues/970>
  - <https://github.com/bytedance/sonic/issues/939>
  - <https://github.com/bytedance/sonic/issues/938>
  - <https://github.com/bytedance/sonic/issues/985>
  - <https://github.com/bytedance/sonic/issues/912>
  - <https://github.com/bytedance/sonic/issues/790>
  - <https://github.com/bytedance/sonic/issues/786>
  - <https://github.com/bytedance/sonic/issues/785>
  - <https://github.com/bytedance/sonic/issues/634>
  - <https://github.com/bytedance/sonic/issues/987>
  - <https://github.com/bytedance/sonic/issues/884>
  - <https://github.com/bytedance/sonic/issues/614>
  - <https://github.com/bytedance/sonic/issues/138>
  - <https://github.com/bytedance/sonic/issues/882>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/bytedance/sonic`) · [data/wave4/enrich/raw/github_com_bytedance_sonic.json](../../../data/wave4/enrich/raw/github_com_bytedance_sonic.json) (enrichment confidence 0.86)

</details>
