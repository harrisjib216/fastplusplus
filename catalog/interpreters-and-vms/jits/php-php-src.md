# PHP JIT (php-src opcache JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> PHP's built-in opcache JIT: 2-9.5x faster than the plain PHP 8.2 interpreter on numeric benchmarks-game kernels.

| | |
|---|---|
| **Beats** | PHP 8.2.3 without JIT (also compared in the same suite against LuaJIT 2.1.0-beta3 and PyPy3 7.3.11) |
| **Claimed result** | kostya/jit-benchmarks best times in s, PHP JIT vs PHP: mandelbrot 0.58 vs 5.51; fannkuchredux 0.77 vs 2.54; nbody 7.0 vs 21.77; spectralnorm 2.51 vs 6.48; binarytrees 2.93 vs 5.84; fasta 2.46 vs 4.64; knucleotide 1.96 vs 2.87 (1 run); revcomp 2.06 vs 2.27 (1 run); roughly equal on regexdna (1.39 vs 1.4) and pidigits (1.57 vs 1.71). |
| **Workload** | Benchmarks-game programs, single thread, PHP 8.2.3 with JIT versus PHP 8.2.3 interpreter, best time of up to 5 runs. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X, 80Gb DDR-4 3200 Mghz, docker on Ubuntu 22.10 (round 1, 2023-02-28) |
| **Compiler and flags** | PHP 8.2.3 built from source in docker/php8 ('./configure --prefix /opt/php8 --with-gmp', configure default CFLAGS) with the Ubuntu 22.10 base image's gcc (12.2.0 per the versions table). JIT row: 'php -dmemory_limit=512M -dzend_extension=opcache.so -dopcache.enable_cli=1 -dopcache.enable=1 -dopcache.jit_buffer_size=500M -dopcache.jit=1255' (tracing JIT); baseline row: 'php -dmemory_limit=512M' with no opcache loaded (kostya/jit-benchmarks tools/languages.rb). |
| **Adoption** | 40.4k stars; PHP itself |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/php/php-src) · [benchmark](https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md) |

## Verdict

kostya/jit-benchmarks round 1 (2023-02-28) built PHP 8.2.3 from source (configure defaults, gcc 12.2.0, Ubuntu 22.10 in Docker on a Ryzen 7 3800X) and ran the same PHP programs with the tracing JIT (opcache.jit=1255, 500M buffer) and without opcache: best iteration times mandelbrot 0.58 vs 5.51 s, fannkuchredux 0.77 vs 2.54 s, nbody 7.0 vs 21.77 s, spectralnorm 2.51 vs 6.48 s, binarytrees 2.93 vs 5.84 s and fasta 2.46 vs 4.64 s, while regexdna, pidigits and revcomp stayed within 10%.

## Use it when

- CPU-bound PHP loops on ints and floats (math, image and pixel loops, emulators, simulations): the independent run shows mandelbrot 9.5x, fannkuchredux 3.3x, nbody 3.1x and spectralnorm 2.6x over the no-opcache interpreter (ratios derived from page data).
- Long-running PHP CLI workers or daemons, where trace compilation is paid once and the best-iteration numbers above apply.
- Existing PHP 8.x deployments on x86-64 or AArch64 that cannot change runtime or language: it is enabled with ini settings only.
- Object- and allocation-heavy PHP code such as tree building, where binarytrees still ran 2.0x faster (2.93 s vs 5.84 s).

## Skip it when

- Typical request-per-process web apps bound by database and network I/O (WordPress-style): the PHP JIT RFC reports large gains only on bench.php and Mandelbrot and little for real apps (RFC page blocked here, search snippet only).
- Code whose time is in C extensions: regexdna (PCRE) 1.39 s vs 1.40 s, pidigits (GMP) 1.57 s vs 1.71 s and revcomp 2.06 s vs 2.27 s were essentially unchanged.
- When you need LuaJIT-, PyPy- or V8-class speed: on the same page PHP JIT is behind LuaJIT on spectralnorm (2.51 s vs 0.12 s) and nbody (7.0 s vs 1.44 s) and behind PyPy3 on spectralnorm (2.51 s vs 0.71 s) and nbody (7.0 s vs 4.44 s).
- Architectures other than i386, x86-64 and AArch64: configure disables the JIT with a warning; on Apple Silicon a ZTS build needs pthread_jit_write_protect_np().
- Risk-averse production code on PHP 8.4-8.6 without testing: several verified JIT miscompilation bugs are open (see gotchas).

## How it is fast

