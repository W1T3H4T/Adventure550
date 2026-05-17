# Refactoring Task List for Adventure550

## Issues Detected

1. **Missing Standard Headers** (Completed)
   - [x] Functions like `calloc`, `exit`, and `printf` are used without including `<stdlib.h>` or `<stdio.h>`.
   - Resolved: Added `#include <stdio.h>` and `#include <stdlib.h>` to all main source files (main.c, actions1.c, actions2.c, score.c, datime.c).
2. **Implicit `int` Return Types** (Completed)
   - [x] Added explicit return types and modern prototypes across refactored files.
   - [x] Resolved implicit function declaration errors by adding prototypes.
   - [x] Addressed `sys/time.h` portability in `datime.c` using Windows-safe conditional compilation.
3. **Deprecated Function Prototypes** (Completed)
   - [x] Converted empty-parenthesis declarations to `(void)` where appropriate.
4. **K&R-Style Function Definitions** (Completed in core runtime files)
   - [x] Converted K&R definitions in key files (notably `misc.c`, `init.c`, and action files) to ANSI C-style signatures.
5. **Unused Labels** (Deferred / Non-functional)
   - [ ] Legacy translated labels remain in several files; warning noise is suppressed in CMake for Clang/GCC.

## Logical Next Steps

1. **Add Standard Headers** (Completed)
   - [x] `<stdio.h>` and `<stdlib.h>` added to all source files using standard library functions.
2. **Update Function Declarations/Definitions** (Completed)
   - [x] Explicit return types applied in modernized units.
   - [x] Missing prototypes added/updated in headers and source.
   - [x] Empty parenthesis declarations converted to `(void)` where applicable.
3. **Modernize Function Definitions** (Completed for active build path)
   - [x] K&R-style definitions migrated to ANSI C prototypes in core files.
4. **Address sys/time.h Error** (Completed)
   - [x] Added platform conditional handling in `datime.c`.
5. **Clean Up Labels** (Optional)
   - [ ] Optional deep cleanup: remove legacy labels and reduce `goto` usage without changing behavior.
6. **CTest Integration**
   - [x] Added a non-interactive `smoke.startup` CTest to validate executable startup/exit.
   - [x] Added parser regression (`smoke.parser_score_quit`).
   - [x] Added save/resume roundtrip regression (`smoke.save_resume_roundtrip`).
   - [x] Added inventory state mutation regression (`smoke.inventory_roundtrip`).
   - [x] Added cross-room inventory persistence regression (`smoke.cross_room_inventory_persistence`).
   - [x] Added map-derived surface route regression (`smoke.map1_surface_route`).
   - [x] Added score ruleset regression pinned to current code-defined maximum (`regression.score_ruleset_current`: 32/430 in 5 turns).
   - [ ] Expand with deeper cave-travel and puzzle-state regressions.

7. **Map Documentation** (Completed)
   - [x] Converted image maps in `maps/` to Mermaid model document (`maps/adventure-maps-mermaid.md`).
   - [x] Linked regression design to documented map routes.
8. **Rebuild and Test** (In Progress)
   - [x] Build now succeeds with CMake + Ninja on Windows Clang toolchain.
   - [x] CTest smoke framework integrated into CMake.
   - [x] Current CTest suite passing (6/6 tests).
   - [ ] Add CTest execution to CI/local automation.

9. **Runtime Data I/O Portability** (Completed)
   - [x] Fixed binary/text file mode mismatch on Windows (`READ_MODE` / `WRITE_MODE`) to prevent corrupted save/data reads.

10. **550-Point Regression Goal** (Blocked)

- [ ] Create a full-cave traversal regression that ends at 550 points.
- Blocker: current game/data reports maximum possible score of 430 (as emitted by runtime scoring output), so a 550-point assertion cannot pass without migrating scoring/data to the 550-point ruleset.

1. **Current Ruleset Regression** (Completed)

- [x] Added score regression aligned to in-code scoring model (430 max) with deterministic map-derived route.

---

_This file will be updated as issues are resolved or new issues are discovered during the refactor process._
