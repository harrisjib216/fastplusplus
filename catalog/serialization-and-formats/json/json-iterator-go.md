# jsoniter (json-iterator/go)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Pure-Go encoding/json replacement with cached per-type codecs; \~1.8x faster typed-struct Unmarshal than encoding/json. Archived.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | 233.6 MB/s vs encoding/json 128.8 MB/s at 8 threads (\~1.81x); 79.3 MB/s vs encoding/json 44.5 MB/s at 1 thread (\~1.78x) (derived from page data) |
| **Workload** | Unmarshal of 5 real SEC companyfacts JSON files (39.9 MB, 285,469 fact records) into typed Go structs, followed by the same fact filter, dedup and sum reduction. Timed over 20 passes after 2 warmups at 1/2/4/8 threads (file-level sharding). Every variant must return kept=245741. Run in the independent tegridy-benchie multi-language shootout |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i7-6820HQ CPU @ 2.70GHz (8 cores) |
| **Compiler and flags** | Go gc toolchain: golang/go.mod declares `go 1.27.1` (minimum toolchain; the exact version is not recorded). Built with plain `go build` (GOFLAGS=-mod=mod, default flags) per the Makefile. Uses jsoniter v1.1.12 with ConfigCompatibleWithStandardLibrary |
| **Adoption** | 13.9k stars |
| **Last commit** | 2022-09-15 |
| **Links** | [repository](https://github.com/json-iterator/go) · [benchmark](https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md) |

## Verdict

The evidence is one run of the third-party tegridy-benchie harness on an Intel i7-6820HQ (8 cores), built with plain `go build` on Go &gt;=1.27.1 (exact version not recorded). jsoniter v1.1.12 with ConfigCompatibleWithStandardLibrary unmarshaled 39.9 MB of SEC companyfacts JSON into typed structs, plus a shared filter/dedup/sum step, at 79.3 MB/s vs encoding/json's 44.5 MB/s on 1 thread and 233.6 vs 128.8 MB/s on 8 threads. That is about 1.7-1.8x at every thread count, and the shared reduction work in the timing understates the pure-decode gap.

## Use it when

- An existing Go service on encoding/json that needs faster typed-struct Unmarshal with a one-line swap and no code generation. The measured gain was about 1.7-1.8x at 1-8 goroutines on 40 MB of nested real-world JSON.
- The codebase already depends on jsoniter (directly or transitively), so upgrading its config costs nothing and moving to another library is not worth it yet.
- You want a low-level pull parser (Iterator with ReadObjectCB/ReadMapCB, Skip) or path lookups (`Get(data, "a", 0, "b")`) to pull fields out of large or dynamic documents without defining full structs.
- You need per-type or per-field custom codecs, or naming-strategy/fuzzy-type decoding, through its extension API instead of MarshalJSON methods on every type.
- Pure-Go portability matters: there is no assembly in the repo. Sonic, by contrast, JITs only on AMD64/ARM64 and falls back to encoding/json elsewhere.

## Skip it when

- New projects. The repo is archived and read-only, the last code commit was 2022-09-15, and the last release was v1.1.12 (2021). On the same harness, goccy/go-json and Sonic are faster at every thread count.
- Code that needs exact encoding/json parity. Decoder.Token/InputOffset and Compact/Indent/HTMLEscape are missing (issue #229). Recursive embedded struct types overflow the stack on Marshal, and overlapping tag names resolve differently (issue #657). On decode, invalid UTF-8 is not replaced with U+FFFD as stdlib does, because the string fast path copies bytes unchecked.
- Untrusted input with small structs. Structs with 10 or fewer fields dispatch on a 64-bit FNV-style hash of the incoming key alone, so an unknown key that collides with a real field's hash gets decoded into that field. The goccy/go-json README also flags this collision risk.
- Marshal-heavy typed workloads. In Sonic's README benchmark (Go 1.17.1, i9-9880H, 13 KB payload), jsoniter's struct-binding encode took 20,056 ns/op vs stdlib's 16,448 (6,170 vs 3,739 in parallel), and its binding decode made 385 allocs/op vs stdlib's 208.
- Memory-constrained hosts. In the tegridy-benchie run, jsoniter's peak RSS was higher than encoding/json's at every thread count (186 vs 158 MB at 1 thread, 346 vs 328 MB at 8).

## How it is fast

The first time it sees a type, it builds a decoder/encoder tree with modern-go/reflect2 and caches it per config (concurrent map keyed by rtype). After that it reads and writes through unsafe.Pointer field offsets rather than reflect.Value; reflect.go says a simple struct binding is 'reflect.Value free and allocation free'. It decodes in a single pass over the buffer, skipping encoding/json's separate checkValid well-formedness scan. It uses lookup-table digit parsing with an exact float fast path (mantissa below 2^53 divided by a power of ten up to 10^6, with a strconv fallback), zero-copy string slicing when a string has no escapes, and FNV-1a-style key-hash dispatch for structs with 10 or fewer fields instead of map lookups. Iterators and Streams are reused through sync.Pool.

## Compared with alternatives

For raw speed, goccy/go-json (256.7 vs 233.6 MB/s at 8 threads, 90.8 vs 79.3 at 1) and Sonic beat it in the same harness at every thread count, and easyjson's code generation is the pick if you can generate code. Choose jsoniter only when it is already in your dependency tree or you specifically want its pull Iterator/Stream API, Get/Any path lookups, or per-type/field extension hooks.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/modern-go/reflect2 v1.0.2, github.com/modern-go/concurrent (test-only: testify, go-spew, gofuzz) |
| **Minimum toolchain** | go.mod declares go 1.12. Go 1.18+ needs reflect2 v1.0.2, which v1.1.12 requires ('fix go1.18'). The benchmark built it with Go &gt;=1.27.1. |
| **Platforms** | Any Go gc target (pure Go, no assembly files). It depends on unsafe and on go:linkname into runtime/reflect via reflect2. gccgo/TinyGo support is not documented. |
| **Thread safety** | A frozen API value (Config.Froze(), ConfigCompatibleWithStandardLibrary) is meant to be shared: codec caches are concurrent maps, and Iterator/Stream come from a pool whose comment says it is thread safe. The docs do not say whether individual Iterator/Stream/Decoder/Encoder instances are safe to share. The global Register\* extension functions write plain package-level maps. |
| **Drop-in for the baseline** | partial — Marshal/Unmarshal/NewEncoder/NewDecoder/Valid mirror encoding/json through ConfigCompatibleWithStandardLibrary. However, Decoder.Token/InputOffset and Compact/Indent/HTMLEscape are missing, MarshalIndent rejects prefixes and tab indents, and error and edge-case behavior differs (issues #229, #559, #657). |

## Gotchas

- The package-level jsoniter.Marshal/Unmarshal use ConfigDefault, which does not sort map keys the way encoding/json does. Use ConfigCompatibleWithStandardLibrary to get stdlib-compatible output.
- MarshalIndent panics if prefix != "" or if indent contains anything but spaces, so `MarshalIndent(v, "", "\t")` panics. Encoder.SetIndent silently ignores the prefix and indents with len(indent) spaces.
- There is no pre-validation pass (stdlib runs checkValid first 'to avoid filling out half a data structure'), so malformed input can leave the target partly filled. Issue #559 also reports that it aborts early on a type-mismatched field where stdlib keeps decoding the other fields.
- The pinned reflect2 v1.0.2 embeds reflect.Type in a way that disables the linker's dead-code elimination, which makes binaries larger. The fix (reflect2 PR #30, 2025) is merged but untagged. Call global Register\* extension functions at init, before any concurrent use.

## Caveats and trade-offs

The repository was archived by its owner. The last code commit is 2022-09-15, and 2024-05-27 is only the archive/push date. The figure comes from a third-party shootout, not the project's own old benchmarks. That shootout is a new, 0-star repo (created 2026-09-23) with one run on one laptop CPU. The timed passes include the shared reduction work, so the ratio understates the pure-decode difference. In the same table, jsoniter is slower than sonic and goccy/go-json at every thread count. At 1 thread it is 0.87x the goccy baseline. [retier] Evidence comes only from a new 0-star third-party harness (tegridy-benchie) with no stated Go version.

Advertised as a '100% compatible drop-in replacement' for encoding/json, but goccy/go-json's README documents real compatibility gaps in that claim

## Maintenance

Archived by its owner and read-only (last code commit 2022-09-15, last release v1.1.12 in 2021). It is MIT-licensed and still builds and runs on current Go according to the benchmark, so it is fine to keep where it is already deployed, but go-json or Sonic are better choices for new adoption.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now C.
- **Tier reason:** In the 'Native — Go' table of RESULTS.md, jsoniter and encoding/json both run the same typed-struct decode plus reduce harness. The code is public: golang/bench.go, golang/decoders.go (jsoniter.ConfigCompatibleWithStandardLibrary vs encoding/json Unmarshal) and golang/parser.go, with the Makefile using plain `go build`. RESULTS.md and results.json state the i7-6820HQ CPU. golang/go.mod pins go 1.27.1 as the minimum toolchain, so Tier A. The exact Go patch release is not recorded.
- **Retiered** A to C: Orchestrator consistency retier: the only evidence is mihailnica10/tegridy-benchie, which states no Go toolchain version (go.mod gives only a minimum, go 1.27.1) and is a 2-day-old, 0-star, single-commit harness. Same rule as jiter (wave 4) and constmap (perfect-hash run): no toolchain version means tier C.
- **Verifier notes:** The quoted numbers are all in jsoniter's own rows: 233.6 vs 128.8 MB/s at 8t and 79.3 vs 44.5 MB/s at 1t. At 2t it is 128.0 vs 73.4 and at 4t 171.4 vs 100.7, so the gain is a consistent \~1.7-1.8x. The metadata is correct apart from last_commit (MIT, 13,867 stars, archived). The Go toolchain is known only as &gt;=1.27.1 from go.mod. If exact compiler versions are strictly required for Tier A, treat this as C.
- **Fields the verifier corrected:** `last_commit`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md>
  - <https://github.com/mihailnica10/tegridy-benchie>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/README.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/README.benchmark.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/Makefile>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/LICENSE>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/results.json>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/run-bench.ts>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/go.mod>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/decoders.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/bench.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/parser.go>
  - <https://github.com/json-iterator/go>
- **Sources the enricher read:**
  - <https://github.com/json-iterator/go>
  - <https://github.com/json-iterator/go/blob/master/README.md>
  - <https://github.com/json-iterator/go/blob/master/config.go>
  - <https://github.com/json-iterator/go/blob/master/adapter.go>
  - <https://github.com/json-iterator/go/blob/master/reflect.go>
  - <https://github.com/json-iterator/go/blob/master/reflect_struct_decoder.go>
  - <https://github.com/json-iterator/go/blob/master/reflect_extension.go>
  - <https://github.com/json-iterator/go/blob/master/reflect_native.go>
  - <https://github.com/json-iterator/go/blob/master/iter.go>
  - <https://github.com/json-iterator/go/blob/master/iter_object.go>
  - <https://github.com/json-iterator/go/blob/master/iter_float.go>
  - <https://github.com/json-iterator/go/blob/master/iter_int.go>
  - <https://github.com/json-iterator/go/blob/master/iter_str.go>
  - <https://github.com/json-iterator/go/blob/master/iter_array.go>
  - <https://github.com/json-iterator/go/blob/master/iter_skip.go>
  - <https://github.com/json-iterator/go/blob/master/iter_skip_strict.go>
  - <https://github.com/json-iterator/go/blob/master/iter_skip_sloppy.go>
  - <https://github.com/json-iterator/go/blob/master/stream.go>
  - <https://github.com/json-iterator/go/blob/master/stream_str.go>
  - <https://github.com/json-iterator/go/blob/master/stream_float.go>
  - <https://github.com/json-iterator/go/blob/master/any.go>
  - <https://github.com/json-iterator/go/blob/master/pool.go>
  - <https://github.com/json-iterator/go/blob/master/go.mod>
  - <https://github.com/json-iterator/go/blob/master/go.sum>
  - <https://github.com/json-iterator/go/commits/master>
  - <https://github.com/json-iterator/go/releases>
  - <https://github.com/json-iterator/go/issues/229>
  - <https://github.com/json-iterator/go/issues/559>
  - <https://github.com/json-iterator/go/issues/657>
  - <http://jsoniter.com/migrate-from-go-std.html>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/decoders.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/go.mod>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/parser.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/bench.go>
  - <https://github.com/goccy/go-json/blob/master/README.md>
  - <https://github.com/bytedance/sonic/blob/main/README.md>
  - <https://github.com/modern-go/reflect2>
  - <https://github.com/modern-go/reflect2/pull/30>
  - <https://github.com/modern-go/reflect2/releases>
  - <https://github.com/golang/go/blob/master/src/reflect/value.go>
  - <https://github.com/golang/go/blob/master/src/encoding/json/decode.go>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/json-iterator/go`) · [data/wave4/enrich/raw/github_com_json_iterator_go.json](../../../data/wave4/enrich/raw/github_com_json_iterator_go.json) (enrichment confidence 0.85)

</details>
