# jiter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust JSON parser from Pydantic: borrowed-string DOM, pull iterator and Python parser; \~2x serde_json::Value DOM throughput.

| | |
|---|---|
| **Beats** | serde_json |
| **Claimed result** | 209.4 MB/s vs serde_json 104.3 MB/s at 8 threads (\~2.01x); 91.9 MB/s vs serde_json 48.0 MB/s at 1 thread (\~1.91x) (derived from page data) |
| **Workload** | Parsing 5 real SEC company-facts JSON files (39.9 MB total, 285,469 fact records) into a DOM (jiter 0.4.2 JsonValue vs serde_json 1.0.151 serde_json::Value) and reducing to fact rows with a shared reducer, at 1/2/4/8 threads (one file per work item), 20 timed passes after 2 warmups, in the third-party tegridy-benchie shootout |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i7-6820HQ CPU @ 2.70GHz (8 cores) |
| **Compiler and flags** | rustc (version not stated) via cargo build --release; release profile opt-level=3, lto=true, codegen-units=1 (rust/Cargo.toml) |
| **Adoption** | 551 stars; used inside Pydantic / pydantic-core |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/pydantic/jiter) · [benchmark](https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md) |

## Verdict

On the third-party tegridy-benchie harness (Linux on an Intel i7-6820HQ, 4C/8T; cargo release build with opt-level 3, LTO and codegen-units 1; rustc version not stated), jiter 0.4.2 JsonValue parsed and reduced 5 SEC company-facts files (39.9 MB) at 91.9 MB/s single-threaded, against 48.0 MB/s for serde_json 1.0.151 into serde_json::Value (\~1.9x). At 8 threads it was 209.4 vs 104.3 MB/s (\~2.0x), but work is split per file, so at most 5 run in parallel. jiter's own README table (3-7x on number shapes, 0.7x on pass2) states no CPU, reuses a JsonValueScratch across iterations, and builds its serde_json baseline with float_roundtrip, a feature serde_json documents as roughly halving float parsing speed, plus arbitrary_precision.

## Use it when

- Rust code that parses JSON into a generic tree (unknown or loose schema) and today uses serde_json::Value. On 40 MB of SEC company-facts files on x86, jiter's DOM measured \~1.9-2.0x serde_json::Value throughput with lower peak RSS (95 vs 116 MB at 1 thread).
- Number-heavy documents such as large float or int arrays, where jiter's own criterion table shows its biggest margins over serde_json::Value (3.4-6.8x). See verified_claims_summary for how that baseline was built.
- Hot paths with a known schema, where you can drive the Jiter pull API and skip unwanted subtrees with next_skip instead of building any tree. The README's iterator column beats its value column on array and number shapes.
- Truncated or streaming JSON, such as LLM token streams: PartialMode (Rust) or partial_mode='trailing-strings' (Python) returns what has arrived so far.
- Python code that parses JSON without going through pydantic and wants string caching, Decimal/LosslessFloat floats or duplicate-key detection (catch_duplicate_keys).

## Skip it when

- Deserializing into #[derive(Deserialize)] structs. Every measured win is against serde_json::Value, which the README itself says is much slower than typed serde. The new jiter::serde Deserializer has no published comparison with serde_json::from_slice::&lt;T&gt;.
- Anything that writes JSON. jiter parses only: there is no serializer and JsonValue has no Serialize impl.
- Key-lookup-heavy access to large objects. JsonObject is Arc&lt;Vec&lt;(key, value)&gt;&gt; with no key index and no duplicate-key removal, so a lookup by key is a linear scan you write yourself.
- Very deep nesting: JsonValue parsing has a fixed depth limit of 200. Only the serde Deserializer lets you raise or disable it.
- C or C++ codebases: jiter is a Rust crate with Python bindings, and the repo has no C API.

## How it is fast