The tracing mode (opcache.jit=1255 in the benchmark: AVX allowed, global linear-scan register allocation, hot-trace trigger, type inference plus inter-procedural analysis) records hot loops and functions after hot counters fire, specialises them on observed types and emits native code, so loops on ints and floats skip the VM's opcode dispatch and zval type checks. Since 8.4 the code is generated through IR, a Sea-of-Nodes style SSA graph modelled on LuaJIT's IR, with on-the-fly folding, SCCP, global code motion and linear-scan register allocation. Calls into C code (PCRE, GMP, string functions) are not sped up, which is why regex, string and bignum kernels barely move.

## Compared with alternatives

Like the CPython copy-and-patch JIT and BeamAsm siblings, this is a JIT measured against its own runtime's interpreter; it is the only option for unmodified PHP code and shows much larger numeric gains (2-9.5x) than CPython's JIT (7-8% geomean), while the HHVM sibling's 1.6x over PHP comes from a 2014-era comparison. If you want to build your own JIT in C, look at the IR framework that PHP 8.4+ embeds rather than at php-src.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none beyond PHP itself; the IR framework is embedded in ext/opcache/jit/ir; Capstone is optional, only for JIT disassembly |
| **Minimum toolchain** | PHP 8.0 or later (JIT introduced in 8.0; IR-based back end from 8.4); built with PHP's normal C toolchain, no extra compiler requirement documented in what was read |
| **Platforms** | i386, x86-64 and AArch64 per the JIT README and config.m4 (which has Linux/BSD and macOS targets; the Windows build files were not checked); other CPUs run the interpreter |
| **Thread safety** | not documented in the files read; config.m4 only notes that ZTS builds on Apple Silicon require pthread_jit_write_protect_np() |
| **Drop-in for the baseline** | partial: drop-in for the PHP interpreter (same code, ini switch), but not a replacement for the category's baselines (PyPy, LuaJIT, V8, HotSpot), which run other languages |

## Gotchas

