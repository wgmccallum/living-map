# Startup Cheatsheet

Quick reference for starting an editing session from a fresh terminal window.

## Standard startup (working at localhost:8000)

```bash
cd "/Users/wgmccallum/Living Map/living-map"
./deploy.sh                   # builds frontend, starts server on :8000
```

Then open `http://localhost:8000` in the browser.

To stop: `Ctrl+C` in the terminal.

`deploy.sh` automatically uses the project's `.venv/bin/python3`, so you don't need to activate the venv manually. If you want to run Python commands by hand (e.g. `python3 -m something`), then activate it: `source .venv/bin/activate`.

## Useful variants

| Command | What it does |
|---|---|
| `./deploy.sh --skip-build` | Skip the slow frontend rebuild (use when you only changed Python code) |
| `./deploy.sh --sandbox` | Run against a throwaway DB copy in `sandboxes/` — your working DB is untouched |
| `./deploy.sh --port 3000` | Use a different port |

## Database files — quick reference

| File | Purpose |
|---|---|
| `living_map.db` | Your live working copy. Edits at :8000 land here. Not in git. |
| `living_map.live.db` | Production snapshot. Committed to git. Railway deploys from this. Updated only by `./publish.sh`. |
| `living_map.seed.db` | "Factory reset" snapshot for `./restore.sh`. Update periodically (see below). |

## Publishing to production

After a session, with the server stopped:

```bash
./publish.sh --dry-run        # preview what will be published
./publish.sh                  # copy → commit → push; Railway redeploys
./publish.sh -m "added X"     # with custom commit message
```

## Updating the seed snapshot

The seed is what `./restore.sh` rolls back to. If it's months old, "restore" wipes out everything you've built since. Refresh it at known-good checkpoints (after a batch of work that validates cleanly, before risky experiments, etc.).

With the server stopped:
```bash
./snapshot.sh --dry-run     # preview: shows current seed age and row-count diff
./snapshot.sh               # interactive: confirms before overwriting
```

The script warns if the server is still running (snapshotting an active DB risks capturing a partial write).

## Panic button

If your working DB is broken and you want to roll back to the seed:
```bash
./restore.sh
```
This auto-backs-up your current `living_map.db` to a timestamped file before overwriting, so you can recover if you change your mind. **Remember**: it restores to whatever date the seed was last refreshed.
