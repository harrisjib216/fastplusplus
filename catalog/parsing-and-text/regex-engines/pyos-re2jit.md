# re2jit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> JIT-compiles RE2's NFA to x86-64 machine code; beats RE2 on capture groups and Unicode classes.

| | |
|---|---|
| **Beats** | RE2 |
| **Claimed result** | Exactly as fast as RE2 for simple unanchored search with discarded groups (falls back to RE2's own DFA); 20-30% faster than RE2 when capture-group boundaries must be reported; up to 100x faster than RE2 on patterns using full Unicode character classes (e.g. \pL), because re2jit matches a whole code point via a 2-stage lookup table instead of RE2's enumerated-alternation expansion. |
| **Workload** | Repo-bundled perf tests: a small Markdown-to-HTML converter using two regexes with capture groups (make test/32-markdownish), and a tokenizer for the 'dg' language whose pattern relies on a Unicode class equivalent to \w (make test/30-long), comparing re2jit's JIT-compiled Thompson-NFA-to-x86-64 approach against google/re2 directly. |
| **Metric** | throughput |
| **Adoption** | 8 stars |
| **Last commit** | 2016-11-25 |
| **Links** | [repository](https://github.com/pyos/re2jit) · [benchmark](https://github.com/pyos/re2jit/blob/master/README.md) |

## Verdict

First-party README benchmarks (no CPU model, compiler, flags, or absolute timings given) claim re2jit matches RE2's speed on unanchored non-capturing search (shared DFA), runs 20-30% faster than RE2 when capture-group boundaries are needed (test/32-markdownish, a two-regex Markdown-to-HTML converter), and up to 100x faster than RE2 on patterns using Unicode property classes like \pL (test/30-long, a tokenizer for the 'dg' language), all measured against google/re2 directly with no C++ stdlib comparison.

## Use it when

- Capture groups whose boundaries must be reported, on x86-64 Linux/macOS.
- Patterns using full Unicode property classes (\pL, \p{Lu}, etc.) in a hot loop, especially against older RE2 versions.
- Backreference-heavy patterns where no backreferenced group is itself repeated, needing guaranteed polynomial (not exponential) time.
- You're willing to vendor an abandoned, single-maintainer MIT source-drop rather than depend on a maintained package.
- You can build RE2 as a git submodule/static lib yourself; no package manager integration exists.

## Skip it when

- Need \b/\B word-boundary matching — not implemented at all, not even as an error.
- Non-x86-64 targets — falls back to a slower VM interpreter (ENABLE_VM=1) with no real speed benefit.
- Comparing against a current RE2 release — the author's own README says newer RE2 closed much of the Unicode-charclass gap, so the up-to-100x figure is likely stale.
- Regexes with a repeated backreferenced group (e.g. (x\*)\*\1) — exponential time, the standard backreference pitfall.
- Anything you'd call production-critical — no commits since 2016, no CI evidence found, and the README literally ends with 'don't use this thing either way.'

## How it is fast

Two techniques: an x86-64 assembler DSL (asm64.h) plus a converter (it.x64.cc) turn Thompson-NFA thread stepping into native opcodes in mmapped executable memory, skipping RE2's VM dispatch loop when capture positions must be reported; and a rewriter (rewriter.h) replaces RE2's per-codepoint alternation expansion of Unicode classes (\pL, \p{Lu}, etc.) with a generated 2-stage lookup table, turning a many-branch match into a table lookup. For simple unanchored, non-capturing search it just defers to RE2's DFA, so there's no regression there.

## Compared with alternatives

Among the catalogued RE2-beating siblings (rejit, BLARE), pick re2jit specifically when the bottleneck is \p{X} Unicode-class matching or capture-group boundary reporting on x86-64 Linux/macOS — that's its one distinctly measured edge. rejit and BLARE report broader RE2 speedups and don't share re2jit's missing \b/\B support, so prefer them for general-purpose replacement.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | google/re2 (git submodule, built to obj/libre2.a) |
| **Minimum toolchain** | C++11, g++-compatible CXX; Python 3 to regenerate unicodedata.h |
| **Platforms** | x86-64 (Linux/macOS and similar 64-bit UNIX); other architectures only via a slower VM interpreter (ENABLE_VM=1) |
| **Thread safety** | not documented beyond an internal std::atomic cache for named_groups(); no stated guarantee for concurrent match() calls on one it instance |
| **Drop-in for the baseline** | partial — separate re2jit::it class mirrors RE2::Match's Anchor/StringPiece signature but isn't a subclass or ABI-compatible replacement for RE2 |

## Gotchas

- Reserves Unicode plane-15 private-use code points (roughly U+F0000-U+F0FFF) for internal use; matching against them is unsupported.
- \b/\B word boundaries are silently absent rather than erroring.
- Unanchored search with backreferences can't use RE2's DFA fallback, so it's slow by a large constant, independent of algorithmic complexity.
- Perf figures come only from two repo-bundled programs (test/30-long, test/32-markdownish, built with ENABLE_PERF_TESTS=1); no independent benchmark exists.

## Known shortcomings

- The author's own README warns against using it in production.

## Caveats and trade-offs

First-party README claim with no CPU model, compiler, flags, or absolute timings (only ranges plus 'run this make target yourself'; perf tests are test/30-long.cc and test/32-markdownish.cc). Abandoned since 2016-11-25 (tagged, not excluded). The author's README notes newer re2 versions 'significantly improved Unicode charclass performance', so the up-to-100x figure is likely stale against current RE2. x86-64 only, \b/\B unsupported, and the README closes with 'don't use this thing either way.'

x86-64 only (hand-written asm64 DSL that JIT-compiles into mmapped executable memory); does not implement \b/\B word boundaries at all; reserves Unicode plane-15 private-use code points internally. Backreferences are supported with a guaranteed-linear-time fast path when no backreferenced group is repeated, exponential otherwise (same as general backreference semantics).

## Maintenance

Abandoned since its last commit on 2016-11-25, and the README itself says 'don't use this thing either way' — but it's MIT-licensed, depends only on RE2, and small enough to vendor if you just want the Unicode-charclass lookup-table trick.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** README gives only first-party ranges vs RE2 (same speed / 20-30% / up to 100x) pointing at repo perf tests test/32-markdownish.cc and test/30-long.cc (make ... ENABLE_PERF_TESTS=1), with no timings, compiler, flags, or CPU; the &gt;50x figure with unstated flags also caps it at C.
- **Verifier notes:** All three claimed figures appear verbatim in the README and are vs google/re2 directly. Metadata (MIT, 8 stars, last commit 2016-11-25, abandoned) matches gh; only caveats extended with the author's own disclaimers.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pyos/re2jit>
  - <https://github.com/pyos/re2jit/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/pyos/re2jit>
  - <https://github.com/pyos/re2jit/blob/master/README.md>
  - <https://github.com/pyos/re2jit/blob/master/re2jit/it.h>
  - <https://github.com/pyos/re2jit/blob/master/Makefile>
  - <https://github.com/pyos/re2jit/blob/master/.gitmodules>
  - <https://github.com/pyos/re2jit/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/pyos/re2jit`) · [data/wave3/enrich/raw/github_com_pyos_re2jit.json](../../../data/wave3/enrich/raw/github_com_pyos_re2jit.json) (enrichment confidence 0.35)

</details>
