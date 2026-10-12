# PAPAGENO (PArallel PArser GENeratOr)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `GPL-2.0` · 🔴 abandoned

> Bison-style generator that emits pthreads-parallel operator-precedence parsers, up to 5.5x faster than Flex+Bison on ARM.

| | |
|---|---|
| **Beats** | GNU Bison + GNU Flex (sequential LALR(1) parser/lexer) |
| **Claimed result** | Text (Sec. 6, 'Comparison with Flex and Bison'): the PAPAGENO-generated parallel lexer/parser shows 'a significant speedup with respect to the state-of-the-art of tool generated parsers, for all but the smallest test-bench files' on both server and mobile platforms. On the ARM platform the paper reports 'a speedup of up to 5.5x, as a combination of the parallel processing technique on multiple cores and the lesser computational requirements with respect to a classic LALR(1) parser.' Figure 13b (JSON, 16-core server) is a 3D surface plot whose speedup axis runs to 7; the text gives no exact peak value against Flex+Bison. The text's explicit 'maximum achieved speedup is 7x' refers to parallel lexing vs a sequential Flex lexer (Fig. 11a), not to the full Flex+Bison comparison. |
| **Workload** | Lexing+AST-construction of real-world JSON files (2.7KiB-75MiB: online-shop shopping list, AdBlocker config, Gospel of John, Italian food-consumption stats, Google Books n-gram stats, UK CKAN index) and Lua files (7KiB-35MiB, built by concatenating files from LucasArts' Grim Fandango codebase), on a 16-core x86_64 Opteron server and a 4x Cortex-A15/4x Cortex-A7 ARM board. |
| **Metric** | throughput |
| **Hardware** | Server: quad-Opteron 8378 (16 physical cores, 4 sockets), Ubuntu 14.04 x86_64. Mobile: Odroid-XU Lite, Exynos 5 Octa (4x Cortex-A15 @1.4GHz + 4x Cortex-A7, big.LITTLE, using only the 4 A15 cores), Debian 7.6 armv7l. |
| **Compiler and flags** | gcc 4.9.1, -O3 -march=native |
| **Adoption** | 14 stars |
| **Last commit** | 2015-04-20 |
| **Links** | [repository](https://github.com/PAPAGENO-devels/papageno) · [benchmark](https://re.public.polimi.it/retrieve/handle/11311/971391/67830/papaj-final.pdf) |

## Verdict

The paper (Barenghi et al., preprint for Science of Computer Programming) benchmarks the PAPAGENO-generated parallel lexer/parser against the authors' own sequential Flex+Bison LALR(1) reference parser, both built with gcc 4.9.1 -O3 -march=native, on a 16-core quad-Opteron 8378 server and a 4x-Cortex-A15 Odroid-XU ARM board, over real-world JSON (2.7KiB-75MiB) and Lua (7KiB-35MiB) inputs. It reports up to 5.5x speedup on the ARM board and a separate maximum 7x speedup for parallel lexing alone vs. sequential Flex (not vs. the full Flex+Bison pipeline); the 16-core server JSON comparison (Fig. 13b) is a 3D plot with no stated exact peak number against Flex+Bison.

## Use it when

- Files large enough for parallelism to amortize thread overhead (paper shows real gains mainly on multi-MB inputs, up to 75MiB JSON / 35MiB Lua)
- A grammar that is already an Operator Precedence Grammar, or small enough to convert without exploding the rule set (e.g. arithmetic expressions, JSON)
- Batch/offline C parsing on multi-core x86_64 servers or ARM big.LITTLE boards where lexing/parsing is a proven bottleneck
- You can vendor and maintain generated C source yourself (Python 2.x generator, no upstream releases since 2015)

## Skip it when

- General LALR(1) or ambiguous/context-free grammars: converting real-world Lua to OPG+Fischer-normal-form blew productions up from 144 to 8547 plus required manual lexer transforms
- Small or streaming inputs (KB-scale) — paper reports negligible or negative speedup there from thread migration/NUMA overhead
- Anywhere you need Bison's GLR mode or ANTLR-style handling of ambiguous grammars — OPG is a strict LALR(1) subset
- Projects needing an actively maintained tool or Python 3 support: last commit 2015-04-20, generator is Python 2.x only, one unresolved GitHub issue
- Anywhere a true drop-in Bison/Flex replacement is required — grammar syntax is Bison-like but the generated parser's call signature and build process differ

## How it is fast

Exploits the OPG property that the shift/reduce decision between two adjacent terminals depends only on a fixed precedence relation, not on global parse state, so the input can be split into chunks and reduced independently on separate POSIX threads with no wasted re-computation when recombining partial trees. Lexing can likewise be split into an independent parallel pass (test/JSON_parallel_lexer). The README states throughput scales close to linearly with thread count on JSON workloads.

## Compared with alternatives

Pick PAPAGENO only when the win you need is multi-core parallelism on a Bison-compatible C grammar that is (or can be forced into) Operator Precedence form; the catalogued siblings (flap, re2c, Pika Parser, winnow, chumsky, MPL/FastParse) are all single-threaded OCaml/Rust tools that get their speedups from fused lexing, code generation, or SIMD/table specialization, not from splitting work across cores, so they don't compete on this axis.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Python 2.x to run the generator; GNU Flex, gcc/clang, Make, and POSIX threads (pthreads) to build the generated parser |
| **Minimum toolchain** | Python 2.x (generator); C with pthreads and GNU Flex for the generated code (paper's own build used gcc 4.9.1, -O3 -march=native) |
| **Platforms** | x86_64 and ARM (tested on Cortex-A15/A7); requires a POSIX threads implementation (tested on Linux NPTL) |
| **Thread safety** | not documented beyond the explicit `parse(threads, file_name)` entry point; no stated guarantees about concurrent parse() calls within one process |
| **Drop-in for the baseline** | partial — explain: grammar file uses Bison-like syntax and reuses a normal Flex .l lexer, but the grammar must be an Operator Precedence Grammar and the generated parser has its own call signature instead of yyparse() |

## Gotchas

- Generator statically rejects non-OPG grammars (consecutive nonterminals, precedence conflicts) and only prints diagnostics — you must manually restructure the grammar
- Real-world grammars can blow up drastically under OPG conversion: Lua went from 144 to 8547 productions in the paper's benchmark
- README states terminal/nonterminal names may not start with '_'
- Generator itself is Python 2.x only; no indication of a Python 3 port

## Caveats and trade-offs

Benchmark authored by the tool's own developers, comparing against a Flex+Bison reference parser they built themselves (not the JSON/Lua ecosystem's own production parsers); smallest test files show negligible or no speedup; only Operator-Precedence-compatible grammars are supported, not general context-free/ambiguous grammars that Bison's GLR mode or ANTLR can handle; project has had no commits since 2015.

Requires the grammar to be restructured as an Operator Precedence Grammar (a strict subset of LALR(1)); converting a real LALR(1) Lua grammar to OPG+Fischer-normal-form blew productions up from 144 to 8547; Lua required manual token-disambiguation and semicolon-insertion transforms in the lexer; parser is generated as C source using POSIX threads, so parallelism only pays off once input is large enough (small files show little or negative speedup from thread migration/NUMA overhead).

## Maintenance

Abandoned: no commits since 2015-04-20, GPL-2.0 licensed, one open GitHub issue and no CI/releases; small enough (a handful of C files plus a Python 2.x code generator) to vendor and maintain yourself if you accept the OPG grammar restriction.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Paper (preprint submitted to Science of Computer Programming) compares the PAPAGENO parallel lexer+parser against a sequential Flex+Bison LALR(1) analyzer (Fig. 13). The Flex+Bison baseline code is public in the repo at test/benchmarks/bison_baselines/{json,lua}, alongside the PAPAGENO test harnesses in test/JSON and test/Lua. The paper states gcc 4.9.1, -O3 -march=native and the CPUs (quad Opteron 8378; Exynos 5 Octa).
- **Verifier notes:** The default branch's last commit is 2015-04-20; repo pushed_at is 2015-09-11, which is probably a non-commit push. The record's 'roughly 7x' Fig. 13b figure was a chart-axis reading, so I reworded it to say the text gives no exact value. The rest of the record matches the paper.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `last_commit`
- **Pages the verifier opened:**
  - <https://re.public.polimi.it/retrieve/handle/11311/971391/67830/papaj-final.pdf>
  - <https://github.com/PAPAGENO-devels/papageno>
  - <https://github.com/PAPAGENO-devels/papageno/tree/master/test/benchmarks/bison_baselines>
- **Sources the enricher read:**
  - <https://github.com/PAPAGENO-devels/papageno>
  - <https://github.com/PAPAGENO-devels/papageno/blob/master/README.md>
  - https://github.com/PAPAGENO-devels/papageno (git tree, recursive)
  - <https://github.com/PAPAGENO-devels/papageno/blob/master/doc/manual.txt>
  - <https://github.com/PAPAGENO-devels/papageno/blob/master/test/JSON/Makefile>
  - <https://github.com/PAPAGENO-devels/papageno/blob/master/include/opp.h>
  - <https://github.com/PAPAGENO-devels/papageno/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/papageno-devels/papageno`) · [data/wave3/enrich/raw/github_com_papageno_devels_papageno.json](../../../data/wave3/enrich/raw/github_com_papageno_devels_papageno.json) (enrichment confidence 0.78)

</details>
