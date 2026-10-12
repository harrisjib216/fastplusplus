# uwcwidth

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Cython (Python)` · `MIT` · 🟡 stale

> Cython wcwidth/wcswidth for Python with Unicode 16 emoji rules; beats pure-Python wcwidth 0.2.13 by 18-42x on short strings.

| | |
|---|---|
| **Beats** | jquast/wcwidth, the standard Python terminal-width package, which was pure Python when measured (most likely 0.2.13, the only wcwidth release between January 2024 and September 2025 per PyPI); cwcwidth, a Cython binding to the C library's wcwidth/wcswidth, was also measured; neither version is stated |
| **Claimed result** | README IPython %%timeit of wcswidth('コンニチハ, セカイ!'): wcwidth 1.73 us, cwcwidth 211 ns, uwcwidth 41 ns (about 42x and 5.1x, derived from page data); README heading '40x faster than wcwidth'. Enricher re-measurement on Linux (glibc 2.39, Python 3.11.15, Xeon 2.1 GHz VM, 2026-10-04): uwcwidth 87-89 ns, wcwidth 0.2.13 1,623 ns (18x), cwcwidth 0.1.9 49-52 ns (uwcwidth 1.7x slower), current wcwidth 0.9.1 (C extension) 183-186 ns (2.1x; 4.5x faster than uwcwidth on ASCII text). |
| **Workload** | wcswidth of the 11-codepoint string 'コンニチハ, セカイ!' (full-width katakana plus ASCII) in IPython %%timeit, 7 runs of 10^6 or 10^7 loops; that one string is the whole benchmark. |
| **Metric** | latency |
| **Compiler and flags** | Not stated for the timing. The package is a Cython extension built with -O3 on non-MSVC compilers and with no extra flags under MSVC (setup.py). Python, wcwidth and cwcwidth versions are not stated. |
| **Adoption** | 4 stars |
| **Last commit** | 2024-10-28 |
| **Links** | [repository](https://github.com/Z4JC/uwcwidth) · [benchmark](https://github.com/Z4JC/uwcwidth) |

## Verdict

The README times wcswidth on one 11-code-point katakana and ASCII string with IPython %%timeit: wcwidth 1.73 us, cwcwidth 211 ns, uwcwidth 41 ns. No CPU, OS or versions are given, but the wcwidth timing fits the pure-Python 0.2.13 of 2024. Re-run in this session on an Intel Xeon 2.1 GHz cloud VM (Linux, glibc 2.39, CPython 3.11.15, best of 7), the numbers were uwcwidth 1.0.0 87-89 ns, wcwidth 0.2.13 1,623 ns (18x, not 42x), wcwidth 0.9.1 183-186 ns (2.1x), and cwcwidth 0.1.9 49-52 ns and 0.1.12 63-67 ns. So on Linux, uwcwidth is about 1.7x slower than cwcwidth, not 5x faster, though cwcwidth gets ZWJ sequences wrong; the README's cwcwidth ratio is presumably specific to the libc of its unstated platform.

## Use it when

- Python TUIs, table printers and log formatters that measure many short, emoji-heavy or CJK strings and still depend on pure-Python wcwidth 0.2.x.
- When ZWJ sequences, flags, keycaps and skin-tone modifiers must count as 2 cells: in this session cwcwidth on glibc 2.39 returned 11 and 6 for the README's edge-case strings, against 8 and 5 from uwcwidth.
- Cython code that can cimport wcswidth and call it without Python-call overhead (ugrapheme does this for ljust, rjust and center).
- Projects that want a tiny, dependency-free MIT module whose widths do not depend on the platform libc or locale.

## Skip it when

- You already run wcwidth 0.3 or later: 0.9.1 ships a C extension, and in this session it was only 2.1x slower on the README string, 1.9x slower on 1,750 characters of mixed text, and 4.5x faster on 2,250 ASCII characters (about 1.1 us against 5.0 us).
- Plain ASCII or Latin text measured in long strings: the per-character loop runs at about 2.2 ns per character, slower than wcwidth 0.9.1 and cwcwidth.
- Unicode 17 text, or output that must match wcwidth exactly: it has had no commits since 2024-10-28, and widths differ from wcwidth 0.2.13 on 730 single code points and from 0.9.1 on 5,541 (spacing marks such as U+0903 are 1 here and 0 there; wide code points added in Unicode 17, such as Tangut ideographs and new emoji, and lone regional indicators are 1 here and 2 in 0.9.1).
- C or C++ callers: it is a CPython/PyPy extension. Its musl-derived tables and loop are short enough to port, and the catalogued Go siblings displaywidth and uniwidth do the same job in Go.
- Platforms without wheels (CPython 3.14+, Linux aarch64): pip falls back to building the sdist with Cython and a C compiler.

## How it is fast

Width comes from musl libc's two-level sparse bitmaps (a 256-entry page index, then 32-byte bit pages) for zero-width and wide code points, recomputed for Unicode 16.0, plus a dense bitmap for Emoji_Modifier_Base; the tables total about 4 KB. Code points below U+00FF take one arithmetic test, and planes 2-3 return 2 without a lookup. The whole loop is a typed Cython function that reads code points straight from the str with no per-character Python objects, while wcwidth 0.2.13 runs a Python while-loop that binary-searches its tables per character behind an lru_cache.

## Compared with alternatives

displaywidth and uniwidth are the catalogued Go terminal-width libraries and beat go-runewidth there. uwcwidth is the Python counterpart, worth taking when a CPython or Cython codebase needs emoji-sequence-aware widths without the jquast wcwidth package or a libc-dependent binding such as cwcwidth.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime; Cython, setuptools and a C compiler only when building from source |
| **Minimum toolchain** | CPython 3.8+ or PyPy 3.7-3.10 (1.0.0 wheels cp38-cp313 and pp37-pp310 for x86-64/i686 manylinux and musllinux, Windows and macOS arm64); built with -O3 on non-MSVC compilers |
| **Platforms** | any platform with a C compiler; prebuilt wheels as listed, none for Linux aarch64 |
| **Thread safety** | Not documented; the functions keep no state, only read static lookup tables and run while holding the GIL. |
| **Drop-in for the baseline** | partial — wcwidth(char) and wcswidth(str, n=None) match wcwidth 0.2.x names and the -1 convention, but there is no unicode_version argument, no ambiguous-width option, no width/ljust/wrap helpers from wcwidth 0.3+, and widths differ on hundreds to thousands of code points |

## Gotchas

- Any narrow character followed by VS16 (U+FE0F) becomes width 2, even when it has no emoji presentation: wcswidth('a\ufe0f') is 2 here and 1 in wcwidth.
- A ZWJ (U+200D) swallows the next code point and one trailing skin-tone modifier or VS16 whatever they are, so '\u200dabc' measures 2; wcwidth 0.2.13 behaves the same.
- Tabs, newlines, ESC and other controls make wcswidth return -1 for the whole string (closed issue #1), so strip ANSI escapes and expand tabs first. Unicode noncharacters such as U+FFFE also return -1, where wcwidth returns 1.
- wcswidth(s, n) with n greater than len(s) raises IndexError, as wcwidth 0.2.13 did; wcwidth 0.9.1 clamps and returns the width.

## Known shortcomings

- Cython (language-filter mismatch); display-width primitive, not shaping. One IPython %%timeit string: wcwidth 1.73 us vs uwcwidth 41 ns (about 42x) and cwcwidth 211 ns (5.1x, derived), with no CPU, Python or wcwidth version and no bench script; the gain is mostly Cython -O3 against the pure-Python wcwidth of 2024, and wcwidth 0.9.1 now ships a C11 core with abi3 wheels, unmeasured. Last commit 2024-10-28.
- README ratios are stale and platform-specific (retier-26): re-measured on Linux, uwcwidth is 18x faster than pure-Python wcwidth 0.2.13 (not 42x), 1.7x slower than cwcwidth 0.1.9 (not 5x faster; cwcwidth is wrong on ZWJ sequences), and only 2.1x faster than the current wcwidth 0.9.1 C extension, which beats uwcwidth 4.5x on ASCII text. Widths differ from wcwidth on 730 (0.2.13) or 5,541 (0.9.1) code points; VS16 widens any narrow character. The author of issue #1 ported uwcwidth to Node.js (duplicate if found).

## Caveats and trade-offs

The 40x comes from one short string with no CPU, OS or Python version, and the numbers are first-party. Most of the 40x is the gap between a compiled Cython extension (uwcwidth.pyx, -O3) and the pure-Python wcwidth of 2024. The like-for-like compiled comparison is cwcwidth, which uwcwidth beats by about 5x. cwcwidth's widths come from the platform libc, so its Unicode coverage varies by system. The baseline has since moved: wcwidth is at 0.9.1 (2026), describes itself as a Python and C11 library and ships platform abi3 wheels, and that version was not measured, so the 40x should be treated as stale. Semantics differ slightly. uwcwidth uses Unicode 16.0 (draft) tables derived from musl's wcwidth, skips the codepoint after a ZWJ unconditionally and forces width 2 on VS16. It returns -1 for control characters, as wcwidth does. The tests do not compare outputs against wcwidth. Terminal cell width is a text-layout primitive rather than shaping, and the baseline is a Python package, not HarfBuzz, FreeType or ICU. [retier] README ratios do not reproduce on Linux: 18x against pure-Python wcwidth 0.2.13 and 2.1x against the C-extension wcwidth 0.9.1 (which beats uwcwidth 4.5x on ASCII); cwcwidth is faster than uwcwidth but wrong on ZWJ sequences. Widths differ from wcwidth on 730 (0.2.13) or 5,541 (0.9.1) code points; VS16 widens any narrow character.

Cython wrapper over about 4 KB of bitmap lookup tables derived from musl libc; covers Unicode 16.0 emoji with VS15/VS16 and ZWJ; width only, no grapheme segmentation (use ugrapheme for that).

## Maintenance

Stale since its 1.0.0 release on 2024-10-28 (4 stars, 4 commits, no open issues) and still at Unicode 16.0, but it is about 80 lines of MIT-licensed Cython plus musl-derived tables, so it is easy to vendor or port; its speed advantage now holds mainly against pure-Python wcwidth 0.2.x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README section 'Performance: 40x faster than wcwidth' shows one IPython %%timeit session on one string: wcwidth 1.73 us, cwcwidth 211 ns, uwcwidth 41 ns. It names no CPU and no Python, wcwidth or cwcwidth versions, and the repo holds no benchmark script (only tests/test_uwcwidth.py). These are first-party numbers without methodology, which is C.
- **Verifier notes:** Language: Cython compiled to a CPython C extension, used from Python; the orchestrator may want language 'Cython' rather than 'Python'. wcwidth (jquast) is the recognisable incumbent for terminal width in Python. baseline_in_list stays false, and the entry belongs in font-shaping-text-layout as a text-layout primitive, not shaping. Metadata checked: MIT (portions from musl, also MIT), 4 stars, not a fork, last commit 2024-10-28, so stale is correct.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Z4JC/uwcwidth>
  - <https://github.com/Z4JC/uwcwidth/commits>
  - <https://github.com/Z4JC/uwcwidth/tree/main/uwcwidth>
  - <https://github.com/Z4JC/uwcwidth/tree/main/tests>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/README.md>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/setup.py>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/uwcwidth/uwcwidth.pyx>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/tests/test_uwcwidth.py>
  - <https://pypi.org/pypi/uwcwidth/json>
  - <https://pypi.org/pypi/cwcwidth/json>
  - <https://pypi.org/pypi/wcwidth/json>
- **Sources the enricher read:**
  - <https://github.com/Z4JC/uwcwidth>
  - <https://github.com/Z4JC/uwcwidth/issues?q=is%3Aissue>
  - <https://github.com/Z4JC/uwcwidth/issues/1>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/README.md>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/uwcwidth/uwcwidth.pyx>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/uwcwidth/uwcwidth.pxd>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/uwcwidth/tables.pxd>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/uwcwidth/__init__.py>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/uwcwidth/__init__.pxd>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/tests/test_uwcwidth.py>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/setup.py>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Z4JC/uwcwidth/HEAD/LICENSE>
  - <https://pypi.org/pypi/uwcwidth/json>
  - <https://pypi.org/pypi/cwcwidth/json>
  - <https://pypi.org/pypi/wcwidth/json>
  - https://pypi.org/project/uwcwidth/ (1.0.0 wheel installed into the scratch directory and run in this session)
  - https://pypi.org/project/cwcwidth/ (0.1.9 and 0.1.12 wheels installed into the scratch directory and timed)
  - https://pypi.org/project/wcwidth/ (0.2.13 and 0.9.1 wheels installed into the scratch directory, timed and diffed over all code points)
  - wcwidth 0.2.13 wcwidth/wcwidth.py (from the PyPI wheel installed in the scratch directory)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/z4jc/uwcwidth`) · [data/wave10/enrich/raw/github_com_z4jc_uwcwidth.json](../../../data/wave10/enrich/raw/github_com_z4jc_uwcwidth.json) (enrichment confidence 0.8)

</details>
