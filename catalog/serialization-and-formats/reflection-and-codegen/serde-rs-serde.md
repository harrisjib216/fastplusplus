# serde (serde_derive typed deserialization)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust's compile-time derive (de)serialization framework; through serde_json it beat a RapidJSON DOM parse 1.4-1.9x on kostya's JSON test.

| | |
|---|---|
| **Beats** | RapidJSON DOM parser and nlohmann/json (JSON libraries in the same suite; no Cereal or Boost.Serialization comparison found) |
| **Claimed result** | kostya/benchmarks Json table (medians; rows measured in the 2025-08-17 update and carried unchanged into the README dated 2026-07-19): Serde Typed (derive) 0.110 s and Serde Custom (derive plus visitor) 0.103 s vs C++ RapidJSON DOM 0.154 s (g++) and 0.194 s (clang++) and nlohmann/json 1.266 s (g++) and 1.182 s (clang++): about 1.4x-1.9x faster than default RapidJSON and about 10.7x-12.3x faster than nlohmann/json (derived from page data). Not faster than the closest declarative type-mapped C++ comparator in the suite, DAW JSON Link (0.085 s clang++, 0.089 s g++), nor than simdjson On-Demand (0.060-0.062 s). No comparison against Boost.Serialization or cereal exists. |
| **Workload** | Parse a generated, pretty-printed JSON file (json/generate_json.rb: 524,288 objects, each with x, y and z doubles, a name string and an opts object holding a one-element array, plus a top-level info string) and average the x, y and z values (kostya/benchmarks 'Json' test). Timed region is parse plus averaging; reading the file and the self-test run before the timer. The Serde Typed row is serde_json::from_str into a struct with #[derive(Deserialize)] (serde_derive code generation) holding only x, y and z; the Serde Custom row adds a hand-written Visitor through #[serde(deserialize_with)] that sums the array without storing it. The C++ rows build a full DOM. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) E-2324G; Docker image based on Debian GNU/Linux trixie/sid at the 2025-08-17 measurement (the 2026-07-19 README's Environment section now says forky/sid, but these Json rows were not re-measured then). |
| **Compiler and flags** | Measured toolchain (the Json rows date from the 2025-08-17 update, kostya/benchmarks commit 63ffa65, and are identical in the 2026-07-19 README, whose Versions table lists newer compilers that did not produce them): Rust 1.89.0, cargo build --release with RUSTFLAGS='-C target-cpu=native -C llvm-args=--x86-branches-within-32B-boundaries' and profile.release lto=true, codegen-units=1, panic=abort, strip=true (edition 2024); json.rs/Cargo.lock at that commit pinned serde/serde_derive 1.0.219 and serde_json 1.0.142, with no float_roundtrip feature. C++ baselines: g++ 14.2.0 and clang++ 19.1.7 (clang++ with -stdlib=libc++), -Wall -Wextra -pedantic -Wcast-align -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries -std=c++23 and no -DNDEBUG; RapidJSON built without RAPIDJSON_SSE2 or RAPIDJSON_SSE42; RapidJSON (miloyip/rapidjson) and nlohmann/json shallow-cloned from master at build time (json/Makefile, common/commands.mk). |
| **Adoption** | 10.9k stars |
| **Last commit** | 2026-10-16 |
| **Links** | [repository](https://github.com/serde-rs/serde) · [benchmark](https://github.com/kostya/benchmarks#json) |

## Verdict

The serde repository has no benchmark. The only numbers are kostya/benchmarks' Json rows, measured on 2025-08-17 on an Intel Xeon E-2324G with Rust 1.89.0, serde/serde_derive 1.0.219 and serde_json 1.0.142, LTO and target-cpu=native. There, serde_json::from_str into a derived three-field struct took 0.110 s (0.103 s with a custom Visitor), against 0.154 s (g++ 14.2.0) and 0.194 s (clang++ 19.1.7) for a full RapidJSON DOM parse and 1.182-1.266 s for nlohmann/json. The work is unequal (typed skipping against full DOM builds, C++ built without -DNDEBUG), and nothing compares serde with cereal or Boost.Serialization.

## Use it when

- Rust code that needs typed (de)serialization for one or more formats from one set of derives. The format crate (serde_json, postcard and so on) decides the throughput.
- Extract-a-few-fields JSON decoding in Rust. In kostya's test, the derive-only Serde Typed row took 0.110 s and 11.12 MiB of extra RSS; a hand-written Visitor attached with #[serde(deserialize_with)] took 0.103 s and 0.00 MiB.
- Zero-copy decoding from an in-memory buffer, using &str or &[u8] fields (borrowed implicitly) or Cow&lt;str&gt; with #[serde(borrow)], with Deserialize&lt;'de&gt; bounds rather than DeserializeOwned.
- no_std targets. The serde crate builds without std (crates.io categories no-std and no-std::no-alloc; alloc and std are features). The MSRV is Rust 1.56 for serde and 1.71 for serde_derive.

## Skip it when

- C++ projects. serde is Rust-only and has no C++ binding; use one of the C++ reflection or codegen serializers instead.
- Hot paths built on untagged enums or #[serde(flatten)], which go through Content buffering. In issue #2101 a hand-written Deserialize for one untagged enum cut a Cargo.toml parse in toml_edit from 484 us to 181 us. The maintainer's answer was that the slow part is the derive-generated code, and he pointed to a moratorium on new serde_derive attributes to control compile time.
- Builds sensitive to compile time or binary size. Every derived type adds proc-macro expansion and monomorphized code; issue #1146, 'Investigate compile time of serde crate', has been open since 2018 (cost not measured here).
- As evidence against cereal or Boost.Serialization. No such comparison exists. The only numbers are kostya JSON rows that measure serde_json plus serde_derive against DOM parsers, and on those rows DAW JSON Link (0.085-0.089 s) and simdjson On-Demand (0.060-0.062 s) are faster.
- Formats that need exact or unusual number types through flatten or untagged enums. Content cannot carry them: in serde_json, arbitrary_precision breaks there (issues #721 and #1108) and 128-bit integers fail inside untagged enums (#740).

## How it is fast

There is no runtime reflection: serde_derive is a proc macro (syn and quote) that emits per-type code at compile time. For a struct it generates a __Field enum, a match on the key string or index, and a visit_map loop that fills one Option per field by calling the format's next_value directly; unknown keys go to IgnoredAny, so the format skips them without building anything. After monomorphization and inlining this can approach a hand-written parser for that type and format, which the crate documentation claims. &str and &[u8] fields borrow from the input instead of allocating, and Cow fields do so with #[serde(borrow)]. The slow paths are features that need lookahead: #[serde(flatten)] and untagged or internally tagged enums buffer the value in serde's private Content tree and replay it.

## Compared with alternatives

No sibling in this category is Rust, so pick serde only when the code is Rust. For C++ binary serialization, bitsery, YAS and struct_pack carry benchmarks against Boost.Serialization, cereal or protobuf; for C++ JSON through reflection or codegen, simdjson's experimental_json_builder and Easy Reflection are the comparable approaches.

## Integration

| | |
|---|---|
| **Form** | crate (serde) plus a proc-macro crate (serde_derive, behind the derive feature) plus a separate format crate |
| **Dependencies** | serde_core (the traits); with the derive feature, serde_derive and its proc-macro2, quote and syn; a format crate such as serde_json |
| **Minimum toolchain** | Rust 1.56 for serde, Rust 1.71 for serde_derive (crates.io rust-version and README badges, serde 1.0.229) |
| **Platforms** | Any Rust target; std, alloc-only or no_std through features |
| **Thread safety** | Not documented. Derive-generated impls are plain functions over a per-call Serializer or Deserializer, so concurrency is governed by the format crate and the user's own types. |
| **Drop-in for the baseline** | no |

## Gotchas

- Unknown fields are skipped silently (IgnoredAny) unless the container has #[serde(deny_unknown_fields)], while a key that repeats a known struct field is a duplicate_field error.
- Borrowing is decided by type, not by input. Cow&lt;str&gt; never borrows without #[serde(borrow)], and borrowed types cannot be used with DeserializeOwned entry points such as serde_json::from_reader.
- Flatten and untagged or internally tagged enums buffer through Content: they allocate, try variants in order and build an error per failed attempt (issue #2101), and they lose formats' special number handling.
- serde_derive has an opt-in deserialize_in_place cargo feature that generates in-place deserialization to reuse existing allocations. It is off by default.

## Known shortcomings

- Downgraded A to C by verifier: no evidence of its own; the only numbers are serde_json's kostya Json rows (unequal work against DOM parsers, 2025-08-17 run, C++ baselines without -DNDEBUG), with no comparison against Boost.Serialization or cereal. Verifier suggested folding it into serde_json; kept because it is listed under reflection-and-codegen.
- no category baseline: no comparison against cereal or Boost.Serialization; numbers shared with the serde_json entry

## Caveats and trade-offs

The serde repository itself has no benchmark or performance numbers (its README only says 'efficiently'); the only numbers found are the kostya/benchmarks Serde rows, which exercise serde's derive path through serde_json on JSON text, so this measures serde_json plus serde_derive, not serde as a format-agnostic framework. No comparison against Boost.Serialization, cereal or a C++ reflection-based serializer was found; the baselines beaten (RapidJSON, nlohmann/json) are DOM-style JSON parsers outside the category's listed baselines. Not like for like: the typed rows skip the name and opts fields without allocating while the C++ rows build the whole document; the DOM-style serde_json::Value row (0.557 s) is slower than RapidJSON DOM (0.154-0.194 s). Asymmetric builds: the C++ flags carry no -DNDEBUG, so RAPIDJSON_ASSERT and nlohmann's JSON_ASSERT stay live as assert() (cost not measured), while the Rust release profile turns debug assertions off; RapidJSON is built without RAPIDJSON_SSE2/SSE42 on a whitespace-heavy pretty-printed file. Version drift: the README's Versions table (Rust 1.97.1, g++ 16.1.0, clang++ 22.1.8) does not describe these rows, which were measured on 2025-08-17 with Rust 1.89.0, g++ 14.2.0, clang++ 19.1.7, serde 1.0.219 and serde_json 1.0.142. The kostya build does not enable serde_json's float_roundtrip, so floats are parsed best-effort, as in default RapidJSON; RapidJSON Precise rows are 0.212 s (g++) and 0.262 s (clang++). UTF-8 validation runs in fs::read_to_string outside the Rust timer. The closest declarative, type-mapped C++ comparator, DAW JSON Link, is faster (0.085-0.089 s) and simdjson On-Demand is about 1.8x faster (0.060 s g++, derived from page data), so serde does not beat the best C++ typed parsers on this workload. The same suite and rows back the serde_json record (https://github.com/serde-rs/json) in this wave and wave14's lang:rust/kostya/benchmarks#json, so this record may fold into those. Single workload, one machine. [retier] Enricher: the evidence is the same kostya Json rows as the serde_json entry, so it measures serde's derive pattern through serde_json only; no comparison against cereal or Boost.Serialization (the category's C++ baselines) was found. Untagged enums and flatten buffer through an intermediate Content value (#2101: 484 vs 181 us) and break serde_json's arbitrary_precision (#721, #1108).

Rust-only framework: derive macros generate the (de)serializers at compile time (no runtime reflection), so a C++ project can only use it across an FFI or a separate process. Typed deserialization uses far less memory than a DOM (111.75 MiB base + 11.12 MiB for Serde Typed vs 113.21 + 123.44 MiB for g++ RapidJSON on the same page). Derive-generated code adds compile time and binary size (not measured here).

## Maintenance

Actively maintained (serde 1.0.229 released 2026-07-18, last commit 2026-10-16), MIT OR Apache-2.0, about 1.58 billion crates.io downloads; Rust-only, so for C++ it is a design reference, and its only evidence is the same kostya rows as the serde_json entry.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The only numbers are the kostya/benchmarks Json rows (public code json/json.rs/src/json_struct.rs and json_pull.rs against json/test_rapid.cpp and test_nlohmann_json.cpp; flags in common/commands.mk; Xeon E-2324G), which test serde's derive path through serde_json against DOM JSON parsers, not against the category baselines Boost.Serialization or cereal. The win rests on unequal work (typed decoding that skips fields against full DOM builds) and on C++ baselines built without -DNDEBUG, so it is capped at C like the same rows in wave14's lang:rust/kostya/benchmarks#json; the record's compiler versions were also wrong (rows measured 2025-08-17).
- **Verifier notes:** Same kostya rows as the serde_json record in this batch; nothing serde-specific beyond the derive path and no reflection-and-codegen baseline (Boost.Serialization, cereal), so recording it as a duplicate of https://github.com/serde-rs/json is reasonable. Metadata confirmed: MIT OR Apache-2.0, 10.9k stars, last commit 2026-10-16, not archived or a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-64 (wave 4 book seed pass, 2026-10-24); enrichment (wave 4 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://github.com/kostya/benchmarks/commits/master/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/4d4ac9a/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/json/json.rs/Cargo.lock>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_struct.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_pull.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_rapid.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_nlohmann_json.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/generate_json.rb>
  - <https://github.com/serde-rs/serde>
  - <https://github.com/serde-rs/serde/commits/master>
- **Sources the enricher read:**
  - <https://github.com/serde-rs/serde>
  - <https://github.com/serde-rs/serde/commits/master>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/README.md>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/crates-io.md>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde/Cargo.toml>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde_core/Cargo.toml>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde_derive/Cargo.toml>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde/src/lib.rs>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde_core/src/lib.rs>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde_derive/src/lib.rs>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde_derive/src/de.rs>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde_derive/src/de/identifier.rs>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde_derive/src/de/struct_.rs>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde_derive/src/de/enum_untagged.rs>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde_derive/src/de/enum_internally.rs>
  - <https://raw.githubusercontent.com/serde-rs/serde/HEAD/serde_derive/src/internals/attr.rs>
  - <https://github.com/serde-rs/serde/issues?q=is%3Aissue+label%3Aperformance>
  - <https://github.com/serde-rs/serde/issues/2101>
  - <https://crates.io/api/v1/crates/serde>
  - <https://raw.githubusercontent.com/serde-rs/json/HEAD/src/de.rs>
  - <https://github.com/serde-rs/json/issues?q=is%3Aissue+is%3Aopen+float>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_struct.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_pull.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_rapid.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/serde-rs/serde`) · [data/wave4/enrich/raw/github_com_serde_rs_serde.json](../../../data/wave4/enrich/raw/github_com_serde_rs_serde.json) (enrichment confidence 0.7)

</details>
