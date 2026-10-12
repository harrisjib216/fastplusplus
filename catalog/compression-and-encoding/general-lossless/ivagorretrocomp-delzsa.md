# DeLZSA (ivagorRetrocomp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Assembly (i8080, PDP-11)` · `no license` · ⚪ unknown

> Intel 8080 and PDP-11 assembly decompressors for the LZSA1/LZSA2 formats; code no longer publicly reachable, no speed figures.

| | |
|---|---|
| **Beats** | LZSA reference decompressor (emmanuel-marty/lzsa) |
| **Claimed result** | none found (no numbers seen) |
| **Workload** | No benchmark found: decompressing LZSA1/LZSA2 streams on Intel 8080 and PDP-11 processors. |
| **Metric** | throughput |
| **Adoption** | Listed under 'External links' in the emmanuel-marty/lzsa README (261 stars) as 'i8080 and PDP-11 decompressors by Ivan Gorodetsky' |
| **Links** | [repository](https://github.com/ivagorRetrocomp/DeLZSA) |

## Verdict

No benchmark exists: nothing was measured for DeLZSA against the LZSA reference decompressor or anything else, and the code cannot be inspected. The record is kept at tier D as a pointer from the LZSA README's External links.

## Use it when

- You are writing software for an Intel 8080 or KR580-class machine, or a PDP-11 family machine, want LZSA-packed assets, and can obtain a copy of Gorodetsky's routines from another source.
- You want a reference for porting the LZSA2 nibble-and-token decoder to a CPU without an existing LZSA routine and the code turns up again.
- Retro or demoscene projects where packed size matters more than decode speed (LZSA2 compresses about as well as ZX7 on the LZSA README corpus).

## Skip it when

- Any modern-CPU workload: this is retro-CPU assembly; use the LZSA C decompressor, LZ4 or zstd instead.
- Anything that needs code you can vendor today: the GitHub repo, the owner account and the GitLab predecessor are all gone, so there is nothing to copy and no license.
- Z80, 6502, 65816, 6809, 8088 or x86 targets: the LZSA repo ships its own size- and speed-optimized decoders for those.
- When you need a measured speed or size figure for the 8080 or PDP-11 routine: none was ever seen.

## How it is fast

Not documented: no source or README could be read. Any speed comes from the LZSA format itself, which is byte-aligned and avoids 16-bit arithmetic on 8-bit CPUs; the LZSA README puts LZSA1 at about 90% and LZSA2 at about 75% of LZ4 decompression speed on 8-bit systems (ZX7 at 47.73%), measured on its own Z80/6502 decoders, not on DeLZSA.

## Compared with alternatives

Only when the target is an 8080 or PDP-11 and you can find the routines elsewhere; for every other CPU use the decoders shipped in LZSA itself, and on modern machines LZ4 or lz4ultra give faster decoding with maintained code.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none known (assembly routines; code not reachable) |
| **Minimum toolchain** | not documented (an 8080 or PDP-11 assembler; dialect unknown) |
| **Platforms** | Intel 8080 and PDP-11 per the LZSA README link text; nothing else documented |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Dead link: github.com/ivagorRetrocomp/DeLZSA, github.com/ivagorRetrocomp and raw.githubusercontent.com README paths (HEAD, main, master) all return 404; the 2019 GitLab home gitlab.com/ivagor/lzsa8080 returns '404 Project Not Found' and GitLab has no user named ivagor.
- The listed baseline is not comparable: the LZSA reference decompressor is portable C for modern machines, while DeLZSA targets 8080 and PDP-11, so 'faster than baseline' has no defined meaning here.
- The only nearby numbers are LZSA format figures from the LZSA README (LZSA1 90%, LZSA2 75% of LZ4 decode speed on a ZX Spectrum and C64 file set), measured with other people's Z80/6502 decoders; that README's text also says LZSA1 decompresses 'faster than LZ4 on 8-bit systems' while its own table shows 90% of LZ4_HC -19 -B4 -BD.

## Known shortcomings

- Repository and owner page return 404, as does the 2019 predecessor gitlab.com/ivagor/lzsa8080; only the emmanuel-marty/lzsa README link and search snippets remain. No code, no numbers, no licence; kept at D under the keep-and-document rule (private-repo precedent) with has_code false.
- Enricher: repo, owner page and raw README 404 on every branch, the GitLab predecessor ivagor/lzsa8080 is gone, and no mirror was found in 3 searches; confidence 0.3. Side note: the LZSA README says LZSA1 decodes 'faster than LZ4' while its own table shows 90% of LZ4_HC.

## Caveats and trade-offs

The repo no longer exists publicly: on 2026-10-07 github.com/ivagorRetrocomp/DeLZSA and the owner page github.com/ivagorRetrocomp return HTTP 404, and the searcher's raw.githubusercontent.com README fetches also returned 404 (deleted, renamed or made private). The emmanuel-marty/lzsa README still links it under External links as 'i8080 and PDP-11 decompressors by Ivan Gorodetsky'; the original 2019 link (LZSA commit 16ac8c7, 'Add link to PDP-11 depackers by Ivan Gorodetsky') pointed to gitlab.com/ivagor/lzsa8080 and its PDP11 subfolder, which the GitLab API now reports as '404 Project Not Found'. The GitHub account ivagor exists but has no public repositories. No README, license, speed table or size table was seen, so tier D, license unknown (usability reference), has_code false because no code is reachable, last commit unknown. DeLZSA is not an alternative to the LZSA reference decompressor in the usual sense: the reference decompressor is a C program for modern machines, while DeLZSA ports the format to 8080 and PDP-11 assembly, so a throughput win over that baseline is not a well-defined comparison. The only speed figures near this topic are from the LZSA README (LZSA1 about 90% of LZ4 decompression speed, LZSA2 about 75%, on 8-bit systems), which concern the format, not DeLZSA. Not notable by stars; kept as the orchestrator's seed record only.

Targets 8-bit and 16-bit retro CPUs (Intel 8080, PDP-11), not modern machines. Decompresses the LZSA formats only (LZSA1 designed to replace LZ4, LZSA2 to replace ZX7 on 8-bit systems).

## Maintenance

Gone: repo, owner account and GitLab predecessor are all 404 (last seen linked from the LZSA README, whose last change was 2023-02-13), license unknown, so it is reference-only with nothing to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** No numbers anywhere: the repo returns HTTP 404 (repo page and owner page), its 2019 predecessor gitlab.com/ivagor/lzsa8080 is also gone (GitLab API: 404 Project Not Found), and the LZSA README only links to it without figures.
- **Verifier notes:** Record is accurate; kept at D per the keep-and-document rule even though the prompt's 'repo does not exist' and 'tier D and not notable' reject criteria both apply (the code existed and is linked from the LZSA README, so the evidence is missing, not fabricated). Shortcomings to record: repo and its GitLab predecessor both gone, no numbers, no license, baseline comparison not meaningful (8-bit assembly ports vs a modern C decompressor). The orchestrator may prefer to drop it from the lists given there is nothing to copy.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** a reachable repository with any speed numbers; a reachable repository
- **Pages the verifier opened:**
  - <https://github.com/ivagorRetrocomp/DeLZSA>
  - <https://github.com/ivagorRetrocomp>
  - <https://github.com/ivagor>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/README.md>
  - <https://github.com/emmanuel-marty/lzsa/commits/master/README.md>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/16ac8c7/README.md>
  - <https://gitlab.com/ivagor/lzsa8080>
  - <https://gitlab.com/api/v4/projects/ivagor%2Flzsa8080>
- **Sources the enricher read:**
  - <https://github.com/ivagorRetrocomp/DeLZSA>
  - <https://raw.githubusercontent.com/ivagorRetrocomp/DeLZSA/main/README.md>
  - <https://raw.githubusercontent.com/ivagorRetrocomp/DeLZSA/master/README.md>
  - <https://raw.githubusercontent.com/ivagorRetrocomp/DeLZSA/HEAD/README.md>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/README.md>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/16ac8c7/README.md>
  - <https://github.com/emmanuel-marty/lzsa/tree/master/asm>
  - <https://github.com/emmanuel-marty/lzsa/commits/master/README.md>
  - <https://gitlab.com/api/v4/users?username=ivagor>
  - <https://gitlab.com/api/v4/projects/ivagor%2Flzsa8080>
  - <https://gitlab.com/api/v4/projects?search=lzsa8080>
  - WebSearch: DeLZSA i8080 PDP-11 LZSA decompressor Gorodetsky (no mirror found)
  - WebSearch: "ivagorRetrocomp" github (no results for the account)
  - WebSearch: LZSA PDP-11 depacker BK-0010 OR UKNC OR Vector-06C Gorodetsky github asm (no copy found)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ivagorretrocomp/delzsa`) · [data/wave9/enrich/raw/github_com_ivagorretrocomp_delzsa.json](../../../data/wave9/enrich/raw/github_com_ivagorretrocomp_delzsa.json) (enrichment confidence 0.3)

</details>
