# Build instructions for Adventure550 with CMake and Ninja

## Prerequisites
- CMake 3.10 or newer
- Ninja build system
- Modern C compiler (gcc, clang, etc.)

## Steps

1. Open a terminal in the project directory.
2. Create a build directory:
   
   mkdir build
   cd build

3. Run CMake with Ninja:
   
   cmake -G Ninja ..

4. Build the project:
   
   ninja

5. Run the application:
   
   ./adventure   (or adventure.exe on Windows)
