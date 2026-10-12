# TurboPython / tpy (typed Python to C++ without GC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Python` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> Pre-1.0 compiler from annotated Python to C++23 binaries without GC or refcounting; no published speed numbers against CPython.

| | |
|---|---|
| **Beats** | CPython (Shed Skin, Cython, mypyc, Nuitka and Codon appear in the README only as design contrasts, with no timings) |
| **Claimed result** | No speed claim against CPython for compiler output. Dev notes (TODO.md, 2026-10-05): shipped 0.6.2 sieve 1.66 s vs Shed Skin 0.66 s (about 2.5x slower, derived from page data); the 1.15 s figure is an unmerged stepped-slice rewrite. The '7.6x vs CPython' is hand-edited C++. |
| **Workload** | No published benchmark of tpy output against CPython. Developer notes in TODO.md (measured 2026-10-05) time Shed Skin's sieve and ant example programs under tpy and Shed Skin, and a JSON parse of a 15 MB, 20K-record dataset; scripts/perf/generator_frames.py compares generator forms inside tpy only. |
| **Metric** | throughput |
| **Adoption** | 6 stars; tpy-lang 0.6.2 on PyPI (released 2026-09-30) |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/trozen/tpy-lang) |

## Verdict

There is no benchmark of tpy output against CPython: the repo has none, tpy-lang.org was unreachable here, and tpy-examples defers per-example speedup numbers until a harness can time both runs on one machine. Developer notes only: a 15 MB, 20K-record JSON parse in tpy went from 68 to 59 ms after library changes, and the '7.6x vs CPython' figure is for hand-edited generated C++ at 23 ms with the CPython side unspecified (in a section headed 2026-03-12/18); on 2026-10-05, Shed Skin's ant ran 2.87 s under tpy against 2.58 s (Boost flat map) and 3.30 s (standard containers) under Shed Skin, and sieve 1.66 s stock against 0.66 s; mandelbrot on an i7-11700K with g++-13 ran 2.73 ms against 2.51 ms for a direct C++ translation.

## Use it when

- New CPU-bound code you are willing to write as annotated, ownership-aware Python and ship as a standalone native binary with no Python runtime.
- Generating readable C++ (.hpp/.cpp plus sources.cmake) from Python-syntax source to embed in a C++ project, calling C/C++ through @native and exposing functions back with @export(binding="C").
- Writing a CPython extension module in Python syntax (`# tpy: ext_module`) instead of Cython syntax, for self-contained code that imports nothing from PyPI.
- Multi-threaded loops that need real OS threads with no GIL, where compile-time Send/Sync checks are wanted.
- Evaluation and experiments rather than production: run the same program under CPython and tpy and byte-compare outputs, as the project's own example ports do.

## Skip it when

- Existing Python code bases or anything importing PyPI packages (numpy, requests and so on): nothing from CPython can be imported, and stdlib coverage is partial (docs/STDLIB_ROADMAP.md: json \~72%, asyncio \~40%, itertools \~35%, collections \~15%, threading not ported).
- Code where a silent wrong result is unacceptable: BUGS.md holds about 1,860 prioritized entries (155 HIGH, 948 MED, 758 LOW), hundreds tagged silent wrong output, miscompile or dangling view, plus a BFS that hangs where CPython finishes in 0.158 s; the README warns that known bugs 'can produce wrong results silently'.
- When you need demonstrated speed over CPython or another Python compiler: there is no CPython timing for compiler output anywhere in the repo, and the developer's 2026-10-05 notes have it slower than Shed Skin on sieve and ant.
- Code that depends on CPython reference aliasing: containers own copies, so the README's example prints `boiler-3` where CPython prints `renamed` (warned at compile time, but output changes).
- Windows-native or MSVC toolchains (WSL only), or machines with only g++ 12 / clang 18 or older and no network for the [bundled] zig toolchain.

## How it is fast

Ahead-of-time translation to plain C++: dataclasses become structs of fixed-width fields, lists are std::vector, parameters are borrowed as const& or std::string_view, and an ownership model (Own[T] moves, Rc, Arc[Mutex[T]]) replaces garbage collection and reference counting, so objects carry no header or refcount traffic. int32 is the default integer width with checked arithmetic (add_check) while plain `int` is a BigInt; generators lower to resumable frame state machines whose step result is a std::expected with an empty StopIteration value, and spawned threads run without a GIL. The developer's mandelbrot note (i7-11700K, g++-13, min of 21 runs) puts the generated scalar loop at 2.73 ms against 2.51 ms for a direct hand translation to C++, about 8% behind.

## Compared with alternatives

