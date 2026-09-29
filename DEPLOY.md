# Deploying atle.dev

The public site (atle.dev) is the FastAPI app in `src/web`. It runs on an AWS Lightsail instance. The domain is registered at GoDaddy and points to the instance's static IP.

## Where things are

| What | Where |
|---|---|
| Server | AWS Lightsail, Ubuntu, user `ubuntu`, public IP `3.223.169.219` (region most likely us-east-1) |
| App checkout | `/opt/agentic` (a git clone of `github.com/andreasatle/agentic-framework`, branch `main`) |
| Secrets / config | `/opt/agentic/.env` (not in git; copied up by hand) |
| Deploy script | `/opt/agentic/update.sh` (`git pull --ff-only`, then `sudo systemctl restart agentic`) |
| Service | systemd unit `agentic` |
| Blog posts | runtime data outside git, located by `AGENTIC_BLOG_POSTS_ROOT` in `.env`; deploys never touch it |

## Deploy steps

1. On the Mac, in `~/Projects/AgenticFramework`, get the changes onto `main` and push:

   ```
   git switch main
   git merge <feature-branch>      # if the work was on a branch
   git push
   ```

2. Open a shell on the server. Plain `ssh ubuntu@atle.dev` from the Mac fails with `Permission denied (publickey)` because the Mac's default key isn't authorized. Use the browser console instead: AWS Console → Lightsail → the instance → **Connect using SSH**.

3. On the server:

   ```
   cd /opt/agentic
   git branch --show-current       # expect: main
   git status --short              # expect: nothing (update.sh refuses to pull over local changes)
   ./update.sh
   ```

4. Check the site: open https://atle.dev and https://atle.dev/work with a hard refresh, so the browser doesn't serve cached CSS/JS.

## If something goes wrong

- Service logs: `sudo journalctl -u agentic -n 50`
- Service state: `systemctl status agentic`
- `git pull --ff-only` fails: the server checkout has local edits or diverged. Inspect with `git status` / `git log --oneline -3` before changing anything.
- App refuses to start with `ADMIN_PASSWORD not set` or a generation/posts directory error: `/opt/agentic/.env` is missing or incomplete. It must define `ADMIN_PASSWORD`, `AGENTIC_GENERATED_DIR`, `AGENTIC_BLOG_POSTS_ROOT`, plus the LLM API key(s).
- Updating `.env`: edit it on the server, or copy it up (`scp .env ubuntu@atle.dev:/opt/agentic/.env` works only once SSH from the Mac is set up), then `sudo systemctl restart agentic`.

## Running locally

`scripts/web-app.sh` starts the app on http://127.0.0.1:8000 with auto-reload, reading the local `.env`.

## Content that needs occasional manual updates

- `src/web/projects.py`: the project list for the home and /work pages.
- `src/web/templates/work/<slug>.html`: one page per project.
- `src/web/templates/home.html`: the "Right now" strip. Also bump `NOW_LABEL` in `src/web/api.py`.
- `src/web/content/profile.md` and `resume.md`: the About page.
