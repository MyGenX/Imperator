"""Shared Imperator installer implementation.

This module is intentionally standard-library only so `install.sh` and
`install.ps1` can download and run it before the CLI package is installed.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

DEFAULT_REPO = "https://github.com/MyGenX/Imperator"
PACKAGE_NAME = "imperator-cli"


@dataclass
class InstallOptions:
    repo: str
    directory: Path
    dry_run: bool = False
    force: bool = False
    uninstall: bool = False
    no_color: bool = False
    non_interactive: bool = False


class InstallerError(RuntimeError):
    pass


class Printer:
    def __init__(self, no_color: bool = False):
        self.no_color = no_color

    def _color(self, text: str, code: str) -> str:
        if self.no_color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def info(self, text: str) -> None:
        print(self._color(f"-> {text}", "36"))

    def ok(self, text: str) -> None:
        print(self._color(f"OK {text}", "32"))

    def warn(self, text: str) -> None:
        print(self._color(f"! {text}", "33"))

    def error(self, text: str) -> None:
        print(self._color(f"ERROR {text}", "31"), file=sys.stderr)


def normalize_argv(argv: Sequence[str]) -> list[str]:
    """Accept PowerShell-style long flags as aliases for argparse long flags."""
    aliases = {
        "-DryRun": "--dry-run",
        "-Force": "--force",
        "-Uninstall": "--uninstall",
        "-Dir": "--dir",
        "-NoColor": "--no-color",
        "-NonInteractive": "--non-interactive",
    }
    return [aliases.get(arg, arg) for arg in argv]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install or uninstall Imperator")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without changing anything")
    parser.add_argument("--force", action="store_true", help="Force refresh/reinstall of an existing Imperator checkout")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the CLI package and remove the Imperator checkout")
    parser.add_argument("--dir", dest="directory", help="Install directory; overrides IMPERATOR_DIR")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--non-interactive", action="store_true", help="Never prompt for input")
    return parser


def parse_args(argv: Sequence[str] | None = None) -> InstallOptions:
    args = build_parser().parse_args(normalize_argv(list(argv or [])))
    directory = args.directory or os.environ.get("IMPERATOR_DIR") or str(Path.home() / ".imperator")
    repo = os.environ.get("IMPERATOR_REPO", DEFAULT_REPO)
    return InstallOptions(
        repo=repo,
        directory=Path(directory).expanduser(),
        dry_run=args.dry_run,
        force=args.force,
        uninstall=args.uninstall,
        no_color=args.no_color,
        non_interactive=args.non_interactive,
    )


def is_imperator_checkout(path: Path) -> bool:
    return (
        (path / ".git").is_dir()
        and (path / "rules" / "global").is_dir()
        and (path / "cli" / "pyproject.toml").is_file()
    )


def _cmd_text(cmd: Sequence[str]) -> str:
    return " ".join(str(part) for part in cmd)


def run_command(
    cmd: Sequence[str],
    options: InstallOptions,
    printer: Printer,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> None:
    if options.dry_run:
        printer.info(f"would run: {_cmd_text(cmd)}")
        return
    runner(list(cmd), check=True)


def ensure_git_available(options: InstallOptions) -> None:
    if shutil.which("git") is None and not options.dry_run:
        raise InstallerError("git is required but was not found on PATH")


def install(
    options: InstallOptions,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    printer: Printer | None = None,
) -> None:
    printer = printer or Printer(options.no_color)
    ensure_git_available(options)

    printer.info(f"Repository: {options.repo}")
    printer.info(f"Install directory: {options.directory}")
    printer.info("Manual review path: clone the repository, inspect it, then run `python3 -m pip install -e cli`")

    if options.directory.exists():
        if not (options.directory / ".git").is_dir():
            raise InstallerError(f"{options.directory} exists but is not a git checkout")
        if not is_imperator_checkout(options.directory):
            raise InstallerError(f"{options.directory} is not recognized as an Imperator checkout")
        if options.force:
            printer.info("Force-refreshing existing Imperator checkout")
            run_command(["git", "-C", str(options.directory), "fetch", "--all", "--quiet", "--prune"], options, printer, runner)
            run_command(["git", "-C", str(options.directory), "reset", "--hard", "origin/main"], options, printer, runner)
        else:
            printer.info("Updating existing Imperator checkout")
            run_command(["git", "-C", str(options.directory), "pull", "--quiet", "--ff-only"], options, printer, runner)
    else:
        printer.info("Cloning Imperator")
        run_command(["git", "clone", "--quiet", options.repo, str(options.directory)], options, printer, runner)

    printer.info("Installing Python CLI")
    run_command([sys.executable, "-m", "pip", "install", "-e", str(options.directory / "cli")], options, printer, runner)
    printer.ok("Imperator install dry run complete" if options.dry_run else "Imperator installed")


def uninstall(
    options: InstallOptions,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    printer: Printer | None = None,
) -> None:
    printer = printer or Printer(options.no_color)
    printer.info(f"Install directory: {options.directory}")

    printer.info("Uninstalling Python CLI package")
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", PACKAGE_NAME], options, printer, runner)

    if not options.directory.exists():
        printer.ok("No Imperator checkout found")
        return
    if not is_imperator_checkout(options.directory):
        raise InstallerError(f"Refusing to remove unrecognized directory: {options.directory}")

    if options.dry_run:
        printer.info(f"would remove: {options.directory}")
    else:
        shutil.rmtree(options.directory)
    printer.ok("Imperator uninstall dry run complete" if options.dry_run else "Imperator uninstalled")


def main(argv: Sequence[str] | None = None) -> int:
    options = parse_args(argv)
    printer = Printer(options.no_color)
    try:
        if options.uninstall:
            uninstall(options, printer=printer)
        else:
            install(options, printer=printer)
    except (InstallerError, subprocess.CalledProcessError) as exc:
        printer.error(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
