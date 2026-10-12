# ada-url/idna

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0 OR MIT` · 🟢 active

> C++20 IDNA to_ascii/to_unicode (UTS #46) domain-name encoder, about 1.26x faster than ICU.

| | |
|---|---|
| **Beats** | ICU |
| **Claimed result** | 1504 ns/op, 48.5 M/s, 3.99 M url/s (Ada) vs 1898 ns/op, 38.5 M/s, 3.16 M url/s (ICU) -- about 1.26x faster (derived from page data) |
| **Workload** | IDNA to_ascii domain-name Unicode processing (UTS #46), Google Benchmark 'to_ascii' tool on Apple M1 Max |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max |
| **Compiler and flags** | LLVM 14 (clang), C++20; exact optimization flags beyond the provided CMake benchmark build are not itemized |
| **Adoption** | 69 stars; used by Node.js and referenced in a ClickHouse PR (per README) |
| **Last commit** | 2026-08-24 |
| **Links** | [repository](https://github.com/ada-url/idna) · [benchmark](https://github.com/ada-url/idna#benchmarks) |

## Verdict

On Apple M1 Max with LLVM 14 (C++20, Release build via the repo's own CMake benchmark target), Google Benchmark's to_ascii tool measured Ada at 1504 ns/op (48.5 M/s, \~3.99 M domains/s) versus ICU's uidna_nameToASCII_UTF8 at 1898 ns/op (38.5 M/s, \~3.16 M domains/s), over a fixed set of 6 sample domain strings defined in benchmarks/to_ascii.cpp — about 1.26x faster.

## Use it when

- Already building or embedding a URL/host-normalization layer and want IDNA to_ascii/to_unicode without linking full ICU
- C++20 toolchain available (GCC 12+, LLVM/Clang 12+, MSVC 2022)
- Workload is many small domain-name labels (matches the benchmark's label-oriented shape), not bulk text
- Want to vendor a small, dual Apache-2.0/MIT-licensed source-drop instead of a system Unicode dependency
- Building something with precedent for this exact use, e.g. Node.js or a ClickHouse-style URL/host column

## Skip it when

- Need general-purpose UTF-8 validation or transcoding, not domain-name IDNA specifically (out of scope for this library)
- Stuck on a pre-C++20 toolchain
- Need ICU's broader Unicode services (locale, collation, etc.) beyond IDNA
- Want strong benchmark confidence: only one README micro-benchmark over 6 fixed sample domain strings, ICU version unstated, and the measured gain is modest (\~1.26x)
- Want a library with a long track record; only 69 stars and comparatively young/niche despite active maintenance

## How it is fast

An all-ASCII fast path (from_ascii_to_ascii) skips the whole Unicode pipeline and just lowercases in place. Non-ASCII input goes through a single UTF-8-&gt;UTF-32 transcode into a pre-sized buffer, a mapping pass into an exactly-sized second buffer to avoid reallocation, and an is_already_nfc check that skips NFC normalization entirely when the input is already normalized; labels are then walked with a single pointer scan instead of repeated string::find calls. Unicode/IDNA lookup tables are stored DEFLATE-compressed on disk and inflated once, lazily, behind an atomic-CAS/spin-wait (no mutex) into the same O(1) multi-stage lookup layout used pre-compression, so steady-state lookups are plain table hits and only first use pays an inflate cost.

## Compared with alternatives

The catalogued siblings (simdutf8, xutf, SimdUnicode, utf8_range, encoding_rs, Boost.Text, unicode-transforms, etc.) are general UTF-8/Unicode validators or transcoders and don't do domain-name IDNA at all. Pick ada-url/idna specifically for URL host normalization (to_ascii/to_unicode), not as a substitute for those general-purpose libraries.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the core library; optional simdutf for UTF transcoding via ADA_USE_SIMDUTF (off by default); benchmarks/tests pull Google Benchmark, GoogleTest, and simdjson via CPM but are not needed to use the library |
| **Minimum toolchain** | C++20 (GCC 12+, LLVM/Clang 12+, MSVC 2022 per README); note the singleheader demo.cpp is documented as compiled with -std=c++17, but the library core itself requires C++20 |
| **Platforms** | portable C++20, no SIMD/arch requirement in the core path; explicit byte-swap code in table_store.hpp for big-endian platforms (e.g. s390x) |
| **Thread safety** | table initialization is thread-safe via atomic CAS + spin-wait, no mutex (table_store.hpp); ensure_tables() returns false on init failure (OOM/corrupt blob), which callers must treat as a hard error; otherwise not documented beyond that |
| **Drop-in for the baseline** | partial — different API shape than ICU: std::string_view free functions vs ICU's uidna_openUTS46/uidna_nameToASCII_UTF8 C API, so a small wrapper is needed to substitute it |

## Gotchas

- to_ascii/to_unicode may accept or even produce invalid domains by design (documented WHATWG carve-outs), not strict RFC validity enforcement
- Inputs over max_domain_input_bytes (16384 bytes) are rejected outright rather than truncated
- Two API shapes exist: the value-returning to_ascii() has an ambiguous empty-string-on-error case; the bool-returning out-parameter overload avoids that ambiguity
- Table inflate happens lazily on first call; a corrupted/OOM init path is a hard error per the source comments, not a silent fallback

## Caveats and trade-offs

Category fit is imperfect: this is IDNA/UTS #46 domain-name processing, not raw UTF-8 validation or transcoding. There is only one README micro-benchmark, over a fixed list of 6 sample domain names (benchmarks/to_ascii.cpp), and the ICU version is not stated. The gain is modest (\~1.26x).

C++20 required; scope is limited to IDNA to_ascii/to_unicode (domain-name encoding), not general-purpose UTF-8 validation or transcoding.

## Maintenance

Actively maintained (last commit 2026-08-24, 5 open issues, used by Node.js and referenced in a ClickHouse PR); dual Apache-2.0/MIT licensed and small enough to vendor as a source-drop despite a modest 69-star footprint.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README shows Google Benchmark output from benchmarks/to_ascii.cpp: Ada 1504 ns vs ICU (uidna nameToASCII) 1898 ns, with the compiler (LLVM 14) and CPU (Apple M1 Max) stated. The documented build (`cmake -D ADA_IDNA_BENCHMARKS=ON -B build`) defaults to Release with C++20 via cmake/idna-flags.cmake, so the flags are pinned by public build files. This matches the accepted precedent for CMake default-Release builds.
- **Verifier notes:** The numbers match the README (1.26x derived). The repo ships LICENSE-APACHE and LICENSE-MIT, and the README says it is dual-licensed; GitHub reports only Apache-2.0. It has 69 stars and its last commit was 2026-08-24.
- **Fields the verifier corrected:** `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ada-url/idna>
  - <https://github.com/ada-url/idna#benchmarks>
  - <https://github.com/ada-url/idna/blob/main/benchmarks/to_ascii.cpp>
  - <https://github.com/ada-url/idna/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/ada-url/idna/blob/main/CMakeLists.txt>
  - <https://github.com/ada-url/idna/blob/main/cmake/idna-flags.cmake>
