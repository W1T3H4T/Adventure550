# Build instructions for Adventure550 with CMake and Ninja

See FEATURE_LIST.md for current supported features.

## Project Structure

```
Adventure550/
??? src/              # C source files
?   ??? main.c
?   ??? init.c
?   ??? actions1.c
?   ??? actions2.c
?   ??? score.c
?   ??? misc.c
?   ??? datime.c
??? include/          # Header files
?   ??? funcs.h
?   ??? main.h
?   ??? misc.h
?   ??? share.h
??? cmake/            # CMake test scripts
??? docs/             # Documentation
??? tests/            # Test input files
??? tools/            # Build and install tools
??? CMakeLists.txt    # CMake build configuration
```

## Prerequisites

- CMake 3.10 or newer
- Ninja build system
- Modern C compiler:
  - **Windows**: MSVC (Visual Studio 2019 or newer), gcc, or clang
  - **Linux/macOS**: gcc, clang, or other C11-compliant compiler
- Python 3.8 or newer (for tools/install.py)

## Platform Support

- Windows
- Linux
- macOS

## Build

### Standard Build (All Platforms)

1. Open a terminal in the project directory.
2. Create a build directory:

   ```
   mkdir build
   cd build
   ```

3. Run CMake with Ninja:

   ```
   cmake -G Ninja ..
   ```

   The CMake configuration will automatically detect your compiler:
   - **MSVC**: Applies Windows-specific flags and disables warnings for legacy FORTRAN code
   - **GCC/Clang**: Applies `-Wall -Wextra -pedantic` with exceptions for legacy code patterns

4. Build the project:

   ```
   ninja
   ```

   Or using CMake's build wrapper:

   ```
   cmake --build .
   ```

5. Run tests with CTest:

   ```
   ctest --output-on-failure
   ```

### Windows-Specific Notes (MSVC)

When building with MSVC (cl.exe), the CMake configuration:
- Automatically detects the MSVC environment
- Sets `/W4` warning level
- Disables `/wd4102` (unreferenced labels) and `/wd4244` (type conversions) for legacy code
- Configures UTF-8 source encoding
- Uses static runtime for better portability

You can verify MSVC detection by checking the configuration output:
```
-- Compiler: MSVC
-- Compiler Version: 19.x.xxxxx.x
-- Configuring for MSVC environment
-- Applying MSVC warning flags and options
```

## Install (Python)

1. Open a terminal in the project directory.
2. Ensure the project has already been built.
3. Install product files into a target directory:

   **Default installation** (uses platform-specific directory):
   ```
   python tools/install.py --overwrite
   ```

   **Custom installation directory**:
   ```
   python tools/install.py --target-dir ./dist/adventure550 --overwrite
   ```

The installer:
- **Auto-detects** Visual Studio CMake build directories (`out/build/x64-Debug`, etc.)
- Falls back to standard `build` directory if present
- Copies the compiled executable and required runtime data (`adventure.text`)
- Creates platform-appropriate launcher scripts (`run_adventure.cmd` on Windows, `run_adventure.sh` on Linux/macOS)

**Platform default install locations:**
- **Windows**: `%LOCALAPPDATA%\Adventure550`
- **Linux/macOS**: `$XDG_CONFIG_HOME/adventure550`

**Explicit build directory** (if auto-detection fails):
```
python tools/install.py --build-dir out/build/x64-Debug --overwrite
```
