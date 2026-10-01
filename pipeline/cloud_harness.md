CLOUD HARNESS OVERRIDE (this replaces the "ORCHESTRATOR HARNESS NOTES" tool lines in your prompt file; everything else in the prompt file stands)

This run is in a locked-down cloud container. What works and what does not:
- WORKS: WebSearch (load with ToolSearch "select:WebSearch,WebFetch"). It is the main discovery tool now; budget is shared by ~14 agents, so make each query count. If it reports exhausted, continue with WebFetch-only sources below.
- WORKS: WebFetch on github.com repo pages (https://github.com/OWNER/REPO gives license, stars, description; https://github.com/OWNER/REPO/commits gives last commit date; https://github.com/OWNER/REPO/blob/BRANCH/PATH for files). WebFetch on a github.com page counts as opening it.
- WORKS: curl https://raw.githubusercontent.com/OWNER/REPO/HEAD/PATH (READMEs, bench files) — save into your scratch dir by absolute path.
- BLOCKED in the 2026-10-01 session (egress policy, EGRESS_BLOCKED): arxiv.org, hn.algolia.com, api.semanticscholar.org, *.github.io, dl.acm.org, ieeexplore, doi.org, sciencedirect, springer, readthedocs and most blogs/project sites. Try one fetch; if it says EGRESS_BLOCKED, do not retry that host. Use WebSearch snippets to learn what a blocked page says, and say so in your notes.
- WebSearch: subagents share a budget that ran out (200/200) when ~28 agents ran at once; try it, and if it reports exhausted, switch to github.com/topics/<topic>?l=c%2B%2B pages and repo READMEs.
- WORKS: github.com pages (WebFetch), raw.githubusercontent.com (curl), gitlab.com, pypi.org.
- DOES NOT WORK: the `gh` CLI (search and api are blocked for other repos), api.github.com, github.com/search, export.arxiv.org API, crossref, dblp, curl to any host except raw.githubusercontent.com and package registries (pypi.org). Do not retry these.
- Move on after 2 failed fetches of the same resource. Draft your output file early (a valid JSON array) and update it as you go.

Privacy and file rules:
- Never send the user's email, name or other personal identifiers to any outside service (URLs, headers, payloads). Do not build headers from `git config`. If an API wants a User-Agent, use exactly: User-Agent: fastpp-research-bot/1.0
- Write nothing in the repository except your named output file. Before fetching anything to disk, run `mkdir -p` on your own scratch directory (given below) and save every file there by ABSOLUTE path. Never write a relative path like readme.md.
- Never disable the sandbox. Do not call any mcp__hearthbot__ tools. Do not use mcp__github__ tools: this session's GitHub access is scoped to the project's own repository, so searching other repositories through them is out of bounds; discover via WebSearch and github.com/topics pages instead.

Output path: the repository root is /home/user/fastpp. Searches write /home/user/fastpp/data/waveN/raw/<ASSIGNMENT_ID>.json (this replaces any /Users/... or /home/claude/... path in the prompt file); verifiers and enrichers write the path their prompt names, rewritten under /home/user/fastpp if it points elsewhere. Check it parses with python3 json.load.

Final reply to the orchestrator: caveman ultra style (fragments, no articles, no filler, no arrows, no invented abbreviations; names, numbers and errors exact), max ~8 lines: entry count and names, plus any blocker. The JSON file itself stays normal prose.
