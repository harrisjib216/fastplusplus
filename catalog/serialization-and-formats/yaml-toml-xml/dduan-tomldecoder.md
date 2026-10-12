# TOMLDecoder

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Swift` · `MIT` · 🟢 active

> Swift TOML 1.1 parser and Codable decoder. In its author's harness, its lazy parse ran about 5x faster than toml++.

| | |
|---|---|
| **Beats** | toml++ |
| **Claimed result** | 1.232ms avg vs toml++ 6.107ms avg (\~4.96x faster); also 1.81x faster than tomlc99 (2.226ms) |
| **Workload** | Parsing, not Codable decoding, the 443,461-byte twitter.toml fixture from Swift: TOMLDecoder `TOMLTable(source:)` vs tomlc99 `toml_parse` and toml++ `toml::parse` (exceptions enabled, through a minimal C wrapper with a static toml::table). 100 timed iterations after warmup, timed with CFAbsoluteTimeGetCurrent. |
| **Metric** | latency |
| **Adoption** | 108 stars |
| **Last commit** | 2026-07-11 |
| **Links** | [repository](https://github.com/dduan/TOMLDecoder) · [benchmark](https://duan.ca/2026/01/01/TOMLDecoder-Is-Faster-Than-C/) |

## Verdict

In the author's own Swift program (harness unpublished, snippets only; 2026-01-01 post released with 0.4.3), averaging 100 warm iterations on the 443,461-byte twitter.toml with CFAbsoluteTimeGetCurrent, TOMLDecoder's lazy `TOMLTable(source:)` took 1.232 ms vs 2.226 ms for tomlc99 `toml_parse` (1.81x) and 6.107 ms for toml++ `toml::parse` with exceptions via a C wrapper (4.96x). This compares a structure-only parse with toml++'s fully validated DOM, the wrapper's move-assign into a static table puts the previous DOM's teardown inside the timed window (our reading of the snippet), and no CPU, OS, compiler versions, flags or baseline versions are given.

## Use it when

- Swift code on Apple platforms, Linux or Windows that loads TOML config into Codable types and wants a pure-Swift parser with no C/C++ dependency.
- Large TOML documents (hundreds of KB, like the 443 KB twitter.toml fixture) where only some fields are read: untouched leaf values are tokenized but never validated or materialized.
- Swift projects now calling tomlc99 or toml++ through C/C++ interop: the author measured 1.81x and 4.96x faster structural parses from Swift.
- Code that wants strictly typed TOML access (Int64, Double, OffsetDateTime, LocalDate/LocalTime) and a choice of proleptic-Gregorian date conversion.

## Skip it when

- C or C++ programs: it is Swift-only, so toml++ or teptris stay the options there.
- You need to write, edit or re-serialize TOML: it has no encoder, and `TOMLTable`'s Codable conformance throws `notReallyCodable` outside TOMLDecoder.
- You need the whole document validated up front: `TOMLTable(source:)` accepts, for example, `x = foo` or a malformed date, and errors only when that value is read. Full checking needs `Dictionary(table)`, which the docs call expensive.
- Untrusted or unusual input: the 0.4 rewrite is young. 0.4.5 (2026-07-11) fixed fuzzer-found traps such as `-=0` and wrongly rejected valid TOML 1.1 (`x = [[true]]`, `x = [[inf]]`). Tables with very many keys fall back to linear scans once the 64-bit Bloom mask saturates (inferred from source, not benchmarked).
- Embedded Swift or Foundation-free builds: the module does `public import Foundation`. The trait to make it optional (issue #232, PR #316) is still open.

## How it is fast

Parsing is two-phase: `TOMLTable(source:)` does a lexing-level pass that checks only structure (syntax, table redefinition, duplicate keys) and records each leaf value as a token byte range in five flat index-linked arrays instead of nested dictionaries, deferring unescaping and number/date validation to the typed accessor that asks for the value. The hot loop reads an UnsafeBufferPointer over the String's contiguous UTF-8 (avoiding String-index bounds checks) and scans basic strings 8 bytes at a time with a SWAR has-byte test for quote, backslash and newline. Key lookups are linear scans filtered by a cheap packed/sampled UInt64 key hash and a per-table 64-bit Bloom mask, with array capacities pre-reserved from input size. Per the author, most of the 0.4.3 micro-optimizations were found by an AI coding agent iterating on package-benchmark instruction counts.

## Compared with alternatives

It is the only Swift TOML entry in the catalog, so pick it for Swift code. For C/C++ pick teptris (C99; its own benchmarks show 5.2-8.5x toml++ throughput with a full DOM and an emitter), for Rust toml-spanner, and for Go go-toml v2.

## Integration

| | |
|---|---|
| **Form** | module (SwiftPM package; also on the Bazel Central Registry as swift-tomldecoder) |
| **Dependencies** | Foundation only for the library target. The benchmark, swift-docc-plugin and SwiftFormat packages are pulled in only when env vars enable them. |
| **Minimum toolchain** | Swift 6.0 (swift-tools-version 6.0; CI tests 6.0 and 6.3.3). Apple minimums are iOS 13, macOS 10.15, tvOS 13, watchOS 6 and visionOS 1. |
| **Platforms** | macOS, iOS, tvOS, watchOS and visionOS (CI simulators), Ubuntu 24.04 and Windows 2025 in CI. WebAssembly is build-only (tests not run, issue #225). There is no architecture-specific code; the SWAR scan uses plain UInt64. |
| **Thread safety** | Not documented in prose. TOMLTable, TOMLArray, TOMLDecoder and the date types are declared Sendable immutable structs, and the shared TOMLDocument is @unchecked Sendable with only `let` fields, so parsed results can be read concurrently. The parser is a per-call \~Copyable value. |
| **Drop-in for the baseline** | no |

## Gotchas

- Errors come in two phases. A document can pass `TOMLTable(source:)` or start decoding and still throw later, from the accessor for a bad value. Only phase-1 errors are wrapped as `DecodingError.dataCorrupted` by `decode`.
- Key strategies slow parsing: with `.convertFromSnakeCase` or `.custom`, every key is built as a String, transformed and rehashed during phase 1. The snake-case converter is marked `// TODO: make this fast`.
- Possible trap with non-contiguous Strings, such as some bridged NSStrings. Parsing falls back to `withUTF8`, but TOMLDocument keeps the caller's original String, and the token accessors force-unwrap `utf8.withContiguousStorageIfAvailable`. This comes from reading TOMLDocument.swift and Token.swift and is not reported in issues. Passing a native String or Data avoids it.
- Lookups by key (`string(forKey:)`, Codable containers) are linear scans of the table's entries, which the author chose deliberately. Cost per lookup grows with table width.

