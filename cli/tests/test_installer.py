from pathlib import Path
from subprocess import CompletedProcess

import pytest

from imperator import installer


def _runner(calls):
    def run(cmd, check):
        calls.append(cmd)
        return CompletedProcess(cmd, 0)

    return run


def _checkout(path: Path) -> None:
    (path / ".git").mkdir(parents=True)
    (path / "rules" / "global").mkdir(parents=True)
    (path / "cli").mkdir()
    (path / "cli" / "pyproject.toml").write_text("[project]\nname='imperator-cli'\n", encoding="utf-8")


def test_parse_args_prefers_dir_flag_over_env(monkeypatch, tmp_path):
    monkeypatch.setenv("IMPERATOR_DIR", str(tmp_path / "env"))
    monkeypatch.setenv("IMPERATOR_REPO", "https://example.test/imperator")

    options = installer.parse_args(["--dir", str(tmp_path / "flag"), "--dry-run", "--no-color"])

    assert options.directory == tmp_path / "flag"
    assert options.repo == "https://example.test/imperator"
    assert options.dry_run is True
    assert options.no_color is True


def test_parse_args_accepts_powershell_aliases(tmp_path):
    options = installer.parse_args(["-DryRun", "-Force", "-Uninstall", "-Dir", str(tmp_path)])

    assert options.dry_run is True
    assert options.force is True
    assert options.uninstall is True
    assert options.directory == tmp_path


def test_dry_run_install_does_not_create_directory(tmp_path):
    target = tmp_path / "imperator"
    options = installer.InstallOptions(
        repo=installer.DEFAULT_REPO,
        directory=target,
        dry_run=True,
        no_color=True,
    )

    installer.install(options)

    assert not target.exists()


def test_force_refresh_uses_fetch_and_reset_for_owned_checkout(tmp_path):
    target = tmp_path / "imperator"
    _checkout(target)
    calls = []
    options = installer.InstallOptions(
        repo=installer.DEFAULT_REPO,
        directory=target,
        force=True,
        no_color=True,
    )

    installer.install(options, runner=_runner(calls))

    assert ["git", "-C", str(target), "fetch", "--all", "--quiet", "--prune"] in calls
    assert ["git", "-C", str(target), "reset", "--hard", "origin/main"] in calls
    assert any(cmd[:4] == [installer.sys.executable, "-m", "pip", "install"] for cmd in calls)


def test_install_refuses_unrecognized_existing_directory(tmp_path):
    target = tmp_path / "not-imperator"
    target.mkdir()
    options = installer.InstallOptions(repo=installer.DEFAULT_REPO, directory=target, no_color=True)

    with pytest.raises(installer.InstallerError):
        installer.install(options, runner=_runner([]))


def test_uninstall_refuses_to_remove_unrecognized_directory(tmp_path):
    target = tmp_path / "not-imperator"
    target.mkdir()
    calls = []
    options = installer.InstallOptions(repo=installer.DEFAULT_REPO, directory=target, no_color=True)

    with pytest.raises(installer.InstallerError):
        installer.uninstall(options, runner=_runner(calls))

    assert target.exists()
    assert calls and calls[0][:4] == [installer.sys.executable, "-m", "pip", "uninstall"]


def test_uninstall_removes_owned_checkout(tmp_path):
    target = tmp_path / "imperator"
    _checkout(target)
    calls = []
    options = installer.InstallOptions(repo=installer.DEFAULT_REPO, directory=target, no_color=True)

    installer.uninstall(options, runner=_runner(calls))

    assert not target.exists()
    assert calls and calls[0][:4] == [installer.sys.executable, "-m", "pip", "uninstall"]
