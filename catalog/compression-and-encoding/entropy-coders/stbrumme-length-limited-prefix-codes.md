# length-limited-prefix-codes (modified Kraft)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib` · 🔴 abandoned

> Heap-driven Kraft-inequality heuristic for length-limited Huffman code lengths, about 3x faster than Package-Merge at near-optimal size.

| | |
|---|---|
| **Beats** | Package-Merge optimal length-limited Huffman codes, and the MiniZ/JPEG/BZip2 length-limiting heuristics |
| **Claimed result** | Modified Kraft (Strategy B) 0.41 s vs Package-Merge 1.17 s, MiniZ 0.58 s, JPEG 0.61 s, BZip2 0.88 s (100,000 runs); output size 62.55% vs 62.51% (Package-Merge) and 62.65% (MiniZ/JPEG). At 8-bit limit 0.24 s vs 0.96 s for Package-Merge. README says it 'outperforms Moffat's Huffman code generator in pretty much all practical use cases' (Moffat unlimited 0.54-0.55 s). |
| **Workload** | Computing length-limited Huffman code lengths from the histogram of the first 64 KB of enwik, 100,000 repeats, length limit 12 bits. |
| **Metric** | throughput |
| **Hardware** | Core i7 (exact model not stated) |
| **Compiler and flags** | GCC x64, flags not stated |
| **Adoption** | 25 stars |
| **Last commit** | 2021-06-30 |
| **Links** | [repository](https://github.com/stbrumme/length-limited-prefix-codes) · [benchmark](https://github.com/stbrumme/length-limited-prefix-codes) |

## Verdict

The author's benchmark.c times 100,000 calls on a fixed 256-symbol histogram of the first 64 KB of enwik at a 12-bit limit: modified Kraft 0.41 s vs the author's own Package-Merge 1.17 s, MiniZ-style 0.58 s, JPEG-style 0.61 s, BZip2-style 0.88 s and unlimited Moffat Huffman 0.54 s. The run used GCC x64 on an unspecified Core i7; the Makefile gives -O3 -s -std=c99. Part of the gap is that the baselines' shared-interface wrappers malloc and qsort the histogram on every call, which the README acknowledges.

## Use it when

- Encoders that rebuild Huffman tables often (per block in deflate-, JPEG- or bzip2-style formats) where table construction shows up in profiles
- Byte-sized alphabets (256 symbols) with limits of 8-16 bits, which is the measured case
- When you can accept about 0.04-0.3 percentage points of extra output versus optimal Package-Merge (62.55% vs 62.51% at 12 bits; 70.76% vs 70.47% at 8 bits on the README data set)
- Small, dependency-free C99 code under the Zlib licence that you want to vendor and adapt

## Skip it when

- When you need provably optimal lengths: use Package-Merge (also in this repo), which the author recommends 'if speed is of no concern'
- Untrusted or unchecked parameters: limitedKraftHeap has no feasibility check, so if the number of used symbols exceeds 2^maxLength its heap underflows (size_t wraps) and it reads out of bounds instead of returning 0
- Single-symbol histograms: the fix-up pass shortens the lone length-1 code to 0, so the function returns 0 ('error') for a valid input
- Large or heavily skewed alphabets: the README says neither was tested, and the code-length quality depends on a crude float log2 approximation
- Upstream activity matters to you: 10 commits, last one 2021-06-30

## How it is fast

Strategy B (limitedKraftHeap) skips building a Huffman tree. It rounds each symbol's estimated entropy -log2(p) to an integer length, then repairs the Kraft-McMillan sum with integer arithmetic (2^(maxLength-len)). A float-keyed max-heap picks the symbols that gained the most from rounding down and lengthens them by one bit until the sum is at most 1, then a single pass shortens codes where spare budget remains. log2 is replaced by a bit-twiddling approximation (exponent plus 0.585 times mantissa), and no qsort is needed, unlike the repo's Package-Merge, MiniZ/JPEG and BZip2 wrappers, which sort the histogram on every call.

## Compared with alternatives

No sibling catalogued here builds code lengths: FiniteStateEntropy's Huff0, zune-entropy and FPC are full Huffman codecs with their own table builders. Pick this when you already have a coder and only need a faster length-limiting step; pick Huff0 or FPC when you need the whole encoder and decoder.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C standard library: malloc/free; Package-Merge, MiniZ/JPEG and BZip2 wrappers also use qsort, and MiniZ/JPEG/BZip2 need moffat.c) |
| **Minimum toolchain** | C99 (Makefile: gcc -O3 -s -std=c99 -Wall -Wextra -Wshadow -pedantic) |
| **Platforms** | any (portable scalar C; fastlog2 assumes 32-bit IEEE-754 float) |
| **Thread safety** | not documented; limitedKraftHeap uses only per-call malloc'd buffers and no globals, so separate calls should be reentrant |
| **Drop-in for the baseline** | partial — same histogram-in, lengths-out contract as the repo's Package-Merge and MiniZ/JPEG/BZip2 limiters, but output lengths differ from them (not bit-identical to zlib/miniz/bzip2), so formats with canonical-table expectations still work but compressed bytes change |

## Gotchas

- No failure path in limitedKraftHeap for an infeasible limit (more used symbols than 2^maxLength): the Kraft-repair loop pops an empty heap, heap-&gt;size-- wraps to SIZE_MAX and heap_sinkDown reads out of bounds. Package-Merge in the same repo returns 0 here. Validate maxLength &gt;= ceil(log2(usedSymbols)) before calling.
- A histogram with exactly one non-zero symbol returns 0 and sets that symbol's length to 0, because the optional shrink loop decrements its length-1 code.
- `one = 1 << maxLength` is an int shift, so maxLength must stay below 31; malloc results are not checked.
- The fastlog2 comment claims zero error at 1.5, but the active 'version C' returns e + 0.585\*m: it overestimates log2 by 0.17-0.59 bits (log2(1.0) comes out as 0.585). Lengths stay valid because Kraft is enforced, but the rounding is biased toward short codes, and the committed fuzzer (fuzzer.c) is hard-wired to packageMerge at 8 bits, so Strategy B was not fuzzed as committed.

## Known shortcomings

- Only 'Core i7 / GCC x64' stated, no flags. Last commit 2021-06-30, abandoned.
- Read in source: limitedKraftHeap has no feasibility check, so more used symbols than 2^maxLength empties the heap, size_t wraps and it reads out of bounds (Package-Merge returns 0 in the same case). A single-symbol histogram returns 0 (the shrink loop drops the lone code to length 0). 1 &lt;&lt; maxLength is an int shift; malloc unchecked. fastlog2 'version C' is off by 0.17-0.59 bits although the comment claims zero error (output is still a valid prefix code). The committed fuzzer.c is hard-wired to packageMerge at 8 bits, so Strategy B was never fuzzed. Makefile flags are -O3 -s -std=c99. Baseline wrappers malloc+qsort on every call, inflating their times.

## Caveats and trade-offs

Benchmark code is public but CPU model and compiler flags are missing, so tier C. One dataset (histogram of the first 64 KB of enwik). Baselines are the author's own reimplementations of Package-Merge, MiniZ/JPEG and BZip2 length limiting, not the upstream libraries run directly. Times are wall times for 100,000 repeats on the author's machine. In the length-limit table the 12-bit Strategy B time is 0.40 s (0.41 s in the main table). The author does not call the project finished; 10 commits, last one 2021-06-30 (over 3 years ago). The repo was fuzzed with afl-fuzz (Feb 2021 commit). Found through the GitHub huffman topic page, not Hacker News.

Code-length construction only (the table-building half of a Huffman coder), not a full encoder or decoder. Strategy B gives slightly longer total output than optimal Package-Merge, worst when the limit nears the lower bound. Single-threaded, plain C with a shared histogram interface that costs some overhead.

## Maintenance

Inactive since 2021-06-30 (10 commits, 25 stars, 0 open issues) but Zlib-licensed, about 300 lines per algorithm and easy to vendor; add an input-feasibility check and a single-symbol special case before using it on untrusted data.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Results table (benchmark program in the repo, `time ./benchmark <id> 12 100000`) shows modified Kraft 0.41 s vs Package-Merge 1.17 s, MiniZ 0.58 s, JPEG 0.61 s, BZip2 0.88 s, and 0.24 s vs 0.96 s at an 8-bit limit. These are first-party numbers on 'Core i7 / GCC x64' with no CPU model or flags, so not A.
- **Verifier notes:** Numbers and license (Zlib, Copyright 2021 Stephan Brumme) verified; 25 stars, not archived. maintenance_status changed from finished to abandoned because the README never says the project is complete and the last commit is 2021-06-30.
- **Fields the verifier corrected:** `maintenance_status`, `caveats`
- **Shortcomings recorded by:** first-party README table
- **Pages the verifier opened:**
  - <https://github.com/stbrumme/length-limited-prefix-codes>
  - <https://github.com/stbrumme/length-limited-prefix-codes/commits/master>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/README.md>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/stbrumme/length-limited-prefix-codes>
  - <https://github.com/stbrumme/length-limited-prefix-codes/issues>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/README.md>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/Makefile>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/limitedkraftheap.c>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/limitedkraftheap.h>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/limitedkraft.c>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/packagemerge.c>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/limitedjpegdeflate.c>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/limitedbzip2.c>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/moffat.c>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/stbrumme/length-limited-prefix-codes/HEAD/fuzzer.c>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/stbrumme/length-limited-prefix-codes`) · [data/wave9/enrich/raw/github_com_stbrumme_length_limited_prefix_codes.json](../../../data/wave9/enrich/raw/github_com_stbrumme_length_limited_prefix_codes.json) (enrichment confidence 0.8)

</details>
