# displaywidth

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Go monospace display-width and truncation library; 1.6-3.3x faster than go-runewidth v0.0.23 in its own benchmarks, zero allocations.

| | |
|---|---|
| **Beats** | mattn/go-runewidth (the common Go terminal display-width library) and rivo/uniseg; ICU, HarfBuzz and FreeType are not involved |
| **Claimed result** | README / comparison/README.md go test -bench output (Apple M2, darwin/arm64), displaywidth vs go-runewidth vs uniseg: String_Mixed 6085 vs 9970 vs 19060 ns/op; String_EastAsian 6118 vs 13917 vs 19263 ns/op; String_ASCII 54.54 ns/op (2347 MB/s) vs 125.5 ns/op (1020 MB/s) vs 1478 ns/op; String_Emoji 3265 vs 5110 vs 7137 ns/op; Rune_EastAsian 3454 vs 11432 ns/op; Rune_ASCII 255.5 vs 264.7 ns/op; TruncateWithTail 2495 vs 4569 ns/op; TruncateWithoutTail 2456 vs 5182 ns/op; 0 allocs except the with-tail truncation (14 allocs on both sides). Speedups over go-runewidth (derived from page data): 1.64x mixed strings, 2.27x East Asian, 2.30x ASCII, 1.57x emoji, 3.31x East Asian runes, 1.04x ASCII runes (parity), 1.83x and 2.11x truncation. |
| **Workload** | Measuring monospace display width of Go strings, bytes and runes on mixed, East Asian, ASCII and emoji text, plus truncate-to-width with and without a tail. |
| **Metric** | throughput |
| **Hardware** | Apple M2 (darwin/arm64) |
| **Compiler and flags** | go test -bench=. -benchmem in comparison/ with default gc build flags; the Go toolchain version is not stated (root go.mod declares go 1.18, but the pinned go-runewidth v0.0.23 declares go 1.23, so the comparison needs Go 1.23 or later) |
| **Adoption** | 19 stars |
| **Last commit** | 2026-05-17 |
| **Links** | [repository](https://github.com/clipperhouse/displaywidth) · [benchmark](https://github.com/clipperhouse/displaywidth) |

## Verdict

go test -bench in comparison/ on an Apple M2 (darwin/arm64), Go version unstated, numbers refreshed in the 2026-04-18 'update versions & benches' commit, against go-runewidth v0.0.23 and rivo/uniseg v0.4.7 in their default configurations. Results: about 1.7 KB of mixed test strings 6085 vs 9970 vs 19060 ns/op; the same with East Asian Ambiguous wide 6118 vs 13917 vs 19263; East Asian runes 3454 vs 11432; truncation 2495 vs 4569 (with tail) and 2456 vs 5182 (without). Reading the harness: both sides do equivalent default work, but go-runewidth's opt-in CreateLUT fast path was not enabled; its default condition follows the runner's locale; its Truncate scans the string twice; and on the emoji set (flags, VS16 emoji) the libraries return different widths. The numbers predate PR #24 (2026-05-17, VS16 rewrite, about 1% per the PR) and go-runewidth v0.0.24-v0.0.30. Record correction: go-runewidth v0.0.23's go.mod declares go 1.20; go 1.23 is its current HEAD.

## Use it when

- Go TUIs and CLI tables that measure or truncate many short cells per frame. lipgloss v2, charmbracelet/x/ansi (v0.11.0) and olekukonko/tablewriter (v0.10.0) already depend on it in their go.mod files.
- ASCII-heavy text: 54.5 ns vs 125.5 ns for 128 bytes over five strings against go-runewidth v0.0.23 (2.3x), and 27x faster than rivo/uniseg.
- Strings carrying ANSI SGR colour codes: Options.ControlSequences counts escape sequences as zero width, and TruncateString keeps trailing escapes so colours do not bleed.
- Emoji-heavy output where flags, keycaps and VS16 emoji should take 2 cells, matching Ghostty, iTerm and VS Code per the author's compatibility notes.
- Allocation-sensitive hot paths: String, Bytes, Rune and TruncateString without a tail report 0 allocs/op.

## Skip it when

- Before re-benchmarking against a current go-runewidth. The comparison pins v0.0.23 (2026-04-08). v0.0.24 (2026-05-29) added a precomputed East Asian width table, v0.0.28 a lazily built full-range lookup table, and v0.0.30 (2026-09-10) a rune fast path in StringWidth and Truncate. The README numbers have not been re-run, so the 2.3-3.3x East Asian gaps may have shrunk.
- Code that uses go-runewidth's Wrap, FillLeft, FillRight or TruncateLeft helpers, which have no displaywidth equivalent.
- Thai and similar text: a cluster's width comes from its leading rune, so Thai clusters ending in SARA AM (U+0E33) measure 1 where terminals draw 2 (issue #25, open since 2026-10-01).
- Layouts that must match macOS Terminal or existing go-runewidth output exactly. Here flags and keycaps are 2 cells and VS16 forces 2, while go-runewidth gives 1, and the author notes Mac Terminal draws flags as 1.
- Proportional-font text layout or shaping. It counts monospace cells only: no bidi, no line breaking, no font metrics.

## How it is fast

Width properties live in a generated multi-stage trie indexed directly by UTF-8 bytes, in the style of x/text/internal/triegen (trie.go: about 16 KB of values plus a 1.9 KB index). It returns a one-byte bitmap (zero-width, wide, ambiguous, VS16-eligible) without decoding runes. Runs of printable ASCII are counted by a plain byte loop that skips grapheme segmentation entirely; the changelog says 2-10x faster on ASCII than v0.7.0. Other text goes through the clipperhouse/uax29 grapheme iterator, and each cluster costs one trie lookup on its leading rune, plus an IndexByte scan for VS16. The code is generic over string and []byte and allocates nothing. The go-runewidth v0.0.23 baseline instead binary-searches interval tables per rune (up to three tables in East Asian mode), and its Truncate measures the whole string before a second cutting pass.

## Compared with alternatives

Among the catalog's terminal-width siblings, pick displaywidth for Go code that wants grapheme-aware widths, ANSI-aware truncation and the library the Charm stack (lipgloss v2, x/ansi) and tablewriter already pull in. uniwidth's numbers are against the older go-runewidth v0.0.19 on an EPYC in CI, so the two cannot be ranked from catalog data. uwcwidth is the Python counterpart and not an alternative for Go.

## Integration

| | |
|---|---|
| **Form** | module (pure-Go package) |
| **Dependencies** | github.com/clipperhouse/uax29/v2 v2.7.0 (grapheme segmentation, same author) |
| **Minimum toolchain** | Go 1.18 per go.mod (generics); CI tests Go 1.20-1.25 with -race. The comparison module needs Go 1.20+, because the pinned go-runewidth v0.0.23 declares go 1.20. |
| **Platforms** | any GOOS/GOARCH (no assembly; the published benchmark ran on darwin/arm64) |
| **Thread safety** | Stateless functions over read-only generated tables, and Options is passed by value, so concurrent calls need no locking. Thread safety is not explicitly documented, and DefaultOptions is an exported mutable package variable. |
| **Drop-in for the baseline** | partial: equivalent functions under different names (String vs StringWidth, Rune vs RuneWidth, TruncateString vs Truncate). East Asian Ambiguous width is not read from the locale or RUNEWIDTH_EASTASIAN as go-runewidth does at init. Results differ on flags, keycaps and VS16 sequences, and there are no Wrap or Fill helpers. |

## Gotchas

- EastAsianWidth defaults to false and is never set from the environment. Code moved from go-runewidth on a CJK locale silently changes ambiguous characters from 2 to 1 cells unless you set Options.EastAsianWidth yourself.
- Invalid UTF-8 is not validated and its results are undefined; the code is fuzzed only against panics and infinite loops. ControlSequences8Bit treats C1 bytes 0x80-0x9F, which are also UTF-8 continuation bytes, as escapes, and Truncate ignores that option.
- Width is taken per grapheme cluster from the leading rune, so measuring rune by rune (Rune) gives different and usually wrong totals for combining sequences, ZWJ emoji and flags. The README itself warns against it.
- Unicode 17 tables are compiled in (v0.9.0). Width changes arrive with library upgrades, as with v0.5.0's VS15 change and PR #24's narrower VS16 rule in May 2026, so pin the version if column layout must stay stable.

## Known shortcomings

- Go library (language-filter mismatch); display-width primitive, not shaping. README numbers match the public comparison/benchmark_test.go (Apple M2), Go toolchain version unstated; baseline go-runewidth is the Go-ecosystem incumbent and now uses the same author's uax29 segmenter.
- Benchmarks are stale: the baseline is pinned to go-runewidth v0.0.23 (2026-04-08) and v0.0.24 to v0.0.30 (May to September 2026) added a precomputed East Asian table, a lazy full lookup table and rune fast paths, so the 2.3-3.3x gaps may have shrunk; runewidth's opt-in CreateLUT is unused and its default follows the locale. The emoji row returns different widths (flags, VS16) and the numbers predate PR #24's VS16 fix (2026-05-17, about 1%). Open issue #25: Thai SARA AM clusters measure 1 instead of 2. The go-runewidth v0.0.23 go.mod says go 1.20 (1.23 is HEAD).

## Caveats and trade-offs

First-party benchmark; code is public (comparison/benchmark_test.go) and the CPU is named, but the Go toolchain version is not, and the README run is undated. Both sides do the same work (string/rune display width with default or East-Asian-ambiguous-wide settings, truncation to the same widths over the same test_cases.txt and string sets). go-runewidth now uses clipperhouse/uax29 (by the same author as displaywidth) for grapheme segmentation, so the gap comes mostly from width lookup, not segmentation. The baselines are Go libraries; go-runewidth (about 720 stars, the de facto Go terminal-width library) is a recognisable incumbent within Go, but ICU, HarfBuzz and FreeType are not involved. Display width is a text-layout primitive, not shaping. No C++ implementation is involved.

Uses Unicode trie lookups from clipperhouse/uax29; README says outputs match go-runewidth and uniseg for most real-world text but differ on some edge cases (East Asian ambiguous width, emoji sequences).

## Maintenance

Active: v0.11.0 is the latest changelog release, the last commit is 2026-05-17 and one issue is open. MIT, small and pure Go with a single dependency, and already used by lipgloss v2, charmbracelet/x/ansi and tablewriter.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README and comparison/README.md carry go test -bench output against mattn/go-runewidth v0.0.23 and rivo/uniseg v0.4.7 (pinned in comparison/go.mod), produced by the public comparison/benchmark_test.go, with the CPU named (Apple M2, darwin/arm64). The Go toolchain version is not stated anywhere, so it falls short of A; first-party only, so C (same as other Go entries with an unstated toolchain).
- **Verifier notes:** Numbers match the README byte for byte; benchmark code calls displaywidth.String/Rune/TruncateString against runewidth.StringWidth/RuneWidth/Truncate and uniseg.StringWidth on identical inputs. MIT license, not a fork, not archived, 19 stars, last commit 2026-05-17 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/README.md>
  - <https://github.com/clipperhouse/displaywidth>
  - <https://github.com/clipperhouse/displaywidth/tree/main/comparison>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/comparison/benchmark_test.go>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/comparison/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/comparison/go.mod>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/comparison/go.sum>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/go.mod>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/LICENSE>
  - <https://github.com/clipperhouse/displaywidth/commits/main>
  - <https://github.com/mattn/go-runewidth>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/HEAD/go.mod>
- **Sources the enricher read:**
  - <https://github.com/clipperhouse/displaywidth>
  - <https://github.com/clipperhouse/displaywidth/commits/main>
  - <https://github.com/clipperhouse/displaywidth/issues?q=is%3Aissue>
  - <https://github.com/clipperhouse/displaywidth/issues/25>
  - <https://github.com/clipperhouse/displaywidth/pull/24>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/go.mod>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/go.sum>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/width.go>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/options.go>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/graphemes.go>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/truncate.go>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/trie.go>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/.github/workflows/gotest.yml>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/.github/workflows/gofuzz.yml>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/testdata/test_cases.txt>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/testdata/testdata.go>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/comparison/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/comparison/benchmark_test.go>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/comparison/go.mod>
  - <https://raw.githubusercontent.com/clipperhouse/displaywidth/HEAD/comparison/COMPATIBILITY_ANALYSIS.md>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/v2.7.0/go.mod>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/v0.0.23/runewidth.go>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/v0.0.23/README.md>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/v0.0.23/go.mod>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/HEAD/go.mod>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/HEAD/runewidth.go>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/HEAD/README.md>
  - <https://github.com/mattn/go-runewidth/commits/master>
  - <https://github.com/mattn/go-runewidth/tags>
  - <https://raw.githubusercontent.com/charmbracelet/lipgloss/HEAD/go.mod>
  - <https://raw.githubusercontent.com/charmbracelet/x/HEAD/ansi/go.mod>
  - <https://raw.githubusercontent.com/olekukonko/tablewriter/HEAD/go.mod>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/clipperhouse/displaywidth`) · [data/wave10/enrich/raw/github_com_clipperhouse_displaywidth.json](../../../data/wave10/enrich/raw/github_com_clipperhouse_displaywidth.json) (enrichment confidence 0.8)

</details>
