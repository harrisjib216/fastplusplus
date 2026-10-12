# liburlparser (abspath fast-path vs ada)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> C++17 RFC 3986-style URL splitter with Public Suffix List domain extraction; its own parse+accessor loop runs \~1.25x ahead of ada.

| | |
|---|---|
| **Beats** | ada-url/ada (ada::url_aggregator) |
| **Claimed result** | Full parse + component-extraction ops/s: liburlparser NEW \~7.4-7.8M vs ada \~6.0-6.1M, new vs ada \~1.24-1.29x as stated on the page. OLD was \~5.4-5.5M, old vs ada \~0.90-0.91x. OPTIMIZATION_NOTES.md TL;DR: 'C++ parse_url vs ada: 22.7% behind -&gt; \~1.24-1.29x ahead'. |
| **Workload** | Single-process, interleaved A/B/C loop, 12 rounds x 4 reps over a urls.txt corpus. Each op parses one URL and reads protocol, host, path (abspath / get_pathname), query and fragment. The three sides are liburlparser OLD (pre-fix), liburlparser NEW (abspath fast-path + cache) and ada::parse&lt;ada::url_aggregator&gt;. This is the parse_url comparison summarized in benchmarks/OPTIMIZATION_NOTES.md. |
| **Metric** | throughput |
| **Adoption** | 21 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/MohammadRaziei/liburlparser) · [benchmark](https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/cpp/abspath_fix_verification/README.md) |

## Verdict

The author's fair_compare.cpp interleaves old liburlparser, new liburlparser and unmodified ada::parse&lt;ada::url_aggregator&gt; in one process; each op parses one URL and reads 5 components, and the new build did \~7.4-7.8M ops/s against ada's \~6.0-6.1M (1.24-1.29x), while the pre-fix build did 0.90-0.91x. Only 'this machine, 3 runs' is stated (no CPU, compiler or flags), urls.txt is not shipped (probably the benchmarks/ corpus of 10k Majestic domains in four simple, clean-path shapes), and ada's side also does WHATWG validation and normalization, so the two sides do not do equal work.

## Use it when

- You need registrable-domain and public-suffix splitting (for example 'ee.aut.ac.ir' becomes domain 'aut', suffix 'ac.ir') together with basic URL component splitting in one C++ or Python library.
- High-volume log or crawl processing of already-well-formed http(s) URLs, where you read scheme, host, path, query and fragment and do not need WHATWG canonicalization.
- Python pipelines that use tldextract, tld or publicsuffix2 for domain extraction. The README (2022 run) reports 1.12 s for 10M hosts, against 29.23 s for tldextract and 1.50 s for PyDomainExtractor.
- Code that must treat IPv4 and IPv6 hosts as typed addresses with integer conversion and arithmetic, not as domain names.

## Skip it when

