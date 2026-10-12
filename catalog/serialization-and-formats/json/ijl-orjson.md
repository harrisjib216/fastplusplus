# orjson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MPL-2.0 AND (Apache-2.0 OR MIT)` · 🟢 active

> CPython JSON extension in Rust (yyjson-backed parser) that serializes \~11-14x and parses \~2-6x faster than stdlib json.

| | |
|---|---|
| **Beats** | Python json (stdlib) |
| **Claimed result** | Median latency vs. stdlib json: twitter.json serialize 0.1ms vs 1.3ms (11.1x), deserialize 0.5ms vs 2.2ms (4.2x); github.json serialize 0.01ms vs 0.13ms (13.6x), deserialize 0.04ms vs 0.1ms (2.2x); citm_catalog.json serialize 0.3ms vs 3ms (11.8x), deserialize 1.3ms vs 4ms (3.1x); canada.json serialize 2.5ms vs 29.8ms (11.9x), deserialize 3ms vs 18ms (6x) |
| **Workload** | Serialize/deserialize twitter.json, github.json, citm_catalog.json, and canada.json using orjson vs. the CPython standard library `json` module, via the `pybench` reproduction script. |
| **Metric** | latency |
| **Hardware** | x86-64-v4 machine, Fedora 42 container (exact CPU model not named) |
| **Compiler and flags** | Measured with the prebuilt PyPI wheel orjson-3.10.11-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl under CPython 3.11.10. The Rust toolchain and flags used to build that wheel are not stated. The README's recommended build is `maturin build --release --strip`, which today needs Rust &gt;= 1.95, and the README notes that nightly Rust gives a significant performance benefit. |
| **Adoption** | 8.2k stars; widely used in the Python ecosystem (FastAPI, Django integrations, etc.) |
| **Last commit** | 2026-08-14 |
| **Links** | [repository](https://github.com/ijl/orjson) · [benchmark](https://github.com/ijl/orjson/blob/master/README.md#performance) |

## Verdict

orjson's README times orjson 3.10.11 (the PyPI manylinux wheel on CPython 3.11.10, in a Fedora 42 container on an unnamed x86-64-v4 CPU) against stdlib json. It uses pytest-benchmark medians with GC disabled and includes .encode('utf-8') in the json.dumps timing: serialization was 11.1-13.6x faster and deserialization 2.2-6x faster across twitter, github, citm_catalog and canada.json. These numbers predate the float-formatter change in 3.11.7 and the serializer rewrite in 3.12.0, so the current release has not been measured this way.

## Use it when

- CPython 3.10+ web and API services where json.dumps/json.loads take a measurable share of request time. On the twitter, github, citm_catalog and canada.json fixtures, README medians show dumps 11-14x faster and loads 2-6x faster.
- Serializing dataclasses, datetimes, UUIDs, enums or numpy arrays without writing a default= hook. The README reports dataclasses about 40x faster than json + asdict(), and float64/int32/bool numpy arrays 10-14x faster with roughly 3-4x lower peak RSS.
- Decoding many payloads that repeat the same short object keys (API records, structured logs). Keys of 64 bytes or less are served from a process-wide cache instead of being allocated each time.
- Trust boundaries that need strict RFC 8259 and UTF-8 checking. On 342 JSONTestSuite + nativejson-benchmark fixtures, orjson accepted 0 invalid documents; stdlib json accepted 17.
- Building responses from JSON that is already serialized (cache entries, JSONB columns), using orjson.Fragment instead of a loads/dumps round trip.

## Skip it when

- Code that relies on the rest of json's API: str output, indent other than 2, separators, ensure_ascii, cls=, object_hook/parse_float/parse_int (for example, Decimal), or file/NDJSON helpers. None of these are provided.
- Data that must round-trip integers wider than 64 bits, lone surrogates, or NaN/Infinity. dumps raises on the first two and silently writes NaN/Infinity as null; loads rejects the NaN/Infinity tokens that stdlib accepts.
- Runtimes other than CPython 3.10+ with the GIL. There is no support for PyPy, GraalPy or other implementations (build.rs refuses them), PEP 554 subinterpreters, or Android/iOS embedded builds. Free-threaded CPython is refused unless ORJSON_BUILD_FREETHREADED is set, and CI builds 3.15t but does not publish it. ppc64le/s390x wheels were dropped in 3.12.0.
- Very large or deeply nested documents. loads allocates about 12 bytes of yyjson DOM per input byte before it builds any Python objects, has no streaming mode, and stops at 1024 nesting levels. dumps raises past 254 nested containers, while stdlib is bounded only by Python's recursion limit.
- Non-Python consumers. orjson ships only as a Python module, with no Rust crate or C API, so Rust code would have to reach it through PyImport_\*.

## How it is fast

In loads, the input is checked as UTF-8 up front with simdutf8 (AVX2/NEON), and yyjson's reader then parses it into one pre-sized pool buffer (yyjson's own UTF-8 check is compiled out). A single walk of that DOM builds lists and dicts allocated at their final size, and object keys of 64 bytes or less come from a 2048-entry, direct-mapped cache keyed by xxh3-64, holding str objects whose hashes are already computed. In dumps, types are dispatched by exact type-pointer comparison, and on 64-bit builds CPython int/str internals are read directly. Output goes straight into a growing PyBytes buffer with no final copy. String escaping is scanned with SSE2 or with AVX-512VL masks detected at runtime, ints are formatted with itoap and floats with the zmij crate. Release builds use fat LTO, codegen-units=1 and PyMem_Malloc as the global allocator. The author says nightly Rust gives a significant speedup.

