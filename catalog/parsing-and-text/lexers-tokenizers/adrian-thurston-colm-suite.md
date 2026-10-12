# Ragel State Machine Compiler

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Lexers and tokenizers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> State-machine compiler that generates FSM-based scanners/parsers in 13 host languages; beats flex on one old, unmeasured example.

| | |
|---|---|
| **Beats** | flex |
| **Claimed result** | Ragel version "goes faster than flex version but not as fast as re2c version" -- directional claim only, no numeric ratio given |
| **Workload** | C++ tokenizer example (examples/cppscan) written three ways -- Ragel (cppscan.rl), flex (cppscan.lex) and re2c (cppscan.rec) -- and compared informally, per the Ragel 3.7 ChangeLog entry (Oct 31, 2004) |
| **Metric** | throughput |
| **Adoption** | 239 stars on adrian-thurston/colm-suite (current home); 619 stars on the archived adrian-thurston/ragel repo; Ragel-generated state machines are used in HarfBuzz (8 .rl sources in src/) and Puma's HTTP parser (ext/puma_http11/http11_parser.rl) |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/adrian-thurston/colm-suite) · [benchmark](https://github.com/adrian-thurston/colm-suite/blob/main/src/ragel/ChangeLog) |

## Verdict

The only comparison is an author's changelog entry for Ragel 3.7 (Oct 31, 2004): a C++ tokenizer example (examples/cppscan) was implemented three ways -- Ragel, flex, and re2c -- and the Ragel version was reported to run faster than the flex version but slower than the re2c version, with no numbers, no stated compiler flags, and no hardware given.

## Use it when

- You need one grammar to generate scanners/parsers for multiple host languages (e.g. C, Go, Rust, Zig) without maintaining separate lexers per language
- You're building a hand-tunable, embeddable tokenizer where you want inlined action code and control over table vs. goto-driven codegen (as HarfBuzz and Puma's http11 parser do)
- You want a long-lived, still-maintained lexer generator over one that's effectively archived (original ragel repo is archived; development continues here)
- You're comfortable learning a dedicated grammar/action-code DSL instead of reusing an existing flex .l file

## Skip it when

- You need a numbers-backed performance case against flex: the only comparison here is a 22-year-old, non-numeric changelog claim (Tier D evidence)
- You have an existing flex grammar and want a mechanical drop-in swap; Ragel's syntax and action-embedding model are different enough to require a rewrite
- You need re2c-class speed specifically: Ragel's own changelog says it did not beat re2c on the one example checked
- You need CI-verified support beyond x86-64 Linux; the project's GitHub Actions matrix only builds on ubuntu-latest, so other platforms/architectures are unverified here
- You want to avoid a bootstrap toolchain: building Ragel from source requires building Colm first, since Ragel's frontend is written in Colm

## How it is fast

The goto-driven backends (-G0/-G1/-G2) generate direct branches between states with action code inlined at each transition, instead of flex's table-driven lookup-and-dispatch loop, trading generated code size for fewer indirections per input byte. Ragel also offers table-driven (-T0/-T1) and flat-table (-F0/-F1) backends for a size/speed tradeoff. The only concrete comparison found is a 2004-era changelog note (Ragel 3.7) that its C++ tokenizer example ran faster than an equivalent flex version but slower than a re2c version, with no numbers given.

## Compared with alternatives

