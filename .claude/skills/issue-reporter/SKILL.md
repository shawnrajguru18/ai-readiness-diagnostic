---
name: issue-reporter
description: File a GitHub issue from findings in this repo, on github.com or a GitHub Enterprise Server host such as partner-github.dxc.com. Use when the user asks to file, open, raise or report an issue, or to turn a bug/finding/review into a tracked ticket. Discovers a token from standard environment variables plus GITHUB_PARTNER_DXC_TOKEN, uses curl (gh CLI is not available), and verifies the result.
---

# Issue Reporter

File a well-evidenced GitHub issue via the REST API using `curl`.

**`gh` is not installed in this environment and will not be.** Do not suggest installing it. Every
call in this skill is `curl` against the REST API.

---

## 1. Resolve the token

Check these names **in order** and use the first that is set. The list is deliberately broad so the
skill works for any developer on the team, whatever their setup:

| Order | Variable | Typical use |
|---|---|---|
| 1 | `GITHUB_PARTNER_DXC_TOKEN` | This project's DXC Enterprise host (`partner-github.dxc.com`) |
| 2 | `GH_ENTERPRISE_TOKEN` | `gh` convention for Enterprise hosts |
| 3 | `GITHUB_ENTERPRISE_TOKEN` | Same, alternate spelling |
| 4 | `GH_TOKEN` | `gh` convention |
| 5 | `GITHUB_TOKEN` | The most common name; CI default |

**Prefer a host-specific token when the target is an Enterprise host.** A `github.com` token will not
authenticate against `partner-github.dxc.com` and vice versa. If the first match is a generic name and
the target is Enterprise, check whether a host-specific one is also set and prefer it.

Check both process and user scope — a variable set through the Windows GUI is not always in the
process environment:

```powershell
$names = @('GITHUB_PARTNER_DXC_TOKEN','GH_ENTERPRISE_TOKEN','GITHUB_ENTERPRISE_TOKEN','GH_TOKEN','GITHUB_TOKEN')
$t = $null; $tName = $null
foreach ($n in $names) {
  $v = [Environment]::GetEnvironmentVariable($n)
  if (-not $v) { $v = [Environment]::GetEnvironmentVariable($n, 'User') }
  if ($v) { $t = $v; $tName = $n; break }
}
if ($t) { "using $tName (length $($t.Length))" } else { "NO TOKEN FOUND" }
```

Bash equivalent:

```bash
for n in GITHUB_PARTNER_DXC_TOKEN GH_ENTERPRISE_TOKEN GITHUB_ENTERPRISE_TOKEN GH_TOKEN GITHUB_TOKEN; do
  v="${!n}"; if [ -n "$v" ]; then TOKEN="$v"; TOKEN_NAME="$n"; break; fi
done
[ -n "$TOKEN" ] && echo "using $TOKEN_NAME (length ${#TOKEN})" || echo "NO TOKEN FOUND"
```

**Never print, echo or log the token value.** Report only which variable was used and its length.
Never write it into a file, a commit, or an issue body.

If none is set, stop and tell the user which names were checked and where to create one
(`https://<host>/settings/tokens`). Do not prompt them to paste a token into the conversation.

---

## 2. Resolve the API base and the repo

| Target | API base |
|---|---|
| `github.com` | `https://api.github.com` |
| GitHub Enterprise Server, e.g. `partner-github.dxc.com` | `https://<host>/api/v3` |

Derive `owner/repo` from the URL the user gave, or from `git remote -v` if they did not give one.
**If neither is available, ask — do not guess.**

Confirm access before writing anything:

```powershell
curl.exe -s -o resp.json -w "%{http_code}" -H "Authorization: token $t" `
  -H "Accept: application/vnd.github+json" "$api/repos/$owner/$repo"
```

Expect `200`, and check `has_issues` is `true` and `permissions.push` is `true`.

### Reading a 404

**A `404` on a repo you know exists is almost never a wrong path.** It is GitHub declining to confirm
existence to a credential that cannot see it. In order of likelihood:

1. **Token scope too narrow.** `public_repo` does not grant private repositories; the full `repo`
   scope does. This is the single most common cause.
2. Wrong host — a `github.com` token against an Enterprise host.
3. The repo genuinely does not exist, or the owner is wrong.

Diagnose scopes from the response headers rather than guessing:

```powershell
curl.exe -s -D hdr.txt -o body.json -H "Authorization: token $t" "$api/user"
Select-String -Path hdr.txt -Pattern '^HTTP|^x-oauth-scopes' -CaseSensitive:$false
```

`X-OAuth-Scopes` lists what the token actually carries. If `repo` is absent and the target is
private, stop and ask the user to add it — do not work around it.

Listing an org's repos (`/orgs/<org>/repos`) reports **the user's** permissions, so a repo can appear
there with `push: true` and still `404` on direct access. That combination is a scope problem, not a
contradiction.

---

## 3. Check before you file

Filing is outward-facing and hard to undo — an issue can be closed but not unsent, and notifications
go out immediately.

- **Proceed without asking** when the user explicitly said to file it and named the target.
- **Ask first** when the target is ambiguous, or when you inferred the repo rather than being told.

**Always stop and ask when the target repo is public and the content is not.** Check `private` on the
repo response. Internal architecture notes, `file:line` citations, commit authorship, customer
impact and security findings routinely appear in a good issue body, and a public repo publishes all of
it. Never substitute a public fork or mirror because the private target returned an error — routing
around a permissions failure is not a routing decision, it is a disclosure decision, and it belongs to
the user.

Search for duplicates first:

```powershell
curl.exe -s -H "Authorization: token $t" `
  "$api/search/issues?q=repo:$owner/$repo+is:issue+<keywords>"
```

