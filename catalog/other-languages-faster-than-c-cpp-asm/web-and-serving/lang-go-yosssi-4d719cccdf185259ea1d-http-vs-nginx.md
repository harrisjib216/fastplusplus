# Go net/http vs nginx on localhost (yosssi gist)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Go` · `no license` · 🔴 abandoned

> 2014 loopback wrk transcript: a Go net/http empty handler beats nginx 1.96x, but no row shows Go serving the same file faster.

| | |
|---|---|
| **Beats** | nginx (C); version and configuration not shown |
| **Claimed result** | nginx 31,780.82 req/s (avg latency 7.71 ms) vs a Go empty handler at GOMAXPROCS=2 62,314.54 req/s (not like-for-like). The cached file-server rows (io.Copy 59,517.07 req/s, ServeContent) are invalid: yosssi/go-fileserver's cache is always empty and those rows return 116-183 bytes per response, the same as the empty handler, while nginx (294.0 bytes) and http.FileServer (242.8) carry the file body. The only valid file row is Go http.FileServer 16,088 vs nginx 31,781 req/s (0.51x, derived from page data): not faster. |
| **Workload** | wrk -t12 -c400 -d2s against 127.0.0.1 for nginx and for Go net/http servers (empty handler, 'Hello' handler and three static-file variants). |
| **Metric** | throughput |
| **Hardware** | Not stated; a 'mac:\~' shell prompt and a /Users/... directory in the file-server code indicate a Mac; CPU model not given |
| **Compiler and flags** | Go servers started with GOMAXPROCS=2 go run main.go (Go version not stated); nginx build, version and configuration not shown |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Last commit** | 2014-06-23 |
| **Links** | [repository](https://gist.github.com/yosssi/4d719cccdf185259ea1d) · [benchmark](https://gist.github.com/yosssi/4d719cccdf185259ea1d) |

## Verdict

On an unspecified 2014 Mac over loopback (wrk -t12 -c400 -d2s), nginx (unknown version and config) served about 31,781 req/s of a small file; Go net/http with GOMAXPROCS=2 reached 62,315 req/s with an empty handler that sends no file (1.96x, derived), 16,088 req/s with http.FileServer (0.51x, derived), and 59,517 and 25,581 req/s for the two go-fileserver cache variants, which this check finds returned empty bodies, so no measured row shows Go serving the same content faster than nginx.

## Use it when

- As a historical anecdote that Go's net/http could already answer about 60k empty requests per second on two cores of a 2014 Mac over loopback.
- As a worked example for auditing server benchmarks: divide Transfer/sec by Requests/sec and check every row returns the same bytes before comparing throughput.
- Not as a basis for picking Go over nginx for static files or proxying; use a current, configured comparison instead.

## Skip it when

- Static file serving: the only valid file-serving row, Go http.FileServer at 16,088 req/s, is about half of nginx's 31,781 req/s (0.51x, derived from page data).
- Do not use yosssi/go-fileserver: its cache stores an empty copy of every file (bug described in gotchas), and handlers write the shared cache map without a lock, which is a data race under concurrent requests.
- Any version- or tuning-sensitive decision: Go version, nginx version, nginx.conf (worker_processes, sendfile, keep-alive), served file and CPU are all unstated, and each run lasted 2 seconds with wrk on the same machine.
- Modern stacks: the code and numbers are from June 2014 and have not been rerun.

## How it is fast

The gist gives no explanation, and the fast Go rows do less work than nginx. Dividing each run's 'MB read' by its request count (derived from page data) gives 294 bytes per nginx response (a body of roughly 59 bytes plus nginx's headers) against 116 bytes for the Go empty handler, which is exactly a 2014 Go header-only 200 response; the Hello run comes out at 121 bytes, 5 more, which confirms the arithmetic. The two cached go-fileserver rows (59,517 and 25,581 req/s) are fast because they send no file at all (see gotchas).

## Compared with alternatives