- You need WHATWG URL Standard behavior (browser-equivalent parsing, percent-encoding of components, host validation, special-scheme rules). ada and its ports implement the standard. liburlparser is not documented as WHATWG-conformant, and its url constructor only trims, splits and lowercases the scheme and host.
- You need the benchmarked speed from a released package. The abspath() fast path and cache landed on master on 2026-09-18. Tag v2.0.0 (2026-09-11), which is also the latest PyPI release, still has the old abspath() that returns std::string by value. That old build measured 0.90-0.91x of ada.
- Input that is often messy or relative (dot-segments, repeated slashes, Unicode hosts). The published speed figures come from clean, simple URLs, where the fast path always applies.
- Several threads reading one url or hostname object at the same time. The const accessors fill mutable caches (host_cache_, abspath_cache_, hostname's parsed fields) with no locking, and the docs do not address this.
- Maturity-sensitive production use: 21 stars, one main author, v2.0.0 only weeks old, and daily API-changing commits (for example scp to scp_url renames and merged source files) in September 2026.

## How it is fast

The url constructor copies every field once into one owned buffer and stores (offset, length) spans, so most accessors are string_view reads with no allocation. It finds '#', '?' and ';' with a compare-and-OR SIMD scan: AVX2 selected at runtime, SSE2 or NEON as the baseline, scalar code otherwise. The ada win comes from abspath(), which used to run a full dot-segment resolver on every call; a cheap path_is_already_normalized() pre-scan now copies clean paths through unchanged and caches the result. PSL lookups use a vendored ankerl::unordered_dense open-addressing map, and the project reports +67-70% on host extraction from that change.

## Compared with alternatives

Pick it over Ada, ada-rs, lucid-url or sorug only when you need Public Suffix List domain and suffix splitting (none of those do it) and RFC 3986-level splitting is enough. When WHATWG-correct parsing or canonical href output matters, use Ada or one of its WHATWG ports.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at runtime (PSL data embedded at compile time; vendored ankerl::unordered_dense header, MIT). Build needs CMake &gt;= 3.19 and a Python 3 interpreter (find_package REQUIRED). Configure tries to download public_suffix_list.dat and falls back to the tracked copy. The Python module needs nanobind. |
| **Minimum toolchain** | C++17, CMake 3.19+; Python binding: Python &gt;= 3.10 per PyPI metadata (README still says &gt;= 3.8) |
| **Platforms** | Linux, macOS, Windows (CI matrix on ubuntu/macos/windows-latest). SIMD: x86-64 SSE2 baseline with runtime-dispatched AVX2, aarch64 NEON, scalar fallback elsewhere. |
| **Thread safety** | PSL singleton is lazily initialized via a function-local static (thread-safe init). No mutex anywhere: psl::load_from_path/load_from_string replace the shared table unguarded, and const accessors on url/hostname write mutable caches, so a shared object is not safe for concurrent reads. Otherwise not documented. |
| **Drop-in for the baseline** | partial — it covers the same 'parse a URL, read components' job, but the API and semantics differ: protocol() has no trailing ':' and query() has no leading '?', while ada's get_protocol() and get_search() include them. Errors are exceptions, not ada::result. There is no WHATWG normalization, href or setters. |

## Gotchas

- abspath() and normalized() drop a trailing '/' on non-root paths ('/a/' becomes '/a') and collapse '//' ('/a//b' becomes '/a/b'). The header documents both as deliberate and as different from ada's normalize_url().
- url parsing keeps Unicode hosts verbatim (ASCII-only per RFC 3986). Only idna::to_ascii() or url::normalized() convert them to Punycode, so 'café.com' and its xn-- form do not compare equal after a plain parse.
- Master still reports URLPARSER_VERSION 2.0.0, but it differs from the v2.0.0 tag (abspath() now returns const std::string& and there are new APIs). You cannot tell the fast and slow builds apart by version number.
- License is ambiguous. The README badge and text say MIT, but the LICENSE file is pybind11's BSD-3-Clause text with 'The Pybind Development Team' as copyright holder, and GitHub reports NOASSERTION.

## Known shortcomings

- The abspath fast path is on master only (2026-09-18); the latest tag and PyPI release v2.0.0 has the old abspath (0.90-0.91x of ada) and master still reports 2.0.0, so builds cannot be told apart by version. Not equal work: its constructor only trims, splits and lowercases scheme/host (no percent-encoding, host validation or IDNA) while ada does full WHATWG processing. The unshipped corpus (probably regenerable) is 10k clean Majestic-domain URLs in 4 shapes, so the fast path always applies. No CPU, compiler or flags. Const accessors fill mutable caches without locks and psl::load_from_\* swaps the shared table unguarded (undocumented). Semantics differ from ada (trailing-slash trimming, // collapsed, Unicode hosts verbatim, protocol()/query() without ':'/'?'). README says MIT but LICENSE holds pybind11's BSD-3 text. Needs Python 3 and CMake 3.19+ to configure; PyPI needs Python 3.10+ (README says 3.8). 21 stars, one main author, daily API changes.

## Caveats and trade-offs

No CPU model, compiler or flags are given ('this machine', 3 runs). The urls.txt corpus and the urlparser_old/new namespace-renamed sources needed to build fair_compare.cpp are not in the repo. ada is a WHATWG-conformant parser with full normalization, and liburlparser is not documented as WHATWG-conformant (its focus is PSL domain splitting). The work per op may therefore differ. The win came from fixing liburlparser's own abspath() cost, not from a faster core parser. License conflict: README says MIT, but LICENSE is pybind11's BSD-3-Clause text with 'The Pybind Development Team' as copyright holder. GitHub reports NOASSERTION. Both candidates are OSI-permissive.

Only the abspath()-only micro-benchmark beats ada; the project's own OPTIMIZATION_NOTES.md says overall parse_url is still \~17.9% behind ada after this and other fixes, so the library as a whole is currently slower than ada, not faster -- only this specific sub-operation wins. Adds Public Suffix List domain extraction that ada does not have.

## Maintenance

Actively developed (near-daily commits through 2026-09-25) and small enough to vendor as one .cpp/.h pair, but the benchmarked fast path is on master only (not in v2.0.0 or on PyPI) and the MIT vs BSD-3-Clause license question should be settled before you copy it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party results ('this machine, 3 runs') from public code (benchmarks/cpp/abspath_fix_verification/fair_compare.cpp), directly against unmodified ada::url_aggregator. No CPU, compiler or flags are stated. The urls.txt corpus and the renamed urlparser_old/new sources are not included, so the run is not reproducible as published.
- **Verifier notes:** The benchmark_url used /blob/main/ and returns 404, because the default branch is master; it is corrected to /blob/master/. The record's workload was wrong: the benchmark times a full parse plus five accessor calls per URL, not isolated abspath() calls. The numbers match exactly. Metadata checks out: 21 stars, last commit 2026-09-25, not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/MohammadRaziei/liburlparser>
  - <https://github.com/MohammadRaziei/liburlparser/blob/main/benchmarks/cpp/abspath_fix_verification/README.md>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/cpp/abspath_fix_verification/README.md>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/cpp/abspath_fix_verification/fair_compare.cpp>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/LICENSE>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/README.md>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/README.md>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/OPTIMIZATION_NOTES.md>
- **Sources the enricher read:**
  - <https://github.com/MohammadRaziei/liburlparser>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/README.md>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/cpp/abspath_fix_verification/README.md>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/cpp/abspath_fix_verification/fair_compare.cpp>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/OPTIMIZATION_NOTES.md>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/README.md>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/CMakeLists.txt>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/cpp/CMakeLists.txt>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/corpus/generate_corpus.py>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/benchmarks/cpp/bench.cpp>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/ARCHITECTURE.md>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/LICENSE>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/CMakeLists.txt>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/include/urlparser.h>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/src/urlparser.cpp>
  - <https://github.com/MohammadRaziei/liburlparser/blob/v2.0.0/src/urlparser.cpp>
  - <https://github.com/MohammadRaziei/liburlparser/blob/v2.0.0/include/urlparser.h>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/tests/cpp/perf_regression_guard.cpp>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/tests/cpp/fuzz_abspath.cpp>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/.github/workflows/cmake.yml>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/.github/workflows/wheels.yml>
  - <https://github.com/MohammadRaziei/liburlparser/blob/master/pyproject.toml>
  - <https://github.com/MohammadRaziei/liburlparser/issues?q=is%3Aissue>
  - <https://github.com/MohammadRaziei/liburlparser/pulls?q=is%3Apr>
  - <https://github.com/MohammadRaziei/liburlparser/releases>
  - <https://github.com/MohammadRaziei/liburlparser/commits/master>
  - <https://pypi.org/pypi/liburlparser/json>
  - <https://hn.algolia.com/api/v1/search?query=liburlparser>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/mohammadraziei/liburlparser`) · [data/wave5/enrich/raw/github_com_mohammadraziei_liburlparser.json](../../../data/wave5/enrich/raw/github_com_mohammadraziei_liburlparser.json) (enrichment confidence 0.35)

</details>
