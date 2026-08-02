#!/usr/bin/env python3

"""Apply portable, non-secret Codex configuration fixes."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import tomllib
from pathlib import Path
from typing import Any

FALLBACK_LINE = 'project_doc_fallback_filenames = ["CLAUDE.md"]'
FALLBACK_RE = re.compile(r"^project_doc_fallback_filenames\s*=.*$", re.MULTILINE)
COMPUTER_USE_SECTION = "[mcp_servers.computer-use]"
RELATIVE_COMPUTER_USE_COMMAND = (
    "./Codex Computer Use.app/Contents/SharedSupport/"
    "SkyComputerUseClient.app/Contents/MacOS/SkyComputerUseClient"
)
COMPUTER_USE_SUFFIX = (
    ".codex/computer-use/Codex Computer Use.app/Contents/SharedSupport/"
    "SkyComputerUseClient.app/Contents/MacOS/SkyComputerUseClient"
)
PRODUCT_DESIGN_DISABLED_SKILLS = ("ideate", "index")
SKILL_CONFIG_HEADER = "[[skills.config]]"
MCP_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")
MCP_ENV_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _insert_root_fallback(text: str) -> str:
    """Ensure the fallback key is top-level rather than inside a TOML table."""

    try:
        parsed = tomllib.loads(text) if text.strip() else {}
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"Refusing to modify invalid TOML: {error}") from error

    if parsed.get("project_doc_fallback_filenames") == ["CLAUDE.md"]:
        return text

    lines = [line for line in text.splitlines() if not FALLBACK_RE.fullmatch(line)]
    table_index = next(
        (index for index, line in enumerate(lines) if line.lstrip().startswith("[")),
        len(lines),
    )
    lines[table_index:table_index] = [FALLBACK_LINE, ""]

    normalized = "\n".join(lines)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    return f"{normalized}\n" if normalized else f"{FALLBACK_LINE}\n"


def _repair_computer_use_command(text: str, home: Path) -> str:
    client = home / COMPUTER_USE_SUFFIX
    if not os.access(client, os.X_OK):
        return text

    lines = text.splitlines()
    in_computer_use = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("["):
            in_computer_use = stripped == COMPUTER_USE_SECTION
            continue
        if not in_computer_use or not stripped.startswith("command"):
            continue

        match = re.fullmatch(r'command\s*=\s*"([^"]*)"\s*', stripped)
        if match and match.group(1) == RELATIVE_COMPUTER_USE_COMMAND:
            lines[index] = f"command = {json.dumps(str(client))}"
        break

    return "\n".join(lines) + "\n"


def _product_design_skill_paths(home: Path) -> list[Path]:
    roots = (
        home / ".codex/plugins/cache/openai-curated-remote/product-design",
        home / ".codex/.tmp/plugins/plugins/product-design",
    )
    paths: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for skill_name in PRODUCT_DESIGN_DISABLED_SKILLS:
            paths.update(root.glob(f"*/skills/{skill_name}/SKILL.md"))
            direct = root / "skills" / skill_name / "SKILL.md"
            if direct.exists():
                paths.add(direct)
    return sorted(path.resolve() for path in paths)


def _disable_skill(text: str, path: Path) -> str:
    rendered_path = json.dumps(str(path))
    blocks = list(
        re.finditer(
            r"(?ms)^\[\[skills\.config\]\]\s*\n.*?(?=^\[|\Z)",
            text,
        )
    )
    for block in blocks:
        body = block.group(0)
        if not re.search(rf"(?m)^path\s*=\s*{re.escape(rendered_path)}\s*$", body):
            continue
        if re.search(r"(?m)^enabled\s*=", body):
            replacement = re.sub(r"(?m)^enabled\s*=.*$", "enabled = false", body, count=1)
        else:
            replacement = body.rstrip() + "\nenabled = false\n\n"
        return text[: block.start()] + replacement + text[block.end() :]

    suffix = "" if not text.strip() else "\n\n"
    return (
        text.rstrip() + suffix + f"{SKILL_CONFIG_HEADER}\npath = {rendered_path}\nenabled = false\n"
    )


def _disable_product_design_image_ideation(text: str, home: Path) -> str:
    for path in _product_design_skill_paths(home):
        text = _disable_skill(text, path)
    return text


def _render_mcp_server(name: str, spec: dict[str, Any]) -> str:
    if not MCP_NAME_RE.fullmatch(name):
        raise ValueError(f"Invalid managed MCP server name: {name}")

    command = spec.get("command")
    args = spec.get("args", [])
    env = spec.get("env", {})
    if not isinstance(command, str) or not command:
        raise ValueError(f"Managed MCP server {name} requires a command")
    if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        raise ValueError(f"Managed MCP server {name} args must be strings")
    if not isinstance(env, dict) or not all(
        isinstance(key, str) and MCP_ENV_KEY_RE.fullmatch(key) and isinstance(value, str)
        for key, value in env.items()
    ):
        raise ValueError(f"Managed MCP server {name} env must map safe keys to strings")

    lines = [
        f"[mcp_servers.{name}]",
        f"command = {json.dumps(command)}",
        f"args = {json.dumps(args)}",
        f"enabled = {'true' if spec.get('enabled', True) else 'false'}",
    ]
    if env:
        rendered_env = ", ".join(
            f"{key} = {json.dumps(value)}" for key, value in sorted(env.items())
        )
        lines.append(f"env = {{ {rendered_env} }}")
    for field in ("startup_timeout_sec", "tool_timeout_sec"):
        value = spec.get(field)
        if value is not None:
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"Managed MCP server {name} {field} must be positive")
            lines.append(f"{field} = {value}")
    return "\n".join(lines) + "\n"


def _upsert_mcp_server(text: str, name: str, spec: dict[str, Any]) -> str:
    rendered = _render_mcp_server(name, spec)
    header = re.compile(rf"(?m)^\[mcp_servers\.{re.escape(name)}\]\s*$")
    match = header.search(text)
    if match is None:
        separator = "" if not text.strip() else "\n\n"
        return text.rstrip() + separator + rendered

    end = len(text)
    table_prefix = f"mcp_servers.{name}."
    for candidate in re.finditer(r"(?m)^\[\[?([^\]\n]+)\]\]?\s*$", text[match.end() :]):
        table_name = candidate.group(1)
        if table_name.startswith(table_prefix):
            continue
        end = match.end() + candidate.start()
        break

    prefix = text[: match.start()].rstrip()
    suffix = text[end:].lstrip("\n")
    parts = [part for part in (prefix, rendered.rstrip(), suffix.rstrip()) if part]
    return "\n\n".join(parts) + "\n"


def load_mcp_servers(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(
        isinstance(name, str) and isinstance(spec, dict) for name, spec in data.items()
    ):
        raise ValueError("Managed MCP server manifest must be an object of server specs")
    return data


def update_config(
    text: str,
    home: Path,
    additional_disabled_skills: tuple[Path, ...] = (),
    managed_mcp_servers: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Return an updated config without changing secrets or runtime auth."""

    updated = _insert_root_fallback(text)
    updated = _repair_computer_use_command(updated, home)
    updated = _disable_product_design_image_ideation(updated, home)
    for path in additional_disabled_skills:
        updated = _disable_skill(updated, path.resolve())
    for name, spec in sorted((managed_mcp_servers or {}).items()):
        updated = _upsert_mcp_server(updated, name, spec)
    return updated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--disable-skill", type=Path, action="append", default=[])
    parser.add_argument("--mcp-servers", type=Path)
    args = parser.parse_args()

    args.config.parent.mkdir(parents=True, exist_ok=True)
    original = args.config.read_text() if args.config.exists() else ""
    managed_mcp_servers = load_mcp_servers(args.mcp_servers) if args.mcp_servers else None
    updated = update_config(
        original,
        args.home,
        tuple(args.disable_skill),
        managed_mcp_servers,
    )
    if updated == original:
        return

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=args.config.parent,
        prefix=f".{args.config.name}.",
        delete=False,
    ) as handle:
        handle.write(updated)
        temporary_path = Path(handle.name)
    os.replace(temporary_path, args.config)


if __name__ == "__main__":
    main()
