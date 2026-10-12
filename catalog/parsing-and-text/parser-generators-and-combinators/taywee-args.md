# args (Taywee)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Single-header C++11 command-line parser in the style of Python argparse; its 2016 benchmark ran 2.2x faster than Boost.Program_options.

| | |
|---|---|
| **Beats** | Boost.Program_options (also TCLAP) |
| **Claimed result** | README 'How fast is it?': 'about 65% faster than TCLAP and 220% faster than boost::program_options'. Run output in the README: args 0.895472 s, tclap 1.45001 s, boost::program_options 1.98972 s. Ratios derived from page data: boost::program_options takes about 2.22x as long as args, TCLAP about 1.62x as long. |
| **Workload** | 100,000 iterations of constructing a parser and parsing the 13-token command line '-i 7 -c a 2.7 --char b 8.4 -c c 8.8 --char d' (one int flag, a char list flag, a positional list of doubles), with asserts on the parsed values. |
| **Metric** | throughput |
| **Compiler and flags** | g++ -obench bench.cxx -O2 -std=c++11 -lboost_program_options (compiler version and Boost version not stated) |
| **Adoption** | 1.6k stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/Taywee/args) · [benchmark](https://github.com/Taywee/args) |

## Verdict

The author's micro-benchmark (g++ -O2 -std=c++11; compiler, Boost and TCLAP versions and CPU not stated) builds a parser and parses the 13-token line '-i 7 -c a 2.7 --char b 8.4 -c c 8.8 --char d' 100,000 times with asserts enabled: args 0.895 s, TCLAP 1.450 s, Boost.Program_options 1.990 s, so Boost takes 2.22x and TCLAP 1.62x as long (about 9 microseconds per iteration for args). The run dates from args 2.0.0 in May 2016, and the Boost loop skips po::notify.

## Use it when

- A C++11 CLI tool that wants argparse-style features (typed flags, lists, maps, counters, help text, bash completion) from one dependency-free header.
- Programs with non-trivial option logic: nested validation groups (Xor, AtLeastOne, AllOrNone, user predicates) or git-like subcommands with shared arguments.
- Code that parses many command lines in-process (test harnesses, REPL or chat-command front ends reusing CLI syntax), where about 9 microseconds per build-and-parse (2016 figure) beats Boost.Program_options and TCLAP.
- Projects that cannot take Boost or a compiled library: copy args.hxx, or install via CMake, meson, conan, buck or tipi.

## Skip it when

- Choosing on speed alone: a CLI parses once per process, the gap is microseconds, and the published numbers are from args 2.0.0 (May 2016), not the current 6.6.0.
- You need config-file or environment-variable sources merged with the command line, as Boost.Program_options offers; args parses argument vectors only.
- Order-sensitive flags (like GNU find), mixed prefix styles in one parser, or a positional list before other positionals: the README says the library will never support these.
- Non-ASCII flag names or help text with combining characters: UTF-8 support is limited and unnormalized, and Windows-style '/' short prefixes have had an open bug (#26) since 2017.
- You want new features or friendly group-validation messages: the author calls it feature-complete, and failed group validation only reports that the whole expression failed.

## How it is fast

No named algorithm: the speed comes from a light object model rather than a clever parser. Each argument object stores its typed value directly, the parser walks the argument vector once and assigns positionals as it goes (the README cites this choice 'for better simplicity and speed'), and flag lookup asks each child's Matcher, which holds the short and long names in an unordered_set&lt;char&gt; and an unordered_set&lt;string&gt;. Integers are converted with strtoll/strtoull and other types with an istringstream pinned to the classic locale.

## Compared with alternatives

The catalogued siblings (lexy, re2c, winnow, chumsky, flap, the pika parser) parse text against grammars, and none of them parses argv. Pick args when the input is a command line, and one of those when you are parsing a language or file format.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only) |
| **Minimum toolchain** | C++11 (meson default cpp_std=c++11); CMake 3.10 for the package; old MSVC (_MSC_VER &lt;= 1800) gets a noexcept shim |
| **Platforms** | any; CI builds and tests on ubuntu-latest, macos-latest and windows-latest in Debug and Release, plus a meson job on Ubuntu |
| **Thread safety** | not documented; parser and argument objects hold mutable parse state, so give each thread its own parser |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark provenance: the README's run output (0.895472 s args, 1.45001 s TCLAP, 1.98972 s Boost) is byte-identical in the README at tag 2.0.0 (May 2016), where the benchmark used the pre-4.0.0 API (ArgFlag, ArgFlagList, PosArgList, integer.value). The source was later rewritten to ValueFlag/PositionalList but never re-run, so the numbers measure args 2.0.0 and a 2016-era TCLAP and Boost. Today's constructors run duplicate-flag detection over the whole parser tree on every flag added, rebuilding two hash sets each time, which makes construction quadratic in flag count, and that construction is inside the timed loop; current speed is unmeasured.
- Errors and control flow use exceptions: --help arrives as a thrown args::Help, completion as args::Completion, bad input as ParseError, ValidationError or RequiredError, and a duplicate flag name throws ParseError from the flag's constructor, outside the try block around ParseCLI in the README examples. Define ARGS_NOEXCEPT to get error codes through GetError() instead.
- Integer values go through strtoll/strtoull with base 0, kept on purpose in PRs #164 and #177: '0x10' parses as 16, '010' as 8, and '08' is rejected.
- A ValueFlag given twice silently keeps the last value unless it was built with Options::Single (then ExtraError), and the first PositionalList swallows every positional after it.

## Known shortcomings

- README micro-benchmark of parser construction plus one parse (g++ -O2, no CPU model, compiler or Boost version; source only in the README): 2.22x vs boost::program_options and 1.62x vs TCLAP (derived). Loose fit for parser-generators-and-combinators (CLI parser).
- Provenance flaw: the README run output (0.895472 / 1.45001 / 1.98972) has been byte-identical since tag 2.0.0 (May 2016, pre-4.0.0 API with ArgFlag/PosArgList); the code was renamed later and the benchmark never re-run, so the numbers measure args 2.0.0, not 6.6.0, which runs duplicate-flag detection per flag registration (quadratic construction inside the timed loop). Gotchas: integers parse with base 0 ('010' is 8, '08' rejected); repeated ValueFlag is last-wins.

## Caveats and trade-offs

First-party micro-benchmark whose full source is printed in the README, but no CPU model, compiler version, Boost version or date is given, so it cannot reach tier A; the source exists only in the README (no bench.cxx at the repo root). Each iteration times building the parser object plus one parse of a 13-token line, about 9 microseconds per iteration for args, which is irrelevant for a CLI that parses once per process. The author says the command line was trimmed to what TCLAP could handle. The README percentage wording is loose: the stated '220% faster' than boost::program_options matches a time ratio of about 2.2x (about 122% higher throughput), and '65% faster' than TCLAP is about 62% by time ratio (derived from page data). Nothing compares against getopt. The Boost loop copies the argument vector like the others but then parses the original carguments and never calls po::notify, so it does slightly less than a full Boost.Program_options use; asserts are enabled (#undef NDEBUG) in all three loops. Numbers are undated and probably from an old Boost release. Boost.Program_options is not one of the category's listed baselines (Bison/Flex, ANTLR, Boost.Spirit, nom): args is a command-line argument parser filed under parser-generators-and-combinators for lack of a closer category. The author describes the library as feature-complete (bug fixes still merged). [retier] README timings (0.895472 / 1.45001 / 1.98972 s) are byte-identical since 2.0.0 (May 2016) and measure the pre-4.0.0 API; never re-run on 6.6.0, which adds per-registration duplicate-flag detection (quadratic construction inside the timed loop). Single machine, no CPU or flags.

Single-header C++11 library, MIT. Python-argparse-like API with static typing, nestable group logic, help generation and bash completion. UTF-8 support is limited (no normalization). The author calls it feature-complete: bug fixes only, no new major functionality.

## Maintenance

Feature-complete but still patched: 6.6.0 was tagged 2026-07-22, the last commit is 2026-10-05, and many 2026 hardening PRs went in; MIT, a single header with CI on Linux, macOS and Windows, safe to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party micro-benchmark whose full source and build command (g++ -O2 -std=c++11) are printed in the README 'How fast is it?' section, but no CPU model, compiler version or Boost/TCLAP version is given, and the source is not checked in as a file (no bench.cxx at the repo root), so it cannot reach A; no independent measurement.
- **Verifier notes:** README numbers and the derived ratios (2.22x vs boost::program_options, 1.62x vs TCLAP) check out against the printed run output; the harness is symmetric (each loop builds the parser and parses once). Fixed baseline_in_list to false since Boost.Program_options is not in the category's baseline list. Category fit is loose (CLI argument parser, not a parser generator), but no wave-3 category fits better. MIT, 1.6k stars, 187 forks, last commit 2026-10-05, author calls it feature-complete.
- **Fields the verifier corrected:** `baseline_in_list`, `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher (wave 3)
- **Pages the verifier opened:**
  - <https://github.com/Taywee/args>
  - <https://github.com/Taywee/args/commits>
  - <https://raw.githubusercontent.com/Taywee/args/HEAD/README.md>
  - <https://raw.githubusercontent.com/Taywee/args/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/Taywee/args>
  - <https://github.com/Taywee/args/commits/master>
  - <https://github.com/Taywee/args/commits/2.0.0>
  - <https://github.com/Taywee/args/tags>
  - <https://github.com/Taywee/args/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/Taywee/args/pulls?q=is%3Apr+integer>
  - <https://github.com/Taywee/args/pull/177>
  - <https://github.com/Taywee/args/pull/164>
  - <https://raw.githubusercontent.com/Taywee/args/HEAD/README.md>
  - <https://raw.githubusercontent.com/Taywee/args/HEAD/args.hxx>
  - <https://raw.githubusercontent.com/Taywee/args/HEAD/CHANGELOG>
  - <https://raw.githubusercontent.com/Taywee/args/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Taywee/args/HEAD/meson.build>
  - <https://raw.githubusercontent.com/Taywee/args/HEAD/conanfile.py>
  - <https://raw.githubusercontent.com/Taywee/args/HEAD/.github/workflows/test.yaml>
  - <https://raw.githubusercontent.com/Taywee/args/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Taywee/args/2.0.0/README.md>
  - <https://raw.githubusercontent.com/Taywee/args/3.0.0/README.md>
  - <https://raw.githubusercontent.com/Taywee/args/4.0.0/README.md>
  - <https://raw.githubusercontent.com/Taywee/args/5.0.0/README.md>
  - <https://raw.githubusercontent.com/Taywee/args/6.0.0/README.md>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/taywee/args`) · [data/wave3/enrich/raw/github_com_taywee_args.json](../../../data/wave3/enrich/raw/github_com_taywee_args.json) (enrichment confidence 0.8)

</details>
