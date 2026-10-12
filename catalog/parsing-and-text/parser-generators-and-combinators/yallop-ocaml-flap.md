# flap (fused lexing and parsing)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `OCaml` · `MIT` · 🔴 abandoned

> Fuses OCaml lexer and parser via MetaOCaml staging, generating token-free code 2-6x faster than ocamlyacc.

| | |
|---|---|
| **Beats** | ocamlyacc (also benchmarked against Menhir's table- and code-generation backends) |
| **Claimed result** | Abstract: flap 'generates specialized token-free code that runs two to six times faster than ocamlyacc on a range of benchmarks.' Figure 11 throughput bar labels (MB/s): json flap=1359 vs ocamlyacc=236 (\~5.8x, derived from page data) and vs menhir+code=326 (\~4.2x, derived from page data); csv flap=323 vs ocamlyacc=70 (\~4.6x, derived from page data); pgn flap=286 vs ocamlyacc=67 (\~4.3x, derived from page data); ppm flap=104 vs ocamlyacc=16 (\~6.5x, derived from page data); sexp flap=213 vs ocamlyacc=76 (\~2.8x, derived from page data); arith flap=57 vs ocamlyacc=30 (\~1.9x, derived from page data). |
| **Workload** | Six grammars benchmarked with Core_bench: Portable Game Notation (pgn, 6759 games), Netpbm PPM images (ppm), S-expressions (sexp), CSV (csv, Shafranovich RFC 4180 with mandatory CRLF), JSON (json), and a small arithmetic/comparison/binding/branching language (arith). Fig. 12 shows linear running time over input sizes up to about 2 MB (sexp, arith), 0.4 MB (csv), 40 kpixels (ppm), 4000 games (pgn) and 150 messages (json). |
| **Metric** | throughput |
| **Hardware** | Single core of an Intel i9-12900K, 1GB memory, Debian Linux. |
| **Compiler and flags** | BER MetaOCaml N111 with flambda optimizations enabled; ocamlopt_flags -O3 in each benchmarks/\*/dune file |
| **Adoption** | 79 stars |
| **Last commit** | 2023-07-01 |
| **Links** | [repository](https://github.com/yallop/ocaml-flap) · [benchmark](https://arxiv.org/pdf/2304.05276) |

## Verdict

PLDI 2023 paper benchmarks six grammars (JSON, CSV, S-expressions, PGN, Netpbm PPM, an arithmetic language) with Core_bench on one core of an Intel i9-12900K (1 GB RAM, Debian Linux), compiled with BER MetaOCaml N111 + flambda and -O3; flap's fused, staged code reached 1.9x-6.5x the throughput of ocamlyacc-generated parsers per grammar (e.g. \~5.8x on JSON, \~6.5x on PPM, \~1.9x on the arithmetic grammar) and also beat both menhir table- and code-generation backends.

## Use it when

- Parsing in OCaml where the grammar is a deterministic context-free grammar with one-token lookahead (structured formats like CSV, JSON, S-expressions, PGN, Netpbm-style binary/text formats)
- Throughput-bound batch parsing of many or large documents (paper measures linear scaling up to \~2 MB inputs) where generated-code specialization amortizes
- Already using, or willing to adopt, the BER MetaOCaml staged-compilation toolchain
- Want to beat ocamlyacc- or menhir-generated parsers without hand-writing a bespoke recursive-descent parser
- Research or prototyping context where an abandoned, single-author artifact (79 stars, MIT) is an acceptable dependency to read or vendor from

## Skip it when

- Need an actively maintained, supported parsing library — last commit 2023-07-01, no releases beyond the PLDI 2023 artifact
- Grammar is ambiguous, needs backtracking/GLR-style resolution, or requires more than one token of lookahead — flap's &lt;|&gt; alternatives must be disjoint (not both nullable, non-overlapping first sets)
- Need the parser usable from C/C++ or any non-OCaml host; there is no FFI story, it is OCaml-only
- Cannot install a nonstandard compiler variant — flap requires the BER MetaOCaml switch (4.11.1+BER, optionally +flambda, or 4.14.1+BER), not stock OCaml
- Generated code size matters: GNF conversion plus lexer/parser fusion can duplicate grammar productions

## How it is fast

The grammar is converted to Greibach Normal Form so the recognizer only ever needs one token of lookahead (a deterministic GNF, DGNF), letting the compiler generate a flat, branch-predictable recognizer instead of a table-driven automaton. Lexing and parsing are fused during code generation, so no intermediate token stream or token allocation is produced between the two phases. BER MetaOCaml multi-stage programming then specializes and unrolls this recognizer into monomorphic native code per grammar, removing the interpretive/dispatch overhead that generic combinator libraries and ocamlyacc/menhir's generated tables carry.

## Compared with alternatives

The catalogued siblings (re2c, lexy, winnow, chumsky, MPL, PAPAGENO, Pika Parser) target C or Rust and aren't usable from OCaml, so there's no direct substitution; pick flap specifically when you're already in OCaml, your grammar is a deterministic single-token-lookahead CFG, and you want to beat ocamlyacc/menhir rather than hand-roll a recursive-descent parser.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | letrec, reex, reex_match, ppx_deriving (opam, runtime); ounit (test-only) |
| **Minimum toolchain** | BER MetaOCaml N111 (opam-variants 4.11.1+BER, +flambda optional, or 4.14.1+BER); dune &gt;= 2.9 with menhir 2.0 integration (used for the benchmark comparisons, not the library itself) |
| **Platforms** | CI only exercises ubuntu-latest (x86-64 Linux) with ocaml-variants.4.11.1+BER; macOS/Windows/ARM support not documented |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | false — different interface: grammars are OCaml combinator terms compiled through MetaOCaml staging, not ocamlyacc/menhir .mly/.mll grammar files |

## Gotchas

- compile returns Error string rather than raising when the grammar is ambiguous or left-recursive, so grammar bugs surface as a typing/compile-time result, not a parser exception
- &lt;|&gt; alternatives must be manually kept disjoint (no shared first token, not both nullable); the library does not infer this for you
- Requires the nonstandard BER MetaOCaml compiler switch; it will not build against a stock ocaml/opam toolchain
- Runtime dependencies (reex, reex_match, letrec) are also single-author (yallop) packages, adding transitive maintenance risk beyond flap itself

## Caveats and trade-offs

Baseline is ocamlyacc/menhir (OCaml-ecosystem yacc-family tools), not Bison/ANTLR/Boost.Spirit/nom directly, though ocamlyacc is architecturally the same class of tool as Bison; single-core, single-CPU-model microbenchmark; peer-reviewed at PLDI 2023 with a public Zenodo artifact (paper and README cite 10.5281/zenodo.7712770); project repo has had no commits since 2023-07-01.

OCaml-only (uses MetaOCaml staging), not usable from C/C++; grammars are limited to deterministic context-free expressions with a single token of lookahead (DGNF), so fully ambiguous/GLR-style grammars are out of scope; Greibach Normal Form conversion plus lexer/parser fusion can duplicate grammar productions, increasing generated code size.

## Maintenance

Abandoned: no commits since 2023-07-01, existing only as the code artifact for a single PLDI 2023 paper. MIT-licensed and small enough to read or vendor, but the BER MetaOCaml toolchain requirement makes it high-friction to actually build on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** PLDI 2023 paper compares flap against ocamlyacc and menhir (table and code backends) on six grammars. Benchmark code is public in the repo under benchmarks/ (e.g. benchmarks/json, benchmarks/csv, benchmarks/intexp; Core_bench harnesses with ocamlopt_flags -O3 in each dune file). The paper states the compiler (BER MetaOCaml N111, flambda) and CPU (Intel i9-12900K), so code, compiler, flags and CPU are all present.
- **Verifier notes:** Figure 11 text is garbled in extraction; I decoded bar labels from PDF word positions and cross-checked them against the paper's inline flap/asp and flap/normalized ratios. The record's csv ocamlyacc value (76) is actually the menhir+table bar; ocamlyacc csv is 70. The record's Zenodo DOI 10.5281/zenodo.7824835 was not seen; the paper and README cite 10.5281/zenodo.7712770.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2304.05276>
  - <https://github.com/yallop/ocaml-flap>
  - <https://github.com/yallop/ocaml-flap/blob/HEAD/README.md>
  - <https://github.com/yallop/ocaml-flap/tree/HEAD/benchmarks>
  - <https://github.com/yallop/ocaml-flap/blob/HEAD/benchmarks/csv/dune>
  - <https://github.com/yallop/ocaml-flap/blob/HEAD/benchmarks/README.md>
- **Sources the enricher read:**
  - <https://github.com/yallop/ocaml-flap>
  - <https://github.com/yallop/ocaml-flap/blob/HEAD/README.md>
  - <https://github.com/yallop/ocaml-flap/tree/HEAD>
  - <https://github.com/yallop/ocaml-flap/blob/HEAD/lib/flap.mli>
  - <https://github.com/yallop/ocaml-flap/blob/HEAD/flap.opam>
  - <https://github.com/yallop/ocaml-flap/blob/HEAD/dune-project>
  - <https://github.com/yallop/ocaml-flap/blob/HEAD/.github/workflows/test.yml>
  - <https://github.com/yallop/ocaml-flap/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/yallop/ocaml-flap`) · [data/wave3/enrich/raw/github_com_yallop_ocaml_flap.json](../../../data/wave3/enrich/raw/github_com_yallop_ocaml_flap.json) (enrichment confidence 0.78)

</details>
