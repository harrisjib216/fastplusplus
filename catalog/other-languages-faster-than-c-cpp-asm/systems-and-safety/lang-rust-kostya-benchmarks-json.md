# Rust serde (kostya/benchmarks json)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> serde_json typed streaming deserializer in kostya/benchmarks: 0.103 s versus 0.131 s for C yyjson DOM parsing, not like for like.

| | |
|---|---|
| **Beats** | C yyjson (gcc and clang) and C++ gason / RapidJSON DOM parsers |
| **Claimed result** | Same-run rows (2025-08-17 update, kostya/benchmarks commit 63ffa65, carried unchanged into the 2026-07-19 README): Rust (Serde Typed) 0.110 s and Rust (Serde Custom) 0.103 s versus C++/g++ RapidJSON 0.154 s (clang++ 0.194 s), about 1.4x-1.9x faster (derived from page data). Not faster than C++/g++ simdjson On-Demand 0.060 s or C++/clang++ DAW JSON Link 0.085 s; about equal to simdjson DOM 0.103 s (clang++). Rust doing like-for-like DOM parsing (Serde Untyped) takes 0.557 s, 2.9-3.6x slower than RapidJSON. The C yyjson rows (0.131/0.132 s) first appeared in the 2026-07-19 update, so the Serde Custom versus yyjson 1.27x compares two runs and toolchains (cross-run, not a valid comparison); check gason's row date before using it. |
| **Workload** | Parse a big JSON file and compute simple values from it; seconds. |
| **Metric** | latency |
| **Hardware** | Intel Xeon E-2324G, Debian forky/sid Docker image |
| **Compiler and flags** | Measured toolchain for the Serde, RapidJSON and nlohmann/json rows (2025-08-17 update, commit 63ffa65; the 2026-07-19 Versions table lists newer compilers that did not produce them): Rust 1.89.0 with RUSTFLAGS='-C target-cpu=native -C llvm-args=--x86-branches-within-32B-boundaries' cargo build --release, profile lto = true, codegen-units = 1, panic = abort; serde_json 1.0.142 and serde 1.0.219. C++: g++ 14.2.0 and clang++ 19.1.7 (clang++ with -stdlib=libc++), -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries -std=c++23 and no -DNDEBUG; RapidJSON built without RAPIDJSON_SSE2/SSE42. The C yyjson rows link Debian's libyyjson-dev shared library and were measured in the 2026-07-19 run. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Adoption** | 2.9k stars (suite repo) |
| **Last commit** | 2026-07-19 |
| **Links** | [repository](https://github.com/kostya/benchmarks) · [benchmark](https://raw.githubusercontent.com/kostya/benchmarks/master/README.md) |

## Verdict

In kostya/benchmarks' Json test (README update 2026-07-19, Intel Xeon E-2324G, Debian forky Docker image, medians), Rust 1.97.1 with serde_json 1.0.150 took 0.103 s with a custom visitor and 0.110 s collecting Vec&lt;Coordinate&gt;, against 0.131 s for C yyjson (gcc 16.1.0, Debian's shared library) and 0.127 s for C++ gason (g++ -O3 -march=native -flto). That is about 1.27x over yyjson (derived from page data), but C++ simdjson On-Demand (0.060 s) and DAW JSON Link (0.085 s) were faster, and the Rust DOM path (0.557 s) was 4.3x slower.

## Use it when

- Rust code that deserializes large JSON documents with a known schema into structs, especially when only a few fields or aggregates are needed: a deserialize_with visitor folds a huge array without materialising it.
- Memory-constrained ingestion: on the 110 MB input the streaming visitor added 0.00 MiB of RSS, Vec&lt;Coordinate&gt; added 11.12 MiB and serde_json::Value added 839.75 MiB.
- Extract-a-few-fields workloads where a typed deserializer replaces a general DOM parser such as yyjson, gason or RapidJSON's Document.
- Data whose floats tolerate an error of 1-2 ULP, or builds that enable serde_json's float_roundtrip feature and accept its cost (not measured in this suite).

## Skip it when

- As evidence that Rust beats C or C++: in the same table C++ simdjson On-Demand takes 0.060 s and DAW JSON Link (typed, streaming, like serde) 0.085 s with clang++ and 0.089 s with g++; simdjson DOM ties at 0.103 s.
- Schemaless or dynamic JSON: the Rust DOM row (serde_json::Value) takes 0.557 s and adds 839.75 MiB, about 4.3x slower than C yyjson (derived from page data).
- When correctly rounded doubles are required and float_roundtrip is not enabled: the measured build uses best-effort float parsing.
- Inside a C++ program: the gain comes from typed or on-demand parsing, which simdjson On-Demand and DAW JSON Link already provide in C++.

## How it is fast

