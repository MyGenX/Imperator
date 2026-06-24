# Install Security

Imperator's installer scripts do two things: download or update this repository,
then install the Python CLI in editable mode. They do not modify your projects
until you later run `imperator init` inside a project directory.

## macOS, Linux, and WSL

`install.sh`:

1. Reads `IMPERATOR_REPO`, defaulting to `https://github.com/MyGenX/Imperator`.
2. Reads `IMPERATOR_DIR`, defaulting to `$HOME/.imperator`.
3. Checks that `git`, `python3`, and `pip3` are available.
4. If `$IMPERATOR_DIR/.git` exists, runs `git -C "$IMPERATOR_DIR" pull --quiet`.
5. Otherwise, runs `git clone --quiet "$REPO" "$IMPERATOR_DIR"`.
6. Runs `pip3 install -e "$IMPERATOR_DIR/cli" --quiet`.

## Windows PowerShell

`install.ps1`:

1. Reads `$env:IMPERATOR_REPO`, defaulting to `https://github.com/MyGenX/Imperator`.
2. Reads `$env:IMPERATOR_DIR`, defaulting to `$HOME\.imperator`.
3. Checks that `git`, `python`, and `pip` are available.
4. If `$IMPERATOR_DIR\.git` exists, runs `git -C $IMPERATOR_DIR pull --quiet`.
5. Otherwise, runs `git clone --quiet $REPO $IMPERATOR_DIR`.
6. Runs `pip install -e "$IMPERATOR_DIR\cli" --quiet`.

## Environment Variables

| Variable | Meaning | Default |
|---|---|---|
| `IMPERATOR_DIR` | Local checkout path used by the installer and by the CLI when locating rules. | `$HOME/.imperator` on Unix-like systems, `$HOME\.imperator` on Windows |
| `IMPERATOR_REPO` | Git repository cloned or pulled by the installer. | `https://github.com/MyGenX/Imperator` |

## Requirements

- Git
- Python 3.8+
- `pip`

The CLI package declares one Python dependency: `Jinja2>=3.0`.

## Telemetry

Imperator does not include telemetry code. The installer does not phone home
beyond the explicit Git clone or pull and the pip install command you run.

## Manual Install

For the most reviewable install path, clone and inspect the repository first:

```bash
git clone https://github.com/MyGenX/Imperator ~/.imperator
cd ~/.imperator
pip install -e cli
```

Then initialize a project from that installed CLI:

```bash
cd /path/to/your/project
imperator init
```

`imperator init` writes generated agent files and `.imperator.json` in the current
project. Review and commit those files if they match your team's policy.