The string scanner tests 16 bytes at a time (SSE2 on x86_64, NEON on aarch64) for quote, backslash, control or non-ASCII bytes. Strings without escapes come back as slices of the input rather than copies; escaped ones are decoded onto a reusable tape. Integers are decoded 16 digits per vector with a multiply-add horizontal reduction, and floats go through lexical-parse-float. Since v0.17, containers are built on two shared stacks (like RapidJSON's parse stack) and copied into an exactly-sized allocation when they close. That cut reallocations 49% on the project's corpus, and JsonValueScratch keeps those buffers between documents. Objects are plain Vec&lt;(key, value)&gt; with no hashing, whereas serde_json's default Map is a BTreeMap&lt;String, Value&gt;. The benchmarked v0.4.2 had SIMD on aarch64 only, so the x86 result came from the scalar paths.

## Compared with alternatives

Against simd-json, the only Rust sibling, pick jiter when you want a DOM parsed from an immutable &[u8] with borrowed strings, Python interop, or partial-JSON parsing. On the same tegridy harness jiter 0.4.2 did 91.9 MB/s single-threaded vs 50.6 MB/s for simd-json 0.13, but that harness used simd-json's OwnedValue on a copied buffer, not its fastest path. go-json and jsoniter post similar \~2x-over-baseline numbers on the same harness, but they are Go libraries, and the C++ siblings (Jsonifier, zzzJSON, LJSON) cannot be used from Rust.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | num-traits, ahash, smallvec, lexical-parse-float, bitvec; num-bigint (default feature); optional serde (serde feature) and pyo3 (python feature) |
| **Minimum toolchain** | Rust 1.88 (edition 2024; the MSRV follows pydantic-core) |
| **Platforms** | Any Rust target. SIMD string and integer paths exist for x86_64 (SSE2 only, chosen at compile time, no AVX2 path) and aarch64 (NEON; SIMD integer decoding on little-endian only). Other targets, including wasm32, use a scalar fallback. |
| **Thread safety** | Not documented for the Rust API. Jiter and JsonValueScratch methods take &mut self, so use one per thread; parsed arrays and objects are Arc-wrapped. The Python string cache is a mutex-guarded pool (up to 8 caches on free-threaded builds). |
| **Drop-in for the baseline** | partial — JsonValue is not serde_json::Value: it uses Cow strings, Arc&lt;Vec&gt; containers, no key index, i64 or BigInt integers, and has no Serialize or to_string. The optional 'serde' feature (v0.16+) gives serde_json-like from_slice/from_str for Deserialize types, but there is no from_reader and no serializer. |

## Gotchas

- Jiter::next_str and next_key return &str borrowed from the Jiter, because escaped strings are decoded into its internal tape. Copy the value before the next call. next_skip does not check that skipped strings are valid UTF-8.
- The README example passes allow_inf_nan=true to JsonValue::parse, and Python's from_json defaults to allow_inf_nan=True. Pass false if you need NaN and Infinity rejected as strict JSON requires.
- JsonValue has only Int(i64) and BigInt. With the default num-bigint feature, integers outside i64, including u64 values above i64::MAX, become heap-allocated BigInt values.
- The 0.x API breaks between minor versions: v0.9 replaced the map-like LazyIndexMap objects with Arc&lt;Vec&lt;...&gt;&gt;, so code like the benchmark harness's obj.get('facts') no longer compiles. Partial mode has open bugs: in #267, next_str on a truncated string leaves current_index past the end of the input, and slice_to_current then panics.

## Known shortcomings

- The benchmarked version (0.4.2) had no x86 SIMD, and jiter's own README table compares against serde_json built with float_roundtrip and arbitrary_precision (which the serde_json docs say costs \~2x on floats), so its 3-7x overstates the gap. Since v0.9 object key lookup is a linear scan.

## Caveats and trade-offs

The rustc version is not stated, which keeps the tegridy-benchie result out of Tier A. That harness is also little known: 0 stars, one commit, created 2026-09-23. It tested jiter 0.4.2 (from Cargo.lock), which is far behind the current v0.17.0. The comparison is DOM against DOM (serde_json::Value); jiter's own README warns that Value is much slower than typed serde deserialization. jiter's README also has a first-party criterion table: up to 6.8x vs serde_json::Value (long_significand_floats), but serde is faster on pass2 (0.7x). That table has no CPU model or compiler, so on its own it is Tier C. The corpus has only 5 files and work is split per file, so the 8-thread runs are limited to 5-way parallelism. The i7-6820HQ is 4 cores / 8 threads.

The low-level Jiter iterator API requires knowing the schema ahead of time to get its full speed; the JsonValue DOM path is the one benchmarked here; also ships a PythonParse mode aimed specifically at CPython interop

## Maintenance

Actively developed by the Pydantic team (v0.17.0 released 2026-09-12, commits through 2026-09-23) and the parser inside pydantic-core; MIT-licensed on crates.io, but still 0.x with breaking API changes between minor versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** RESULTS.md (Native — Rust table) shows jiter at 209.4 / 91.9 MB/s against serde_json at 104.3 / 48.0 MB/s (8t / 1t). The harness is public (rust/jiter.rs, rust/serde.rs, rust/runner.rs, rust/reduce.rs), the flags are stated (Cargo.toml release profile: opt-level=3, lto=true, codegen-units=1) and so is the CPU (i7-6820HQ). The rustc version is not stated anywhere (README.benchmark.md only says 'rustc/cargo'), so this is not A; earlier batches treated a missing rustc version the same way (lute, chumsky). The harness is also not a well-known suite (0 stars, created 2026-09-23), so it is not B. The tier is C.
- **Verifier notes:** The numbers match RESULTS.md exactly, and the derived ratios (\~2.01x at 8t, \~1.91x at 1t) are correct. I downgraded A to C only because the rustc version is not stated anywhere, following the lute/chumsky precedent. If the orchestrator accepts an unversioned rustc when the Cargo profile and CPU are stated, this would be A. last_commit was corrected to 2026-09-23, the newest commit on main; 2026-09-25 is only pushed_at. Otherwise the metadata checks out: MIT, 551 stars, not a fork, not archived, active.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pydantic/jiter>
  - <https://github.com/pydantic/jiter/blob/main/README.md>
  - <https://github.com/pydantic/jiter/releases>
  - <https://github.com/pydantic/jiter/commits/main>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md>
  - <https://github.com/mihailnica10/tegridy-benchie>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/README.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/README.benchmark.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/Makefile>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/results.json>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/variants.ts>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/run-bench.ts>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/Cargo.toml>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/Cargo.lock>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/jiter.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/serde.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/runner.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/reduce.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/bench_jiter.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/bench_serde.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/lib.rs>
- **Sources the enricher read:**
  - <https://github.com/pydantic/jiter>
  - <https://github.com/pydantic/jiter/blob/main/README.md>
  - <https://github.com/pydantic/jiter/blob/main/Cargo.toml>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/Cargo.toml>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/build.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/lib.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/simd/mod.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/simd/x86_64.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/simd/aarch64.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/value.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/serde.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/jiter.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/errors.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/number_decoder.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/parse.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/string_decoder.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/src/py_string_cache.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/benches/README.md>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter/benches/main.rs>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter-python/README.md>
  - <https://github.com/pydantic/jiter/releases>
  - <https://github.com/pydantic/jiter/commits/main>
  - <https://github.com/pydantic/jiter/commits/main/crates/jiter/src/serde.rs>
  - <https://github.com/pydantic/jiter/commits/main/crates/jiter/src/simd/x86_64.rs>
  - <https://github.com/pydantic/jiter/commits/main/crates/jiter/src/lazy_index_map.rs>
  - <https://github.com/pydantic/jiter/tree/v0.4.2>
  - <https://github.com/pydantic/jiter/blob/v0.4.2/crates/jiter/Cargo.toml>
  - <https://github.com/pydantic/jiter/blob/v0.4.2/crates/jiter/src/lib.rs>
  - <https://github.com/pydantic/jiter/blob/v0.4.2/crates/jiter/src/value.rs>
  - <https://github.com/pydantic/jiter/pull/184>
  - <https://github.com/pydantic/jiter/pull/269>
  - <https://github.com/pydantic/jiter/pull/279>
  - <https://github.com/pydantic/jiter/issues>
  - <https://github.com/pydantic/jiter/issues/267>
  - <https://github.com/pydantic/jiter/issues/120>
  - <https://github.com/pydantic/jiter/issues/249>
  - <https://github.com/pydantic/jiter/issues/261>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/jiter.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/serde.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/simdjson.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/runner.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/Cargo.toml>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/Cargo.lock>
  - <https://github.com/serde-rs/json/blob/master/src/map.rs>
  - <https://github.com/serde-rs/json/blob/master/Cargo.toml>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/pydantic/jiter`) · [data/wave4/enrich/raw/github_com_pydantic_jiter.json](../../../data/wave4/enrich/raw/github_com_pydantic_jiter.json) (enrichment confidence 0.85)

</details>