- **Sources the enricher read:**
  - <https://github.com/ada-url/idna>
  - <https://github.com/ada-url/idna#benchmarks>
  - https://github.com/ada-url/idna (readme via gh api)
  - https://github.com/ada-url/idna/git/trees/HEAD (recursive file tree via gh api)
  - <https://github.com/ada-url/idna/blob/main/include/idna.h>
  - <https://github.com/ada-url/idna/blob/main/CMakeLists.txt>
  - <https://github.com/ada-url/idna/blob/main/cmake/idna-flags.cmake>
  - <https://github.com/ada-url/idna/blob/main/singleheader/README.md>
  - <https://github.com/ada-url/idna/blob/main/src/to_ascii.cpp>
  - <https://github.com/ada-url/idna/blob/main/benchmarks/to_ascii.cpp>
  - <https://github.com/ada-url/idna/blob/main/include/ada/idna/to_ascii.h>
  - <https://github.com/ada-url/idna/blob/main/src/table_store.hpp>
  - <https://github.com/ada-url/idna/blob/main/include/ada/idna/identifier.h>
  - <https://github.com/ada-url/idna/blob/main/include/ada/idna/limits.h>
  - https://github.com/ada-url/idna (repo metadata via gh api: license, stars, pushed_at, archived, open_issues)
  - gh search issues --repo ada-url/idna "bug OR performance OR crash" (no matching open issues found)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/ada-url/idna`) · [data/wave3/enrich/raw/github_com_ada_url_idna.json](../../../data/wave3/enrich/raw/github_com_ada_url_idna.json) (enrichment confidence 0.6)

</details>