Pick it over Shed Skin or Codon only when you need deterministic ownership-based memory with no garbage collector, no GIL and readable C++ to embed in a C++ build; Shed Skin is faster on the developer's own sieve and ant runs and needs no annotations, and Codon has independent benchmark numbers. Prefer Cython or mypyc when the code must keep importing CPython packages, which tpy cannot do.

## Integration

| | |
|---|---|
| **Form** | module (pip package tpy-lang providing the tpy/tpyc compiler); `tpyc -o` also writes a self-contained source-drop of generated C++, runtime headers and sources.cmake |
| **Dependencies** | Python 3.12+ and a C++23 compiler (the optional [bundled] extra installs ziglang); vendored PCRE2, zlib, Mbed TLS, Howard Hinnant's date and the Mozilla CA bundle are compiled in only when re, zlib/gzip, ssl or datetime time zones are imported |
| **Minimum toolchain** | Python 3.12+; C++23 plus the GCC statement-expression extension: g++ 13+ or clang++ 19+ (MSVC unsupported); builds use -O3 with no -march |
| **Platforms** | Linux and macOS; Windows through WSL only; no architecture-specific code documented |
| **Thread safety** | No GIL: tpy.thread.spawn runs OS threads with Send/Sync checked at compile time; shared mutable state goes through Arc[Mutex[T]], RwLock, atomics or channels. Memory safety is partial: aliasing rules are not enforced, and mutating a container while a reference into it is live is only a warning. |
| **Drop-in for the baseline** | partial — source stays valid Python syntax, but programs need annotations, ownership edits (copy(), Own[T]), int32-default integers and TurboPython-only imports, and CPython packages cannot be imported |

## Gotchas

- Harness flaw in the Shed Skin comparison (TODO.md, measured 2026-10-05, no hardware, compiler or flags given): the sieve notes chain the stock list[bool] build at 1.66 s, the same program over list[uint8] at 1.52 s, and an unmerged one-pass stepped-slice-assignment rewrite at 1.15 s, so the quoted '1.14 s vs Shed Skin 0.66 s' is a hand-patched build; the shipped 0.6.2 compiler is about 2.5x slower than Shed Skin on sieve (derived from page data), and 0.69 s needs GLIBC_TUNABLES malloc thresholds. The ported programs also differ from Shed Skin's sources (sieve uses BigInt `int` elements; ant spells out Neumaier summation instead of sum()).
- The 6,500-program test suite builds every case with no optimization flags (opt_flags=[], NDEBUG undefined) while every user build is -O3; TODO.md says optimizer-exposed undefined behaviour, such as a dangling reference the -O0 build tolerates, has no harness form.
- Integer and evaluation traps: `int` is a BigInt while literals default to int32, so annotating a loop bound `Final[int]` made mandelbrot 1.7x slower (2.73 to 4.67 ms); int32 overflow stops the program instead of widening; call arguments and operands are evaluated in the C++ compiler's order, not left to right; sum() over floats is naive and differs from CPython 3.12+ by an ULP, which changed 124 of 400 output lines in the ant port until it was hand-written.
- Name collision: the PyPI package 'turbopython' (ribalba/TurboPython 0.1.0) advertises 37.1x and 59.4x over pure Python, and web-search summaries attribute those numbers to tpy-lang; they belong to the other project.

## Known shortcomings

- No speed claim against CPython: the dev notes give '7.6x vs CPython' only for hand-edited C++, and the same notes show tpy slower than Shed Skin (sieve 1.14 s vs 0.66 s; ant 2.87 s vs 2.58/3.30 s). 6 stars, silent wrong-result bugs noted in its own TODO; the PyPI 'turbopython' package (37.1x and 59.4x) is a different project. Kept at D under the keep-and-document rule.
- Enricher: the TODO.md Shed Skin sieve notes (2026-10-05, no hardware or flags) give the stock list[bool] build 1.66 s, a list[uint8] variant 1.52 s and an unmerged stepped-slice rewrite 1.15 s, so the record's '1.14 s vs Shed Skin 0.66 s' is a hand-patched build and the shipped 0.6.2 is about 2.5x slower than Shed Skin (derived from page data); the ports differ from the Shed Skin sources (sieve uses BigInt int, ant has a hand-written Neumaier sum). The 6,500-case test suite builds unoptimised (opt_flags=[]) while user builds are -O3, so optimiser-exposed undefined behaviour is untested; BUGS.md lists about 1,860 entries (155 HIGH), hundreds marked silent wrong output. Mandelbrot 2.73 ms vs 2.51 ms for direct C++ (i7-11700K, g++-13).

## Caveats and trade-offs

