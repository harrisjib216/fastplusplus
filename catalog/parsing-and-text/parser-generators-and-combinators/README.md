# Parser generators and combinators

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md)</sub>

**What these beat:** Bison/Flex, ANTLR, Boost.Spirit, nom  
**12 entries:** 4 tier A · 0 tier B · 7 tier C · 1 tier D · 12 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**libpg_query**](pganalyze-libpg-query.md) | PostgreSQL's own Bison parser as a standalone C library; raw parse about 5-7x faster than sqlparser-rs in a rival's harness. | **A** | C | BSD-3-Clause | 🟢 active |
| 2 | [**re2c**](skvadrik-re2c.md) | Lexer generator emitting inline jump-based state machines for 12 languages; beats Ragel on real-world grammars, loses on synthetic repetition. | **A** | C | Public Domain (dedication… | 🟢 active |
| 3 | [**flap (fused lexing and parsing)**](yallop-ocaml-flap.md) | Fuses OCaml lexer and parser via MetaOCaml staging, generating token-free code 2-6x faster than ocamlyacc. | **A** | OCaml | MIT | 🔴 abandoned |
| 4 | [**PAPAGENO (PArallel PArser GENeratOr)**](papageno-devels-papageno.md) | Bison-style generator that emits pthreads-parallel operator-precedence parsers, up to 5.5x faster than Flex+Bison on ARM. | **A** | C | GPL-2.0 | 🔴 abandoned |
| 5 | [**chumsky**](zesterer-chumsky.md) | Rust parser-combinator library beating nom on JSON throughput, with error recovery and zero-copy output. | **C** | Rust | MIT | 🟢 active |
| 6 | [**PEGTL (JSON grammar)**](taocpp-pegtl.md) | Header-only C++ PEG parser-combinator library; its JSON grammar validates 1.7-5.5x faster than nlohmann::json::accept in lexy's benchmark. | **C** | C++ | BSL-1.0 | 🟢 active |
| 7 | [**args (Taywee)**](taywee-args.md) | Single-header C++11 command-line parser in the style of Python argparse; its 2016 benchmark ran 2.2x faster than Boost.Program_options. | **C** | C++ | MIT | 🟢 active |
| 8 | [**lexy**](foonathan-lexy.md) | C++17 parser combinator DSL that beats PEGTL on JSON validation by avoiding implicit backtracking. | **C** | C++ | BSL-1.0 | 🟢 active |
| 9 | [**winnow**](winnow-rs-winnow.md) | Zero-copy Rust parser-combinator crate, forked from nom, favoring API evolution and built-in features over strict compatibility. | **C** | Rust | MIT | 🟢 active |
| 10 | [**Pika Parser (reference implementation)**](lukehutch-pikaparser.md) | Reference implementation of pika parsing: a bottom-up, right-to-left PEG algorithm that beats ANTLR4 on simple grammars but loses on Java. | **C** | Java | MIT | 🟢 active |
| 11 | [**MPL / FastParse (kurotakazuki/mpl)**](kurotakazuki-mpl.md) | One-rule TDPL/PEG grammar crate whose static-codegen backend (FastParse) beats nom, pest, peg, winnow, chumsky on recognition benchmarks. | **C** | Rust | Apache-2.0 | 🟢 active |
| 12 | [**Spicy**](zeek-spicy.md) | Grammar-to-C++ parser generator for network protocols and file formats; Zeek's binpac successor, but slower than binpac on most microbenchmarks. | **D** | C++ | BSD-3-Clause | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
