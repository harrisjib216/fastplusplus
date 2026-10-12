# wc in Haskell ('Beating C with 80 lines of Haskell')

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Haskell` · `BSD-3-Clause` · 🔴 abandoned

> Haskell wc clone that beats single-threaded macOS wc only by splitting the file across 4 cores.

| | |
|---|---|
| **Beats** | wc (the C wc shipped with the author's macOS; also wc -mwl for UTF-8) |
| **Claimed result** | 543 MB plain text: wc 2.07 s vs multicore-wc 1.23 s and streaming-wc 1.07 s (about 1.7x and 1.9x faster, derived from page data). UTF-8: wc -mwl 5.56 s vs multicore-utf8-wc 3.07 s and streaming-utf-wc 2.67 s (about 1.8x and 2.1x, derived from page data). Single-core Haskell does not win: inlined-monoid-bs-wc 2.73 s vs wc 2.06 s on 543 MB, and 0.47 s vs 0.37 s on 90 MB. |
| **Workload** | Wall-clock time to count bytes, lines and words of a 543 MB plain-text file (and 90 MB for single-core runs); UTF-8 mode compared with wc -mwl. |
| **Metric** | throughput |
| **Hardware** | 4-core 2013 MacBook Pro with SSD |
| **Compiler and flags** | Haskell: GHC via Stack resolver lts-14.1 (stack.yaml); executable built with -O2 -threaded -rtsopts -with-rtsopts=-N plus package-wide -fstatic-argument-transformation -fspec-constr-recursive=10 -funbox-strict-fields and StrictData (package.yaml at HEAD; the article itself does not state flags). C baseline: the wc binary shipped with macOS (Apple text_cmds-68 source), build flags unknown. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Parallel (and streaming) chunked counting where each chunk yields a monoidal state that is merged across word boundaries; wc is single-threaded. No claim that Haskell code is faster per core. |
| **Adoption** | 137 stars |
| **Last commit** | 2021-08-20 |
| **Links** | [repository](https://github.com/ChrisPenner/wc) · [benchmark](https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/README.md) |

## Verdict

On a 4-core 2013 MacBook Pro with SSD and warm disk cache (a few runs averaged, no CPU model or GHC version stated), macOS's BSD-derived wc (text_cmds-68, build unknown) took 2.07 s on a 543 MB text file versus 1.23 s for a 4-thread file-split Haskell version and 1.07 s for a Streamly version (about 1.7x and 1.9x, derived from page data); with UTF-8 counting, wc -mwl took 5.56 s versus 3.07 s and 2.67 s. Single-threaded Haskell lost (2.73 s vs 2.06 s), so the speedup is 4 threads against 1.

## Use it when

- Learning or teaching how to turn a sequential fold (word counting) into an associative monoid that can be split across threads or chunks.
- Counting very large files already in the page cache, or on NVMe, on an otherwise idle multicore machine where wall time matters more than CPU time.
- ASCII text, where byte mode and wc agree on lines, words and bytes.
- As a template for a chunked parallel byte scan in Haskell with Streamly or async.

## Skip it when

- Non-ASCII UTF-8 text in byte mode: byte 0xA0 is treated as whitespace, so word counts drift from wc (issue #4: 13,306,747 vs 13,303,065 words on enwik8); Unicode whitespace beyond ASCII is never a separator in either mode.
- Single core, busy machines or CPU-budgeted jobs: single-threaded Haskell lost to macOS wc (2.73 s vs 2.06 s on 543 MB) and the 4-thread run used 4.22 s of user time, about twice wc's CPU.
- Pipes and stdin: the CLI only takes file names and has no flags to pick a subset of counts, so it is not a wc drop-in.
- Production use or a modern toolchain: pinned to Stack lts-14.1 and a 2019 Streamly git commit whose Streamly.Internal.\* modules were later renamed; GNU wc -l and Rust tools such as cw are faster per core.

## How it is fast

Word counting is made associative with a 'flux' monoid (leftmost char type, word count, rightmost char type; joining two chunks that meet mid-word subtracts one), so the file can be cut at arbitrary byte offsets. The fast modes fold each chunk on its own thread, either with one handle per capability seeked to disjoint offsets (forConcurrently) or with Streamly aheadly over about 1 MB arrays capped at numCapabilities threads, then mappend the chunk results. The per-byte fold uses strict, UNPACKed fields and INLINE pragmas with -O2 -funbox-strict-fields -fspec-constr-recursive=10; UTF-8 characters are counted as bytes that are not 10xxxxxx continuation bytes, with no decoding. There is no SIMD or memchr: each core is slower than wc, and the win is parallelism.

## Compared with alternatives

Pick it to read a short, clear parallel monoid design in Haskell; as a tool, cw (Rust, hyperfine against FreeBSD and GNU wc) or wz is the better wc replacement, hwc shows single-threaded Haskell beating GNU wc 4-6x, and wc.apl is the same challenge against the same macOS wc.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | base, bytestring, async, parallel, mtl, unix, unix-bytestring, streamly (git commit 0e98baf, internal modules); tests add hedgehog and hedgehog-classes |
| **Minimum toolchain** | Stack resolver lts-14.1 (GHC 8.6 era, 2019); newer GHC/Streamly not tested |
| **Platforms** | POSIX only (System.Posix file status, fdPread); measured on macOS, issue #4 shows it running on Linux |
| **Thread safety** | not applicable (standalone CLI); internally uses -threaded RTS with -N |
| **Drop-in for the baseline** | partial — counts match wc on ASCII files and print in wc's order (lines, words, chars, name), but the CLI needs a mode word first, has no -l/-w/-c/-m flags or stdin, and the split modes print 'Using available cores: N' to stdout |

## Gotchas

- Correctness fix after the numbers: byte-mode word counting (lazy, split, streaming, and the article's multicore-wc and streaming-wc) classifies bytes with bytestring's isSpaceChar8, which includes 0xA0, so UTF-8 continuation bytes such as the A0 in 'à' (C3 A0) split words (issue #4, enwik8: lazy 13,306,747 words vs wc 13,303,065). The 2019-10-18 fix (b89af48) only made countByteUTF8 skip continuation bytes; byte mode still has the bug, and the README (last edited 2019-10-16) still shows the pre-fix UTF-8 counter and was not re-measured.
- Repo and article diverge: at HEAD no CLI mode matches the article's non-UTF multicore-wc row (handle-utf uses the UTF-8 counter; split/split-utf read each quarter of the file into a strict ByteString with fdPread, so peak memory is roughly the file size, not the 7 MB reported), and StreamingUTF.hs and the streaming-utf command were committed on 2019-10-18, two days after the streaming tables were published, the same day Streaming.hs switched from countByteUTF8 to countByte.
- Empty input crashes: getFlux has no case for the Unknown identity, so an empty file (or an empty stream) ends in a non-exhaustive pattern error instead of printing 0 0 0.
- test/Spec.hs cannot compile (uses T.pack, the rx quasiquoter and lens operators without imports or dependencies) and would only compare the String-based Simple path on short ASCII strings; the parallel and streaming modes are not tested against wc. Timings are warm-cache averages of a few runs (open issue #5 asks for hyperfine).

## Known shortcomings

- Win only from 4-core parallelism against the single-threaded macOS wc of unknown build; single-core Haskell is slower; UTF-8 mode does less work than wc -m; -O2 with lts-14.1 from package.yaml; no CPU model.
- Correctness bug behind the numbers: byte mode (multicore-wc, streaming-wc) uses bytestring's isSpaceChar8, which counts 0xA0 as space, so UTF-8 words split (issue #4; enwik8: 13,306,747 words vs wc's 13,303,065); fix b89af48 (2019-10-18) touched only the UTF-8 counter, the README (last edited 2019-10-16) was never re-measured and still shows pre-fix code, and HEAD has no CLI mode matching the multicore-wc row. An empty file crashes (getFlux has no Unknown case) and test/Spec.hs does not compile. The win is 4 threads against 1.

## Caveats and trade-offs

Author calls the timings unscientific: averages of a few runs after warming the disk cache, no confidence intervals. Baseline is the Mac's BSD-derived C wc (text_cmds-68), not GNU wc, and its build flags are unknown; the author notes faster wc implementations exist. The win comes only from parallelism: multicore-wc runs one thread per core on disjoint file ranges and streaming-wc processes 1 MB chunks in parallel with Streamly's aheadly, against single-threaded wc; multicore user time is 4.22 s vs 2.07 s wall for wc, and single-core Haskell is slower than wc. In UTF-8 mode the Haskell code counts non-continuation bytes and classifies whitespace per byte, while wc -m decodes every character through the locale, so the work differs; a later commit (2019-10-18, 'Fix up handling of space detection on UTF-8 strings') changed space detection, and the article does not say whether the UTF-8 table was re-measured after it. CPU model not given. [retier] Correctness bug behind the numbers: byte mode (multicore-wc, streaming-wc) uses bytestring's isSpaceChar8, which counts 0xA0 as space, so UTF-8 words split (issue #4; enwik8: 13,306,747 words vs wc's 13,303,065); fix b89af48 (2019-10-18) touched only the UTF-8 counter, the README (last edited 2019-10-16) still shows pre-fix code, and HEAD has no CLI mode matching the multicore-wc row. An empty file crashes and test/Spec.hs does not compile. The win is 4 threads against 1.

Peak memory on 543 MB: wc 1.87 MB, multicore Haskell 7.06 MB, streaming 17.81 MB (8.02 MB with 100 KB chunks). The parallel version splits one file by byte offsets.

## Maintenance

Code untouched since October 2019 (the 2021 commit only added talks) and abandoned; BSD-3-Clause and small enough to vendor, but it needs porting to current Streamly and GHC, has a known word-count bug on non-ASCII text in byte mode, and is best read as a tutorial rather than used as a tool.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party article (README.md) with public Haskell code and build flags in package.yaml, but no CPU model (only '4 core 2013 Macbook Pro'), unknown build of the macOS C wc, and admittedly unscientific timing, so C.
- **Verifier notes:** All numbers match README.md (the article copy). Metadata confirmed: BSD-3-Clause, 137 stars, last commit 2021-08-20, abandoned. Shortcomings: multi-threaded Haskell vs single-threaded macOS wc of unknown build; single-core Haskell slower; UTF-8 mode does less work than wc -m; warm-cache unscientific timing; no CPU model. The 2019 post is widely known (it started a series of 'beating wc' follow-ups; general knowledge, not re-checked here), so notable despite 137 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-105 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/README.md>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/package.yaml>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/stack.yaml>
  - <https://github.com/ChrisPenner/wc>
  - <https://github.com/ChrisPenner/wc/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/README.md>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/package.yaml>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/stack.yaml>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/app/Main.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/test/Spec.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/Types.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/FileSplit.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/FileSplitUTF.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/HandleSplitUTF.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/Streaming.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/StreamingUTF.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/Parallel.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/InlinedMonoidBSFold.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/Lazy.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/LazyUTFAgnostic.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/Strict.hs>
  - <https://raw.githubusercontent.com/ChrisPenner/wc/HEAD/src/Simple.hs>
  - <https://raw.githubusercontent.com/haskell/bytestring/0.10.8.2/Data/ByteString/Internal.hs>
  - <https://github.com/ChrisPenner/wc>
  - <https://github.com/ChrisPenner/wc/tree/master/src>
  - <https://github.com/ChrisPenner/wc/commits/master>
  - <https://github.com/ChrisPenner/wc/commits/master/README.md>
  - <https://github.com/ChrisPenner/wc/commit/b89af48>
  - <https://github.com/ChrisPenner/wc/commit/7a77329>
  - <https://github.com/ChrisPenner/wc/commit/22cfbb9>
  - <https://github.com/ChrisPenner/wc/issues?q=is%3Aissue>
  - <https://github.com/ChrisPenner/wc/issues/4>
  - <https://github.com/ChrisPenner/wc/issues/5>
  - <https://github.com/ChrisPenner/wc/pulls?q=is%3Apr>
  - <https://github.com/hugodro/fudd-1brc>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/chrispenner/wc`) · [data/wave14/enrich/raw/github_com_chrispenner_wc.json](../../../data/wave14/enrich/raw/github_com_chrispenner_wc.json) (enrichment confidence 0.8)

</details>