Schema-driven deserialization: serde_derive generates a field matcher for x, y and z, serde_json reads directly from the borrowed &str, and the unknown name and opts fields are skipped as IgnoredAny without allocating, so no DOM is built (peak RSS increase 0.00 MiB versus 229.38 MiB for yyjson). Two harness details also favour the Rust rows. serde_json 1.0.150 is built without its float_roundtrip feature, so floats go through the best-effort f64_from_parts path (significand cast to f64, then one multiply or divide by a power-of-ten table entry), which serde_json's Cargo.toml says is about 2x cheaper than the exact path. And the UTF-8 check of the input happens in fs::read_to_string before the timer starts, after which serde_json's StrRead trusts the string (from_utf8_unchecked), while yyjson validates UTF-8 inside its timed parse.

## Compared with alternatives

This is the only JSON-parsing row in the category, and weaker evidence than the LangArena Rust slice::sort row: there the algorithms match, while here the Rust win comes from typed streaming against DOM parsers and from best-effort float parsing. A C++ project that wants the same effect should look at simdjson On-Demand or DAW JSON Link rather than a language change.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | serde 1.0.228 (derive feature) and serde_json 1.0.150 as pinned in json/json.rs/Cargo.lock; serde_json pulls in itoa, memchr and zmij |
| **Minimum toolchain** | serde_json 1.0.150 declares rust-version 1.71 and serde 1.0.228 declares 1.56 (crates.io); the benchmark crate uses edition 2024 and was built with Rust 1.97.1 |
| **Platforms** | Portable Rust; measured on x86-64 (Intel Xeon E-2324G) with -C target-cpu=native, LTO, codegen-units 1 and panic=abort |
| **Thread safety** | Not documented in the sources read; the benchmark parses on one thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry in float parsing: json.rs/Cargo.toml does not enable serde_json's float_roundtrip feature, so 1.0.150 uses its best-effort f64_from_parts (src/de.rs). A Python emulation of that function on numbers drawn the way json/generate_json.rb draws them (200,000 samples per field, shortest round-trip formatting) gave results 1-2 ULP away from correct rounding for about 35% of x values (around 1e-30), 10.5% of y and 10.4% of z; this is an emulation, not a run of the benchmark binary. yyjson ('can accurately read ... double numbers') and simdjson ('lossless parsing') claim exact parsing, the README's list of number-parsing inaccuracies (DAW JSON Link, gason, default RapidJSON, D) omits serde_json, and the self-test values 2.0, 0.5 and 0.25 are exact, so the check cannot catch it. For scale, RapidJSON's exact mode costs 0.212 s against 0.154 s for its default mode with g++.
- UTF-8 validation of the 110 MB input is outside the Rust timed region (fs::read_to_string runs before notify), while yyjson and simdjson ('Full JSON and UTF-8 validation') validate inside theirs. The cost was not measured; at the 13 GB/s simdjson quotes for its own validator the pass would take roughly 8 ms, about 8% of the 0.103 s row (derived; a lower-bound estimate, since std::str::from_utf8 is not that SIMD validator).
- The C++ streaming-callback row is handicapped by its harness: test_rapid_sax.cpp feeds RapidJSON's Reader through IStreamWrapper over a std::stringstream with the wrapper's default 4-byte buffer, so it calls std::istream::read every 4 bytes and runs 0.366 s, 2.4x slower than the RapidJSON DOM row that parses a std::string (0.154 s). No RapidJSON row defines RAPIDJSON_SSE2 or RAPIDJSON_SSE42, so its SIMD whitespace skipping is off. Do not read that row as the cost of streaming in C++.
- The C yyjson rows link Debian's prebuilt libyyjson-dev instead of a build with the suite's -O3 -march=native -flto (verifier finding). Times are wall clock from xtime.rb, one median per configuration, with memory sampled every 10 ms.

## Known shortcomings

