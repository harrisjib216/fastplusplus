# Visual Basic .NET (CLR JIT) vs C: Fourmilab fbench

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Visual Basic .NET` · `CC-BY-SA-4.0` · 🔴 abandoned

> A 2005-era VB.NET port of John Walker's fbench ran in 0.866 of C's time, but its trig code differs from the C build's.

| | |
|---|---|
| **Beats** | The C version of fbench built with GCC 3.2.3 -O3 on Linux (the table's reference row, relative time 1) |
| **Claimed result** | Visual Basic .NET 'All optimisations, Windows XP': relative time 0.866 versus C 1 (about 1.15x faster, derived from page data). Visual Basic 6 on the same OS is 1.132 (slower). |
| **Workload** | fbench: John Walker's optical-design ray-tracing benchmark (heavy on sin, cos, tan, atan and sqrt); each language run for about five minutes and the time per iteration divided by the C version's time per iteration on the same machine. |
| **Metric** | throughput |
| **Hardware** | Not stated per row (the page says each language was compared with the C version 'on the same machine'; no CPU model given) |
| **Compiler and flags** | VB.NET: 'All optimisations', Windows XP; the checked-in fbench.vbproj (Visual Studio .NET project, ProductVersion 7.0.9955, an upgrade-wizard conversion of Jim White's 2005 VB6 port) has a Release config with Optimize=true and RemoveIntegerChecks=true; .NET Framework version not stated; timed with GetTickCount in a WinForms app. C baseline: GCC 3.2.3 -O3 on Linux (src/c/Makefile: gcc -Wall -O3 -lm, INTRIG commented out so libm trig is used). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 6 stars; John Walker's benchmark in use since 1980 |
| **Last commit** | 2021-09-24 |
| **Links** | [repository](https://github.com/Fourmilab/floating_point_benchmarks) · [benchmark](https://github.com/Fourmilab/floating_point_benchmarks/blob/master/Web_pages/fbench.html) |

## Verdict

fbench.html's language table gives Visual Basic .NET ('All optimisations, Windows XP') a relative time of 0.866 against C = 1 (labelled GCC 3.2.3 -O3, Linux), about 1.15x faster (derived from page data). VB6 on the same OS is 1.132. Each language was run for about five minutes and divided by the C time per iteration on the same, unnamed, machine, and no CPU, .NET version or date is given beyond the port's July 2005 header.

## Use it when

- As a historical data point: a straight VB6-to-VB.NET translation, JIT-compiled by an early CLR, landed in the same range as compiled C on a trig-heavy loop, and ahead of the VB6 native-code build of the same port (1.132).
- As a cautionary example when reading cross-language tables: check which math library each port's hot loop actually calls before comparing ratios.
- As a readable VB.NET reference of the fbench algorithm, for example to port it to modern .NET and rerun it against C on one machine.

## Skip it when

- As evidence that the .NET JIT beats C on floating-point code: the two sides evaluate sine and arcsine differently, ran on different OSes, and the C build, CPU and date behind the 0.866 are not named.
- For current .NET performance: the project is a Visual Studio .NET 7.0 file (ProductVersion 7.0.9955), which implies .NET Framework 1.x (inference), and it needs conversion before a modern SDK can build it.
- Outside Windows: it is a System.Windows.Forms app that P/Invokes kernel32 GetTickCount and references Microsoft.VisualBasic.Compatibility.
- When you need a permissive licence: the repository is CC BY-SA 4.0, which is share-alike and not an OSI software licence.

## How it is fast

No mechanism is published, and the source points to different work rather than a better compiler. The timed loop in modFBENCH.vb takes the file's #Else branch (INTRIG is not defined there), so sines come from fSin. fSin is the benchmark's own range-reduced polynomial in fbench_lib.vb. Arcsines go through the internal rational aTan plus System.Math.Sqrt (that file sets #Const INTRIG = True), and only cotangents call the .NET library (1 / System.Math.Tan). Per iteration that is about 35 polynomial sines, 24 internal arcsines and 12 library tangents (derived from the code; all four lens surfaces are curved, so the flat-surface System.Math.Cos path never runs). The C reference row instead calls libm for all of them. The plausible reason for 0.866, inferred and not measured, is that this mix of cheap polynomials plus a library square root costs less than both C modes. C INTRIG also replaces tan and uses a Newton-Raphson square-root loop.

## Compared with alternatives

Do not pick it as evidence. Like the JavaScript fbench sibling (Firefox's trig memo cache) and the xemantic Java Math.sin-versus-libm sibling, the win comes from different math work rather than better code generation. For current .NET JIT-versus-C++ evidence with the same algorithm on both sides, use the LangArena C# rows (Distance::NGram, Graph::AStar) or the benchLANG .NET binary-trees entry.

## Integration

| | |
|---|---|
| **Form** | source-drop (Visual Studio .NET WinForms project: modFBENCH.vb, fbench_lib.vb, fbench.vb) |
| **Dependencies** | .NET Framework with System.Windows.Forms and Microsoft.VisualBasic.Compatibility; kernel32 GetTickCount via Declare |
| **Minimum toolchain** | Visual Studio .NET project format ProductVersion 7.0.9955 (Release config: Optimize=true, RemoveIntegerChecks=true); .NET Framework version not stated |
| **Platforms** | Windows only as written; the published row ran on Windows XP (CPU not named) |
| **Thread safety** | not applicable; all state lives in module-level variables driven from the UI thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the number: the VB.NET loop computes sine with fSin and arcsine with the internal aTan2/aTan, with Math.Sqrt as the only library call, while the C reference row (src/c/Makefile 'gcc -Wall -O3 -lm', -DINTRIG commented out) uses libm for sin, asin and tan. The page's own Pentium 4 row shows the two C modes differ by 1.25x (0.00862 vs 0.01074 s per 1000 iterations), and the VB.NET mix matches neither mode, so 0.866 is not a same-work ratio.
- Latent correctness bugs in the port's maths library (fbench_lib.vb, also in the VB6 original). LibInitialise, which fills the atanc arctangent table, is never called, so the table stays all zeros. The table also stores 0.982793723247329 in atanc(4) where its own comment says 1.1071487177940905. And aInt converts with VB's round-half-even Integer conversion instead of truncating. aTan therefore returns wrong values for any argument of 0.25 or more, which means any arcsine of an argument above about 0.2425. The fbench lens never reaches that range, so the published results are still correct, but any other lens or steeper ray would give wrong results without warning.
- There is no automatic accuracy check. Unlike fbench.c, which compares its output with reference strings, the VB.NET app only lists the numbers, and fbench.html says such ports leave the comparison to the user.
- The comparison crosses machines and toolchains. The C row is labelled 'GCC 3.2.3 -O3, Linux' while the VB.NET row ran on Windows XP. The page says each language was compared with C on the same machine, but it names neither the machine nor the C compiler used on Windows. Timing is GetTickCount, which is fine for the page's roughly five-minute runs.

## Known shortcomings

- Unequal work: the VB.NET project times fbench's own polynomial sin/cos/atan while the C reference calls libm (INTRIG off); VB.NET ran on Windows XP against GCC 3.2.3 on Linux.
- Harness flaw confirmed: the VB.NET timed loop uses the fSin polynomial and the internal aTan with Math.Sqrt, and only tan comes from the library (35 polynomial sines, 24 internal arcsines and 12 Math.Tan calls per iteration), while the C reference uses libm for all, so the mix matches neither C mode. Latent port bugs in VB.NET and VB6: LibInitialise is never called (the atanc table stays all zero), atanc(4) has the wrong value, aInt rounds instead of truncating, and aTan is wrong for arguments of 0.25 or more (the fbench lens never reaches that). The port has no automatic result check.

## Caveats and trade-offs

Different work on the two sides: the VB.NET timed loop mostly uses the benchmark's internal polynomial trig routines (the C equivalent is the INTRIG build), while the C reference row uses libm trig; on the page's own Pentium 4 / GCC 3.2.3 -O3 row the C INTRIG build is 0.01074 s vs 0.00862 s for the libm build, so the two modes are not interchangeable. The VB.NET row ran on Windows XP and the C reference row is GCC 3.2.3 on Linux; the page says each language was compared with C 'on the same machine' but names neither the machine nor the C build used for this row. The reference compiler is 2003-vintage (the page's own G++ 5.4.0 -O3 row is 0.939, also faster than the C reference). No mechanism, CPU model, .NET version or date for the VB.NET run is given. The VB6 build of the same port is 1.132 (slower). CC BY-SA 4.0 is not an OSI licence, so reference only. Last commit 2021-09-24 and the author does not say the work is complete. [retier] Enricher: the VB.NET timed loop uses the fSin polynomial and the internal aTan with Math.Sqrt, and only tan comes from the library (35 polynomial sines, 24 internal arcsines and 12 Math.Tan calls per iteration). Latent port bugs in VB.NET and VB6: LibInitialise is never called (the atanc table stays all zero), atanc(4) is wrong, aInt rounds instead of truncating, and aTan is wrong for arguments of 0.25 or more; the port has no automatic result check.

None to adopt: this is a benchmark result, not a library. CC BY-SA 4.0 is a share-alike content licence, not OSI-approved for code.

## Maintenance

Abandoned (last commit 2021-09-24, page last updated the same day) and CC BY-SA 4.0. The VB.NET project is a 2002/2003-era WinForms upgrade-wizard conversion, so this is a reference data point only, with nothing to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The 0.866 relative time is on the page, but no valid same-work comparison exists: the checked-in VB.NET project (src/visualbasic/vbnet) times the benchmark's own polynomial sine/cosine and arctangent routines while the C reference (src/c/Makefile, INTRIG off) calls the C library's trig functions, and the VB.NET row ran on Windows XP against a C row built with GCC 3.2.3 on Linux, with no CPU, .NET version or C build named for the VB.NET run; under the cross-run and crippled-baseline precedents this is D.
- **Verifier notes:** Numbers on the page match (VB.NET 0.866, VB6 1.132), but the checked-in VB.NET source shows the port runs a different trig implementation from the C reference and on a different OS, so this is not a same-work language comparison; downgraded to D. maintenance_status corrected to abandoned (no completion statement; last commit 2021-09-24).
- **Fields the verifier corrected:** `compiler_and_flags`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** verifier batch-85 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/Web_pages/fbench.html>
  - <https://github.com/Fourmilab/floating_point_benchmarks>
  - <https://github.com/Fourmilab/floating_point_benchmarks/commits/master>
  - <https://github.com/Fourmilab/floating_point_benchmarks/tree/master/src>
  - <https://github.com/Fourmilab/floating_point_benchmarks/tree/master/src/visualbasic>
  - <https://github.com/Fourmilab/floating_point_benchmarks/tree/master/src/visualbasic/vbnet>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/LICENSE.md>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/c/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/c/fbench.c>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vbnet/fbench.vbproj>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vbnet/fbench.log>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vbnet/modFBENCH.vb>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vbnet/fbench_lib.vb>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vbnet/fbench.vb>
- **Sources the enricher read:**
  - <https://github.com/Fourmilab/floating_point_benchmarks/commits/master>
  - <https://github.com/Fourmilab/floating_point_benchmarks/tree/master/src/visualbasic>
  - <https://github.com/Fourmilab/floating_point_benchmarks/tree/master/src/visualbasic/vb6>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/LICENSE.md>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/Web_pages/fbench.html>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/c/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/c/fbench.c>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vbnet/fbench.vbproj>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vbnet/fbench.log>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vbnet/modFBENCH.vb>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vbnet/fbench_lib.vb>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vbnet/fbench.vb>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vb6/fbench.vbp>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vb6/fbench.bas>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vb6/fbench_lib.bas>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/master/src/visualbasic/vb6/fbench.frm>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:vb.net/fourmilab/floating_point_benchmarks#fbench`) · [data/wave14/enrich/raw/lang_vb_net_fourmilab_floating_point_benchmarks_fbench.json](../../../data/wave14/enrich/raw/lang_vb_net_fourmilab_floating_point_benchmarks_fbench.json) (enrichment confidence 0.7)

</details>
