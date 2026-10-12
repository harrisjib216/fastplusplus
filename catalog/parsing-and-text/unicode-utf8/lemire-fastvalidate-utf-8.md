# fastvalidate-utf-8

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0 OR BSL-1.0 OR MIT` · 🟡 stale

> Header-only C99 SSE/AVX2 UTF-8 validator (2018) that validates at 0.45-0.7 cycles/byte versus about 11 for a branchy scalar loop.

| | |
|---|---|
| **Beats** | scalar C UTF-8 validator (validate_utf8 in benchmarks/benchmark.c, copied in part from Guava, with an ASCII fast path) |
| **Claimed result** | Random-looking UTF-8: 0.702 cycles/byte (SSE validate_utf8_fast) and 0.448 (AVX) vs 10.967 for the scalar validator (about 15.6x and 24.5x, derived from page data). ASCII input: 0.704 and 0.450 vs 1.256 cycles/byte (about 1.8x and 2.8x, derived from page data); the ASCII-path variants reach 0.088. |
| **Workload** | Validating 64 KiB buffers: pure ASCII input and random-looking UTF-8; cycles per input byte. |
| **Metric** | throughput |
| **Hardware** | Intel Skylake processor (exact model not stated) |
| **Compiler and flags** | GCC (version not stated); Makefile: -std=c99 -march=native -O3 -Wall -D_GNU_SOURCE |
| **Adoption** | 309 stars; a modified version sped up Scylla (per README) |
| **Last commit** | 2024-03-13 |
| **Links** | [repository](https://github.com/lemire/fastvalidate-utf-8) · [benchmark](https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/README.md) |

## Verdict

On an unnamed Skylake with GCC (version not stated) and -std=c99 -march=native -O3, best of five rdtsc runs on 64 KiB buffers: random-looking valid UTF-8 took 0.702 cycles/byte (SSE) and 0.448 (AVX2) against 10.967 for the repo's byte-at-a-time Guava-derived scalar validator (about 15.6x and 24.5x), and pure ASCII took 0.704 and 0.450 against 1.256 (about 1.8x and 2.8x). The scalar baseline is not a standard-library function and, as noted, accepts some invalid input.

## Use it when

- Learning or teaching SIMD UTF-8 validation: the SSE validator is about 200 lines of commented C99 intrinsics in one header.
- A C code base on known x86-64 hardware that can only take a single permissively licensed header (Apache-2.0, BSL-1.0 or MIT) and is built with fixed -msse4.1 or -mavx2 flags.
- Bulk yes/no checks of buffers with many multibyte characters (tens of KiB), where a byte-at-a-time validator pays around 11 cycles/byte in branch misses.
- A fast all-ASCII gate before a slower path: validate_ascii_fast_avx ran at 0.05 cycles/byte in the README run.

## Skip it when

- Production use: the README marks the library obsolete since 2022 and for demonstration only, and points to simdutf, which adds runtime CPU dispatch, ARM NEON, AVX-512 and the faster lookup algorithm.
- Any non-x86 target (ARM, POWER, RISC-V): there is no implementation, and there is no runtime dispatch, so a binary built with -mavx2 or -march=native faults on CPUs without that ISA.
- You need the error position, decoding or UTF-16/UTF-32 conversion: the functions return bool only.
- Mostly-ASCII text with the plain SSE function: validate_utf8_fast ran at 0.704 cycles/byte on ASCII, slower than the repo's scalar eight-bytes-at-a-time ASCII check (0.104); use the AVX asciipath variant (0.088) or simdutf instead.
- Short strings: only 64 KiB buffers were benchmarked, and the tail is copied into a zeroed 16- or 32-byte stack buffer on every call; small-input cost is not documented.

## How it is fast

It works on 16 (SSE) or 32 (AVX2) bytes per step. A pshufb lookup on each byte's high nibble gives the expected sequence length, and two shifted saturating subtractions ('carry continuations') spread that length over the following bytes; comparing carried and initial lengths flags missing or extra continuation bytes, while separate vector compares catch bytes above 0xF4, overlong forms (C0/C1, E0 followed by less than A0, F0 followed by less than 90), surrogates (ED followed by more than 9F) and code points above U+10FFFF (F4 followed by more than 8F). Errors are OR-ed into one register across the whole buffer with no data-dependent branches, which removes the branch mispredictions that dominate scalar validators on mixed-length text. This is the 2018 predecessor of the Keiser-Lemire 'lookup' algorithm used in simdjson and simdutf; the paper the README cites describes that later algorithm, not this code.

## Compared with alternatives

Rarely: simdutf (catalogued under encoding) supersedes it on speed, platforms and testing, protobuf's utf8_range (range algorithm) adds NEON and beat a NEON port of this algorithm by about 1.32x in its own tables, and simdutf8 is the Rust choice; pick fastvalidate-utf-8 only for a tiny, readable, permissively licensed C99 x86 header or to study the original carry-continuations technique. In lemire/validateutf8-experiments the same algorithm ported to AVX2 ('basic' rows) ran at 13.1-15.5 GB/s on hongkong.html against 17.1-20.9 GB/s for the later lookup4, and at 6.4 versus 12.2 GB/s on random multibyte input (results/skylake.txt).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (compiler intrinsics via x86intrin.h) |
| **Minimum toolchain** | C99 (designated initializers), GCC or Clang with x86intrin.h; MSVC not documented. SSE path needs SSSE3 and SSE4.1 (pshufb, palignr, ptest); AVX2 variants need __AVX2__; AVX-512 variants need AVX512F+VL+VBMI. Makefile builds with -std=c99 -march=native -O3. |
| **Platforms** | x86-64 only (SSE4.1 minimum; AVX2 and AVX-512 VBMI variants selected at compile time); README says it does not work on ARM |
| **Thread safety** | not documented; the validators are pure functions over the caller's buffer and keep no global state in the headers |
| **Drop-in for the baseline** | partial — same bool validate(const char \*, size_t) shape as the scalar validate_utf8 in the benchmark, but x86-only, chosen per ISA at compile time, and it never exits early on an error |

## Gotchas

- Harness flaw in the baseline: the scalar validate_utf8 in benchmarks/benchmark.c ('copied in part from Guava') ported Java's signed-byte test bytes[i] &gt; (byte)0xBF as an unsigned &gt; 0xBF, so ASCII bytes are accepted as continuation bytes: "\xC3\x28", "\xC2\x7F", "\xE2\x82\x28" and "\xF1AAA" all return true (a faithful Python model of the function misclassifies 3,840 of the 65,536 two-byte inputs, always by accepting invalid ones). tests/unit.c never runs it. On the all-valid benchmark input the timing is not affected, but the baseline is a lenient checker, not a reference validator.
- The random-looking UTF-8 input is half ASCII spaces and half multibyte characters of random length, which maximises scalar branch mispredictions; the 15.6x and 24.5x gaps are a best case, and on mostly-ASCII text the SSE function's lead shrinks to 1.8x (and it loses to a word-at-a-time ASCII skip).
- Current harness defects (after the README numbers): commit c0a5f7e (2024-03-13, issue #27) removed the out-of-bounds data[N] = '\0' write from populate(), but demo() still calls the Hoehrmann DFA validators with N + 1 on a malloc(N) buffer, so those rows now read one uninitialised byte past the allocation; the PR #26 fix for issue #25 scales tv_sec by 1E6 instead of 1E9, so the GB/s print is wrong whenever a run crosses a second boundary. Neither touches the README cycle counts, which predate both the DFA rows (2020) and the GB/s output (2020).
- The 'double' DFA schemes the current benchmark also prints are known not to validate correctly (issue #24, warning printed by the program); ignore those rows.

## Known shortcomings

- README numbers (15.6x/24.5x) are against a Guava-derived scalar validator with no CPU model or GCC version; declared obsolete in 2022 and superseded by simdutf (its successor, already listed); kept as the predecessor record under unicode-utf8.
- Harness flaw in the baseline: the scalar validate_utf8 in benchmarks/benchmark.c ports Guava's signed '&gt; (byte)0xBF' test as an unsigned '&gt; 0xBF', so it accepts ASCII bytes in continuation slots ('\xC3\x28' and '\xF1AAA' return true; a Python model misclassifies 3,840 of 65,536 two-byte inputs), and tests/unit.c never exercises it; the timing on all-valid input is unaffected, but the baseline is not a real validator. Current harness defects: c0a5f7e removed populate's out-of-bounds write, but the DFA rows in demo() still read N + 1 bytes of a malloc(N) buffer; the PR #26 fix scales tv_sec by 1E6 instead of 1E9. Neither touches the README cycle counts.

## Caveats and trade-offs

README marks the library obsolete as of 2022 and says it is for demonstration, not production; simdutf (already catalogued) carries the newer lookup algorithm. Benchmark CPU is named only as Skylake and the GCC version is missing, so tier C. Cycles are rdtsc reference cycles, best of 5 runs on 64 KiB buffers. The only baseline in the README table is a byte-at-a-time Guava-derived scalar validator with an ASCII fast path; the current benchmark.c also times Hoehrmann-style DFA validators (added after issue #24, 2020) whose results are not in the README, so the published table predates the current harness. The ASCII rows favour schemes that skip ASCII quickly (the program prints this); validate_ascii_fast and validate_ascii_fast_avx are ASCII-only checks, not UTF-8 validators. Harness fixes after the README numbers: issue #25 (elapsed seconds mis-scaled, closed 2024-03-13; affects only the time output, not the cycle counts) and issue #27 (populate wrote one byte past the buffer; the current populate no longer does). The two cited lemire.me blog posts (2018) could not be opened. x64 SSE/AVX only, no ARM.

Header-only C; x64 with SSE (and AVX variants) only, no ARM; no runtime dispatch; a demonstration library, not meant for production.

## Maintenance

Stale, self-declared obsolete demonstration code (last commit 2024-03-13, a benchmark-only change); triple-licensed Apache-2.0, BSL-1.0 or MIT and small enough to vendor, but the author directs production users to simdutf.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README 'Experimental results' table (GCC, 'a Skylake processor') matches the record exactly, and the harness is public (benchmarks/benchmark.c, rdtsc best-of-5 via benchmarks/benchmark.h) with Makefile flags -std=c99 -march=native -O3; the CPU model and GCC version are missing, so not A. The Keiser and Lemire SPE 2021 paper the README cites covers the later lookup algorithm (simdjson/simdutf), not this repo's 2018 code, so it does not lift the tier.
- **Verifier notes:** Numbers and derived ratios check out (10.967/0.702 = 15.6x, 10.967/0.448 = 24.5x, 1.256/0.704 = 1.8x, 1.256/0.450 = 2.8x). Not a duplicate: it is the 2018 predecessor of simdutf and the baseline of the catalogued protobuf utf8_range entry; it fits wave 3's unicode-utf8 category better than simd-intrinsics-libraries (category plus domain override if moved). 309 stars, last commit 2024-03-13 (stale), Apache-2.0 OR BSL-1.0 OR MIT (repo root has LICENSE-APACHE, LICENSE-BOOST and LICENSE-MIT).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-77 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/benchmarks/benchmark.c>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/benchmarks/benchmark.h>
  - <https://github.com/lemire/fastvalidate-utf-8>
  - <https://github.com/lemire/fastvalidate-utf-8/commits>
  - <https://github.com/lemire/fastvalidate-utf-8/issues?q=is%3Aissue>
  - <https://github.com/lemire/fastvalidate-utf-8/issues/25>
  - <https://github.com/lemire/fastvalidate-utf-8/issues/27>
  - <https://github.com/lemire/fastvalidate-utf-8/issues/8>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/benchmarks/benchmark.c>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/benchmarks/benchmark.h>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/benchmarks/hoehrmann.h>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/tests/unit.c>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/include/simdutf8check.h>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/include/simdutf8check_avx512.h>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/include/simdasciicheck.h>
  - <https://raw.githubusercontent.com/lemire/fastvalidate-utf-8/HEAD/include/simdasciicheck_avx512.h>
  - <https://github.com/lemire/fastvalidate-utf-8>
  - <https://github.com/lemire/fastvalidate-utf-8/commits>
  - <https://github.com/lemire/fastvalidate-utf-8/commit/c0a5f7e>
  - <https://github.com/lemire/fastvalidate-utf-8/issues?q=is%3Aissue>
  - <https://github.com/lemire/fastvalidate-utf-8/issues/3>
  - <https://github.com/lemire/fastvalidate-utf-8/issues/5>
  - <https://github.com/lemire/fastvalidate-utf-8/issues/8>
  - <https://github.com/lemire/fastvalidate-utf-8/issues/24>
  - <https://github.com/lemire/fastvalidate-utf-8/issues/25>
  - <https://github.com/lemire/fastvalidate-utf-8/issues/27>
  - <https://github.com/scylladb/scylla/commit/6fadba56cc18bebe6648e6aec09be1b0b93f4817>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/src/generic/utf8_fastvalidate_algorithm.h>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/results/skylake.txt>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/lemire/fastvalidate-utf-8`) · [data/wave13/enrich/raw/github_com_lemire_fastvalidate_utf_8.json](../../../data/wave13/enrich/raw/github_com_lemire_fastvalidate_utf_8.json) (enrichment confidence 0.8)

</details>