- A typed streaming deserializer against DOM parsers: simdjson On-Demand (0.060 s) and DAW JSON Link (0.085 s) beat it, and the Rust DOM path (Serde Untyped, 0.557 s) is 4.3x slower than yyjson; yyjson is linked from Debian libyyjson-dev rather than built with the suite flags.
- The JSON3.jl enricher found that kostya/benchmarks' 2026-07-19 update re-measured only the Primes table and the environment table: the Json table rows kept their 2025-08-17 values (gcc 14.2.0, clang 19.1.7), so the compiler versions recorded here (gcc 16.1.0, clang 22.1.8) describe the current environment table and may not be the toolchain behind this table's rows; whether this table was re-run on 2026-07-19 was not checked.
- Harness asymmetry in float parsing: json.rs/Cargo.toml leaves serde_json's float_roundtrip feature off, so 1.0.150 uses its best-effort f64_from_parts; a Python emulation of that function on numbers drawn like generate_json.rb's gave results 1-2 ULP from correct rounding for about 35% of x values and about 10.5% of y and z, while yyjson and simdjson parse exactly (the README's inaccuracy list omits serde). The UTF-8 check runs in read_to_string outside the Rust timer, while yyjson and simdjson validate inside theirs. The RapidJSON SAX row (0.366 s) is crippled by an IStreamWrapper over a stringstream with the default 4-byte buffer and no RAPIDJSON_SSE2 or SSE42 define.
- Verifier batch-64 (wave 4): the Serde Custom versus C yyjson 1.27x compares two runs (yyjson rows first appeared 2026-07-19, Serde rows date from 2025-08-17), and the recorded toolchain was the README's later Versions table; claim rebuilt on same-run RapidJSON rows.

## Caveats and trade-offs

This compares libraries and algorithms, not languages. Rust (Serde Custom), in json/json.rs/src/json_pull.rs, is a serde-derived typed deserializer. Its visitor folds the x, y and z sums while streaming and skips the name and opts fields without building them (memory increase 0.00 MiB). Rust (Serde Typed), in json_struct.rs, collects a Vec&lt;Coordinate&gt; (+11.12 MiB). The C and C++ baselines named in the record are DOM parsers that materialise the whole document: yyjson +229.38 MiB, gason +96.75 MiB, RapidJSON +123.44 MiB. C++ schema-driven or on-demand parsers doing comparable work are faster (simdjson On-Demand 0.060 s, DAW JSON Link 0.085 s), and Rust doing DOM work (Serde Untyped) takes 0.557 s. The C yyjson rows use the distro-built shared library rather than a build with the suite's -O3 -march=native -flto. The README notes number-parsing inaccuracies in gason, default RapidJSON and DAW JSON Link, and that gason mutates its input and simdjson needs padded input. The input is 524,288 generated coordinate objects (json/generate_json.rb). File reading is outside the timed region on both sides. [retier] [verifier batch-64, wave 4] The earlier toolchain (Rust 1.97.1, serde_json 1.0.150, gcc 16.1.0, clang 22.1.8) is the README's current Versions table, not what measured the Json rows; the yyjson rows come from a later run than the Serde rows. The C++ baselines keep asserts enabled (no -DNDEBUG) and RapidJSON runs without its SSE paths.

Typed deserialization requires a schema (Serde Typed) or custom visitor; Serde Untyped is 0.557 s.

## Maintenance

Active MIT-licensed suite (2.9k stars, last commit 2026-07-19); serde and serde_json are MIT OR Apache-2.0 and actively released (serde_json 1.0.154 on 2026-10-11), but this row is a library-level data point whose margin over yyjson rests partly on best-effort float parsing and untimed UTF-8 validation, harness flaws found in this enrichment.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The harness is A-grade: json/json.rs/src/json_pull.rs and json_struct.rs against json/test_yyjson.c and test_gason.cpp, flags in common/commands.mk and json/Makefile, gcc 16.1.0, clang 22.1.8, Rust 1.97.1 and a Xeon E-2324G. But it compares a streaming typed deserializer with DOM parsers (same_algorithm false), the C yyjson baseline is a distro-built shared library, and C++ parsers doing comparable work beat Rust. Capped at C (unequal-work precedent).
- **Verifier notes:** The numbers match the README Json table row for row. Metadata checks out: MIT, 2.9k stars, last commit 2026-07-19. same_opt_level is corrected to false because yyjson is linked from Debian's prebuilt libyyjson-dev, while the gason, RapidJSON and simdjson rows are built with the suite flags. Shortcoming: the win is a typed streaming deserializer against DOM parsers. C++ simdjson On-Demand (0.060 s) and DAW JSON Link (0.085 s) beat it, and Rust's own DOM row (0.557 s) is 4.3x slower than yyjson, so this is not a Rust language advantage.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** verifier batch-29 (wave 14); enricher (wave 14 pass, 2026-10-12); verifier batch-64 (wave 4 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits/master>
  - <https://github.com/kostya/benchmarks/tree/master/json>
  - <https://github.com/kostya/benchmarks/tree/master/json/json.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_yyjson.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_gason.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/generate_json.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_pull.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_struct.rs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://github.com/kostya/benchmarks/commits/master>
  - <https://github.com/kostya/benchmarks/issues?q=is%3Aissue+json+serde>
  - <https://github.com/kostya/benchmarks/issues?q=json>
  - <https://github.com/kostya/benchmarks/pull/509>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/generate_json.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/Cargo.lock>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_pull.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_struct.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/json.rs/src/json_value.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_yyjson.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_gason.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_rapid.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_rapid_sax.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_dawjsonlink.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_simdjson.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_simdjson_dom.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_boost_json.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/json/test_yajl.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/rust/src/lib.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/libnotify/libnotify.h>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/xtime.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/docker/Dockerfile>
  - <https://raw.githubusercontent.com/serde-rs/json/master/Cargo.toml>
  - <https://raw.githubusercontent.com/serde-rs/json/master/src/read.rs>
  - <https://raw.githubusercontent.com/serde-rs/json/v1.0.150/src/de.rs>
  - <https://raw.githubusercontent.com/Tencent/rapidjson/master/include/rapidjson/istreamwrapper.h>
  - <https://raw.githubusercontent.com/ibireme/yyjson/master/README.md>
  - <https://crates.io/api/v1/crates/serde_json>
  - <https://crates.io/api/v1/crates/serde>
  - <https://raw.githubusercontent.com/simdjson/simdjson/master/README.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/kostya/benchmarks#json`) · [data/wave14/enrich/raw/lang_rust_kostya_benchmarks_json.json](../../../data/wave14/enrich/raw/lang_rust_kostya_benchmarks_json.json) (enrichment confidence 0.75)

</details>
