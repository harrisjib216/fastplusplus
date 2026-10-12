# pybase64

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Python` · `BSD-2-Clause` · 🟢 active

> Python base64 module replacement backed by the SIMD libbase64 codec; roughly 6.6x faster encode than the stdlib.

| | |
|---|---|
| **Beats** | base64 (Python standard library base64 module) |
| **Claimed result** | Default settings (altchars=None, validate=True, padded=True): b64encode 17,492 MB/s vs stdlib base64.b64encode 2,653 MB/s (\~6.6x); b64decode with validate=True 9,037 MB/s vs 2,656 MB/s (\~3.4x); encodebytes 6,595 vs 2,386 MB/s (\~2.8x). With validate=False (the b64decode default in both libraries), decode is only 2,369 vs 2,030 MB/s (\~1.17x). With padded=False or ignorechars=b'', decode is slower than stdlib, e.g. 2,521 vs 2,655 MB/s. Ratios derived from page data. |
| **Workload** | b64encode/b64decode of a 135,696-byte buffer, measured with the package's own 'pybase64 benchmark' CLI |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max, macOS 26.5.2 |
| **Compiler and flags** | Apple clang version 21.0.0 (clang-2100.1.1.101); Python 3.15.0rc1. Per setup.py, the bundled aklomp/base64 is built via CMake with CMAKE_BUILD_TYPE=Release and the C extension with Python sysconfig CFLAGS. Exact flags are not printed in the README. |
| **Adoption** | 182 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/mayeut/pybase64) · [benchmark](https://raw.githubusercontent.com/mayeut/pybase64/master/README.rst) |

## Verdict

The package's own `pybase64 benchmark` CLI ran pybase64 1.5.0 (NEON path) against the stdlib base64 module in one Python 3.15.0rc1 process on an Apple M1 Max, using a 135,696-byte input and a build from Apple clang 21. b64encode ran at 17,492 vs 2,653 MB/s (\~6.6x) and validate=True decode at 9,037 vs 2,656 MB/s (\~3.4x). Non-validating decode was only \~1.17x faster, and two unpadded strict-decode configurations were slower than the stdlib. No x86 results are published.

## Use it when

- Python code that base64-encodes large binary payloads such as API responses, data URIs or attachments: b64encode measured 17,492 vs 2,653 MB/s on a 136 KB buffer.
- Decoding well-formed, padded input where you can pass validate=True: 9,037 vs 2,656 MB/s for standard base64, and 5,974 vs 1,186 MB/s for the URL-safe alphabet.
- Threaded or free-threaded (3.13t+) Python that decodes or encodes on many threads at once: the GIL is released, and the module declares Py_MOD_GIL_NOT_USED.
- Deployments that need prebuilt wheels beyond x86-64: PyPI has 1.5.0 wheels for Linux aarch64, armv7l, ppc64le, s390x and riscv64 (glibc and musl), macOS arm64, Windows ARM64, iOS, Android and wasm32.

## Skip it when

- Your decode calls use the defaults (validate=False). That path is scalar, only 2,369 vs 2,030 MB/s (about 1.17x), and SIMD for it is still an open issue (#4, filed 2017).
- Your input is unpadded and you need strict validation: validate=True with padded=False ran at 2,521 vs 2,655 MB/s, and URL-safe with ignorechars=b'' and padded=False at 2,201 vs 2,606 MB/s. Both are slower than CPython 3.15's stdlib.
- You need base32, base16, base85, Ascii85, decodebytes or file/stream encode()/decode(). None of these are provided. A streaming API is only a discussion in open issue #914.
- Your payloads are short, such as JWT-sized tokens. The only published benchmark uses a 135,696-byte buffer, so per-call overhead on small strings is not documented.
- You build from source on hosts without CMake or a C compiler. Outside cibuildwheel the extension is optional, so the install succeeds but silently runs at stdlib speed.

## How it is fast

The work is done by a bundled, statically linked copy of aklomp/libbase64. It picks a SIMD codec at import time from CPUID/XGETBV (SSSE3, SSE4.1, SSE4.2, AVX, AVX2 or AVX-512 VBMI) or NEON on ARM, and encodes or decodes a full vector of bytes per step using shuffle/lookup instructions instead of a per-byte table loop. With validate=True and padded input, decoding and validation happen in one SIMD pass. Other alphabets such as URL-safe are handled by an SSE2/NEON compare-and-blend pass that maps +/ to the alternate characters, applied in 16 KiB chunks around the standard codec. The GIL is released for the whole C loop.

## Compared with alternatives

Pick pybase64 when the calling code is Python and you want a pip-installable, stdlib-compatible API: it is a Python binding of aklomp/base64, so reach for that library (or simdutf / Turbo-Base64) directly only from C/C++. It is the only Python-callable base64 entry in the catalog.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (libbase64 is bundled as a git submodule and linked statically); source builds need a C compiler and CMake, and cannot use a system libbase64 because private internals are used (#911) |
| **Minimum toolchain** | Python 3.9+ (classifiers cover CPython 3.9-3.15; PyPy and GraalPy wheels published); setuptools&gt;=77 plus CMake for sdist builds |
| **Platforms** | any platform CPython supports. SIMD is selected at runtime: x86/x86-64 SSSE3 through AVX2 and AVX-512 VBMI, NEON on 32/64-bit ARM. Other architectures (ppc64le, s390x, riscv64, wasm32) get libbase64's plain codec. Only Apple M1 (NEON) numbers are published. |
| **Thread safety** | Functions are stateless and release the GIL during encoding and decoding. Free-threaded builds are supported since 1.4.0 (Py_MOD_GIL_NOT_USED). 1.5.0 fixed a thread-safety bug in codec selection, which is now mutex-protected. |
| **Drop-in for the baseline** | partial — same names and arguments for b64encode/b64decode, standard_\*, urlsafe_\* and encodebytes, but no b32/b16/b85/a85/z85, decodebytes or file functions, and the big decode speedup requires changing call sites to validate=True |

## Gotchas

- Check pybase64.get_version(): it reports "C extension active - NEON/AVX2..." or "C extension inactive". The inactive fallback is just the stdlib with extra Python overhead.
- Since 1.5.0, urlsafe_b64decode defaults to padded=False to match Python 3.15. It therefore takes the slow non-SIMD path (2,081 vs 1,031 MB/s) unless you call b64decode(s, b'-_', validate=True) on padded data.
- 1.5.0 changed error behavior to track CPython 3.15. Non-ASCII str input is rejected even with validate=False. Excess or discontinuous padding raises binascii.Error. Accepting '+' or '/' alongside an alternate alphabet is deprecated and emits a warning.
- Input buffers must be C-contiguous; non-contiguous memoryviews raise BufferError.

## Known shortcomings

- Python binding. The 3.4x decode figure needs validate=True; default decode is only \~1.17x over the stdlib and some configurations are slower than the stdlib.
- Default decode (validate=False) runs a scalar path (SIMD request #4 open since 2017); unpadded validate=True and ignorechars=b'' are slower than the CPython 3.15 stdlib; urlsafe_b64decode defaults to padded=False since 1.5.0 (slow path). An sdist built without CMake installs fine but silently runs at stdlib speed. No b32/b85/stream API. Numbers are M1 NEON only, one 136 KB buffer.

## Caveats and trade-offs

Compared against Python's own stdlib base64 module (a C-implemented binascii wrapper), not a C/C++ baseline. The speed comes from the bundled aklomp/base64 SIMD codec (a git submodule; aklomp/base64 is catalogued separately). The large decode win (\~3.4x) needs validate=True. With default validate=False decode is \~1.17x, and several unpadded or ignorechars decode configurations are slower than CPython 3.15's stdlib. Encode (\~6.6x) is the robust win. Numbers come from a single machine (Apple M1 Max, NEON path).

Python package with a C/SIMD (NEON/AVX2/AVX-512) extension; falls back to a pure binascii path if the compiled extension is unavailable; URL-safe (altchars) decode variants show smaller speedups (\~2x) than plain decode (\~3.4x)

## Maintenance

Actively maintained (commits through 2026-09-26, v1.5.0 released 2026-08-08, Production/Stable classifier) and BSD-2-Clause, with wheels for most platforms, so `pip install pybase64` is the normal route and vendoring is unnecessary.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Benchmark section runs pybase64 and the stdlib base64 module in the same process via the public CLI (src/pybase64/__main__.py, 'pybase64 benchmark'). It states the compiler (Apple clang 21.0.0, clang-2100.1.1.101), Python 3.15.0rc1 and the CPU (Apple M1 Max). Flags come from setup.py, which builds the bundled aklomp/base64 SIMD codec with CMAKE_BUILD_TYPE=Release and the extension with Python's sysconfig CFLAGS, so A holds under the build-config-counts-as-flags precedent.
- **Verifier notes:** The record's benchmark_url returned 404 because the repo's default branch is master, not main; I corrected it to the master README. All quoted numbers match the README exactly. Metadata checks out: BSD-2-Clause, 182 stars, last commit 2026-09-26, not archived and not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** pybase64 README (M1, 136 KB): validate=True padded decode 5,974 vs stdlib 1,186 MB/s (\~5x).
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mayeut/pybase64/main/README.rst>
  - <https://raw.githubusercontent.com/mayeut/pybase64/master/README.rst>
  - <https://github.com/mayeut/pybase64>
  - <https://raw.githubusercontent.com/mayeut/pybase64/master/setup.py>
  - <https://raw.githubusercontent.com/mayeut/pybase64/master/src/pybase64/__main__.py>
  - <https://raw.githubusercontent.com/mayeut/pybase64/master/noxfile.py>
  - <https://raw.githubusercontent.com/mayeut/pybase64/master/.gitmodules>
- **Sources the enricher read:**
  - <https://github.com/mayeut/pybase64>
  - <https://github.com/mayeut/pybase64/blob/master/README.rst>
  - <https://github.com/mayeut/pybase64/blob/master/src/pybase64/__init__.py>
  - <https://github.com/mayeut/pybase64/blob/master/src/pybase64/_pybase64.c>
  - <https://github.com/mayeut/pybase64/blob/master/src/pybase64/_pybase64_get_simd_flags.c>
  - <https://github.com/mayeut/pybase64/blob/master/src/pybase64/_fallback.py>
  - <https://github.com/mayeut/pybase64/blob/master/src/pybase64/__main__.py>
  - <https://github.com/mayeut/pybase64/blob/master/setup.py>
  - <https://github.com/mayeut/pybase64/blob/master/pyproject.toml>
  - <https://github.com/mayeut/pybase64/blob/master/.gitmodules>
  - <https://github.com/mayeut/pybase64/blob/master/SECURITY.md>
  - <https://github.com/mayeut/pybase64/blob/master/docs/intro.rst>
  - <https://github.com/mayeut/pybase64/blob/master/docs/api.rst>
  - <https://github.com/mayeut/pybase64/blob/master/.github/workflows/benchmark.yml>
  - <https://github.com/mayeut/pybase64/issues>
  - <https://github.com/mayeut/pybase64/issues/4>
  - <https://github.com/mayeut/pybase64/issues/680>
  - <https://github.com/mayeut/pybase64/issues/911>
  - <https://github.com/mayeut/pybase64/issues/914>
  - <https://pypi.org/pypi/pybase64/json>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/mayeut/pybase64`) · [data/wave7/enrich/raw/github_com_mayeut_pybase64.json](../../../data/wave7/enrich/raw/github_com_mayeut_pybase64.json) (enrichment confidence 0.85)

</details>
