# Box86 (x86 userspace emulator for ARM with dynarec)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> 32-bit x86 Linux userspace emulator for armhf with a dynarec; author's 2022 7-Zip test: about 4.5x QEMU, 2.6x FEX.

| | |
|---|---|
| **Beats** | QEMU user-mode (x86 guest) and FEX; also Box86's own interpreter |
| **Claimed result** | Search-result text of the article as recorded by the search agent (not re-confirmed by the verifier; article blocked): 7-Zip MIPS native ARM 6157, Box86 3117 (about 50% of native), FEX 1197 (about 19%), QEMU 691 (about 11%), so Box86 about 4.5x QEMU and about 2.6x FEX (derived from snippet data, article not opened); glmark2 Box86 178 versus native 181. A news summary of the same article (snippet only) gives Box64 at 27-53% of native versus QEMU 5-16% and FEX-emu 13-26% across 7-zip and dav1d. Repo docs/README.md: 'DynaRec ... providing a speed boost between 5 to 10 times faster than only using the interpreter.' First-party FOSDEM 2022 page (Box86 versus native only, 7z 16.02 'Tot' rating): Raspberry Pi 4 5733 native vs 2912 Box86 (51%, 2021), ODroid N2 8981 vs 3811 (42%), Phytium D2000/8 18001 vs 8462 (47%). |
| **Workload** | box86.org article 'Box86/Box64 vs QEMU vs FEX (vs Rosetta2)' (March 2022, by the Box86/Box64 author): 7-Zip benchmark MIPS run as an x86 (32-bit) guest under QEMU user-mode, FEX and Box86 on an ARM Linux machine, against the same benchmark built natively for ARM; further rows for dav1d and glmark2. |
| **Metric** | throughput |
| **Adoption** | 3.8k stars |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/ptitSeb/box86) · [benchmark](https://box86.org/2022/03/box86-box64-vs-qemu-vs-fex-vs-rosetta2/) |

## Verdict

In the Box86 author's March 2022 box86.org comparison (EGRESS_BLOCKED here; numbers from search-result text, which also says the 7-Zip build was version 16 from Ubuntu), 7-Zip as a 32-bit x86 guest scored Box86 3117 MIPS against native ARM 6157, FEX 1197 and QEMU user-mode 691, about 4.5x QEMU and 2.6x FEX (derived from snippet data), with no CPU, emulator versions or flags visible. The author's FOSDEM 2022 page gives hardware-labelled Box86-versus-native numbers only (7-Zip 16.02 'Tot' 40-61% of native across seven boards, e.g. ODROID N2 3811 vs 8981; dav1d 21-55%; glmark2 96-100%; OpenArena 72-86%), and the README's '5 to 10 times faster' DynaRec figure is against its own interpreter with no workload stated.

## Use it when

- Running closed-source 32-bit x86 Linux games and tools (GameMaker, Unity3D, older Steam titles, steamcmd) on ARM boards that can still run AArch32 userspace (Raspberry Pi 2-4, ODROID N2, RK3399/RK3588, Phytium D2000/FT2000).
- Running i386 Wine on ARM next to Box64, which needs Box86 (or Box32) for the 32-bit components.
- Programs that spend most of their time in wrapped libraries (OpenGL, SDL, Vulkan): the author's FOSDEM 2022 page shows glmark2 at 96-100% of native and OpenArena at 72-86%.
- Replacing qemu-i386 user-mode when throughput matters more than exact x87 precision or x86 memory ordering.

## Skip it when

- 64-bit-only ARM CPUs or distributions without an armhf multiarch or chroot: Box86 needs a 32-bit userspace and a 32-bit toolchain and is 'useless on 64-bit only systems'; use Box64's experimental Box32 mode or FEX there.
- Hand-optimised SIMD code, especially SSSE3: one SSSE3 op can expand to 10 NEON ops (pmaddubsw), and dav1d runs at only 21-55% of native on the FOSDEM page; CPU-bound integer code (7-Zip) sits at 40-61%.
- Software that needs x86 memory ordering or exact x87, NaN and rounding behaviour: the fast defaults relax all three, and multithreaded JIT guests (Mono, JVM) are switched to BIGBLOCK=0 STRONGMEM=1, which is slower.
- Non-ARM hosts or x86_64 binaries: the dynarec is ARM-only (other targets such as PowerPC LE run the interpreter), and 64-bit guests need Box64.
- When you need fast upstream fixes: the repo is in low-cadence maintenance with 186 open issues, including dynarec-only failures such as #1042 (La-Mulana runs only with dynarec disabled).

## How it is fast

The ARM dynarec translates x86 code in blocks over four passes (pass0 finds block extent and jumps, pass1 tracks flag use, pass2 sizes, pass3 emits), with a backward liveness pass (updateNeed) so x86 EFLAGS are only materialised when something reads them; MMX/SSE/SSE2 mostly map 1:1 onto NEON. Translated blocks are cached and guarded by page protection plus a hash signature, with a SIGSEGV handler catching writes to translated code. The biggest wins come from library wrapping, which runs GL, SDL or libc work at native speed, and from speed-over-accuracy defaults (STRONGMEM=0, FASTNAN=1, FASTROUND=1, x87 in float where possible).

## Compared with alternatives

Pick Box86 over FEX or QEMU user-mode when the guest is 32-bit x86 and the host can run armhf: in the author's 2022 7-Zip run it reached about 50% of native against 19% for FEX and 11% for QEMU. Use Box64 for x86_64 guests (or its Box32 mode on 64-bit-only hosts), FEX on aarch64-only hardware or when you want stricter x86 semantics, and Blink to run x86-64 Linux programs on non-ARM hosts.

## Integration

| | |
|---|---|
| **Form** | standalone executable (CMake build from source, installs the box86 binary, a binfmt_misc entry, bundled x86 libs and /etc/box86.box86rc; Debian packaging in debian/) |
| **Dependencies** | armhf (32-bit) libc plus the 32-bit native libraries to be wrapped (SDL, OpenGL or gl4es, Vulkan); optional Zydis for TRACE builds; ccache recommended for development |
| **Minimum toolchain** | CMake 3.10+, a 32-bit ARM GCC (gcc-arm-linux-gnueabihf on aarch64 hosts), -std=gnu11; docs recommend -DCMAKE_BUILD_TYPE=RelWithDebInfo with a board profile (-DRPI4=1, -DODROIDN2=1, -DRK3588=1 ...) |
| **Platforms** | 32-bit little-endian ARM Linux userspace (armhf) on ARMv7, or on ARMv8 CPUs that keep AArch32 at EL0 with a multiarch or chroot setup; dynarec for ARM only |
| **Thread safety** | Emulates multithreaded guests; dynarec block building (FillBlock) is not multithreaded, and BOX86_DYNAREC_WAIT chooses whether other threads wait for it or fall back to the interpreter |
| **Drop-in for the baseline** | partial: replaces qemu-i386 user-mode via binfmt_misc for x86 Linux binaries, but only on armhf userspaces, with relaxed x87 and memory-ordering defaults, and some programs need per-app box86rc profiles |

## Gotchas

- Config precedence is inverted from what most tools do: \~/.box86rc beats /etc/box86.box86rc, which beats the command line, so BOX86_\* variables you set when benchmarking can be silently overridden by a shipped per-program profile.
- JIT'd guest code is tracked with memory protection and a SIGSEGV handler, so gdb stops on many 'normal' segfaults; use `handle SIGSEGV nostop` and break in my_box86signalhandler.
- Several correctness fixes landed in September 2026 after the newest CHANGELOG entry (v0.3.8): a use-after-free in aligned_realloc, a CVTTPS2PI lower-lane bounds check, an atfork loop out-of-bounds, interpreter LOCK 16-bit INC/DEC; build from master rather than an old package.
- The QEMU and FEX numbers come from a 2022 article by the Box86 author, read here only through search-result text: the machine, the QEMU, FEX and Box86 versions and the build flags are not visible; QEMU and FEX keep 80-bit x87 in softfloat while Box uses hardware float, and 7-Zip's built-in benchmark ('7z b') runs one thread per core by default (4 threads in the FOSDEM sample output), so the scores also reflect each emulator's threading and atomics handling.

## Known shortcomings

- The QEMU and FEX 7-Zip numbers (7z 3117 vs QEMU 691) are a 2022 first-party article by a competitor's author, read as snippets only (box86.org blocked) with no CPU model; the FOSDEM 2021 page (rajdakin/box86-fosdem2021-content performances.md) compares Box86 with native on named boards; the 5-10x dynarec claim is against its own interpreter with no method. Not a duplicate of Box64.
- Enricher: the QEMU and FEX 7-Zip numbers (3117 vs 6157 native, 1197 FEX, 691 QEMU) are confirmed only through search-result text with machine, versions and flags unknown; the FOSDEM page compares Box86 with native only. \~/.box86rc overrides /etc rc, which overrides the command line, so shipped profiles can silently override benchmark environment variables; fast defaults (STRONGMEM=0, FASTNAN=1, FASTROUND=1) relax semantics; September 2026 bug fixes postdate v0.3.8; maintenance is low-cadence (about 15 commits from 2025-06 to 2026-09), and Box64's Box32 now covers 32-bit binaries.

## Caveats and trade-offs

Snippet only: box86.org is blocked here (EGRESS_BLOCKED), so the article itself was not opened; the 7-Zip and glmark2 numbers come from search-result text that the verifier could not reproduce, and no CPU model, compiler flags, guest binary versions or QEMU and FEX versions are visible. The measurement is from March 2022 and was made by the Box86 author, a competing project; FEX has changed substantially since (per the catalogued FEX entry, a FEX maintainer said in October 2024 that he had never compared FEX with Box). FEX needs aarch64, so the Box86 versus FEX rows imply an aarch64 machine running an armhf userspace for Box86. The same article's Box64 and Rosetta2 comparison ran on an Apple M1; the machine for the Box86 rows is not visible. QEMU and FEX use softfloat for x87 to keep 80-bit precision while Box uses hardware float (lower precision), which favours Box on x87 code. glmark2 and game rows mostly measure native GL pass-through via wrapped libraries, not the JIT. The author's FOSDEM 2021/2022 page (github.com/rajdakin/box86-fosdem2021-content performances.md) has Box86 versus native only (7-Zip 40-61% of native, dav1d 21-55%, glmark2 96-100%, OpenArena 72-86%) on named boards with 7z 16.02 from Debian, but no Box86 build flags and no QEMU or FEX rows. The 5-10x dynarec claim in the README is versus Box86's own interpreter and has no workload, CPU or flags. The article is also the source used for the catalogued Box64 and FEX entries. [retier] QEMU and FEX 7-Zip figures (3117 vs QEMU 691, FEX 1197, native 6157) come from a 2022 box86.org article by Box64's author, read as search snippets only, with no machine, versions or flags; the FOSDEM 2021 page compares Box86 with native only; the 5-10x dynarec claim is against its own interpreter. Default fast settings (STRONGMEM=0, FASTNAN=1, FASTROUND=1) relax semantics and rc files override command-line settings. About 15 commits from 2025-06 to 2026-09; Box64's Box32 now handles 32-bit binaries. Not a duplicate of Box64.

Needs a 32-bit ARM userspace (armhf, a multiarch or chroot environment on aarch64) and is useless on 64-bit-only systems; runs x86 Linux programs only (x86_64 is the separate Box64 project, already catalogued from the same article); wraps native system libraries (libc, libm, SDL, OpenGL), which is where much of the speed on games comes from; dynarec uses memory protection plus a SIGSEGV handler, so debugging JIT-using programs under gdb is noisy.

## Maintenance

MIT-licensed, 3.8k stars and not archived, but in low-cadence maintenance (about 15 commits between 2025-06-22 and 2026-09-27, mostly opcodes, wrappers and bug fixes) while the Box64 README now offers Box32 as an alternative for 32-bit binaries; still the standard way to run i386 Linux binaries on armhf.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The QEMU and FEX comparison is a first-party article by the Box86/Box64 author on box86.org, which is EGRESS_BLOCKED here; a search snippet (news summary of the article) confirms it compared Box against QEMU and FEX on 7-zip and dav1d, but the exact Box86 row numbers in the record could not be re-confirmed. The author's FOSDEM 2021/2022 performance page (rajdakin/box86-fosdem2021-content performances.md) gives first-party Box86 versus native numbers with hardware but no QEMU or FEX rows, no Box86 build flags and no public harness, so C.
- **Verifier notes:** Repo metadata confirmed (MIT, 3.8k stars, not archived, last commit 2026-09-27). Shortcomings: first-party 2022 comparison by a competitor's author, article blocked so the Box86/QEMU/FEX numbers rest on a search snippet the verifier could not reproduce, no hardware or versions visible for those rows; hardware-stated first-party Box86-versus-native numbers exist on the FOSDEM page. Box86 is the 32-bit sibling of the catalogued Box64, not a duplicate.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** first-party table with hardware or an independent run
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ptitSeb/box86/HEAD/docs/README.md>
  - <https://github.com/ptitSeb/box86>
  - <https://github.com/ptitSeb/box86/commits>
  - <https://raw.githubusercontent.com/rajdakin/box86-fosdem2021-content/master/performances.md>
- **Sources the enricher read:**
  - <https://github.com/ptitSeb/box86>
  - <https://github.com/ptitSeb/box86/commits/master>
  - <https://github.com/ptitSeb/box86/issues?q=is%3Aissue+slow+OR+performance+OR+qemu+OR+fex>
  - <https://github.com/ptitSeb/box86/tree/master/src/dynarec>
  - <https://raw.githubusercontent.com/ptitSeb/box86/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/ptitSeb/box86/HEAD/docs/COMPILE.md>
  - <https://raw.githubusercontent.com/ptitSeb/box86/HEAD/docs/USAGE.md>
  - <https://raw.githubusercontent.com/ptitSeb/box86/HEAD/docs/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ptitSeb/box86/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ptitSeb/box86/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ptitSeb/box86/HEAD/src/dynarec/dynarec_arm.c>
  - <https://raw.githubusercontent.com/ptitSeb/box86/HEAD/src/dynarec/dynarec_arm_pass0.h>
  - <https://raw.githubusercontent.com/ptitSeb/box86/HEAD/src/dynarec/dynarec_arm_pass1.h>
  - <https://raw.githubusercontent.com/rajdakin/box86-fosdem2021-content/master/performances.md>
  - <https://raw.githubusercontent.com/ptitSeb/box64/HEAD/README.md>
  - https://box86.org/2022/03/box86-box64-vs-qemu-vs-fex-vs-rosetta2/ (EGRESS_BLOCKED; search-result text only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ptitseb/box86`) · [data/wave12/enrich/raw/github_com_ptitseb_box86.json](../../../data/wave12/enrich/raw/github_com_ptitseb_box86.json) (enrichment confidence 0.6)

</details>