Never as evidence: kawipiko (a Go static server) documents its NGINX config and measures matched Hello World serving, and the HttpArena entries (raw tokio, Kestrel, ioxide) compare against a known nginx 1.31.4 -O3 build doing the same endpoints. This gist is only a 2014 anecdote, and its one valid file-serving row favours nginx.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Go standard library net/http; the cached rows also import github.com/yosssi/go-fileserver (MIT, 7 commits, last commit 2014-06-24) |
| **Minimum toolchain** | Not stated; 2014-era Go, version not given in the gist |
| **Platforms** | macOS inferred from the 'mac:\~' shell prompt and /Users/... paths; the Go code itself is portable |
| **Thread safety** | net/http runs each connection in its own goroutine; go-fileserver reads and writes its cache map from those goroutines with no lock (data race) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw that invalidates the record's 'closest like-for-like' 1.87x row: go-fileserver (commits 3966915 'Add files' with io.Copy and 21d1e12 with http.ServeContent, both 2014-06-23, matching gist sections 6 and 5) serves a cache miss with http.ServeContent(w, r, ..., f), which reads f to EOF, and only then runs io.Copy(&buf, f) to fill the cache, so the cached data is always empty. Every later request gets an empty body: section 6 averages 116.1 bytes per response, the same as the empty handler's 116, and section 5 averages 183.1 bytes, exactly a header-only ServeContent reply with Content-Length: 0 and Content-Type text/html (derived from page data), while http.FileServer (242.8 bytes) and nginx (294.0 bytes) each sent a body of about 59 bytes. The current HEAD (73806fe, 2014-06-24) keeps the bug and also never stores the file size, so Content-Length stays 0.
- The gist's section 6 shows the same code as section 5 (commenter Azareal, 2016-12-03); the io.Copy version exists only in the go-fileserver history. Section 3's first run is a byte-for-byte copy of section 2's output; its second run (60,837.67 req/s) is the real Hello result.
- Effective concurrency differs: nginx and Go sections 2-4 report 'connect 155' socket errors (about 245 of 400 connections opened, consistent with a default 256 open-file limit on macOS, inference), while sections 5 and 6 report connect 0. nginx's worker count is unknown; the stock nginx.conf runs 1 worker against GOMAXPROCS=2 for Go.
- A commenter asked for the nginx version and configuration in 2018 and got no answer; the gist has no licence, so its code is reference only.

## Known shortcomings

- The headline 1.96x row is not like-for-like and 2 of 3 file-serving rows are slower; unequal connect errors (155 vs 0); sections 2 and 3 of the gist print identical output; nginx worker count unknown vs GOMAXPROCS=2; gist last updated 2014-06-23.
- Harness bug invalidates the 'like-for-like 1.87x' row: yosssi/go-fileserver (commits 3966915, 21d1e12, HEAD 73806fe) reads the file to EOF via http.ServeContent and then io.Copy fills the cache, so the cache is always empty; bytes per response (MB read over requests) are 116.1 for the io.Copy row, the same as the empty handler's 116, and 183.1 for the ServeContent row, a header-only reply with Content-Length 0, while nginx (294.0) and http.FileServer (242.8) each carry the about 59-byte body. The only valid file row is Go 16,088 vs nginx 31,781 req/s (0.51x). The cache map is written without locking (data race).

## Caveats and trade-offs

