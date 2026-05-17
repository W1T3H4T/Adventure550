#!/usr/bin/env python3
"""Cross-platform installer for Adventure550.

Installs the compiled executable and all required runtime data files into the
platform-appropriate user application directory, or an explicitly supplied
target directory.

Platform defaults (when --target-dir is not given):
  Windows  : %LOCALAPPDATA%\\Adventure550
  Linux    : $XDG_CONFIG_HOME/adventure550   (if XDG_CONFIG_HOME is set)
  macOS    : $XDG_CONFIG_HOME/adventure550   (if XDG_CONFIG_HOME is set)

If XDG_CONFIG_HOME is not set on Linux/macOS and --target-dir is not given,
the installer will prompt for an install path interactively.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "Adventure550"
APP_DIR_NAME = "adventure550"
EXECUTABLE_NAMES = ["adventure.exe", "adventure"]

# Required runtime files relative to source root.
REQUIRED_DATA = ["adventure.text"]
# Optional runtime files: copied when present.
OPTIONAL_DATA = ["adventure.data"]


# ---------------------------------------------------------------------------
# Platform helpers
# ---------------------------------------------------------------------------

def default_install_dir() -> Path | None:
    """Return the platform-default install directory, or None if undetermined."""
    if os.name == "nt":
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            return Path(local_appdata) / APP_NAME
        return None

    # Linux and macOS: honour XDG_CONFIG_HOME when set.
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / APP_DIR_NAME

    return None


def prompt_install_dir() -> Path:
    """Interactively ask the user for an install directory."""
    try:
        raw = input(
            "XDG_CONFIG_HOME is not set. Enter the install directory: "
        ).strip()
    except EOFError:
        print("\nError: no install directory provided and stdin is not a terminal.",
              file=sys.stderr)
        raise SystemExit(1)
    if not raw:
        print("Error: empty path is not valid.", file=sys.stderr)
        raise SystemExit(1)
    return Path(raw).expanduser().resolve()


# ---------------------------------------------------------------------------
# Executable discovery
# ---------------------------------------------------------------------------

def find_executable(build_dir: Path, config: str | None) -> Path | None:
    candidate_dirs: list[Path] = [build_dir]
    if config:
        candidate_dirs.extend([build_dir / config, build_dir / "bin" / config])
    candidate_dirs.append(build_dir / "bin")

    for folder in candidate_dirs:
        for name in EXECUTABLE_NAMES:
            candidate = folder / name
            if candidate.is_file():
                return candidate

    # Fallback: recursive search.
    for name in EXECUTABLE_NAMES:
        matches = list(build_dir.rglob(name))
        if matches:
            return matches[0]

    return None


# ---------------------------------------------------------------------------
# Runtime dependency resolution
# ---------------------------------------------------------------------------

def collect_shared_libs_windows(exe: Path) -> list[Path]:
    """Collect non-system DLLs from a Windows executable via dumpbin /DEPENDENTS."""
    system32 = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32"
    syswow64 = system32.parent / "SysWOW64"
    skip_prefixes = ("api-ms-", "ext-ms-")

    if not shutil.which("dumpbin"):
        return []

    try:
        result = subprocess.run(
            ["dumpbin", "/DEPENDENTS", str(exe)],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError:
        return []

    deps: list[Path] = []
    for line in result.stdout.splitlines():
        name = line.strip()
        if not name.lower().endswith(".dll"):
            continue
        if any(name.lower().startswith(p) for p in skip_prefixes):
            continue
        # Skip DLLs found in system directories.
        if (system32 / name).is_file() or (syswow64 / name).is_file():
            continue
        # Look next to the executable first.
        candidate = exe.parent / name
        if candidate.is_file():
            deps.append(candidate)

    return deps


def collect_shared_libs_posix(exe: Path) -> list[Path]:
    """Collect non-system shared libs via ldd (Linux) or otool -L (macOS)."""
    is_mac = sys.platform == "darwin"

    if is_mac:
        if not shutil.which("otool"):
            return []
        try:
            result = subprocess.run(
                ["otool", "-L", str(exe)],
                capture_output=True, text=True, check=True,
            )
        except subprocess.CalledProcessError:
            return []
        raw_paths = [
            line.strip().split()[0]
            for line in result.stdout.splitlines()[1:]
            if line.strip()
        ]
    else:
        if not shutil.which("ldd"):
            return []
        try:
            result = subprocess.run(
                ["ldd", str(exe)],
                capture_output=True, text=True, check=True,
            )
        except subprocess.CalledProcessError:
            return []
        raw_paths = []
        for line in result.stdout.splitlines():
            parts = line.split("=>")
            if len(parts) == 2:
                path_part = parts[1].split("(")[0].strip()
                if path_part and path_part != "not found":
                    raw_paths.append(path_part)

    skip_prefixes = (
        "/lib/", "/lib64/", "/usr/lib/", "/usr/lib64/",
        "/System/", "/usr/", "@rpath/", "@executable_path/",
    )
    deps: list[Path] = []
    for raw in raw_paths:
        p = Path(raw)
        if not p.is_file():
            continue
        if any(raw.startswith(prefix) for prefix in skip_prefixes):
            continue
        deps.append(p)

    return deps


def collect_runtime_deps(exe: Path) -> list[Path]:
    """Return a list of non-system shared libraries to bundle alongside the exe."""
    if os.name == "nt":
        return collect_shared_libs_windows(exe)
    return collect_shared_libs_posix(exe)


# ---------------------------------------------------------------------------
# Launcher generation
# ---------------------------------------------------------------------------

def write_launcher(target_dir: Path, exe_name: str) -> None:
    if os.name == "nt":
        launcher = target_dir / "run_adventure.cmd"
        launcher.write_text(
            "@echo off\n"
            "set SCRIPT_DIR=%~dp0\n"
            "pushd \"%SCRIPT_DIR%\"\n"
            f"\"%SCRIPT_DIR%{exe_name}\"\n"
            "set RC=%ERRORLEVEL%\n"
            "popd\n"
            "exit /b %RC%\n",
            encoding="utf-8",
        )
    else:
        launcher = target_dir / "run_adventure.sh"
        launcher.write_text(
            "#!/usr/bin/env sh\n"
            "set -eu\n"
            'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"\n'
            'cd "$SCRIPT_DIR"\n'
            f'exec "./{exe_name}"\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install Adventure550 into the platform-appropriate user directory.\n\n"
            "Defaults:\n"
            "  Windows  : %%LOCALAPPDATA%%\\Adventure550\n"
            "  Linux/macOS : $XDG_CONFIG_HOME/adventure550 (prompt if unset)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--source-dir",
        default=str(Path(__file__).resolve().parents[1]),
        help="Project source directory (default: repository root).",
    )
    parser.add_argument(
        "--build-dir",
        default="build",
        help="Build directory containing compiled executable (default: build).",
    )
    parser.add_argument(
        "--target-dir",
        default=None,
        help=(
            "Override install destination. "
            "If omitted, the platform default is used or the user is prompted."
        ),
    )
    parser.add_argument(
        "--config",
        default=None,
        choices=["Debug", "Release", "RelWithDebInfo", "MinSizeRel"],
        help="Build configuration subdirectory to search first.",
    )
    parser.add_argument(
        "--no-deps",
        action="store_true",
        help="Skip bundling of runtime shared library dependencies.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing install directory.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    source_dir = Path(args.source_dir).resolve()
    build_dir = (
        Path(args.build_dir).resolve()
        if Path(args.build_dir).is_absolute()
        else Path(args.build_dir)
    )

    # Resolve build_dir relative to source when given as a bare name.
    if not build_dir.is_dir():
        alt = source_dir / args.build_dir
        if alt.is_dir():
            build_dir = alt
        else:
            # Check common Visual Studio CMake output patterns.
            vs_patterns = [
                "out/build/x64-Debug",
                "out/build/x64-Release",
                "out/build/x86-Debug",
                "out/build/x86-Release",
                "out/build",
            ]
            for pattern in vs_patterns:
                vs_build = source_dir / pattern
                if vs_build.is_dir():
                    build_dir = vs_build
                    print(f"Auto-detected Visual Studio build directory: {build_dir}")
                    break

    # Determine target directory.
    if args.target_dir:
        target_dir = Path(args.target_dir).expanduser().resolve()
    else:
        target_dir = default_install_dir()
        if target_dir is None:
            target_dir = prompt_install_dir()
        else:
            print(f"Using platform default install directory: {target_dir}")

    # Validate prerequisites.
    if not source_dir.is_dir():
        print(f"Error: source directory not found: {source_dir}", file=sys.stderr)
        return 1
    if not build_dir.is_dir():
        print(
            f"Error: build directory not found: {build_dir}. "
            "Run cmake --build first.",
            file=sys.stderr,
        )
        return 1

    executable = find_executable(build_dir, args.config)
    if executable is None:
        print(
            "Error: compiled executable not found in build directory. "
            "Run cmake --build first.",
            file=sys.stderr,
        )
        return 1

    missing = [
        source_dir / f for f in REQUIRED_DATA
        if not (source_dir / f).is_file()
    ]
    if missing:
        for m in missing:
            print(f"Error: required runtime file missing: {m}", file=sys.stderr)
        return 1

    # Sanity-check existing target.
    if target_dir.exists():
        if not args.overwrite:
            print(
                f"Error: install directory already exists: {target_dir}\n"
                "Use --overwrite to replace it.",
                file=sys.stderr,
            )
            return 1
        shutil.rmtree(target_dir)

    target_dir.mkdir(parents=True)

    # Install executable.
    exe_dst = target_dir / executable.name
    print(f"  Installing executable : {exe_dst}")
    shutil.copy2(executable, exe_dst)

    # Set executable bit on POSIX.
    if os.name != "nt":
        exe_dst.chmod(exe_dst.stat().st_mode | 0o111)

    # Install required runtime data.
    for name in REQUIRED_DATA:
        src = source_dir / name
        dst = target_dir / name
        print(f"  Installing data       : {dst}")
        shutil.copy2(src, dst)

    # Install optional runtime data when present.
    for name in OPTIONAL_DATA:
        src = source_dir / name
        if src.is_file():
            dst = target_dir / name
            print(f"  Installing optional   : {dst}")
            shutil.copy2(src, dst)

    # Bundle runtime shared library dependencies.
    if not args.no_deps:
        deps = collect_runtime_deps(executable)
        for dep in deps:
            dst = target_dir / dep.name
            print(f"  Installing dependency : {dst}")
            shutil.copy2(dep, dst)

    # Write launcher script.
    write_launcher(target_dir, executable.name)

    print(f"\nInstall complete: {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
