# FreeBSD libmd md5block.S (amd64 baseline, BMI1 and AVX-512 MD5 kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly (x86-64, with C ifunc dispatch)` · `BSD-2-Clause` · 🟢 active

> FreeBSD libmd's hand-written amd64 MD5 block kernels (scalar, BMI1, AVX-512), 1.2-1.6x faster than libmd's C MD5.

| | |
|---|---|
| **Beats** | libmd's C MD5 block function: the 'orig' build (previous md5c.c) and the new 'generic' C build measured in the same review |
| **Claimed result** | Snippet only (review page unreachable here): Ryzen 7 PRO 7840U (Zen 4): orig 774.6 MB/s, generic 758.5, baseline asm 945.5, bmi1 asm 1062.4, avx512 asm 936.0 (derived from snippet data: bmi1 1.40x over generic C, 1.37x over orig C; baseline asm 1.22x over orig). Core i7-1165G7 (Tiger Lake): orig 605.9 MB/s, generic 587.8, baseline asm 765.3, bmi1 854.0, avx512 965.1 (derived from snippet data: avx512 1.64x over generic C, 1.59x over orig C). The ifunc dispatcher picks bmi1 on AMD and avx512 on Intel parts with AVX-512F/VL, matching the fastest variant per CPU. |
| **Workload** | MD5 hashing throughput in MB/s over a large input (run times of roughly 10-14 s per variant), comparing libmd variants orig, generic, baseline, bmi1 and avx512 in the D45670 review; method and exact command not visible in the snippet. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 PRO 7840U (Zen 4) and 11th Gen Intel Core i7-1165G7 (Tiger Lake), per search snippet |
| **Adoption** | 9.4k stars on the freebsd-src publish-only mirror; kernels imported by commit d92e987 'lib/libmd: import md5 amd64 kernels' (2025-10-24), file lib/libmd/amd64/md5block.S by Robert Clausecker (BSD-2-Clause) |
| **Last commit** | 2025-10-24 |
| **Links** | [repository](https://github.com/freebsd/freebsd-src) · [benchmark](https://reviews.freebsd.org/D45670) |

## Verdict

Robert Clausecker's own runs in Phabricator review D45670, known here only from search snippets: MD5 throughput over a large input with unknown compiler, flags and command, on a Ryzen 7 PRO 7840U (old C 774.6, new C 758.5, scalar asm 945.5, BMI1 1062.4, AVX-512 936.0 MB/s) and a Core i7-1165G7 (old C 605.9, new C 587.8, scalar asm 765.3, BMI1 854.0, AVX-512 965.1 MB/s). The dispatched kernel is 1.40x (Zen 4) and 1.64x (Tiger Lake) faster than the new C fallback and 1.37x and 1.59x faster than the previous md5c.c (derived from snippet data); the C rewrite's commit message itself says it is slightly slower than the original C.

## Use it when

- You hash large files or streams with MD5 on FreeBSD amd64 (checksums, legacy protocol fields, dedup keys) and want the fastest single-stream libmd path for free.
- You need a small, BSD-2-Clause, dependency-free single-buffer MD5 kernel to vendor into C or C++ code on x86-64 SysV, with a ready CPU dispatch policy (AVX-512VL on Intel, BMI1 elsewhere, scalar fallback).
- Intel parts with AVX-512F and AVX-512VL (Ice Lake, Tiger Lake, Xeon Scalable): the AVX-512 kernel was the fastest variant there in the author's runs (965.1 MB/s vs 587.8 MB/s for the new C code on a Core i7-1165G7).
- AMD Zen and other BMI1 CPUs: the BMI1 kernel (1062.4 MB/s vs 758.5 MB/s for the new C code on a Ryzen 7 PRO 7840U).

## Skip it when

- Many independent messages at once: a multi-buffer SIMD MD5 (minio/md5-simd, or the md5x8 kernel in gocrack) runs several streams per core and gets far higher aggregate throughput.
- Anything security-relevant: MD5 is broken for collisions; use SHA-256 or BLAKE3.
- You already link OpenSSL: its MD5 is also hand-written x86-64 assembly, and no comparison of these kernels against OpenSSL (or animetosho/md5-optimisation) was published; the measured baseline is only libmd's own C code.
- Windows x64 or other non-SysV ABIs, and non-amd64 targets (aarch64 has a separate kernel in lib/libmd/aarch64): the kernels take arguments in rdi/rsi/rdx and clobber xmm8-xmm15 without saving them.
- Kernel, bootloader or bootstrap builds: the FreeBSD kernel, libsa and libcrypt use the C md5c.c, and the asm is skipped when BOOTSTRAPPING or WITHOUT_MACHDEP_OPTIMIZATIONS is set.

## How it is fast

MD5 is one serial dependency chain, so the gain comes from shortening each round's critical path rather than from parallelism: the baseline kernel keeps a, b, c, d in registers, folds the round constant and message word into the add chain before the round function result arrives, and unrolls all 64 rounds through GAS macros. The BMI1 kernel rewrites round function G as (d & b) + (\~d & c) and I as -1 - (c ^ (\~b & d)) using ANDN, which removes a dependent mov/xor step. The AVX-512 kernel is not vectorised across messages: it uses single-lane XMM registers so that VPTERNLOGD computes each round function in one instruction and VPROLD does the rotate, with the constant added through an embedded-broadcast load.

## Compared with alternatives

Pick it over animetosho/md5-optimisation when you want a short, already-integrated BSD-2-Clause kernel set with a tested dispatch policy rather than the widest menu of single-buffer variants (animetosho's work is the one actually measured against OpenSSL's assembly); pick minio/md5-simd or gocrack instead when you hash many independent streams and can use multi-buffer SIMD.

## Integration

| | |
|---|---|
| **Form** | shared lib (part of FreeBSD base libmd on amd64) or source-drop of md5block.S plus a small dispatcher |
| **Dependencies** | none at run time; in tree it uses FreeBSD headers &lt;machine/asm.h&gt; (ENTRY/END), &lt;x86/ifunc.h&gt; (DEFINE_UIFUNC), &lt;machine/cpufunc.h&gt; and &lt;machine/specialreg.h&gt;, which an out-of-tree copy replaces with plain .globl symbols and its own CPUID check |
| **Minimum toolchain** | not documented; needs an assembler that understands BMI1 and AVX-512VL with EVEX embedded broadcast (FreeBSD base builds it with clang); the companion C fallback uses clang's _Pragma("unroll") |
| **Platforms** | x86-64 only (SysV ABI); scalar kernel on any x86-64, BMI1 kernel needs BMI1, AVX-512 kernel needs AVX-512F and AVX-512VL and is never selected on AMD |
| **Thread safety** | not documented; all state lives in the caller's MD5_CTX and the dispatcher resolves once at load time, so separate contexts can be used from separate threads |
| **Drop-in for the baseline** | yes |

## Gotchas

- Context-wipe regression in the code that ships with the kernels: the C rewrite imported under the same review (commit 90fa789, sys/crypto/md5c.c on main) ends MD5Final with explicit_bzero(ctx, sizeof(ctx)), which clears only 8 bytes (pointer size) of the 88-byte MD5_CTX; state[2..3], the bit count and the 64-byte buffer holding the message tail stay in memory, whereas the pre-rewrite code cleared sizeof(\*context). Digests and speed are unaffected.
- The AVX-512 kernel is slower than the BMI1 kernel on AMD Zen 4 in the author's own numbers (936.0 vs 1062.4 MB/s, even below the scalar asm at 945.5), so md5dispatch.c excludes AMD by vendor string; a copy that dispatches on feature bits alone picks the slower kernel on Zen 4. A Zen 4 performance regression the author mentioned in the related review D52909 is probably this, but the resolution is snippet-only.
- lib/libmd/tests checks only the seven RFC 1321 vectors through whichever kernel the ifunc picks on the test host, so the two kernels not selected on that machine are not exercised by the in-tree tests.
- The kernels process only whole 64-byte blocks (len is masked with \~63) and never touch MD5_CTX.count or buffer; padding, length and partial blocks stay in the C MD5Update/MD5Final, whose length parameter is unsigned int (split inputs over 4 GiB).

## Known shortcomings

- Numbers come only from search snippets of reviews.freebsd.org/D45670 (blocked here): Zen 4 bmi1 1.40x over the generic kernel, Tiger Lake avx512 1.64x (orig 605.9 MB/s); no harness, compiler or flags; the baseline is libmd's own C code, not OpenSSL; the numbers may predate later revisions of the review (opened 2024-06-21); the dispatcher skips AVX-512 on AMD.
- Enricher: the three kernels' round tricks check out (ANDN rewrite of G and I, vpternlogd 0xca, 0xe4, 0x96, 0x39) and the D45670 numbers recur in snippets (Zen 4 orig 774.6 vs bmi1 1062.4 MB/s), but no harness is in the tree; the AVX-512 kernel is slower than bmi1 on Zen 4 (936.0 vs 1062.4), hence the AMD exclusion; in-tree tests run only the RFC 1321 vectors through whichever kernel ifunc picks; the kernels are SysV-only. Defect shipped with them (C rewrite 90fa789, same review, still on main): MD5Final does explicit_bzero(ctx, sizeof(ctx)), clearing 8 of 88 bytes of MD5_CTX (a context-wipe regression; digest and speed unaffected). The rewrite's own commit message says the new C is slightly slower than the old C.

## Caveats and trade-offs

The commit d92e987 ('lib/libmd: import md5 amd64 kernels', committed 2025-10-24, Reviewed by imp, Approved by markj) carries no numbers, only 'Differential Revision: https://reviews.freebsd.org/D45670'. reviews.freebsd.org, reviews-dev.freebsd.org and cgit.freebsd.org do not resolve here, so every number comes from WebSearch result snippets of the D45670 review (titled 'lib/libmd: reimplement and enhance md5', opened by fuz on 2024-06-21) and is snippet only. One search snippet notes that an earlier revision of the review (id=144760) carried different labels and numbers, so the figures may predate later changes to the committed kernels; a related review (D52909) snippet mentions a Zen 4 performance regression noticed when moving the md5 code. Compiler, flags, input size and command are unknown; author-run on two laptop CPUs, one run each as far as visible. 'orig' is the previous md5c.c and 'generic' the reimplemented C path, so the baseline is libmd's own C code, not OpenSSL MD5. The author notes the AVX-512 kernel is not really vectorised (it uses vpternlogd for the round functions), and md5dispatch.c skips it on AMD because it 'performs poorly on AMD'. The kernel build always uses the generic C version (the AVX-512 kernel is compiled only outside _KERNEL).

Three kernels selected at load time by an ifunc resolver (lib/libmd/amd64/md5dispatch.c): AVX-512 (vpternlogd, XMM-only) when AVX512F and AVX512VL are present and the vendor is not AMD, else BMI1 (ANDN shortens dependency chains), else the baseline scalar kernel. The review snippet says the kernel build reuses the new code except the AVX-512 path (FPU state cost). Single-stream MD5 (no multi-buffer); MD5 itself is cryptographically broken, only for compatibility and checksums. amd64 only.

## Maintenance

Active: committed to FreeBSD main on 2025-10-24 (d92e987, with an aarch64 SIMD kernel in c1135b2 whose only later change is a GNU-as build fix), BSD-2-Clause and small enough to vendor; evidence stays first-party and snippet-only, and the C MD5Final shipped alongside wipes only 8 bytes of the context (explicit_bzero(ctx, sizeof(ctx))).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers posted by the author (Robert Clausecker) in his own Phabricator review D45670, comparing the asm kernels against libmd's old and new C MD5 block functions on two named CPUs; no compiler, flags, input size or benchmark command are visible, and the review page itself is unreachable here (reviews.freebsd.org ENOTFOUND), so the figures are confirmed from WebSearch snippets only. Kernel code is public (lib/libmd/amd64/md5block.S, md5dispatch.c) but no benchmark harness is, so C.
- **Verifier notes:** Real, copyable BSD-2-Clause asm MD5 kernels in FreeBSD libmd with a modest 1.4-1.6x gain over the C block function; numbers confirmed only through search snippets of the blocked Phabricator review, with the Tiger Lake 'orig' figure now exact (605.9 MB/s). Shortcomings: snippet-only evidence, no published harness, compiler or flags, baseline is libmd's own C code rather than OpenSSL, numbers may come from an earlier review revision.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-124 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/freebsd/freebsd-src/commit/d92e987421001c365216b039f8c3303939c195f7>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libmd/amd64/md5block.S>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libmd/amd64/md5dispatch.c>
  - <https://github.com/freebsd/freebsd-src/commits/main/lib/libmd/amd64>
  - <https://github.com/freebsd/freebsd-src>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libmd/amd64/md5block.S>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libmd/amd64/md5dispatch.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libmd/Makefile>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libmd/md5.h>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libmd/tests/Makefile>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/sys/md5.h>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/crypto/md5c.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/73a9b273d3d315716304c2cc237fef3141a93f2a/sys/crypto/md5c.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libcrypt/Makefile>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/conf/files.amd64>
  - <https://github.com/freebsd/freebsd-src/commits/main/lib/libmd>
  - <https://github.com/freebsd/freebsd-src/commits/main/sys/crypto/md5c.c>
  - <https://github.com/freebsd/freebsd-src/commit/90fa789cfab54294d4c3a0ac74e01747ce074386>
  - <https://github.com/freebsd/freebsd-src/commits/main/lib/libmd/aarch64>
  - <https://github.com/freebsd/freebsd-src/commit/244f498074b5574d18d4518583863580498b8d3b>
  - https://reviews.freebsd.org/D45670 (WebSearch snippet only, host unreachable)
  - https://reviews-dev.freebsd.org/differential/diff/163567/ (D52909, WebSearch snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `paper:freebsd-libmd-amd64-md5block`) · [data/wave13/enrich/raw/paper_freebsd_libmd_amd64_md5block.json](../../../data/wave13/enrich/raw/paper_freebsd_libmd_amd64_md5block.json) (enrichment confidence 0.7)

</details>
