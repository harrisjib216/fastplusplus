# Apex memmove (Trevor Herselman): SSE2 memcpy and memmove for x86 and x64

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `C` · `no license` · 🔴 abandoned

> Unlicensed 2016 mirror of Trevor Herselman's 2014 SSE2 memcpy/memmove with CPUID dispatch. Claims to beat the C library but ships no numbers.

| | |
|---|---|
| **Beats** | C library memcpy and memmove (the README names no baseline; the repo's source has no comparison) |
| **Claimed result** | No numbers on the pages opened ('fastest memcpy/memmove on x86/x64 ... EVER'). |
| **Workload** | No benchmark in the repository. README only says 'The fastest memcpy/memmove on x86/x64 ... EVER, written in C (according to the author)' and links the original CodeProject article, which could not be opened. |
| **Metric** | throughput |
| **Adoption** | 14 stars, 1 fork; code by Trevor Herselman (2014), mirrored by rukkal in 2016. Discussed on Hacker News as 'Apex memmove', on the PostgreSQL mailing list in July 2016 (Alvaro Herrera raised licence compatibility and asked for real-workload gains; snippet only) and in a 2020 Ultimate++ forum thread (snippet only). |
| **Last commit** | 2016-09-22 |
| **Links** | [repository](https://github.com/rukkal/apex-memmove) · [benchmark](https://github.com/rukkal/apex-memmove) |

## Verdict

Nothing is measured in the repository. The README says only 'The fastest memcpy/memmove on x86/x64 ... EVER (according to the author)'. The CodeProject article with the original methodology does not resolve from here, nor does the PostgreSQL 2016 thread where Alvaro Herrera asked for real-workload gains. The only number known, 3.55 ms vs 4.37 ms against the MSVC CRT memcpy in one Core i7 run, comes from a search snippet of a 2020 Ultimate++ forum post (snippet only, block size and flags unknown).

## Use it when

- Studying a compact C-intrinsics design for overlap-safe small copies: load-everything-then-store branch trees for sizes 0-112 bytes.
- Benchmarking against the CPUs it was tuned on (2014-era Core i, Core 2, Pentium 4), or keeping its history in a memcpy survey.
- Copying ideas into your own licensed code after independent testing; copying the files themselves is not possible because the mirror carries no license (see status note).

## Skip it when

- Any production use. No license, no tests and no benchmark are in the repository, and the tiberium variant has the out-of-bounds write described under gotchas.
- Modern CPUs with AVX2, AVX-512, ERMS or FSRM. The code is SSE2-only, and current libc memcpy implementations use wider vectors and rep movsb, which this code predates.
- Copies between 256 KiB and a few MB whose destination is read right afterwards. The 256 KiB non-temporal threshold is hard-coded, so such copies bypass the cache.
- Small fixed-size copies (struct copies, memcpy-based type punning). An indirect call through a function pointer replaces what the compiler would otherwise inline as a single move.
- Non-x86 targets, where it only forwards to libc memcpy and memmove.

## How it is fast

Copies of 112 bytes or less go through a branch tree with no loop. It loads every 16-byte SSE2 block plus an overlapping 8- or 16-byte tail before it stores anything, so a single path handles overlap. Larger copies use a 64-byte loop (tiberium) or a 32-byte loop (kryptonite) of unaligned SSE2 loads and stores, counting a negative offset up to zero. At 256 KiB and above, the copy aligns the destination to 16 bytes and prefetches 4 KiB ahead with _MM_HINT_NTA. It then writes with non-temporal _mm_stream_si128 stores, running forward or backward depending on overlap. No AVX, ERMS or rep movsb path exists.

## Compared with alternatives

Rarely. Agner Fog's asmlib and DPDK's rte_memcpy are x86 copy routines with documented measurements against glibc, and AOCL-LibMem covers AMD Zen with a benchmark tool. Pick apex-memmove only as a short, readable C-intrinsics reference for overlap-safe SSE2 small-size copies.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (emmintrin.h plus cpuid.h or intrin.h from the compiler) |
| **Minimum toolchain** | C99 (long long, declarations in for loops) or C++ with long long; MSVC, GCC or Clang for the CPUID path; other x86-64 compilers always get tiberium |
| **Platforms** | x86 and x86-64 with SSE2; any other architecture falls back to the C library |
| **Thread safety** | Copy routines are stateless. The first call's dispatcher writes the two global function pointers without atomics, a formal data race when several threads make their first call at once (each thread writes the same value). |
| **Drop-in for the baseline** | partial: same signature and return value, but different names called through function pointers; libc memcpy and memmove are not replaced, and memcpy also pays memmove's direction check |

## Gotchas

- Correctness bug found by reading the code; it was not run, since building is outside this task. In tiberium's backward (overlapping, dst &gt; src) path for 113 bytes to 256 KiB, `size = -size;` runs before the `size > 32` and `size > 48` tests (apex_memmove.c lines 377-382, apex_memmove.cpp lines 379-382). size is an unsigned size_t, so both tests always pass. When n mod 64 is 17-47, the tail loads from src-32 and src-48 and stores to dst-32 and dst-48 relative to the 17-47-byte remainder. That writes up to 31 bytes before dst and reads up to 31 bytes before src. Example: memmove(buf+10, buf, 150) overwrites buf[0..9] (source bytes outside the destination) and the 16 bytes before buf with the bytes that lie 10 positions earlier. kryptonite and mithril test before negating and are not affected. tiberium runs on x86-64 CPUs without SSE4.2 (Core 2, AMD K8/K10), on 32-bit SSSE3-only CPUs, and on every x86-64 build from a compiler other than MSVC, GCC or Clang.
- Copies of 256 KiB and up use _mm_stream_si128 non-temporal stores and never issue _mm_sfence (no sfence appears anywhere in the source). Another thread that sees a later ordinary flag store may still read stale destination data.
- Unaligned accesses through casts to long long\*, int\* and short\* are formally undefined behaviour under C alignment and strict-aliasing rules. They work on x86 with current compilers, but sanitizers will flag them.
- The .c and .cpp files are near-identical copies (the C++ one adds namespace apex). A fix to one must be repeated in the other.

## Known shortcomings

- No benchmark, numbers or baseline in the repo and no licence (reference only); the only number is a snippet of a 2020 Ultimate++ forum post (one MSVC run on a Core i7, 3.55 ms vs 4.37 ms CRT memcpy); the dispatcher sets memcpy = memmove; an abandoned 2016 mirror, 14 stars.
- Correctness bug found by reading the code (not run): in tiberium's backward overlap path for 113 bytes to 256 KiB, 'size = -size;' runs before the 'size &gt; 32' and 'size &gt; 48' tests (apex_memmove.c lines 377-382, .cpp 379-382); size is unsigned, so the tests always pass, and when n mod 64 is 17-47 the tail writes up to 31 bytes before dst (memmove(buf+10, buf, 150) clobbers buf[0..9] plus 16 bytes before buf). tiberium runs on x86-64 without SSE4.2, 32-bit SSSE3-only CPUs and non-MSVC/GCC/Clang x86-64 builds; kryptonite (SSE4.2) is clean. No sfence after the non-temporal stores used at 256 KiB and up. No licence in the mirror; the CodeProject original is reportedly CPOL (snippet only).

## Caveats and trade-offs

Tier D: a self-description with no numbers in the repository. A search-result snippet of a 2020 Ultimate++ forum post reports one user's single MSVC run on a Core i7: apex_memcpy averaged 3.55 ms against 4.37 ms for the CRT memcpy, with clang similar. Neither the block size nor the flags appear in the snippet. The page could not be opened, so none of it is claimed here. The same snippet notes that the code has no licensing information. The CodeProject article is the only methodology source, and codeproject.com does not resolve from here. A CodeProject message titled 'Bug' exists on the article (codeproject.com/Messages/5374685/Bug), but its content could not be read. The mirror has three commits, all dated 2016-09-22, and no tests or benchmark code, so the claim cannot be reproduced from the repository. The dispatcher points apex_memcpy and apex_memmove at the same routine, so memcpy pays the overlap handling. It selects a variant by CPUID: SSE4.2 is taken as a proxy for fast unaligned access (kryptonite), SSSE3 selects tiberium and SSE2 alone selects mithril (32-bit only); every other target falls back to the C library. The code targets 2014-era CPUs, long before ERMS and FSRM made rep movsb competitive in glibc and the MSVC CRT. The .c and .cpp files are near-identical copies.

x86 and x86-64 only (SSE2 intrinsics from emmintrin.h, cpuid dispatch via __cpuid or __get_cpuid, several variants named tiberium, kryptonite and mithril); falls back to the library functions elsewhere. No license text anywhere in the repository or file headers, so the code is reference only. Handles overlapping moves like memmove.

## Maintenance

Abandoned mirror (three commits, all on 2016-09-22, 14 stars, no issues filed). It is reference only: the mirror carries no license, and a PostgreSQL list post (search snippet only) says the CodeProject original is under the Code Project Open License. Its tiberium variant also has an out-of-bounds write on backward overlapping moves.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The repository holds only README.md and src/apex_memmove.{c,cpp,h}. The README says 'fastest memcpy/memmove on x86/x64 ... EVER (according to the author)'. No benchmark code, numbers or baseline appear anywhere in it, and the source comments only compare the author's own variants (memmove09, memmove40/41, mm04). The CodeProject article, the PostgreSQL thread and the Ultimate++ forum post do not resolve from this environment (ENOTFOUND), so no numbers could be checked.
- **Verifier notes:** Kept at tier D with no number on any reachable page. The main shortcomings are no benchmark and no license, so it is reference only, and the repository is an abandoned 2016 mirror with 14 stars. Low notability is a tag here, not a reject, under the keep-and-document rule. The only known number (3.55 ms vs 4.37 ms, one MSVC run on a Core i7) is snippet only; if the Ultimate++ forum or the CodeProject article opens elsewhere, it could support tier C. No license text was found anywhere, and is_fork_of and the license were left uncorrected.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-97 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/rukkal/apex-memmove>
  - <https://github.com/rukkal/apex-memmove/tree/master/src>
  - <https://github.com/rukkal/apex-memmove/commits>
  - <https://raw.githubusercontent.com/rukkal/apex-memmove/HEAD/README.md>
  - <https://raw.githubusercontent.com/rukkal/apex-memmove/master/src/apex_memmove.c>
  - <https://raw.githubusercontent.com/rukkal/apex-memmove/master/src/apex_memmove.cpp>
  - <https://raw.githubusercontent.com/rukkal/apex-memmove/master/src/apex_memmove.h>
- **Sources the enricher read:**
  - <https://github.com/rukkal/apex-memmove>
  - <https://github.com/rukkal/apex-memmove/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/rukkal/apex-memmove/master/README.md>
  - <https://raw.githubusercontent.com/rukkal/apex-memmove/master/src/apex_memmove.c>
  - <https://raw.githubusercontent.com/rukkal/apex-memmove/master/src/apex_memmove.cpp>
  - <https://raw.githubusercontent.com/rukkal/apex-memmove/master/src/apex_memmove.h>
  - https://www.codeproject.com/Messages/5374685/Bug (ENOTFOUND)
  - https://www.postgresql.org/message-id/000001d1d77e%2415e7f7f0%2441b7e7d0%24%40checknetworks.com (ENOTFOUND)
  - https://postgrespro.com/list/thread-id/1560674 (ENOTFOUND)
  - WebSearch: "apex memmove" Herselman bug OR benchmark memcpy codeproject (snippets only)
  - WebSearch: "Apex memmove" CPOL license "Code Project Open License" (snippets only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/rukkal/apex-memmove`) · [data/wave13/enrich/raw/github_com_rukkal_apex_memmove.json](../../../data/wave13/enrich/raw/github_com_rukkal_apex_memmove.json) (enrichment confidence 0.65)

</details>
