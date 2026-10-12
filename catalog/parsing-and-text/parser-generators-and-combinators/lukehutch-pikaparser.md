# Pika Parser (reference implementation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `MIT` · 🟢 active

> Reference implementation of pika parsing: a bottom-up, right-to-left PEG algorithm that beats ANTLR4 on simple grammars but loses on Java.

| | |
|---|---|
| **Beats** | ANTLR4 (also benchmarked against Parboiled2) |
| **Claimed result** | For the arithmetic-expression grammar, the paper states pika parsing was 'roughly the same speed' as ANTLR4/Parboiled2 for small inputs but became '10 times faster than ANTLR4' and '1000 times faster than Parboiled2' for large expressions (ANTLR4 scaled as \~n^1.21, Parboiled2 as \~n^1.9, pika as linear). For the Java grammar, the relationship reverses: the paper states pika parsing was 'up to 1000, 100 or 10 times slower' than ANTLR4 depending on input length, and about 100x slower than Parboiled2, because of a large per-character constant-factor overhead on complex grammars. |
| **Workload** | (1) 2,500 random arithmetic expressions (integers, binary ops, unary negation, parens), input lengths 5 chars to 4.8MB; (2) 5,372 real Java 6 source files from the Spring framework (avg 3.8KiB, max 76KiB, comments stripped). |
| **Metric** | latency |
| **Hardware** | Ryzen 1800X CPU, single-threaded, JRE 13.0.2. |
| **Compiler and flags** | JRE 13.0.2 (no JVM flags stated); baselines Parboiled2 1.3.1 and ANTLR4 4.8-1 |
| **Adoption** | 153 stars |
| **Last commit** | 2026-01-01 |
| **Links** | [repository](https://github.com/lukehutch/pikaparser) · [benchmark](https://arxiv.org/abs/2005.06444) |

## Verdict

Single-threaded on a Ryzen 1800X under JRE 13.0.2 (baselines ANTLR4 4.8-1 and Parboiled2 1.3.1), the arXiv preprint reports pika parsing roughly matching both baselines on small arithmetic expressions but becoming about 10x faster than ANTLR4 and 1000x faster than Parboiled2 as expression length grows to 4.8MB, because pika scales linearly versus their \~n^1.21/\~n^1.9 growth; on 5,372 real Java source files (Spring framework, comments stripped) the result reverses, with pika measured as 10-1000x slower than ANTLR4 and about 100x slower than Parboiled2.

## Use it when

- Grammars with heavy or ambiguous left recursion (e.g. left-associative expression grammars) where you want a linear-time guarantee without hand-rewriting rules to eliminate left recursion
- Very large single inputs (multi-MB, e.g. up to 4.8MB in the paper's benchmark) parsed with shallow, simple grammars, where ANTLR4/Parboiled2's superlinear scaling becomes the bottleneck
- Need built-in, no-extra-code syntax-error recovery/reporting (NavigableMap of syntax error spans) rather than hand-written recovery rules
- Prototyping in pure Java with no code-generation step or external toolchain (no `.g4` compile step, no build plugin)
- Small/greenfield projects willing to author the grammar in Pika's own text dialect and consume the `MemoTable`/`Match` API directly

## Skip it when

- Parsing complex, deeply nested grammars for real languages (Java, and by extension similarly complex languages) — the paper's own benchmark on 5,372 Spring-framework Java files shows pika 10-1000x slower than ANTLR4 and \~100x slower than Parboiled2
- You need to reuse an existing ANTLR4 `.g4` grammar or its generated visitor/listener tooling — there is no converter and the clause syntax differs
- Memory-constrained parsing of large inputs — pika memoizes every rule at every position, so memory scales with grammar size times input length
- Production use needing an actively released, versioned dependency — this is a 153-star reference implementation tied to one paper, still at `0.0.1-SNAPSHOT`, not published to Maven Central
- Left-recursive grammars where the recursion's "seed" can match zero characters — open issue #35 ("Infinite left-recursion when seed parent might be empty") documents incorrect/looping behavior in this case

## How it is fast

The pika algorithm memoizes every clause (rule) at every input position in a single bottom-up pass over the input, so each rule/position pair is computed once total rather than repeatedly re-tried via backtracking, giving guaranteed linear-time parsing independent of how the grammar recurses. Because shorter substrings are resolved before longer ones, left-recursive rules fall out of the recurrence naturally, with no seed-growing or left-recursion-elimination rewriting needed, unlike ANTLR4's ALL(\*) prediction. This linear scaling is what produces the 10x/1000x wins over ANTLR4/Parboiled2's superlinear (\~n^1.21 / \~n^1.9) scaling on multi-megabyte arithmetic expressions; on Java source the same exhaustive per-position memoization of every rule (most of which go unused at most positions) adds a large constant-factor overhead per character, which is why it loses badly there.

## Compared with alternatives

The catalogued siblings (re2c, winnow, chumsky, lexy, MPL, PAPAGENO, flap) are lexer/combinator/codegen libraries in C, Rust, or OCaml aimed at fast recognition of relatively fixed grammars; pika parser is the only one here offering built-in left-recursion support plus dynamic-programming syntax-error recovery in Java. Pick it specifically for expression-like or left-recursive grammars needing a linear-time guarantee on large single inputs — not for complex language grammars, where ANTLR4 itself (its own baseline here) or the other siblings' combinator/codegen approaches will be faster.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none at runtime; JUnit 4.13.1 for tests only (per pom.xml) |
| **Minimum toolchain** | Java 11 (pom.xml maven-compiler-plugin source/target 11); paper's benchmark ran on JRE 13.0.2 |
| **Platforms** | any (pure Java, no native/SIMD code) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: grammar must be rewritten in Pika's own PEG-like text format, and callers use a different Java API (Grammar/MemoTable/Match/Rule) instead of ANTLR4-generated parser classes |

## Gotchas

- Left recursion whose "seed" can match zero characters can loop or mis-parse (open issue #35, unresolved)
- README warns that negated character sets (`[^...]`) "will slow down the parser" since the negated rule spuriously matches at many more positions
- Every grammar rule is memoized at every input position regardless of whether it is actually needed there, so cost and memory scale with grammar size x input length even when most memo entries are unused — this is the paper's own explanation for the Java-grammar slowdown
- The repo's only runnable benchmark (src/test/java/pikaparser/Benchmark.java) compares against Parboiled2 only; there is no ANTLR4 harness in the repo, so the ANTLR4 numbers can't be reproduced from this codebase, only from the PDF plots under paper/

## Caveats and trade-offs

Not a universal speed win: the same paper shows pika is 10-1000x slower than both baselines on the Java grammar. The repo's test suite (src/test/java/pikaparser/Benchmark.java) covers only the Parboiled2 comparison; no ANTLR4 harness is in the repo (only result plots under paper/), so the ANTLR4 numbers cannot be re-run from this codebase. The paper is an arXiv preprint ('Submitted to ACM'); no peer-reviewed publication was found, which keeps it at tier C. The expression-grammar win comes from ANTLR4/Parboiled2 superlinear scaling on very long (up to 4.8M-char) single expressions.

Result is strongly grammar-dependent: faster than ANTLR4/Parboiled2 only for simple/shallow grammars (expression grammar) and markedly slower for large, deeply-nested grammars like Java's; pika parsing's benefit is mainly linear-time guarantee plus built-in left-recursion support and syntax-error recovery, not raw speed on complex languages; memoizes every rule at every position, which costs memory.

## Maintenance

Repo metadata shows a push as recently as the record's last_commit date and open issues still being answered, so it is not abandoned, but it remains a single-paper reference implementation (153 stars, `0.0.1-SNAPSHOT`, never released to Maven Central); MIT-licensed and small enough to vendor as source if you accept that unreleased-artifact status.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The arXiv paper compares pika against ANTLR4 4.8-1 and Parboiled2 1.3.1 (Ryzen 1800X, JRE 13.0.2). It is an author-run preprint (arXiv comment: 'Submitted to ACM'), and I found no peer-reviewed venue. The repo contains only the Parboiled2 harness (src/test/java/pikaparser/Benchmark.java), with no ANTLR4 harness and no JVM flags. So this is first-party evidence with partial methodology: not A, not B.
- **Verifier notes:** The quoted numbers ('roughly the same speed', '10 times faster than ANTLR4', '1000 times faster than Parboiled2', 'up to 1000, 100 or 10 times slower') all appear in Sec. 4.3-4.4. The record's claim that the paper was published at SLE 2020 is not supported: arXiv and the README cite only the preprint, and one web search found no conference or journal version. DBLP was blocked by a bot wall.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2005.06444>
  - <https://arxiv.org/pdf/2005.06444>
  - <https://github.com/lukehutch/pikaparser>
  - <https://github.com/lukehutch/pikaparser/blob/HEAD/README.md>
  - <https://github.com/lukehutch/pikaparser/blob/HEAD/src/test/java/pikaparser/Benchmark.java>
  - <https://github.com/lukehutch/pikaparser/blob/HEAD/LICENSE>
  - <https://dblp.org/search?q=pika+parsing+Hutchison>
- **Sources the enricher read:**
  - <https://github.com/lukehutch/pikaparser>
  - <https://github.com/lukehutch/pikaparser/blob/HEAD/README.md>
  - <https://github.com/lukehutch/pikaparser/blob/HEAD/pom.xml>
  - <https://github.com/lukehutch/pikaparser/blob/HEAD/src/test/java/pikaparser/Benchmark.java>
  - https://github.com/lukehutch/pikaparser/tree/HEAD (recursive file listing)
  - <https://github.com/lukehutch/pikaparser/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/lukehutch/pikaparser`) · [data/wave3/enrich/raw/github_com_lukehutch_pikaparser.json](../../../data/wave3/enrich/raw/github_com_lukehutch_pikaparser.json) (enrichment confidence 0.62)

</details>
