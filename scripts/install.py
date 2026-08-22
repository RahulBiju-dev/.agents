#!/usr/bin/env python3
"""Symlink this repository's portable registries into a target project.

Creates the native config directories Cursor, Claude Code, and Google
Antigravity each discover on their own (.cursor/, .claude/, .agents/),
populated with relative symlinks back into this repository's agents/,
commands/, workflows/, rules/, and skills/ directories, plus AGENTS.md and
CLAUDE.md at the target project root. Authoring templates (any file or
directory starting with "_") are never linked. Safe to re-run: a link this
script previously created is refreshed, a real file left in its place is
never touched.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent.parent

HOST_LAYOUTS: dict[str, dict[str, str]] = {
    "cursor": {
        ".cursor/agents": "agents",
        ".cursor/commands": "commands",
        ".cursor/rules": "rules",
        ".cursor/skills": "skills",
    },
    "claude": {
        ".claude/agents": "agents",
        ".claude/commands": "commands",
        ".claude/skills": "skills",
    },
    "antigravity": {
        ".agents/agents": "agents",
        ".agents/workflows": "workflows",
        ".agents/skills": "skills",
    },
}

ROOT_FILES = ("AGENTS.md", "CLAUDE.md")


def is_managed_link(path: Path) -> bool:
    if not path.is_symlink():
        return False
    resolved = path.resolve()
    return resolved == SOURCE_DIR or SOURCE_DIR in resolved.parents


def link(src: Path, dest: Path, dry_run: bool) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() or dest.exists():
        if not is_managed_link(dest):
            print(f"skip (exists, not managed by this script): {dest}", file=sys.stderr)
            return
        if not dry_run:
            dest.unlink()
    relative_target = os.path.relpath(src, dest.parent)
    print(f"link: {dest} -> {relative_target}")
    if not dry_run:
        dest.symlink_to(relative_target, target_is_directory=src.is_dir())


def unlink(dest: Path, dry_run: bool) -> None:
    if not is_managed_link(dest):
        return
    print(f"unlink: {dest}")
    if not dry_run:
        dest.unlink()


def link_dir_contents(src_dir: Path, dest_dir: Path, dry_run: bool) -> None:
    if not src_dir.is_dir():
        return
    for entry in sorted(src_dir.iterdir()):
        if entry.name.startswith("_"):
            continue
        link(entry, dest_dir / entry.name, dry_run)


def unlink_dir_contents(dest_dir: Path, dry_run: bool) -> None:
    if not dest_dir.is_dir():
        return
    for entry in sorted(dest_dir.iterdir()):
        unlink(entry, dry_run)


def parse_hosts(raw: str) -> list[str]:
    hosts = [part.strip() for part in raw.split(",") if part.strip()]
    unknown = [host for host in hosts if host not in HOST_LAYOUTS]
    if unknown:
        raise ValueError(f"unknown host(s) {unknown}; expected one of {sorted(HOST_LAYOUTS)}")
    return hosts


def run(target_dir: Path, hosts: list[str], uninstall: bool, dry_run: bool) -> None:
    for host in hosts:
        for dest_rel, src_name in HOST_LAYOUTS[host].items():
            dest_dir = target_dir / dest_rel
            if uninstall:
                unlink_dir_contents(dest_dir, dry_run)
            else:
                link_dir_contents(SOURCE_DIR / src_name, dest_dir, dry_run)

    for name in ROOT_FILES:
        dest = target_dir / name
        if uninstall:
            unlink(dest, dry_run)
        else:
            link(SOURCE_DIR / name, dest, dry_run)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--target", default=".", type=Path, help="project directory to install into (default: cwd)"
    )
    parser.add_argument(
        "--hosts",
        default="cursor,claude,antigravity",
        help="comma-separated subset of cursor,claude,antigravity (default: all three)",
    )
    parser.add_argument(
        "--uninstall", action="store_true", help="remove links this script previously created"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="print planned actions without touching the filesystem"
    )
    args = parser.parse_args(argv)

    try:
        hosts = parse_hosts(args.hosts)
    except ValueError as exc:
        parser.error(str(exc))

    target_dir = args.target.resolve()
    if not target_dir.is_dir():
        parser.error(f"target directory does not exist: {target_dir}")

    run(target_dir, hosts, args.uninstall, args.dry_run)

    action = "Uninstalled" if args.uninstall else "Installed"
    print(f"{action} agents config for [{', '.join(hosts)}] in {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
