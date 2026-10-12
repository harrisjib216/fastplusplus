# asp (algebraic, staged parsing)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Preprocessors and code generators](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `OCaml` · `MIT` · 🟡 stale

> Staged, typed OCaml parser combinators (MetaOCaml) that beat ocamlyacc/ocamllex throughput on 4 of 5 grammars.

| | |
|---|---|
| **Beats** | ocamlyacc/ocamllex |
| **Claimed result** | Staged combinators beat ocamlyacc/ocamllex throughput on 4 of 5 benchmarks: arith 14.31 vs 10.96 MB/s (\~31%), pgn 33.26 vs 21.29 MB/s (\~56%), ppm 11.83 vs 6.75 MB/s (\~75%, stated explicitly in the paper text), sexp 43.65 vs 28.6 MB/s (\~53%); JSON is the exception at 60.32 vs 80.42 MB/s, \~25% SLOWER than ocamlyacc/ocamllex (all derived from Figure 8 page data) |
| **Workload** | Five parser/lexer benchmarks (arith expressions, PGN chess records, PPM images, s-expressions, JSON) comparing staged parser-combinator generated code against ocamlyacc/ocamllex-generated parsers, measured in MB/s |
| **Metric** | throughput |
| **Hardware** | AMD FX 8320, 16GB RAM, Debian Linux |
| **Compiler and flags** | BER MetaOCaml N107 (exact compiler flags not stated) |
| **Adoption** | 105 stars; PLDI 2019 paper won Distinguished Paper Award and Distinguished Artifact Award |
| **Last commit** | 2025-05-16 |
| **Links** | [repository](https://github.com/yallop/ocaml-asp) · [benchmark](https://www.cl.cam.ac.uk/~jdy22/papers/a-typed-algebraic-approach-to-parsing.pdf) |

## Verdict

Verified directly in the PLDI'19 paper (Figure 8, Section 7): staged asp combinators, compiled with BER MetaOCaml N107 and run on an AMD FX 8320/16GB Debian machine via Core_bench (95% CIs), beat ocamlyacc/ocamllex throughput on 4 of 5 benchmarks (arith 14.31 vs 10.96 MB/s, pgn 33.26 vs 21.29, ppm 11.83 vs 6.75 — the paper states 75% for PPM, sexp 43.65 vs 28.6) but lose on json, 60.32 vs 80.42 MB/s (\~25% slower). Exact ocamlopt/compiler flags used for the benchmark build are not stated in the paper.

## Use it when

- Grammar is unambiguous, non-left-recursive, and parseable with one token of lookahead (arith expressions, PGN, S-expressions measured 31-75% faster than ocamlyacc/ocamllex)
- Throughput on MB/s-scale character streams matters more than avoiding a new toolchain
- Willing to adopt BER MetaOCaml and write parsers as staged combinator code instead of .mly/.mll grammar files
- Want static rejection of ambiguous or left-recursive grammars at type-check time rather than at ocamlyacc build time
- Research/prototype context where vendoring a small, peer-reviewed artifact (PLDI'19 Distinguished Artifact Award) is acceptable

## Skip it when

- String/JSON-heavy grammars: staged asp measured \~25% slower than ocamlyacc on JSON (60.32 vs 80.42 MB/s) due to per-character string handling overhead
- Can't add BER MetaOCaml to the build; it is a distinct OCaml variant/toolchain, not stock OCaml plus opam
- Need an actively maintained library: last commit 2025-05-16, and the repo has received only toolchain-compatibility updates since 2019
- Need the unstaged/plain-combinator form for simplicity: it is 4.5-125x slower than ocamlyacc (as low as &lt;1% of ocamlyacc's JSON throughput), so only the staged path is usable in production
- Need backtracking or ambiguous-grammar support: the type system deliberately forbids ambiguous and left-recursive grammars

## How it is fast

Combinators build a first-order GADT-typed grammar representation that is type-checked for unambiguity and absence of left-recursion, which guarantees linear-time, single-token-lookahead, backtrack-free parsing. Multi-stage programming (BER MetaOCaml brackets/escapes) then specializes the generic combinator interpreter into a flat, mutually-recursive first-order program per grammar, using CPS-based binding-time improvements, 'the Trick', and type-directed branch pruning (FIRST/NULL sets) to eliminate the combinator-dispatch and redundant-peek overhead present in the unstaged version.

## Compared with alternatives

The sibling entries (RapidProto, Zserio, FlatBuffers, vtprotobuf) all beat protoc on serialization codegen, a different problem from asp's parser-combinator-vs-ocamlyacc/ocamllex target, so none is a substitute. Pick asp only when the real baseline is ocamlyacc/ocamllex, the grammar is unambiguous/LL(1), and BER MetaOCaml is acceptable in the build.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | letrec (metaocaml-letrec); the BER MetaOCaml compiler itself |
| **Minimum toolchain** | BER MetaOCaml (paper benchmarks used N107; current opam/README target the 4.11.1+BER switch; closed issues show added support for N111 and N153); not plain OCaml |
| **Platforms** | not documented beyond the paper's test machine (AMD FX 8320, Debian Linux); no explicit platform restriction in source |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | false — combinator API in OCaml/MetaOCaml source (Parse(Token).type_check, Parser(S).compile), not a .mly/.mll grammar-file replacement |

## Gotchas

- type_check rejects ambiguous or left-recursive grammars outright with no backtracking fallback, so some grammars simply cannot be expressed
- Parser(S).compile returns a MetaOCaml `code` value, not a ready function; it must be run through MetaOCaml staging/execution, an extra step versus ocamlyacc's directly generated .ml
- the Unstaged module (same combinators, no staging) is 4.5-125x slower than ocamlyacc per the paper, so don't use it expecting usable performance
- string-heavy tokens (e.g. JSON) go through per-char list conversion, which the paper identifies as the specific cause of the JSON slowdown; still unfixed as of the last commit

## Caveats and trade-offs

Baseline is ocamlyacc/ocamllex, OCaml's own yacc/lex-equivalent, not cpp/protoc/m4 directly, so baseline_in_list=false. Peer-reviewed with a public Docker artifact (Distinguished Artifact Award), but exact compiler flags are not listed in the paper, capping this at tier B rather than A.

Requires BER MetaOCaml (multi-stage programming), not plain OCaml; the paper reports the unstaged version of the same combinators is 4.5-125x SLOWER than ocamlyacc, so only the staged variant wins; also loses to ocamlyacc on the JSON benchmark due to string-handling overhead

## Maintenance

Stale: last commit 2025-05-16 was toolchain-compatibility only, and all 6 closed issues concern supporting newer BER MetaOCaml releases, not fixes or features. MIT-licensed and small enough to vendor, with a Docker-based PLDI artifact, but depends on the niche BER MetaOCaml toolchain rather than stock OCaml.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification B, tier now B.
- **Tier reason:** This is a peer-reviewed PLDI'19 paper. Figure 8 compares staged combinators vs ocamlyacc/ocamllex, the paper states the compiler (BER MetaOCaml N107) and hardware (AMD FX 8320, 16GB, Debian, Core_bench, 95% CIs), and the benchmark code is public (benchmarks/ + Makefile 'make bench'). Compiler flags are not stated in the paper, so it falls short of A.
- **Verifier notes:** Figure 8 values match: staged/ocamlyacc arith 14.31/10.96, pgn 33.26/21.29, ppm 11.83/6.75, sexp 43.65/28.6, json 60.32/80.42 (MB/s). The paper text states 'except JSON' and '75% for PPM'. The repo Makefile builds the benchmarks with default ocamlopt flags via ocamlbuild, and the current README targets the 4.11.1+BER switch rather than the paper's N107. Metadata is correct: MIT, 105 stars, last commit 2025-05-16, stale.
- **Pages the verifier opened:**
  - <https://www.cl.cam.ac.uk/~jdy22/papers/a-typed-algebraic-approach-to-parsing.pdf>
  - <https://github.com/yallop/ocaml-asp>
  - <https://github.com/yallop/ocaml-asp/blob/master/Makefile>
  - <https://github.com/yallop/ocaml-asp/blob/master/_tags>
- **Sources the enricher read:**
  - <https://github.com/yallop/ocaml-asp>
  - <https://github.com/yallop/ocaml-asp/blob/master/README.md>
  - <https://github.com/yallop/ocaml-asp/blob/master/META>
  - <https://github.com/yallop/ocaml-asp/blob/master/LICENSE>
  - <https://github.com/yallop/ocaml-asp/blob/master/benchmarks/README.md>
  - <https://github.com/yallop/ocaml-asp/blob/master/lib/asp.mli>
  - <https://github.com/yallop/ocaml-asp/blob/master/lib/asp_staged.mli>
  - <https://github.com/yallop/ocaml-asp/issues>
  - <https://www.cl.cam.ac.uk/~jdy22/papers/a-typed-algebraic-approach-to-parsing.pdf>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/yallop/ocaml-asp`) · [data/wave2/enrich/raw/github_com_yallop_ocaml_asp.json](../../../data/wave2/enrich/raw/github_com_yallop_ocaml_asp.json) (enrichment confidence 0.78)

</details>
