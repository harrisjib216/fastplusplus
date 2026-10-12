# uniwidth

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go terminal cell-width library; CI shows 1.1-52x faster StringWidth than go-runewidth v0.0.19, with width bugs on symbols.

| | |
|---|---|
| **Beats** | mattn/go-runewidth v0.0.19 (the de facto Go terminal display-width library) and rivo/uniseg v0.4.7 StringWidth, both pinned in bench/go.mod; HarfBuzz, FreeType and ICU are not involved |
| **Claimed result** | CI three-way comparison on PR #5 (AMD EPYC 7763, linux/amd64, Go 1.25, median of 3 runs), uniwidth vs go-runewidth vs uniseg: StringWidth ASCII short 6.06 vs 73.18 vs 112.2 ns (12.0x / 18.5x); ASCII medium 16.85 vs 625.1 vs 958.1 ns (37.0x / 56.8x); ASCII long 64.08 vs 3,327 vs 5,129 ns (51.9x / 80.0x); CJK short 69.40 vs 156.6 vs 204.7 ns (2.2x / 2.9x); CJK medium 711.2 vs 1,539 vs 1,987 ns (2.1x / 2.7x); mixed short 146.6 vs 255.8 vs 363.9 ns (1.7x / 2.4x); emoji short 151.3 vs 266.6 vs 392.7 ns (1.7x / 2.5x); flags 111.6 vs 232.0 vs 311.5 ns (2.0x / 2.7x); ZWJ 185.1 vs 217.5 vs 486.9 ns (1.1x / 2.6x); TUI table header 548.7 vs 686.0 vs 939.1 ns (1.2x / 1.7x). RuneWidth vs go-runewidth: CJK 2.50 vs 21.97 ns (8.7x), emoji 2.81 vs 13.26 ns (4.7x), ASCII 2.39 vs 2.81 ns (1.1x). The bench/README table (Intel Core i7-1255U, Windows) reports ASCII short 9 vs 107 vs 165 ns, ASCII long 340 vs 5,380 vs 8,058 ns, CJK short 96 vs 347 vs 379 ns, mixed short 173 vs 469 vs 632 ns, emoji short 158 vs 380 vs 534 ns, and ZWJ 323 vs 326 vs 691 ns. The top-level README headline is '3-46x faster than go-runewidth'. |
| **Workload** | RuneWidth on an ASCII, a CJK and an emoji rune, plus StringWidth on ASCII (5/43/228 chars), CJK, mixed, emoji, TUI (prompt, box-drawing table header, emoji status line), flag, ZWJ and combined strings, all in the separate bench/ module (bench/comparison_test.go). Results are discarded with `_ =`, and the widths are not cross-checked between libraries. |
| **Metric** | latency |
| **Hardware** | AMD EPYC 7763 64-Core Processor, linux/amd64, GitHub-hosted ubuntu-latest runner, 4 procs (CI on PR #5); bench/README run: Intel Core i7-1255U, Windows, amd64 |
| **Compiler and flags** | Go 1.25 gc toolchain (actions/setup-go go-version '1.25'; the patch release is not printed); go test -bench=. -benchmem -count=3 -benchtime=100ms -run=^\$ in bench/ (Library Comparison job in .github/workflows/benchmarks.yml). The bench/README Windows run used go test -bench=. -benchmem -count=5 -run=^\$ and states no toolchain version (bench/go.mod: go 1.25.1). |
| **Adoption** | 8 stars |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/unilibs/uniwidth) · [benchmark](https://github.com/unilibs/uniwidth/pull/5) |

## Verdict

The 'Library Comparison' comment on PR #5 (2026-08-25) ran on a GitHub-hosted AMD EPYC 7763 (linux/amd64) with Go 1.25, -count=3 -benchtime=100ms, taking medians, against go-runewidth v0.0.19 and uniseg v0.4.7 in default configuration. Against go-runewidth: StringWidth 12-52x faster on ASCII, 2.1-2.2x on CJK, 1.7-2.0x on mixed, emoji and flags, 1.1x on ZWJ and 1.2x on the table header; RuneWidth 8.7x on CJK. The workflow itself warns of 10-20% runner variance. Reading the code: the ASCII gap comes mostly from skipping go-runewidth's per-string UAX #29 segmentation. The TUI Prompt row (156.0 vs 270.7 vs 389.7 ns) times a wrong result: uniwidth returns 17 for '❯ Enter command:', where go-runewidth's Neutral classification gives 16, and the harness never cross-checks outputs.

## Use it when

- Go TUIs and CLI tables whose cells are mostly ASCII. In CI on an EPYC 7763: 6.06 vs 73.18 ns for 5 characters and 64.08 vs 3,327 ns for 228 characters against go-runewidth, with 0 allocations.
- CJK, Hangul or kana text where per-code-point width is all you need: StringWidth is about 2.1-2.2x faster, and RuneWidth('世') takes 2.50 vs 21.97 ns.
- Modules that must stay dependency-free. The library module imports only the standard library; the competitors are confined to the separate bench/ module.
- Emoji-heavy status lines where ZWJ families, skin tones and flags should count as 2 cells, without pulling in a grapheme segmenter.

## Skip it when

- Text with dingbats or miscellaneous symbols such as ❯ ✓ ✗ ➜ ★ ♥ ☀ ❤ (without VS16). RuneWidth returns 2 for every code point in U+2600-27BF and in U+1F300-1F5FF, U+1F680-1F6FF and U+1F900-1F9FF. Per the Unicode 15.1 tables in go-runewidth v0.0.19, 402 of the 448 code points in U+2600-27BF are not East Asian Wide (✓ U+2713, ❯ U+276F and ➜ U+279C are Neutral and not even emoji), nor are 259 in those SMP blocks. Prompts and check-mark columns come out misaligned.
- CJK-locale terminals that draw ambiguous characters wide. StringWidthWithOptions drops the ZWJ, VS and flag handling (a family emoji measures 8), returns len(s) for ASCII input so control characters count 1, and ambiguous symbols inside the hard-coded ranges (★ ♥ ♠) stay 2 whatever the option says.
- Code that needs truncation, wrapping, padding or grapheme iteration; none of these exist in the package.
- Layouts that must match uniseg or terminals exactly. Widths come from heuristics rather than segmentation: any character followed by U+FE0F counts 2, and Extended_Pictographic is approximated by whole blocks, including arrows, geometric shapes and Misc Technical.
- Toolchains older than Go 1.25. The project is also young (v0.2.0, 18 commits, 8 stars).

## How it is fast

ASCII strings go through SWAR: 8-byte words are tested against a 0x8080... mask, and control bytes are found with the subtract-and-mask zero-byte trick (Lemire), while strings under 8 bytes use one fused loop. RuneWidth answers from hard-coded range checks for CJK ideographs, Hangul, kana and Bopomofo, four SMP emoji blocks and U+2600-27BF, and otherwise from a 3-stage table (ROOT[256], MIDDLE[17x64], LEAVES[78x32], 2 bits per code point, about 3.8 KB). Non-ASCII strings are converted to []rune and scanned once with a 3-state ZWJ/modifier state machine. go-runewidth v0.0.19's StringWidth instead runs clipperhouse/uax29 grapheme segmentation on every string, ASCII included, and binary-searches interval tables per rune; that difference explains the 12-52x ASCII gap.

## Compared with alternatives

displaywidth is the safer Go choice: it measures grapheme clusters with clipperhouse/uax29, has ANSI-aware truncation and ships in lipgloss v2 and tablewriter. Choose uniwidth only when almost all your strings are ASCII and you can avoid or patch the U+2600-27BF over-width. The two were benchmarked against different go-runewidth versions on different machines, so catalog data cannot rank them. uwcwidth is the Python counterpart and not an option in Go.

## Integration

| | |
|---|---|
| **Form** | module (pure-Go package) |
| **Dependencies** | none (bench/ is a separate module that pins go-runewidth v0.0.19 and rivo/uniseg v0.4.7) |
| **Minimum toolchain** | Go 1.25.1 per go.mod (README says Go 1.25+) |
| **Platforms** | any GOOS/GOARCH (no assembly; the SWAR helpers do unaligned 8-byte loads through unsafe); benchmarked on linux/amd64 and windows/amd64 |
| **Thread safety** | README: 'Thread-safe (immutable design, no global state)'; the functions are pure over read-only generated tables |
| **Drop-in for the baseline** | partial: StringWidth and RuneWidth share go-runewidth's names and signatures, but the Truncate, Wrap and Fill helpers, Condition and locale/env detection are missing, and results differ on symbols in U+2600-27BF, on VS16 sequences and on clusters that only UAX #29 merges |

## Gotchas

- The tests cannot catch range mistakes. cmd/generate-tables filters U+2600-27BF and the other hot ranges out of the generated tables, and the test reference function runeWidthViaBinarySearch repeats the same hard-coded ranges, so the tests compare the code with itself. The conformance test even expects ☀ U+2600 and ❤ U+2764 to be 2.
- RuneWidth/StringWidth and the \*WithOptions variants disagree: the options path has no ZWJ/VS/flag state machine, counts ASCII control characters, and uses a narrower kana range (0x3040-0x30FF, so Bopomofo is excluded). WithEmojiPresentation is accepted but never read.
- The README's truncate example adds up RuneWidth per rune. That miscounts ZWJ sequences and flags, which only StringWidth handles.
- Non-ASCII StringWidth builds a []rune copy for lookahead. The CHANGELOG lists this as one allocation; the verifier observed it only for medium and long strings.

## Known shortcomings

- Go library (language-filter mismatch); display-width primitive, not shaping. Tier A on the CI Library Comparison in PR #5 (public bench/comparison_test.go, Go 1.25, go test -bench with -benchmem -count=3, AMD EPYC 7763 shared runner): ASCII 12-52x, non-ASCII StringWidth 1.1-2.2x, RuneWidth CJK 8.7x over go-runewidth v0.0.19, which does full UAX #29 segmentation while uniwidth does not; Unicode 16.0 vs 15.1.0, no output cross-check, bench/README Windows table stale, and the headline 3-46x overstates the low end.
- Retiered A to C (retier-24): RuneWidth's hot path returns width 2 for all of U+2600-27BF and the U+1F300-1F5FF, U+1F680-1F6FF and U+1F900-1F9FF blocks although 402 of 448 code points in U+2600-27BF and 259 in those SMP blocks are not East Asian Wide per go-runewidth's Unicode 15.1 tables (check mark, cross, right arrowhead, star, heart), the generator filters these ranges out and the tests repeat them, so the CI 'TUI Prompt' row times a wrong answer (17 against go-runewidth's 16); the catalogued rows' inputs are unaffected. The \*WithOptions path lacks ZWJ, variation-selector and flag handling (family emoji measures 8) and returns len(s) for ASCII; WithEmojiPresentation is never read; no Truncate, Wrap or Fill.

## Caveats and trade-offs

The numbers are first-party. The CI comparison runs on a shared GitHub Actions runner with -count=3 and -benchtime=100ms, and the workflow itself calls these results directional with 10-20% variance, which matters for the 1.1-1.4x rows (ZWJ, table header, combined). The work is not identical. go-runewidth v0.0.19 StringWidth runs full UAX #29 grapheme segmentation (clipperhouse/uax29/v2) on every string, ASCII included. uniwidth instead takes a SWAR ASCII path and a lightweight ZWJ/VS16/flag/skin-tone state machine without full segmentation. The Unicode tables differ too: 16.0 in uniwidth, 15.1.0 in go-runewidth (script/generate.go). Both treat East Asian Ambiguous as narrow by default outside CJK locales; go-runewidth picks the setting from RUNEWIDTH_EASTASIAN or the locale or console. The bench never checks that the libraries agree, and their outputs can differ on VS16 sequences (uniwidth forces any character followed by U+FE0F to width 2) and on clusters that only UAX #29 merges. go-runewidth's optional CreateLUT() lookup table is not enabled. The bench/README Windows table looks stale against the current code: it gives uniwidth ASCII long as 340 ns, against 64 ns in CI and \~50 ns in the CHANGELOG. The README headline '3-46x' overstates the low end, since non-ASCII StringWidth gains are 1.1-2.2x in CI. Display width is a text-layout primitive, not shaping. The baselines are Go libraries, not HarfBuzz, FreeType or ICU. [retier] Correctness bug in the hot path: RuneWidth reports width 2 for all of U+2600-27BF and the U+1F300-1F5FF, U+1F680-1F6FF and U+1F900-1F9FF blocks, where most code points are not East Asian Wide (402 of 448 in U+2600-27BF per go-runewidth's Unicode 15.1 tables), so common terminal symbols measure wrong and the CI 'TUI Prompt' row times a wrong answer (17 versus go-runewidth's 16); the generator filters these ranges and the tests cannot catch it. The \*WithOptions path lacks ZWJ, variation-selector and flag handling (a family emoji measures 8) and returns len(s) for ASCII (control characters count 1); WithEmojiPresentation is never read; no Truncate, Wrap or Fill. First-party CI numbers on a shared GitHub Actions runner (-count=3, -benchtime=100ms) that the workflow itself calls directional with 10-20% variance. The work differs: go-runewidth v0.0.19 runs full UAX #29 grapheme segmentation on every string while uniwidth uses a SWAR ASCII path and a lightweight state machine; Unicode tables differ (16.0 versus 15.1).

Four-tier lookup tables plus 8-byte SWAR ASCII fast path with zero dependencies; allocates one []rune for medium and long non-ASCII strings; width of ZWJ and variation-selector sequences can differ from uniseg, which does full UAX #29 segmentation.

## Maintenance

Active but small: v0.2.0 (2026-02-05), last commit 2026-08-25, 8 stars, 18 commits, no open issues. MIT and dependency-free, so easy to vendor, but patch the U+2600-27BF hot path before relying on it for symbol-heavy TUIs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded from C to A on stronger evidence. The CI 'Library Comparison' comment on PR #5 (2026-08-25) runs the public bench/comparison_test.go through .github/workflows/benchmarks.yml: actions/setup-go go-version '1.25', `go test -bench=. -benchmem -count=3 -benchtime=100ms -run=^$` in bench/. Its raw output prints cpu: AMD EPYC 7763 64-Core Processor (linux/amd64), so code, compiler, flags and CPU model are all public, and the raw lines match the table. The bench/README Windows i7-1255U table alone would be C, since it states no Go version.
- **Retiered** A to C: Lowered A to C (vpxyz/xorshift precedent: measured code carries a correctness bug in its hot path). The enricher's code reading shows RuneWidth returns 2 for every code point in U+2600-27BF and in U+1F300-1F5FF, U+1F680-1F6FF and U+1F900-1F9FF, although per go-runewidth v0.0.19's Unicode 15.1 tables 402 of the 448 code points in U+2600-27BF and 259 in those SMP blocks are not East Asian Wide (for example the common terminal symbols check mark, cross, right arrowhead, star and heart); the table generator filters these ranges out and the tests repeat the same ranges, so they cannot catch it. The CI 'TUI Prompt' row (156.0 versus 270.7 versus 389.7 ns) therefore times a wrong answer (17 for the prompt string where go-runewidth gives 16). The inputs of the catalogued ASCII, CJK, emoji, flag and ZWJ rows are unaffected, but a drop-in that returns different widths from the baseline is not doing the same work, and the harness remains first-party on a shared runner with 10-20% variance.
- **Verifier notes:** Language Go, pure Go with zero dependencies (no assembly). go-runewidth is a recognisable incumbent for terminal width in Go, and uniseg is the Go UAX #29 reference. baseline_in_list stays false. The entry belongs in font-shaping-text-layout as a text-layout primitive (terminal cell width), not shaping. Metadata checked: MIT, 8 stars, not a fork, last commit 2026-08-25.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/README.md>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/bench/comparison_test.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/bench/go.mod>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/go.mod>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/docs/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/conformance_test.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/uniwidth.go>
  - <https://github.com/unilibs/uniwidth>
  - <https://github.com/unilibs/uniwidth/commits>
  - <https://github.com/unilibs/uniwidth/tree/main/.github/workflows>
  - <https://github.com/unilibs/uniwidth/pull/5>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/v0.0.19/runewidth.go>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/v0.0.19/runewidth_windows.go>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/v0.0.19/runewidth_table.go>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/v0.0.19/go.mod>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/v0.0.19/script/generate.go>
- **Sources the enricher read:**
  - <https://github.com/unilibs/uniwidth>
  - <https://github.com/unilibs/uniwidth/pull/5>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/README.md>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/ROADMAP.md>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/go.mod>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/uniwidth.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/options.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/tables_generated.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/cmd/generate-tables/main.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/docs/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/conformance_test.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/uniwidth_test.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/options_test.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/fuzz_test.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/benchmark_test.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/bench/comparison_test.go>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/bench/go.mod>
  - <https://raw.githubusercontent.com/unilibs/uniwidth/HEAD/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/v0.0.19/runewidth.go>
  - <https://raw.githubusercontent.com/mattn/go-runewidth/v0.0.19/runewidth_table.go>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/unilibs/uniwidth`) · [data/wave10/enrich/raw/github_com_unilibs_uniwidth.json](../../../data/wave10/enrich/raw/github_com_unilibs_uniwidth.json) (enrichment confidence 0.75)

</details>
