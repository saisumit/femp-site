# Plugins experiment: state and rollback

> **Status, 22 Nov 2026, 03:10:** the website part is **LIVE on femp.ai** (femp-site `main`, merge commit
> `6088f73`), and the waitlist sheet script is on **version 3** (adds the `Wants` column). The iPhone app and the
> server are still only on their `main-plugin` branches. To undo the live website, use
> “Roll back after going live” below: one restore and a push, back in about a minute.

Femp as a general assistant with plugins (femp-dtc, femp-jobs, femp-finance; shown as Femp for DTC brands, Femp for Jobs, Femp for Finance) lives only on a branch called
`main-plugin` in each repo. Nothing on `main` / `main-python` changed, and the live femp.ai, the live server and the
live waitlist sheet are untouched. Rolling back means switching branches and deleting `main-plugin`.

## Where everything stands (22 Nov 2026)

| Repo | Safe branch (unchanged) | Experiment | What the experiment changes |
|---|---|---|---|
| `~/femp-site` | `main` at `1759cd8`, live on femp.ai | `main-plugin` at `bb9f4d4`, **local only, not pushed, not live** | General home `/`, one page per plugin (`/dtc/` = today's home, `/jobs/`, `/finance/`), shared Pricing, FAQ, Security and Blog with one nav, old Features/How it works/Integrations addresses forward to `/dtc/`, waitlist asks “What do you want Femp for?”, sheet script gains a `Wants` column (file only, not deployed) |
| `~/ops-secretary-ios` | `main` at `4c2909a` | `main-plugin` at `063c876`, local only | Plugins tab replaces Store and WhatsApp tabs; DTC opens the old store screen; Femp for Jobs and Femp for Finance show “Coming soon”; WhatsApp moves into You. **This build is installed on Sumit's iPhone.** |
| `~/ecom-secretary` | `main-python` at `2a3a77e` | `main-plugin`, same commit, only this file added | No code changes. (Uncommitted waitlist work in the working tree is separate from the experiment and moves with whichever branch is checked out.) |
| Google Sheet script | Version 2, live | none | The branch's `scripts/waitlist-sheet.gs` adds a `Wants` column but has **not** been deployed |

## Roll back (you don't want plugins)

Run these four blocks. Each takes seconds. Nothing live needs to change, because nothing live was changed.

```sh
# 1. Website: back to the live version, drop the experiment
cd ~/femp-site && git switch main && git branch -D main-plugin

# 2. iPhone app: back to the old code and reinstall the old app on the phone
cd ~/ops-secretary-ios && git switch main && scripts/run-on-phone.sh && git branch -D main-plugin

# 3. Server: back to main-python (no code changed on the branch)
cd ~/ecom-secretary && git switch main-python && git branch -D main-plugin

# 4. Google Sheet script: nothing to do (the new version was never deployed)
```

`git branch -D` deletes the branch for good. To keep it for later instead, skip the `git branch -D …` part; the
experiment then just sits on its branch.

## Pause without deleting (decide later)

```sh
cd ~/femp-site && git switch main
cd ~/ops-secretary-ios && git switch main && scripts/run-on-phone.sh   # old app back on the phone
cd ~/ecom-secretary && git switch main-python
```

Come back with `git switch main-plugin` in each repo (and `scripts/run-on-phone.sh` for the app).

## Go live (you like it)

Only when you say so:

1. **Waitlist sheet:** paste the branch's `scripts/waitlist-sheet.gs` into the sheet's Apps Script, then Deploy →
   Manage deployments → edit → New version. It only adds a `Wants` column, so the current site keeps working.
2. **Website:** `cd ~/femp-site && git switch main && git merge --no-ff main-plugin && git push`. GitHub Pages
   publishes in about a minute. Old addresses (`/features/` etc.) forward to `/dtc/…` through small pages.
   Optional later: move hosting to Cloudflare Pages for real 301 redirects.
3. **App:** merge `main-plugin` into `main` in `~/ops-secretary-ios`, then TestFlight as usual.

## Roll back after going live

```sh
# Website: put every file back exactly as it was before plugins (1759cd8) and publish
# (works however many changes came after the go-live; old site back in about a minute)
cd ~/femp-site && git switch main && git restore --source=1759cd8 --staged --worktree :/ \
  && git commit -m "Roll back to the pre-plugins site" && git push

# Waitlist sheet: Apps Script → Deploy → Manage deployments → edit → Version 2 → Deploy
# (optional: version 3 only adds a Wants column, and the old site works with it)
# (rows already collected keep their Wants value; the column is simply ignored)

# App: revert the merge on main the same way, then reinstall or ship a new TestFlight build
cd ~/ops-secretary-ios && git switch main && git revert -m 1 --no-edit $(git log --merges -1 --format=%H) && scripts/run-on-phone.sh
```

`git revert` adds an “undo” commit instead of rewriting history, so nothing is lost and it can itself be undone.
