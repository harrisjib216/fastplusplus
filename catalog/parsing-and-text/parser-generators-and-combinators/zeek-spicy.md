# Spicy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Grammar-to-C++ parser generator for network protocols and file formats; Zeek's binpac successor, but slower than binpac on most microbenchmarks.

| | |
|---|---|
| **Beats** | binpac (Zeek's earlier protocol parser generator); not hand-written parsers |
| **Claimed result** | Not faster: evantypanski/spicy-performance (2025) has Spicy WithUnit 14.087 s vs binpac 3.809 s and Regex 10.228 vs 0.378 s even with Spicy at -O3 and binpac at -O0; the BytesUntil 'win' (0.286 vs 1.635 s) compares bytes &until against a per-element uint8[] vector and is not like for like. The 2026 Zeek post's snippet numbers read as seconds (WithUnit 9.357 s, about 1.5x faster than 2025, derived), still about 2x behind binpac. |
| **Workload** | Microbenchmarks of generated parsers on one synthetic input (an 8-byte big-endian length followed by 100,000,000 'Z' bytes): Spicy units BytesLength, BytesUntil, Regex, SinkUntil, Sync, SyncRegex, While, WithUnit, WithUnitSwitch versus binpac BytesLength, BytesUntil, WithRecord, WithRecordCase and a Zeek-plugin regex test; the 2026 follow-up post (not opened) reran similar cases inside Zeek 8.2 / Spicy 1.16 and an end-to-end Zeek run across Spicy versions. |
| **Metric** | throughput |
| **Compiler and flags** | 2025 harness: Spicy side built with spicy-config --cxx and spicy-config --cxxflags --ldflags; binpac side built with a bare 'clang++ ../bench_binpac.cc ... -o binpac-bench' and no -O flag (unoptimized baseline). 2026 post: not known. |
| **Adoption** | 303 stars; the parser framework bundled with Zeek |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/zeek/spicy) · [benchmark](https://github.com/evantypanski/spicy-performance) |

## Verdict

In evantypanski/spicy-performance (Feb-Apr 2025, std::clock CPU seconds for one parse of a 100 MB synthetic input, mean of 5, no CPU or compiler version stated) Spicy built at -O3 tied binpac built at -O0 on BytesLength (0.005 s), won BytesUntil 0.286 vs 1.635 s only against a binpac uint8[] vector, and lost WithUnit 14.087 vs 3.809 s, WithUnitSwitch 17.232 vs 4.128 s and Regex 10.228 vs 0.378 s. The 2026 zeek.org follow-up (snippet only) reports the unit cases about 1.6x faster than a year earlier, consistent with seconds (WithUnit 9.357, WithUnitSwitch 11.061; 1.51x and 1.56x derived from page data) but still about 2x behind binpac's 4.663 and 4.866.

## Use it when

- Writing a new Zeek protocol or file analyzer without hand-written C++: grammar plus EVT file, events generated for you, shipped with Zeek.
- Parsing untrusted binary network input where robustness matters more than peak throughput: generated code carries runtime checks and &synchronize-based error recovery.
- Input that arrives in chunks of arbitrary size (reassembled TCP streams, large files): parsers suspend and resume incrementally instead of needing the whole buffer.
- Grammars dominated by large bytes fields with &size or &until on a delimiter, where the 2025 harness shows Spicy at parity with binpac (BytesLength 0.005 s each) and binpac is only competitive when it uses bytestring rather than uint8[].
- Standalone C++ tools that want a generated, type-safe parser for a binary file format via spicyc -x and the parse1/parse2 prototypes.

## Skip it when

- Hot paths made of many tiny nested units or records: WithUnit took 14.087 s vs binpac's 3.809 s and WithUnitSwitch 17.232 s vs 4.128 s on 100 MB (2025 harness), and still about 2x behind after the 1.16 improvements per the 2026 zeek.org post (snippet only).
- Regex-heavy parsing of large payloads: /A\*/ over 100 MB took 10.228 s vs 0.378 s for binpac's Zeek RE_Matcher (about 27x); a character class took 13.5 s on the same input.
- When the goal is maximum raw throughput versus a hand-written C++ parser: no measurement against hand-written parsers exists, and the runtime carries fibers, hooks and location tracking that binpac and hand-written code do not.
- Deployments that cannot ship a C++ compiler or tolerate long build times when using JIT: 80-90% of compile time is spent compiling generated C++; precompile HLTOs or generate C++ ahead of time instead.
- Windows production use: MSVC support is community-contributed and not an officially supported platform.

## How it is fast

Generated C++ is compiled with -O3 -DNDEBUG in release mode (spicy-config --cxxflags), after HILTI optimizer passes: control-flow-based dataflow with constant and copy propagation (default since 1.15), removal of unused struct fields and of unused filter/sink/random-access feature code, std::move insertion for last uses (1.17). Spicy 1.16 moved parsed unit instances onto the stack instead of the heap and trimmed parser state, which the release notes credit with 20-60% microbenchmark throughput gains; 1.17 inlined the waitForInput/atEod fast paths. Fixed-size bytes fields avoid per-byte work (100 MB BytesLength in 0.005 s, derived from page data), and regex fields run on the bundled justrx library; the speed story is incremental improvement of Spicy itself, not a technique that beats binpac.

## Compared with alternatives

Pick Spicy over re2c or lexy only when the input is a binary network protocol or file format that needs incremental, robust parsing and Zeek integration; for raw C++ lexing or parsing throughput re2c (vs Ragel) and lexy (vs PEGTL) are the measured-faster choices, and Spicy itself is slower than its own baseline.

## Integration

| | |
|---|---|
| **Form** | code generator (spicyc) plus runtime libraries: generated C++ linked against libhilti-rt/libspicy-rt, or JIT-compiled .hlto shared objects; built into Zeek |
| **Dependencies** | Toolchain build: CMake &gt;= 3.15, Bison &gt;= 3.0, Flex &gt;= 2.6, Zlib; bundled 3rdparty justrx regex library; JIT mode needs a C++ compiler at runtime |
| **Minimum toolchain** | C++20 (generated code compiled with -std=c++20); Clang &gt;= 9 or GCC &gt;= 12 per the installation docs |
| **Platforms** | Linux and macOS (source, Homebrew, Zeek Docker images; binary packages were removed); Windows/MSVC unofficial; fiber runtime enabled on PowerPC64 in 1.17 |
| **Thread safety** | Parsers can run concurrently in separate threads (README: 'potentially highly concurrently'), but 1.17 fixed a Fiber constructor race on the shared stack (GH-2354) and a data race on the checkStack counter, so use 1.17+ for multithreaded hosts; Spicy global variables are process-wide (FAQ). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the catalogue numbers: run-benchmark.rb builds the Spicy side with spicy-config --cxxflags, which emits -O3 -DNDEBUG (hilti/toolchain/src/config.cc.in), but the binpac side with a bare 'clang++ ../bench_binpac.cc ...' and no -O flag, so it is Spicy -O3 against binpac -O0; Spicy's 3.7x-4.2x unit losses understate the gap to an optimized binpac.
- The only Spicy win (BytesUntil 0.286 s vs 1.635 s) compares unlike grammars: Spicy parses 'bytes &until=b"B"' while binpac/bytes_until.pac parses 'uint8[] &until(\$element == 66)', a per-element vector; the harness README itself says binpac with bytestring is 'roughly the same as Spicy'. The committed bench.cc also fills its input with 'Z' while the README table was measured on 'A's, and the While (&while=\$\$=='A') and Regex (/A\*/) units then need a 'B' terminator, so as committed those rows should hit a parse error (inferred from the grammar, not run); the binpac regex row came from a separate Zeek plugin not in the repo, with a patched Compile() call.
- Regex fields capture by default; issue #1986 reports &nosub cutting the /A\*/ case from about 10 s to about 3 s, still several times binpac's 0.3 s.
- Since 1.16 units live on the stack and the optimizer drops struct fields no Spicy code reads: very large units can exhaust the fiber stack (declare them &on-heap, 1.17), and host code reading a field may find it '(optimized out)' unless the type is declared export or compiled with --strict-public-api.

## Known shortcomings

- Downgraded claim (tier C stays): mostly slower than binpac. The readable 2025 harness evantypanski/spicy-performance has Spicy WithUnit 14.087 s vs 3.809 s and Regex 10.228 vs 0.378 s (27x slower); BytesUntil is the only win (0.286 vs 1.635 s) and that is against binpac built by bare clang++ with no -O flag. The 2026 Zeek post's snippet 'Gbps' numbers look like seconds, so the record's original ratios were backwards; zeek.org blocked.
- Enricher (evantypanski/spicy-performance): run-benchmark.rb builds Spicy with spicy-config --cxxflags (-O3 -DNDEBUG per hilti/toolchain/src/config.cc.in) and binpac with bare clang++ (-O0), so the table is Spicy -O3 vs binpac -O0 and Spicy's 3.7x-4.2x unit losses understate the gap; the only Spicy win (BytesUntil 0.286 vs 1.635 s) compares unlike grammars (Spicy bytes &until=b"B" vs a binpac uint8[] &until per-element vector; the harness README admits binpac with bytestring is roughly the same as Spicy), so it is invalid; the committed bench.cc input is 'Z' while the README table was measured on 'A's, so the While and Regex units cannot reach their 'B' terminator (inferred); the binpac regex row comes from a separate Zeek plugin not in the repo. The 2026 zeek.org snippet's about 1.6x year-over-year unit speedup fits the seconds reading (WithUnit 14.087 to 9.357 s, 1.51x derived), leaving Spicy about 2x behind binpac. Regex captures by default (issue #1986: &nosub cuts 10 s to about 3 s, still about 8x binpac); units on the stack since 1.16 can exhaust the fiber stack (&on-heap in 1.17); multithread races fixed only in 1.17 (GH-2354); in-repo CodSpeed benchmarks have no binpac baseline.

## Caveats and trade-offs

Spicy is not faster than binpac in general: in both the reachable 2025 harness and the snippet figures of the 2026 zeek.org post, Spicy loses units, unit switches and regex patterns (2x to 27x) and wins only on bytes &until. The 2025 harness's binpac baseline was compiled without any optimization flag ('Just assume the binpac compile command, I don't care enough' in run-benchmark.rb), so even the BytesUntil win is against an -O0 baseline; binpac's Zeek regex dependency was stubbed out, and its regex test needed a patched Compile() call. Timing is std::clock CPU time of a single parse call over one synthetic 100 MB input; no CPU model, compiler version or hardware stated. SNIPPET ONLY for the 2026 post (zeek.org egress-blocked): its numbers are labelled Gbps in search summaries but behave like seconds (BytesLength, the cheapest case, has the smallest value), so the record's 'Spicy about 2.0x/2.3x faster' readings were inverted; units should be confirmed from an environment that can reach zeek.org. The post's own framing (per snippets) is that Spicy stays slower in most real analyzers. Version-over-version gain (Spicy 1.16 vs 1.13, about 1.07x end to end) is not a baseline win. [retier] Harness: Spicy built with spicy-config --cxxflags (-O3 -DNDEBUG), binpac with bare clang++ (-O0); committed bench.cc input differs from the README run; binpac regex row from an out-of-repo Zeek plugin. Regex captures by default (&nosub cuts 10 s to about 3 s, issue #1986); fiber-stack exhaustion for large units before 1.17; thread races fixed in 1.17. zeek.org blocked.

Spicy is a domain-specific language that compiles grammars to C++ (JIT or ahead of time) with incremental parsing of streams of arbitrary size and many built-in features; per the Zeek author it is slower than binpac in most real analyzers because binpac is barebones and often needs hand-written C++. Spicy is a code generator, not a drop-in for hand-written C++ parsers.

## Maintenance

Actively maintained by the Zeek project (1.18.0-dev.37 on 2026-09-24, 1.17 released, CodSpeed-tracked Spicy-only microbenchmarks in spicy/runtime/tests/benchmarks) and BSD-licensed, but this entry documents a not-faster result: the only reachable Spicy-vs-binpac harness pits -O3 Spicy against -O0 binpac and shows Spicy slower on units, switches and regex.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now D.
- **Tier reason:** zeek.org is egress-blocked, so the 2026 post was not opened; the reachable predecessor harness (github.com/evantypanski/spicy-performance: bench.cc, bench_binpac.cc, custom.spicy, binpac/\*.pac, run-benchmark.rb, results in README.md) is first-party Zeek-developer code with no CPU model, and its runner builds the binpac baseline with a bare 'clang++' command and no optimization flag (an -O0 build), which caps it at C; Spicy loses most rows there.
- **Retiered** C to D: The only readable harness builds Spicy at -O3 against binpac at -O0 and its single Spicy win compares different grammars, so no valid like-for-like number exists; Spicy is slower than binpac on every comparable unit (3.7x-4.2x, understated). Directional, not faster.
- **Verifier notes:** Downgraded for an overstated (largely inverted) claim, tier stays C: the reachable harness shows Spicy 3.7x-27x slower than binpac on units and regex and faster only on BytesUntil, against an unoptimized binpac build; the record's 'Gbps' snippet numbers are most likely seconds. Metadata verified: BSD-3-Clause, 303 stars, not a fork, last commit 2026-09-24; benchmark_url moved to the openable harness repo.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-20 (wave 3); enricher (wave 3)
- **Pages the verifier opened:**
  - <https://github.com/zeek/spicy>
  - <https://github.com/zeek/spicy/commits/main>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/LICENSE>
  - <https://github.com/evantypanski?tab=repositories>
  - <https://github.com/evantypanski/spicy-performance>
  - <https://github.com/evantypanski/spicy-performance/commits/main>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/README.md>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/bench_binpac.cc>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/run-benchmark.rb>
- **Sources the enricher read:**
  - <https://github.com/zeek/spicy>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/README.md>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/VERSION>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/NEWS.rst>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/CHANGES>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/doc/installation.rst>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/doc/faq.rst>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/doc/toolchain.rst>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/doc/index.rst>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/doc/programming/parsing.rst>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/doc/programming/guidelines.rst>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/doc/host-applications.rst>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/spicy/toolchain/bin/spicy-config.cc>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/hilti/toolchain/src/config.cc.in>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/hilti/toolchain/include/config.h.in>
  - <https://github.com/zeek/spicy/tree/main/spicy>
  - <https://github.com/zeek/spicy/tree/main/spicy/runtime>
  - <https://github.com/zeek/spicy/tree/main/spicy/runtime/tests/benchmarks>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/spicy/runtime/tests/benchmarks/parsers.spicy>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/spicy/runtime/tests/benchmarks/parsing.cc>
  - <https://raw.githubusercontent.com/zeek/spicy/HEAD/spicy/runtime/tests/benchmarks/CMakeLists.txt>
  - <https://github.com/zeek/spicy/issues?q=is%3Aissue+is%3Aopen+label%3APerformance>
  - <https://github.com/zeek/spicy/issues?q=is%3Aissue+performance+OR+slow>
  - <https://github.com/zeek/spicy/issues/1986>
  - <https://github.com/zeek/spicy/issues/1987>
  - <https://github.com/evantypanski/spicy-performance>
  - <https://github.com/evantypanski/spicy-performance/commits/main>
  - <https://github.com/evantypanski/spicy-performance/tree/main/sequential>
  - <https://github.com/evantypanski/spicy-performance/tree/main/sequential/patches>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/README.md>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/bench_binpac.cc>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/custom.spicy>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/run-benchmark.rb>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/binpac/bytes_length.pac>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/binpac/bytes_until.pac>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/binpac/with_record.pac>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/binpac/with_record_case.pac>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/sequential/run-sequential.rb>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/sequential/custom.spicy>
  - <https://raw.githubusercontent.com/evantypanski/spicy-performance/HEAD/sequential/bench.cc>
  - https://zeek.org/ (EGRESS_BLOCKED)
  - https://community.zeek.org/t/are-spicy-parsers-slower-than-binpac-parsers/7794 (EGRESS_BLOCKED)
  - https://zeek.org/2026/07/spicy-vs-binpac-performance-one-year-later/ (WebSearch snippet only)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/zeek/spicy`) · [data/wave3/enrich/raw/github_com_zeek_spicy.json](../../../data/wave3/enrich/raw/github_com_zeek_spicy.json) (enrichment confidence 0.65)

</details>
