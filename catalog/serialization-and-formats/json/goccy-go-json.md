# go-json

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Import-swap replacement for Go's encoding/json; unmarshalled typed structs \~2x faster than encoding/json in one third-party benchmark.

| | |
|---|---|
| **Beats** | encoding/json |
| **Claimed result** | 256.7 MB/s vs encoding/json 128.8 MB/s at 8 threads (\~1.99x); 90.8 MB/s vs encoding/json 44.5 MB/s at 1 thread (\~2.04x) (derived from page data) |
| **Workload** | Unmarshal of 5 real SEC company-facts JSON files (39.9 MB total, 285,469 fact records) into the same typed Go structs, followed by the same fact-row reduction; goccy/go-json v0.10.5 vs encoding/json at 1/2/4/8 threads (GOMAXPROCS=threads, one file per work item), 20 timed passes after 2 warmups, in the third-party tegridy-benchie shootout |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i7-6820HQ CPU @ 2.70GHz (8 cores) |
| **Compiler and flags** | Go 1.27+ (go.mod: go 1.27.1); plain `go build` with GOFLAGS=-mod=mod GOPROXY=off and no extra flags (Makefile) |
| **Adoption** | 3.7k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/goccy/go-json) · [benchmark](https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md) |

## Verdict

In the third-party tegridy-benchie harness (i7-6820HQ, 4 cores/8 threads; Go 1.27.1 or later, exact patch not recorded; plain go build), go-json v0.10.5 decoded 5 SEC companyfacts files (39.9 MB) into typed structs with nested maps, plus the same fact reduction, at 90.8 MB/s vs encoding/json 44.5 MB/s at 1 thread (\~2.0x) and 256.7 vs 128.8 MB/s at 8 threads (\~2.0x), using more peak memory. The baseline is Go 1.27's encoding/json, which go-json's option docs describe as built on encoding/json/v2, and the timings include the shared reduction step, which dilutes the parse-only ratio.

## Use it when

- Services that Unmarshal into concrete Go structs, including nested map[string]T and slices of structs, and want roughly 2x over encoding/json by changing one import. The measured case was multi-MB documents (5 SEC files, 39.9 MB total).
- Decode throughput at low to moderate parallelism: in the same harness it matched or beat sonic at 1-4 threads (90.8 vs 86.1 MB/s at 1 thread, 200.1 vs 180.2 MB/s at 4 threads).
- Codebases that need encoding/json semantics but won't add code generation (easyjson) or learn a different API.
- Portable builds: v0.10.x has no assembly, so it compiles on any GOARCH that Go supports. Master adds SIMD paths with a word-at-a-time fallback, and its CI runs on Linux, macOS and Windows.
- Code that wants context.Context passed into custom (Un)MarshalJSON methods, or JSON field filtering, which encoding/json doesn't provide.

## Skip it when

