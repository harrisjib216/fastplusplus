CLOUD HARNESS OVERRIDE (this replaces the "ORCHESTRATOR HARNESS NOTES" tool lines in your prompt file; everything else in the prompt file stands)

This run is in a locked-down cloud container. What works and what does not:
- WORKS: WebSearch (load with ToolSearch "select:WebSearch,WebFetch"). It is the main discovery tool now; budget is shared by ~14 agents, so make each query count. If it reports exhausted, continue with WebFetch-only sources below.
- WORKS: WebFetch on github.com repo pages (https://github.com/OWNER/REPO gives license, stars, description; https://github.com/OWNER/REPO/commits gives last commit date; https://github.com/OWNER/REPO/blob/BRANCH/PATH for files). WebFetch on a github.com page counts as opening it.
- WORKS: curl https://raw.githubusercontent.com/OWNER/REPO/HEAD/PATH (READMEs, bench files) — save into your scratch dir by absolute path.
- WORKS: WebFetch https://hn.algolia.com/api/v1/search?query=<terms>&tags=story ; WebFetch https://arxiv.org/abs/<id> and https://arxiv.org/html/<id> ; most blogs and project sites via WebFetch.
- SOMETIMES: WebFetch https://api.semanticscholar.org/graph/v1/paper/search?query=<terms>&fields=title,url,year,externalIds&limit=20 (rate-limited 429; move on after 2 failures).
- DOES NOT WORK: the `gh` CLI (search and api are blocked for other repos), api.github.com, github.com/search, export.arxiv.org API, crossref, dblp, curl to any host except raw.githubusercontent.com and package registries (pypi.org). Do not retry these.
- Move on after 2 failed fetches of the same resource. Draft your output file early (a valid JSON array) and update it as you go.

Privacy and file rules:
- Never send the user's email, name or other personal identifiers to any outside service (URLs, headers, payloads). Do not build headers from `git config`. If an API wants a User-Agent, use exactly: User-Agent: fastpp-research-bot/1.0
- Write nothing in the repository except your named output file. Before fetching anything to disk, run `mkdir -p` on your own scratch directory (given below) and save every file there by ABSOLUTE path. Never write a relative path like readme.md.
- Never disable the sandbox. Do not call any mcp__hearthbot__ tools.

Output path: /home/claude/fastpp/data/wave8/raw/<ASSIGNMENT_ID>.json for searches (replaces the /Users/... path in the prompt file); verifiers and enrichers keep the path their prompt names. Check it parses with python3 json.load.

Final reply to the orchestrator: terse, max ~8 lines — entry count and names (the JSON file itself is normal).
