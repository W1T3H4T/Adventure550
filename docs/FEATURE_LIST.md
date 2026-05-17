# Feature List

## Project Organization

- Clean directory structure with separate `src/` and `include/` directories.
- Modular C source code organization.
- CMake-based build system with Ninja support.
- Cross-platform build support for Windows, Linux, and macOS.

## Build and Tooling

- CMake configuration with MSVC, GCC, and Clang compiler support.
- CTest regression suite for deterministic gameplay and scoring checks.
- Python installer script: tools/install.py with auto-detection of Visual Studio build directories.
- Cross-platform installation into a target directory with runtime files.

## Testing Coverage

- Startup smoke validation.
- Parser and score command regression.
- Save/resume roundtrip regression.
- Inventory and cross-room state persistence regressions.
- Map-derived route regression.
- Current ruleset score regression (max score: 430).
