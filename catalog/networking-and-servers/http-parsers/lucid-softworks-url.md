# lucid-url

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Dependency-free, safe-Rust WHATWG URL parser with Ada's API; faster than ada::url, slower than ada::url_aggregator and can_parse.

| | |
|---|---|
| **Beats** | ada-url (C++ Ada) |
| **Claimed result** | Url parse+href: 85.41ns vs Ada's 108.54ns (1.27x faster); UrlAggregator parse+href: 59.70ns vs Ada's 57.26ns (0.96x, i.e. slower); can_parse: 12.95ns vs Ada's 11.25ns (0.87x, i.e. slower) -- mixed result, faster on only 1 of 3 measured operations |
| **Workload** | Google Benchmark comparison, official Ada v4 release-benchmark protocol (parse+href and can_parse, mean of five repetitions), run over Ada's pinned 100,025-URL dataset against a dependency-free Rust WHATWG URL parser with an Ada-compatible interface |
| **Metric** | latency |
| **Hardware** | Apple M4, macOS 26.5 |
| **Compiler and flags** | Rust 1.98.0 (opt-level=3, codegen-units=1, panic=abort, -C target-cpu=native) vs Apple Clang 21 building amalgamated Ada with -O3 -DNDEBUG -mcpu=native -fomit-frame-pointer (per benchmarks/run.sh); LTO matched by being OFF on both sides on macOS (on for both on Linux); ADA_USE_SIMDUTF=OFF, ADA_INCLUDE_URL_PATTERN=ON (Ada defaults) |
| **Adoption** | 4 stars |
| **Last commit** | 2026-09-07 |
| **Links** | [repository](https://github.com/lucid-softworks/url) · [benchmark](https://github.com/lucid-softworks/url/blob/main/README.md) |

## Verdict

The benchmark links Lucid and amalgamated Ada b2c2d7f6 into one Google Benchmark binary and runs Ada's pinned 100,025-URL corpus, taking the mean of 5 reps. Setup: Apple M4, macOS 26.5, Rust 1.98.0 with target-cpu=native against Apple Clang 21 at -O3 -mcpu=native, LTO off on both sides, simdutf off. Result: Lucid `Url` parse+href 85.41 vs `ada::url` 108.54 ns/URL (1.27x); `UrlAggregator` 59.70 vs `ada::url_aggregator` 57.26 (Ada \~4% faster); can_parse 12.95 vs 11.25 (Ada \~15% faster). The raw JSON matches these numbers, shows zero validity or serialization disagreements, and records a 1-minute load average of \~4.5.

## Use it when

- You need WHATWG-conformant URL parsing in pure safe Rust, with no C++ toolchain, FFI or unsafe code, and want Ada's API shape and Ada-fixture conformance.
- Getter-heavy code on `UrlAggregator`: component getters are borrowed slices of one buffer with no allocation.
- Code that repeatedly rewrites the query, fragment or credentials of http(s)/ws/ftp URLs: these setters edit a range in place, at \~15 ns for an ASCII query and \~100 ns for a Unicode query on an M4. That is a Lucid before/after gain, not a comparison with Ada.
- You are porting code built on Ada's multi-string `ada::url` and parse-plus-href cost matters: Lucid's `Url` took 85.41 vs 108.54 ns/URL. Lucid's own `UrlAggregator` is faster still, at 59.70.
- Mostly absolute, canonical http(s) inputs such as crawled or logged URLs, which stay on the fastest scanner path.

## Skip it when

- Top parse or validation throughput: in the project's own run Ada's `url_aggregator` (57.26 vs 59.70 ns/URL) and `can_parse` (11.25 vs 12.95 ns/URL) are faster, and the README says parsing experiments 'did not show a dependable across-the-board gain'.
- Hot relative-URL resolution: with a base, every call reparses the base href and runs the char-based state machine, skipping all fast paths. There is no benchmark for this case.
- Hot hostname/host/port/pathname/protocol setters: they reparse the whole URL through the generic state machine and rebuild it. Before the range-edit work, query and credential setters on this same path took \~2.5-3.9 µs per call.
- You need URLSearchParams, URLPattern, Ada's C API, a crates.io release or semver guarantees: none exist yet. The 0.1.0 release PR is still open.
- Binary size or maturity matter: the native object is 45% larger than Ada's (462.1 vs 318.4 KiB, measured against an older Ada pin) because of built-in Unicode/IDNA tables. The repo is \~2 months old with 4 stars, and there is no fuzzing (the fuzz targets are out of scope and not in the tree).

## How it is fast

Several fast paths run before a full parse. The first is a single-pass scanner for already-canonical http(s) URLs. It checks bytes against a 256-entry byte-class bitmask table, ANDing class bits for 8, 4 or 2 bytes at a time, and on success copies the input verbatim into the buffer and records offsets. Further direct paths cover ftp/ws/wss, common normalization (percent-encoding, dot segments, IPv4, IPv6, IDNA) and clean non-special URLs; anything else goes to a spec-literal state machine over a `Vec<char>`, whose result is re-serialized into the aggregator. There is no SIMD (the author dropped the hostname-SWAR and wider-scan-block experiments). The large setter gains come from rewriting only the affected byte range and shifting offsets instead of reparsing.

## Compared with alternatives

Choose it over Ada (C++, or Ada's Rust bindings) only when pure safe Rust with no C++ build is worth \~4% slower aggregator parsing and \~15% slower can_parse. Over sorug, another pure-Rust WHATWG parser that is benchmarked against servo url rather than Ada, choose it when you want Ada's API and Ada's fixture suite; ada-rs publishes a larger lead over C++ Ada, but only on a 9-URL corpus.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (std only; serde_json is dev-only) |
| **Minimum toolchain** | Rust 1.87 (declared rust-version, edition 2024); CI only tests stable |
| **Platforms** | any Rust target (pure safe Rust, no arch-specific code); CI tests Linux, macOS and Windows; published performance numbers cover only Apple M4 (aarch64) |
| **Thread safety** | Not documented. Both types are plain owned data (a String plus offsets) with no interior mutability. The max-input-length limit is a process-global `AtomicU32` using Relaxed ordering. |
| **Drop-in for the baseline** | partial — the Rust API reuses Ada's C++ names (parse::&lt;Url\|UrlAggregator&gt;, can_parse, get_\*/set_\*/has_\*, get_components) but it is not a C/C++ ABI replacement, it has no url_search_params, URLPattern or ada_c, and `Url` is internally an aggregator, not Ada's multi-string layout |

## Gotchas

- `Url` only wraps `UrlAggregator`. Its owned getters (get_href, get_protocol, get_host, get_hostname, get_port, get_search, get_hash) clone into a new String on every call. The headline 1.27x win comes from this layout difference, and `UrlAggregator` is the faster type to use.
- Only set_search/set_hash on special non-opaque URLs and set_username/set_password on special non-file URLs are in-place range edits. Every other setter, and those same setters on file, non-special or opaque URLs, reparses the whole buffer.
- Setting `set_max_input_length` to anything except the default u32::MAX makes `can_parse` skip every fast path and run a full parse. The setting is global to the process.
- The error type has a single `TypeError` variant ('invalid URL'), so it gives no detail on why a parse failed.

## Known shortcomings

- Not faster than Ada in practice: the only win (1.27x) is owned Url against ada::url, Ada's heavier type; against ada::url_aggregator (what Ada's README uses) and on can_parse it is slower. The author says parsing showed no dependable across-the-board gain.
- Most setters (protocol, host, port, pathname) still reparse the whole URL; parsing with a base always takes the slow path; setting a non-default max input length disables all can_parse fast paths. Not on crates.io; no fuzzing; Apple M4 numbers only.

## Caveats and trade-offs

Only one of the three headline operations (owned Url parse+href vs ada::url) is faster than Ada, and ada::url is Ada's heavier multi-string representation; Ada's own README examples all use ada::url_aggregator, and against it Lucid's UrlAggregator is slower (59.70 vs 57.26 ns/URL), as is can_parse (12.95 vs 11.25 ns). The README itself says Ada is \~1.04x faster for aggregator parsing and \~1.15x faster for can_parse and that 'parsing experiments did not show a dependable across-the-board gain'; the large setter speedups (up to \~174x) are Lucid before/after, not versus Ada. Single machine; Google Benchmark context records a 1-minute load average of \~4.5 during the run.

no unsafe dependency on Ada itself (pure Rust, stdlib-only); the project's own README acknowledges Ada is faster on 2 of the 3 core parse/can_parse benchmarks and that 'parsing experiments did not show a dependable across-the-board gain'; native code footprint is 45% larger than Ada's

## Maintenance

Active (created 2026-07-30, last commit 2026-09-07) and MIT-licensed, but not yet on crates.io, so use it as a git dependency. It is small, dependency-free safe Rust that can be vendored, and a daily CI job tracks Ada main's fixtures.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification A, tier now A.
- **Tier reason:** README runs Ada's own v4 Google Benchmark protocol via public code (benchmarks/run.sh + benchmarks/official_compare.cpp + benchmarks/official_bridge) against Ada pinned at b2c2d7f6 on the pinned 100,025-URL dataset, stating CPU (Apple M4), compilers (Rust 1.98.0, Apple Clang 21) and flags (run.sh: -O3 -DNDEBUG -mcpu=native -fomit-frame-pointer for C++, -C target-cpu=native for Rust, LTO off on both sides on macOS); raw JSON benchmarks/results/ada-b2c2d7f6-merged.json matches the README table exactly. The evidence is A-grade, but it shows Ada winning.
- **Verifier notes:** Rejected as not-faster: the fastest representation of each library (UrlAggregator vs ada::url_aggregator) and can_parse both favor Ada in the project's own run, and the author explicitly disclaims a general parsing gain; the only win is against ada::url, Ada's heavier multi-string representation (all of Ada's README examples use ada::url_aggregator). Record's numbers, hardware, license (MIT), stars (4) and last commit (2026-09-07) are otherwise accurate; if the orchestrator keeps partial-win entries, tier A with the compiler_and_flags correction applies.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lucid-softworks/url>
  - <https://github.com/lucid-softworks/url/blob/main/README.md>
  - <https://github.com/lucid-softworks/url/blob/main/benchmarks/METHODOLOGY.md>
  - <https://github.com/lucid-softworks/url/blob/main/benchmarks/run.sh>
  - <https://github.com/lucid-softworks/url/blob/main/benchmarks/official_compare.cpp>
  - <https://github.com/lucid-softworks/url/blob/main/benchmarks/results/ada-b2c2d7f6-merged.json>
  - <https://github.com/lucid-softworks/url/blob/main/Cargo.toml>
  - <https://github.com/ada-url/ada/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/lucid-softworks/url>
  - <https://github.com/lucid-softworks/url/blob/main/README.md>
  - <https://github.com/lucid-softworks/url/blob/main/Cargo.toml>
  - <https://github.com/lucid-softworks/url/blob/main/benchmarks/METHODOLOGY.md>
  - <https://github.com/lucid-softworks/url/blob/main/benchmarks/run.sh>
  - <https://github.com/lucid-softworks/url/blob/main/benchmarks/official_compare.cpp>
  - <https://github.com/lucid-softworks/url/blob/main/benchmarks/official_bridge/src/lib.rs>
  - <https://github.com/lucid-softworks/url/blob/main/benchmarks/results/ada-b2c2d7f6-merged.json>
  - <https://github.com/lucid-softworks/url/blob/main/benchmarks/results/setters-after.txt>
  - <https://github.com/lucid-softworks/url/blob/main/tests/ADA_TEST_SCOPE.md>
  - <https://github.com/lucid-softworks/url/blob/main/tests/ada_conformance.rs>
  - <https://github.com/lucid-softworks/url/blob/main/tests/fixtures/ada/wpt/IdnaTestV2.json>
  - <https://github.com/lucid-softworks/url/blob/main/.github/workflows/ci.yml>
  - <https://github.com/lucid-softworks/url/blob/main/src/lib.rs>
  - <https://github.com/lucid-softworks/url/blob/main/src/legacy.rs>
  - <https://github.com/lucid-softworks/url/blob/main/src/suffix_edit.rs>
  - <https://github.com/lucid-softworks/url/blob/main/src/credential_edit.rs>
  - <https://github.com/lucid-softworks/url/blob/main/src/idna.rs>
  - <https://github.com/lucid-softworks/url/issues>
  - <https://github.com/lucid-softworks/url/pull/1>
  - <https://github.com/lucid-softworks/url/commits/main>
  - <https://crates.io/api/v1/crates/lucid-url>
  - <https://github.com/ada-url/ada/blob/main/README.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/lucid-softworks/url`) · [data/wave5/enrich/raw/github_com_lucid_softworks_url.json](../../../data/wave5/enrich/raw/github_com_lucid_softworks_url.json) (enrichment confidence 0.8)

</details>
