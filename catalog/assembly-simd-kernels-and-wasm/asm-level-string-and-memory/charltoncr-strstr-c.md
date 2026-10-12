# strstr.c (Ron Charlton)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `CC0-1.0` · 🟢 active

> 15-line public-domain scalar C strstr; author reports it ties or beats 18 variants, libc included, on English text.

| | |
|---|---|
| **Beats** | The compiler's C library strstr (rows 0, 9 and 17 of Competitors/strstrFunctions.c are labelled 'Compiler library strstr'; rows 9 and 17 replaced the SunOS and Boyer-Moore-Horspool versions). The library is not named; comments in the competitor file mention macOS clang (2023-05-01), so it was probably Apple's libc, not glibc or musl. |
| **Claimed result** | README: 'tied for speed with its nearest competitor among 18 diverse strstr implementations' when finding English words in English text; 'Its other competitors are between 10.5% and 348% slower.' The README also says it 'is faster in many cases' than the C Standard Library's strstr. |
| **Workload** | Finding English words in English text with a 15-line strchr-style strstr, compared with 18 other strstr implementations (BSD, GNU coreutils 5.3.0, Plauger, Moore, Visual C, compiler libraries). |
| **Metric** | throughput |
| **Compiler and flags** | Not stated (competitor-file comments mention macOS clang; no flags given) |
| **Adoption** | 3 stars |
| **Last commit** | 2026-06-21 |
| **Links** | [repository](https://github.com/charltoncr/strstr.c) · [benchmark](https://github.com/charltoncr/strstr.c/blob/main/README.md) |

## Verdict

Only author prose, with no harness, corpus list, CPU, compiler or flags published. Searching English words in English text (the competitor file mentions mobyThesaurus.txt), it ties GNU coreutils 5.3.0's strstr (within 0.5% on English and French text and word lists), and 17 other versions, including the compiler's library strstr (probably Apple's libc under macOS clang), are 10.5% to 348% slower. The author also reports that strchr-based versions are about 6.5x faster than it when the needle's first character is rare.

## Use it when

- Short English-like needles (single words) searched in short to medium natural-language text, the workload the author timed.
- Freestanding, embedded or toy-libc builds that lack strstr or ship a naive one (SunOS-style strlen-per-step or strncmp-per-position versions), where 15 lines of CC0 code are easy to vendor.
- When you need a strstr that never reads past either string's terminator and has no SIMD block reads, for example under strict sanitizers or on unusual memory maps.
- Hot loops with many tiny haystacks, where the setup work of two-way or Horspool-style library strstr (strlen, strnlen, shift tables) dominates.

## Skip it when

- Long haystacks where the needle's first character is rare: the author's own competitor-file note says the versions that call the library's SIMD strchr are about 6.5x faster than the others, this one included. glibc's generic strstr also starts with strchr, and x86-64 glibc selects __strstr_sse2_unaligned on CPUs with fast unaligned loads.
- Adversarial or repetitive inputs (for example, a run of 'a' searched for 'aaa...ab'): the scan-and-compare loop is O(n\*m), while glibc's strstr is linear (short-needle special cases, a bigram-hash Horspool for needles up to 256 bytes, Two-Way beyond) and musl uses dedicated 2-, 3- and 4-byte searches plus Two-Way.
- When you need evidence of a speedup on your platform: the only numbers are README prose against an unnamed libc (probably macOS, from 2023 comments in the competitor file), with no harness, CPU, compiler or flags.
- C++17 or later translation units: the code uses the register storage class, which C++17 removed (clang rejects it by default), so compile it as C or delete the keyword.

## How it is fast

It is a naive first-character scan: a strchr-like loop unrolled by two finds the needle's first byte, checks for the terminator on every byte, and then compares the rest of the needle byte by byte. If that fails it resumes one byte after the candidate. It has no setup cost (no strlen of the needle, no shift table, no strncmp call), which pays off on short haystacks and short English words where most first-byte hits fail within a character or two. There is no SIMD or word-at-a-time scanning.

## Compared with alternatives

Pick it over WojciechMula/toys strstr (SWAR and SIMD Rabin-Karp, needs SSE/AVX-class hardware for its gains, no published results) or AOCL-LibMem's Zen-tuned strstr when you need a dependency-free, portable, public-domain scalar fallback and your workload is short-word search in natural-language text. For long haystacks on x86-64, a SIMD sibling or the platform libc will usually win.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (includes &lt;string.h&gt; only for declarations) |
| **Minimum toolchain** | C99 (uses // comments); compile as C, not C++17, because of 'register' |
| **Platforms** | any (portable byte-at-a-time C) |
| **Thread safety** | Reentrant pure function with no state; safe from any thread |
| **Drop-in for the baseline** | partial: same signature and semantics as strstr, but the file defines the reserved name strstr itself. Rename it (for example strstr_rc) and call it explicitly; otherwise the compiler may treat calls as the builtin, and in a dynamically linked ELF program the definition interposes over libc's strstr for every shared library too. |

## Gotchas

- Defining a function named strstr is undefined behaviour in ISO C (reserved external identifier). With GCC or Clang, calls with constant arguments may be folded or turned into strchr/libc calls by builtin handling, so benchmark it under a different name or with -fno-builtin-strstr.
- After a partial match runs into the end of the haystack it does not stop early; it keeps scanning byte by byte from the next position. That is correct but wasted work on near-miss tails.
- Licence wording differs: LICENSE.md and the header text say CC0 1.0, but the header links the Public Domain Mark URL. CC0 has no patent grant, and Competitors/strstrFunctions.c contains GPL-2.0+ (coreutils) and unlicensed USENET code that is not covered.
- The competitor file contradicts itself on strchr. Its header credits the library's SIMD strchr for a 6.5x win on rare first characters, while a 2023-05-01 note on strstr7 says calling macOS clang's strchr 'is slower here', so how the library strstr was built and called in the timings is unclear.

## Known shortcomings

- No harness and no per-competitor numbers; the library strstr is unnamed (probably macOS clang); naive O(n\*m) worst case; CC0 (no patent grant) while the competitors file holds GPL-2.0+ code.
- Enricher: no harness in the repo, README prose only; defines the reserved name strstr (undefined behaviour, builtin folding and ELF interposition risks); 'register' is invalid in C++17; O(n\*m) worst case against glibc's linear bigram Horspool/Two-Way and musl's Two-Way; the author's own file says SIMD-strchr variants are 6.5x faster on rare first characters and the competitor file contradicts itself on strchr.

## Caveats and trade-offs

Repo holds only strstr.c and the competitor sources (Competitors/strstrFunctions.c); there is no timing harness, test corpus list, per-competitor table, CPU model, compiler or flags, so the result is not reproducible and the library strstr's own margin is never stated separately. The competitor-file header says that when the first pattern character is rare, versions that call the library's SIMD strchr (strstr7, 8, 15, 16) are about 6.5 times faster than the others (strstr1 included), so the claim holds for English-word searches and may lose to a SIMD libc strstr elsewhere. The algorithm is a naive first-character scan plus compare, O(n\*m) in the worst case, unlike the linear two-way strstr in glibc and musl. The nearest competitor is GNU coreutils 5.3.0 strstr (Stephen R. van den Berg, GPL-2.0+), not current glibc. Licence: LICENSE.md says CC0 1.0 for strstr.c (no patent grant), but the file header links the Public Domain Mark URL; the Competitors file contains GPL-2.0+ and unlicensed USENET code and is not covered.

Plain C, no SIMD or table setup; 15 executable lines, public domain (CC0, no patent grant). Its inner loop is an unrolled strchr-like scan, so it relies on nothing platform specific.

## Maintenance

Small CC0 file, last touched 2026-06-21 (README wording only; the code was reverted to the 'original fast code' on 2024-02-29 after two tuning attempts). It has 3 stars, no issues and no tests, but is trivial to vendor under a non-reserved name.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Only the author's README prose gives numbers (tied with the nearest competitor, others 10.5% to 348% slower, the compiler library strstr being row 0 of the competitor list); there is no timing harness, no per-competitor table, and no compiler, flags or CPU, so first-party numbers without methodology.
- **Verifier notes:** README numbers quoted correctly; the competitor file confirms strstr1 and strstr20 (GNU coreutils 5.3.0) within 0.5% on English and French text. Tier C stays, low confidence: no harness or methodology, unnamed libc (probably macOS), naive worst-case algorithm, 3 stars. Metadata checked: CC0-1.0 via LICENSE.md, last commit 2026-06-21, active.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-28 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/charltoncr/strstr.c>
  - <https://github.com/charltoncr/strstr.c/commits>
  - <https://github.com/charltoncr/strstr.c/tree/main/Competitors>
  - <https://raw.githubusercontent.com/charltoncr/strstr.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/charltoncr/strstr.c/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/charltoncr/strstr.c/HEAD/strstr.c>
  - <https://raw.githubusercontent.com/charltoncr/strstr.c/HEAD/Competitors/strstrFunctions.c>
- **Sources the enricher read:**
  - <https://github.com/charltoncr/strstr.c>
  - <https://github.com/charltoncr/strstr.c/commits>
  - <https://github.com/charltoncr/strstr.c/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/charltoncr/strstr.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/charltoncr/strstr.c/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/charltoncr/strstr.c/HEAD/strstr.c>
  - <https://raw.githubusercontent.com/charltoncr/strstr.c/HEAD/Competitors/strstrFunctions.c>
  - <https://raw.githubusercontent.com/bminor/glibc/master/string/strstr.c>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/x86_64/multiarch/strstr.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/string/strstr.c>
  - https://raw.githubusercontent.com/bminor/musl/master/src/string/strstr.c (404)
  - https://raw.githubusercontent.com/apple-oss-distributions/Libc/main/string/FreeBSD/strstr.c (404)
  - https://raw.githubusercontent.com/apple-oss-distributions/Libc/HEAD/string/FreeBSD/strstr.c (404)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/charltoncr/strstr.c`) · [data/wave13/enrich/raw/github_com_charltoncr_strstr_c.json](../../../data/wave13/enrich/raw/github_com_charltoncr_strstr_c.json) (enrichment confidence 0.6)

</details>
