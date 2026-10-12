# rawscan

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0 OR MIT OR GPL-2.0 (author's choice; PCG code in generate_input_data.c is Apache-2.0)` · 🟡 stale

> Small Linux C line reader over a raw fd; about 30-40% less user CPU than fgets or getline on large inputs.

| | |
|---|---|
| **Beats** | fgets, getline (glibc stdio) |
| **Claimed result** | User CPU: rawscan 1.60s vs fgets 2.61s vs getline 2.36s vs grep 4.38s (30-40% less CPU than fgets/getline) |
| **Workload** | Read an 11.2GB file of 55.6M lines already in RAM, matching a hex prefix per line |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 1700, input file (11.27 GB, 55,626,370 lines) already in RAM, average of 10 runs under nice -n-10 |
| **Adoption** | 6 stars |
| **Last commit** | 2024-09-25 |
| **Links** | [repository](https://github.com/ThePythonicCow/rawscan) · [benchmark](https://github.com/ThePythonicCow/rawscan) |

## Verdict

First-party README: on a Ryzen 1700 with an 11.27 GB, 55.6M-line file already in the page cache, user CPU (mean of 10 runs, nice -n-10) was 1.60 s for rawscan versus 2.61 s for glibc fgets, 2.36 s for getline and 4.38 s for grep, matching the prefix '6fffbf42'. Only user CPU is reported, not wall time; the committed harness (source/tests) compares rawscan with a hand-inlined 3-byte compare and min1stchunklen=3 against fgets/getline using strncmp, and builds getline_test without the -march=native flag the others get, so the gap includes harness differences.

## Use it when

- Linux/glibc command-line filters that scan very large files line by line and do little work per line (prefix match, field split), where per-line reader overhead dominates.
- Inputs with untrusted or unbounded line lengths: the buffer never grows, so a giant line is returned in chunks instead of exhausting memory as getline's realloc can.
- Records with embedded nul bytes or a non-newline delimiter (e.g. find -print0 output), which fgets handles badly.
- Code that can work on (begin, end) byte spans without nul-terminated copies.

## Skip it when

- Anything multi-threaded on one stream: the README says a RAWSCAN stream must be used by a single thread.
- Non-Linux or non-glibc targets: it needs rawmemchr, sbrk/brk and mprotect; the CMake port to BSD, macOS, Windows, clang and MSVC is untested by the author.
- Long-lived programs that open many streams: rs_open grows the data segment with brk(2) and rs_close is an empty function, so each stream's buffer plus two pages is never freed.
- Programs where the line reader is not the bottleneck, or where Rust's bstr is an option: the author reports bstr is as fast or faster and only matched it with hand-written inline compare code.
- Projects needing maintenance or a track record: version 0.1.4, 6 stars, last commit 2024-09-25, no issues filed.

## How it is fast

It bypasses stdio's double buffering by calling read(2) straight into its own buffer and returns pointers into it, copying only when a partial line must be shifted down (memmove). Delimiter search uses glibc's vectorized rawmemchr, made safe by placing a copy of the delimiter in a read-only sentinel page just past the buffer and writing a delimiter after each read's end, so the scan never needs a length check. The hot path is a small inline function that returns the pre-computed next delimiter position and peeks the following one; rawscan_static.h compiles everything into the caller's unit (10% faster than the shared library on 8-byte lines, no difference at 512+ bytes per the README).

## Compared with alternatives

None of the catalogued filesystems-and-io siblings is a line reader: liburing and SPDK speed up the I/O submission path, and diskus, gdu and fclones are whole tools. Pick rawscan when the cost is splitting already-cached data into lines in a single-threaded C filter; combine it with a faster I/O layer only if reads, not scanning, dominate.

## Integration

| | |
|---|---|
| **Form** | shared lib (librawscan.so via CMake) or header-only (include rawscan_static.h) |
| **Dependencies** | glibc (rawmemchr, sbrk/brk, mprotect, sysconf) |
| **Minimum toolchain** | C11 (anonymous union in rawscan.h), CMake 3.13; developed with GCC; library built with -O3 -march=native |
| **Platforms** | Linux x86-64 tested; other systems not tested |
| **Thread safety** | Not thread-safe per stream (README); rs_open also calls brk, which is not safe while other threads use malloc |
| **Drop-in for the baseline** | no |

## Gotchas

- rs_open allocates with sbrk/brk behind malloc's back and asserts the current break is page-aligned; man brk(2) advises against mixing these calls with malloc, and the asserts vanish under NDEBUG (CMake Release adds it).
- Returned line pointers are invalidated by the next rs_getline when the buffer is shifted or refilled; use rs_enable_pause / rs_resume_from_pause if you need them to live longer.
- Line end points at the delimiter byte (inclusive), and lines are not nul-terminated; a final line without a delimiter comes back as rt_full_line_without_eol.
- The read count is stored in an int, so buffers above 2 GiB are not safe.

## Known shortcomings

- Harness asymmetry: rawscan_test uses a hand-inlined 3-byte compare with min1stchunklen=3 while fgets_test and getline_test use strncmp, and getline_test is built without -march=native; it is unknown which code version produced the 1.60 s figure. Design flaws: rs_open allocates with brk/sbrk behind malloc's back, rs_close is empty (every buffer leaks), the read count is stored in an int (unsafe above 2 GiB). Library flags from CMake: -O3 -march=native.

## Caveats and trade-offs

User CPU time only, not wall time; compiler and flags not stated; first-party measurement. The author says Rust bstr is faster on this case and only beat it with hand-coded inline code. grep row excludes about 10% of runs that took about 7.10 s. Uses glibc rawmemchr with a read-only sentinel page, so it is Linux/glibc oriented. Not thread-safe per stream.

Zero-copy pointers into an internal buffer; relies on rawmemchr and sentinel page; Linux/glibc oriented.

## Maintenance

Stale since 2024-09-25 and a self-described learning project at v0.1.4, but about 1,000 lines of C under Apache-2.0, MIT or GPL-2.0 at the user's choice, so it is easy to vendor and fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README table gives user CPU seconds (grep 4.38, fgets 2.61, getline 2.36, rawscan 1.60) on a Ryzen 1700, averages of 10 runs, with a harness in source/tests (random_line_generator.c, compare_various_apis.sh); compiler and flags are not stated, so first-party with partial methodology is C.
- **Verifier notes:** LICENSE.md offers Apache-2.0, MIT or GPLv2 at the user's choice, so usability moves to copyable. Last commit 2024-09-25 (stale) confirmed on the commits page; 6 stars, not archived.
- **Fields the verifier corrected:** `license`, `usability`, `hardware`, `caveats`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/ThePythonicCow/rawscan>
  - <https://github.com/ThePythonicCow/rawscan/commits>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/README.md>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/LICENSE.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/README.md>
  - <https://github.com/ThePythonicCow/rawscan/tree/master/source>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/source/include/rawscan.h>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/source/include/rawscan_static.h>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/source/lib/rawscan.c>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/source/CMakeLists.txt>
  - <https://github.com/ThePythonicCow/rawscan/tree/master/source/tests>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/source/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/source/tests/fgets_test.c>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/source/tests/getline_test.c>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/source/tests/rawscan_test.c>
  - <https://raw.githubusercontent.com/ThePythonicCow/rawscan/HEAD/source/tests/rawscan_static_test.c>
  - <https://github.com/ThePythonicCow/rawscan/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/thepythoniccow/rawscan`) · [data/wave11/enrich/raw/github_com_thepythoniccow_rawscan.json](../../../data/wave11/enrich/raw/github_com_thepythoniccow_rawscan.json) (enrichment confidence 0.7)

</details>
