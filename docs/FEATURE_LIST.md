# Feature List

## Build and Tooling

- CMake-based build system with Ninja support.
- CTest regression suite for deterministic gameplay and scoring checks.
- Python installer script: tools/install.py.
- Cross-platform build support for Windows, Linux, and macOS.
- Cross-platform installation into a target directory with runtime files.

## Testing Coverage

- Startup smoke validation.
- Parser and score command regression.
- Save/resume roundtrip regression.
- Inventory and cross-room state persistence regressions.
- Map-derived route regression.
- Current ruleset score regression (max score: 430).
