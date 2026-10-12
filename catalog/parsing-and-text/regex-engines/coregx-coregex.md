# coregex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Drop-in Go regexp replacement using 17 pattern-specific engines and SIMD prefilters; beats Rust regex on literal-heavy patterns only.

| | |
|---|---|
| **Beats** | Rust regex |
| **Claimed result** | Per kolkov/regex-bench README (coregex v0.12.23, FindAll, 6.0 MB input, GitHub Actions AMD EPYC): faster than Rust regex on 6 of 16 patterns: inner_literal 52x (0.26 ms vs 13.55 ms), ip 17.6x, suffix 7.7x, multiline_php 2.0x, char_class 1.4x, version 1.2x. SLOWER than Rust regex on 8 of 16: email 2.1x, uri 1.8x, literal_alt 7.4x, http_methods 2.4x, multi_literal 2.4x, alpha_digit 2.2x, word_digit 2.2x, word_repeat 3.2x. About the same on the 2 anchored patterns. Against Go stdlib regexp: 3.6x-893x on the same patterns. |
| **Workload** | Cross-language benchmark (kolkov/regex-bench) on a 6.0 MB generated text file across 16 real-world patterns (inner literal, IP address, email, URI, multiline PHP path, version string, suffix, literal alternation, HTTP methods, multi-literal, char class, word-repeat, anchored), using FindAll for a fair cross-engine comparison |
| **Metric** | throughput |
| **Hardware** | AMD EPYC (GitHub Actions Ubuntu runner) |
| **Compiler and flags** | Go 1.23 with default go build; Rust stable toolchain (dtolnay/rust-toolchain@stable), regex crate 1.11, cargo build --release with lto = true, codegen-units = 1 (per .github/workflows/benchmark.yml and rust/Cargo.toml in kolkov/regex-bench) |
| **Adoption** | 261 stars |
| **Last commit** | 2026-09-06 |
| **Links** | [repository](https://github.com/coregx/coregex) · [benchmark](https://github.com/kolkov/regex-bench) |

## Verdict

On kolkov/regex-bench's cross-language corpus (6.0 MB generated text, 16 real-world patterns, FindAll, coregex v0.12.23, Rust regex 1.11 built with --release/LTO/codegen-units=1, Go 1.23, on a GitHub Actions AMD EPYC runner), coregex beat Rust regex on 6 of 16 patterns (1.2x-52x: version, char_class, multiline_php, suffix, ip, inner_literal), lost on 8 of 16 (1.8x-7.4x slower: uri, alpha_digit, word_digit, http_methods, multi_literal, email, word_repeat, literal_alt), and tied on 2 anchored patterns. Against Go stdlib regexp it was 3.6x-893x faster on all 16 patterns.

## Use it when

- Pattern has an extractable literal (suffix like .\*\.log, inner substring like .\*error.\*, an IP/digit run, or an anchored prefix): reverse-DFA/prefilter paths ran 1.2x-52x faster than Rust regex on kolkov/regex-bench.
- Migrating a Go codebase off stdlib regexp for CPU-bound matching where the 100%-API-compatible surface (per docs/STDLIB_COMPATIBILITY.md) avoids a rewrite.
- Deploying on amd64 with AVX2/SSSE3 available (the benchmark ran on a GitHub Actions AMD EPYC runner); SIMD prefilters only exist on that architecture.
- A zero-allocation hot loop over many matches: AllIndex/AppendAllIndex iterators are up to 30% faster than FindAll per the README.
- Multi-pattern literal alternation (foo|bar|baz, roughly 2-64 literals) handled by the Teddy or Aho-Corasick engines.

## Skip it when

- Pattern is alternation-heavy without a literal anchor, has bounded-repeat groups, or is a plain character class: coregex was 1.8x-7.4x slower than Rust regex on 8 of 16 kolkov/regex-bench patterns (email, uri, literal_alt, http_methods, multi_literal, alpha_digit, word_digit, word_repeat).
- Backreferences are required: not supported (by design, to keep the O(n) guarantee) — use regexp2 instead.
- Target is not amd64: SIMD paths are disabled and it falls back to pure Go, so the Rust-beating numbers do not apply there.
- Toolchain is older than what the module requires: go.mod pins `go 1.27.1`, while the README's stated minimum ("Go 1.25+") is lower and inconsistent with go.mod — verify against your own Go version before adopting.
- Correctness-sensitive code relying on stdlib's exact empty-match positions or repeated-capture-group semantics: docs/STDLIB_COMPATIBILITY.md lists these as unresolved known differences, and the tracker shows a steady stream of matching bugs (dot-vs-codepoint, anchors, negated classes, case-insensitivity) fixed between Dec 2025 and Mar 2026.

## How it is fast

At compile time it extracts required literals (prefix, suffix, inner substring, digit runs) and routes to an engine built for that shape instead of one generic NFA: SIMD memchr/memmem (AVX2/SSSE3) for single-literal search, Slim/Fat Teddy or Aho-Corasick for multi-literal alternation, and reverse (right-to-left) DFA search for suffix/inner-literal patterns that skips most of the input entirely. Patterns without a strong literal anchor fall back to LazyDFA, PikeVM, OnePass, or BoundedBacktracker.

## Compared with alternatives

It's the only catalogued regex engine targeting Go; the other siblings (nim-regex, rejit, SafeRE, BLARE, RE#, nanoregex, re2jit) are for Nim, C++/RE2, Java, .NET, and Python. Pick coregex specifically when you're on Go stdlib regexp and your patterns are literal-anchored (suffix/inner/prefix); the siblings aren't options in a Go codebase.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys, github.com/coregx/ahocorasick (per go.mod) |
| **Minimum toolchain** | go.mod declares `go 1.27.1`; README separately claims "Go 1.25+" — the two disagree, go.mod is the binding constraint for `go build` |
| **Platforms** | amd64 with AVX2/SSSE3 for SIMD prefilters; other architectures use a pure-Go fallback (per the record's tradeoffs field, not independently verified this session on non-amd64) |
| **Thread safety** | compiled \*Regexp is safe for concurrent use by multiple goroutines, using an internal sync.Pool for per-search state (per README) |
| **Drop-in for the baseline** | partial — 100% of the stdlib regexp API is implemented (docs/STDLIB_COMPATIBILITY.md), but documented behavioral differences remain in empty-match counts/positions, repeated capture-group results, and some combined-flag case-insensitive edge cases |

## Gotchas

- Repeated capture groups like (a)\* can capture a different iteration than stdlib's "last match" behavior (docs/STDLIB_COMPATIBILITY.md).
- Empty-match count and position can differ from stdlib on patterns such as [a-c]\*, .\*, ^ — documented as an open, unresolved difference.
- No backreference support at all; RE2-syntax only.
- Two open performance issues on the tracker at verification time: #153 (FindAllStringIndex slower than stdlib in some cases) and #120 (Teddy SIMD 8.6x slower than Rust due to Go/assembly call-boundary overhead).

## Caveats and trade-offs

kolkov/regex-bench is maintained by coregex's top contributor (kolkov), so it is a first-party benchmark despite being a separate repo. Hardware is a shared GitHub Actions runner reported only as 'AMD EPYC' (no model), and the README warns that results vary by +/-30% between runs. coregex is slower than Rust regex on 8 of 16 patterns. The widely quoted '3-3000x' headline is against Go stdlib regexp on no-match edge cases, not against Rust regex.

Requires Go 1.25+; AVX2/SSSE3 SIMD paths are AMD64-only with a pure-Go fallback elsewhere; results are pattern-dependent, winning on literal-prefilterable patterns and losing on alternation-heavy or bounded-repeat patterns compared to Rust's mature Teddy/DFA implementation

## Maintenance

Actively maintained (last commit 2026-09-06), MIT-licensed, 261 stars; the issue tracker shows a fast-closing but frequent stream of correctness bugs fixed between Dec 2025 and Mar 2026, indicating a young engine rather than one battle-hardened over years like Rust regex.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party cross-language benchmark (kolkov/regex-bench, by coregex's top contributor). Code and build flags are public, but hardware is only 'AMD EPYC' on a shared GitHub Actions runner with no CPU model, so C.
- **Verifier notes:** The numbers match the README table. The record said 'slower on 7 of 16' but listed 8 patterns; the table shows 8 slower, 6 faster and 2 the same. The Rust version and build flags ARE stated in the repo (regex 1.11, release, LTO), so that caveat was corrected. Metadata (MIT, 261 stars, last commit 2026-09-06) verified.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kolkov/regex-bench>
  - <https://github.com/kolkov/regex-bench/blob/main/rust/Cargo.toml>
  - <https://github.com/kolkov/regex-bench/blob/main/.github/workflows/benchmark.yml>
  - <https://github.com/coregx/coregex>
- **Sources the enricher read:**
  - <https://github.com/coregx/coregex>
  - <https://github.com/coregx/coregex/blob/main/go.mod>
  - <https://github.com/coregx/coregex/issues>
  - <https://github.com/coregx/coregex/blob/main/docs/STDLIB_COMPATIBILITY.md>
  - <https://github.com/kolkov/regex-bench>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/coregx/coregex`) · [data/wave3/enrich/raw/github_com_coregx_coregex.json](../../../data/wave3/enrich/raw/github_com_coregx_coregex.json) (enrichment confidence 0.55)

</details>
