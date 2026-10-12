# Accelerated-Zig-Parser (compacting SIMD tokenizer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Lexers and tokenizers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT AND Apache-2.0` · 🟡 stale

> SIMD 'compacting' tokenizer for Zig source that beats the stdlib's hand-written tokenizer 2.75x on AVX-512 x86-64.

| | |
|---|---|
| **Beats** | Zig standard library tokenizer (hand-written, used by the Zig 0.14 self-hosted compiler) |
| **Claimed result** | 2.75x faster: 1.41 GB/s (compacting tokenizer) vs 0.51 GB/s (legacy std tokenizer); equivalently 105.25B lines-of-code/s vs 38.34B loc/s |
| **Workload** | Tokenizing a user-assembled corpus of Zig source files placed in src/files_to_parse (README says the author used the Zig compiler, ZLS and a few other Zig projects; the blog suggests cloning e.g. the Zig compiler, TigerBeetle, Bun): 3,253 files, \~47MB of source (not 47GB), processed 64 bytes at a time by the SIMD 'compacting' tokenizer; the harness prints 3,504,899,722 lines, which is implausible for \~47MB |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen AI 9 HX 370 (requires AVX-512 support) |
| **Compiler and flags** | Zig 0.14, -Doptimize=ReleaseFast |
| **Adoption** | 268 stars |
| **Last commit** | 2025-04-16 |
| **Links** | [repository](https://github.com/Validark/Accelerated-Zig-Parser) · [benchmark](https://validark.dev/posts/deus-lex-machina/) |

## Verdict

On one run on a Ryzen AI 9 HX 370 (Zig 0.14, -Doptimize=ReleaseFast) over a 3,253-file/\~47MB user-assembled Zig source corpus, the AVX-512 'compacting' tokenizer reached 1.41 GB/s versus 0.51 GB/s for the mainline std.zig.Tokenizer used by the Zig 0.14 self-hosted compiler — a 2.75x throughput gain and \~2.47x less memory — measured as a single timed pass on the author's own laptop, not an independent benchmark suite.

## Use it when

- Batch/offline tokenization of large Zig corpora on AVX-512 x86-64 hardware (recent AMD or a 'beefy' Intel server) where raw GB/s throughput matters more than portability
- You want a source-droppable reference for chunk-wise SIMD bitstring lexing tricks (perfect hashing, multiply-based movemask, sentinel padding) to adapt into your own tokenizer
- Token memory footprint matters: the byte-length token encoding gets \~2.47x less memory than std's tokenizer in the author's test
- You can pin a specific Zig 0.14 / -Doptimize=ReleaseFast toolchain and don't need long-term API stability

## Skip it when

- Any non-AVX-512 target (older x86-64, Apple Silicon/ARM, RISC-V, POWER/SPARC): the 2.75x number is AVX-512-only, and the README says the older 'Tokenizer 1' ARM/RISC-V code path 'has gone poof'
- You need a stable, embeddable tokenizer API: this is a benchmark harness with `pub fn main()` as the only public function, not a packaged module
- You need a full parser: AST generation is explicitly disabled/unimplemented in the harness (RUN_NEW_AST/RUN_LEGACY_AST off), and issue #2 ('parser design') is still open
- You need conformant Unicode handling without checking current code state: the README repeatedly notes the UTF-8 validator being turned off during development
- You want an actively maintained project: last commit 2025-04-16, and the author calls the project 'not ready for prime-time just yet'

## How it is fast

Computes per-64-byte-chunk bitstrings marking character classes (identifier/quote/comment/whitespace boundaries) via SIMD/SWAR so the cursor jumps via count-trailing-zeros instead of a branchy per-character loop. The 'compacting' variant additionally uses AVX-512 masked-compress/permute intrinsics (llvm.x86.avx512.mask.compress.q, avx512vbmi permvar) to pack token boundaries out of a chunk in parallel. Keywords/operators are matched with a compile-time perfect hash plus an array-mapped-trie bitmap (Bagwell-style) instead of DFA transitions, and tokens are stored as 1-byte lengths (with a 0-sentinel escape to a 4-byte length) rather than 32-bit start indices, cutting memory versus the stdlib tokenizer.

## Compared with alternatives

Pick this over the flex/logos-family entries (LRSTAR, simd-lexing, Ragel, lexer-exp, logos) only if your workload is specifically Zig source on AVX-512 x86-64 and you want implementation ideas for a hand-rolled chunk-wise SIMD lexer; unlike Gigatoken or CrossDB it isn't a finished, general-purpose library, and it has no parser yet, so it's a reference/benchmark, not a drop-in replacement.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | jdz_allocator (pinned in build.zig.zon); vendored simdjson/simdjzon-derived UTF-8 validation code (Apache-2.0) inside main.zig |
| **Minimum toolchain** | Zig 0.14 (build.zig.zon leaves minimum_zig_version unset; the verified benchmark used Zig 0.14 with -Doptimize=ReleaseFast) |
| **Platforms** | x86-64 with AVX-512 (avx512f/avx512bw/avx512vbmi) needed for the compacting tokenizer's benchmarked speed; SWAR and ARM NEON code paths exist in main.zig for other architectures but are not covered by the verified numbers |
| **Thread safety** | not documented; no thread usage found in the source, harness runs single-threaded |
| **Drop-in for the baseline** | partial — explain: does the same job as std.zig.Tokenizer conceptually, but the tokenizer logic lives as internal functions inside a benchmark main.zig rather than an exported library call, so using it means extracting the code yourself |

## Gotchas

- Compacting-tokenizer speed depends on specific AVX-512 intrinsics (mask.compress.q, avx512vbmi permvar/pshufb); hardware lacking these features uses different, unbenchmarked-here paths
- The harness's printed line count (3,504,899,722 lines for \~47MB of source) is implausible and looks like a counting bug — trust the GB/s figures, not the derived loc/s numbers
- Author notes legacy-tokenizer timings can shift \~15% from trivial code changes, so single-run comparisons are noisy
- UTF-8 validation has been repeatedly disabled/re-enabled during development ('Currently the utf8 validator is turned off') — verify its state before relying on Unicode correctness

## Caveats and trade-offs

Benchmark corpus is user-assembled and not published, and the figures come from one timed pass per run on the author's laptop (src/main.zig), not an independent suite; the printed line count (3.5B lines for \~47MB) and so the loc/s figures look like a counting bug, so the GB/s numbers are the meaningful ones; AVX-512 on AMD64 only; the README notes legacy-tokenizer timings can shift \~15% from trivial code changes; the blog text is CC BY-NC-SA 4.0, while the code is MIT (Apache-2.0 for the simdjson/simdjzon-derived parts)

Requires AVX-512 (x86-64-v4) hardware to hit the headline numbers; tokenizer-focused (full parser is a separate, still-evolving component of the repo); a future 512-byte-chunk version is only planned, not yet benchmarked

## Maintenance

Stale (last commit 2025-04-16) and explicitly not production-ready by the author's own account (parser unimplemented, UTF-8 validation toggled during development); MIT/Apache-2.0-licensed and small enough (\~4.8k-line main.zig) to read or vendor, but expect to extract and rewire the tokenizer code rather than import it as a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Blog and README show 'Legacy Tokenizing took 91.419ms (0.51 GB/s, 38.34B loc/s)' vs 'Tokenizing with compression took 33.301ms (1.41 GB/s, 105.25B loc/s)', '2.75x faster', with the baseline being std.zig.Tokenizer; harness is public in src/main.zig; Zig 0.14, `zig build -Doptimize=ReleaseFast` and CPU (Ryzen AI 9 HX 370) are all stated.
- **Verifier notes:** Numbers and baseline check out; the only real error was the corpus size: the page says 47.018545MB, not \~47GB (0.51 GB/s x 91.4ms is about 47MB). GitHub reports the license as NOASSERTION, and the LICENSE file is MIT plus Apache-2.0 for the simdjson-derived parts, so 'MIT AND Apache-2.0' is correct. Last commit 2025-04-16, so stale.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://validark.dev/posts/deus-lex-machina/>
  - <https://github.com/Validark/Accelerated-Zig-Parser>
  - <https://github.com/Validark/Accelerated-Zig-Parser/blob/main/LICENSE>
  - <https://github.com/Validark/Accelerated-Zig-Parser/blob/main/README.md>
  - <https://github.com/Validark/Accelerated-Zig-Parser/blob/main/src/main.zig>
- **Sources the enricher read:**
  - <https://github.com/Validark/Accelerated-Zig-Parser>
  - <https://github.com/Validark/Accelerated-Zig-Parser/blob/main/README.md>
  - <https://github.com/Validark/Accelerated-Zig-Parser/blob/main/build.zig.zon>
  - <https://github.com/Validark/Accelerated-Zig-Parser/blob/main/src/main.zig>
  - <https://validark.dev/posts/deus-lex-machina/>
  - <https://github.com/Validark/Accelerated-Zig-Parser/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/validark/accelerated-zig-parser`) · [data/wave3/enrich/raw/github_com_validark_accelerated_zig_parser.json](../../../data/wave3/enrich/raw/github_com_validark_accelerated_zig_parser.json) (enrichment confidence 0.8)

</details>
