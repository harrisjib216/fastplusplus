# ssrJSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> SIMD C extension replacing CPython's json.dumps/loads; README claims 4-31x faster dumps and 2-8x faster loads.

| | |
|---|---|
| **Beats** | Python json (stdlib) |
| **Claimed result** | README text: 'ssrjson.dumps() is about 4x-31x as fast as json.dumps()' and 'ssrjson.loads() is about 2x-8x as fast as json.loads()' for both str and bytes input (Python3.14, x86-64, AVX2). TL;DR: 'faster than or nearly as fast as orjson ... on most benchmark cases'. The page's v0.0.17 charts label these ratios vs json. dumps to str: canada 23.07x, mesh 17.79x, github 9.63x, twitter 7.52x, simple_object_zh 4.93x. loads str: canada 7.75x, mesh 4.49x, github 3.40x, simple_object_zh 2.58x, twitter 2.54x. dumps_to_bytes: canada 26.27x. orjson on the same charts: twitter loads str 1.80x, canada dumps to str 16.67x. |
| **Workload** | dumps / dumps_to_bytes / loads (str and bytes input) on twitter.json, github.json, canada.json, mesh.json and simple_object_zh.json (README charts, v0.0.17). Measured with the companion ssrjson-benchmark package (src/ssrjson_benchmark/benchmark.py): the stdlib json baseline uses separators=(',', ':'), libraries are interleaved across rounds, and the process is pinned to one core. Python 3.14, x86-64 AVX2, compared against json, ujson, pydantic_core, msgspec and orjson. |
| **Metric** | throughput |
| **Hardware** | Not stated for the README's v0.0.17 dumps/loads charts, which say only 'x86-64, AVX2'. The float-formatting micro-benchmark names Apple M1 and AMD R7-7840H. The linked ssrJSON-benchmark repo publishes per-CPU PDF reports (e.g. i7-13700K AVX2 for 0.0.21 with Python 3.14.6 built by GCC 15.3.0; also i7-11370H, Ryzen 9 9900X, Apple M1/M4, Raspberry Pi 5), but none for 0.0.17. |
| **Compiler and flags** | Clang is required: CMakeLists.txt aborts unless CMAKE_C_COMPILER_ID is Clang, and Windows uses clang-cl. CMake defaults to Release (-fomit-frame-pointer, -fno-stack-protector; LTO/PGO optional). PyPI wheels are built by a Nix flake in .github/workflows/release.yml. The Clang version is not stated anywhere, and the benchmark reports record only the CPython build compiler. |
| **Adoption** | 39 stars; beta stage, PyPI package `ssrjson` |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/Antares0982/ssrJSON) · [benchmark](https://github.com/Antares0982/ssrJSON/blob/main/README.md#how-fast-is-ssrjson) |

## Verdict

These are first-party ssrjson-benchmark charts for v0.0.17 on Python 3.14 and an unnamed x86-64 AVX2 CPU; the Clang version and build flags for the measured ssrJSON are not stated, and the harness pins one core and interleaves libraries against stdlib json with compact separators. They show dumps-to-str 4.9x (simple_object_zh) to 23.1x (canada) and loads(str) 2.5x (twitter) to 7.8x (canada) faster than json, which the README rounds to 4-31x and 2-8x, with orjson at 1.80x (twitter loads str) and 16.67x (canada dumps str) on the same charts.

## Use it when

- CPython 3.10-3.14 services on x86-64-v2+ or aarch64 where json.dumps/json.loads of plain dict/list/str/int/float/bool/None data shows up in profiles, and the code calls them with default options.
- Encode-heavy workloads producing str: the v0.0.17 charts show dumps-to-str 7.5x (twitter.json) to 23x (canada.json) faster than json, and 1.2-2.0x ahead of orjson on the same charts.
- Emitting UTF-8 bytes of non-ASCII text such as CJK strings: dumps_to_bytes on simple_object_zh.json is charted at 6.55x json vs 1.46x for orjson when the str objects have no UTF-8 cache (a fast-path probe, not real-world data).
- Float/number-heavy documents and NumPy arrays: canada.json loads is 7.75x json vs orjson 4.28x on the charts, and the README's NumPy microbenchmark shows ndarray dumps_to_bytes 1.4-10x faster than orjson.
- Parsing JSON that is already a Python str: loads(str) skips UTF-8 transcoding (twitter.json 2.54x json vs orjson 1.80x).

## Skip it when

- Code that relies on json options: sort_keys, default=, cls, separators, ensure_ascii=True, parse_float/parse_int and object_pairs_hook are ignored, and indent accepts only 2 or 4. Output ordering and escaping will differ from json.
- Data outside the JSON core types: dict keys that are not str raise JSONEncodeError (json turns int keys into strings); datetime, dataclass, UUID, Decimal and similar objects raise 'Unsupported type to encode' with no default hook; ints outside the int64/uint64 range fail in dumps and silently become float in loads.
- 32-bit targets, x86-64-v1 CPUs without SSE4.2, big-endian machines, PyPy or other non-CPython runtimes. musl Linux, glibc older than 2.34, Intel macOS and Python 3.15 get no wheel, so they must build from source with Clang and CMake 3.30+.
- Risk-averse production: the project is beta (0.0.x, PyPI 'Development Status :: 4 - Beta'), has 39 stars, and 2026 releases fixed several memory-safety bugs (a NEON encoder heap overflow in 0.0.19 that 'all prior versions' should upgrade past, 1-byte heap overflows in 0.0.20/0.0.21, invalid reads in 0.0.23), although fuzzing and ASAN run in CI.
- Free-threaded CPython with containers shared across threads: support is experimental. The encoder locks dicts/lists outer-to-inner and can deadlock against other lock orders, and the optional lock-free build crashes on concurrent mutation.

## How it is fast

Strings are processed directly in CPython's internal PEP 393 layout (ASCII/UCS1/UCS2/UCS4) by hand-written SIMD kernels for escape scanning, copying and width conversion. On x86-64 it compiles three copies of the core (SSE4.2, AVX2, AVX-512) and picks one at runtime; aarch64 uses NEON. dumps_to_bytes has its own SIMD UTF-8 encoder instead of CPython's cached PyUnicode_AsUTF8, and bytes input to loads is validated and transcoded with simdutf-style vector shapes plus Lemire's lookup4 UTF-8 validation, widening the output buffer in place. Floats are printed with xjb64/xjb32 shortest-round-trip formatting; integer printing, number parsing and the core parser come from yyjson; and object keys of 64 bytes or less are reused from a 512-slot xxHash64-indexed cache (orjson's short-key cache idea) to avoid allocating str objects.