- Untrusted or malformed input on the released v0.10.6: open issues report index-out-of-range panics (#604, where decoder state carries over between calls, and #609) and a fatal checkptr crash (#575) where encoding/json returns an error. The fixes exist only on untagged master.
- Memory-tight processes: peak RSS was 227 vs 158 MB at 1 thread and 409 vs 328 MB at 8 threads against encoding/json. v0.10.x copies the whole input on each call, and decoded strings keep that copy alive.
- Structs with more than 16 fields that rely on case-insensitive key matching in v0.10.x: fields can silently stay empty (#427, open).
- Token-by-token streaming with Decoder.Token(): an open issue (#396) reports up to \~50x slower than encoding/json on some files and \~90 MB of memory to walk a 50 MB file.
- Teams that can't absorb toolchain breakage or unreleased code. v0.10.x hooks into runtime/reflect internals with dozens of go:linkname directives, and one of them broke against Go 1.23 dev (#506). The linkname-free master was largely rewritten between 20 and 25 Sept 2026 (PR bodies say 'Generated with Claude Code') and has no tag.

## How it is fast

Instead of walking values with reflect on every call, it compiles a decoder per type, and for encoding a linear opcode program run by a switch-dispatch VM that fuses opcodes and handles recursion as a jump, both cached by the type's runtime pointer ("typeptr") and looked up without a lock. The decoder copies the input into a NUL-terminated buffer so scan loops need no end-of-buffer check, and reads bytes through unsafe pointers to skip bounds checks. In v0.10.x, the version benchmarked, struct keys are matched with per-character bitmaps (up to 16 fields, keys under 64 bytes) and decoded strings point into that buffer instead of being copied. Unreleased master replaces this with AVX2/NEON 64-byte block scanning to skip values (prefix-XOR quote masks, popcount bracket counting), a hash table of case-folded keys compared 8 bytes at a time, and one-pass number parsing (Clinger's fast path plus a 128-bit power-of-ten table).

## Compared with alternatives

Pick it over jsoniter when you want the faster and more compatible drop-in: in the same harness it beat jsoniter at every thread count (90.8 vs 79.3 MB/s at 1 thread, 256.7 vs 233.6 at 8 threads), and its README calls jsoniter only partially encoding/json-compatible. Pick it over Sonic at 1-4 threads or where you want no JIT (sonic edged it at 8 threads, 260.0 vs 256.7 MB/s, with 320 vs 409 MB peak RSS), and over easyjson when you can't add a code-generation step.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none |
| **Minimum toolchain** | go.mod says Go 1.19 for v0.10.5/v0.10.6 and Go 1.21 on master; master CI tests only Go 1.25, 1.26 and 1.27 |
| **Platforms** | any GOOS/GOARCH for v0.10.x (pure Go plus unsafe). Master adds AVX2 scanners on amd64 (detected at runtime via CPUID/XGETBV) and NEON on arm64, with a word-at-a-time fallback elsewhere |
| **Thread safety** | Package-level Marshal/Unmarshal are meant to be called concurrently: per-call contexts come from a pool and type caches are shared without locks (README). v0.10.5 has an open data-race report in the type compiler's non-race build path (#566). The fix (#567, July 2026) is on master only and in no release. |
| **Drop-in for the baseline** | partial: same function names, types and struct-tag rules, so switching is an import swap. Open v0.10.x issues document divergences, though: interface decoding (#443), MarshalJSON handling (#418), case-insensitive keys on structs with more than 16 fields (#427), and panics or fatal errors instead of returned errors on some malformed input (#575, #604). |

## Gotchas

- The benchmark measured v0.10.5, and `go get` today resolves v0.10.6, which adds one bug fix. The large decoder/encoder rewrite (SIMD scanning, key table, UnmarshalOf, linkname removal) is untagged master. Its speed claims, such as beating sonic on struct decoding, come from the author's own CI, not a release.
- In v0.10.x, decoded strings point into an internal copy of the whole input, so keeping any decoded string keeps the entire document copy alive (described in PR #658). Master copies strings into shared buffers of up to 16 KB by default. DecodeNoCopyString makes strings alias the caller's input, which must then not be modified.
- MarshalOf/UnmarshalOf (master only) work on a pooled copy and copy the result back. That makes large values slower, and UnmarshalJSON/UnmarshalText methods must not keep the receiver's address. MarshalNoEscape/UnmarshalNoEscape are deprecated as unsafe when a goroutine stack moves, and now behave like the plain calls.
- Heavy unsafe use even after the linkname removal: master reads string-keyed maps by reinterpreting map[K]V as map[string][n]uint64. That relies on the runtime's map layout, with separate go1.24 and pre-go1.24 build variants, so a future change to Go's maps could break it.

## Caveats and trade-offs

go-json's own README shows results only as chart images (from `go test -bench` in benchmarks/) with no CPU or Go version, so on its own it would be Tier C/D. The Tier-A number comes from tegridy-benchie instead, a third-party harness that is not well known: 0 stars, one commit, created 2026-09-23. It tested go-json v0.10.5 (Jan 2025), not v0.10.6 or current master, which rewrote parts of the decoder on 2026-09-24/25. go-json used more memory than encoding/json (peak RSS 409 vs 328 MB at 8t, 227 vs 158 MB at 1t). sonic was faster at 8 threads (260.0 MB/s). The corpus has only 5 files and work is split per file, so the 8-thread runs are limited to 5-way parallelism. The i7-6820HQ is 4 cores / 8 threads (the page says '8 cores'). [retier] Evidence comes only from a new 0-star third-party harness (tegridy-benchie) with no stated Go version.

Advertised and used as a full drop-in replacement for encoding/json (single import swap)

## Maintenance

An MIT, dependency-free Go module usable via `go get`, active again but unreleased: only two commits landed between v0.10.5 (Jan 2025) and 20 Sept 2026, v0.10.6 (Mar 2026) holds a single fix, and dozens of large performance and compatibility PRs merged to master between 20 and 25 Sept 2026 without a tag.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now C.
- **Tier reason:** RESULTS.md (Native — Go table) shows goccy/go-json at 256.7 MB/s (8t) and 90.8 MB/s (1t), against encoding/json at 128.8 and 44.5 MB/s. The same harness runs both, unmarshalling into the same typed struct (golang/decoders.go, golang/bench.go, golang/parser.go). The Makefile gives a plain `go build` and go.mod requires Go 1.27.1, while RESULTS.md names the CPU (i7-6820HQ). Code, compiler, flags and CPU are all stated, so A.
- **Retiered** A to C: Orchestrator consistency retier: the only evidence is mihailnica10/tegridy-benchie, which states no Go toolchain version (go.mod gives only a minimum, go 1.27.1) and is a 2-day-old, 0-star, single-commit harness. Same rule as jiter (wave 4) and constmap (perfect-hash run): no toolchain version means tier C.
- **Verifier notes:** Numbers verified on RESULTS.md and results.json (go_goccy 256.74 / 90.83 MB/s; encoding/json 128.8 / 44.5). The ratios are correctly marked as derived. A holds because go.mod pins Go &gt;=1.27.1, although the exact patch release run is not recorded. Metadata checks out via gh: MIT, 3709 stars, not a fork, not archived, last commit 2026-09-25 (active).
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/goccy/go-json>
  - <https://github.com/goccy/go-json/blob/master/README.md>
  - <https://github.com/goccy/go-json/releases>
  - <https://github.com/goccy/go-json/commits/master>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md>
  - <https://github.com/mihailnica10/tegridy-benchie>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/README.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/README.benchmark.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/Makefile>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/LICENSE>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/results.json>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/variants.ts>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/run-bench.ts>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/decoders.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/bench.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/parser.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/go.mod>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/go.sum>
- **Sources the enricher read:**
  - <https://github.com/goccy/go-json>
  - <https://github.com/goccy/go-json/blob/master/README.md>
  - <https://github.com/goccy/go-json/blob/master/go.mod>
  - <https://github.com/goccy/go-json/blob/v0.10.5/go.mod>
  - <https://github.com/goccy/go-json/releases>
  - <https://github.com/goccy/go-json/commits/master>
  - <https://github.com/goccy/go-json/blob/master/CHANGELOG.md>
  - <https://github.com/goccy/go-json/blob/master/.github/workflows/go.yml>
  - <https://github.com/goccy/go-json/blob/master/json.go>
  - <https://github.com/goccy/go-json/blob/master/decode_of.go>
  - <https://github.com/goccy/go-json/blob/master/option.go>
  - <https://github.com/goccy/go-json/blob/master/internal/decoder/struct_keys.go>
  - <https://github.com/goccy/go-json/blob/master/internal/decoder/scan.go>
  - <https://github.com/goccy/go-json/blob/master/internal/decoder/scan_other.go>
  - <https://github.com/goccy/go-json/blob/master/internal/runtime/type_cache.go>
  - <https://github.com/goccy/go-json/blob/master/internal/runtime/cpu_amd64.go>
  - <https://github.com/goccy/go-json/blob/master/internal/encoder/map_collect.go>
  - <https://github.com/goccy/go-json/blob/master/internal/encoder/map_collect_swiss.go>
  - <https://github.com/goccy/go-json/blob/master/internal/encoder/map_collect_buckets.go>
  - <https://github.com/goccy/go-json/tree/master>
  - <https://github.com/goccy/go-json/tree/v0.10.5>
  - <https://github.com/goccy/go-json/tree/v0.10.6>
  - <https://github.com/goccy/go-json/blob/v0.10.5/decode.go>
  - <https://github.com/goccy/go-json/blob/v0.10.5/internal/decoder/string.go>
  - <https://github.com/goccy/go-json/blob/v0.10.5/internal/decoder/struct.go>
  - <https://github.com/goccy/go-json/blob/v0.10.5/internal/runtime/rtype.go>
  - <https://github.com/goccy/go-json/blob/v0.10.5/internal/runtime/type.go>
  - <https://github.com/goccy/go-json/blob/v0.10.5/internal/decoder/map.go>
  - <https://github.com/goccy/go-json/blob/v0.10.5/internal/encoder/encoder.go>
  - <https://github.com/goccy/go-json/pull/659>
  - <https://github.com/goccy/go-json/pull/658>
  - <https://github.com/goccy/go-json/pull/656>
  - <https://github.com/goccy/go-json/issues/506>
  - <https://github.com/goccy/go-json/issues/566>
  - <https://github.com/goccy/go-json/issues/604>
  - <https://github.com/goccy/go-json/issues/575>
  - <https://github.com/goccy/go-json/issues/427>
  - <https://github.com/goccy/go-json/issues/421>
  - <https://github.com/goccy/go-json/issues/396>
  - <https://github.com/goccy/go-json/issues?q=panic>
  - <https://github.com/goccy/go-json/issues?q=label%3Abug>
  - <https://github.com/goccy/go-json/issues?q=label%3Aperformance>
  - <https://github.com/goccy/go-json/issues?q=compatible>
  - <https://github.com/mihailnica10/tegridy-benchie>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/go.mod>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/decoders.go>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/golang/parser.go>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/goccy/go-json`) · [data/wave4/enrich/raw/github_com_goccy_go_json.json](../../../data/wave4/enrich/raw/github_com_goccy_go_json.json) (enrichment confidence 0.8)

</details>
