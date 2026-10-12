# Node.js (V8) fannkuch-redux in kostya/jit-benchmarks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `JavaScript (Node.js/V8)` · `MIT` · 🟢 active

> Node 19.7 (V8) runs a Pall-style fannkuch-redux 1.38x faster than the suite's plainer C program; the gap is algorithmic, not a JIT win.

| | |
|---|---|
| **Beats** | C fannkuch-redux (fannkuchredux/test.c, the Benchmarks Game Java-derived program with variable-length arrays), gcc 12.2.0 -O3 -march=native -funroll-loops |
| **Claimed result** | fannkuchredux (README round 1, 2023-02-28): Node 0.15 s vs C 0.21 s best run (about 1.4x, derived from page data); GraalVM_JVM 0.18 s and GraalVM 0.19 s also below C; Lua JIT 0.27 s slower. Same table: Cython 0.13 s (Cython-generated C built with the same gcc flags, Pall-style flip loop) beats Node, and Crystal 0.19 s (same algorithm as the C program) roughly ties C. |
| **Workload** | Benchmarks Game fannkuch-redux at n=10 (tools/benchmarks.rb args [10, TEST_COUNT], TEST_COUNT 5): one process runs the kernel 5 times and each run prints its own in-language time (C clock(), JS Date); Best T is the minimum of those in-process times, so start-up is excluded and JIT warm-up is largely excluded. Single thread. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X, 80 GB DDR4-3200, Docker on Ubuntu 22.10 |
| **Compiler and flags** | C/C++: gcc and g++ 12.2.0 with -O3 -march=native -fomit-frame-pointer -funroll-loops (C++ uses -std=c++11), from tools/languages.rb; luajit 2.1.0-beta3; nodejs 19.7.0 |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Adoption** | 105 stars |
| **Last commit** | 2026-01-27 |
| **Links** | [repository](https://github.com/kostya/jit-benchmarks) · [benchmark](https://github.com/kostya/jit-benchmarks) |

## Verdict

On an AMD Ryzen 7 3800X under Docker on Ubuntu 22.10 (round 1, 2023-02-28), fannkuch-redux at n=10 took 0.152 s for test.js on Node 19.7.0 against 0.21 s for test.c built with gcc 12.2.0 -O3 -march=native -fomit-frame-pointer -funroll-loops, each the best of five in-process runs timed by the program itself (about 1.38x, derived from page data and results/amd64/round_1.yml). The two programs use different algorithms, and a gcc -O3 build of a closer-to-Pall algorithm (the Cython row, 0.129 s) beats Node.

## Use it when

- As a data point that V8's optimising tier can run tight integer array loops within the same range as gcc -O3 output, once warm.
- When choosing between JS engines for compute kernels: in the same table Node 0.15 s beats GraalVM JS (0.18-0.19 s) and LuaJIT running the same Pall algorithm (0.27 s).
- When porting a hot integer loop from JavaScript to C or C++: carry the algorithmic tricks over, or the native port can come out slower, as this C program does.
- Teaching or reviewing cross-language benchmarks: a clear example of an algorithm mismatch masquerading as a language result.

## Skip it when

- As evidence that JavaScript beats C or C++: the suite's own Cython row, gcc -O3 compiling a closer-to-Pall flip loop with the lookahead trick and swap-based permutation step, runs in 0.129 s, faster than Node's 0.152 s.
- As a statement about current engines: numbers are from 2023-02-28 with Node 19.7.0 and gcc 12.2.0; the benchmark code has not changed since March 2023 and nothing was re-run.
- Memory-constrained use: Node's process peaks at 45.4 MB against 0.9 MB for the C program.
- Short single-shot runs: Best T excludes start-up (about 0.24 s to reach the started marker in Node's container) and the slowest of Node's five in-process runs was 0.183 s.
- Multi-threaded or SIMD work: the suite is deliberately single-threaded and avoids low-level hacks, so it says nothing about the Benchmarks Game's fastest parallel C fannkuch programs.

## How it is fast

Mostly by doing less work. The JS program caches the first element, writes q[q0]=q0 directly instead of moving it through the flip, reverses only q[1..q0-1] and skips the reverse when q0 &lt; 3, skips the copy entirely when the permutation already starts with 0, and steps permutations with an alternating swap instead of a full prefix rotation. The C program (Mazurov/Piché, Java-derived, VLA arrays) copies the whole permutation every time, reverses the full prefix including element 0 on each flip and rotates perm1[0..r] for each new permutation. An agent count of array element moves in the two algorithms at n=10 gives 168.4M for the C program against 118.8M for the JS one, 1.42x more work, which matches the measured 1.38x time ratio (agent instrumentation in Python, both reproduce checksum 73196 and max flips 38; a proxy, not a timing). V8's TurboFan then runs the cheaper algorithm at native-like speed on small-integer arrays.

## Compared with alternatives

Do not pick it as a performance claim: among the same suite's catalogued rows, Node regex-dna (5.3x over C using PCRE without its JIT) and LuaJIT k-nucleotide (2.7x over substr-heavy std::unordered_map C++) also rest on weak baselines but at least use comparable algorithms, while benchLANG and LangArena entries measure one shared algorithm per language with current toolchains. Cite this row only to show how an algorithm swap can flip a language ranking.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Node.js 19.7.0 (built from the suite's docker/nodejs image); the C baseline needs only libc |
| **Minimum toolchain** | Node.js 19.7.0 as measured; the program uses only Array, Date, console and process.argv, so any recent Node runs it |
| **Platforms** | Measured on x86-64 (AMD Ryzen 7 3800X, Docker on Ubuntu 22.10); the README says the suite also runs on aarch64 (tested on Apple M1), but no aarch64 results are published |
| **Thread safety** | Not applicable: single-threaded program |
| **Drop-in for the baseline** | no |

## Gotchas

- Algorithm mismatch behind the numbers: test.c is the Mazurov/Piché Java-derived program and test.js is Pall's Lua algorithm, so the README's promise of 'one algorithm' does not hold here. By agent count the C program moves 1.42x more array elements at n=10 (168.4M vs 118.8M), about the same as the 1.38x time gap; Crystal's port of the C algorithm takes 0.19 s and LuaJIT's run of the Pall algorithm 0.27 s, so neither language nor JIT explains the Node row alone.
- Different clocks with different resolution: C reports clock() process CPU time printed with %.2f (10 ms steps, so 'C 0.21 s' covers 0.205-0.215 s), Node reports Date wall time in milliseconds (0.152 s); the ratio is therefore 1.35x to 1.41x, not a precise 1.4x.
- Best T is the minimum of five in-process runs (results/amd64/round_1.yml: Node 0.152-0.183 s, C 0.21-0.22 s), so V8 warm-up and on-stack replacement are mostly excluded; the earlier round_0.yml run agrees (Node 0.148 s, C 0.21 s).
- The harness checks output only at n=5 (expected checksum 11 and 'Pfannkuchen(5) = 7'), not at the measured n=10; the agent re-ran both algorithms in Python and they agree at n=10 (73196, 38), so no correctness problem was found.

## Known shortcomings

- Crippled baseline (tier D): the programs use different algorithms and the suite's own Cython row (gcc -O3, Pall-style loop) runs 0.13 s against Node's 0.15 s; the workload is n=10, best of 5 runs in one process, timed inside the program with startup excluded.
- Harness flaw confirmed and quantified: the programs are different algorithms. A Python count of array element moves at n=10 gives the C program 168.4M against JS's 118.8M (1.42x), matching the 1.38x time gap (0.21 vs 0.152 s in results/amd64/round_1.yml). The clocks also differ: C uses clock() CPU time printed to 10 ms steps while JS uses Date wall time, so the ratio is 1.35-1.41x. The output check runs only at n=5. Cython at 0.129 s beats Node.

## Caveats and trade-offs

Not the same algorithm: test.js is Isaac Gouy's transliteration of Mike Pall's Lua program (caches the first element, writes q[q0]=q0, skips the swap loop when q0 &lt; 3, sign-swap permutation step), while test.c is the Oleg Mazurov Java-derived program (reverses the full prefix including element 0 on every flip, VLA arrays). The suite's own Cython program, a Pall-style variant compiled by gcc with the same -O3 flags, runs in 0.13 s and beats Node's 0.15 s, so the Node win over C is algorithmic, not a JIT effect; README's 'one algorithm' promise does not hold for this benchmark. Timing is in-language (C clock() CPU time, JS Date wall time), best of 5 runs inside one process at n=10, so the earlier note that start-up is included was wrong. Numbers date from 2023-02-28 (gcc 12.2.0, nodejs 19.7.0); the only commit since 2023-03-30 is a README link (2026-01-27). V8 is a known entry; this record is a language-level claim kept under the suite repo. [retier] Different algorithms, quantified: a count of array element moves at n=10 gives the C program 168.4M against JS's 118.8M (1.42x), matching the 1.38x time gap (0.21 vs 0.152 s). C uses clock() CPU time printed to 10 ms steps while JS uses Date wall time. The output check runs only at n=5. Cython at 0.129 s beats Node.

Node uses 45.4 MB vs 0.9 MB for the C program.

## Maintenance

MIT-licensed, 105 stars, 69 commits and 6 open issues; benchmark code and results unchanged since 2023 (the only 2026 commit adds a README link to the author's newer LangArena suite), so treat it as a frozen 2023 snapshot and use LangArena or kostya/benchmarks for current numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** Methodology alone would reach A (fannkuchredux/test.c and test.js public, gcc 12.2.0 with -O3 -march=native -fomit-frame-pointer -funroll-loops in tools/languages.rb, nodejs 19.7.0, Ryzen 7 3800X), but the two programs use different algorithms and the same table shows a gcc -O3 build of the faster algorithm (Cython row, 0.13 s) beating Node (0.15 s), so the C baseline is algorithmically handicapped against a tuned JS program and the language-level claim falls under the crippled-baseline precedent (tier D).
- **Verifier notes:** Numbers on the README match the record (Node 0.15 s, C 0.21 s, GraalVM 0.18/0.19 s, LuaJIT 0.27 s), but the record's workload was wrong (n=10 with 5 in-process runs and in-language timers, not n=7 with start-up included). Shortcoming to record: different algorithms; the suite's own Cython row (gcc -O3, Pall-style loop, 0.13 s) beats Node, so the C baseline is crippled for this comparison (tier D). last_commit 2026-01-27 is within 12 months, so status is active by rule, though code is unchanged since 2023-03-30.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** verifier batch-08 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/kostya/jit-benchmarks>
  - <https://github.com/kostya/jit-benchmarks/commits/master>
  - <https://github.com/kostya/jit-benchmarks/tree/master/fannkuchredux>
  - <https://github.com/kostya/jit-benchmarks/tree/master/tools>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/tools/runner.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/tools/cli.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/fannkuchredux/test.c>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/fannkuchredux/test.js>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/fannkuchredux/test.lua>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/fannkuchredux/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/fannkuchredux/test.cr>
- **Sources the enricher read:**
  - <https://github.com/kostya/jit-benchmarks>
  - <https://github.com/kostya/jit-benchmarks/commits/master>
  - <https://github.com/kostya/jit-benchmarks/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/fannkuchredux/test.c>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/fannkuchredux/test.js>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/fannkuchredux/test.lua>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/fannkuchredux/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/fannkuchredux/test.cr>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/tools/runner.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/tools/cli.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/docker-compose.yml>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/results/amd64/round_1.yml>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/master/results/amd64/round_0.yml>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:javascript/kostya/jit-benchmarks#fannkuchredux`) · [data/wave14/enrich/raw/lang_javascript_kostya_jit_benchmarks_fannkuchredux.json](../../../data/wave14/enrich/raw/lang_javascript_kostya_jit_benchmarks_fannkuchredux.json) (enrichment confidence 0.8)

</details>
