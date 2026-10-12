# BeeCrypt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1-or-later` · 🔴 abandoned

> Portable LGPL C crypto library with per-CPU assembler bignum code; 2003-era tables show 2-4.6x faster modexp than Java BigInteger.

| | |
|---|---|
| **Beats** | Java multiprecision-integer modular exponentiation (JVM 1.2.2 to 1.4.0; the file says only 'Java', presumably java.math.BigInteger) |
| **Claimed result** | BENCHMARKS file text: 'as of version 1.0.1 BeeCrypt now beats Java on every platform, including UltraSparc. Depending on the version of Java, BeeCrypt is from twice to four times faster.' Same-machine rows: Pentium III 600 / Windows 2000 / 256 MB: BeeCrypt 2.1.0 (Visual C 6.0) 4.3 sec vs Java 1.4.0 Sun Server VM 10.2 sec (\~2.4x, derived from page data) and Sun Client VM 19.7 sec (\~4.6x, derived from page data); Pentium III 450 / Solaris 8 / 128 MB: BeeCrypt 2.0.0 (gcc-2.95.2) 5.9 sec vs Java 1.3 Sun Server VM 17.1 sec (\~2.9x, derived from page data); UltraSparc I 143 / Solaris 8 / 128 MB: BeeCrypt 2.0.0 (Forte C++ 6.1, 64-bit) 40.7 sec vs Java 1.3.1 Sun Server VM 83.4 sec (\~2.0x, derived from page data). The file also says 'both on Solaris and Linux, beecrypt is least 5 times faster for this operation than a commercial product we at one time considered using' (product not named). |
| **Workload** | Modular exponentiation (1024-bit base ^ 1024-bit exponent mod 1024-bit modulus), 100 repetitions, wall time in seconds (less is better), BeeCrypt 2.0.0 to 2.3.0 (C with assembler) versus several Java VMs on 1999 to 2002 era machines (BENCHMARKS revision 1.17 and earlier). |
| **Metric** | latency |
| **Hardware** | Per row, 1999 to 2002 era: Pentium III 450/600/800/1000, PIII Mobile 850, Pentium Pro 200, Athlon 1000/1200, Pentium 4M 1700, Alpha EV6.7 667, UltraSparc I 143 and II 450, PowerPC 604 166/604ev 375/G3 400/7450, Itanium 666/733, StrongARM 110, IBM zSeries 633, Sparc v8 70; Java rows (Pentium III 450/600, Pentium II 333, Pentium Pro 200, PowerPC G3/G4, UltraSparc I 143) were mostly measured on different machines, only a few coincide with BeeCrypt rows |
| **Compiler and flags** | Compiler named per row (Visual C 6.0, Visual Studio .NET, gcc-2.95.x, gcc 3.2.1, Compaq C 6.3, Forte C 6.0 / Forte C++ 6.1); optimization flags not stated in this revision. The table predates tests/benchme.c (first revision 2003-03-01; BENCHMARKS revision 1.18 says 'Replaced with new benchmarking program results'); the C timings of that era come from beetest.c (now Attic/beetest.c,v, a loop of 100 mp32bnpowmod calls timed with clock()). The Java benchmark program is not in the CVS tree. |
| **Adoption** | SourceForge project, 161 downloads in the latest tracked week, 2 reviews (5.0 of 5); CVS only, no star count |
| **Last commit** | 2015-12-28 |
| **Links** | [repository](https://beecrypt.sourceforge.net/) · [benchmark](https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip) |

## Verdict

BENCHMARKS revision 1.17 (2003-01-28) times 100 modular exponentiations of 1024-bit random base and exponent mod a fixed 1024-bit prime: BeeCrypt 2.1.0 (Visual C 6.0) took 4.3 s on a Pentium III 600 under Windows 2000 against 10.2 s for the Java 1.4.0 Sun Server VM and 19.7 s for the Client VM (about 2.4x and 4.6x, derived from page data), with similar 2-3x gaps on Solaris 8 PIII 450 and UltraSparc I rows; no optimization flags are given and most Java rows ran on different machines. The current BENCHMARKS (revision 1.35, 2015) has only BeeCrypt-alone fixed-time scores from tests/benchme.c and does not say which of its two loops (1024^160 or 1024^1024 bits) the score is.

## Use it when

- Maintaining or building legacy software (for example old RPM stacks) that already links BeeCrypt and needs its RSA/DSA/DH/ElGamal API.
- Classic finite-field public-key operations (1024-bit-class RSA, DSA, DH) in C on an unusual or legacy CPU where BeeCrypt still has assembler bignum code (Alpha, IA-64, m68k, s390x, SPARC).
- Reading a compact, LGPL reference implementation of Barrett reduction plus sliding-window exponentiation with per-architecture assembler kernels.
- C code that must exchange key material with Java's security classes in the same encodings, which the README says the structures were designed for.

## Skip it when

- Any new security-sensitive deployment: the project is unmaintained (last CVS change 2015-12-28, last file release 4.2.1 per SourceForge, updated 2013-04-23) and has no published security process.
- Private-key operations exposed to timing or cache attackers: the sliding-window exponentiation is secret-dependent and rsapricrt has no blinding.
- Modern primitives: no AES-GCM, ChaCha20-Poly1305, X25519/Ed25519, ECDSA or post-quantum schemes (elliptic curves are still listed under 'Planned' in the README).
- When you need a speed claim against OpenSSL, BoringSSL or libsodium: none was ever published; the only comparison is against 1999-2002 JVMs.
- Projects that cannot accept LGPL-2.1-or-later linking terms.

## How it is fast

Modular exponentiation uses Barrett reduction with the mu coefficient precomputed once per modulus (stored in the mpbarrett struct) plus 4-bit sliding-window exponentiation over a table of odd powers g^1..g^15. The inner multiply-accumulate and squaring loops have hand-written assembler for x86 (including Pentium 4 SSE2 multiplication), x86_64, PowerPC/PPC64, SPARC v8/v8plus, Alpha, IA-64, ARM, m68k and s390x, generated from m4 sources (gas) or masm on Windows. RSA private-key operations use CRT, with the two half-size exponentiations run as OpenMP sections since 4.2.0.

## Compared with alternatives

The catalogued siblings (libsecp256k1, FourQlib, curve25519-voi, Snowshoe, the PQC entries) all target elliptic-curve or lattice schemes; pick BeeCrypt only when you are stuck with classic RSA/DSA/ElGamal/DH in C on legacy hardware or legacy code, otherwise use a maintained sibling or OpenSSL.

## Integration

| | |
|---|---|
| **Form** | shared lib (autotools/libtool build, static also possible; Makefile.mak and vcproj for MSVC) |
| **Dependencies** | none for the C core; C++ API needs IBM ICU &gt;= 2.8; optional OpenMP, Python module and Java JNI glue (gcj headers) |
| **Minimum toolchain** | ANSI C compiler plus GNU m4 and an assembler for the optimized routines; last maintenance commit (2015) fixed the C++ code for gcc-5.3.0 |
| **Platforms** | README lists Linux on x86, x86_64, alpha, arm, ia64, m68k, ppc, ppc64, s390, s390x and sparc; Solaris sparc/x86; Tru64; Darwin/MacOS X; Cygwin; Win32. MinGW and 64-bit AIX shared libraries were unfinished. |
| **Thread safety** | Contexts are caller-owned structs; 2.0.0 made mp32barrett operations multithread-safe (NEWS), and the FIPS-186 PRNG locks a pthread/Solaris/Win32 mutex (--enable-threads, default yes). The C++ API adds Java-style synchronization. |
| **Drop-in for the baseline** | partial — the baseline is Java BigInteger.modPow; BeeCrypt is a C library, reachable from Java only through the separate BeeCrypt for Java JCE provider and the JNI glue in java/, not as a BigInteger replacement |

## Gotchas

- Harness flaw: the C timings come from beetest.c, which times 100 mpbnpowmod calls with clock() (processor time on Unix, wall time on Windows) after the Barrett mu has already been computed by mpbset outside the loop; the Java harness is not in the tree, so whether the Java rows include JIT warm-up or per-call setup is unknown and the two sides are not measured the same way.
- The 2.0.0 rows behind the Solaris PIII 450 (about 2.9x) and UltraSparc I (about 2.0x) ratios predate the 2.1.0 fix for a missed carry in the C version of mp32sub, which the reduction path uses; NEWS does not say whether those builds used the C or the assembler routine.
- Not constant-time: mpbpowmodsld_w picks table entries and squaring counts from exponent bits, and rsapricrt has no base blinding; no side-channel hardening is mentioned anywhere in the source tree.
- mpbpowmod_w mallocs the 8-entry window table on every call without checking for NULL; NEWS also records later correctness fixes in mpextgcd_w (3.1.0 and 4.0.0), RSA keypair generation (4.0.0) and mpbsubmod (4.1.0).

## Known shortcomings

- Baselines are 1999-2002 Java BigInteger, not OpenSSL; flags unstated and the Java harness is not public; most rows ran on different machines. C timings came from Attic/beetest.c (BENCHMARKS,v rev 1.17, 2003-01-28), versions 2.0.0-2.3.0. LGPL-2.1-or-later per headers. Abandoned since 2015-12-28.
- Enricher: the C side is beetest.c timing 100 mpbnpowmod calls with clock() (CPU time) and the Barrett mu computed outside the loop, while the Java harness is absent, so the two sides were not measured alike; the 2.0.0 rows (Solaris PIII 450 2.9x, UltraSparc I 2.0x) predate the 2.1.0 fix of a missed carry in mp32sub. The sliding-window modexp is not constant-time and rsapricrt has no blinding. The SourceForge bug tracker returns 403.

## Caveats and trade-offs

The only numeric comparison reachable is against Java on 1999 to 2003 era hardware and JVMs (the table was removed from BENCHMARKS in revision 1.18, 2003-05-20; the newest revision 1.35 of 2015-12-28 holds only BeeCrypt-alone numbers, e.g. modular exponentiation score 64747 on a Core i7-2600). It says nothing about OpenSSL, libsodium or BoringSSL, so it is far off the usual incumbents and baseline_in_list is false. Java and BeeCrypt rows are mostly on different machines; the ratios quoted above use rows where machine and OS match as closely as the file allows. The C timings came from the old beetest.c program, not tests/benchme.c, and the Java harness is not public, so the comparison cannot be reproduced. The 5x-over-a-commercial-product remark names no product. An independent 2008 panthema.net speedtest (OpenSSL vs BeeCrypt vs Crypto++ vs Botan) exists but the host is EGRESS_BLOCKED here and search summaries gave conflicting AES numbers, so none of it is used. The benchmark page URL is a CVS snapshot zip; the data is in beecrypt/beecrypt/BENCHMARKS,v (revision 1.17 of 2003-01-28 and earlier). Source headers say LGPL 2.1 or later; the SourceForge project page lists LGPLv2. Unmaintained: last CVS change 2015-12-28, last file release 4.2.1 (SourceForge 'last update' 2013-04-23).

LGPL copyleft. C library with assembler routines for several CPUs (NEWS mentions x86 and PowerPC; gas and masm directories in the tree) plus C++ and Java glue. Primitive set in the CVS tree is older: MD5, SHA-1/2, RIPEMD, Blowfish, AES in ECB/CBC, RSA, DSA, ElGamal, Diffie-Hellman; no GCM, ChaCha20, Poly1305 or Curve25519 sources in the file listing. Project website beecrypt.sourceforge.net is a placeholder page; source lives at sourceforge.net/projects/beecrypt.

## Maintenance

Abandoned (last CVS commit 2015-12-28, SourceForge last update 2013-04-23) but LGPL-2.1-or-later and buildable as a shared library; usable for legacy code and study, not recommended for new security work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The CVS snapshot's BENCHMARKS,v revision 1.17 (2003-01-28), reconstructed from the RCS file, holds the BeeCrypt-vs-Java modular exponentiation table and every number and quote in claimed_speedup matches it; it is first-party, gives compilers and machines but no flags, and the Java timing harness is not in the tree, so it is C.
- **Verifier notes:** Numbers verified by rebuilding BENCHMARKS revision 1.17 from the RCS file in the CVS snapshot: PIII 600/Win2000 4.3 vs 10.2 and 19.7 sec, PIII 450/Solaris 8 5.9 vs 17.1 sec, UltraSparc I 143/Solaris 8 40.7 vs 83.4 sec, and the 'twice to four times faster' quote all match. Shortcomings: baseline is 1999-2002 Java BigInteger, not OpenSSL or any C/C++ incumbent; first-party, flags unstated, Java harness not public, most Java and BeeCrypt rows on different machines; abandoned since 2015. Licence LGPL-2.1-or-later per source headers (SourceForge page says LGPLv2); 161 weekly downloads and 2 reviews (5.0) confirmed.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** CVS BENCHMARKS file (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip>
  - <https://sourceforge.net/projects/beecrypt/>
  - <https://beecrypt.sourceforge.net/>
- **Sources the enricher read:**
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip>
  - https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/BENCHMARKS,v (revisions 1.17 and 1.35 rebuilt from RCS)
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/README,v>
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/NEWS,v>
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/BUGS,v>
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/configure.ac,v>
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/mpbarrett.c,v>
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/include/beecrypt/mpbarrett.h,v>
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/rsa.c,v>
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/fips186.c,v>
  - https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/Attic/beetest.c,v (revision 1.12)
  - https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/tests/beetest.c,v (revisions 1.3 and 1.6)
  - <https://sourceforge.net/code-snapshots/cvs/b/be/beecrypt.zip#beecrypt/beecrypt/tests/benchme.c,v>
  - <https://sourceforge.net/projects/beecrypt/>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://beecrypt.sourceforge.net`) · [data/wave7/enrich/raw/beecrypt_sourceforge_net.json](../../../data/wave7/enrich/raw/beecrypt_sourceforge_net.json) (enrichment confidence 0.6)

</details>