Weak, informal result from 2014 (all nine gist revisions are dated 2014-06-23; the page's 'Last active August 7, 2024' is not a content change). Runs last only 2 seconds, the load generator and servers share one machine (apparently a Mac), and Go and nginx versions, nginx configuration (including worker_processes; the stock nginx.conf sets 1 while Go ran with GOMAXPROCS=2) and the served content are not given. The nginx run and Go sections 2 to 4 all report 'connect 155' socket errors, so only about 245 of the 400 wrk connections were open, while the two go-fileserver runs report connect 0, so effective concurrency differs between rows. Section 2 (empty response) and the first run of section 3 (Hello) show byte-identical output (62,314.54 req/s, same socket errors), which looks like a pasted duplicate. The empty-handler and Hello rows do not serve files, so they are not like-for-like with nginx; of the three file-serving rows two are slower than nginx and the faster one serves from an in-memory cache. A commenter notes sections 5 and 6 show identical code, and another asked for the nginx version and configuration without an answer. Gist has no licence, so the code is reference only. Tier C: numbers without methodology. [retier] Harness bug: yosssi/go-fileserver reads the file to EOF via http.ServeContent and then io.Copy fills the cache, so the cache is always empty; bytes per response are 116.1 for the io.Copy row (same as the empty handler's 116) and 183.1 for the ServeContent row (header-only, Content-Length 0). The cache map is written without locking (data race).

Go runtime and GC; no TLS, keep-alive tuning or real file workload is exercised.

## Maintenance

Abandoned since 2014-06-23, no licence (reference only), and the evidence for the record's file-serving win is invalid (the cached server sent empty responses, as in the stb-zip and Pipa precedents), so the record should be rejected or at least moved to tier D with the claim corrected to 'Go slower than nginx on the only valid file-serving row'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** Informal first-party wrk transcript in a 2014 gist: nginx 31,780.82 req/s and the Go rows match the record, but nginx version, configuration and served content, Go version and CPU are all missing; numbers without methodology.
- **Retiered** C to D: Enricher: the gist's cached file-server rows never served the file (the cache stays empty and the io.Copy and ServeContent rows return 116-183 bytes per response, the same as an empty handler), so the 'like-for-like 1.87x' row is invalid, and the only valid file row has Go at 0.51x nginx. No valid like-for-like win (stb-zip-style wrong work, kept and documented): C to D.
- **Verifier notes:** Numbers verified on the gist page; dates corrected to the 2014-06-23 revisions (abandoned). Shortcomings: no versions, configs or CPU, 2-second runs on one Mac, unequal effective connection counts (connect 155 errors), duplicated output in two sections, headline 1.96x row is not like-for-like and two of three file-serving rows are slower than nginx; possible worker-count asymmetry. Raw gist (gist.githubusercontent.com) was blocked, so details come from the rendered gist page.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** verifier batch-95 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://gist.github.com/yosssi/4d719cccdf185259ea1d>
  - <https://gist.github.com/yosssi/4d719cccdf185259ea1d/revisions>
- **Sources the enricher read:**
  - <https://gist.github.com/yosssi/4d719cccdf185259ea1d>
  - <https://github.com/yosssi/go-fileserver>
  - <https://github.com/yosssi/go-fileserver/commits/master>
  - <https://raw.githubusercontent.com/yosssi/go-fileserver/HEAD/file_server.go>
  - <https://raw.githubusercontent.com/yosssi/go-fileserver/HEAD/file.go>
  - <https://raw.githubusercontent.com/yosssi/go-fileserver/HEAD/options.go>
  - <https://raw.githubusercontent.com/yosssi/go-fileserver/HEAD/consts.go>
  - <https://raw.githubusercontent.com/yosssi/go-fileserver/HEAD/README.md>
  - <https://raw.githubusercontent.com/yosssi/go-fileserver/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/yosssi/go-fileserver/3966915/file_server.go>
  - <https://raw.githubusercontent.com/yosssi/go-fileserver/21d1e12/file_server.go>
  - <https://raw.githubusercontent.com/yosssi/go-fileserver/73806fe/file_server.go>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:go/yosssi/4d719cccdf185259ea1d#http-vs-nginx`) · [data/wave14/enrich/raw/lang_go_yosssi_4d719cccdf185259ea1d_http_vs_nginx.json](../../../data/wave14/enrich/raw/lang_go_yosssi_4d719cccdf185259ea1d_http_vs_nginx.json) (enrichment confidence 0.8)

</details>
