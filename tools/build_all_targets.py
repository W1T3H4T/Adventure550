#!/usr/bin/env python3
"""Build Adventure550 CMake targets, with optional clean step.

Examples:
  python tools/build_all_targets.py
  python tools/build_all_targets.py --clean
  python tools/build_all_targets.py --clean --config Release --parallel 8
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


CONFIG_CHOICES = ["Debug", "Release", "RelWithDebInfo", "MinSizeRel"]


def run_cmd(cmd: list[str], cwd: Path) -> None:
    print("+", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(cwd), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def add_build_common_args(cmd: list[str], config: str | None, parallel: int | None) -> None:
    if config:
        cmd.extend(["--config", config])
    if parallel and parallel > 0:
        cmd.extend(["--parallel", str(parallel)])


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Build all CMake targets for Adventure550, optionally cleaning first."
    )
    parser.add_argument(
        "--source-dir",
        default=str(repo_root),
        help="Project source directory (default: repository root).",
    )
    parser.add_argument(
        "--build-dir",
        default="build",
        help="Build directory (default: build).",
    )
    parser.add_argument(
        "--config",
        choices=CONFIG_CHOICES,
        default=None,
        help="Build config for multi-config generators (e.g. Visual Studio).",
    )
    parser.add_argument(
        "--target",
        default="all",
        help="Target to build (default: all).",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Run clean target before building.",
    )
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Run clean target and exit.",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=None,
        help="Parallel build jobs passed to cmake --build.",
    )
    parser.add_argument(
        "--cmake",
        default="cmake",
        help="CMake executable path/name (default: cmake).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    source_dir = Path(args.source_dir).resolve()
    build_dir = Path(args.build_dir)
    if not build_dir.is_absolute():
        build_dir = (source_dir / build_dir).resolve()

    if not source_dir.is_dir():
        print(f"Error: source directory not found: {source_dir}", file=sys.stderr)
        return 1

    # Auto-configure if missing.
    cache = build_dir / "CMakeCache.txt"
    if not cache.is_file():
        build_dir.mkdir(parents=True, exist_ok=True)
        run_cmd([args.cmake, "-S", str(source_dir), "-B", str(build_dir)], cwd=source_dir)

    if args.clean or args.clean_only:
        clean_cmd = [args.cmake, "--build", str(build_dir), "--target", "clean"]
        add_build_common_args(clean_cmd, args.config, args.parallel)
        run_cmd(clean_cmd, cwd=source_dir)

    if args.clean_only:
        print("Clean complete.")
        return 0

    build_cmd = [args.cmake, "--build", str(build_dir), "--target", args.target]
    add_build_common_args(build_cmd, args.config, args.parallel)
    run_cmd(build_cmd, cwd=source_dir)

    print(f"Build complete: target '{args.target}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