## Compared with alternatives

Pick it over orjson, the other catalogued stdlib-json replacement, when you want json-style call signatures and str output, encode a lot of non-ASCII text or numeric/NumPy data, or want control over the UTF-8 cache: the same first-party charts put it 1.2-2.0x ahead of orjson on dumps-to-str and 1.1-1.8x on loads. Stay with orjson if you need default=, OPT_SORT_KEYS/OPT_NON_STR_KEYS, native datetime/dataclass/UUID serialization, x86-64-v1/32-bit/musl wheels or a more mature project; simdjson and yyjson are C/C++ parsers rather than Python modules, and ssrJSON reuses yyjson's parser and number code.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime beyond CPython (NumPy optional, enabled explicitly via setup_numpy_types). Source build needs Clang (clang-cl on Windows), CMake &gt;= 3.30 and C17/C++20; yyjson-derived code, xjb, xxHash and khash are vendored. |
| **Minimum toolchain** | CPython 3.10+ (PyPI wheels for 3.10-3.14 and 3.14t; 3.15 is source-only). Source builds require Clang (minimum version not documented); GCC and plain MSVC are rejected by CMake. |
| **Platforms** | x86-64-v2+ (SSE4.2 minimum; runtime dispatch to SSE4.2/AVX2/AVX-512) and aarch64 (NEON), 64-bit little-endian only. Wheels: manylinux_2_34 x86-64/aarch64, macOS arm64, Windows amd64. |
| **Thread safety** | GIL builds: safe to call from any thread; the global decode buffers and key cache rely on the GIL. Free-threaded 3.14t builds: experimental, with per-thread buffers and key cache and lock-based encoding (deadlock possible under conflicting lock orders); decoding is lock-free. Settings such as write_utf8_cache and strict_argparse are process-global. |
| **Drop-in for the baseline** | partial — `import ssrjson as json` works for dumps/loads with default arguments, but output is compact and unescaped (like separators=(',',':'), ensure_ascii=False), most kwargs are ignored, non-str keys and ints wider than 64 bits are rejected or converted to float, and there is no dump/load, JSONEncoder or JSONDecoder. |