## Known shortcomings

- Not like-for-like: since 0.4 the timed TOMLTable(source:) parse is lazy (it records token offsets and does not check or convert leaf values), while toml++ builds a fully checked tree. The harness that compares against toml++ and tomlc99 is not public, and no CPU, compiler or flags are given.
- Invalid TOML can pass TOMLTable(source:): bad leaf values only error when read; full checking needs the expensive Dictionary(table) path. The toml++ timing includes freeing the previous tree. The 0.4 rewrite is young (0.4.5 fixed fuzz-found crashes). Read-only (no encoder) and requires Foundation. Enrichment confidence 0.4.

## Caveats and trade-offs

This is a first-party blog post from 2026-01-01 about 0.4.x. The comparison harness is not published; only snippets are in the post, and the repo benchmarks cover TOMLDecoder alone. There is no CPU model, Swift/Xcode or C++ compiler version, or optimization flags for any library, and no toml++ or tomlc99 version. The comparison is not like-for-like: per the author's 0.4.1 post, `TOMLTable(source:)` parses lazily. It only records token byte offsets and does not validate or materialize leaf values, while toml++ builds a fully validated DOM. The author openly invites feedback on whether the comparison is fair to the C/C++ side.

Swift-only; toml++ was exercised through Swift/C++ bridging, which the author acknowledges may add overhead not present in a native C++ benchmark; most recent optimization commits were authored by an AI coding agent per the author's own account

## Maintenance