Early development, pre-1.0: the README says 'known bugs can produce wrong results silently' and BUGS.md (about 2.3 MB) lists many open items, including a hang where CPython finishes in 0.158 s. No published speed evidence against CPython, so tier D with very low notability (6 stars, 0 forks; the tpy-examples repo has 1 star). TODO.md holds internal developer timings only: the one CPython ratio (7.6x) is for hand-edited generated C++, and against Shed Skin tpy is 1.7x slower on sieve without malloc tunables and between Shed Skin's two builds on ant; no hardware or compiler flags are given for these. tpy-lang.org (docs) is blocked here and was not checked. Name collision: the PyPI package 'turbopython' is a different project (ribalba/TurboPython, version 0.1.0, uploaded 2026-03-11) whose description claims 37.1x and 59.4x over pure Python; those numbers do not belong to trozen/tpy-lang. [retier] Typed Python to C++ transpiler without GC, 6 stars, Python ports differ from the Shed Skin sources; BUGS.md lists about 1,860 entries (155 HIGH) with hundreds marked silent wrong output; the test suite builds unoptimised while user builds are -O3. The PyPI 'turbopython' package (37.1x/59.4x) is ribalba/TurboPython, a different project. Kept at D under the keep-and-document rule.

Statically typed Python compiled through C++ (g++ 13+ or clang++ 19+) to a native binary; deterministic ownership model (Own[T], Rc, Arc[Mutex[T]]) instead of GC or reference counting; not a drop-in CPython replacement and no CPython packages (everything imported is TurboPython source, with a CPython extension-module export mode); Linux and macOS, WSL on Windows; standard library is a subset.

## Maintenance

Very active (2,532 commits, last 2026-10-06, tpy-lang 0.6.2 on PyPI 2026-09-30) but pre-1.0 with breaking releases, 6 stars and 0 open issues; Apache-2.0 WITH LLVM-exception lets compiled binaries ship without the notice, yet with silent miscompiles open and only first-party developer timings, it is for evaluation, not production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now D.
- **Tier reason:** No published speed claim for tpy's output against CPython: the README has none, and the only CPython ratio in the repo (a TODO.md developer note, '7.6x vs CPython') is for hand-edited generated C++, not compiler output. Developer notes against Shed Skin show tpy slower or level, so no number supports a win over the baseline.
- **Verifier notes:** Kept at D (confirm): no benchmark_url and no published claim against CPython; the record wrongly said TODO.md has no Shed Skin or CPython timings, so workload, claimed_speedup and caveats were corrected to the developer notes, which show tpy slower than or level with Shed Skin. Shortcomings to record: no speed evidence for compiler output, 6 stars, early development with silent wrong-result bugs. Metadata confirmed: Apache-2.0 WITH LLVM-exception (copyable), last commit 2026-10-06, tpy-lang 0.6.2 on PyPI uploaded 2026-09-30.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** any benchmark against CPython; any CPython comparison of shipped compiler output
- **Pages the verifier opened:**
  - <https://github.com/trozen/tpy-lang>
  - <https://github.com/trozen/tpy-lang/commits>
  - <https://github.com/trozen/tpy-lang/tree/master/scripts/perf>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/README.md>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/BUGS.md>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/RELEASE_NOTES.md>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/scripts/perf/generator_frames.py>
  - <https://github.com/trozen/tpy-examples>
  - <https://pypi.org/pypi/tpy-lang/json>
  - <https://pypi.org/pypi/turbopython/json>
- **Sources the enricher read:**
  - <https://github.com/trozen/tpy-lang>
  - <https://github.com/trozen/tpy-lang/commits>
  - <https://github.com/trozen/tpy-lang/issues>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/README.md>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/BUGS.md>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/RELEASE_NOTES.md>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/scripts/perf/generator_frames.py>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/docs/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/docs/NATIVE_INTEROP.md>
  - <https://raw.githubusercontent.com/trozen/tpy-lang/HEAD/docs/STDLIB_ROADMAP.md>
  - <https://raw.githubusercontent.com/trozen/tpy-examples/HEAD/README.md>
  - <https://raw.githubusercontent.com/trozen/tpy-examples/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/trozen/tpy-examples/HEAD/shedskin/README.md>
  - <https://raw.githubusercontent.com/trozen/tpy-examples/HEAD/shedskin/sieve/README.md>
  - <https://raw.githubusercontent.com/trozen/tpy-examples/HEAD/shedskin/sieve/sieve.py>
  - <https://raw.githubusercontent.com/trozen/tpy-examples/HEAD/shedskin/ant/README.md>
  - <https://raw.githubusercontent.com/trozen/tpy-examples/HEAD/shedskin/ant/ant.py>
  - <https://pypi.org/pypi/tpy-lang/json>
  - <https://pypi.org/pypi/turbopython/json>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/trozen/tpy-lang`) · [data/wave12/enrich/raw/github_com_trozen_tpy_lang.json](../../../data/wave12/enrich/raw/github_com_trozen_tpy_lang.json) (enrichment confidence 0.75)

</details>
