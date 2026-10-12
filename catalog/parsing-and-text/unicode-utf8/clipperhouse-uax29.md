# uax29 (graphemes and words)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Zero-allocation Go UAX #29 grapheme/word/sentence segmenter (Unicode 17); 14x rivo/uniseg graphemes, 3.6x blevesearch/segment words, first-party.

| | |
|---|---|
| **Beats** | rivo/uniseg (graphemes); blevesearch/segment (words) |
| **Claimed result** | Graphemes (graphemes/README.md, Apple M2): mixed multilingual sample 142635 ns/op, 245.12 MB/s versus rivo/uniseg 2018284 ns/op, 17.32 MB/s (about 14.2x, derived from page data); ASCII 8846 ns/op, 508.73 MB/s versus 366760 ns/op, 12.27 MB/s (about 41.5x, derived from page data); 0 allocs/op for both. The uniseg side uses uniseg.NewGraphemes/Graphemes.Next, which calls StepString and computes word, sentence and line-break boundaries plus monospace width on every step, while uax29 computes grapheme boundaries only, so these ratios overstate a graphemes-only comparison (uniseg's lighter FirstGraphemeClusterInString API was not benchmarked). Words (words/README.md): multilingual 164760 ns/op, 212.20 MB/s versus blevesearch/segment 593147 ns/op, 58.94 MB/s (about 3.6x, derived from page data); ASCII prose 224518 ns/op, 282.38 MB/s versus 1387461 ns/op, 45.69 MB/s (about 6.2x, derived from page data); the blevesearch loop also copies the input string to []byte on every iteration (40960 and 65537 B/op, 1 alloc/op). |
| **Workload** | Go testing benchmarks iterating every grapheme cluster (graphemes) or word token (words) of a multilingual sample (project testdata) and of repeated ASCII text, against rivo/uniseg and blevesearch/segment; the loop counts tokens only. |
| **Metric** | throughput |
| **Hardware** | Apple M2, darwin/arm64, GOMAXPROCS 8 (benchmark names end in -8) |
| **Compiler and flags** | Go toolchain version not printed in either README output; graphemes/comparative/go.mod declares go 1.24.2 and words/comparative/go.mod declares go 1.18; plain go test -bench defaults, no flags stated |
| **Adoption** | 123 stars; dependency of clipperhouse displaywidth and jargon |
| **Last commit** | 2026-02-16 |
| **Links** | [repository](https://github.com/clipperhouse/uax29) · [benchmark](https://github.com/clipperhouse/uax29/blob/master/graphemes/README.md) |

## Verdict

First-party go test -bench on an Apple M2 (darwin/arm64, GOMAXPROCS 8), Go version unstated, single runs, from the in-repo comparative modules (local replace, so they measure HEAD-era code from February 2026). Graphemes are 14.2x (multilingual 34,962-byte sample) and 41.5x (4,500-byte ASCII) faster than rivo/uniseg v0.4.7's NewGraphemes, which also computes word, sentence, line and width state, so those ratios overstate a graphemes-only comparison. Words are 3.6x and 6.2x faster than blevesearch/segment v0.9.1. That baseline ran in its default build, the table-driven Ragel -T1 machine its README says is not the fastest; the -tags prod goto machine (-G2) was not used. Its loop also copies the input to []byte on every iteration, so the word ratios are upper bounds as well.

## Use it when

- Go search and NLP pipelines (inverted indexes, BM25, embedding chunking) that need standard UAX #29 word tokens: 212 MB/s multilingual and 282 MB/s ASCII prose on an Apple M2, with no allocations.
- Grapheme-correct cursor movement, truncation or counting in Go TUIs and CLIs; clipperhouse/displaywidth and the Charm stack build on it.
- ASCII-heavy or mostly-Latin text, where the fast paths apply on almost every byte (509 MB/s graphemes on a repeated ASCII pangram).
- Terminal output carrying colour codes: AnsiEscapeSequences keeps each escape sequence as one token, checked against charmbracelet/x/ansi's DecodeSequence in the comparative tests.
- Streaming input via FromReader/SplitFunc with bufio.Scanner, or text already in memory as string or []byte with no conversion.

## Skip it when

- When you also need line-break (UAX #14) opportunities or monospace width per cluster: rivo/uniseg's Step returns graphemes, words, sentences, line breaks and width in one pass. uax29 has no line breaking (issue #50 closed), and width lives in the separate displaywidth package.
- Language-tailored word segmentation (Thai, Lao, Khmer, Chinese and Japanese dictionary breaking): only the default UAX #29 rules are implemented, so ideographs and Southeast Asian scripts are not split into dictionary words.
- Untrusted input that may be invalid UTF-8: the README calls the result undefined (garbage in, garbage out); fuzzing guards only against panics and infinite loops, so validate with utf8.Valid first.
- Pipelines that rely on blevesearch/segment token types (Letter, Number, Kana, Ideo) or its exact boundaries: uax29 words returns untyped tokens, and the harness itself notes that counts can differ from blevesearch.
- Non-Go code: this is a pure Go module. The C# port (clipperhouse/uax29.net) is separate, and for C/C++ the catalogued alternatives are libgrapheme, uni-algo and ICU.

## How it is fast

Break properties come from generated tries indexed directly by UTF-8 bytes, so a lookup needs no rune decoding. The rules run as one forward pass that carries the last two non-ignored properties, a regional-indicator count and a three-state GB9c (Indic conjunct) tracker, so it never looks back. ASCII fast paths in Next() (PR #42, January 2026) skip the rule engine: an ASCII byte other than CR followed by another ASCII byte or end of text is a grapheme by itself, and a run of [A-Za-z0-9] followed by an ASCII space or end of text is a word. Both shortcuts are correct under UAX #29, since no ASCII character is Extend, SpacingMark, Prepend or regional indicator. Iterators are generic over string and []byte and report 0 allocs/op.

## Compared with alternatives

It is the only Go segmenter in the category. Pick it for Go code, and pick cometkim/fast-grapheme-segmenter (Rust), unicode-segmenter (JavaScript), ugrapheme (Python) or uni-algo, libgrapheme and ICU (C/C++) in those languages. Its multilingual grapheme rate (245 MB/s on an M2) is in the same range as those siblings' own first-party numbers, but no shared harness compares them.

## Integration

| | |
|---|---|
| **Form** | module (pure-Go packages: graphemes, words, phrases, sentences) |
| **Dependencies** | none (root go.mod has no require lines; the comparative benchmark modules pull rivo/uniseg v0.4.7, blevesearch/segment v0.9.1 and charmbracelet/x/ansi v0.11.6) |
| **Minimum toolchain** | go.mod declares go 1.18 (generics); CI only tests Go 1.21-1.26 with -race -short. PR #42 described a bump to 1.20 that HEAD's go.mod does not show. |
| **Platforms** | any GOOS/GOARCH (no assembly or unsafe in the iterator and split code read); the published benchmarks ran on darwin/arm64 |
| **Thread safety** | Not documented. An Iterator is a small mutable struct, so give each goroutine its own; the SplitFunc and generated tables are read-only and safe to share. |
| **Drop-in for the baseline** | false: a different API from uniseg (NewGraphemes/Next/Str, Step with boundary flags) and blevesearch/segment (NewWordSegmenter/Segment/Bytes/Type); FromReader and SplitFunc fit any bufio.Scanner the same way blevesearch's SplitWords does |

## Gotchas

- v2.1.0 and v2.1.1 are retracted in go.mod (surprising allocations). v2.5.0 changed FromString/FromBytes to return a pointer iterator, and v2 removed the Filter, Transform and All helpers, so code written for v1 needs rework.
- words yields whitespace and punctuation tokens. Filtering to word-like tokens is now up to the caller, since the v1 Wordlike filter was removed.
- FromReader inherits bufio.Scanner's 64 KiB default token limit, so a pathological grapheme or word longer than that (for example stacked combining marks) stops the scan with an error unless you call Buffer to raise it.
- AnsiEscapeSequences8Bit reads C1 bytes 0x80-0x9F as controls. They are only checked at a token start, where valid UTF-8 never has a continuation byte, so valid text is unaffected, but mixed-encoding input will tokenize differently with it on.

## Known shortcomings

- The grapheme ratios (14.2x, 41.5x on ASCII) are inflated because uniseg's Graphemes.Next runs StepString, computing word, sentence, line and width boundaries per step; Unicode 17 with GB9c is compared against uniseg's 15.0.0 tables; the Bleve loop copies []byte on every iteration; Go version unstated. The ASCII fast path comparison is valid.
- Enricher (e127, 2026-10-05): no correctness bug; the ASCII fast paths (graphemes, words) are correct under UAX #29. New measurement flaw: the blevesearch/segment v0.9.1 baseline was built without -tags prod, so the slower table-driven Ragel -T1 machine ran instead of the documented fastest -G2 build, plus a []byte copy per iteration, so the word ratios 3.6x/6.2x are upper bounds. uniseg v0.4.7 is still the latest tag. Tier C stands.
- Domain set to parsing-and-text to match its unicode-utf8 category.

## Caveats and trade-offs

Author-run, single runs without variance, on one Apple M2 (darwin/arm64, -8 suffix so GOMAXPROCS 8); Go version not stated, so not tier A even though the harnesses are public and trivial to rerun. Not like-for-like on work done: rivo/uniseg's Graphemes.Next (v0.4.7) runs StepString, which also computes word, sentence and line-break boundaries and monospace width per cluster, so the 14.2x and 41.5x grapheme ratios partly measure that extra work; uniseg's graphemes-only FirstGraphemeClusterInString was not compared. Unicode versions differ: uax29 implements Unicode 17 (trie generated from the 17.0.0 UCD, GB9c Indic conjunct rule implemented) while uniseg v0.4.7 implements Unicode 15.0.0 without GB9c, and the 34,962-byte multilingual sample has about 2,000 Indic code points, so boundaries can differ there (extra work on the uax29 side). The ASCII fast path (any ASCII byte other than CR followed by an ASCII byte or end of input is a single grapheme) is correct under UAX #29 (no ASCII Extend, SpacingMark, Prepend or RI; CR LF handled by the slow path), and the ASCII input is a 4,500-byte repeated pangram that hits it on almost every byte. For words, the harness itself notes word counts may differ from blevesearch/segment because of different rule implementations, and the blevesearch loop pays a string-to-[]byte copy per iteration. Baselines are Go libraries only: no ICU, simdutf, C or golang.org/x/text comparison. Conformance is checked against the official Unicode test suites in CI.

Go only; Unicode 17 UAX #29 grapheme, word, phrase and sentence tokenizers with string, []byte and io.Reader APIs; optional 7-bit and 8-bit ANSI escape sequence handling; zero allocations. Invalid UTF-8 is undefined behavior (garbage in, garbage out), so validate with utf8.Valid. Word rules are the basic UAX #29 defaults, not language tailored.

## Maintenance

Active: v2.7.0 tagged 2026-02-16 with the last commit the same day, one open issue (#51, README link) and one open PR (#52, exporting the ANSI length functions). MIT-licensed, zero dependencies, conformance-tested against the Unicode 17 test files in CI and fuzzed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party go test -bench output in graphemes/README.md and words/README.md, with public harnesses graphemes/comparative/comparative_test.go (rivo/uniseg v0.4.7 pinned) and words/comparative/comparative_test.go (blevesearch/segment v0.9.1), on an Apple M2; the Go toolchain version is never printed and the results are single runs, so not A, and no independent measurement exists, so not B.
- **Verifier notes:** Numbers on both README pages match the record exactly and the derived ratios check out (bytes per op are consistent across rows: 34,962 for the sample, 4,500 for the ASCII string). Tier C stands; the main new shortcoming is that the uniseg baseline call does grapheme plus word, sentence, line and width work, so the grapheme ratios are inflated. License MIT, 123 stars, 7 forks, last commit 2026-02-16, not archived or a fork, all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party go test -bench; orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://github.com/clipperhouse/uax29>
  - <https://github.com/clipperhouse/uax29/commits/master>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/words/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/go.mod>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/comparative/comparative_test.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/comparative/go.mod>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/words/comparative/comparative_test.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/words/comparative/go.mod>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/iterator.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/splitfunc.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/trie.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/testdata/testdata.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/testdata/sample.txt>
  - <https://raw.githubusercontent.com/rivo/uniseg/v0.4.7/README.md>
  - <https://raw.githubusercontent.com/rivo/uniseg/v0.4.7/grapheme.go>
  - <https://raw.githubusercontent.com/rivo/uniseg/v0.4.7/step.go>
  - <https://raw.githubusercontent.com/rivo/uniseg/v0.4.7/properties.go>
  - <https://raw.githubusercontent.com/blevesearch/segment/v0.9.1/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/go.mod>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/words/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/sentences/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/phrases/README.md>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/comparative/comparative_test.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/comparative/go.mod>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/words/comparative/comparative_test.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/words/comparative/go.mod>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/iterator.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/splitfunc.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/reader.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/graphemes/ansi.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/words/iterator.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/words/splitfunc.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/words/reader.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/testdata/testdata.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29/HEAD/.github/workflows/gotest.yml>
  - <https://github.com/clipperhouse/uax29/issues?q=is%3Aissue>
  - <https://github.com/clipperhouse/uax29/pulls?q=is%3Apr>
  - <https://github.com/clipperhouse/uax29/pull/42>
  - <https://github.com/clipperhouse/uax29/releases>
  - <https://github.com/clipperhouse/uax29/tags>
  - <https://github.com/clipperhouse/uax29/commits/master>
  - <https://github.com/rivo/uniseg/tags>
  - <https://github.com/blevesearch/segment>
  - <https://raw.githubusercontent.com/blevesearch/segment/v0.9.1/README.md>
  - <https://raw.githubusercontent.com/blevesearch/segment/v0.9.1/segment_words.go>
  - <https://raw.githubusercontent.com/blevesearch/segment/v0.9.1/segment_words_prod.go>
  - <https://raw.githubusercontent.com/blevesearch/segment/v0.9.1/segment.go>
  - <https://raw.githubusercontent.com/blevesearch/segment/v0.9.1/go.mod>
  - <https://raw.githubusercontent.com/blevesearch/segment/v0.9.1/maketesttables.go>
  - <https://raw.githubusercontent.com/clipperhouse/uax29.net/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/clipperhouse/uax29`) · [data/wave10/enrich/raw/github_com_clipperhouse_uax29.json](../../../data/wave10/enrich/raw/github_com_clipperhouse_uax29.json) (enrichment confidence 0.8)

</details>
