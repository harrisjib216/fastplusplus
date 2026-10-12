# Lexers and tokenizers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md)</sub>

**What these beat:** re2c, hand-written baselines the benchmark names  
**11 entries:** 1 tier A · 1 tier B · 8 tier C · 1 tier D · 10 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Accelerated-Zig-Parser (compacting SIMD tokenizer)**](validark-accelerated-zig-parser.md) | SIMD 'compacting' tokenizer for Zig source that beats the stdlib's hand-written tokenizer 2.75x on AVX-512 x86-64. | **A** | Zig | MIT AND Apache-2.0 | 🟡 stale |
| 2 | [**StreamTok (Static Analysis for Efficient Streaming…**](paper-streamtok-static-analysis-for-efficient-streaming-tokenization.md) | Rust streaming tokenizer using static max-lookahead analysis for O(1)-per-symbol maximal-munch tokenization vs flex's backtracking | **B** | Rust | no license (study only) | ⚪ unknown |
| 3 | [**Gigatoken**](marcelroed-gigatoken.md) | SIMD/cache-optimized BPE tokenizer with a Python API, roughly 7x-1300x faster encoding than HF tokenizers. | **C** | Rust | MIT | 🟢 active |
| 4 | [**flex**](westes-flex.md) | The standard lex-compatible scanner generator; table-driven DFA scanners its author timed 1.5-3.8x faster than AT&T lex in 1988. | **C** | C | BSD-3-Clause-flex | 🟢 active |
| 5 | [**logos**](maciejhirsz-logos.md) | Rust proc-macro lexer generator: compiles token/regex rules into one DFA with jump tables, aiming to beat hand-written lexers. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 6 | [**merve (nodejs CommonJS export lexer)**](nodejs-merve.md) | C++20 lexer that finds CommonJS named exports for Node's ESM import(); replaced cjs-module-lexer, making cold CJS imports about 21% faster. | **C** | C++ | Apache-2.0 OR MIT | 🟢 active |
| 7 | [**LRSTAR (DFA lexer generator)**](p7r0x7-lrstar.md) | A grammar-driven DFA-table lexer generator for C++, claiming 2x flex's throughput at similar table size. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 8 | [**CrossDB (hand-written SQL lexer/parser)**](crossdb-org-crossdb.md) | Hand-written SQL scanner/parser inside CrossDB's embedded RDBMS, claimed 10x faster than Flex/Bison-generated code. | **C** | C | MPL-2.0 | 🟡 stale |
| 9 | [**lexer-exp (SIMD NEON lexer experiments, dist1ll)**](dist1ll-lexer-exp.md) | Hand-rolled NEON SIMD lexer for a toy language; beats the Rust logos crate 20-35% on Apple M1. | **C** | Rust | MPL-2.0 | 🟡 stale |
| 10 | [**simd-lexing**](mateuszd6-simd-lexing.md) | Single-header AVX2 C99 lexer with no tables, \~3-6x faster than flex on tokenizing GCC source. | **C** | C | Zlib | 🔴 abandoned |
| 11 | [**Ragel State Machine Compiler**](adrian-thurston-colm-suite.md) | State-machine compiler that generates FSM-based scanners/parsers in 13 host languages; beats flex on one old, unmeasured example. | **D** | C++ | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
