#!/usr/bin/env python3
"""Validate a DiceFrame adventure package with the production loader.

Usage:
    python validate_pack.py <package-directory> [--repo <diceframe-repo-root>]

Locates the diceframe repository (default: search upward from the current
directory for ``src/adventures/bundle.py``), loads the package through
``AdventureBundleLoader`` — the same atomic validation production uses — and
prints a manifest summary plus the content digest. Exit code 0 = valid.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def find_repo(start: Path) -> Path | None:
    for candidate in (start, *start.parents):
        if (candidate / "src" / "adventures" / "bundle.py").is_file():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="package directory containing manifest.json")
    parser.add_argument("--repo", type=Path, default=None, help="diceframe repository root")
    args = parser.parse_args()

    package = args.package.resolve()
    if not (package / "manifest.json").is_file():
        print(f"not an adventure package (missing manifest.json): {package}", file=sys.stderr)
        return 2

    repo = args.repo.resolve() if args.repo else (
        find_repo(Path.cwd()) or find_repo(package)
    )
    if repo is None:
        print(
            "cannot locate the diceframe repo (looked for src/adventures/bundle.py "
            "from the current directory); pass --repo <path>",
            file=sys.stderr,
        )
        return 2
    sys.path.insert(0, str(repo))

    from src.adventures.bundle import AdventureBundleError, AdventureBundleLoader

    try:
        # Importing the ruleset registers the core:dnd2024 mechanics validator.
        # If this environment cannot import it, D&D-specific checks are simply
        # skipped (unresolved), mirroring production behavior.
        try:
            import src.rulesets.dnd2024.adventure_validation  # noqa: F401
        except Exception as exc:  # noqa: BLE001
            print(f"note: dnd2024 mechanics validator unavailable ({exc}); skipped", file=sys.stderr)

        bundle = AdventureBundleLoader(package.parent).load(package.name)
    except AdventureBundleError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    manifest = bundle.manifest
    counts = {kind: len(items) for kind, items in sorted(bundle.entities.items())}
    print(f"OK  adventure_id={manifest.adventure_id}  version={manifest.version}")
    print(
        f"    format={manifest.format}  world_policy={manifest.world_policy}"
        + (f"  world={manifest.recommended_world_id}" if manifest.recommended_world_id else "")
    )
    print(
        f"    runtime={manifest.required_runtime_id}>={manifest.required_runtime_version}"
        f"  locales={','.join(manifest.supported_locales)} (default {manifest.default_locale})"
    )
    print(f"    entities={counts}")
    print(f"    content_digest={bundle.content_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
