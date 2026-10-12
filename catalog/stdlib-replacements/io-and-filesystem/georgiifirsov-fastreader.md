# FastReader

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [I/O and filesystem](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🔴 abandoned

> Windows memory-mapped line reader using memchr; \~4x faster line iteration than std::ifstream::getline on a 9 KB file.

| | |
|---|---|
| **Beats** | std::ifstream |
| **Claimed result** | CFileHandler: 56,700 ns vs std::ifstream: 241,000 ns, about 4.25x faster (derived from page data). Each figure is the mean of 10 timed samples, and each sample is 3 full line-by-line passes over the 9 KB TestFile.txt. The repo description, not the README, says 'almost 5 times faster than standard C++ std::ifstream'. |
| **Workload** | Iterating the lines of a memory-mapped file (CreateFileMapping/MapViewOfFile + memchr, WinAPI) vs std::getline on a std::ifstream. The input is the repo's 9,194-byte TestFile.txt. The Google Test 'Timing' tests in FastReaderTest/test.cpp average 10 samples of 3 passes each, and opening/mapping the file is outside the timed region. The README shows the output of one execution of those tests. |
| **Metric** | latency |
| **Compiler and flags** | MSVC, Visual Studio 2019 toolset v142 (per FastReaderTest.vcxproj). The Debug configs use /Od; the Release configs define NDEBUG with no explicit optimization override. Which configuration produced the README numbers is not stated. |
| **Adoption** | 5 stars |
| **Last commit** | 2019-11-13 |
| **Links** | [repository](https://github.com/GeorgiiFirsov/FastReader) · [benchmark](https://github.com/GeorgiiFirsov/FastReader#test-results) |

## Verdict

On the repo's own Google Test 'Timing' suite (mean of 10 samples x 3 full passes over the repo's 9,194-byte TestFile.txt), CFileHandler averaged 56,700 ns versus 241,000 ns for std::ifstream + std::getline against the MSVC STL — about 4.25x faster — with no CPU disclosed and the Debug-vs-Release build configuration used for the published numbers unstated.

## Use it when

- Windows-only tool that repeatedly parses a small-to-medium text file line-by-line and can absorb the one-time CreateFileMapping cost
- Read-only, whole-file-fits-in-memory workloads (log parsing, config files) where std::ifstream + getline overhead is a measured bottleneck
- Codebases already linking ATL (atlbase.h/CHandle), so the extra dependency is free
- Prototyping or benchmarking where GPL-3.0 licensing of the file itself is acceptable

## Skip it when

- Any non-Windows target - code compiles only against WinAPI + ATL
- Files without a trailing newline: memchr returning nullptr on the last unterminated line yields (BYTE\*)0 + 1, an invalid non-null pointer bug present in both the constructor and operator++
- Proprietary/closed-source projects that cannot take on GPL-3.0
- Anything needing formatted input, seeking, writing, or multi-threaded access - no documented thread safety, and CFileHandler holds raw pointers with no locking
- Production use generally: single-maintainer, 5 stars, no commits since 2019-11-13, no issues or PRs on record

## How it is fast

Maps the file into the process address space once instead of streaming through libc/CRT buffered I/O, avoiding per-getline syscalls and intermediate buffer copies. Line boundaries are found with memchr, which uses a vectorized/optimized scan, rather than std::getline's char-by-char sentry loop with locale-aware traits comparisons. Each line is copied exactly once, directly from the mapped pages into the returned std::string.

## Compared with alternatives

Neither catalogued sibling (CPath, reckless) targets line-by-line file reading, so this is the only io-and-filesystem entry solving that specific std::ifstream problem; pick it only if the workload is Windows-only line iteration and the GPL-3.0 license, ATL dependency, and unterminated-newline bug are all acceptable.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | WinAPI (CreateFile/CreateFileMapping/MapViewOfFile) and ATL (atlbase.h, for CHandle) |
| **Minimum toolchain** | Visual Studio 2019, PlatformToolset v142 per FastReader.vcxproj; uses std::iterator&lt;&gt; as an iterator base, which is deprecated in C++17 and removed in C++20, so it will not compile unmodified under /std:c++20 |
| **Platforms** | Windows x86 and x64 (Win32 and x64 configs in the vcxproj); WinAPI-dependent, no POSIX path |
| **Thread safety** | not documented; raw pointers with no locking around Open/Close/iteration |
| **Drop-in for the baseline** | partial — explain: same job (iterate lines of a file) but different construction (wide-char path only), a different exception type (CWin32Error, not stream fail state), and no seek/write/formatted-extraction API |

## Gotchas

- Unterminated final line (no trailing '\n') triggers memchr returning nullptr, which the code adds 1 to unchecked, producing an invalid pointer instead of a clean end-of-file marker
- Copy constructor and assignment are deleted with no move alternative provided, so CFileHandler cannot be stored in most STL containers directly
- CFileHandlerIterator::operator\* allocates a new std::string per line, so iteration is not zero-copy despite the memory-mapped backing
- Requires ATL (atlbase.h) solely for CHandle's RAII wrapper around HANDLE, pulling in more than a plain WinAPI call would need

## Caveats and trade-offs

The numbers come from one execution of a small Google Test timing test (mean of 10 samples x 3 passes over a \~9 KB file), with no stated CPU and no stated build configuration. A Debug build of the MSVC STL would inflate the std::ifstream time. The library is Windows-only (WinAPI memory mapping), so the baseline is the MSVC STL's std::ifstream. Small single-maintainer project with no commits since November 2019.

Windows-only (WinAPI-based); narrower API than std::ifstream (line iteration only, wide-char paths); GPL-3.0 is copyleft, which may be unsuitable for proprietary use.

## Maintenance

Abandoned since 2019-11-13 (single maintainer, no open issues or PRs, 5 stars); GPL-3.0 plus the ATL dependency make it copyable only into GPL-compatible, Windows-with-ATL projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Test results' block shows CFileHandler 56700 ns vs std::ifstream 241000 ns from the public Google Test code in FastReaderTest/test.cpp. It states no CPU, no build configuration (Debug /Od vs Release) and no flags, so it is first-party with partial methodology: C.
- **Verifier notes:** The numbers match the README. The 'almost 5 times' wording is from the GitHub repo description, not the README. The workload is tiny (9 KB file) and the build configuration is unknown, so treat the 4.25x as weak evidence. The metadata (GPL-3.0, 5 stars, last commit 2019-11-13) is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `baseline_stdlib`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/GeorgiiFirsov/FastReader>
  - <https://github.com/GeorgiiFirsov/FastReader#test-results>
  - <https://github.com/GeorgiiFirsov/FastReader/blob/master/FastReaderTest/test.cpp>
  - <https://github.com/GeorgiiFirsov/FastReader/blob/master/FastReaderTest/FastReaderTest.vcxproj>
  - <https://github.com/GeorgiiFirsov/FastReader/blob/master/FastReader/FileHandler.cpp>
- **Sources the enricher read:**
  - <https://github.com/GeorgiiFirsov/FastReader>
  - <https://github.com/GeorgiiFirsov/FastReader#test-results>
  - <https://github.com/GeorgiiFirsov/FastReader/blob/master/FastReader/FileHandler.h>
  - <https://github.com/GeorgiiFirsov/FastReader/blob/master/FastReader/FileHandler.cpp>
  - <https://github.com/GeorgiiFirsov/FastReader/blob/master/FastReaderTest/test.cpp>
  - <https://github.com/GeorgiiFirsov/FastReader/blob/master/FastReader/FastReader.vcxproj>
  - <https://github.com/GeorgiiFirsov/FastReader/blob/master/FastReader/stdafx.h>
  - <https://github.com/GeorgiiFirsov/FastReader/issues>
  - <https://github.com/GeorgiiFirsov/FastReader/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/georgiifirsov/fastreader`) · [data/wave1/enrich/raw/github_com_georgiifirsov_fastreader.json](../../../data/wave1/enrich/raw/github_com_georgiifirsov_fastreader.json) (enrichment confidence 0.55)

</details>