## Gotchas

- Unsupported kwargs are ignored, not rejected: dumps(obj, sort_keys=True) returns unsorted output and prints only a one-time stderr warning ('some options are not supported'). Call ssrjson.strict_argparse(True) to turn these into errors.
- dumps_to_bytes writes CPython's per-str UTF-8 cache by default, so each non-ASCII str encoded keeps an extra UTF-8 copy alive until the str is freed. For one-shot encodes, disable it with ssrjson.write_utf8_cache(False) or is_write_cache=False. dumps_to_bytes also rejects lone surrogates (U+D800-DFFF), which dumps passes through.
- loads turns out-of-range integers into float without an error, accepts NaN/Infinity in any letter case (but not 'inf'), and stops at 1024 levels of nesting (encode as well). object_hook/array_hook re-entrancy is capped at 32 nested decoder levels.
- Memory footprint: each decoding context carries about 1 MB of scratch (two 512 KB string buffers), and the key cache holds references to up to 512 short key str objects between calls. Free-threaded builds allocate this per thread.

## Caveats and trade-offs

A 39-star beta project whose numbers are all first-party: the benchmark repo Nambers/ssrJSON-benchmark (0 stars) is maintained by an ssrJSON contributor. Per-case figures appear only as labels inside the SVG charts. Neither the CPU behind the README charts nor the Clang version is stated. The baseline is CPython's stdlib json, which is not a named baseline for this category (baseline_in_list=false). Both ssrJSON and orjson use a global short-key cache in loads, which the benchmark README warns may not reflect production. dumps_to_bytes results depend on the UTF-8 cache setting. Requires x86-64-v2 (SSE4.2) or aarch64, and CPython only.

Beta-quality, several standard json-module features not yet implemented; requires Clang specifically to build; only supports x86-64-v2+ (SSE4.2 minimum) and aarch64, no 32-bit or older-CPU fallback; enabling its UTF-8 str cache trades memory for speed on repeated encodes.

## Maintenance

Actively maintained: 0.0.23 was released to PyPI on 2026-09-17, the same day as the last commit, and CI runs fuzzing and ASAN. It is still a beta 0.0.x project (39 stars, mostly one author with 230 of 246 commits), MIT-licensed and easiest to consume as PyPI wheels, since vendoring or source builds require Clang.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README compares ssrJSON directly with stdlib json, both as text ranges and as ratio labels in the v0.0.17 charts, and links public benchmark code (Nambers/ssrJSON-benchmark, src/ssrjson_benchmark/benchmark.py). The README charts name no CPU, though. No Clang version or build flags are stated for the measured build; the per-CPU PDF reports cover other versions and record only the CPython build compiler. First-party with partial methodology, so C.
- **Verifier notes:** The claims match the README text; I extracted the chart ratios from the SVG text labels. Metadata checks out: MIT, 39 stars, last commit 2026-09-17, not a fork. The per-CPU PDF reports in Nambers/ssrJSON-benchmark still omit the ssrJSON compiler version, so they do not lift the tier.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Antares0982/ssrJSON>
  - <https://github.com/Antares0982/ssrJSON/commits/main>
  - <https://github.com/Antares0982/ssrJSON/blob/main/README.md>
  - <https://github.com/Antares0982/ssrJSON/blob/main/CMakeLists.txt>
  - <https://github.com/Antares0982/ssrJSON/blob/main/.github/workflows/release.yml>
  - <https://github.com/Antares0982/ssrJSON/graphs/contributors>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/ratio_distribution.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/twitter.json_load%26dump.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/twitter.json_dumps_to_bytes.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/canada.json_load%26dump.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/canada.json_dumps_to_bytes.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/github.json_load%26dump.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/github.json_dumps_to_bytes.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/mesh.json_load%26dump.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/mesh.json_dumps_to_bytes.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/simple_object_zh.json_load%26dump.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/simple_object_zh.json_dumps_to_bytes.v0.0.17.svg>
  - <https://github.com/Nambers/ssrJSON-benchmark>
  - <https://github.com/Nambers/ssrJSON-benchmark/blob/main/README.md>
  - <https://github.com/Nambers/ssrJSON-benchmark/blob/main/src/ssrjson_benchmark/benchmark.py>
  - <https://github.com/Nambers/ssrJSON-benchmark/blob/main/src/ssrjson_benchmark/report.py>
  - <https://github.com/Nambers/ssrJSON-benchmark/blob/main/src/ssrjson_benchmark/template.md>
  - <https://raw.githubusercontent.com/Nambers/ssrJSON-benchmark/main/results/AVX2/i7-13700K_linux_0.0.21.pdf>
  - <https://ikuyo.dev/ssrJSON-benchmark/>
