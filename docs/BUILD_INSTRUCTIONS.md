# Build instructions for Adventure550 with CMake and Ninja

See FEATURE_LIST.md for current supported features.

## Prerequisites

- CMake 3.10 or newer
- Ninja build system
- Modern C compiler (gcc, clang, etc.)
- Python 3.8 or newer (for tools/install.py)

## Platform Support

- Windows
- Linux
- macOS

## Build

1. Open a terminal in the project directory.
2. Create a build directory:

   mkdir build
   cd build

3. Run CMake with Ninja:

   cmake -G Ninja ..

4. Build the project:

   ninja

5. Run tests with CTest:

   ctest --output-on-failure

## Install (Python)

1. Open a terminal in the project directory.
2. Ensure the project has already been built.
3. Install product files into a target directory:

   python tools/install.py --target-dir ./dist/adventure550 --overwrite

The installer copies the compiled executable and required runtime data
(`adventure.text`) and creates platform-appropriate launcher scripts in the
target directory.
