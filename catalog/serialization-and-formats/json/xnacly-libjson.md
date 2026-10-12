# libjson (xnacly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Minimal pure-Go JSON parser with dot-path queries; parses about 2x faster than encoding/json into any by mutating input.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | 1.94x-2.43x faster in Go benchmarks (ns/op) with 2.1x-3.1x fewer allocations; 1.69x-1.81x faster wall-clock time on 1MB-100MB files |
| **Workload** | Parsing JSON of varying complexity (naive, string-escape-heavy, deeply-nested 'hard' cases) via Go micro-benchmarks, plus parsing generated 1MB-100MB JSON files as a CLI end-to-end benchmark. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3700X 8-Core Processor, linux/amd64 (stated in the go test output; the hyperfine file benchmark does not restate hardware) |
| **Compiler and flags** | go test -bench=. -benchmem with default Go build flags; Go toolchain version not stated (go.mod declares only a minimum, go 1.26.4). File benchmarks: go build + hyperfine (--warmup 1 --runs 10). |
| **Adoption** | 5 stars |
| **Last commit** | 2026-06-06 |
| **Links** | [repository](https://github.com/xnacly/libjson) · [benchmark](https://github.com/xnacly/libjson/blob/master/README.md) |

## Verdict

On an AMD Ryzen 7 3700X (linux/amd64, Go version not stated), go test benchmarks parse a 50,000-element array of one of three self-written records. libjson.New was 1.94x, 2.29x and 2.43x faster than json.Unmarshal into any for the naive, escape-heavy and nested cases, with 2.1-3.1x fewer allocations, and the input copy libjson needs was excluded from timing. A hyperfine CLI run on generated 1MB-100MB files compared libjson's mmap FromFile with encoding/json's Decoder and measured 1.69x-1.81x faster wall-clock. Neither benchmark converts libjson's tree into Go values.

## Use it when

- Pulling a few fields by path out of large, trusted JSON documents (the README tests 1-100MB files) when you own the byte slice and can let the parser consume it.
- Loading JSON files on Linux/macOS through FromFile, which maps the file MAP_PRIVATE/copy-on-write. This skips the io.ReadAll copy: 134MB/op vs 217MB/op for NewReader in the README, though it was about 17% slower in that microbenchmark.
- Internal pipelines or generated data where input is known to be well-formed, so the lax validation below does not matter.
- You want a small stdlib-only parser (about 1,040 lines of non-test Go) that you can vendor and read end to end, with no JIT or assembly.

## Skip it when

- You decode into structs or rely on struct tags, custom Unmarshalers or streaming. libjson has none of these. Use go-json, Sonic, easyjson or segmentio/encoding instead.
- Untrusted input. The parser is recursive with no depth limit: PR #4's goal to replace recursion with an explicit stack was left unchecked. pow10 loops once per unit of exponent, so a number like 1e999999999 costs about a billion iterations. It accepts invalid JSON such as `-` (read as 0), `1-2` (read as 1), leading zeros and raw control characters inside strings. The README's RFC 8259 claim defers JSONTestSuite runs to 'the future'.
- Numeric fidelity matters. The custom float parser multiplies a uint64 mantissa by a pow10 built from repeated \*10 or /10, so results are not correctly rounded. Mantissas longer than about 19 digits overflow silently, and out-of-range exponents give ±Inf instead of an error. There is no UseNumber or int64 path. A Feb 2026 commit switched to strconv.ParseFloat as 'as fast but more correct', but the June 2026 redesign (v1.0.0) went back to the custom parser.
- You need the whole document as plain Go values. Get[any](&doc, ".") runs a second full-tree conversion into map[string]any/[]any. Neither published benchmark times that step, so the \~2x margin over json.Unmarshal into any shrinks.
- Maturity-sensitive production use. It has one author, 5 stars, a single v1.0.0 tag, and pkg.go.dev lists no known importers.

## How it is fast

A hand-written recursive-descent parser pulls tokens on demand from a lexer that returns start/end byte offsets rather than copies, and finds number characters with a 256-entry lookup table. Strings are zero-copy: escapes are decoded in place inside the input buffer (unescapeInPlace) and the bytes are aliased as a Go string through unsafe. Object keys are aliased the same way but never unescaped. Each value is a float64 plus a tagged pointer (a 3-bit kind in the low address bits) into chunked arenas of 256 nodes. Numbers use a custom non-allocating float parser instead of strconv.ParseFloat, and there is no reflection.

## Compared with alternatives

Rarely. valyala/fastjson has the same whole-document-plus-path-getter shape and is catalogued up to \~14.8x faster than encoding/json map decoding. gjson (3.2-4.4x) and buger/jsonparser (6.5x, zero alloc) skip full materialization, and go-json and Sonic are drop-ins for struct decoding. Pick libjson only if you want the smallest, most readable stdlib-only parser to vendor or study, and your input is trusted.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (stdlib only; stretchr/testify is used by tests) |
| **Minimum toolchain** | Go 1.26.4 (go directive in go.mod) |
| **Platforms** | Pure Go. FromFile uses syscall.Mmap under the `unix` build tag and falls back to io.ReadAll elsewhere. 64-bit targets only in practice: value.go keeps a 3-bit tag in node addresses, and on 32-bit targets some arena nodes are only 4-byte aligned (inferred from source, untested). |
| **Thread safety** | Not documented. Get only reads the parsed maps and slices, so concurrent reads look safe from the code, but parsing mutates the input buffer, so no other goroutine may read that buffer during or after New. |
| **Drop-in for the baseline** | no |

## Gotchas

- New consumes the input ('DO NOT REUSE'). Returned strings alias the buffer, or the mmap when you use FromFile, so strings you keep after doc.Close() point at unmapped memory. The Go benchmark copies the input before each New outside the timed region; a caller who needs the original bytes pays that copy.
- JSONVal stores node pointers as uintptr and converts them back with unsafe.Pointer(v.Ptr &^ tagMask). The Go compiler's checkptr instrumentation, on by default under -race, -msan and -asan, throws 'pointer arithmetic result points to invalid allocation' for such a conversion into a heap object. Expect code that reads libjson strings, arrays or objects to abort under `go test -race` (inferred from Go compiler/runtime source, not run).
- Get has sharp edges. An out-of-range array index panics because there is no bounds check. Keys that contain '.' cannot be addressed. A missing key or an index into an empty array returns null with no error. The path is re-parsed on every call. Every call rebuilds the requested subtree as fresh map[string]any/[]any. The libjson.Compile and libjson.Set APIs in the README do not exist in v1.0.0.
- Object keys are not unescaped: {"a\u00e9":1} is stored under the literal key `a\u00e9`. Escaped surrogate pairs (e.g. \ud83d\ude00) are deliberately not merged, and each half goes through utf8.EncodeRune, which writes U+FFFD for surrogates. Duplicate keys silently keep the last value.

## Known shortcomings

- Go toolchain version not stated (go.mod only sets a minimum), so not tier A. Author's own benchmark against encoding/json; 5 stars.
- Not like-for-like: libjson's timed step builds an internal tree while json.Unmarshal produces Go values (conversion never timed), its input copy is excluded, and the CLI benchmark mmaps for libjson only. The README advertises Compile and Set, which do not exist in v1.0.0. The custom float parser is not correctly rounded and loops once per exponent unit (1e999999999 costs about a billion iterations). Lax validation, no depth limit, Get panics on out-of-range indices; tagged-uintptr pointers likely abort under -race (inferred).

## Caveats and trade-offs

Very small project (5 stars, single author). The 'Naive'/'Escaped'/'Hard' inputs are self-defined strings repeated inside json_test.go, not a standard external corpus. No Go toolchain version is stated. libjson mutates its input buffer for zero-copy parsing, while encoding/json unmarshals into `any` without that trade-off. The hyperfine file benchmark does not restate the machine.

Zero-copy design mutates the input byte slice in place for string unescaping, so callers cannot reuse/read the original buffer after parsing; uses a custom JIT-cached query language instead of encoding/json's reflection-based struct tags, so migration requires API changes; very new, low-adoption project.

## Maintenance

Active single-author project (last commit 2026-06-06, tagged v1.0.0, no open issues). MIT, stdlib-only and about 1k lines, so it is easy to vendor, but the README is ahead of the code (Compile/Set, JSONTestSuite) and a 7.6MB libjson.test binary is committed to the repo root.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README Benchmarks section compares libjson directly with encoding/json (json.Unmarshal into `any`), using public code: BenchmarkLibJson_\* and BenchmarkEncodingJson_\* in json_test.go, and benchmarks/bench.sh + gen.py (hyperfine on cmd/lj.go). The go test output names the CPU (AMD Ryzen 7 3700X), but no Go toolchain version is stated (go.mod gives only a minimum, go 1.26.4), so by the orchestrator's Go rule (goccy/go-json, constmap retier) this is C, not A.
- **Verifier notes:** Every number in claimed_speedup (1.94x/2.29x/2.43x ns/op, 2.10x-3.14x fewer allocs, 1.69x-1.81x on 1MB-100MB files) matches the README. The recorded benchmark_url used /blob/main/, which returns 404; the default branch is master. Metadata checks out: MIT, 5 stars, not a fork, last commit 2026-06-06 (active).
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/xnacly/libjson>
  - <https://github.com/xnacly/libjson/blob/main/README.md>
  - <https://github.com/xnacly/libjson/blob/master/README.md>
  - <https://github.com/xnacly/libjson/blob/master/go.mod>
  - <https://github.com/xnacly/libjson/blob/master/json_test.go>
  - <https://github.com/xnacly/libjson/blob/master/benchmarks/bench.sh>
- **Sources the enricher read:**
  - <https://github.com/xnacly/libjson>
  - <https://github.com/xnacly/libjson/blob/master/README.md>
  - <https://github.com/xnacly/libjson/blob/master/go.mod>
  - <https://github.com/xnacly/libjson/blob/master/json.go>
  - <https://github.com/xnacly/libjson/blob/master/value.go>
  - <https://github.com/xnacly/libjson/blob/master/object.go>
  - <https://github.com/xnacly/libjson/blob/master/tokens.go>
  - <https://github.com/xnacly/libjson/blob/master/lexer.go>
  - <https://github.com/xnacly/libjson/blob/master/parser.go>
  - <https://github.com/xnacly/libjson/blob/master/float.go>
  - <https://github.com/xnacly/libjson/blob/master/hex.go>
  - <https://github.com/xnacly/libjson/blob/master/mmap_unix.go>
  - <https://github.com/xnacly/libjson/blob/master/mmap_unsupported.go>
  - <https://github.com/xnacly/libjson/blob/master/json_test.go>
  - <https://github.com/xnacly/libjson/blob/master/parser_test.go>
  - <https://github.com/xnacly/libjson/blob/master/object_test.go>
  - <https://github.com/xnacly/libjson/blob/master/lexer_test.go>
  - <https://github.com/xnacly/libjson/blob/master/example_test.go>
  - <https://github.com/xnacly/libjson/blob/master/cmd/lj.go>
  - <https://github.com/xnacly/libjson/blob/master/benchmarks/bench.sh>
  - <https://github.com/xnacly/libjson/blob/master/benchmarks/gen.py>
  - <https://github.com/xnacly/libjson/commits/master>
  - <https://github.com/xnacly/libjson/commit/212859e11e070329d173934f4b81b073456bfd60>
  - <https://github.com/xnacly/libjson/commit/79124c1badd70edb3790f05739004f95298ac2f8>
  - <https://github.com/xnacly/libjson/pull/4>
  - <https://github.com/xnacly/libjson/pull/3>
  - <https://github.com/xnacly/libjson/pull/2>
  - <https://github.com/xnacly/libjson/issues>
  - <https://github.com/xnacly/libjson/releases/tag/v1.0.0>
  - <https://proxy.golang.org/github.com/xnacly/libjson/@v/list>
  - <https://proxy.golang.org/github.com/xnacly/libjson/@latest>
  - <https://pkg.go.dev/github.com/xnacly/libjson?tab=importedby>
  - <https://github.com/xnacly/blog/blob/master/content/posts/2025/optimizing-libjson.md>
  - <https://github.com/xnacly/blog/blob/master/content/posts/2024/libjson.md>
  - <https://github.com/golang/go/blob/master/src/cmd/compile/internal/walk/convert.go>
  - <https://github.com/golang/go/blob/master/src/runtime/checkptr.go>
  - <https://github.com/golang/go/blob/master/src/cmd/compile/internal/base/flag.go>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/xnacly/libjson`) · [data/wave4/enrich/raw/github_com_xnacly_libjson.json](../../../data/wave4/enrich/raw/github_com_xnacly_libjson.json) (enrichment confidence 0.8)

</details>
