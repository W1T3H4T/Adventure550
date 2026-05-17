cmake_minimum_required(VERSION 3.10)
project(Adventure550 C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Source files
set(SOURCES
    main.c
    init.c
    actions1.c
    actions2.c
    score.c
    misc.c
    datime.c
)

add_executable(adventure ${SOURCES})

target_include_directories(adventure PRIVATE ${CMAKE_SOURCE_DIR})

target_compile_options(adventure PRIVATE -Wall -Wextra -pedantic)
