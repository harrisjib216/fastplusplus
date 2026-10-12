# wc.apl (Dyalog APL wc, 'Beating C with Dyalog APL')

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Dyalog APL` · `BSD-2-Clause` · 🔴 abandoned

> Short Dyalog APL wc (lines, words, bytes) that ran about 2.9x faster than the stock macOS wc in a 2019 blog test.

| | |
|---|---|
| **Beats** | wc (the C wc shipped with the author's macOS) |
| **Claimed result** | Array-arithmetic version: 3.36 s on the first run, then 2.75, 2.34 and 2.36 s; windowed-reduction (2&lt;/) version: 3.33 s on the first run, then about 1.85 s; versus macOS wc user times of 5.345 to 5.549 s on the same 1.661 GB file. First naive partition-based APL version: 32.97 s. That is about 2.9-3.0x for the windowed version on warm runs and about 1.6-1.7x on its first run (derived from page data). |
| **Workload** | Counting lines, words and characters of one 1.661 GB text file (big.txt from Chris Penner's Haskell wc post, repeated), read in 256 KB blocks, timed with the dfns user-defined timing operator in Dyalog APL (wall time) against the time utility on the macOS wc (user time). |
| **Metric** | throughput |
| **Hardware** | 2.2 GHz Intel Core i7 (exact model not stated), 8 GB 1600 MHz DDR3, 11-inch early-2015 MacBook Air |
| **Compiler and flags** | Dyalog APL interpreter (free personal copy, version not stated); wc is the binary shipped with macOS (Apple text_cmds), build flags unknown. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Array-oriented primitives over 256 KB blocks: boolean membership of whitespace, then a windowed reduction (2&lt;/) to count word starts; the README does not say whether the interpreter uses SIMD or several threads. |
| **Adoption** | 7 stars |
| **Last commit** | 2019-10-26 |
| **Links** | [repository](https://github.com/ummaycoc/wc.apl) · [benchmark](https://raw.githubusercontent.com/ummaycoc/wc.apl/HEAD/README.md) |

## Verdict

On a 1.661 GB file (big.txt x256) on an early-2015 MacBook Air (2.2 GHz Core i7), the windowed-reduction Dyalog APL version took about 1.85 s wall time on warm repeat runs (3.33 s on the first run) while the macOS-shipped C wc took 5.345-5.549 s user time, about 2.9-3.0x (1.6-1.7x on the first run); the first partition-based APL version took 32.97 s. The baseline is a locale-aware scalar wc with unknown build flags, not tuned C.

## Use it when

- You already work in Dyalog APL and need line/word/byte counts of large ASCII text files from inside a session.
- Teaching or comparing array-style versus scalar-loop text processing; the README walks from a 32.97 s partition version to the 1.85 s windowed version on the same 1.661 GB file.
- Streaming over files larger than memory: the procedural versions and mem-split keep constant memory by reading fixed-size blocks.
- As a template for other block-wise boolean-array scans (counting delimiters, field separators) in APL.

## Skip it when

- As a wc replacement: no CLI, no flags, no multibyte character counting, and it needs the proprietary Dyalog interpreter (the author used a free personal copy).
- Files with CRLF, CR, VT or FF bytes: bytes 10, 11, 12 and 13 all count as line ends, so CRLF text reports twice wc's line count.
- Non-ASCII or locale-dependent text: only six bytes (9-13 and 32) count as whitespace, while wc applies the locale's iswspace(), so word counts can differ.
- If you just want a faster wc: catalogued tools such as cw and wz are command-line replacements with flags and hyperfine benchmarks against FreeBSD and GNU wc.
- Anything needing maintenance or support: 7 commits, last on 2019-10-26, no issues or releases.

## How it is fast

The file is read in 256 KB blocks with ⎕NREAD, turned into boolean vectors with membership (data∊nl, data∊sp), and counted with whole-array primitives: +/ for newlines and the windowed reduction 2&lt;/ to find nonspace-to-space transitions, plus one carry bit (lnsp) to fix words split across blocks. That replaces wc's per-byte scalar loop, which calls the locale-aware iswspace() on every byte, with a few interpreter calls per block over packed booleans. The README gives the windowed version about the same warm time (1.85 s) as a version with word counting removed, so block reading plus membership, not word counting, sets the floor.

## Compared with alternatives

Only when you are inside Dyalog APL already: ChrisPenner/wc (the Haskell post this one answers) and hwc make the same point against C wc, while cw and wz are the practical faster wc replacements with flags and hyperfine benchmarks.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Dyalog APL interpreter (proprietary; the README says a free personal copy was used) |
| **Minimum toolchain** | Dyalog APL, version not stated; the slow variant uses the ⊆ partition primitive |
| **Platforms** | Any platform Dyalog APL runs on; measured only on macOS on a 2.2 GHz Intel Core i7 (early-2015 11-inch MacBook Air) |
| **Thread safety** | Not documented; each call ties and unties its own file handle, and the split variant mutates an enclosing variable with ∘←. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness check: the README never prints the APL output next to wc's, but the test file is Chris Penner's data/big.txt (6,488,666 bytes, pure ASCII, LF line ends, no CR/VT/FF, only space, tab and LF as whitespace) repeated 256 times, which is exactly 1,661,098,496 bytes; on that input both programs' rules give identical counts, so the different line and whitespace definitions do not inflate the measured speedup.
- Timing is mixed and unscripted: APL wall time from the dfns timing operator inside a warm session (first runs 3.33-3.36 s, later about 1.85 s) against wc user time from time (5.345-5.549 s); wc system and wall time are not reported, which if anything favours wc. Single file, single machine, no variance, Dyalog version and wc build not stated.
- src/split/wc.dyalog and src/mem-split/wc.dyalog contain only the wc dfn; blockCount, blockCollapse or blockAdd and the rc operator they call exist only in the README, so those two variants do not run as checked in.
- The words dfn returns 1 for an empty vector (README admits this); the loop never calls it on an empty block, but reusing it elsewhere needs a guard.

## Known shortcomings

- Baseline is stock macOS wc with unknown flags; unequal work (wc runs a scalar per-byte loop calling iswspace() while the APL uses a fixed 6-byte whitespace set and treats bytes 10-13 as line ends); APL wall time is compared against wc user time, best numbers are warm-cache runs (1.85 s warm, 3.33 s first run vs 5.345-5.549 s), single file, no variance; the win is Dyalog's vectorised bit-packed boolean primitives, not APL codegen; needs the proprietary Dyalog interpreter; last commit 2019-10-26.
- big.txt checked: 6,488,666 bytes, pure ASCII, LF only, no CR, VT or FF; x256 is 1,661,098,496 bytes, matching the README file size, so the line and space rule differences cannot change the counts on this input and do not inflate the speed-up. Remaining flaws: APL wall time against wc user time, warm runs, no script; the windowed 1.85 s equals the README's no-word-count time; src/split and src/mem-split hold only the wc dfn with helpers that exist only in the README, so those two variants do not run as checked in.

## Caveats and trade-offs

Mixed measurements: APL figures are wall-clock times from a timing operator, wc figures are user CPU times from time; wc's wall time is not reported (for a single-threaded wc it can only be equal or higher, so this mix does not favour APL, but the comparison is still not like for like). The fast APL figures are warm-cache repeat runs; the first runs are 3.33-3.36 s. Single file, single machine, no variance, no harness script. Not the same work: the APL version treats bytes 10, 11, 12 and 13 as line ends (so CRLF counts as two lines) and a fixed six-byte whitespace set, while wc counts only '\n' and calls the locale-aware iswspace() on every byte in a scalar loop (Apple text_cmds wc/wc.c, current source; the 2019 macOS build was not checked). wc build flags unknown, so equal optimisation cannot be shown. The README itself says faster wc versions likely exist. The code is BSD-2-Clause but needs the proprietary Dyalog interpreter (free for personal use) to run. [retier] big.txt is pure ASCII with LF only (6,488,666 bytes; x256 is 1,661,098,496 bytes, matching the README), so the line and space rule differences cannot change the counts on this input. src/split and src/mem-split hold only the wc dfn with helpers that exist only in the README, so those variants do not run as checked in.

Needs the Dyalog APL interpreter, which is proprietary (free for non-commercial use). Reads the file in 256 KB blocks and keeps word-boundary state between blocks.

## Maintenance

Abandoned blog companion (7 commits, last 2019-10-26), BSD-2-Clause and a few dozen lines, so trivially copyable, but it runs only on the proprietary Dyalog interpreter and the evidence stays first-party tier C.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README numbers only: the APL code is public (README and src/{slow,procfn,windowed,split,mem-split}), but there is no timing harness, the Dyalog version is not stated, the wc build flags are unknown (macOS-shipped binary) and the CPU is given only as '2.2 GHz Intel Core i7', so it falls short of A; no independent or peer-reviewed measurement exists.
- **Verifier notes:** README numbers match the record; metadata checked on github.com (BSD-2-Clause, 7 stars, 0 forks, not a fork, not archived, 7 commits, last commit 2019-10-26 'Added Windowed Reductions', so abandoned). Shortcomings to record: baseline is the stock macOS wc (unknown flags, not shown to be -O3) doing different work (locale-aware iswspace per byte, '\n'-only line count) with a scalar loop; APL wall time against wc user time; warm-cache best runs; single file, no variance; language-level claim not supported because same_algorithm is false. aplwiki.com was unreachable (ENOTFOUND), so the bit-packing statement is from search snippets only.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-106 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ummaycoc/wc.apl/HEAD/README.md>
  - <https://github.com/ummaycoc/wc.apl>
  - <https://github.com/ummaycoc/wc.apl/commits>
  - <https://github.com/ummaycoc/wc.apl/tree/master/src>
  - <https://raw.githubusercontent.com/apple-oss-distributions/text_cmds/main/wc/wc.c>
- **Sources the enricher read:**
  - <https://github.com/ummaycoc/wc.apl>
  - <https://raw.githubusercontent.com/ummaycoc/wc.apl/HEAD/README.md>
  - <https://raw.githubusercontent.com/ummaycoc/wc.apl/HEAD/LICENSE>
  - <https://github.com/ummaycoc/wc.apl/tree/master/src>
  - <https://github.com/ummaycoc/wc.apl/tree/master/src/windowed>
  - <https://raw.githubusercontent.com/ummaycoc/wc.apl/HEAD/src/slow/wc.dyalog>
  - <https://raw.githubusercontent.com/ummaycoc/wc.apl/HEAD/src/procfn/wc.dyalog>
  - <https://raw.githubusercontent.com/ummaycoc/wc.apl/HEAD/src/windowed/wc.dyalog>
  - <https://raw.githubusercontent.com/ummaycoc/wc.apl/HEAD/src/split/wc.dyalog>
  - <https://raw.githubusercontent.com/ummaycoc/wc.apl/HEAD/src/mem-split/wc.dyalog>
  - <https://github.com/ChrisPenner/wc>
  - <https://github.com/ChrisPenner/wc/tree/master/data>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/data/big.txt>
  - <https://raw.githubusercontent.com/apple-oss-distributions/text_cmds/main/wc/wc.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/ummaycoc/wc.apl`) · [data/wave14/enrich/raw/github_com_ummaycoc_wc_apl.json](../../../data/wave14/enrich/raw/github_com_ummaycoc_wc_apl.json) (enrichment confidence 0.6)

</details>
