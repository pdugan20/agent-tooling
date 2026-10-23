#!/usr/bin/env python3
"""Read-only audit of user skill sources, complete resource trees and private recovery bindings."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

IGNORED = {".git", "__pycache__", "node_modules", ".DS_Store"}


def tree_files(root: Path) -> dict[str, str]:
    """Hash runtime resources; generated Python caches are not source."""
    result = {}
    for directory, directories, files in os.walk(root, followlinks=False):
        directories[:] = sorted(name for name in directories if name not in IGNORED)
        for name in sorted(
            files + [name for name in directories if (Path(directory) / name).is_symlink()]
        ):
            path = Path(directory) / name
            if name in IGNORED or path.suffix == ".pyc":
                continue
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                # A linked resource can change without changing its link text.
                # Require a self-contained tree rather than claiming to pin it.
                path.resolve(strict=True).relative_to(root.resolve())
                value = b"link\0" + os.readlink(path).encode() + b"\0"
                if path.is_file():
                    value += path.read_bytes()
                else:
                    raise ValueError("linked resource directories need explicit packaging")
            else:
                value = path.read_bytes()
            result[relative] = hashlib.sha256(value).hexdigest()
    return result


def tree_hash(files: dict[str, str]) -> str:
    return hashlib.sha256(
        json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def git_info(source: Path, files: dict[str, str]) -> dict:
    source = source.resolve()

    def git(*arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(source), *arguments],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

    top = git("rev-parse", "--show-toplevel")
    if top.returncode:
        return {"tracked": False, "untracked": sorted(files)}
    root = Path(top.stdout.strip()).resolve()
    prefix = source.relative_to(root)
    tracked = set(git("ls-files", "--full-name", "-z", "--", ".").stdout.split("\0"))
    missing = sorted(name for name in files if (prefix / name).as_posix() not in tracked)
    head = git("rev-parse", "HEAD")
    dirty = git("status", "--porcelain", "--", ".")
    committed = (
        not missing
        and head.returncode == 0
        and git("diff", "--quiet", "HEAD", "--", ".").returncode == 0
    )
    return {
        "tracked": not missing,
        "committed": committed,
        "untracked": missing,
        "root": str(root),
        "revision": head.stdout.strip() if head.returncode == 0 else None,
        "dirty": bool(dirty.stdout),
    }


def audit(roots: list[Path], ledger: dict, optional_roots: set[Path] | None = None) -> dict:
    findings, entries, sources = [], [], {}
    bindings = {
        str(Path(item["path"]).expanduser().absolute()): item for item in ledger.get("bindings", [])
    }

    def finding(code: str, entry: str, severity: str = "error") -> None:
        findings.append({"code": code, "entry": entry, "severity": severity})

    for root in roots:
        if not root.exists():
            if root not in (optional_roots or set()):
                finding("missing-configured-root", root.name)
            continue
        for installed in sorted(root.iterdir()):
            if installed.name.startswith("."):
                continue
            if installed.is_symlink() and not installed.exists():
                finding("broken-link", installed.name)
                continue
            if not (installed / "SKILL.md").is_file():
                continue
            source = installed.resolve()
            key = str(source)
            if key not in sources:
                try:
                    files = tree_files(source)
                    sources[key] = {
                        "path": key,
                        "treeSha256": tree_hash(files),
                        "files": len(files),
                        **git_info(source, files),
                    }
                except (OSError, ValueError, subprocess.SubprocessError):
                    finding("unreadable-or-external-resource", installed.name)
                    continue
            record = sources[key]
            binding = bindings.get(str(installed.absolute()), {})
            entry = {
                "name": installed.name,
                "path": str(installed),
                "source": key,
                "treeSha256": record["treeSha256"],
                "owner": binding.get("owner"),
                "scope": binding.get("intendedScope"),
                "state": binding.get("state"),
            }
            entries.append(entry)
            if (
                binding.get("resolvedSource")
                and str(Path(binding["resolvedSource"]).resolve()) != key
            ):
                finding("source-mismatch", installed.name)
            expected = binding.get("treeSha256")
            if expected and expected != record["treeSha256"]:
                finding("resource-drift", installed.name)
            recovered = False
            if binding.get("recoverySource"):
                try:
                    recovery = Path(binding["recoverySource"])
                    recovered_files = tree_files(recovery)
                    recovered = tree_hash(recovered_files) == record["treeSha256"] and git_info(
                        recovery, recovered_files
                    ).get("committed", False)
                except (OSError, ValueError, subprocess.SubprocessError):
                    recovered = False
                if not recovered:
                    finding("recovery-mismatch", installed.name)
            if not record["tracked"]:
                if not (
                    recovered and expected and binding.get("owner") and binding.get("intendedScope")
                ):
                    finding("untracked-resources", installed.name)
                else:
                    finding("retained-copy-with-tracked-recovery", installed.name, "warning")
            elif record.get("dirty"):
                finding("source-has-local-edits", installed.name, "warning")
    by_name = {}
    for entry in entries:
        by_name.setdefault(entry["name"], set()).add(entry["treeSha256"])
    for name, hashes in by_name.items():
        if len(hashes) > 1:
            finding("divergent-duplicate", name)
    return {
        "schemaVersion": 1,
        "entryCount": len(entries),
        "sourceCount": len(sources),
        "entries": entries,
        "sources": list(sources.values()),
        "findings": findings,
        "ok": not any(item["severity"] == "error" for item in findings),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, action="append", help="Bounded skill root; repeat for multiple roots."
    )
    parser.add_argument("--ledger", type=Path)
    parser.add_argument(
        "--json", action="store_true", help="Include machine paths in a private JSON report."
    )
    args = parser.parse_args()
    codex_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    roots = args.root or [
        Path.home() / ".agents/skills",
        codex_root / "skills",
        Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "skills",
    ]
    ledger_path = args.ledger or codex_root / "local/skill-ownership.json"
    try:
        ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
        optional_roots = set() if args.root else set(roots)
        report = audit(roots, ledger, optional_roots)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"Skill ownership audit failed: {type(error).__name__}") from error
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"Skill ownership: {report['entryCount']} entries, "
            f"{report['sourceCount']} source trees."
        )
        for item in report["findings"]:
            print(f"{item['severity']}: {item['entry']}: {item['code']}")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
