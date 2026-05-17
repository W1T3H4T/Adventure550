# Header Files

This directory contains all header files for Adventure550.

## Files

- **funcs.h** - Function declarations
- **main.h** - Main program declarations
- **misc.h** - Miscellaneous function declarations and macros
- **share.h** - Shared global variable declarations (legacy FORTRAN common blocks)

These headers are included by the source files in the `../src/` directory.

## Note on Legacy Code

Many of the global variables declared in `share.h` originate from FORTRAN common blocks
in the original 1970s Adventure game implementation. The code style reflects this heritage.
