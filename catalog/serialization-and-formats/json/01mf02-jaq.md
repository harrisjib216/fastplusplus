# jaq

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust reimplementation of the jq language and CLI; faster than jq 1.8.1 on 23 of 30 author filter benchmarks.

| | |
|---|---|
| **Beats** | jq 1.8.1 (also compared against gojq 0.12.18) |
| **Claimed result** | README table (ms, user CPU time): jaq-3.0 is fastest of the three on 20 of 30 benchmarks, jq-1.8.1 on 5, gojq-0.12.18 on 6. Against jq: sort 90 vs 430, group-by 260 vs 1790, to-fromjson 50 vs 350, tree-contains 90 vs 830, bf-fib 530 vs 1030, reverse 30 vs 440, kv-update 130 vs 440, str-slice 170 vs 650; upto and reduce-update round to 0 ms for jaq vs 440 and 720 ms for jq; startup ('empty' x512) 410 vs 430. jq is faster on reduce (700 vs 740), try-catch (200 vs 220), pyramid (250 vs 300), tree-flatten (330 vs 700), ack (490 vs 570), range-prop (250 vs 370) and cumsum-xy (350 vs 380). Head to head with jq, jaq is faster on 23 of 30 rows and slower on 7 (derived from page data). |
| **Workload** | 30 jq-filter benchmarks run by bench.sh: startup (empty filter x512), a Brainfuck interpreter written in jq (bf-fib), sort, group-by, reverse, min-max, add on 1,048,576 elements, object and tree updates, to-fromjson on 65,536, ack, cumsum, str-slice. |
| **Metric** | throughput |
| **Hardware** | Linux system with an AMD Ryzen 5 5500U |
| **Compiler and flags** | jaq: cargo build --release with the workspace release profile (codegen-units = 1, strip = true); rustc version not stated. jq-1.8.1 from the official Arch Linux package; gojq-0.12.18 GitHub release binary. Timing: bench.sh with 'timeout 10 /usr/bin/time -f %U' (user CPU seconds), min of 3 runs per filter row (single run for empty, bf-fib and defs); filter outputs are piped through '\| length' and discarded. |
| **Adoption** | 3.8k stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/01mf02/jaq) · [benchmark](https://raw.githubusercontent.com/01mf02/jaq/HEAD/README.md) |

## Verdict

The author ran jaq 3.0 (cargo release build, codegen-units = 1) against jq 1.8.1 (Arch Linux package) and gojq 0.12.18 on 30 jq-filter benchmarks on a Linux AMD Ryzen 5 5500U laptop, taking the minimum user CPU time of 3 runs. jaq beat jq on 23 rows and lost on 7, e.g. sort 90 vs 430 ms and group_by 260 vs 1790 ms on 1,048,576 elements, and to/fromjson 50 vs 350 ms; jq won reduce 700 vs 740 ms and tree-flatten 330 vs 700 ms.

## Use it when

- jq programs that build or reshape large arrays and objects: sort of 1,048,576 numbers 90 ms vs 430 ms in jq, group_by 260 vs 1790 ms, reverse 30 vs 440 ms, kv-update 130 vs 440 ms.
- Accumulating reduce/update loops and deep recursion in jq code (reduce-update, upto, Brainfuck interpreter bf-fib 530 vs 1030 ms), where copy-on-write and tail-call optimisation change the complexity.
- Field extraction over multi-GB NDJSON: a third-party README (6/qj, M5 Max) lists jaq at 6.7 s vs jq 18.0 s and gojq 17.2 s for `.actor.login` on 3.4 GB (not verified here).
- Embedding jq filters in a Rust service: jaq-core is no_std with alloc, forbids unsafe code, and accepts custom value types through ValT.
- Running jq syntax over YAML, CBOR, TOML or XML without a separate conversion step.

## Skip it when

- Scripts that depend on exact jq behaviour: jaq errors on float array indices and on updating null with an index, returns nan/infinite for division by zero, prints NaN as NaN, treats `. |= empty` and multi-output reduce/foreach differently, slurps multiple files into one array per file, and lacks the `?//` operator.
- Pipelines that need jq's --stream, --stream-errors, --seq, --ascii-output, --unbuffered or --jsonargs options, which jaq does not support.
- Startup-bound use (many tiny invocations): 512 empty runs took 410 ms vs 430 ms for jq 1.8.1 and 270 ms for gojq; jaq's original startup edge was over jq 1.6.
- Workloads shaped like the 7 rows jq won: reduce (700 vs 740 ms), try-catch, pyramid, tree-flatten (330 vs 700 ms; gojq 10 ms because it implements flatten natively), ack, range-prop, cumsum-xy.
- Untrusted filters or inputs: the README states jaq takes no countermeasures against resource exhaustion, so deeply nested input or unbounded recursion can overflow the stack or exhaust memory.

## How it is fast

Values are reference counted (arrays as Rc&lt;Vec&gt;, objects as Rc&lt;IndexMap&gt; hashed with foldhash) and updates go through Rc::make_mut copy-on-write, so an accumulator that is uniquely owned is mutated in place; that is why `reduce range(.) as $x ([[]]; .[0] += [$x])` finishes in under 10 ms where jq takes 720 ms. The compiler detects tail-recursive calls and executes them as tail-call exceptions that reuse the stack (tail-call optimisation in compile.rs and filter.rs), so recursive generators like `upto` run in under 10 ms versus 440 ms in jq. Filters run as lazy Rust iterators, numbers stay native isize integers (BigInt on overflow) or f64, with decimal literals kept as strings until used, and the CLI uses mimalloc by default.

## Compared with alternatives

Pick jaq when the work is running jq filter logic (sorting, grouping, updates, recursion) rather than raw parsing; for parse/serialise throughput inside C++ or Rust code, simdjson, yyjson or sonic-rs are the right tools. jist's numbers cover a single lookup on multi-GB files, whereas jaq implements the whole jq language.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | jaq-core: dyn-clone, once_cell, typed-arena; jaq-json: indexmap, foldhash, num-bigint; CLI binary: mimalloc (default feature), rustyline, env_logger, log, dirs, tempfile |
| **Minimum toolchain** | Rust 1.70 for the jaq CLI, Rust 1.69 for jaq-core (rust-version fields) |
| **Platforms** | any Rust target per the README; release binaries for Linux (musl), macOS and Windows; jaq-core is no_std plus alloc |
| **Thread safety** | README says jaq-core can be used safely in multi-threaded environments, unlike the jq C API; jaq-json values are built on Rc (non-atomic), so each value stays in one thread |
| **Drop-in for the baseline** | partial — the README calls the CLI a drop-in replacement for jq, but the manual's compatibility blocks list semantic divergences and six unsupported jq options |

## Gotchas

- Harness limits in bench.sh: it records only user CPU time (/usr/bin/time -f %U, 10 ms resolution), so system time is excluded. In issue #136 an earlier jaq lost to jq partly on system time (3.5 s vs 0.6 s, unbuffered stdout). The two 0 ms rows mean under 10 ms, so their ratios have no upper bound, and 7 of the 30 jaq-vs-jq rows differ by 10% or less (10 to 40 ms).
- Each filter gets a single number as input and pipes its output through `| length`, so apart from to-fromjson the suite measures interpreter work, not parsing or printing large JSON documents.
- del(.key) on an object swap-removes the entry (IndexMap swap_remove in jaq-json), so the last key moves into the deleted slot; open issue #436 reports `del(.b)` on {a,b,c,d} yielding {a,d,c}, while jq keeps the order.
- The table measured jaq 3.0, while crates.io is at 3.1.1 (2026-08-05). The README's command line names gojq-0.12.17 while the table and footnote say 0.12.18.

## Known shortcomings

- bench.sh reports user CPU time rather than wall time (Arch jq 1.8.1, Ryzen 5 5500U); jaq is slower than jq on 7 of 30 rows (derived from page data), the rustc version is unstated and the README names both gojq 0.12.17 and 0.12.18. Rust jq clone; moved to the json category where jq-style tools belong.
- Enricher: bench.sh times user CPU only (/usr/bin/time -f %U at 10 ms ticks), so system time is excluded (issue #136 had an older jaq at 3.5 s vs 0.6 s sys); the two 0 ms rows give unbounded ratios and 7 of 30 rows differ by 10% or less; the input is a single number with output through '| length', so no large-JSON parse or print is measured. Open bug #436: del() reorders keys (IndexMap swap_remove); table measured 3.0, crates.io at 3.1.1.

## Caveats and trade-offs

Author-run benchmarks on one laptop CPU; times are user CPU time, not wall time (system time and, for gojq, multi-threaded GC accounting differ). jq is a distro build whose flags are not restated. jaq loses to jq on 7 of 30 rows (reduce, try-catch, pyramid, tree-flatten, ack, range-prop, cumsum-xy), so the claim is 'faster on most', not all. The upto and reduce-update rows (0 ms vs 440/720 ms) reflect algorithmic differences (in-place updates, recursion handling) rather than constant-factor speed. The README's command line names gojq-0.12.17 while the table and footnote say 0.12.18. jq is a JSON filter-language interpreter, not one of the listed C++ baselines.

Reimplementation of the jq language in Rust with its own differences (stricter handling of some jq quirks); not every jq feature or CLI option is identical. Binary or crate usable from Rust.

## Maintenance

Actively maintained (commits through 2026-10-02, jaq 3.1.1 on crates.io with about 123k downloads), MIT-licensed; NLnet funded two security audits whose findings were fixed, and fuzz targets were added. Usable as a CLI or crate, with documented jq incompatibilities.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** README Performance table compares jaq-3.0 with jq-1.8.1 and gojq-0.12.18 on 30 filters; the harness is public (bench.sh plus examples/benches.json and examples/benches/\*.jq, timed with /usr/bin/time -f %U, min of 3 runs for the 27 filter rows), the build is cargo build --release with the public Cargo.toml release profile (codegen-units = 1, strip), jq comes from the Arch Linux package and the CPU is named (AMD Ryzen 5 5500U). rustc version is not stated, which matches earlier wave-12 A entries that use distro-package baselines.
- **Verifier notes:** Numbers match the README table exactly; harness, filters and build profile are public. Metadata checked on github.com: MIT, 3.8k stars, 123 forks, not a fork or archived, last commit 2026-10-02 (active). Real category from an earlier wave: json (wave 4), since jaq is a jq clone and JSON query tool; language-interpreters also fits.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/README.md>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches.json>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/upto.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/reduce-update.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/sort.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/to-fromjson.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/tree-contains.jq>
  - <https://github.com/01mf02/jaq>
  - <https://github.com/01mf02/jaq/commits>
- **Sources the enricher read:**
  - <https://github.com/01mf02/jaq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/README.md>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/jaq/Cargo.toml>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/jaq-core/Cargo.toml>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches.json>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/upto.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/reduce-update.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/sort.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/reverse.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/tree-contains.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/to-fromjson.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/examples/benches/group-by.jq>
  - <https://github.com/01mf02/jaq/tree/main/jaq-core/src>
  - <https://github.com/01mf02/jaq/tree/main/jaq-json/src>
  - <https://github.com/01mf02/jaq/tree/main/docs>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/jaq-core/src/lib.rs>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/jaq-core/src/filter.rs>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/jaq-core/src/compile.rs>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/jaq-core/src/rc_lazy_list.rs>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/jaq-core/src/path.rs>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/jaq-json/src/lib.rs>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/jaq-json/src/num.rs>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/jaq-std/src/defs.jq>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/docs/intro.dj>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/docs/corelang.dj>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/docs/advanced.dj>
  - <https://raw.githubusercontent.com/01mf02/jaq/HEAD/docs/cli.dj>
  - <https://crates.io/api/v1/crates/jaq>
  - <https://github.com/01mf02/jaq/issues?q=is%3Aissue+slow>
  - <https://github.com/01mf02/jaq/issues/111>
  - <https://github.com/01mf02/jaq/issues/136>
  - <https://github.com/01mf02/jaq/issues/436>
  - <https://github.com/6/qj>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/01mf02/jaq`) · [data/wave12/enrich/raw/github_com_01mf02_jaq.json](../../../data/wave12/enrich/raw/github_com_01mf02_jaq.json) (enrichment confidence 0.8)

</details>