- Harness: kostya/jit-benchmarks runs each program up to 5 times inside one process and reports the fastest self-timed (microtime) iteration, so start-up and first-pass JIT compilation are excluded; knucleotide, regexdna and revcomp ran a single iteration, and the no-JIT nbody hit the 80 s timeout after 3 iterations. The PHP knucleotide program fails the suite's own output check (tools/benchmarks.rb lists php and php_jit under expected_check_failed): its do ... while (\$i) loop never counts position 0 and divides by strlen - k. Both PHP rows ran that same code, so the JIT ratio stands, but the cross-language knucleotide row is unvalidated. The README header says PHP8.1 while the versions table says 8.2.3, and there are no PHP rows for brainfuck, brainfuck2 or matmul.
- The baseline row loads no opcache at all, so the speedup includes opcache's optimizer passes as well as the JIT; and the measured 8.2.3 JIT is the DynASM back end that PHP 8.4 replaced with the IR framework, so the numbers do not transfer directly to current releases.
- Open, maintainer-verified miscompilations: #22559 (tracing JIT in 8.4-8.6, not 8.3: high bits of \~ leak through a masked OR into a typed int property, 0x9C became 0xFFFFFFFFFFFFFFFF in a Z80 emulator), #23983 (function JIT in 8.4+: wrong boolean result when interrupt handlers run inside a loop, fix PR #24003) and #23572 (tracing JIT calls the wrong method for self::/parent:: static calls in shared trait methods).
- Configuration traps: since 8.4 the defaults are opcache.jit=disable and opcache.jit_buffer_size=64M, so setting only jit_buffer_size no longer enables the JIT, and JIT start-up failures are fatal; since 8.5 opcache is always built in and zend_extension=opcache.so (as in the benchmark's command line) emits a warning; the CLI needs opcache.enable_cli=1.

## Known shortcomings

- Off-baseline: PHP's opcache JIT is compared with PHP's own interpreter, and kostya/jit-benchmarks ran the baseline without opcache, so opcache and JIT gains are mixed; behind PyPy and LuaJIT on numeric kernels. Language is C (PHP License 3.01); baselines PyPy, LuaJIT, V8 and HotSpot are not met.
- Enricher: in kostya/jit-benchmarks the PHP knucleotide fails the suite's own output check (benchmarks.rb expected_check_failed for php and php_jit: a do-while skips position 0), so the cross-language knucleotide row is unvalidated although both PHP rows ran the same code; best time is the fastest in-process microtime iteration (startup and warm-up excluded) and the no-JIT nbody hit the 80 s timeout after 3 iterations. The measured 8.2.3 JIT used the DynASM back end, replaced by IR in 8.4+. Open verified miscompiles #22559, #23983, #23572.

## Caveats and trade-offs

Compares the JIT with PHP's own interpreter, which is not one of the category baselines (PyPy, LuaJIT, V8, HotSpot). The baseline row runs without opcache loaded at all, so the gain mixes the opcache optimizer with the JIT. Cross-language rows on the same page (different programs per language): PHP JIT is slower than PyPy3 on fannkuchredux (0.77 vs 0.71), mandelbrot (0.58 vs 0.54), nbody (7.0 vs 4.44) and spectralnorm (2.51 vs 0.71), and slower than LuaJIT on fannkuchredux, fasta, knucleotide, mandelbrot, nbody and spectralnorm; Node is faster on most kernels. This is an independent 2023 snapshot of simple benchmarks-game kernels; the README header says PHP8.1 but the versions table says 8.2.3. php-src master is BSD-3-Clause (LICENSE checked); released versions before the relicense, including the 8.2.3 tested, carry the PHP License 3.01. I did not open the php-src JIT sources or the PHP RFC.

JIT is an optional part of the PHP runtime (opcache), mostly benefits CPU-bound numeric code; little gain on string/regex or I/O-bound code.

## Maintenance

Actively developed in php-src (40.4k stars, commits on 2026-10-06, master BSD-3-Clause, the tested 8.2.3 under the PHP License 3.01) and shipped with every PHP 8 build but off by default; it is usable only as part of the PHP runtime, and the reusable piece for other projects is the IR framework (github.com/dstogov/ir), which its README says is still under development.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A: the 'PHP JIT' and blank 'PHP' rows of kostya/jit-benchmarks README.md match the record. The setup is fully public: &lt;bench&gt;/test.php sources, tools/languages.rb, which defines php (no opcache) and php_jit (-dzend_extension=opcache.so -dopcache.enable_cli=1 -dopcache.jit_buffer_size=500M -dopcache.jit=1255), and docker/php8, which builds PHP 8.2.3 from source with './configure --prefix /opt/php8 --with-gmp' using the Ubuntu 22.10 base image's gcc (12.2.0 per the versions table). The CPU is stated (Ryzen 7 3800X).
- **Verifier notes:** All numbers verified; blank rows confirmed as no-opcache runs from tools/languages.rb, and upgraded to A because the build, JIT flags, code and CPU are public. Shortcomings: off-baseline (PHP interpreter, not PyPy/LuaJIT/V8/HotSpot), behind LuaJIT and PyPy on numeric kernels, and opcache and JIT gains are not separated.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/php8>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/base>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker-compose.yml>
  - <https://github.com/kostya/jit-benchmarks>
  - <https://github.com/kostya/jit-benchmarks/commits>
  - <https://github.com/php/php-src>
  - <https://github.com/php/php-src/commits>
  - <https://raw.githubusercontent.com/php/php-src/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/runner.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/cli.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/xtime.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/dc>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/php8>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/base>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/wrapper>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/mandelbrot/test.php>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/mandelbrot/test.lua>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/mandelbrot/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.php>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/spectralnorm/test.php>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/spectralnorm/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/fannkuchredux/test.php>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/knucleotide/test.php>
  - <https://github.com/kostya/jit-benchmarks>
  - <https://github.com/kostya/jit-benchmarks/tree/master/tools>
  - <https://raw.githubusercontent.com/php/php-src/HEAD/README.md>
  - <https://raw.githubusercontent.com/php/php-src/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/php/php-src/HEAD/ext/opcache/jit/README.md>
  - <https://raw.githubusercontent.com/php/php-src/HEAD/ext/opcache/config.m4>
  - <https://raw.githubusercontent.com/php/php-src/HEAD/ext/opcache/jit/zend_jit.h>
  - <https://raw.githubusercontent.com/php/php-src/PHP-8.2/ext/opcache/jit/zend_jit.h>
  - <https://github.com/php/php-src/tree/PHP-8.2/ext/opcache/jit>
  - <https://raw.githubusercontent.com/php/php-src/HEAD/php.ini-production>
  - <https://raw.githubusercontent.com/php/php-src/HEAD/UPGRADING>
  - <https://raw.githubusercontent.com/php/php-src/PHP-8.4/UPGRADING>
  - <https://raw.githubusercontent.com/php/php-src/PHP-8.5/UPGRADING>
  - <https://raw.githubusercontent.com/php/php-src/PHP-8.0/UPGRADING>
  - <https://github.com/php/php-src/issues?q=is%3Aissue%20is%3Aopen%20JIT%20label%3A%22Extension%3A%20opcache%22>
  - <https://github.com/php/php-src/issues/22559>
  - <https://github.com/php/php-src/issues/23983>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/README.md>
  - https://wiki.php.net/rfc/jit (EGRESS_BLOCKED; claims taken from a WebSearch snippet)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/php/php-src`) · [data/wave12/enrich/raw/github_com_php_php_src.json](../../../data/wave12/enrich/raw/github_com_php_php_src.json) (enrichment confidence 0.75)

</details>