Pick Ragel over the numbers-backed siblings (LRSTAR's \~2x, simd-lexing's \~6.8x, CrossDB's \~10x, all vs. flex) when you need multi-target-language codegen and a widely-deployed, actively maintained generator rather than a project with an actual measured speedup; for a documented numeric win over flex specifically, LRSTAR or simd-lexing have real benchmark data and Ragel does not.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for generated code beyond the chosen host language's standard runtime; building the ragel compiler itself needs make, libtool, gcc, g++, autoconf, automake (or CMake 3.16+) |
| **Minimum toolchain** | not documented (no minimum C/C++ standard stated for generated code; build-from-source requires autotools or CMake 3.16+) |
| **Platforms** | CI covers x86-64 Linux only (GitHub Actions, ubuntu-latest); changelog references macOS build fixes (7.1.0, Aug 2026); no aarch64 CI observed |
| **Thread safety** | not documented |

## Gotchas

- Ragel's frontend is written in Colm, so building from source bootstraps Colm first, not just Ragel
- Generated code style is chosen per grammar via compiler flag (table/flat-table/goto-driven, -T/-F/-G), so speed vs. code-size is a build-time decision, not automatic
- The original standalone adrian-thurston/ragel GitHub repo is archived; active development moved to this adrian-thurston/colm-suite monorepo
- The flex/re2c comparison lives in examples/, not in the project's test suite, and has never been rerun or updated with numbers since 2004

## Known shortcomings

- Directional claim only (tier D): the flex/re2c comparison in examples/cppscan dates from Ragel 3.7 (2004) and publishes no current numbers; flex is not in this category's baseline list.

## Caveats and trade-offs

Only a directional claim with no numbers, methodology, compiler flags, or hardware -- a Tier D entry (capped at one per run), included because Ragel is a long-standing, widely used project, not because the flex claim is strong. The claim dates from Ragel 3.7 (2004), so it is about 22 years old and refers to an early code generator. Ragel is not claimed to beat re2c. The original adrian-thurston/ragel GitHub repo is archived; active development continues under adrian-thurston/colm-suite, used as the canonical URL here.

Ragel embeds action code directly into generated state machines (goto-driven), which can outgrow flex's table-driven approach in speed but requires learning Ragel's own grammar/action-code language; project's original name/repo was folded into the broader Colm language suite.

## Maintenance

Actively maintained under the colm-suite umbrella with a commit on 2026-09-25 and a 7.1.0 release (Aug 2026) adding Zig support; MIT licensed and small enough to vendor, but the original standalone ragel repo is archived so colm-suite is the current canonical home.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification D, tier now D.
- **Tier reason:** The Ragel 3.7 ChangeLog entry (Oct 31, 2004) only says the Ragel version of examples/cppscan 'goes faster than flex version but not as fast as re2c version'. There are no numbers, so Tier D. It is kept despite &lt;1k stars because Ragel is widely used (e.g. HarfBuzz src/\*.rl, Puma's ext/puma_http11/http11_parser.rl).
- **Verifier notes:** Quote verified verbatim in src/ragel/ChangeLog under 'Ragel 3.7 - Oct 31, 2004'. The comparison is in examples/, not the test suite. The benchmark_url branch 'master' 302-redirects to 'main'. MIT, not archived, last commit 2026-09-25, ragel repo archived with 619 stars: all verified. I could not verify the Gherkin usage claim, so I replaced it with the HarfBuzz and Puma usage I did verify. baseline_in_list set to false because flex is not in this category's baseline list.
- **Fields the verifier corrected:** `benchmark_url`, `baseline_in_list`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/adrian-thurston/colm-suite/blob/master/src/ragel/ChangeLog>
  - <https://github.com/adrian-thurston/colm-suite/blob/main/src/ragel/ChangeLog>
  - <https://github.com/adrian-thurston/colm-suite>
  - <https://github.com/adrian-thurston/ragel>
  - <https://github.com/harfbuzz/harfbuzz>
  - <https://github.com/puma/puma>
- **Sources the enricher read:**
  - <https://github.com/adrian-thurston/colm-suite>
  - <https://github.com/adrian-thurston/colm-suite/blob/main/README.md>
  - <https://github.com/adrian-thurston/colm-suite/blob/main/src/ragel/ChangeLog>
  - <https://github.com/adrian-thurston/colm-suite/blob/main/COPYING>
  - <https://github.com/adrian-thurston/colm-suite/blob/main/examples/cppscan.rl>
  - <https://github.com/adrian-thurston/colm-suite/blob/main/.github/workflows/build.yml>
  - <https://github.com/adrian-thurston/colm-suite/blob/main/src/ragel/CMakeLists.txt>
  - <https://github.com/adrian-thurston/colm-suite/blob/main/configure.ac>
  - <https://github.com/adrian-thurston/colm-suite/issues?q=performance>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/adrian-thurston/colm-suite`) · [data/wave3/enrich/raw/github_com_adrian_thurston_colm_suite.json](../../../data/wave3/enrich/raw/github_com_adrian_thurston_colm_suite.json) (enrichment confidence 0.4)

</details>
