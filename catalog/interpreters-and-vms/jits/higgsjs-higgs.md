# Higgs (higgsjs/Higgs JavaScript JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `D` · `BSD-3-Clause` · 🔴 abandoned

> Research JavaScript JIT in D using lazy basic block versioning; per paper snippets it beats V8's old non-optimizing compiler, not Crankshaft.

| | |
|---|---|
| **Beats** | V8 (its baseline compiler; its optimizing Crankshaft compiler is faster than Higgs) |
| **Claimed result** | Snippet only (paper not opened): with typed shapes and shape propagation, Higgs outperforms the V8 baseline (non-optimizing) compiler on all but one of 26 benchmarks, with speedups of up to 682%; it lags behind V8's Crankshaft (run without inlining, per one snippet), which performs 49% better on average. Abstract (snippet): the techniques eliminate on average 48% of type tests, reduce code size by 17% and reduce execution time by 25% versus Higgs with plain polymorphic inline caches. |
| **Workload** | 26 JavaScript benchmarks run on Higgs, a basic-block-versioning JIT for x86-64, versus V8 compilers, as reported in the DLS 2015 paper 'Extending Basic Block Versioning with Typed Object Shapes' (arXiv 1507.02437). |
| **Metric** | throughput |
| **Adoption** | 882 stars |
| **Last commit** | 2023-06-09 |
| **Links** | [repository](https://github.com/higgsjs/Higgs) · [benchmark](https://arxiv.org/abs/1507.02437) |

## Verdict

Search snippets of arXiv 1507.02437 (the paper itself was not opened, and its venue is unconfirmed) say that on 26 SunSpider and V8-suite benchmarks, Higgs with typed shapes outperforms V8's non-optimizing full-codegen compiler (removed from V8 in 2017) on 25, with speedups of up to 682%, while V8's Crankshaft is 49% faster on average. Hardware, V8 version, flags and timing method are unknown.

## Use it when

- Studying or teaching lazy basic block versioning and typed shapes in a small, readable JIT. The same author later applied the technique in YJIT for CRuby.
- Reproducing or extending the Higgs papers: the 26-benchmark list (19 SunSpider plus 7 V8 Benchmark Suite programs) and its runner ship in source/, and --stats prints counters for type tests, shape tests, versions and code size.
- Experiments on x86-64 Linux with a D toolchain where comparing a BBV JIT against interpreters or baseline compilers is the point, not production JavaScript.

## Skip it when

- Any production JavaScript: modern V8 (Ignition/Sparkplug/Maglev/TurboFan), SpiderMonkey or JavaScriptCore are far ahead. By the record's snippets, even 2015-era Crankshaft beat Higgs by 49% on average.
- Code that needs ES2015+ syntax (let, arrow functions, classes, template strings, for-of), typed arrays, Node or browser APIs, the 'with' statement, or eval over local variables.
- Non-x86-64 or non-POSIX targets: the JIT emits x86-64 only and the README requires a POSIX OS, so there is no AArch64 (Apple Silicon), Windows or 32-bit support.
- Embedding in a C or C++ application: it is a D program with its own runtime and garbage collector, and has no documented embedding API.
- Anything that needs fixes: development has stopped (17 open issues, including a parser null dereference reported in 2026 (#219), truncated JSON.stringify output (#192) and a SunSpider date-format test that does not run (#112)).

## How it is fast

Lazy basic block versioning (BBV): the JIT compiles each basic block only when it is first reached, and compiles a separate version for each combination of known value types flowing into it. Type tests proven by an earlier version are dropped (the --maxvers option caps versions per block, default 100). The DLS-style paper adds typed object shapes, where shapes record property types and function pointers, and shape propagation, which removes repeated shape checks in inline caches. The record's abstract snippet credits these with removing 48% of type tests and cutting execution time by 25% against Higgs with plain polymorphic inline caches.

## Compared with alternatives

Do not pick it to run JavaScript fast: Graal.js (beats Node.js V8 on Are We Fast Yet peak performance) and V8 itself are the live options. Pick Higgs only to study lazy BBV and typed shapes. YJIT (catalogued under language-interpreters) is the production descendant of the technique.

## Integration

| | |
|---|---|
| **Form** | standalone executable (built with make; 'make install' copies the binary to /usr/bin and its JS runtime files to /etc/higgs) |
| **Dependencies** | DMD D compiler, GNU make, GNU time (tests), Python 3 to regenerate object layouts, libdl; libx11-dev for the draw library and examples |
| **Minimum toolchain** | DMD ('latest DMD recommended'; the release flags are -m64 -O -release -inline -boundscheck=off -dip25). The last build fix (PR #218, 2023) only addressed Python 3. No building with a current DMD was tested this session. |
| **Platforms** | x86-64 only, on POSIX (Linux; macOS and BSD with notes, open issue #103 on OS X test compatibility) |
| **Thread safety** | not documented (single-threaded VM; no worker or threading API documented) |
| **Drop-in for the baseline** | no |

## Gotchas

- Possible harness bias: source/benchmark.py takes Higgs's own --stats 'exec time (ms)', which excludes JIT compile time (reported separately as 'comp time') and VM startup. For any other --vm_cmd such as d8, which prints no such line, it falls back to wall-clock time, which includes startup and compilation. Whether the paper's V8 comparison used this path is unknown, because the paper could not be opened here.
- benchmark.py is Python 2 only (print statements, csv over a file opened 'rb') even though the README asks for Python 3. It defaults to one run, and its geoMean skips zero values in the product but still divides by the full count.
- The binary must run from the source directory, or after 'make install', to find its runtime JS files. Those runtime files are compiled at startup, so short scripts pay a noticeable start-up cost.
- The licence is not declared at repository level: the Modified BSD (3-clause) text appears only in source file headers (e.g. source/main.d), and the header still points at github.com/maximecb/Higgs.

## Known shortcomings

- Beats only the old V8 full-codegen baseline compiler (up to 682%, 25 of 26 benchmarks); V8 Crankshaft was 49% faster than Higgs on average, so it is not faster than the V8 of its day. Numbers come from WebSearch snippets of arXiv 1507.02437 (blocked here); the DLS 2015 venue is unconfirmed. D language, abandoned since 2023-06-09, BSD-3 only in source headers with no LICENSE file.
- Enricher: source/benchmark.py takes Higgs's own 'exec time (ms)' (excluding JIT compile time and startup) but wall time for other VMs such as d8, so the comparison is biased toward Higgs; it is Python 2 only, defaults to one run, and its geoMean skips zeros but divides by the full count. ES5 subset, x86-64 only, abandoned, 17 open issues (#219 parser null dereference, 2026). Paper still unreachable (arXiv, umontreal thesis blocked).

## Caveats and trade-offs

Weak claim: it beats only V8's old full-codegen baseline compiler (removed from V8 in 2017) and loses to Crankshaft by 49% on average; no comparison exists against any current engine. Numbers are from WebSearch snippets of arXiv 1507.02437, which could not be opened here, so hardware, V8 version and flags are unverified. Venue unverified: search results describe the paper as a CoRR/arXiv technical report from Universite de Montreal; the record's 'DLS 2015' label could not be confirmed, so it is not treated as peer-reviewed. The benchmark list and a Python 2 runner (source/benchmark.py) are in the repo. Licence: no LICENSE file and no GitHub licence badge; source headers (e.g. source/main.d) carry a three-clause Modified BSD licence; JS runtime and library files were not checked. Last commit 2023-06-09 (Python 3 build fix, PR #218); the previous commit was 2019.

Research JIT written in D (needs the DMD compiler), x86-64 and POSIX only, needs GNU make and GNU time. Not callable from C++ without embedding a D runtime.

## Maintenance

Abandoned research VM: the only recent activity is a 2023 Python 3 build fix (PR #218). Its licence is BSD-3-Clause per the file headers, which makes it usable as a reference implementation of BBV, but not as a maintained engine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are WebSearch snippets of arXiv 1507.02437 (paper not opened: ar5iv.labs.arxiv.org EGRESS_BLOCKED, arxiv.org blocked by policy); the README has no benchmarks. The repo does carry the 26-benchmark list (source/benchmark-list.csv: 19 SunSpider plus 7 V8 benchmark suite programs) and runner (source/benchmark.py with --vm_cmd), but hardware, V8 version and flags cannot be checked, so snippet-only evidence stays at C.
- **Verifier notes:** Metadata confirmed on github.com: 882 stars, 64 forks, not a fork or archived, last commit 2023-06-09, so abandoned; licence BSD-3-Clause from file headers only. Re-tier to B only if a copy of the paper shows it was peer-reviewed and confirms the numbers; to A would also need the paper's CPU, DMD version and flags. Arguably an off-baseline entry: the only win is over a non-optimizing compiler that no longer exists.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** paper access and a licence file; wall-time comparison including compile time
- **Pages the verifier opened:**
  - <https://github.com/higgsjs/Higgs>
  - <https://github.com/higgsjs/Higgs/commits/master>
  - <https://github.com/higgsjs/Higgs/tree/master/devnotes>
  - <https://github.com/higgsjs/Higgs/tree/master/source>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/README.md>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/source/main.d>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/source/benchmark-list.csv>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/source/benchmark.py>
  - <https://github.com/QDucasse/lectern>
  - <https://github.com/QDucasse/lectern/tree/master/articles>
- **Sources the enricher read:**
  - <https://github.com/higgsjs/Higgs>
  - <https://github.com/higgsjs/Higgs/commits/master>
  - <https://github.com/higgsjs/Higgs/issues>
  - <https://github.com/higgsjs/Higgs/wiki>
  - <https://github.com/higgsjs/Higgs/wiki/JavaScript-Language-Support>
  - <https://github.com/higgsjs/Higgs/wiki/The-Higgs-JIT>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/README.md>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/source/benchmark.py>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/source/benchmark-list.csv>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/source/main.d>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/source/makefile>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/source/stats.d>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/source/options.d>
  - <https://raw.githubusercontent.com/higgsjs/Higgs/HEAD/source/benchmarks/v8bench/drv-richards.js>
  - <https://github.com/QDucasse/lectern/tree/master/articles>
  - <https://github.com/bsaleil/lc>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/higgsjs/higgs`) · [data/wave12/enrich/raw/github_com_higgsjs_higgs.json](../../../data/wave12/enrich/raw/github_com_higgsjs_higgs.json) (enrichment confidence 0.55)

</details>
