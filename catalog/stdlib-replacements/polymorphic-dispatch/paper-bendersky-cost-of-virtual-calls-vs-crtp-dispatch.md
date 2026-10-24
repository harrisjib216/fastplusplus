# Static CRTP dispatch versus virtual calls (Eli Bendersky benchmark)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Polymorphic dispatch](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔵 finished

> 2013 blog benchmark: CRTP static dispatch runs a trivial-method call loop about 6x faster than virtual calls.

| | |
|---|---|
| **Beats** | virtual function call through a base-class pointer (run_dynamic version of the same loop) |
| **Claimed result** | run_dynamic 1.25 s versus run_crtp 0.21 s on an Intel i7-4771, about 6x faster (derived); the author reportedly expected about 2x. Snippet only: figures come from web-search result summaries of the post, which also cite a Hacker News comment quoting 1.25 s for the dynamic version (about 8e8 virtual calls, 1.5 ns per call). |
| **Workload** | Synthetic O(N^2) loop that calls a trivial 'tick' method on objects, once through a virtual call on a base pointer and once through CRTP static dispatch; wall-clock run time of the whole loop. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-4771 (from search-result snippet) |
| **Adoption** | Widely cited blog post (2013-12-05); also cited by the book as the source for the dispatch-cost gap |
| **Links** | [repository](https://eli.thegreenplace.net/2013/12/05/the-cost-of-dynamic-virtual-calls-vs-static-crtp-dispatch-in-c) · [benchmark](https://eli.thegreenplace.net/2013/12/05/the-cost-of-dynamic-virtual-calls-vs-static-crtp-dispatch-in-c) |

## Verdict

Reported, not re-verified: a nested loop of trivial tick calls took about 1.25 s through a virtual call on a base pointer and about 0.21 s through CRTP on an Intel Core i7-4771, about 6x (derived), with compiler and flags unknown. An HN commenter in the post's repost thread (item 9123571) independently quotes the 6x figure and a 1.5x reversal when the static method is not inlined, both seen as search snippets only.

## Use it when

- Hot inner loops that call very small methods (accessors, counters, per-element kernels) where the concrete type is fixed at compile time
- Static interfaces and mixins in template libraries, where runtime substitution of implementations is never needed
- Code paths that hold objects in per-type (homogeneous) containers rather than containers of base pointers
- As a quick reference when arguing whether virtual-call overhead matters in a given loop; re-measure on your own compiler before acting on it

## Skip it when

- Heterogeneous collections, plug-ins or types chosen at runtime: CRTP gives no runtime polymorphism
- Methods that do substantial work per call: an HN commenter (snippet only) reports practically no difference between CRTP and virtual functions in a raytracer with heavy calls
- When the CRTP call cannot be inlined (across a library boundary or with noinline): the reported advantage disappears and the static version was reported slower
- When code size or compile time matters: every derived type instantiates its own copy of the templated code
- When the compiler can already devirtualize (final classes, whole-program or profile-guided optimisation), which commenters note may shrink the 6x gap

## How it is fast

CRTP binds the call at compile time, so there is no vtable load or indirect call, and the compiler can inline the tiny method body into the loop and optimise the loop as a whole. Search snippets of the post and of a Hacker News discussion indicate the gap is mostly inlining: one commenter (npalli, in the HN repost thread news.ycombinator.com/item?id=9123571) reports the virtual version about 6x slower than the inlined static one, and the static version about 1.5x slower than the virtual one once inlining is disabled.

## Compared with alternatives

The Hands-On Design Patterns chapter 8 sibling reports a similar gap (9.04 ns versus 1.55 ns per 32 calls, about 5.8x) and ships in a publisher repository, so prefer it when you want runnable, licensed example code; read Bendersky's post for the widely cited original argument and its inlining analysis. For replacing dynamic_cast type tests rather than virtual calls, the chapter 1 sibling is the relevant entry.

## Integration

| | |
|---|---|
| **Form** | source-drop (language idiom; example code inline in the blog post) |
| **Dependencies** | none |
| **Minimum toolchain** | any C++ compiler with class templates (C++98); the post's own compiler and flags were not seen |
| **Platforms** | any |
| **Thread safety** | not applicable (dispatch idiom, no shared state) |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline figures (1.25 s virtual versus 0.21 s CRTP on an Intel i7-4771) come only from web-search summaries seen by the search agent; the post, its isocpp.org mirror and HN mirrors are unreachable here (getaddrinfo ENOTFOUND), and the verifier and this enrichment found no snippet carrying those exact numbers. Independent HN snippets corroborate only the roughly 6x ratio.
- One trivial method in a tight loop is the best case for CRTP: the measured gap is mostly lost inlining, not the cost of the indirect call itself, and reportedly reverses when the static call is not inlined.
- 2013-era compiler and CPU; the post itself warns that benchmarks, including its own, should be taken with a large grain of salt.
- CRTP relies on the derived class naming itself as the template argument; passing the wrong type still compiles and the base's static_cast then targets the wrong class.

## Known shortcomings

- Numbers unverified: eli.thegreenplace.net and its mirrors were unreachable from the cloud session and no search snippet shows the 1.25 s / 0.21 s / i7-4771 figures, so they rest on the search agent's reading. Kept at C per the ccan precedent; D if strict.
- Enricher: post still unreachable; an HN snippet backs only the about 6x ratio and reports the CRTP version 1.5x slower than virtual with inlining disabled, so the gap is inlining; code not in eliben/code-for-blog.

## Caveats and trade-offs

Snippet only: eli.thegreenplace.net is blocked from this environment (getaddrinfo ENOTFOUND), so the page was never opened; the numbers and CPU come from WebSearch result summaries seen by the search agent (two searches agreeing on 1.25 s for the dynamic run, one giving 0.21 s for CRTP), and compiler and flags were not seen (null). The verifier could not re-confirm them: eli.thegreenplace.net, the isocpp.org mirror and an HN mirror all failed with getaddrinfo ENOTFOUND, and five further searches returned the post's topic, date and its warning that benchmarks, 'including the one posted here', should be taken with a large grain of salt, but no timing figures. The code is inline in the article; the eliben/code-for-blog 2013 directory has no matching file (its listing shows only two JavaScript inheritance files and two Twisted IRC files), so no repo carries it and no license was seen (usability reference). One trivial method in a tight loop: the large gap is mostly inlining (a secondary source says so), the worst case for virtual calls; a real gap depends on method size and cache behaviour. 2013-era CPU and compiler. Tier C: single first-party blog measurement, methodology not verified. [retier] Enricher: a search snippet of HN thread 9123571 backs only the about 6x ratio, and reports that with inlining disabled the static (CRTP) version runs 1.5x slower than the virtual one, so the gap is inlining, not dispatch cost as such. The code is not in eliben/code-for-blog for 2013.

CRTP binds the call at compile time so the compiler can inline it, but gives no runtime polymorphism: no heterogeneous containers of base pointers, no plug-ins, one template instantiation per type (code size, compile time). Virtual dispatch keeps a vptr per object and an indirect call.

## Maintenance

Finished 2013 reference post, still widely cited; the code is inline in the post with no license seen (the author's Unlicense code-for-blog repository has no copy in its 2013 folder), so treat it as reference reading rather than copyable code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Single first-party blog measurement of the same loop through virtual and CRTP dispatch; the post (and its isocpp.org mirror) is blocked here and five verifier searches confirmed the post, its December 2013 date and its benchmark method but returned no snippet with the 1.25 s / 0.21 s figures or the i7-4771, so the numbers rest on the search agent's snippet summaries. No compiler, flags or repo-hosted code were seen, so it cannot reach A or B.
- **Verifier notes:** Widely cited post (mirrored on isocpp.org); kept at C on the same basis as other blocked first-party blog posts, but its numbers were seen only by the search agent, so treat claimed_speedup as unverified. A copy of the post or its code in a reachable repo would settle it.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/eliben/code-for-blog/tree/main/2013>
- **Sources the enricher read:**
  - <https://github.com/eliben/code-for-blog/tree/main/2013>
  - <https://github.com/eliben?tab=repositories&q=blog>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:bendersky-cost-of-virtual-calls-vs-crtp-dispatch`) · [data/wave1/enrich/raw/paper_bendersky_cost_of_virtual_calls_vs_crtp_dispatch.json](../../../data/wave1/enrich/raw/paper_bendersky_cost_of_virtual_calls_vs_crtp_dispatch.json) (enrichment confidence 0.45)

</details>
