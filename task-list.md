# Refactoring Task List for Adventure550

## Issues Detected


1. **Missing Standard Headers** (Completed)
   - [x] Functions like `calloc`, `exit`, and `printf` are used without including `<stdlib.h>` or `<stdio.h>`.
   - Resolved: Added `#include <stdio.h>` and `#include <stdlib.h>` to all main source files (main.c, actions1.c, actions2.c, score.c, datime.c).
2. **Implicit `int` Return Types** (In Progress)
   - [ ] Many functions (including `main`) are declared/defined without explicit return types, causing `-Wimplicit-int` errors.
   - [ ] Implicit function declarations (`-Wimplicit-function-declaration`) due to missing prototypes.
   - [ ] Fatal error: `sys/time.h` not found in `datime.c` (may require conditional compilation or removal).
3. **Deprecated Function Prototypes**
   - [ ] Function declarations use empty parentheses (e.g., `void fTYPE0();`) instead of `(void)`.
4. **K&R-Style Function Definitions**
   - [ ] Parameter types are declared after the parameter list, not in the signature.
5. **Unused Labels**
   - [ ] Several labels (e.g., `L6001`) are defined but never used.

## Logical Next Steps

1. **Add Standard Headers** (Completed)
   - [x] `<stdio.h>` and `<stdlib.h>` added to all source files using standard library functions.
2. **Update Function Declarations/Definitions** (In Progress)
   - [ ] Add explicit return types to all functions.
   - [ ] Add missing function prototypes to header files as needed.
   - [ ] Change all function declarations with empty parentheses to use `(void)` for no-argument functions.
3. **Modernize Function Definitions**
   - [ ] Refactor K&R-style definitions to ANSI C prototypes (move parameter types into the signature).
4. **Address sys/time.h Error**
   - [ ] Use conditional compilation or remove sys/time.h from datime.c if not needed.
5. **Clean Up Labels**
   - [ ] Remove or refactor unused labels and minimize `goto` usage where possible.
6. **CTest Integration**
   - [ ] Generate CTest tests for modules and files as part of the modernization process.
7. **Rebuild and Test**
   - [ ] Rebuild after each major change and address any new warnings or errors.

---

_This file will be updated as issues are resolved or new issues are discovered during the refactor process._
