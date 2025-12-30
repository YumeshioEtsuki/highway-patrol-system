#!/usr/bin/env python3
"""Validate frontend paths after directory refactor."""
from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent
SRC_STATIC = ROOT / "src" / "static"
SRC_TEMPLATES = ROOT / "src" / "templates"
MINIPROGRAM = ROOT / "miniprogram"

ISSUES: list[str] = []


def require_dir(path: Path, label: str) -> None:
    if not path.exists():
        ISSUES.append(f"MISSING: {label} ({path})")
        print(f"✗ {label} missing: {path}")
    else:
        print(f"✓ {label}: {path}")


def check_static() -> None:
    print("\n[1/4] static assets")
    require_dir(SRC_STATIC, "src/static")
    for sub in ("css", "js", "images"):
        p = SRC_STATIC / sub
        if p.exists():
            count = len(list(p.glob("*")))
            print(f"  ✓ {sub}/ (items: {count})")
        else:
            ISSUES.append(f"MISSING: src/static/{sub}")
            print(f"  ✗ {sub}/ missing")


def check_templates() -> None:
    print("\n[2/4] templates")
    require_dir(SRC_TEMPLATES, "src/templates")
    if SRC_TEMPLATES.exists():
        html_files = sorted(SRC_TEMPLATES.glob("*.html"))
        print(f"  html files: {len(html_files)}")
        for f in html_files:
            print(f"    - {f.name}")


def check_miniprogram() -> None:
    print("\n[3/4] miniprogram")
    require_dir(MINIPROGRAM, "miniprogram")
    for sub in ("pages", "components", "utils", "images"):
        p = MINIPROGRAM / sub
        if p.exists():
            print(f"  ✓ {sub}/")
        else:
            ISSUES.append(f"MISSING: miniprogram/{sub}")
            print(f"  ✗ {sub}/ missing")


def check_mounts() -> None:
    print("\n[4/4] expected mounts (src/app.py)")
    print("  /static -> src/static")
    print("  /photos -> settings.UPLOAD_FOLDER (absolute)")
    print("  /assets -> src/assets")
    print("  templates -> src/templates")


def main() -> int:
    print("=== Frontend Path Check ===")
    check_static()
    check_templates()
    check_miniprogram()
    check_mounts()

    print("\n=== SUMMARY ===")
    if ISSUES:
        for item in ISSUES:
            print(f"- {item}")
        print(f"Found {len(ISSUES)} issue(s).")
        return 1
    print("All frontend paths look good.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
