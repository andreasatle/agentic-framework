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

From the Mac, in `~/Projects/AgenticFramework`, with the changes merged into `main`:

```
scripts/deploy.sh
```

It pushes `main` to GitHub, then runs `ssh atle` to check the server checkout is clean, run `/opt/agentic/update.sh`, and confirm the `agentic` service is active. Afterwards, check https://atle.dev with a hard refresh so the browser doesn't serve cached CSS/JS.

### SSH setup (already done on the Mac mini)

- Key pair: `~/.ssh/id_ed25519_atle` (private, has a passphrase) and `~/.ssh/id_ed25519_atle.pub`. The public key is appended to `/home/ubuntu/.ssh/authorized_keys` on the server.
- `~/.ssh/config` entry:

  ```
  Host atle
      HostName atle.dev
      User ubuntu
      IdentityFile ~/.ssh/id_ed25519_atle
  ```

- Test with `ssh atle hostname`. It should print `ip-172-26-3-207`.
- New machine: generate a key with `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_atle`, append its `.pub` line to the server's `authorized_keys`, and add the config entry.
- To revoke a machine, delete its line from the server's `~/.ssh/authorized_keys`.

### Manual fallback (no SSH from the Mac)

AWS Console → Lightsail → the instance → **Connect using SSH**, then:

```
cd /opt/agentic
git branch --show-current       # expect: main
git status --short              # expect: nothing (update.sh refuses to pull over local changes)
./update.sh
```

## If something goes wrong

- Service logs: `ssh atle sudo journalctl -u agentic -n 50`
- Service state: `ssh atle systemctl status agentic`
- `git pull --ff-only` fails: the server checkout has local edits or diverged. Inspect with `git status` / `git log --oneline -3` before changing anything.
- App refuses to start with `ADMIN_PASSWORD not set` or a generation/posts directory error: `/opt/agentic/.env` is missing or incomplete. It must define `ADMIN_PASSWORD`, `AGENTIC_GENERATED_DIR`, `AGENTIC_BLOG_POSTS_ROOT`, plus the LLM API key(s).
- Updating `.env`: `scp .env atle:/opt/agentic/.env`, then `ssh atle sudo systemctl restart agentic`.

## Running locally

`scripts/web-app.sh` starts the app on http://127.0.0.1:8000 with auto-reload, reading the local `.env`.

## Content that needs occasional manual updates

- `src/web/projects.py`: the project list for the home and /work pages.
- `src/web/templates/work/<slug>.html`: one page per project.
- `src/web/templates/home.html`: the "Right now" strip. Also bump `NOW_LABEL` in `src/web/api.py`.
- `src/web/content/profile.md` and `resume.md`: the About page.
