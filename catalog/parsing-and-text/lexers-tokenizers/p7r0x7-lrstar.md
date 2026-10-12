# LRSTAR (DFA lexer generator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Lexers and tokenizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> A grammar-driven DFA-table lexer generator for C++, claiming 2x flex's throughput at similar table size.

| | |
|---|---|
| **Beats** | flex |
| **Claimed result** | "These are TWO TIMES the speed of 'flex' created lexers and about the same size"; separately, re2c-generated lexers are described as "up to 10% faster than DFA [LRSTAR] lexers", i.e. LRSTAR does not beat re2c |
| **Workload** | General lexer/scanner generation via compressed-matrix DFA tables, compared against flex-generated lexers and re2c-generated lexers, for compiler-style grammars with many keywords |
| **Metric** | throughput |
| **Adoption** | 0 stars on this GitHub mirror; author states the DFA lexer technique has been in use "since 1987"; original project hosted on SourceForge (sourceforge.net/projects/lrstar) |
| **Last commit** | 2026-04-19 |
| **Links** | [repository](https://github.com/p7r0x7/LRSTAR) · [benchmark](https://github.com/p7r0x7/LRSTAR/blob/master/website/dfa_doc_expert.html) |

## Verdict

The only benchmark is a first-party statement on the project's own DFA documentation page: DFA-generated lexers are 'TWO TIMES the speed of "flex" created lexers and about the same size,' with no compiler, compiler flags, hardware, or benchmark corpus given. The same page states re2c-generated lexers are up to 10% faster than LRSTAR's DFA lexers, so LRSTAR is presented as beating flex but not re2c.

## Use it when

- Compiler-style grammar with a large keyword set (hundreds of keywords) where you want them recognized without a separate keyword hash lookup
- Already comfortable with a flex-like 'grammar in, C++ lexer source out' workflow and want a claimed 2x throughput bump over flex at similar generated-lexer size
- Want lexer-generation (build) time and generated table size to stay small, even if that costs a few percent of runtime speed versus re2c
- Building on Windows (MSVC, 32- or 64-bit) or Linux (g++), willing to vendor generated C++ into the build rather than link a library
- Want the lexer and an LALR parser generated from one coupled toolchain (LRSTAR proper) instead of stitching together separate lexer/parser generators

## Skip it when

- Need the fastest possible generated lexer: by the same author's own account, re2c-generated lexers are up to 10% faster than LRSTAR's DFA lexers
- Grammar needs matching-parenthesis-style recursive constructs handled in the lexer -- the author found a PDA-based approach \~5x slower and says to push that into the parser grammar instead
- Need macOS support: the author's own build docs say plainly, 'ON MAC OS X SYSTEMS: I don't know about this, sorry'
- Want an actively maintained or widely adopted project: 0 GitHub stars, 0 forks, 0 open issues, and this GitHub copy is a third-party 'maintenance fork' whose recent commits are GitHub-linguist/language-detection tweaks, not functional changes
- Need benchmark numbers you can independently verify: the only figures are first-party, with no stated compiler, flags, hardware, or benchmark corpus, and the upstream SourceForge page for the same project cites a different number ('80% faster than flex') for what appears to be the same claim

## How it is fast

The core technique is a compressed-matrix DFA transition table: each input character does one table lookup to advance state, with no backtracking and no separate hash-table lookup for keywords (keyword literals are compiled into the same DFA as identifier matching). Comment skipping is also expressed as ordinary DFA transitions rather than a separate scanning routine. The tradeoff for compile-time size is table compression (an explicit 'minimize lexer-table size' /m option), which the author says keeps generation fast even for large keyword sets, unlike more aggressive table-based generators such as re2c.

## Compared with alternatives

Pick LRSTAR/DFA over Ragel when you want a stated numeric improvement over flex (2x, even if first-party/unverified) rather than Ragel's directional-only 'faster than flex, slower than re2c' claim with no ratio; pick it over re2c-class or SIMD approaches (simd-lexing, StreamTok) when your grammar has a large keyword set and short lexer-generation time and small table size matter more to you than the last \~10% of runtime throughput.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (standalone C++, no external libraries) |
| **Minimum toolchain** | not documented as a specific standard; author reports building with GCC 4.6.1 (2014) and Visual Studio project files are checked in; code style predates modern C++ (raw pointers, static class members), no C++11+ features required |
| **Platforms** | Windows (x86/x64 via -Dx64), Linux (g++ with -DLINUX); macOS explicitly untested/unsupported per author |
| **Thread safety** | not documented; the runtime LEXER class exposes only static members (a single global lexer/token state), which suggests it is not reentrant or thread-safe |
| **Drop-in for the baseline** | partial — explain: same generate-C++-from-a-grammar workflow as flex, but a different grammar file format (.grm/.lgr instead of flex .l) and a different runtime API (LEXER::get_token() instead of yylex()), so porting from flex means rewriting the grammar and lexer call sites, not swapping a binary |

## Gotchas

- DFA lexers can't natively handle matching-parenthesis-style constructs; the author's PDA-based workaround measured \~5x slower, so that logic belongs in the parser grammar instead
- GitHub shows this repo as having no license because there is no root LICENSE file, even though doc/software_license.txt and source_dfa/license.txt both state BSD-3-Clause
- Generated LALR/DFA table files are marked read-only by the tool; the project's own setup notes warn to check your editor's read-only-file handling or regeneration can silently fail
- Default build target is 32-bit; 64-bit executables require an explicit -Dx64 (Windows) or -Dx64 command-line flag

## Known shortcomings

- Compared against flex, which is not in this category's baseline list; the '2x flex' claim has no stated compiler, hardware or corpus, and the SourceForge page says '80% faster' instead.

## Caveats and trade-offs

First-party claim with a number but no stated compiler, flags, hardware, benchmark corpus, or linked benchmark code -- capped at Tier C. The upstream SourceForge page states a different figure ('a DFA lexer generator, 80% faster than flex lexers'), so the size of the gain is inconsistent. By the same author's account, re2c lexers are up to 10% faster, so LRSTAR does not beat re2c. p7r0x7/LRSTAR is a third-party 'maintenance fork' (per its GitHub description; not a GitHub fork) of Paul B Mann's SourceForge project (last updated there 2024-07-09); its recent commits are GitHub linguist tweaks. Code is BSD-3-Clause (doc/software_license.txt, source_dfa/license.txt); GitHub reports no license because there is no root LICENSE file. The website HTML pages are '(c) Paul B Mann 2023, All rights reserved'.

Pure-DFA lexers can't natively handle matching-parenthesis-style constructs (author found a PDA-based approach \~5x slower and recommends handling that in the grammar instead); LRSTAR trades a bit of runtime speed vs re2c for much shorter lexer-generation (compile) time and smaller generated lexers, which matters for languages with large keyword sets.

## Maintenance

Listed as actively maintained (last commit 2026-04-19) and copyable (BSD-3-Clause, confirmed via doc/software_license.txt and source_dfa/license.txt despite GitHub showing no license), but this GitHub repository is a third-party 'maintenance fork' of Paul B Mann's SourceForge project and its recent commits are GitHub-linguist tweaks rather than functional work -- treat the SourceForge project as the canonical upstream.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The DFA page says 'These are TWO TIMES the speed of "flex" created lexers' and that re2c lexers are 'up to 10% faster than DFA lexers'. It gives no corpus, code, compiler, flags or hardware, so this is a first-party number without methodology: Tier C.
- **Verifier notes:** benchmark_url used branch 'main', which returns 404; the repo's only branch is 'master'. License fixed from null to BSD-3-Clause after reading the two license files, so usability changes to copyable. 0 stars and last commit 2026-04-19 verified; the canonical project is arguably sourceforge.net/projects/lrstar rather than this mirror.
- **Fields the verifier corrected:** `benchmark_url`, `baseline_in_list`, `license`, `usability`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/p7r0x7/LRSTAR>
  - <https://github.com/p7r0x7/LRSTAR/blob/main/website/dfa_doc_expert.html>
  - <https://github.com/p7r0x7/LRSTAR/blob/master/website/dfa_doc_expert.html>
  - <https://github.com/p7r0x7/LRSTAR/blob/master/doc/software_license.txt>
  - <https://github.com/p7r0x7/LRSTAR/blob/master/source_dfa/license.txt>
  - <https://sourceforge.net/projects/lrstar/>
- **Sources the enricher read:**
  - <https://github.com/p7r0x7/LRSTAR>
  - <https://github.com/p7r0x7/LRSTAR/blob/master/doc/readme.txt>
  - <https://github.com/p7r0x7/LRSTAR/blob/master/doc/linux.txt>
  - <https://github.com/p7r0x7/LRSTAR/blob/master/source_dfa/readme.txt>
  - <https://github.com/p7r0x7/LRSTAR/blob/master/website/dfa_doc_expert.html>
  - <https://github.com/p7r0x7/LRSTAR/blob/master/website/dfa_doc_basic.html>
  - <https://github.com/p7r0x7/LRSTAR/blob/master/code/lexer.h>
  - <https://github.com/p7r0x7/LRSTAR/issues>
  - <https://github.com/p7r0x7/LRSTAR/commits>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/p7r0x7/lrstar`) · [data/wave3/enrich/raw/github_com_p7r0x7_lrstar.json](../../../data/wave3/enrich/raw/github_com_p7r0x7_lrstar.json) (enrichment confidence 0.5)

</details>