## Compared with alternatives

Pick orjson over ssrJSON (the other stdlib-json replacement here) when you need native dataclass/datetime/UUID serialization, `default`, Fragment, or wheels for x86-64-v1, 32-bit or armv7 targets. ssrJSON needs SSE4.2+ or aarch64 and a Clang build, but its README claims speed equal to or better than orjson on most cases, 1.4-10x faster numpy encoding, and a json-compatible, str-returning API. Pick orjson over jiter when you also need to serialize (jiter's Python package only parses). From C/C++, use yyjson directly: orjson's loads wraps yyjson's reader.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (numpy is optional and read through its array interface, not linked). For builds, Rust crates (pyo3-ffi, itoap, zmij, simdutf8, xxhash-rust, associative-cache, jiff-core, encoding_rs, bytecount, once_cell) plus vendored yyjson C. The PyPI sdist bundles all sources, so it can be built offline. |
| **Minimum toolchain** | CPython 3.10-3.15. Building from source needs Rust 1.95+, a C compiler and maturin&gt;=1,&lt;2. Nightly Rust is recommended for speed; CI pins nightly-2026-08-01 alongside stable 1.95. |
| **Platforms** | PyPI wheels for Linux x86_64/i686/aarch64/armv7, macOS x86_64/arm64 and Windows x86_64/i686/arm64. x86_64 wheels need only x86-64-v1 and switch to AVX-512VL paths at runtime (the AVX-512 paths are not built on macOS). aarch64 needs ARMv8-A. No ppc64le/s390x wheels since 3.12.0. |
| **Thread safety** | The GIL is held for the whole of each dumps/loads call, so calls from multiple threads are safe but never run in parallel. The module declares Py_mod_gil USED and does not support multiple interpreters. Integration tests cover multithreaded use and forked gunicorn workers. Free-threaded builds are not officially supported, and the key cache is disabled in them. |
| **Drop-in for the baseline** | partial — for plain use, loads(bytes\|str) behaves like json.loads, and JSONDecodeError subclasses json.JSONDecodeError. But dumps returns bytes, sort_keys and indent become the OPT_SORT_KEYS and OPT_INDENT_2 flags, and there is no object_hook, cls, separators or ensure_ascii. |

## Gotchas

- dumps serializes subclasses of str/int/dict/list/dataclass/enum natively and skips `default` for them. A redacting str subclass is written verbatim unless OPT_PASSTHROUGH_SUBCLASS is set (OPT_PASSTHROUGH_DATACLASS and OPT_PASSTHROUGH_DATETIME do the same for their types). A `default` that forgets to raise emits null.
- The loads key cache (keys of 64 bytes or less, 2048 entries, process-global) is indexed by an unseeded xxh3-64 hash. On a hash match it returns the cached str without comparing bytes (src/deserialize/pyobject.rs), so in principle two distinct keys that collide would decode to the same key.
- Output bytes change between releases: 3.11.7 changed float text (1.2e+30 instead of 1.2e30) and 3.12.0 rewrote serialization. The default key order is documented as unspecified. Pin the version if you have byte-exact golden tests.
- Pin &gt;=3.11.6. Two high-severity advisories covered unbounded recursion: CVE-2024-27454 / GHSA-pwr2-4v36-6qpr in loads, fixed in 3.9.15, and CVE-2025-67221 / GHSA-hx9q-6w63-j58v in dumps, fixed in 3.11.6.

## Caveats and trade-offs

The baseline is Python's stdlib json module, not RapidJSON, nlohmann, simdjson or serde_json, so baseline_in_list=false. The numbers are first-party (orjson's own README) and reproducible with the published pybench script, but the CPU is given only as x86-64-v4, with no model. The benchmark used orjson 3.10.11, while the current release is 3.12.0 (2026-08-14). The license is mixed OSI: much of src/ is MPL-2.0 (file-level copyleft) and the rest is Apache-2.0 OR MIT; GitHub reports only Apache-2.0. orjson ships only as a Python module, not a Rust crate.

Only usable from Python (Rust internals are not exposed as a Rust crate); does not serialize to str (bytes-only) or support object_hook/NDJSON; also independently verified against `nativejson-benchmark`'s conformance corpus (0 invalid-docs-accepted / 0 valid-docs-rejected vs 17/0 for stdlib json).

## Maintenance

