# Adventure550

A modernized port of the classic **Colossal Cave Adventure** text adventure game, originally developed by Will Crowther and Don Woods in the 1970s. 
This version is refactored from [Adventure550](https://github.com/keidroid/Adventure550), which was ported from the original FORTRAN code to C11 with 
a modern CMake build system.

## Features

- **Cross-platform support** - Windows, Linux, and macOS
- **Modern build system** - CMake with Ninja generator
- **Comprehensive test suite** - 8 automated CTest regression tests
- **Multiple compiler support** - MSVC, GCC, and Clang
- **Clean code organization** - Separate `src/` and `include/` directories
- **Save/resume functionality** - Save your game progress and continue later
- **Original gameplay** - Faithful to the classic 550-point Adventure experience
	-  **Note** This version retains the original 430-point maximum score, as the 550 points in the title refer to the original expansion from 350 to 550 points by Don Woods, not the actual maximum score.
		Future work will explore adding the missing 120 points to reach the full 550-point or perhaps the 770-point experience.

## Quick Start

### Prerequisites

- **CMake** 3.10 or newer
- **Ninja** build system
- **C Compiler:**
  - Windows: MSVC (Visual Studio 2019+), GCC, or Clang
  - Linux/macOS: GCC, Clang, or any C11-compliant compiler
- **Python** 3.8+ (optional, for installation script)

### Building

```bash
# Clone the repository
git clone https://github.com/W1T3H4T/Adventure550.git
cd Adventure550

# Create build directory and configure
mkdir build
cd build
cmake -G Ninja ..

# Build the project
cmake --build .

# Run tests (optional)
ctest --output-on-failure
```

### Running the Game

From the project root directory:

```bash
./build/adventure
```

Or use the installer to set up a permanent installation:

```bash
python tools/install.py --overwrite
```

## Project Structure

```
Adventure550/
├── src/              # C source files
│   ├── main.c        # Main game loop
│   ├── init.c        # Initialization and save/load
│   ├── actions1.c    # Action handlers (part 1)
│   ├── actions2.c    # Action handlers (part 2)
│   ├── score.c       # Scoring system
│   ├── misc.c        # Utility functions
│   └── datime.c      # Date/time compatibility
├── include/          # Header files
│   ├── funcs.h       # Function declarations
│   ├── main.h        # Main program declarations
│   ├── misc.h        # Utility declarations
│   └── share.h       # Global variable declarations
├── cmake/            # CMake test scripts
├── docs/             # Documentation
│   ├── BUILD_INSTRUCTIONS.md
│   └── FEATURE_LIST.md
├── tests/            # Test input files
├── tools/            # Build and installation tools
├── adventure.text    # Game data file
└── CMakeLists.txt    # CMake configuration
```

## Documentation

- **[Build Instructions](docs/BUILD_INSTRUCTIONS.md)** - Detailed build and installation guide
- **[Feature List](docs/FEATURE_LIST.md)** - Complete feature documentation
- **[Mermaid Viewing Guide](docs/MERMAID_VIEWING_GUIDE.md)** - How to view map diagrams (Visual Studio doesn't render Mermaid)
- **[Cave Maps](docs/Colossal%20Cave%20Adventure.md)** - Game map overview and GIF images

## Testing

The project includes comprehensive automated tests:

```bash
cd build
ctest --output-on-failure
```

**Test Coverage:**
- Startup validation
- Parser and command processing
- Save/resume game state
- Inventory management
- Map navigation
- Score regression testing

All tests must pass before commits are accepted.

## Installation

### Platform-Specific Installation

The Python installer handles cross-platform deployment:

```bash
# Install to platform default location
python tools/install.py --overwrite

# Install to custom directory
python tools/install.py --target-dir /path/to/install --overwrite
```

**Default Install Locations:**
- **Windows:** `%LOCALAPPDATA%\Adventure550`
- **Linux/macOS:** `$XDG_CONFIG_HOME/adventure550`

The installer automatically:
- Detects Visual Studio build directories
- Copies the executable and game data
- Creates platform-appropriate launcher scripts

## Development

### Building with Visual Studio

The project includes `CMakeSettings.json` for Visual Studio integration:

1. Open the folder in Visual Studio
2. Visual Studio will auto-configure CMake
3. Build using the CMake menu or Ctrl+B

Build output: `out/build/<config>/adventure.exe`

### Compiler Configuration

The CMake system automatically configures compiler-specific settings:

**MSVC:**
- Warning level `/W4`
- UTF-8 source encoding
- Static runtime for portability
- Suppresses legacy code warnings

**GCC/Clang:**
- Flags: `-Wall -Wextra -pedantic`
- Suppresses warnings for FORTRAN-legacy patterns

## Game Commands

Basic commands to get started:

- `n`, `s`, `e`, `w` - Navigate (north, south, east, west)
- `take [object]` - Pick up an item
- `drop [object]` - Drop an item
- `inventory` - Show what you're carrying
- `look` - Examine your surroundings
- `save` - Save your game
- `quit` - Exit the game

Type `help` in-game for more commands.

## Contributing

This is a fork of the upstream repository. To contribute:

1. Fork from upstream: `https://github.com/keidroid/Adventure550`
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass: `ctest --output-on-failure`
5. Ensure clean build with no warnings
6. Submit a pull request

## History

**Colossal Cave Adventure** is one of the earliest and most influential text adventure games:

- **1976** - Original version by Will Crowther (350 points)
- **1977** - Expanded by Don Woods (550 points) - this version
- **1970s-80s** - Various ports and adaptations
- **This port** - Modern C11 implementation with CMake build system

The code retains many original FORTRAN conventions (global variables, goto statements) as a historical artifact of its translation from the 1970s source.

## License

This version of Adventure was developed by Don Woods on private equipment and has been ported for entertainment purposes. Don Woods retains full rights to the work.

## Acknowledgments

- **Will Crowther** - Original Adventure creator
- **Don Woods** - 550-point expansion
- **keidroid** - Upstream maintainer
- All contributors to this and previous ports

---

**Current Version:** 550-point Adventure  
**Maximum Score:** 430 points  
**Language Standard:** C11  
**Build System:** CMake 3.10+
