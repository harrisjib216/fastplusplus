# UltraJSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C (CPython extension; bundled C++ double-conversion)` · `BSD-3-Clause AND TCL` · 🟢 active

> Maintenance-only CPython C extension for JSON; up to 2.5x faster than stdlib json on standard fixtures; Python-only.

| | |
|---|---|
| **Beats** | CPython json module (stdlib json) |
| **Claimed result** | orjson README Performance tables (unchanged in 3.9.4; measured with orjson 3.7.9, ujson 5.4.0, Python 3.10.5, Linux amd64), median latency ujson vs stdlib json, ratios derived from page data: canada.json serialize 14.16 vs 35.7 ms (2.5x faster), deserialize 8.73 vs 21.1 ms (2.4x); citm_catalog.json serialize 2.89 vs 3.93 ms (1.4x), deserialize 3.5 vs 4.99 ms (1.4x); twitter.json serialize 1.68 vs 1.8 ms (1.07x), deserialize 1.87 vs 2.45 ms (1.3x); github.json serialize 0.18 vs 0.18 ms (tie), deserialize 0.19 vs 0.16 ms (ujson slower). The same README's pretty-print rows (derived from page data) show the largest gaps, because json's indent path is pure Python: github.json pretty 0.19 vs 0.71 ms (3.7x) and citm_catalog.json pretty 3.59 vs 33.42 ms (9.3x). Sorted twitter.json is 2.07 vs 2.32 ms (1.1x). |
| **Workload** | Python loads/dumps of the twitter.json, github.json, citm_catalog.json and canada.json fixtures, median latency per call, measured in the orjson project's README (Python 3.10.5, ujson 5.4.0). |
| **Metric** | latency |
| **Hardware** | Linux amd64, CPU model not stated in the orjson README; the project's own README gives only 'Linux 5.15.0-1037-azure x86_64'. |
| **Compiler and flags** | orjson README: Python 3.10.5 on Linux (amd64) with the ujson 5.4.0 PyPI wheel; the wheel's compiler and flags are not stated. ujson's setup.py adds only -D_GNU_SOURCE (optimization comes from CPython's sysconfig defaults), compiles the bundled C++ double-conversion library plus dconv_wrapper.cc, and links -lstdc++ -lm; wheels are built in CI with cibuildwheel. UltraJSON's own README table used CPython 3.11.3 built with GCC 11.3.0 and ujson 5.7.1.dev26. |
| **Adoption** | 4.5k stars; widely installed Python package (ujson on PyPI) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/ultrajson/ultrajson) · [benchmark](https://github.com/ijl/orjson/blob/3.9.4/README.md#performance) |

## Verdict

orjson's README (orjson 3.7.9, ujson 5.4.0, CPython 3.10.5, Linux amd64, CPU not stated; pytest-benchmark medians with GC disabled and CPUs 0-1 pinned; both libraries wrapped as dumps(obj).encode('utf-8') and loads(bytes)) shows ujson 1.07-2.5x faster than stdlib json on twitter, citm_catalog and canada, tied on github.json dumps and slower on github.json loads (0.19 vs 0.16 ms). A spot check this session (ujson 6.0.0 PyPI wheel, CPython 3.13.16, 4-vCPU Intel Xeon @ 2.10GHz VM, timeit medians of 15, same fixtures and wrappers; not a tier source) found ujson faster on all 16 rows, by 1.21x (github loads) to 3.31x (canada dumps). In the same check 6.0.0 encoded 10-20% faster than 5.13.0, and decode speed was unchanged.

## Use it when

- Existing Python services already on ujson, or code that wants a json-style str-returning API with a moderate speedup without orjson's bytes output and option flags (1.2-3.3x over stdlib json on the four standard fixtures in a CPython 3.13 spot check)
- Float-heavy documents such as GeoJSON coordinates (canada.json): the largest gains, 2.4x on loads and 2.5-3.3x on dumps
- Platforms the faster replacements do not ship wheels for: PyPy 3.11, GraalPy, i686 and musllinux i686, win32, and free-threaded CPython 3.14t/3.15t (wheels cover CPython 3.10-3.15 on Linux x86/x86_64/aarch64 glibc and musl, macOS x86_64/arm64, and Windows x86/x64/ARM64)
- Pretty-printing on CPython 3.12 or older, where json.dumps(indent=...) still runs in pure Python (3.7-9.3x gaps in the 2022 orjson tables)

## Skip it when

- New projects: the README puts the library in maintenance-only mode, says its architecture risks new buffer overflows with any change, and recommends orjson, which orjson's own tables put 2-2.8x ahead of ujson on loads and 3.9-5.3x on dumps
- C or C++ code: since 6.0.0 the encoder and decoder depend on the CPython API; use yyjson or simdjson, or the catalogued ujson4c for the old decoder core
- Validating untrusted JSON: on 6.0.0, loads accepts '-' (returns 0), leading zeros ('01'), '1.' and raw control characters inside strings, all of which json rejects; orjson's suite counted 38 of 342 invalid documents accepted (json: 17)
- Code that needs exact Decimal round-trips, object_hook/parse_float/parse_int hooks, or output byte-identical to json.dumps
- Memory-tight parsing of large documents with repeated keys: there is no key memoization, so after loads it retained 1.4-1.75x the memory json did (citm_catalog, twitter, github), which matches open issue #333

## How it is fast

The decoder is a single-pass recursive-descent parser over UTF-8 bytes. It classifies string bytes through a 256-entry lookup table into a UCS4 scratch buffer, then calls PyUnicode_FromKindAndData. Integers are parsed by a hand-written overflow-checked loop that falls back to PyLong_FromString, and floats both ways go through Google's bundled double-conversion library (shortest round-trip output on encode). The encoder writes into a 64 KiB stack buffer that moves to a doubling heap buffer when full, escapes with switch and lookup tables derived from modp_ascii, takes compact-ASCII str data directly from PyUnicode_AsUTF8AndSize, and decodes the finished buffer once with PyUnicode_DecodeUTF8. There is no SIMD. Against stdlib json it also skips json's bytes-to-str decode before parsing, and on CPython 3.12 and older it skips json's pure-Python indent path.

## Compared with alternatives

Against orjson and ssrJSON, the other Python stdlib-json replacements catalogued, pick ujson only for its json-style str API on targets they do not cover (PyPy, GraalPy, i686/win32, musl i686, free-threaded wheels) or when you already depend on it. orjson is several times faster, is what ujson's maintainers recommend, and also serializes dataclasses and datetimes natively. From C or C++ this package does not apply: use yyjson, simdjson or the catalogued ujson4c (the old UltraJSON decoder core).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | CPython (or PyPy/GraalPy) C API; bundled Google double-conversion (C++), linked with -lstdc++ -lm; a system double-conversion can be used via UJSON_BUILD_DC_INCLUDES and UJSON_BUILD_DC_LIBS |
| **Minimum toolchain** | Python &gt;= 3.10; a source build needs a C compiler and a C++ compiler for double-conversion, plus setuptools &gt;= 80 and setuptools-scm &gt;= 9.2 |
| **Platforms** | PyPI 6.0.0 wheels: CPython 3.10-3.15 (including free-threaded 3.14t/3.15t), PyPy 3.11 and GraalPy, on manylinux/musllinux x86_64, i686 and aarch64, macOS x86_64 and arm64, and Windows x86, x64 and ARM64. ultrajson.h stops with #error if the byte order cannot be detected. No riscv64 wheels yet (open issue #694) |
| **Thread safety** | No global state, and the module declares Py_MOD_GIL_NOT_USED for free-threaded builds. The README says mutating an object in one thread while another thread serializes it is unsupported and unsafe ('all bugs are features'). |
| **Drop-in for the baseline** | partial — it accepts the common json arguments and returns str, but its default output differs (compact ',' and ':' separators, '/' escaped as '\/'), loads has no hooks, Decimal and non-str keys (even tuples) are coerced instead of raising TypeError, cycles raise OverflowError after 1024 levels instead of ValueError, and it accepts invalid inputs that json rejects |

## Gotchas

- Harness flaws behind the numbers: the 9.3x (citm_catalog) and 3.7x (github) pretty-print wins are a CPython 3.10 artifact, because CPython 3.13 moved json.dumps(indent=...) to the C encoder (Lib/json/encoder.py). A CPython 3.13.16 spot check this session measured only 1.72x and 1.66x. UltraJSON's own README table (tests/benchmark.py) runs ujson with ensure_ascii=False against json's default ensure_ascii=True, so the encode rows compare different outputs and favour ujson. Its 'UTF-8 strings' decode input is json.dumps output, which is all ASCII \u escapes. In orjson's harness json.dumps keeps its spaced ', ' and ': ' separators (a small bias; compact separators moved github dumps from 1.82x to 1.65x).
- Silent coercions and hooks on encode: Decimal is converted through float, so Decimal('12345678901234567890.123') is written as 1.2345678901234567e+19 (json raises TypeError); non-str dict keys are passed through str(), so a (1, 2) key becomes "(1, 2)"; any object with a toDict() method is serialized as that dict; and __json__() output is spliced in unvalidated, so it can produce invalid JSON.
- Lenient parser: '-' parses to 0, '01' to 1 (open issue #591), '1.' to 1.0, and raw control characters are accepted inside strings. NaN and Infinity are accepted on loads and emitted by default on dumps, as in json. The orjson README's reports that ujson segfaults on sorting int keys and returns '' for a lone '\ud800' escape are stale: on 6.0.0, mixed-type keys raise TypeError and the lone escape returns '\ud800', as json does.
- Memory and safety: the decoder's UCS4 string scratch buffer is sized to 4 bytes per remaining input byte, so peak memory during loads reached 1.7x json's on citm_catalog (11,189 vs 6,546 KiB). Issue #712 (unchecked mallocs) is still open, and decode.c's Object_newIntegerFromString still uses PyObject_Malloc without a NULL check. Issue #675 (a 4-byte UTF-8 overread in Buffer_EscapeStringValidated) is also open, but current encode.c checks end - io &lt; 4 before reading.

## Known shortcomings

- Python-only entry (like orjson and ssrJSON): since 6.0.0 (2026-09-04) the encoder and decoder include Python.h and use PyObject\*, so it is not a C library callable from C++ (the older Python-free lib/ core is what the already-listed esnme/ujson4c wraps). orjson 3.9.4 README tables (orjson 3.7.9, ujson 5.4.0, Python 3.10.5) with no CPU model or wheel flags; wins are small or absent on github.json; maintenance-only (the README points to orjson), 2022 numbers, 2026 security advisories. Licence BSD-3-Clause AND TCL.
- Harness flaws: the 9.3x/3.7x pretty-print wins are a CPython 3.10 artefact (CPython 3.13's json.dumps(indent) uses the C encoder; spot check on citm gives 1.72x); the first-party tests/benchmark.py runs ujson with ensure_ascii=False against json's default True, and its 'UTF-8 strings' decode input is all \u escapes; the orjson harness keeps json's spaced separators (small bias). Scratch spot check (ujson 6.0.0, CPython 3.13.16, not tier evidence): ujson faster on all 16 rows by 1.21x-3.31x, github loads no longer slower, 6.0.0 encodes 10-20% faster than 5.13.0. On 6.0.0 loads accepts '-' (returns 0), '01', '1.' and raw control characters; Decimal silently goes through float; __json__ output is spliced in unvalidated; retained memory is 1.4-1.75x json's (no key memo). Stale caveats: the int-key sort segfault and '' for a lone \ud800 are fixed (now TypeError and '\ud800').

## Caveats and trade-offs

Python-only since 6.0.0: commit 'Collapse the /lib vs /python source code split' (2026-07-26, released 2026-09-04) removed the JSONObjectDecoder callback struct and replaced JSOBJ with PyObject\*. src/ujson/encode.c and decode.c now include Python.h and build Python objects directly, so the current code is not a C library callable from C or C++ without embedding CPython. Up to 5.13.0, src/ujson/lib/ (ultrajsondec.c, ultrajsonenc.c, ultrajson.h) was a Python-free callback API (JSON_DecodeObject, JSON_EncodeObject); its decoder is what esnme/ujson4c wraps, and ujson4c is already listed (wave 4, tier A, nativejson-benchmark). All UltraJSON numbers are Python-level, against CPython's json module, whose _json C accelerator does the scanning and compact encoding, so the baseline is itself largely C. The baseline is not a C++ library, and the guessed list (nlohmann/json) does not apply. The win is workload-dependent and small on modern CPython: a tie on github.json serialize and slower on github.json deserialize. In UltraJSON's own README, decoding an array of 256 strings (28,518 vs 42,221 calls/s) and encoding 256 UTF-8 strings (3,457 vs 3,653) are slower than json, and ujson trails orjson everywhere (256 doubles encode 18,282 vs 79,569). The independent numbers are from 2022 (ujson 5.4.0); the first-party ones are from 2023 (5.7.1.dev26). The README puts the project in maintenance-only mode: 'UltraJSON's architecture is fundamentally ill-suited to making changes without risk of introducing new security vulnerabilities'. It recommends migrating to orjson. Security advisories: double free and surrogate mishandling (fixed in 5.4.0); an integer overflow on a large indent leading to buffer overflow or an infinite loop, and a memory leak parsing large integers (both fixed in 5.12.0); a ujson.dump() leak on write failure (5.12.1); malformed UTF-8 accepted in dumps of bytes (5.13.0); loose continuation-byte validation in loads from bytes (#750, 6.0.0). The #750 fix changes a mask from 0x80 to 0xc0 and adds error cases, so it does not alter valid-input speed. The orjson README also reports that ujson segfaulted on sorting int keys, fails to reject 38 of 342 invalid JSONTestSuite/nativejson documents (json: 17), and returns '' for a lone surrogate escape. The nativejson-benchmark figures (parse of 3 files 8.95 ms vs Nlohmann 72.48 ms, derived from the i7-4980HQ clang 7.0 CSV; Parse Double 34/66 and Parse String 5/9 correct) belong to ujson4c, not to this package. License terms: EA BSD-3-Clause, plus the modp_ascii BSD notice and permissive TCL terms for the numeric decoder; the bundled double-conversion is BSD-3-Clause. No patent grant. [retier] Pretty-print 9.3x/3.7x rows are a CPython 3.10 artefact (3.13 json.dumps(indent) uses the C encoder, about 1.72x on citm); first-party benchmark runs ujson ensure_ascii=False vs json default True and its UTF-8 rows decode pure \u escapes; orjson harness keeps json's spaced separators. ujson 6.0.0 on CPython 3.13 still leads 1.21x-3.31x on all 16 rows (scratch spot check, not tier evidence). Lenient loads ('-', '01', '1.', raw control chars), Decimal through float, __json__ spliced unvalidated, 1.4-1.75x retained memory. Int-key sort segfault and lone \ud800 handling fixed.

Project is in maintenance-only mode: its README warns that 'UltraJSON's architecture is fundamentally ill-suited to making changes without risk of introducing new security vulnerabilities' (buffer overflows) and recommends migrating to orjson, which it calls much faster. Defaults differ from json.dumps (ensure_ascii=True, escape_forward_slashes=True), so output is not byte-identical without options. The orjson 3.9.4 README reports that ujson 5.4.0 segfaulted in its int-keys sort benchmark and that ujson.loads of a lone surrogate escape returns an empty string instead of raising.

## Maintenance

Maintenance-only by the README's own warning, but actively released (6.0.0 on 2026-09-04, last commit 2026-10-05), BSD-3-Clause AND TCL licensed, and shipped as wheels for CPython 3.10-3.15, PyPy and GraalPy. The independent numbers are sound but dated: the 9.3x pretty-print figure does not hold on CPython 3.13+, and the first-party README table runs ujson with ensure_ascii=False against json's default ensure_ascii=True.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** The orjson README (shipped unchanged in orjson 3.9.4, measured with orjson 3.7.9 and ujson 5.4.0 on Python 3.10.5) is an independent, widely cited third-party comparison with public harness code (bench/benchmark_dumps.py, bench/benchmark_loads.py, bench/util.py, script/pybench: pytest-benchmark, GC disabled, CPUs 0-1 pinned) and has ujson and stdlib json rows. Every latency in the record matches. It falls short of A because no CPU model is given and the ujson wheel's compiler and flags are not stated. UltraJSON's own README table (tests/benchmark.py, Azure VM, no CPU model) is first-party and would be C on its own.
- **Verifier notes:** All claimed numbers match the orjson README tables and UltraJSON's own README, and metadata checks out (4.5k stars, not a fork, not archived, last commit 2026-10-05, latest release 6.0.0 on 2026-09-04); PyPI declares the license as 'BSD-3-Clause AND TCL', and the language field could read 'C (CPython extension; bundled C++ double-conversion)'. On the C++ question: UltraJSON does NOT qualify as a C library callable from C++. Since 6.0.0 its encoder and decoder are fused with the CPython API, and its measured claims are Python-level against stdlib json. Keep it only as a Python-binding entry on the same footing as orjson and ssrJSON in wave 4 json, flagged 'Python-only, not usable from C++'. It is not a cross-language claim, since both sides are C. C++ users wanting its decoder core already have esnme/ujson4c (listed, tier A), so this is not a duplicate of ujson4c: the claims and baselines differ.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `license`, `caveats`
- **Shortcomings recorded by:** orjson README tables (verifier); enricher (wave 4)
- **Pages the verifier opened:**
  - <https://pypi.org/pypi/orjson/3.9.4/json>
  - <https://github.com/ijl/orjson/blob/3.9.4/README.md>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/bench/benchmark_loads.py>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/bench/benchmark_dumps.py>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/bench/util.py>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/script/pybench>
  - <https://github.com/ultrajson/ultrajson>
  - <https://github.com/ultrajson/ultrajson/commits/main>
  - <https://github.com/ultrajson/ultrajson/tree/main/src/ujson>
  - <https://github.com/ultrajson/ultrajson/commits/main/src/ujson/decode.c>
  - <https://github.com/ultrajson/ultrajson/releases>
  - <https://github.com/ultrajson/ultrajson/releases/tag/6.0.0>
  - <https://github.com/ultrajson/ultrajson/releases/tag/5.13.0>
  - <https://github.com/ultrajson/ultrajson/pull/750>
  - <https://github.com/ultrajson/ultrajson/pull/750/files>
  - <https://github.com/ultrajson/ultrajson/security/advisories>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/README.md>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/setup.py>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/tests/benchmark.py>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/src/ujson/ultrajson.h>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/src/ujson/encode.c>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/src/ujson/decode.c>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/src/ujson/ujson.c>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/src/ujson/dconv_wrapper.cc>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/5.13.0/src/ujson/lib/ultrajsondec.c>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/5.13.0/src/ujson/lib/ultrajsonenc.c>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/5.13.0/src/ujson/lib/ultrajson.h>
  - <https://pypi.org/pypi/ujson/json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/README.md>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/setup.py>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/tests/benchmark.py>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/src/ujson/ultrajson.h>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/src/ujson/ujson.c>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/src/ujson/encode.c>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/src/ujson/decode.c>
  - <https://raw.githubusercontent.com/ultrajson/ultrajson/HEAD/src/ujson/dconv_wrapper.cc>
  - <https://github.com/ultrajson/ultrajson/releases/tag/6.0.0>
  - <https://github.com/ultrajson/ultrajson/issues>
  - <https://github.com/ultrajson/ultrajson/issues/675>
  - <https://github.com/ultrajson/ultrajson/issues/712>
  - <https://github.com/ultrajson/ultrajson/commits/main>
  - <https://pypi.org/pypi/ujson/json>
  - https://pypi.org/project/ujson/6.0.0/ (wheel installed into scratch for behaviour probes and spot timing)
  - https://pypi.org/project/ujson/5.13.0/ (wheel installed into scratch for spot timing)
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/bench/data.py>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/bench/benchmark_dumps.py>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/bench/benchmark_loads.py>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/bench/benchmark_empty.py>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/bench/util.py>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/bench/requirements.txt>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/script/pybench>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/script/graph>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/data/twitter.json.xz>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/data/citm_catalog.json.xz>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/data/canada.json.xz>
  - <https://raw.githubusercontent.com/ijl/orjson/3.7.9/data/github.json.xz>
  - <https://raw.githubusercontent.com/ijl/orjson/3.9.4/README.md>
  - <https://raw.githubusercontent.com/ijl/orjson/3.9.4/script/pyindent>
  - <https://raw.githubusercontent.com/ijl/orjson/3.9.4/script/pysort>
  - <https://raw.githubusercontent.com/ijl/orjson/3.9.4/script/pynonstr>
  - <https://raw.githubusercontent.com/ijl/orjson/HEAD/README.md>
  - <https://raw.githubusercontent.com/python/cpython/3.10/Lib/json/encoder.py>
  - <https://raw.githubusercontent.com/python/cpython/3.13/Lib/json/encoder.py>
  - <https://raw.githubusercontent.com/python/cpython/3.14/Lib/json/encoder.py>
  - <https://raw.githubusercontent.com/python/cpython/3.13/Lib/json/__init__.py>
  - <https://raw.githubusercontent.com/python/cpython/3.13/Modules/_json.c>
  - <https://raw.githubusercontent.com/python/cpython/3.13/Doc/whatsnew/3.13.rst>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/ultrajson/ultrajson`) · [data/wave4/enrich/raw/github_com_ultrajson_ultrajson.json](../../../data/wave4/enrich/raw/github_com_ultrajson_ultrajson.json) (enrichment confidence 0.85)

</details>
