# The Platinum Searcher (pt, Go code search)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Go` · `MIT` · 🔴 abandoned

> pt: an ack/ag-style recursive code searcher in Go. A single 2015 first-party run put it 8% ahead of C ag on one literal search.

| | |
|---|---|
| **Beats** | The Silver Searcher (ag, written in C: ggreer/the_silver_searcher has src/main.c) and ack (Perl); versions of all three tools not stated. |
| **Claimed result** | README benchmark (one run per tool, shell time, Linux kernel tree): ack 32.613 s total (30.18 s user, 2.32 s system, 99% cpu), ag 1.069 s total (1.57 s user, 1.76 s system, 311% cpu), pt 0.991 s total (2.29 s user, 1.26 s system, 358% cpu). README Features claim pt is 'about 3-5x faster than ack' and 'as fast as' ag. By wall time pt is about 1.08x (8%) faster than ag and about 33x faster than ack (derived from page data), but it uses more CPU time than ag (3.55 s vs 3.33 s, derived from page data). |
| **Workload** | Recursive search for EXPORT_SYMBOL_GPL in the Linux kernel source tree, timed with the shell `time` builtin (one run per tool). |
| **Metric** | latency |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 2.8k stars, 144 forks; Homebrew formula pt |
| **Last commit** | 2018-09-05 |
| **Links** | [repository](https://github.com/monochromegane/the_platinum_searcher) · [benchmark](https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/README.md) |

## Verdict

The claim rests on one first-party zsh `time` run per tool, recorded in December 2015: a search of the Linux kernel tree for the literal EXPORT_SYMBOL_GPL. pt took 0.991 s wall against 1.069 s for ag (C, about 8% faster) and 32.6 s for ack (Perl), but used more CPU (3.55 s vs 3.33 s user+sys); no versions, Go toolchain, CPU or kernel revision are given. The only independent number found, for a regex workload, goes the other way: the ripgrep 0.8.0 README (i7-6900K, Linux kernel, -w '[A-Z]+_SUSPEND') has pt at 14.208 s and ag at 0.589 s.

## Use it when

- Interactive, case-sensitive literal searches in source trees, where one static Go binary (macOS, Windows and Linux release builds, Homebrew `pt`) is convenient.
- Trees that mix UTF-8 with EUC-JP or Shift_JIS files: pt detects the encoding per file, transcodes the pattern and can re-encode output with -o (jis, sjis, euc).
- Existing Vim Unite.vim or Emacs pt.el setups that already call pt with --nogroup --nocolor.

## Skip it when

- Regex, -i, -S or -w searches. These run Go regexp on each line, and the independent ripgrep 0.8.0 README timed `pt -w -e '[A-Z]+_SUSPEND'` on the Linux kernel at 14.208 s, against ag at 0.589 s and ripgrep at 0.106 s (i7-6900K). In issue #34 (2014, pt 1.5.2), `-i time_t` on php-src took 7.284 s against ag's 0.437 s; that issue is still open.
- Files with lines over 64 KiB (minified JS, JSON) when any of -e, -i, -S, -w or -A/-B/-C is used: everything after the long line is silently missed (issue #168, open since 2016; see gotchas).
- UTF-16 files (issue #202), symlinked directories (#188) and very long filenames (#197). All three are open reports of missing results.
- Any project that needs a maintained tool: last commit and release v2.2.0 on 2018-09-05, 41 open issues, no go.mod, and a 2025 issue (#219) saying Gentoo GURU wants to drop it as dead.
- Large trees containing unreadable, locked or special files, or runs under a low file-descriptor limit: one failed open aborts the whole search (issues #106 and #192).

## How it is fast

One walker goroutine reads directories with raw syscall.ReadDirent and uses the dirent type byte, so most files need no stat call. It feeds paths through a 5,000-slot channel to max(NumCPU, 2) grep goroutines, with GOMAXPROCS set to NumCPU. On the default literal path (bufferGrep, rewritten in v2.2.0), each worker reads the file into a reused 16 KiB buffer, which doubles when a line does not fit. It runs Go's bytes.Index over the whole chunk up to the last newline and gets line numbers by counting newlines with bytes.Count, so it never splits the chunk into lines first. bytes.Index skips ahead with IndexByte on the first pattern byte and falls back to the internal/bytealg SIMD assembly for patterns up to 63 bytes on AVX2. Regex, ignore-case, word and context searches instead scan line by line with bufio.Scanner and Go's regexp package.

## Compared with alternatives

Pick pt only for automatic EUC-JP/Shift_JIS handling or an existing pt editor integration. Otherwise ripgrep (already in the catalog, built on the Rust regex crate sibling) is maintained, reads EUC-JP, Shift_JIS and UTF-16 via -E, and was 134x faster than pt on a regex word search in its own 0.8.0 README. fastgrep is the sibling to pick when GNU grep flag compatibility matters.

## Integration

| | |
|---|---|
| **Form** | CLI binary (Go package with cmd/pt; prebuilt release binaries; Homebrew formula pt) |
| **Dependencies** | jessevdk/go-flags, monochromegane/conflag (BurntSushi/toml), monochromegane/go-gitignore, go-home, terminal, shiena/ansicolor, golang.org/x/text (Japanese encodings), gopkg.in/yaml.v2 (pinned in Godeps/Godeps.json) |
| **Minimum toolchain** | Go 1.11 era (Godeps GoVersion go1.11; Travis CI tested 1.11.x and master in 2018). There is no go.mod, and the README's `go get -u` install predates Go modules; building with a current Go toolchain is not documented. |
| **Platforms** | macOS, Windows and Linux release binaries. The fast ReadDirent walker is built on linux, darwin, freebsd, openbsd and netbsd, with a portable readdir fallback elsewhere. |
| **Thread safety** | Not documented. It is a CLI, and the library entry point PlatinumSearcher.Run mutates a package-level `opts` global (platinum_searcher.go, search.go), so concurrent Run calls in one process are unsafe (from the code). |
| **Drop-in for the baseline** | partial — the flags and output resemble ag (-A/-B/-C, -l, -c, -g, -G, -i, -S, -w, --hidden, --ignore, --nogroup), but the pattern is a literal unless -e is given, regex syntax is Go RE2, and option.go has no file-type filter options |

## Gotchas

- Harness and staleness: the README's Linux-kernel numbers were added on 2015-12-07 (commit a86ecd3, around pt v2.0.x). They are one zsh `time` run per tool, listed in the order ack, ag, pt, with no tool versions, hardware or kernel revision. The default search path was rewritten in v2.2.0 (2018-09-05), so the published numbers measure neither the current pt nor a current ag. The README's earlier 'pt became faster than ag!!' update (commit 374b952, January 2014) changed only the pt row (1.066 s to 0.892 s) and kept the old ack and ag rows, so it was a cross-run comparison.
- Silent missed matches: lineGrep.grepEachLines (line_grep.go) uses bufio.Scanner with its default 64 KiB token limit, never enlarges the buffer and never checks scanner.Err(). With -e, -i, -S, -w or any context option, a line over 64 KiB ends that file's scan, and matches on that line and every later line are dropped without an error (issue #168, still open). The default literal path (bufferGrep) grows its buffer and is not affected.
- Fatal aborts: bufferGrep, fixedGrep and extendedGrep call log.Fatalf on any os.Open error, and bufferGrep panics on a read error. A single permission-denied, locked or EMFILE file therefore kills the whole run partway through its output (issue #106 'too many open files', issue #192 Windows locked file). find.go skips only named pipes, so sockets and device nodes are passed to the grep workers (from the code). A malformed .gitignore line can also panic inside go-gitignore (issue #190).
- Binary and encoding detection reads only the first 512 bytes of the first read. A NUL byte later in the file is not seen, and 4-byte UTF-8 sequences (emoji and similar) count as 'suspicious', so a file whose head is more than 10% such bytes is classed as binary and skipped silently (encoding.go).

## Known shortcomings

- One run with no hardware or tool versions; only about 8% faster than ag (C) by wall time while using more CPU; last commit 2018.
- README kernel numbers date from 2015-12-07 (commit a86ecd3, about v2.0.x) and predate the v2.2.0 grep rewrite; the January 2014 'faster than ag' commit 374b952 changed only the pt row and reused the ack and ag rows (cross-run). The independent ripgrep 0.8.0 README has pt -w -e '[A-Z]+_SUSPEND' at 14.208 s against ag's 0.589 s. Code bugs: bufio.Scanner 64 KiB limit with scanner.Err() unchecked, so -e, -i, -S, -w and context paths silently drop the rest of a file (#168 open); log.Fatalf on any open error aborts the run (#106, #192). Abandoned since 2018.

## Caveats and trade-offs

Single run on an unspecified machine, with no tool versions, Go version, kernel tree revision or flags; the 8% wall-time gap over ag is within one-run noise, and pt spends more total CPU time than ag. The runs are listed in the order ack, ag, pt, so pt probably ran on the warmest page cache (inference; order of execution not stated). Both ag and pt are multithreaded, so the result is a tool-versus-tool comparison, not a language-level one; the README states no mechanism. Last commit 2018-09-05 (Travis CI and wercker badges). ripgrep, already in the catalog, is the common choice today. [retier] The README kernel numbers date from 2015-12-07 (commit a86ecd3, about v2.0.x) and predate the v2.2.0 grep rewrite; the January 2014 'faster than ag' commit 374b952 changed only the pt row and reused the ack and ag rows (cross-run). The independent ripgrep 0.8.0 README has pt -w -e '[A-Z]+_SUSPEND' at 14.208 s against ag's 0.589 s. bufio.Scanner's 64 KiB limit with scanner.Err() unchecked makes -e, -i, -S, -w and context paths silently drop the rest of a file (#168 open); log.Fatalf on any open error aborts the run (#106, #192). Abandoned since 2018.

Honours .gitignore, skips dot-directories unless --hidden, reads UTF-8, EUC-JP and Shift_JIS; binaries for macOS, Windows and Linux (README).

## Maintenance

Abandoned since the v2.2.0 release on 2018-09-05, with 41 open issues, unanswered crash and missed-match reports, and a 2025 issue (#219) on Gentoo GURU's plan to drop it. It is MIT-licensed and small (about 30 Go files) but has no go.mod. The 2015 README numbers predate the current search code, so the claim is not evidence for today's pt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README shows a single shell `time` run of ack, ag and pt on the Linux kernel tree, with no CPU model, tool versions, Go version or build flags, so it falls short of A and is first-party (C).
- **Retiered** C to D: Enricher: the README's ack and ag rows were reused from an earlier run while only the pt row was re-measured (cross-run), the 8% gap over ag is within single-run noise, and the independent ripgrep README shows pt 24x slower than ag on a regex search; cross-run precedent: C to D.
- **Verifier notes:** README numbers match the record exactly; ag is confirmed C. Keep at C with shortcomings: one run, no hardware or versions, wall-time win over the C baseline of only about 8% with higher CPU use, abandoned since 2018.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/README.md>
  - <https://github.com/monochromegane/the_platinum_searcher>
  - <https://github.com/monochromegane/the_platinum_searcher/commits>
  - <https://github.com/ggreer/the_silver_searcher>
  - <https://raw.githubusercontent.com/ggreer/the_silver_searcher/HEAD/src/main.c>
- **Sources the enricher read:**
  - <https://github.com/monochromegane/the_platinum_searcher>
  - <https://github.com/monochromegane/the_platinum_searcher/commits/master>
  - <https://github.com/monochromegane/the_platinum_searcher/commits/master/README.md>
  - <https://github.com/monochromegane/the_platinum_searcher/blame/master/README.md>
  - <https://github.com/monochromegane/the_platinum_searcher/commit/374b952>
  - <https://github.com/monochromegane/the_platinum_searcher/commit/1234254>
  - <https://github.com/monochromegane/the_platinum_searcher/commit/6a9274a>
  - <https://github.com/monochromegane/the_platinum_searcher/tags>
  - <https://github.com/monochromegane/the_platinum_searcher/issues?q=is%3Aissue+slow+OR+performance+OR+long+OR+%22too+many+open+files%22>
  - <https://github.com/monochromegane/the_platinum_searcher/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/monochromegane/the_platinum_searcher/issues/34>
  - <https://github.com/monochromegane/the_platinum_searcher/issues/106>
  - <https://github.com/monochromegane/the_platinum_searcher/issues/168>
  - <https://github.com/monochromegane/the_platinum_searcher/issues/190>
  - <https://github.com/monochromegane/the_platinum_searcher/issues/192>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/README.md>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/grep.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/buffer_grep.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/fixed_grep.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/extended_grep.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/line_grep.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/passthrough_grep.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/find.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/walk.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/search.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/pattern.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/platinum_searcher.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/option.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/ignore.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/encoding.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/decoder.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/match.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/file_handler.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/file_info.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/print.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/readdir_unix.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/cmd/pt/main.go>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/wercker.yml>
  - <https://raw.githubusercontent.com/monochromegane/the_platinum_searcher/HEAD/Godeps/Godeps.json>
  - <https://raw.githubusercontent.com/golang/go/master/src/bytes/bytes.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/internal/bytealg/index_amd64.go>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/0.8.0/README.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/monochromegane/the_platinum_searcher`) · [data/wave14/enrich/raw/github_com_monochromegane_the_platinum_searcher.json](../../../data/wave14/enrich/raw/github_com_monochromegane_the_platinum_searcher.json) (enrichment confidence 0.75)

</details>