Active, single-maintainer, MIT (108 stars): 0.4.5 (2026-07-11) fixed fuzzer-found crashes and 0.4.4 added TOML 1.1.0 plus another 24% cut in twitter.toml parse instructions, but the API is pre-1.0 and 0.4.1 broke source compatibility with 0.3.x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** A first-party blog post prints 'TOMLDecoder is 4.96x faster than cTOMLPlusPlus' (1.232 ms vs 6.107 ms average) and 1.81x vs tomlc99. It gives no CPU model, no Swift or C++ compiler version, and no optimization flags. The full comparison harness is not public: only snippets appear in the post, and the repo's Benchmarks/TOMLDecoderBenchmarks/Benchmarks.swift benchmarks TOMLDecoder alone with ordo-one/package-benchmark.
- **Verifier notes:** The numbers match the page exactly, and toml++ is a list baseline (yaml-toml-xml). The main fix is the workload: the timed call is `TOMLTable(source:)`, a lazy parse, not decoding into Codable types. Metadata verified: MIT, 108 stars, last commit 2026-07-11 (v0.4.5), not archived, not a fork.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://duan.ca/2026/01/01/TOMLDecoder-Is-Faster-Than-C/>
  - <https://duan.ca/2025/12/10/TOMLDecoder-0.4.1/>
  - <https://github.com/dduan/TOMLDecoder>
  - <https://github.com/dduan/TOMLDecoder/commits>
  - <https://github.com/dduan/TOMLDecoder/blob/main/README.md>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Package.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Benchmarks/TOMLDecoderBenchmarks/Benchmarks.swift>
- **Sources the enricher read:**
  - <https://github.com/dduan/TOMLDecoder>
  - <https://github.com/dduan/TOMLDecoder/blob/main/README.md>
  - <https://duan.ca/2026/01/01/TOMLDecoder-Is-Faster-Than-C/>
  - <https://duan.ca/2025/12/10/TOMLDecoder-0.4.1/>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Package.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/.swift-version>
  - <https://github.com/dduan/TOMLDecoder/blob/main/MODULE.bazel>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/TOMLDecoder.docc/CHANGELOG.md>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/TOMLDecoder.docc/GettingStarted.md>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/TOMLDecoder.docc/DeserializingTOML.md>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/TOMLDecoder.docc/DecodingTOML.md>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/TOMLDecoder.docc/TOMLDecoder.md>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/Parsing/Parser.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/Parsing/Parser+Finish.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/Parsing/TOMLDocument.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/Parsing/Token.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/TOMLTable.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/TOMLArray.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/TOMLDecoder.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/_TOMLDecoder.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/TOMLKeyedDecodingContainer.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/TOMLError.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/TOMLDecoder/DateTime.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Sources/compliance/main.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Benchmarks/TOMLDecoderBenchmarks/Benchmarks.swift>
  - <https://github.com/dduan/TOMLDecoder/blob/main/Scripts/benchmark.sh>
  - <https://github.com/dduan/TOMLDecoder/blob/main/.github/workflows/swift.yml>
  - <https://github.com/dduan/TOMLDecoder/blob/main/.github/workflows/build-wasm.yml>
  - <https://github.com/dduan/TOMLDecoder/issues>
  - <https://github.com/dduan/TOMLDecoder/issues/326>
  - <https://github.com/dduan/TOMLDecoder/issues/330>
  - <https://github.com/dduan/TOMLDecoder/issues/264>
  - <https://github.com/dduan/TOMLDecoder/issues/232>
  - <https://github.com/dduan/TOMLDecoder/issues/67>
  - <https://github.com/dduan/TOMLDecoder/pulls>
  - <https://github.com/dduan/TOMLDecoder/pull/315>
  - <https://github.com/dduan/TOMLDecoder/pull/316>
  - <https://github.com/dduan/TOMLDecoder/releases>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/dduan/tomldecoder`) · [data/wave4/enrich/raw/github_com_dduan_tomldecoder.json](../../../data/wave4/enrich/raw/github_com_dduan_tomldecoder.json) (enrichment confidence 0.4)

</details>
