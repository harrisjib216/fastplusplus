# AVR-AES-faster (rgrgrg)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `AVR assembly (.S files) with C/C++ wrappers` · `MPL-2.0` · 🔴 abandoned

> Constant-time AES-128/192/256 block functions in AVR assembly, about 2,100 cycles per AES-128 block on ATmega328P.

| | |
|---|---|
| **Beats** | AVRAES (point-at-infinity.org, rijndaelfast.asm), Osvik et al. 'Fast Software AES Encryption', AVR CryptoLib, AVR-Crypto-Lib, the tiny version of uclouvain lightweight cipher code, and any pure C/C++ implementation |
| **Claimed result** | README says 'Seems to be faster than' the five listed AVR AES libraries and 'Any pure C/C++ implementation' (no competitor numbers on the page). Own table: AES-128 encrypt 2111 cycles (S-box in flash) or 1951 (S-box in RAM), decrypt 2687 / 2527, key expansion 748 / 708; tiny version (keys on the fly) 2949 encrypt, 3538 decrypt. |
| **Workload** | AES-128/192/256 block encryption, decryption and key expansion on 8-bit AVR, cycle counts for the inline (no call overhead) assembly version |
| **Metric** | throughput |
| **Hardware** | 8-bit AVR, Arduino Uno (ATmega328P) test sketch; cycles counted with Timer1 under AES_BENCHMARK in AVR-AES-Faster.ino |
| **Adoption** | 7 stars |
| **Last commit** | 2020-12-18 |
| **Links** | [repository](https://github.com/rgrgrg/AVR-AES-faster) · [benchmark](https://github.com/rgrgrg/AVR-AES-faster) |

## Verdict

The author's own Timer1 cycle counts on an Arduino Uno (ATmega328P) for the inlined core with no call overhead, per 16-byte block: AES-128 encryption 2,111 (flash S-box) / 1,951 (RAM S-box), decryption 2,687 / 2,527, key expansion 748 / 708; the repo never times any competitor, and its bundled C implementation is used only to check key expansion. Cross-source, derived from page data with different harnesses: rweather's C++ Arduino Crypto library lists AES128 on a 16 MHz Uno at 33.28 us/byte encryption and 63.18 us/byte decryption (about 8,520 and 16,174 cycles per block), so this library is about 3.8x and 5.7x faster even with its 140-cycle ABI overhead; against Osvik et al.'s 124.6 and 181.3 cycles/byte (search snippet only, about 1,994 and 2,901 cycles per block) it is about 6% slower at encryption with the flash S-box, 2% faster with the RAM S-box, and 7-13% faster at decryption, so 'faster than' the paper holds only for decryption and the RAM variant.

## Use it when

- AES-128/192/256 on classic 8-bit AVR (ATmega328P class) where cycles per block matter: the author's counts are 2,111 cycles to encrypt an AES-128 block with the S-box in flash and 1,951 with it in RAM, plus about 140 cycles of C ABI overhead.
- Flash-constrained builds: the RAM variant totals 1,236 bytes of flash for AES-128 encrypt, decrypt and key expansion (688 bytes of RAM), the Flash variant 1,610 bytes.
- RAM-starved parts that still need AES-128: the Tiny variant needs only the 16-byte key buffer (2,949 cycles to encrypt, 3,538 to decrypt) at the cost of rolling the key back after each block.
- Code that needs timing independent of key and data on AVR: there are no secret-indexed branches with unequal cycle counts and the table lookups take fixed time on these cacheless cores.

## Skip it when

- Threats that include power or EM side-channel analysis: 'constant-time' covers timing only; the code has no masking or shuffling, and the xtime steps still branch on secret bits (balanced in cycles, not in instruction stream).
- If you need a mode of operation (CTR, CBC, GCM, CCM) or AEAD out of the box: only single-block ECB primitives are provided, so a C++ library such as rweather's Arduino Crypto is easier to integrate, though about 4x slower per its own figures.
- AVR parts with more than 64 KB of flash (ATmega1280/2560) unless you control placement: the flash tables sit in ordinary .text.AES_SBox_F/.text.AES_InvSBox_F sections and are read with plain lpm through Z, with no ELPM/RAMPZ handling, so they must be linked into the first 64 KB.
- Reduced-core ATtiny (4/5/9/10/20/40) or pre-MOVW AVR cores: the code uses all of r0-r15, movw and lpm Rd,Z.
- Projects that need maintenance or wider test coverage: last commit 2020-12-18, self-tests use only the four FIPS-197 Appendix B/C vectors (the 'test against more vectors' TODO is open), and the 'Nano' variant is unfinished.

## How it is fast

The whole 16-byte state lives in registers r0-r15 for all rounds, SubBytes and ShiftRows are fused into one pass of table lookups through Z (zh fixed to the 256-byte-aligned table, zl set to the state byte: 3-cycle lpm from flash or 2-cycle ld from RAM), and MixColumns uses the shared t = a0^a1^a2^a3 formulation with three xtime doublings per column. Decryption uses the straight Inverse Cipher rather than the Equivalent Inverse Cipher, so the same expanded key serves both directions with no InvMixColumns pass over the round keys.

## Compared with alternatives

Pick it when the target is 8-bit AVR: the closest catalogued AES sibling, aadomn/aes (fixsliced constant-time AES), covers only Cortex-M and RV32I, and the other assembly entries target x86, Arm or Go, so none of them runs on an ATmega.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (avr-libc headers only for the optional AES_BENCHMARK timing hooks) |
| **Minimum toolchain** | avr-gcc with GNU as and the C preprocessor for .S files (exact version not documented); the test sketch builds in the Arduino IDE |
| **Platforms** | 8-bit AVR enhanced cores with MOVW and LPM Rd,Z (tested on Arduino Uno, ATmega328P); flash tables must sit in the low 64 KB |
| **Thread safety** | not documented; functions keep state in registers and caller buffers, so separate keys and blocks are reentrant, but the Tiny functions mutate the caller's key buffer and the RAM tables are shared globals |
| **Drop-in for the baseline** | no |

## Gotchas

- The functions use r0 and r1 (avr-gcc's __zero_reg__) as state bytes and clear r1 only on return; ordinary avr-gcc ISRs re-zero r1 in their prologue, but a naked or hand-written assembly ISR that assumes r1 == 0 will misbehave if it fires mid-block.
- RAM tables must be 256-byte aligned (`ldi zh, hi8(table)` then `mov zl, byte`): the README's example defines `uint8_t AES_SBox_R[256];` without the attribute, which only works because the header's extern declaration carries aligned(256), so define the tables in a translation unit that includes AVR-AES-Faster.h.
- The README's Flash example expands the key into `xtest` but encrypts with `xkey`; copied literally it encrypts with uninitialised round keys. The Tiny functions leave the key buffer as the last (or first) round key, so each block needs a 16-byte copy or a roll-back call (405 or 423 cycles per the README table).
- Published cycle counts exclude the call: they time only the inlined core with arguments already in registers (Timer1 at CLK/1 with interrupts disabled, eight cycles of probe overhead subtracted); add about 140 cycles per block through the C ABI. AES-256 key expansion goes through the generic AES_ExpandKey_F (2,044 cycles against 748 for the dedicated 128-bit routine).

## Known shortcomings

- "Seems faster" claims with no competitor numbers; against the snippet-derived Osvik FSE 2010 figure (about 1994 cycles/block) the flash encrypt (2111) is slower and the RAM variant (1951) about 2% faster. Abandoned 2020-12-18.
- No timing or correctness bug found: the Timer1 harness is sound (cli, CLK/1, overflow check) and the xtime branches take the same cycles on both paths, so timing is constant. Main shortcoming: no competitor is ever timed. Cross-source (derived from page data): rweather's Crypto C++ docs give 33.28/63.18 us per byte on a 16 MHz Uno, about 8,520/16,174 cycles per block, so this library is about 3.8x/5.7x faster including the 140-cycle ABI cost; against Osvik (snippet only) the flash-S-box encrypt is 6% slower and decrypt 7-13% faster. Flash tables are read with plain lpm in .text with no ELPM, so they must sit in the first 64 KB on ATmega2560-class parts; r0/r1 hold state, which breaks naked ISRs; the README Flash example expands the key into xtest but encrypts with xkey.

## Caveats and trade-offs

The faster-than claims against named libraries carry no numbers on the page, and the bundled pure C implementation (TestAES.cpp) is used only as a key-expansion self-check, never timed. Cycle counts are for the inlined assembly with no rcall/ret; the README says the C ABI adds about 140 cycles per block on the callee side. Search snippet only: Osvik, Bos, Stefan and Canright (FSE 2010) report 124.6 and 181.3 cycles per byte on AVR, about 1994 and 2901 cycles per block (derived), so this library's flash-S-box AES-128 encryption at 2111 cycles is slower than that paper's figure and the RAM-S-box 1951 cycles only about 2% faster, while decryption (2527 to 2687 cycles) is faster; whether the paper's counts include call overhead or key handling could not be checked. Baseline libraries are other AVR assembly, not compiler output. Constant-time claim relies on AVR having no data cache (table lookups in flash or RAM).

Constant-time; 512 bytes of S-box tables (flash) or 688 bytes RAM in the RAM variant; tiny variant needs only 16 bytes RAM but overwrites the key in place and must roll it back; C ABI call adds about 140 cycles per block.

## Maintenance

Abandoned single-author project (23 commits between 2020-12-09 and 2020-12-18, 7 stars, no issues filed), MPL-2.0 per file, so modified .S files must stay open; small enough to vendor, but the speed claims against other AVR AES libraries remain unbenchmarked.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README lists only the project's own cycle counts (all match the record) and says it 'seems to be faster than' five AVR AES libraries and any pure C/C++ implementation without any competitor numbers. Public cycle-counting code exists (Timer1 measurements under AES_BENCHMARK in AVR-AES-Faster.ino plus AES_benchmark.S), but it times only this library; toolchain and flags are not stated.
- **Verifier notes:** Numbers match the README; tier C confirmed. Main shortcoming: no competitor numbers anywhere in the repo, and a snippet-derived check against Osvik et al. suggests encryption is not faster with the flash S-box. 7 stars, MPL-2.0, last commit 2020-12-18 (abandoned).
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-69 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/rgrgrg/AVR-AES-faster>
  - <https://github.com/rgrgrg/AVR-AES-faster/commits>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/README.md>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_benchmark.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AVR-AES-Faster.ino>
- **Sources the enricher read:**
  - <https://github.com/rgrgrg/AVR-AES-faster>
  - <https://github.com/rgrgrg/AVR-AES-faster/commits/main>
  - <https://github.com/rgrgrg/AVR-AES-faster/tree/main/pure_asm>
  - <https://github.com/rgrgrg/AVR-AES-faster/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/README.md>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AVR-AES-Faster.h>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AVR-AES-Faster-devel.h>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AVR-AES-Faster.ino>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_benchmark.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_Encrypt_F.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_Decrypt_F.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_Encrypt128_T.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_Decrypt128_T.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_ExpandKey_F.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_ExpandKey128_F.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_SBox_F.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_InitSBox_R.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/AES_InitInvBox_N.S>
  - <https://raw.githubusercontent.com/rgrgrg/AVR-AES-faster/HEAD/TestAES.h>
  - <https://raw.githubusercontent.com/rweather/arduinolibs/master/doc/crypto.dox>
  - <https://github.com/kildom/AVR-AES>
  - <https://raw.githubusercontent.com/kildom/AVR-AES/HEAD/README.md>
  - <https://github.com/Churro/avr-aes128-groestl256>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/rgrgrg/avr-aes-faster`) · [data/wave13/enrich/raw/github_com_rgrgrg_avr_aes_faster.json](../../../data/wave13/enrich/raw/github_com_rgrgrg_avr_aes_faster.json) (enrichment confidence 0.75)

</details>
