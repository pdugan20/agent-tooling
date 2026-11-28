#!/usr/bin/env python3
"""Link selected Apple skills bundled with Xcode into a user skill folder.

Xcode stores each skill as `<name>.idechatprompttemplate` with its references beside it as
`<name>-ref-<reference>.md.packaged`. This script copies each selected skill into an ordinary skill
folder under ~/.agents/xcode-skills and links that folder into the target skill folder. The files
are copies because Codex skips a skill whose SKILL.md is a symlink. Each folder records where its
files came from in .xcode-source.json, so the check and the skill ownership audit can tell when an
Xcode update has changed them and bootstrap needs to run again.

A name ending in "-*" selects the newest numbered release, so "swiftui-whats-new-*" moves from
swiftui-whats-new-27 to swiftui-whats-new-28 when Xcode ships it.

Without Xcode it prints a notice and changes nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/xcode-skills.json"
MANIFEST = ".xcode-source.json"
TEMPLATE_SUFFIX = ".idechatprompttemplate"
REFERENCE_RE = re.compile(r"references/([A-Za-z0-9_.-]+\.md)")


def xcode_app() -> Path | None:
    """The Xcode selected by xcode-select, or AGENT_TOOLING_XCODE_APP when set."""
    override = os.environ.get("AGENT_TOOLING_XCODE_APP")
    if override is not None:
        return Path(override) if override and Path(override).is_dir() else None
    try:
        developer = subprocess.run(
            ["xcode-select", "-p"], capture_output=True, text=True, timeout=15, check=True
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    app = Path(developer).parent.parent
    return app if app.suffix == ".app" and app.is_dir() else None


def resolve_names(patterns: list[str], resources: Path) -> list[str]:
    available = {
        path.name.removesuffix(TEMPLATE_SUFFIX) for path in resources.glob("*" + TEMPLATE_SUFFIX)
    }
    names = []
    for pattern in patterns:
        if pattern.endswith("-*"):
            prefix = pattern[:-1]
            releases = [
                name for name in available if re.fullmatch(re.escape(prefix) + r"\d+", name)
            ]
            if releases:
                names.append(max(releases, key=lambda name: int(name[len(prefix) :])))
        elif pattern in available:
            names.append(pattern)
    return sorted(names)


def skill_files(name: str, resources: Path) -> dict[str, Path]:
    """Map each file of the skill folder to its file in Xcode."""
    template = resources / (name + TEMPLATE_SUFFIX)
    files = {"SKILL.md": template}
    prefix = f"{name}-ref-"
    for reference in sorted(resources.glob(f"{prefix}*.md.packaged")):
        files["references/" + reference.name[len(prefix) :].removesuffix(".packaged")] = reference
    for script in sorted(resources.glob(f"{name}-script-*")):
        files["scripts/" + script.name[len(f"{name}-script-") :]] = script
    missing = sorted(
        set("references/" + item for item in REFERENCE_RE.findall(template.read_text()))
        - set(files)
    )
    if missing:
        raise ValueError(f"{name} names references Xcode doesn't ship: {', '.join(missing)}")
    return files


def build_folder(folder: Path, files: dict[str, Path]) -> None:
    """Make folder hold exactly copies of these files. The folder belongs to this script."""
    folder.mkdir(parents=True, exist_ok=True)
    keep = {*files, MANIFEST}
    for existing in sorted(folder.rglob("*"), reverse=True):
        if existing.is_symlink() or (
            existing.is_file() and existing.relative_to(folder).as_posix() not in keep
        ):
            existing.unlink()
        elif existing.is_dir() and not any(existing.iterdir()):
            existing.rmdir()
    for relative, source in files.items():
        path = folder / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, path)
    manifest = {"files": {relative: str(source) for relative, source in sorted(files.items())}}
    (folder / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n")


def stale_files(folder: Path) -> list[str]:
    """Files in a copied skill folder that are missing, extra, or differ from Xcode's copy.

    Raises ValueError when the folder has no manifest or names a source outside an Xcode bundle.
    """
    sources = {
        relative: Path(source)
        for relative, source in json.loads((folder / MANIFEST).read_text())["files"].items()
    }
    if not sources or any(".app/Contents/" not in source.as_posix() for source in sources.values()):
        raise ValueError(f"{folder.name} copies files from outside an Xcode bundle")
    present = {
        path.relative_to(folder).as_posix()
        for path in folder.rglob("*")
        if (path.is_file() or path.is_symlink()) and path.name != MANIFEST
    }
    stale = sorted(present - set(sources))
    for relative, source in sources.items():
        copy = folder / relative
        if (
            copy.is_symlink()
            or not copy.is_file()
            or not source.is_file()
            or copy.read_bytes() != source.read_bytes()
        ):
            stale.append(relative)
    return sorted(stale)


def links_into(target: Path, cache: Path) -> dict[str, Path]:
    """Links in target that this script made, by skill name."""
    if not target.is_dir():
        return {}
    return {
        path.name: Path(os.readlink(path))
        for path in target.iterdir()
        if path.is_symlink() and Path(os.readlink(path)).parent == cache
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--target", type=Path, required=True, help="User skill folder to link into."
    )
    parser.add_argument("--cache", type=Path, default=Path.home() / ".agents/xcode-skills")
    parser.add_argument("--check", action="store_true", help="Report without changing anything.")
    args = parser.parse_args()
    # Links store this path, so it must not depend on the working directory.
    args.cache = args.cache.expanduser().absolute()
    config = json.loads(CONFIG.read_text())

    app = xcode_app()
    if app is None:
        print("NOTICE Xcode isn't installed, so no Xcode skills were linked.")
        return 0
    resources = app / config["resources"]
    names = resolve_names(config["skills"], resources)
    ours = links_into(args.target, args.cache)
    problems = []

    if args.check:
        for name in names:
            folder = args.cache / name
            expected = {
                relative: str(path) for relative, path in skill_files(name, resources).items()
            }
            try:
                recorded = json.loads((folder / MANIFEST).read_text())["files"]
                current = recorded == expected and not stale_files(folder)
            except (OSError, ValueError, KeyError):
                current = False
            linked = (args.target / name).is_symlink() and Path(
                os.readlink(args.target / name)
            ) == folder
            if current and linked:
                print(f"PASS Xcode skill {name}")
            else:
                problems.append(f"FAIL Xcode skill {name} is missing or stale; rerun bootstrap")
        for name in sorted(set(ours) - set(names)):
            problems.append(
                f"FAIL {args.target / name} links an Xcode skill that is no longer selected"
            )
        for problem in problems:
            print(problem)
        return 1 if problems else 0

    for name in names:
        build_folder(args.cache / name, skill_files(name, resources))
        link = args.target / name
        if link.is_symlink() and Path(os.readlink(link)) == args.cache / name:
            continue
        if link.exists() or link.is_symlink():
            print(f"Refusing to replace existing path: {link}", file=sys.stderr)
            print(
                "Compare and preserve it before changing its owner; no path was removed.",
                file=sys.stderr,
            )
            return 1
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(args.cache / name)
    # A newer Xcode can replace a numbered release, so retire links this script made for it.
    for name in sorted(set(ours) - set(names)):
        (args.target / name).unlink()
    print(f"Linked {len(names)} Xcode skills from {app.name}: {', '.join(names)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
