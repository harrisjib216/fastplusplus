# Arm Optimized Routines (string subproject)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Assembly` · `MIT OR Apache-2.0 WITH LLVM-exception` · 🟢 active

> Arm's own AArch64 assembly memcpy, memset, memchr, strlen, strcmp and friends; replaces generic or older libc string routines.

| | |
|---|---|
| **Beats** | System libc string.h routines; string/bench/memcpy.c runs the libc memcpy alongside the Arm variants with SPEC2017-derived size and alignment distributions, but no libc (glibc, musl, newlib, bionic) is named and no results are published |
| **Claimed result** | memcpy +26-37%, memmove \~2x on small sizes, memcmp +50-80%, strlen 2.9x, memchr 3x (vs the previous musl state, measured on Graviton4) |
| **Workload** | ClickHouse PR description: Arm's AdvSIMD/SVE/MTE string routines linked into ClickHouse for aarch64 and compared with the previous static-binary state, which used musl. |
| **Metric** | throughput |
| **Hardware** | AWS Graviton4 (Neoverse-V2) |
| **Adoption** | 716 stars, 126 forks; vendored in FreeBSD as contrib/arm-optimized-routines (README says v25.01); newlib syncs its aarch64 memchr, memcpy and strchr from it (WebSearch snippet only); biannual releases, latest v26.07 |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/ARM-software/optimized-routines) · [benchmark](https://github.com/ClickHouse/ClickHouse/pull/118916) |

## Verdict

No measured comparison against any libc exists in the repository; the only libc numbers are in ClickHouse PR #118916 (open, unmerged as of 2026-10-08), which reports memcpy +26-37%, memmove about 2x on small sizes, memcmp +50-80%, strlen 2.9x and memchr 3x on Graviton4 (Neoverse-V2) versus its musl build's previous routines, themselves 'generic C and 2020-vintage AOR asm', with no harness, sizes, compiler or run count stated, while the automated ClickHouse performance report showed no significant change across 32 queries.

## Use it when

- AArch64 binaries linked against a libc with generic C or stale string code: musl (static builds), newlib, older or custom embedded libcs, bare-metal and kernel-like environments.
- Fully static or PLT-free builds where you want glibc-class string routines without glibc's ifunc indirection (the ClickHouse PR's motivation).
- Workloads dominated by small, random-size memcpy/memcmp/strlen/memchr calls (the repo's own benchmarks use SPEC2017-derived size and alignment distributions, mostly under 300 bytes).
- Building a libc or runtime (as FreeBSD libc and Android bionic do) and needing a permissively licensed, maintained AArch64 string set with MTE-safe variants.
- You want to benchmark or pick a specific variant (AdvSIMD versus SVE versus MOPS) per core yourself.

## Skip it when

- On a current glibc for AArch64: the maintainer says 'pretty much all of it is in GLIBC already' (issue #71) and the ClickHouse PR expects no large change there; replacing glibc's ifunc-selected SVE memcpy on Graviton 3/4 made an early ClickHouse revision 12-17% slower in several queries.
- Blindly choosing the SVE string variants on 128-bit-SVE cores (Neoverse-V2, Graviton4): the ClickHouse PR reports them 'up to 3x slower' there and kept AdvSIMD instead.
- 32-bit Arm: the maintainer calls the string/arm routines 'quite old and not very optimized' (issue #71); x86-64 has no string routines at all (string/x86_64 holds only check-arch.S).
- Projects that need FORTIFY _chk variants (issue #27 still open) or a drop-in that dispatches by CPU feature on its own.
- Anyone who needs published numbers before adopting: the repo stores none, and the only figures against a libc are unmethodologised claims in an unmerged ClickHouse PR.

## How it is fast

Branchless size-class copying with overlapping unaligned loads and stores (small copies up to 32 bytes, medium up to 128, then a software-pipelined 64-byte loop with a 16-byte-aligned destination and an always-overlapping tail), so one entry point serves memcpy and memmove. The string scanners load 16 or 32 bytes at a time with AdvSIMD (or SVE/SVE2 predicated loads), compute a NUL/character syndrome and locate the first match with bit tricks instead of a byte loop; MOPS variants use the Armv8.8 CPYP/CPYM/CPYE and SETP instructions. The code is tuned on several Neoverse and Cortex cores and is the upstream source of glibc's AArch64 string routines.

## Compared with alternatives

Pick it over jnettlet/cortex_a72_memcpy (one core, memcpy/memset only, claims parity or small wins over this library on Cortex-A72) or dssgabriel's SVE string routines (a research set benchmarked against this library's 23.01 SVE versions) when you need a complete, maintained AArch64 string.h set with MTE-safe variants; bavison/arm-mem or copies-and-fills only make sense for 32-bit Raspberry Pi targets, and AOCL-LibMem is the x86 (AMD) counterpart.

## Integration

| | |
|---|---|
| **Form** | static lib, shared lib or source-drop (one .S file plus asmdefs.h per function) |
| **Dependencies** | none at run time; GNU make and a GCC or Clang that assembles the wanted extensions (+sve, +sve2, +mops, +memtag) |
| **Minimum toolchain** | not documented; CI moved to GCC 16 and Clang 22 in July 2026; SVE files are only built if the compiler supports them |
| **Platforms** | AArch64 (Armv8-A baseline; optional SVE, SVE2, SME streaming-compatible, MOPS, MTE variants) and 32-bit Arm; Linux/ELF primarily, with config.mk.dist sections for Windows on Arm (Msys, clang) and macOS |
| **Thread safety** | Stateless leaf routines operating only on caller buffers (reentrant); not otherwise documented |
| **Drop-in for the baseline** | partial: same C semantics and glibc-compatible ABI, but suffixed symbol names, so you alias them to memcpy/strlen yourself (link-time override is described as best effort for static linking) and choose the CPU variant yourself |

## Gotchas

- Harness flaw in string/bench/memcpy.c: the 'Forwards/Backwards memmove unaligned' rows call each memcpy variant, including the libc `memcpy` baseline row, on overlapping buffers (fn(a, a + 256 + (i & 31), size) with size up to 64 KB). That is undefined behaviour for a libc memcpy, and libc memmove is never timed, so those rows are not a valid libc comparison; Arm's own memcpy is overlap-safe by design.
- A user reported in issue #76 (Dec 2024) that the strlen benchmark built at -O2 'will just skip running the test function'; the maintainer replied he had not seen it with the latest version and suggested -flto. No benchmark results are stored anywhere in the repo.
- The default (non -mte) strlen, strchr and memchr read whole aligned 16-byte blocks past the terminator and are documented 'Not MTE compatible'; on MTE-enabled systems use the -mte variants, which ClickHouse measured 20-40% slower than plain strlen above 512 bytes. Issue #63 (closed 2023) was a false MTE fault from the 16-byte overread with unaligned input.
- memcmp may read all n bytes even when the first difference is earlier (issue #60, closed as correct per the C standard), which trips hand-written guard-page tests that pass a length longer than the mapped data.

## Known shortcomings

- No numbers against any libc; the string/bench harness has no stored results and commits only report gains over earlier versions (24% memset on Neoverse N1). Kept at D because FreeBSD vendors it in contrib/arm-optimized-routines.
- Enricher: string/bench/memcpy.c's memmove rows call libc memcpy on overlapping buffers (undefined behaviour) and never time libc memmove; issue #76 reports the strlen bench at -O2 skipping the call; the ClickHouse PR #118916 is still open with no stated method and a musl baseline ('generic C and 2020-vintage AOR asm'); SVE variants are up to 3x slower on 128-bit SVE and an early revision was 12-17% slower than glibc 2.39 __memcpy_sve; string/x86_64 holds only check-arch.S (no x86 routines); FreeBSD libc and Android bionic dispatch to AOR symbols and the maintainer says glibc already carries nearly all of it.

## Caveats and trade-offs

Tier D: no performance numbers versus any libc in the repo pages opened; string/bench/{memcpy,memset,strlen}.c are harnesses without stored results, and commit messages report only gains over the routine's previous version (e.g. 9190f2f, 24% on a random memset benchmark on Neoverse N1; 375f32e says the SVE2 strlen beats the AdvSIMD versions, no numbers). The same maintainers upstream AArch64 string routines to glibc, so against a current glibc on AArch64 the gap may be small; the expected win is over generic C libc code (musl, newlib generic) and older libcs, which is not measured here. AArch64 and 32-bit Arm only. The newlib usage comes from a search snippet because sourceware.org was unreachable. The same repo also holds math, fp and networking subprojects that other categories may report separately.

Arm-specific assembly (string/aarch64, string/arm, some string/x86_64); MTE-aware variants exist. In the ClickHouse integration memcpy and memmove pick SVE or AdvSIMD at first call, the routines are linked with --whole-archive and libc is kept in sanitizer builds. Math routines from the same repo were reverted in that PR for 0.5-2.5 ULP error, so only the string routines are covered here.

## Maintenance

Actively maintained by Arm (last commit 2026-10-08, biannual releases, latest v26.07, new SVE2 strlen and memchr in September 2026), dual MIT or Apache-2.0 WITH LLVM-exception, copyable; already shipped inside glibc, FreeBSD libc and Android bionic, so check your libc before vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** Neither README nor the string README gives any number; string/bench/memcpy.c benchmarks libc memcpy beside __memcpy_aarch64/_simd/_sve/_mops/__memcpy_arm but no results are published, and the commit messages opened quote only gains over earlier versions of the same routine (9190f2f: random memset benchmark 24% faster on Neoverse N1), not over a libc.
- **Verifier notes:** Kept at D and not rejected as not-notable: under 1k stars but widely used (FreeBSD vendors it in contrib/, newlib syncs from it per snippet). Shortcomings: no published numbers versus any libc; harness exists (string/bench) but results are not stored; gains likely small versus glibc AArch64, which shares authors and code lineage.
- **Fields the verifier corrected:** `baseline`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-35 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ARM-software/optimized-routines>
  - <https://github.com/ARM-software/optimized-routines/commits/master>
  - <https://github.com/ARM-software/optimized-routines/commits/master/string/aarch64>
  - <https://github.com/ARM-software/optimized-routines/commit/9190f2f>
  - <https://github.com/ARM-software/optimized-routines/commit/375f32e>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/README.md>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/README.md>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/bench/memcpy.c>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/bench/memset.c>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/bench/strlen.c>
  - <https://github.com/freebsd/freebsd-src/tree/main/contrib/arm-optimized-routines>
- **Sources the enricher read:**
  - <https://github.com/ARM-software/optimized-routines>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/README.md>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/README.md>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/Dir.mk>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/config.mk.dist>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/include/stringlib.h>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/include/benchlib.h>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/bench/memcpy.c>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/bench/strlen.c>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/bench/memset.c>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/aarch64/memcpy.S>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/aarch64/memcpy-sve.S>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/aarch64/strlen.S>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/aarch64/strlen-mte.S>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/aarch64/memchr.S>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/HEAD/string/aarch64/memcmp.S>
  - <https://github.com/ARM-software/optimized-routines/tree/master/string>
  - <https://github.com/ARM-software/optimized-routines/tree/master/string/aarch64>
  - <https://github.com/ARM-software/optimized-routines/tree/master/string/x86_64>
  - <https://github.com/ARM-software/optimized-routines/commits/master>
  - <https://github.com/ARM-software/optimized-routines/commits/master/string/aarch64/memcpy-sve.S>
  - <https://github.com/ARM-software/optimized-routines/commit/23c4393>
  - <https://github.com/ARM-software/optimized-routines/issues?q=is%3Aissue+memcpy+OR+strlen+OR+memchr+OR+string+OR+memset+OR+strcmp>
  - <https://github.com/ARM-software/optimized-routines/issues/76>
  - <https://github.com/ARM-software/optimized-routines/issues/71>
  - <https://github.com/ARM-software/optimized-routines/issues/60>
  - <https://github.com/ClickHouse/ClickHouse/pull/118916>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libc/aarch64/string/Makefile.inc>
  - <https://raw.githubusercontent.com/aosp-mirror/platform_bionic/main/libc/arch-arm64/dynamic_function_dispatch.cpp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/arm-software/optimized-routines`) · [data/wave13/enrich/raw/github_com_arm_software_optimized_routines.json](../../../data/wave13/enrich/raw/github_com_arm_software_optimized_routines.json) (enrichment confidence 0.75)

</details>
