# serde_json (typed, #[derive(Deserialize)])

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust's standard JSON crate; typed derive decoding beat a RapidJSON DOM parse 1.4-1.8x in kostya's suite, but not simdjson.

| | |
|---|---|
| **Beats** | RapidJSON (DOM parser) and nlohmann/json; simdjson is faster |
| **Claimed result** | kostya/benchmarks Json table (medians; rows measured in the 2025-08-17 update and carried unchanged into the README dated 2026-07-19): Rust Serde Typed 0.110 s vs C++ RapidJSON 0.154 s (g++) and 0.194 s (clang++), RapidJSON Precise 0.212 s (g++) and 0.262 s (clang++), and nlohmann/json 1.266 s (g++) and 1.182 s (clang++). That is about 1.4x-1.8x faster than default RapidJSON, 1.9x-2.4x faster than RapidJSON Precise and 10.7x-11.5x faster than nlohmann/json (derived from page data). Rust Serde Custom (derive plus a hand-written visitor that folds the array without storing it) takes 0.103 s. Not faster than simdjson On-Demand 0.060 s (g++) / 0.062 s (clang++) or DAW JSON Link 0.085 s (clang++) / 0.089 s (g++); about equal to simdjson DOM 0.103 s (clang++) / 0.107 s (g++). The like-for-like DOM row, Rust Serde Untyped (serde_json::Value) at 0.557 s, is about 2.1x-2.3x faster than nlohmann/json but about 2.9x-3.6x slower than RapidJSON DOM (derived from page data). |
| **Workload** | Parse a generated, pretty-printed JSON file (json/generate_json.rb: 524,288 objects, each with x, y and z doubles, a name string and an opts object holding a one-element array, plus a top-level info string) and average the x, y and z values (kostya/benchmarks 'Json' test). Timed region is parse plus averaging; reading the file and the self-test run before the timer. The Serde Typed row is serde_json::from_str into a #[derive(Deserialize)] struct with only x, y and z fields; the C++ rows build a full DOM. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) E-2324G; Docker image based on Debian GNU/Linux trixie/sid at the 2025-08-17 measurement (the 2026-07-19 README's Environment section now says forky/sid, but the Json rows for Rust, RapidJSON and nlohmann/json were not re-measured then). |
| **Compiler and flags** | Measured toolchain (the Json rows date from the 2025-08-17 update, kostya/benchmarks commit 63ffa65, and are identical in the 2026-07-19 README, whose Versions table lists newer compilers that did not produce them): Rust 1.89.0, cargo build --release with RUSTFLAGS='-C target-cpu=native -C llvm-args=--x86-branches-within-32B-boundaries' and profile.release lto=true, codegen-units=1, panic=abort, strip=true (edition 2024); json.rs/Cargo.lock at that commit pinned serde_json 1.0.142 and serde/serde_derive 1.0.219, with no float_roundtrip feature. C++ baselines: g++ 14.2.0 and clang++ 19.1.7 (clang++ with -stdlib=libc++), -Wall -Wextra -pedantic -Wcast-align -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries -std=c++23 and no -DNDEBUG; RapidJSON built without RAPIDJSON_SSE2 or RAPIDJSON_SSE42; RapidJSON (miloyip/rapidjson), nlohmann/json and simdjson shallow-cloned from master at build time (json/Makefile, common/commands.mk). |
| **Adoption** | 5.7k stars |
| **Last commit** | 2026-10-16 |
| **Links** | [repository](https://github.com/serde-rs/json) · [benchmark](https://github.com/kostya/benchmarks#json) |

## Verdict

In kostya/benchmarks' Json test, the rows were measured on 2025-08-17 on an Intel Xeon E-2324G in a Debian trixie/sid Docker image with Rust 1.89.0, serde_json 1.0.142, LTO and target-cpu=native, and carried unchanged into the 2026-07-19 README. serde_json::from_str into a derived struct holding only x, y and z took 0.110 s (0.103 s with a folding visitor), against 0.154 s (g++ 14.2.0) and 0.194 s (clang++ 19.1.7, libc++) for a full RapidJSON DOM parse and 1.182-1.266 s for nlohmann/json. The work is unequal: typed skipping against full DOM builds, with C++ built without -DNDEBUG and RapidJSON without its SSE paths, though serde_json's whitespace skipping is scalar too. The like-for-like serde_json::Value row took 0.557 s, slower than RapidJSON.

## Use it when

- Rust code that decodes JSON with a known schema into structs, especially large documents where only a few fields matter. Unknown keys are skipped without allocating: in kostya's test the derived three-field struct added 11.12 MiB of RSS, against 123.44 MiB for RapidJSON's DOM (g++).
- Folding huge arrays without materializing them. A hand-written Visitor hooked in with #[serde(deserialize_with)] or a DeserializeSeed processed 524,288 objects in 0.103 s with 0.00 MiB extra RSS (kostya's Serde Custom row).
- Input that is already in memory. Call from_str or from_slice on a buffer. In issue #160 a 23 MiB file took 4710 ms with unbuffered from_reader, 562 ms with a BufReader, and 55 ms with from_str or from_slice.
- Portable or embedded Rust builds. The crate is pure Rust with no target-specific intrinsics, picks 64-bit limb arithmetic on 64-bit targets in build.rs, and supports no_std plus alloc (default-features = false, features = ["alloc"]).

## Skip it when

- A C++ codebase that wants faster JSON. On the same kostya test, simdjson On-Demand (0.060 s with g++) and DAW JSON Link (0.085-0.089 s) beat Serde Typed (0.110 s) natively, and simdjson DOM (0.103-0.107 s) ties it.
- Dynamic or untyped JSON. serde_json::Value took 0.557 s and added 839.75 MiB in kostya's test, 2.9x-3.6x slower than RapidJSON's DOM (derived from page data). Value objects are a BTreeMap&lt;String, Value&gt; with owned keys (an IndexMap with preserve_order), and issue #635 reports Value using more than 10x the input size in memory.
- Rust code where raw parse throughput is the bottleneck. sonic-rs's README (Xeon Platinum 8260) shows twitter.json struct decoding at 0.708 ms for sonic_rs::from_slice_unchecked, against 1.384 ms for serde_json::from_str and 2.290 ms for serde_json::from_slice, and canada.json to a DOM at 4.957 ms against 16.980 ms.
- Data that must round-trip floats exactly, unless you enable float_roundtrip. The default parser is best-effort, and the feature costs about 2x on float parsing per the crate's Cargo.toml.
- Unbuffered streaming Read sources. from_reader adds no buffering of its own and is the slowest entry point (issue #160 is still open).

## How it is fast

On the typed path no tree is built. serde_derive generates a field-name match and a visitor for each struct, and serde_json's recursive-descent Deserializer calls them while it scans. Keys the struct does not name are skipped by ignore_value, which keeps an explicit bracket stack and allocates nothing, and strings without escapes come back as slices borrowed from the input. Strings are scanned with a SWAR (Mycroft-style word-at-a-time) test for quote, backslash and control bytes, or with memchr2 where control bytes are allowed. Whitespace is skipped one byte at a time and there is no SIMD stage (issue #120, 'SIMD vectorization behind a feature flag', open since 2016). Floats take a best-effort path by default: the u64 significand is cast to f64, then multiplied or divided by one power-of-ten table entry. Exact parsing (the float_roundtrip feature, a vendored lexical port) is opt-in and costs about 2x on floats. Output uses itoa for integers and, since 1.0.147, the Żmij float formatter in place of Ryū.

## Compared with alternatives

Pick serde_json when you write Rust and want the ecosystem default: typed derive decoding, no target-specific code, and the widest format and crate interoperability. If the parse itself is the bottleneck, sonic-rs and simd-json (Rust) are faster per their READMEs. A C++ project should use simdjson or yyjson natively rather than cross an FFI to reach serde_json.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | serde_core (&gt;= 1.0.220), itoa, memchr, zmij; optional indexmap and foldhash for preserve_order. User code adds serde with the derive feature for typed decoding. |
| **Minimum toolchain** | Rust 1.71 (rust-version of 1.0.150-1.0.154; 1.0.142, the version measured in kostya's suite, declared 1.56) |
| **Platforms** | Any Rust target, with no SIMD intrinsics and no CPU-feature requirement; std, or no_std with alloc |
| **Thread safety** | Not documented. Each Deserializer or Serializer is a single-threaded cursor over its own input, and the source files read (de.rs, read.rs, ser.rs, value/mod.rs) have no global mutable state, so independent parses can run on separate threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- Nesting depth is capped at 128 (remaining_depth) and deeper input returns an error. Turning the cap off with disable_recursion_limit needs the unbounded_depth feature plus a stack guard such as serde_stacker. The maintainer closed issue #1327, a stack overflow from comparing Values nested 100,000 deep, as not a serde_json vulnerability, pointing to the 128 limit on parsed data.
- Default float parsing rounds twice (cast the significand, then multiply or divide by POW10), so values with 16-17 significant digits, like the random doubles kostya's generator writes, can come out 1-2 ULP off (an earlier enricher's emulation found this for about 35% of x values). Serialization switched from Ryū to Żmij in 1.0.147, which changed some output strings (issues #1309 and #1340 are open).
- from_str trusts the UTF-8 of its &str (StrRead uses str::from_utf8_unchecked), while from_slice validates strings during the parse and is slower: 2.290 ms against 1.384 ms on twitter.json struct decoding in sonic-rs's README. In kostya's harness the UTF-8 check runs in fs::read_to_string before the timer starts. That is no advantage over default RapidJSON, whose default flags (kParseNoFlags) leave kParseValidateEncodingFlag off, but it matters against parsers that validate inside the timed region.
- #[serde(flatten)], untagged enums and internally tagged enums buffer each value in serde's private Content tree, which costs allocations and breaks arbitrary_precision (issues #721 and #1108) and 128-bit integers inside untagged enums (#740). Unknown fields are ignored silently unless the struct has #[serde(deny_unknown_fields)].

## Known shortcomings

- Downgraded A to C by verifier: the win over RapidJSON and nlohmann/json comes from unequal work (the typed decode skips the name and opts fields while the C++ rows build a full DOM); the like-for-like Serde Untyped row is 2.9-3.6x slower than RapidJSON; C++ baselines built without -DNDEBUG and RapidJSON without its SSE paths; the rows date from the 2025-08-17 run (Rust 1.89.0, g++ 14.2.0, clang++ 19.1.7), not the listed toolchain. serde_json is itself a listed json baseline.
- from_reader without a BufReader is about 85x slower than from_str (#160); 128-level nesting limit

## Caveats and trade-offs

1) Not like for like: the typed Rust rows deserialize only x, y and z and skip name and opts without allocating (Serde Custom does not even store the array), while the RapidJSON and nlohmann/json rows build the whole document; the like-for-like DOM row (Serde Untyped, 0.557 s) loses to RapidJSON (0.154-0.194 s). 2) Asymmetric builds: the C++ flags carry no -DNDEBUG, so RAPIDJSON_ASSERT and nlohmann's JSON_ASSERT stay live as assert() (cost not measured), while the Rust release profile turns debug assertions off; RapidJSON is also built without RAPIDJSON_SSE2/SSE42, so its SIMD whitespace skipping is off on a pretty-printed, whitespace-heavy file. 3) Version drift: the README's Versions table (Rust 1.97.1, g++ 16.1.0, clang++ 22.1.8, serde_json 1.0.150) does not describe these rows; they were measured on 2025-08-17 with Rust 1.89.0, g++ 14.2.0, clang++ 19.1.7 and serde_json 1.0.142. 4) Float handling: the kostya Cargo.toml enables no float_roundtrip, so serde_json parses floats best-effort (an emulation by a wave14 enricher put 1-2 ULP errors on about 35% of the x values and about 10% of y and z); the README's list of inexact parsers names default RapidJSON but omits serde_json, and only the RapidJSON Precise rows (0.212/0.262 s) are exact, so the margin over Precise is not a same-accuracy comparison. UTF-8 validation of the input runs in fs::read_to_string outside the Rust timer. 5) simdjson On-Demand (0.060 s g++, 0.062 s clang++) is about 1.8x faster than Serde Typed and DAW JSON Link (0.085-0.089 s) about 1.2x-1.3x faster (derived from page data), so serde_json is not the fastest JSON option here. 6) Single workload on one machine from a third-party multi-language suite; medians with median absolute deviation. 7) The crate README's claim ('500 to 1000 megabytes per second deserialization and 600 to 900 megabytes per second serialization ... competitive with the fastest C and C++ JSON libraries or even 30% faster for many use cases') carries no table; its linked https://github.com/serde-rs/json-benchmark (archived by its owner 2024-05-20; serde_json 1.0.72, rustc 1.59.0-nightly 2021-12-07, Intel Core i7-6600U; C++ built with -std=c++1z -O3 under clang 11.0.0 and gcc 10.1.0) shows serde_json DOM parse at 320/420/300 MB/s (canada/citm_catalog/twitter), slower than RapidJSON's 380-390/680-890/320-440 MB/s on all three files; DOM stringify is faster on canada (430 vs 200-250 MB/s) and twitter (910 vs 600-870 MB/s) but slower on citm_catalog (560 vs 1090-1650 MB/s); struct parse is 580/710/550 MB/s with no labelled C++ struct column. That Rust harness sets jemalloc as the global allocator while the C++ harness uses the default allocator, the README's RapidJSON table does not say whether its columns are DOM or struct, and the committed cpp/main.cc runs only canada.json (citm_catalog and twitter are commented out), so those rows are not reproducible as committed. 8) serde_json is itself one of the json category's listed baselines. [retier] Enricher corrections: on caveat 4, UTF-8 validation outside the Rust timer is not an asymmetry against default RapidJSON, whose default kParseNoFlags leaves kParseValidateEncodingFlag off; it is an asymmetry only against parsers that validate inside the timer. On caveat 2, RapidJSON built without SSE is not an advantage taken by serde_json, whose parse_whitespace is also byte by byte with no SIMD (issue #120 open since 2016); it only means RapidJSON is not at its best configuration. Gotchas: 128-level nesting limit (#1327); from_reader is slow without a BufReader (#160: 23 MiB file, 4710 ms unbuffered vs 55 ms from_str); from_slice vs from_str on twitter.json struct decode 2.290 vs 1.384 ms (sonic-rs README); serde_json::Value maps are BTreeMaps with heavy memory use (#635); 1.0.147 replaced Ryu with Zmij for float output, changing printed floats (#1309, #1340 open); untagged and flatten buffer through Content (#2101: 484 vs 181 us) and break arbitrary_precision (#721, #1108).

Rust crate; a C++ project must reach it through an FFI or a separate process. Typed deserialization needs the target types known at compile time (derive), ignores unknown fields by default and uses far less memory than a DOM (111.75 MiB base + 11.12 MiB for Serde Typed vs 113.21 + 123.44 MiB for g++ RapidJSON and 447.88 MiB increase for g++ nlohmann/json on the same page). The untyped serde_json::Value DOM is much slower (0.557 s) and uses 839.75 MiB extra. float_roundtrip (exact float round-tripping) is an opt-in feature that costs about 2x float-parse speed per the crate's Cargo.toml comment.

## Maintenance

Actively maintained (1.0.154 released 2026-10-11, last commit 2026-10-16), MIT OR Apache-2.0, about 1.49 billion crates.io downloads; usable from C++ only across an FFI or process boundary.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The kostya/benchmarks Json table has every quoted row, and the harness is public (json/json.rs/src/json_struct.rs, json_pull.rs and json_value.rs against json/test_rapid.cpp and test_nlohmann_json.cpp; flags in common/commands.mk and json/Makefile; Xeon E-2324G), but the win over RapidJSON and nlohmann/json comes from unequal work (typed decoding that skips name and opts against full DOM builds; the like-for-like serde_json::Value row is 2.9x-3.6x slower than RapidJSON) and from C++ baselines built without -DNDEBUG or RapidJSON SIMD, so it is capped at C, matching the tier given to the same rows in wave14 (lang:rust/kostya/benchmarks#json). The record's compiler versions were also wrong: these rows date from the 2025-08-17 run.
- **Verifier notes:** Numbers match the kostya README exactly, but the Json rows for Rust, RapidJSON and nlohmann/json are byte-identical to the 2025-08-17 README (commit 63ffa65), so they were measured with Rust 1.89.0 / g++ 14.2.0 / clang++ 19.1.7, not the versions in the current table; all compared rows come from that same run. The same rows already back wave14's lang:rust/kostya/benchmarks#json (tier C); that entry's yyjson rows (0.131/0.132 s) first appeared in the 2026-07-19 update, so its Serde Custom vs yyjson ratio is a cross-run comparison and its recorded Rust 1.97.1 / serde_json 1.0.150 toolchain is wrong (retier candidate).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-64 (wave 4 book seed pass, 2026-10-24); enrichment (wave 4 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://github.com/kostya/benchmarks/tree/master/json>
  - <https://github.com/kostya/benchmarks/commits/master/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/4d4ac9a/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/199aa74/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/json/json.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/json/json.rs/Cargo.lock>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/Cargo.lock>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_struct.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_pull.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_value.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_rapid.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_nlohmann_json.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/generate_json.rb>
  - <https://raw.githubusercontent.com/Tencent/rapidjson/master/include/rapidjson/rapidjson.h>
  - <https://raw.githubusercontent.com/nlohmann/json/develop/include/nlohmann/detail/macro_scope.hpp>
  - <https://github.com/serde-rs/json>
  - <https://github.com/serde-rs/json/commits/master>
  - <https://github.com/serde-rs/json-benchmark>
  - <https://raw.githubusercontent.com/serde-rs/json-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/serde-rs/json-benchmark/master/cpp/main.cc>
  - <https://raw.githubusercontent.com/serde-rs/json-benchmark/master/cpp/Makefile>
  - <https://raw.githubusercontent.com/serde-rs/json-benchmark/master/Cargo.toml>
  - <https://raw.githubusercontent.com/serde-rs/json-benchmark/master/src/main.rs>
- **Sources the enricher read:**
  - <https://github.com/serde-rs/json>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/README.md>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/build.rs>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/src/de.rs>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/src/read.rs>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/src/ser.rs>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/src/value/mod.rs>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/src/map.rs>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/src/number.rs>
  - <https://github.com/serde-rs/json/releases>
  - <https://github.com/serde-rs/json/commits/master>
  - <https://github.com/serde-rs/json/issues?q=is%3Aissue+label%3Aperformance>
  - <https://github.com/serde-rs/json/issues?q=is%3Aissue+is%3Aopen+float>
  - <https://github.com/serde-rs/json/issues?q=is%3Aissue+stack+overflow+OR+recursion+OR+duplicate+key>
  - <https://github.com/serde-rs/json/issues/160>
  - <https://github.com/serde-rs/json/issues/635>
  - <https://github.com/serde-rs/json/issues/1327>
  - <https://crates.io/api/v1/crates/serde_json>
  - <https://raw.githubusercontent.com/serde-rs/json-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/Cargo.lock>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_struct.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_pull.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_value.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_rapid.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/generate_json.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/Tencent/rapidjson/master/include/rapidjson/reader.h>
  - <https://raw.githubusercontent.com/cloudwego/sonic-rs/main/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/serde-rs/json`) · [data/wave4/enrich/raw/github_com_serde_rs_json.json](../../../data/wave4/enrich/raw/github_com_serde_rs_json.json) (enrichment confidence 0.8)

</details>