---

## 4. Write the body

Ground every claim in something the reader can check. The structure that works:

1. **Summary** — what is wrong and what it costs, in three sentences. Lead with impact on users or
   data, not on code.
2. **Verified against** — the commit SHA the claims were checked at. Findings age; say when.
3. **Evidence** — `path/to/file.py:120-134` citations, and short quoted code for the load-bearing
   lines. Cite line ranges, not whole files.
4. **Why it is silent / why it was missed** — if a defect survived review, say what hid it. This is
   often the most useful section.
5. **Provenance** — which commit introduced it. `git log -S '<distinctive string>' -- <path>` finds
   it directly. Quote the commit message when it explains the intent; the author usually had a
   reason, and naming it fairly makes the issue actionable rather than accusatory.
6. **Proposed fix** — concrete diffs or patches. If a layered fix is right (make it fail loudly, then
   fix the instance, then fix the root cause, then add a regression test), lay the layers out with
   their dependencies so work can start on the independent ones.
7. **Already-affected data** — how to identify records produced while the defect was live. A
   forensic marker beats "we should investigate".
8. **Open decision** — anything genuinely the team's call, stated as a question with options, not
   resolved silently.

Write in the repo's register. Attribute code to commits, not to people — `5661b28` rather than a
name, even though `git log` gives you both.

Draft to a file in the scratchpad directory, not inline in the request. It keeps the payload
reviewable and lets you iterate before posting.

---

## 5. Post it

Build the JSON with a real serializer. **Never hand-assemble JSON** — issue bodies contain quotes,
backticks, backslashes and newlines that will break a string-concatenated payload.

```powershell
$body = [IO.File]::ReadAllText($draftPath)                       # UTF-8 aware
$payload = @{ title = $title; body = $body } | ConvertTo-Json -Depth 3 -Compress
[IO.File]::WriteAllText("$env:TEMP\issue.json", $payload, [Text.UTF8Encoding]::new($false))

$code = & curl.exe -s -o "$env:TEMP\resp.json" -w "%{http_code}" -X POST `
  -H "Authorization: token $t" -H "Accept: application/vnd.github+json" `
  -H "Content-Type: application/json" `
  --data-binary "@$env:TEMP\issue.json" "$api/repos/$owner/$repo/issues"
```

`201` means created. The response carries `number` and `html_url`.

### Encoding traps on Windows PowerShell 5.1

These will silently corrupt a body containing em-dashes, ellipses, arrows or emoji:

- **`Get-Content` defaults to the ANSI codepage.** Use
  `[IO.File]::ReadAllText($p, [Text.UTF8Encoding]::new($false))` for anything you will compare or
  post. Reading an API response with `Get-Content` produces mojibake (`â€¦`, `âŒ`) that looks like a
  server-side defect and is not.
- **Write the payload with `[IO.File]::WriteAllText` and an explicit BOM-less UTF-8 encoding.** A BOM
  at the start of a JSON body is a parse error.
- **Use `--data-binary "@file"`, not `-d`.** `-d` strips newlines, which destroys Markdown.

### Labels and assignees

**Do not set labels blindly.** A label that does not exist on the repo makes the whole request `422`
and nothing is created. Either omit them and patch afterwards, or fetch what exists first:

```powershell
curl.exe -s -H "Authorization: token $t" "$api/repos/$owner/$repo/labels?per_page=100"
```

To add them after the fact:

```powershell
curl.exe -s -X PATCH -H "Authorization: token $t" -H "Content-Type: application/json" `
  --data-binary "@patch.json" "$api/repos/$owner/$repo/issues/<number>"
```

---

## 6. Verify, then report

Re-read the created issue and confirm the body survived the round trip:

```powershell
$raw = [IO.File]::ReadAllText($respPath, [Text.UTF8Encoding]::new($false))
$j = $raw | ConvertFrom-Json
"identical: $($src.TrimEnd() -ceq $j.body.TrimEnd())"
```

If the lengths differ, suspect your **reading** before you suspect the server (see the encoding traps
above).

Report to the user: the issue number, the full `html_url`, the HTTP status, and anything you
deliberately left unset (labels, assignees, milestone) so they can decide on it. If you considered a
different repo and rejected it, say so and why.

---

## Failure modes, in one table

| Symptom | Cause | Action |
|---|---|---|
| `404` on a repo that exists | Token lacks `repo` scope for a private repo | Check `X-OAuth-Scopes`; ask the user to widen the token |
| `401` | Token empty, expired, or wrong host | Re-resolve; confirm the variable is actually populated |
| `403` with a rate-limit header | Secondary rate limit | Wait; do not retry in a loop |
| `422 Validation Failed` | Non-existent label, assignee, or milestone | Omit them; patch after creation |
| `410 Gone` | Issues disabled on the repo | Check `has_issues`; ask where to file instead |
| Body renders as one long line | Posted with `-d` instead of `--data-binary` | Repost or `PATCH` the body |
| `â€¦` / `âŒ` in the body | Read with `Get-Content` (ANSI) | Re-read as UTF-8 before concluding anything is wrong |