Actively maintained by ijl (3.12.0 released 2026-08-14) and published as Production/Stable wheels, so usability is pip-install. GitHub issues and PRs are closed by policy, and the code is MPL-2.0 for parts of src/ with Apache-2.0 OR MIT for the rest.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables compare orjson with CPython's stdlib json, and every latency and ratio in the record matches them. The benchmark code is public (script/pybench runs bench/benchmark_dumps.py and benchmark_loads.py under pytest-benchmark), and Python 3.11.10 plus the exact PyPI wheel are stated. It is not A because no CPU model is given (only 'x86-64-v4') and the Rust toolchain that built the wheel is not stated.
- **Verifier notes:** All eight median-latency rows and ratios in claimed_speedup match the README verbatim. The latest commit on the default branch (master) is 2026-08-14. The record's 2026-09-14 is the repo pushed_at date, not a master commit. Stars are 8,234; not archived, not a fork.
- **Fields the verifier corrected:** `license`, `last_commit`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ijl/orjson/blob/master/README.md#performance>
  - <https://github.com/ijl/orjson>
  - <https://github.com/ijl/orjson/blob/master/script/pybench>
  - <https://github.com/ijl/orjson/blob/master/bench/benchmark_dumps.py>
- **Sources the enricher read:**
  - <https://github.com/ijl/orjson>
  - <https://github.com/ijl/orjson/blob/master/README.md#performance>
  - <https://github.com/ijl/orjson/blob/master/Cargo.toml>
  - <https://github.com/ijl/orjson/blob/master/build.rs>
  - <https://github.com/ijl/orjson/blob/master/pyproject.toml>
  - <https://github.com/ijl/orjson/blob/master/CHANGELOG.md>
  - <https://github.com/ijl/orjson/blob/master/src/lib.rs>
  - <https://github.com/ijl/orjson/blob/master/src/alloc.rs>
  - <https://github.com/ijl/orjson/blob/master/src/typeref.rs>
  - <https://github.com/ijl/orjson/blob/master/src/deserialize/backend/yyjson.rs>
  - <https://github.com/ijl/orjson/blob/master/src/deserialize/cache.rs>
  - <https://github.com/ijl/orjson/blob/master/src/deserialize/pyobject.rs>
  - <https://github.com/ijl/orjson/blob/master/src/deserialize/deserializer.rs>
  - <https://github.com/ijl/orjson/blob/master/src/deserialize/input.rs>
  - <https://github.com/ijl/orjson/blob/master/src/ffi/utf8.rs>
  - <https://github.com/ijl/orjson/blob/master/src/ffi/pystrref/avx512.rs>
  - <https://github.com/ijl/orjson/blob/master/src/ffi/pystrref/object.rs>
  - <https://github.com/ijl/orjson/blob/master/src/ffi/pyintref.rs>
  - <https://github.com/ijl/orjson/blob/master/src/ffi/iterator/pydict.rs>
  - <https://github.com/ijl/orjson/blob/master/src/serialize/mod.rs>
  - <https://github.com/ijl/orjson/blob/master/src/serialize/obtype.rs>
  - <https://github.com/ijl/orjson/blob/master/src/serialize/writer/byteswriter.rs>
  - <https://github.com/ijl/orjson/blob/master/src/serialize/writer/container.rs>
  - <https://github.com/ijl/orjson/blob/master/src/serialize/writer/num.rs>
  - <https://github.com/ijl/orjson/blob/master/src/serialize/writer/format_str.rs>
  - <https://github.com/ijl/orjson/blob/master/src/serialize/writer/str/mod.rs>
  - <https://github.com/ijl/orjson/blob/master/src/serialize/writer/str/avx512.rs>
  - <https://github.com/ijl/orjson/blob/master/src/serialize/writer/str/sse2.rs>
  - <https://github.com/ijl/orjson/blob/master/script/pybench>
  - <https://github.com/ijl/orjson/blob/master/bench/benchmark_dumps.py>
  - <https://github.com/ijl/orjson/blob/master/bench/benchmark_loads.py>
  - <https://github.com/ijl/orjson/blob/master/bench/data.py>
  - <https://github.com/ijl/orjson/blob/master/test/test_recursion.py>
  - <https://github.com/ijl/orjson/blob/master/.github/workflows/artifact.yaml>
  - <https://github.com/ijl/orjson/commits/master>
  - <https://github.com/advisories/GHSA-hx9q-6w63-j58v>
  - <https://github.com/advisories/GHSA-pwr2-4v36-6qpr>
  - <https://pypi.org/pypi/orjson/json>
  - <https://github.com/Antares0982/ssrJSON>
  - <https://github.com/pydantic/jiter>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter-python/README.md>
  - <https://github.com/pydantic/jiter/blob/main/crates/jiter-python/bench.py>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/ijl/orjson`) · [data/wave4/enrich/raw/github_com_ijl_orjson.json](../../../data/wave4/enrich/raw/github_com_ijl_orjson.json) (enrichment confidence 0.85)

</details>