- **Sources the enricher read:**
  - <https://github.com/Antares0982/ssrJSON>
  - <https://github.com/Antares0982/ssrJSON/blob/main/README.md>
  - <https://github.com/Antares0982/ssrJSON/tree/main>
  - <https://github.com/Antares0982/ssrJSON/blob/main/pysrc/__init__.pyi>
  - <https://github.com/Antares0982/ssrJSON/blob/main/pysrc/__init__.py>
  - <https://github.com/Antares0982/ssrJSON/blob/main/pyproject.toml>
  - <https://github.com/Antares0982/ssrJSON/blob/main/CHANGELOG.md>
  - <https://github.com/Antares0982/ssrJSON/blob/main/CMakeLists.txt>
  - <https://github.com/Antares0982/ssrJSON/blob/main/cmake/CompilerFeatures.cmake>
  - <https://github.com/Antares0982/ssrJSON/blob/main/flake.nix>
  - <https://github.com/Antares0982/ssrJSON/blob/main/ci/nixfiles/build_package.nix>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/multilib.c>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/ssrjson_config.h>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/ssrjson.h>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/tls.h>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/decode/decode.c>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/decode/decode_shared.h>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/decode/str/cache_key.h>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/encode/encode.c>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/encode/_encode_impl.inl.h>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/encode/encode_shared.h>
  - <https://github.com/Antares0982/ssrJSON/blob/main/src/utils/encode_utils.c>
  - <https://github.com/Antares0982/ssrJSON/blob/main/python-test/test_dict.py>
  - <https://github.com/Antares0982/ssrJSON/blob/main/python-test/test_reentrant.py>
  - <https://github.com/Antares0982/ssrJSON/issues?q=is%3Aissue>
  - <https://github.com/Antares0982/ssrJSON/issues/32>
  - <https://github.com/Antares0982/ssrJSON/graphs/contributors>
  - <https://github.com/Antares0982/ssrJSON/commits/main>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/ratio_distribution.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/twitter.json_load%26dump.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/twitter.json_dumps_to_bytes.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/canada.json_load%26dump.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/github.json_load%26dump.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/mesh.json_load%26dump.v0.0.17.svg>
  - <https://raw.githubusercontent.com/Antares0982/ssrJSON/main/pics/simple_object_zh.json_dumps_to_bytes.v0.0.17.svg>
  - <https://github.com/Nambers/ssrJSON-benchmark/blob/main/README.md>
  - <https://github.com/Nambers/ssrJSON-benchmark/blob/main/src/ssrjson_benchmark/benchmark.py>
  - <https://en.chr.fan/2026/01/07/python-json/>
  - <https://chr.fan/en/python-json/>
  - <https://pypi.org/pypi/ssrjson/json>
  - <https://github.com/ijl/orjson/blob/master/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/antares0982/ssrjson`) · [data/wave4/enrich/raw/github_com_antares0982_ssrjson.json](../../../data/wave4/enrich/raw/github_com_antares0982_ssrjson.json) (enrichment confidence 0.8)

</details>
