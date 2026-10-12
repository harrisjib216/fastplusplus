# fast_io

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `Anti-Tivo License (ATL) v1.0 (custom, non-OSI-approved)` · 🟢 active

> Header-only C++20 I/O library replacing iostream/cstdio and std::to_chars with buffered, syscall-near I/O.

| | |
|---|---|
| **Beats** | iostreams (std::fstream); std::to_chars (MSVC, for double formatting) |
| **Claimed result** | 10M integers written to a file and read back. MinGW-W64 GCC 11: fstream 0.462s output / 1.192s input vs fast_io i/obuf_file 0.049s / 0.081s (\~9.4x / \~14.7x), measured with libstdc++ BUFSIZ modified by the author. Linux GCC 11: fstream with the sputc trick 0.319s / 0.429s vs 0.050s / 0.065s (\~6.3x / \~6.6x). MSVC 19.26: fstream 3.635s / 3.842s vs 0.063s / 0.103s (\~57x / \~37x). Against std::to_chars+obuf_file for integer output: \~2.3-2.6x (e.g. Linux 0.115s vs 0.050s). 10M doubles, Ryu round-trip, MSVC 19.26 only: fast_io 0.4654s vs std::to_chars(charconv)+obuf_file 0.6011s. That is \~22.6% less time (\~1.29x throughput), matching the readme's claim of 'over 20%'. |
| **Workload** | Writing and re-reading 10 million sequential integers to/from a file, and separately writing 10 million doubles with round-trip Ryu-based formatting, measured in wall-clock seconds, against std::fstream/stdio/boost::iostreams and, for the double case, MSVC's std::to_chars. |
| **Metric** | throughput |
| **Compiler and flags** | MinGW-W64 GCC 11.0.0; MSVC 19.26.28805; GCC 11.0.0 with glibc+libstdc++ (Linux); optimization flags not stated in the tables |
| **Adoption** | 851 stars |
| **Last commit** | 2026-07-02 |
| **Links** | [repository](https://github.com/cppfastio/fast_io) · [benchmark](https://github.com/cppfastio/fast_io/blob/master/readme.md) |

## Verdict

Author-run benchmarks (no CPU model or optimization flags stated) show fast_io's buffered file I/O beating std::fstream by roughly 6-15x for writing/reading 10 million integers on GCC 11 (Linux and MinGW-W64) and MSVC 19.26, and beating MSVC's std::to_chars(charconv) by about 23% (\~1.29x throughput) for round-trip formatting of 10 million doubles, also on MSVC 19.26.

## Use it when

- Bulk sequential file I/O (writing/reading millions of integers or lines) where std::fstream or stdio throughput is the bottleneck.
- Already on C++20 with a concepts-capable compiler (GCC&gt;=14, Clang&gt;=17, or MSVC per current support.md) and able to adopt a non-drop-in API.
- Low-level, embedded, kernel-driver, or freestanding/WASM targets that need direct handle/syscall-level I/O and small binaries (readme's static-link comparison: 155KB fast_io vs 925KB fstream).
- Need Unicode-aware (UTF-8/16/32) transcoding I/O in the same layer as raw throughput.
- Can accept the Anti-Tivo License's non-standard terms in exchange for the speed.

## Skip it when

- Need a true drop-in replacement for std::iostream or std::to_chars without touching call sites — fast_io's API shape and exceptions-only error model differ substantially.
- Legal review requires an OSI-approved permissive or conventional copyleft license — Anti-Tivo License v1.0 is custom and not OSI-approved.
- Toolchain can't reach the current minimum (GCC&gt;=14/Clang&gt;=17 per support.md), which is notably newer than the GCC 11/MSVC 19.26 used in the readme's own benchmark numbers.
- Need independently reproduced numbers before adopting — all published results are the author's own, with no CPU model or optimization flags stated, and the readme's cited benchmark paths no longer exist in the reorganized benchmark/ directory.
- Multithreaded writers by default — the fast unbuffered types are not thread-safe; the thread-safe \*_mutex variants give up much of the speed edge (readme: 0.049s to 0.146s output time on MinGW for the mutex variant).

## How it is fast

Devices are abstracted through C++20 concepts (static polymorphism), avoiding the vtable dispatch, locale machinery, and sentry-object overhead that &lt;iostream&gt;/streambuf carry on every call. I/O goes through the library's own buffered file objects close to the raw syscall/native-handle level rather than through libc FILE\* layering. Integer formatting uses the jeaiii digit-pair method (include/fast_io_core_impl/integers/jeaiii_method.h, the same technique as the jeaiii/itoa sibling entry). Double round-trip formatting is implemented in include/fast_io_unit/floating/roundtrip.h, whose header comment attributes the algorithm to 'Dragonbox' (Jk Jeon) even though the readme's benchmark section calls it the 'Ryu algorithm' — these are different, related fast float-to-string algorithms.

## Compared with alternatives

Pick fast_io over Boost.Charconv, c4core, fast_double_parser, rigtorp/CharConv, or jeaiii/itoa when the goal is whole-file/stream I/O throughput via buffered file objects and syscall-near handles, not just isolated number&lt;-&gt;string conversion — those siblings only replace to_chars/from_chars/stoi/strtod, while fast_io replaces the entire iostream/cstdio layer (and internally reuses jeaiii's itoa method for its own integer formatting).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for core I/O (single fast_io.h entry header); optional interop code exists for Boost, Qt, MFC, OpenSSL, LLVM raw_fd_ostream, Lua/Python bindings |
| **Minimum toolchain** | C++20 with concepts; per support.md: GCC&gt;=14, Clang&gt;=17, or MSVC (readme's own benchmarks were run on the older GCC 11.0.0 and MSVC 19.26.28805) |
| **Platforms** | x86/x86_64, arm/aarch64, riscv/riscv64, powerpc64, mips variants, wasm32-wasi, avr, ia64, loongarch64, xtensa-esp32, and more per support.md; Windows/Linux/BSD/Darwin/iOS/Android, Cygwin/MSYS2/Wine/ReactOS, plus freestanding, kernel-driver, and bootloader targets |
| **Thread safety** | Default buffered types (e.g. obuf_file) are not thread-safe; explicit \*_mutex variants (obuf_file_mutex, c_file) add thread safety at a measured throughput cost in the readme's own benchmarks |
| **Drop-in for the baseline** | partial — explain: constructs from and interoperates with FILE\*/iostream objects for gradual adoption, but the print/scan API and exceptions-only error model are a different interface from &lt;iostream&gt;/std::to_chars, not a drop-in replacement |

## Gotchas

- readme's cited benchmark source paths (benchmarks/0000.10m_size_t/unit, benchmarks/0001.10m_double/charconv) do not exist in the current repo; benchmark/ has been reorganized into numbered dirs (e.g. 0002.file_io_tsc, 0004.file_io_floating).
- readme calls the double round-trip formatting the 'Ryu algorithm', but the implementation header (include/fast_io_unit/floating/roundtrip.h) is commented 'Algorithm: Dragonbox, Author: Jk Jeon' — a different, related algorithm.
- MinGW benchmark numbers required the author to patch libstdc++'s BUFSIZ from 512 bytes to 1MB before comparing against fstream; the out-of-the-box gap on stock MinGW would be smaller.
- License is the custom Anti-Tivo License v1.0 (non-OSI-approved, GitHub reports it as NOASSERTION) — review it before shipping, it is not a standard permissive or copyleft license.

## Caveats and trade-offs

No CPU model or optimization flags are stated for any table, only the OS and compiler versions. The benchmark source paths cited in the readme (benchmarks/0000.10m_size_t/unit, benchmarks/0001.10m_double/charconv) are missing from the current repo, which has a reorganized benchmark/ directory. For the MinGW run, the author modified libstdc++'s BUFSIZ. The numbers are the author's own readme claims, not reproduced independently. The MSVC fstream gap (\~57x) is far larger than the Linux gap (\~6x). The license is custom and not OSI-approved (Anti-Tivo License v1.0, with fallback to GPLv3 under some conditions).

Uses a non-standard, non-OSI-approved 'Anti-Tivo License' with unusual conditional-GPLv3 clauses rather than a conventional permissive/copyleft license; large paradigm shift from &lt;iostream&gt; (not a drop-in replacement, requires C++20 concepts); the original repository was archived once already due to git history bloat.

## Maintenance

Actively maintained (last commit 2026-07-02 on the 'next' branch, 2026-03-13 on master); usability is capped at 'reference' because of the non-OSI Anti-Tivo License, not because of code immaturity — 851 stars and an extensive examples/benchmark/fuzzing tree.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The readme gives compiler versions but no optimization flags and no hardware. The benchmark paths it cites (benchmarks/0000.10m_size_t/unit, benchmarks/0001.10m_double/charconv) are missing from the current repo, which has a reorganized benchmark/ directory instead. The MSVC fstream gap is &gt;50x with flags unstated. Any one of these rules out A and caps the tier at C. The prior tier B was invalid because the numbers are the author's own.
- **Verifier notes:** The license was confirmed from license.txt (Anti-Tivo License v1.0, custom, not OSI-approved, GitHub reports NOASSERTION), so usability stays 'reference'. last_commit 2026-07-02 is the 'next' branch. The default branch (master) last commit is 2026-03-13. Both are active, so the field was left unchanged. The record's integer comparisons left out the larger MSVC fstream gap and the direct std::to_chars integer comparison. Both are now added.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cppfastio/fast_io>
  - <https://github.com/cppfastio/fast_io/blob/master/readme.md>
  - <https://github.com/cppfastio/fast_io/blob/master/license.txt>
  - <https://github.com/cppfastio/fast_io/tree/master/benchmark>
  - <https://github.com/cppfastio/fast_io/tree/master/benchmark/0004.file_io_floating>
  - <https://github.com/cppfastio/fast_io/tree/master/benchmark/0002.file_io_tsc>
- **Sources the enricher read:**
  - <https://github.com/cppfastio/fast_io>
  - <https://github.com/cppfastio/fast_io/blob/master/readme.md>
  - <https://github.com/cppfastio/fast_io/blob/master/support.md>
  - <https://github.com/cppfastio/fast_io/blob/master/CMakeLists.txt>
  - <https://github.com/cppfastio/fast_io/blob/master/include/fast_io_unit/floating/roundtrip.h>
  - <https://github.com/cppfastio/fast_io/tree/master>
  - <https://github.com/cppfastio/fast_io/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/cppfastio/fast_io`) · [data/wave1/enrich/raw/github_com_cppfastio_fast_io.json](../../../data/wave1/enrich/raw/github_com_cppfastio_fast_io.json) (enrichment confidence 0.6)

</details>
