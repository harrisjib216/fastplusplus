# Topaz (Ruby on RPython)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (RPython)` · `BSD-3-Clause` · 🔴 abandoned

> Ruby 1.9.3 subset on PyPy's RPython meta-tracing JIT; in one shootout beats CRuby 2.7.7 on 12 of 13 programs.

| | |
|---|---|
| **Beats** | CRuby (MRI) 2.7.7p221 and 3.2.1p31, interpreter without JIT |
| **Claimed result** | Faster than CRuby 2.7.7 on 12 of 13 programs (derived from page data): fannkuchredux 0.43 s vs 4.34 s, mandelbrot 1.47 s vs 16.74 s, matmul 1.83 s vs 18.39 s, spectralnorm 1.44 s vs 17.18 s, nbody 5.42 s vs 43.56 s, brainfuck 17.41 s vs 115.31 s, binarytrees 1.97 s vs 6.75 s, fasta 5.29 s vs 18.19 s; smallest win pidigits 7.78 s vs 11.42 s; slower only on revcomp (7.3 s vs 4.2 s). Also faster than the same run's Ruby 3.2.1 interpreter on 12 of 13 (revcomp 7.3 s vs 3.67 s slower). |
| **Workload** | Thirteen simplified Benchmarks Game style programs (binarytrees, brainfuck, brainfuck2, fannkuchredux, fasta, knucleotide, mandelbrot, matmul, nbody, pidigits, regexdna, revcomp, spectralnorm); best of up to 5 runs, time measured inside the language, in seconds. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X, 80GB DDR4-3200, Docker on Ubuntu 22.10 |
| **Compiler and flags** | Topaz translated with rpython -Ojit on PyPy 2.7 v7.3.6 inside Docker (docker/topaz); CRuby built from source with a plain ./configure and make (docker/ruby2); gcc 12.2.0 for the C reference; no extra optimisation flags given |
| **Adoption** | 1.0k stars (topazproject/topaz); the measured fork kostya/topaz is a fork of it |
| **Last commit** | 2022-06-18 |
| **Links** | [repository](https://github.com/topazproject/topaz) · [benchmark](https://github.com/kostya/jit-benchmarks) |

## Verdict

In kostya/jit-benchmarks round 1 (2023-02-28, AMD Ryzen 7 3800X, Docker on Ubuntu 22.10), the kostya/topaz fork translated with RPython from PyPy 2.7 v7.3.6 beat CRuby 2.7.7p221 (gcc 12.2.0 build) on 12 of 13 Benchmarks-Game-style programs, from 1.5x on pidigits (7.78 s vs 11.42 s) to about 10x on fannkuchredux and 12x on spectralnorm (derived from page data), and lost on revcomp (7.3 s vs 4.2 s). Times are the best in-process iteration measured by each program, so JIT warm-up and startup are excluded.

## Use it when

- Research or teaching on meta-tracing JITs: a compact example of a dynamic-language VM built on RPython.
- Self-contained numeric or object-allocation Ruby scripts (nbody, mandelbrot, matmul, spectralnorm, binarytrees style) that use only core Ruby 1.9 classes, where it ran 3.4x-12x faster than CRuby 2.7.7.
- Batch Ruby jobs under a tight memory budget where JRuby or TruffleRuby cost hundreds of MB to GBs: Topaz used about 27-116 MB on 11 of 13 shootout programs.
- Long-running loops where JIT warm-up is amortised over several iterations in one process.

## Skip it when

- Any real application or gem: Ruby 1.9.3 only, most of the stdlib and many builtin methods missing, no Rails, no C extensions, no threads.
- Production use: upstream calls itself not stable and untested in the real world, issue #841 'Is this project dead?' (2015) went unanswered, and the last upstream code change is a 2022 one-line fix after 2017.
- String-transform and IO-heavy work: revcomp ran 7.3 s vs CRuby 2.7.7 4.2 s and Ruby 3.2.1 3.67 s, using 787.5 MB vs 164.4 MB.
- Code relying on Hash#compare_by_identity or heavy hash deletion when using the measured kostya fork (see gotchas).
- Windows: upstream says it is untested there.

## How it is fast

RPython generates a meta-tracing JIT from the bytecode interpreter (a JitDriver with greens pc/bytecode/block_bytecode, `jit.promote` on receiver classes and lexical scopes), plus RPython's generational GC, so hot loops become specialised machine code with boxed integers and floats removed. Objects use SELF-style maps with type-specialised instance variables that store Fixnum and Float fields unboxed. The measured fork also replaces the RPython OrderedDict behind Hash with a simpler hash-to-index-list table (commit claims 8x faster get/set) and streams file reads.

## Compared with alternatives

Against JRuby (faster than CRuby on 9 of 13 programs in the same shootout but using about 370 MB-2.1 GB per run) and the shootout's TruffleRuby rows (faster than Topaz on 8 of 13, e.g. nbody 0.85 s vs 5.42 s, with 330 MB-2.8 GB), Topaz wins only on knucleotide, regexdna and revcomp among the JITs and on memory (about 27-120 MB on most programs); pick it only for code inside its Ruby 1.9.3 subset where footprint matters, and use JRuby or TruffleRuby for any real Ruby program.

## Integration

| | |
|---|---|
| **Form** | standalone executable (RPython-translated bin/topaz); not an embeddable library |
| **Dependencies** | PyPy source tree for the RPython toolchain (upstream README: PyPy tag release-2.4.0; kostya fork: pypy2.7 v7.3.2 in its Dockerfile, v7.3.6 in the shootout), a Python 2.7/PyPy2 host to run translation, rply, libffi-dev, gcc |
| **Minimum toolchain** | Python 2.7 / PyPy2 host; translation takes 5-10 minutes; the shootout Dockerfile notes the fork compiles only with pypy2.7-v7.3.6 |
| **Platforms** | Linux and macOS tested upstream; Windows untested; the shootout builds the fork on x86_64 and aarch64 |
| **Thread safety** | No threading support (docs/current-status.rst) |
| **Drop-in for the baseline** | partial — same `topaz file.rb` command line as `ruby file.rb`, but only for programs inside its Ruby 1.9.3 subset |

## Gotchas

- The shootout times the kostya/topaz fork (cloned at HEAD, unpinned), not this repository; upstream lacks the fork's hash and file-read speedups and pins PyPy 2.4.0, so it will likely not build on current PyPy and may be slower on knucleotide, fasta and other hash or IO programs.
- The fork's speed-up came with semantic loss: Hash#compare_by_identity and compare_by_identity? are commented out (17 rubyspec tags in spec/tags/core/hash/compare_by_identity_tags.txt), and its OrderedHash never compacts deleted entries (rebuild() is a no-op), so deletes leave tombstones and repeated Hash#shift rescans them from the start.
- Harness flaw favouring JITs: 'Runs' are in-process iterations of one launch and the table reports the best one, so Topaz shows a warm-JIT best of 5 while CRuby 2.7.7 finished only 1 iteration of brainfuck (115.31 s) and 2 of brainfuck2 within the timeout; startup is excluded.
- Topaz can use more memory than CRuby on string-heavy programs: regexdna 298.9 MB vs 112.5 MB, revcomp 787.5 MB vs 164.4 MB.

## Known shortcomings

- The measured binary is kostya/topaz, a fork by the shootout author tuned 'for benchmark' (8x hash, faster file read), not upstream Topaz; upstream has been abandoned since 2022-06-18. 12 of 13 programs beat CRuby 2.7.7 in kostya/jit-benchmarks.
- Enricher: the shootout ran the kostya/topaz fork cloned at unpinned HEAD. The fork's 8x hash speedup cost semantics: Hash#compare_by_identity and compare_by_identity? are commented out (17 rubyspec tags fail) and the fork's OrderedHash never compacts deletes (rebuild() is a no-op), so tombstones pile up and repeated Hash#shift rescans them. Harness: 'Runs' are in-process iterations and the table takes the best, so Topaz gets a warm-JIT best of 5 while CRuby 2.7.7 finished only one brainfuck iteration (115.31 s). Memory: revcomp 787.5 MB vs CRuby 164.4 MB. Upstream pins PyPy release-2.4.0; last real development 2017.

## Caveats and trade-offs

The code measured is not this repository: docker/topaz clones kostya/topaz, a fork by the shootout's own author (8 stars, last commit 2023-01-27) whose README says the original 'is not developed since 2016' and that the fork fixes the build on newer PyPy and speeds up 'some small things for benchmark', e.g. a faster default hash implementation; its commits include 'Optimize hash, by 8 times get/set operations' and 'Make file read operations much faster, by using stream'. Upstream topazproject/topaz (last commit 2022-06-18) would likely be slower on hash- and IO-heavy programs (knucleotide, fasta, revcomp, regexdna). Outputs pass the suite's own check step (Topaz is not on any expected_check_failed list). Baseline is CRuby 2.7.7; the shootout has no YJIT row. Times are measured inside the program, best of up to 5 iterations, so startup is excluded. Topaz implements only part of Ruby, so the programs exercise a small slice of the language. Single benchmark author, one machine, one round (2023-02-28). Found by harvesting a row from a shootout, not from a Topaz-authored claim. RPython/Python project, not C++. [retier] Measured binary is the kostya/topaz fork (unpinned HEAD), tuned 'for benchmark' with an 8x hash path that drops Hash#compare_by_identity semantics (17 rubyspec tags fail) and never compacts deletes; upstream Topaz (abandoned 2022-06-18, last real development 2017, pinned to PyPy 2.4.0) was not measured. kostya/jit-benchmarks takes the best of up to 5 warm in-process iterations while CRuby 2.7.7 finished one brainfuck iteration (115.31 s); revcomp uses 787.5 MB vs CRuby 164.4 MB; no YJIT or CRuby 3.x row.

Implements Ruby on RPython; the README does not state which Ruby version or how much of CRuby 2.7 or 3.x it covers, so compatibility is unverified. Translation with RPython takes 5-10 minutes and needs a PyPy source tree at tag release-2.4.0 per the upstream README. Memory use is higher than CRuby on allocation heavy runs (binarytrees 63.1 MB vs 44.6 MB Ruby 2.7 in the same table).

## Maintenance

Abandoned: upstream development stopped in 2017 (one 2022 fix) and the benchmarked fork's last commit is 2023-01-27; BSD-3-Clause and pure RPython, but it needs an old PyPy2 toolchain to build and only runs a subset of Ruby 1.9.3, so it is a research artefact rather than a usable Ruby.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now C.
- **Tier reason:** The Ruby2/Topaz and Ruby2 (CRuby 2.7.7p221) rows of the kostya/jit-benchmarks README match every number in the record, and the run is reproducible from public files: &lt;bench&gt;/test.rb sources, `topaz <file>` in tools/languages.rb, docker/topaz (clones kostya/topaz and translates it with `rpython -Ojit targettopaz.py` under PyPy 2.7 v7.3.6), docker/ruby2 (CRuby 2.7.7, gcc 12.2.0 on ubuntu:22.10), CPU AMD Ryzen 7 3800X.
- **Retiered** A to C: A to C (uniwidth precedent: correctness bug in the measured hot path): the kostya/jit-benchmarks numbers come from the kostya/topaz fork at unpinned HEAD whose 8x hash speedup disables Hash#compare_by_identity (17 rubyspec tags fail) and never compacts deleted hash entries, and the harness takes Topaz's warm best-of-5 against a CRuby run that completed one brainfuck iteration; upstream Topaz was never measured.
- **Verifier notes:** Numbers and the 12-of-13 count are correct; metadata verified (BSD-3-Clause, 1k stars, not a fork, last commit 2022-06-18, abandoned). Main shortcoming: the measured binary is kostya/topaz, a benchmark-tuned fork made by the shootout author, so the orchestrator may want a repo_url override to https://github.com/kostya/topaz or to keep this id with that documented; upstream is unmaintained.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** measurement of upstream Topaz against CRuby 3.x; measurement of upstream Topaz with equal iteration counts
- **Pages the verifier opened:**
  - <https://github.com/topazproject/topaz>
  - <https://github.com/topazproject/topaz/commits>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/LICENSE>
  - <https://github.com/kostya/topaz>
  - <https://github.com/kostya/topaz/commits>
  - <https://raw.githubusercontent.com/kostya/topaz/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/cli.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/base>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/ruby2>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/ruby3>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/java>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/jruby>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/topaz>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/dc>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/revcomp/test.rb>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/README.rst>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/docs/current-status.rst>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/docs/index.rst>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/docs/contributing.rst>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/docs/getting-started.rst>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/docs/source-map.rst>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/docs/blog/index.rst>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/docs/blog/announcing-topaz.rst>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/docs/blog/one-year.rst>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/docs/blog/type-specialized-instance-variables.rst>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/targettopaz.py>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/topazproject/topaz/HEAD/topaz/interpreter.py>
  - <https://github.com/topazproject/topaz/commits>
  - <https://github.com/topazproject/topaz/issues>
  - <https://github.com/topazproject/topaz/issues/841>
  - <https://raw.githubusercontent.com/kostya/topaz/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/topaz/HEAD/Dockerfile>
  - <https://github.com/kostya/topaz/commits>
  - <https://github.com/kostya/topaz/commit/1b0c1fe>
  - <https://github.com/kostya/topaz/commit/028a3e1>
  - <https://raw.githubusercontent.com/kostya/topaz/HEAD/topaz/utils/ordered_hash.py>
  - <https://raw.githubusercontent.com/kostya/topaz/HEAD/topaz/objects/hashobject.py>
  - <https://raw.githubusercontent.com/kostya/topaz/HEAD/spec/tags/core/hash/compare_by_identity_tags.txt>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/topaz>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/ruby3>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/cli.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/runner.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/revcomp/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/knucleotide/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/regexdna/test.rb>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/topazproject/topaz`) · [data/wave12/enrich/raw/github_com_topazproject_topaz.json](../../../data/wave12/enrich/raw/github_com_topazproject_topaz.json) (enrichment confidence 0.65)

</details>
