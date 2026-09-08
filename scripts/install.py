#!/usr/bin/env python3
"""Symlink this repository's portable registries into a target project.

Clone this repository once to any path, then run it from inside whichever
project should get the toolkit. It creates the native config directories
Cursor, Claude Code, and Google Antigravity each discover on their own
(.cursor/, .claude/, .agents/), populated with symlinks back into this
repository's agents/, commands/, workflows/, rules/, and skills/
directories, plus AGENTS.md and CLAUDE.md at the target project root.
Authoring templates (any file or directory starting with "_") are never
linked. Safe to re-run: a link this script previously created is refreshed,
a real file left in its place is never touched.
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
LINK_STYLES = ("auto", "relative", "absolute")


def is_managed_link(path: Path) -> bool:
    if not path.is_symlink():
        return False
    resolved = path.resolve()
    return resolved == SOURCE_DIR or SOURCE_DIR in resolved.parents


def is_broken_link(path: Path) -> bool:
    """A symlink whose target no longer exists.

    Reclaimable even though it does not resolve into this repository: it is
    what a link written by an earlier clone location becomes once that clone
    is moved or deleted. The guard exists to protect real files, and a
    dangling link is not one, so refusing to touch it would leave a project
    with no way to repair itself short of deleting the links by hand.
    """
    return path.is_symlink() and not path.exists()


def resolve_link_style(style: str, target_dir: Path) -> str:
    """Pick relative links when this repository lives inside the target project.

    A clone nested in the project (or added under it by hand) moves with the
    project, so relative links survive relocation. A clone kept anywhere else
    does not, so absolute links are the ones that keep resolving.
    """
    if style != "auto":
        return style
    inside_target = SOURCE_DIR == target_dir or target_dir in SOURCE_DIR.parents
    return "relative" if inside_target else "absolute"


def link(src: Path, dest: Path, link_style: str, dry_run: bool) -> None:
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() or dest.exists():
        if is_broken_link(dest) and not is_managed_link(dest):
            print(f"replacing broken link: {dest}", file=sys.stderr)
        elif not is_managed_link(dest):
            print(f"skip (exists, not managed by this script): {dest}", file=sys.stderr)
            return
        if not dry_run:
            dest.unlink()
    if link_style == "relative":
        target = os.path.relpath(src, dest.parent)
    else:
        target = str(src)
    print(f"link: {dest} -> {target}")
    if not dry_run:
        dest.symlink_to(target, target_is_directory=src.is_dir())


def unlink(dest: Path, dry_run: bool) -> None:
    if not (is_managed_link(dest) or is_broken_link(dest)):
        return
    print(f"unlink: {dest}")
    if not dry_run:
        dest.unlink()


def link_dir_contents(src_dir: Path, dest_dir: Path, link_style: str, dry_run: bool) -> None:
    if not src_dir.is_dir():
        return
    for entry in sorted(src_dir.iterdir()):
        if entry.name.startswith("_"):
            continue
        link(entry, dest_dir / entry.name, link_style, dry_run)


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


def run(
    target_dir: Path, hosts: list[str], link_style: str, uninstall: bool, dry_run: bool
) -> None:
    for host in hosts:
        for dest_rel, src_name in HOST_LAYOUTS[host].items():
            dest_dir = target_dir / dest_rel
            if uninstall:
                unlink_dir_contents(dest_dir, dry_run)
            else:
                link_dir_contents(SOURCE_DIR / src_name, dest_dir, link_style, dry_run)

    for name in ROOT_FILES:
        dest = target_dir / name
        if uninstall:
            unlink(dest, dry_run)
        else:
            link(SOURCE_DIR / name, dest, link_style, dry_run)


def print_ignore_hint(target_dir: Path, hosts: list[str]) -> None:
    """Name the entries a project usually keeps out of its own history.

    These are symlinks into a clone that only exists on this machine, so
    committing them hands collaborators dangling paths. Printed as a hint;
    this script never edits the project's .gitignore itself.
    """
    if not (target_dir / ".git").exists():
        return
    entries = sorted({dest_rel.split("/", 1)[0] for host in hosts for dest_rel in HOST_LAYOUTS[host]})
    entries.extend(ROOT_FILES)
    print("\nThese entries are symlinks into this clone, so they only resolve on")
    print("this machine. Add them to the project's .gitignore (or")
    print(".git/info/exclude) unless you deliberately want them committed:")
    for entry in entries:
        print(f"  {entry}")


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
        "--link-style",
        default="auto",
        choices=LINK_STYLES,
        help="symlink target form; auto uses relative links only when this "
        "repository lives inside the target project (default: auto)",
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

    link_style = resolve_link_style(args.link_style, target_dir)
    run(target_dir, hosts, link_style, args.uninstall, args.dry_run)

    action = "Uninstalled" if args.uninstall else "Installed"
    print(f"{action} agents config for [{', '.join(hosts)}] in {target_dir}")
    if not args.uninstall:
        print_ignore_hint(target_dir, hosts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
