cmake_minimum_required(VERSION 3.10)
project(Adventure550 C)

include(CTest)

# Compiler identification
message(STATUS "Compiler: ${CMAKE_C_COMPILER_ID}")
message(STATUS "Compiler Version: ${CMAKE_C_COMPILER_VERSION}")
message(STATUS "System: ${CMAKE_SYSTEM_NAME}")

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# MSVC-specific configuration
if(MSVC)
    message(STATUS "Configuring for MSVC environment")
    # Use static runtime for better portability
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
    # Ensure proper Windows subsystem
    set(CMAKE_WIN32_EXECUTABLE FALSE)
endif()

# Directory structure
set(SRC_DIR ${CMAKE_SOURCE_DIR}/src)
set(INCLUDE_DIR ${CMAKE_SOURCE_DIR}/include)

# Source files
set(SOURCES
    ${SRC_DIR}/main.c
    ${SRC_DIR}/init.c
    ${SRC_DIR}/actions1.c
    ${SRC_DIR}/actions2.c
    ${SRC_DIR}/score.c
    ${SRC_DIR}/misc.c
    ${SRC_DIR}/datime.c
)

add_executable(adventure ${SOURCES})

target_include_directories(adventure 
    PRIVATE 
        ${INCLUDE_DIR}
        ${CMAKE_SOURCE_DIR}  # For backward compatibility with data files
)

# Platform-specific definitions
if(WIN32)
    target_compile_definitions(adventure PRIVATE 
        _CRT_SECURE_NO_WARNINGS
        _CRT_NONSTDC_NO_DEPRECATE
    )
endif()

# Compiler-specific flags
if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    message(STATUS "Applying GCC/Clang warning flags")
    target_compile_options(adventure PRIVATE -Wall -Wextra -pedantic)
    # Legacy FORTRAN-translated sources intentionally retain labels/goto structure.
    target_compile_options(adventure PRIVATE -Wno-unused-label -Wno-missing-braces)
elseif(MSVC)
    message(STATUS "Applying MSVC warning flags and options")
    # Remove default /W3 and apply /W4
    string(REPLACE "/W3" "" CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
    target_compile_options(adventure PRIVATE 
        /W4                    # Warning level 4
        /wd4102               # Unreferenced label (expected in FORTRAN-translated code)
        /wd4244               # Conversion warnings (expected in legacy code)
        /utf-8                # Set source and execution character sets to UTF-8
    )
    # MSVC-specific definitions
    target_compile_definitions(adventure PRIVATE
        _CONSOLE
    )
endif()

if(BUILD_TESTING)
    add_test(
        NAME smoke.startup
        COMMAND ${CMAKE_COMMAND}
            -DADVENTURE_EXE=$<TARGET_FILE:adventure>
            -DADVENTURE_CWD=${CMAKE_SOURCE_DIR}
            -DADVENTURE_INPUT=${CMAKE_SOURCE_DIR}/tests/empty_input.txt
            -P ${CMAKE_SOURCE_DIR}/cmake/RunSmokeTest.cmake
    )

    add_test(
        NAME smoke.parser_score_quit
        COMMAND ${CMAKE_COMMAND}
            -DADVENTURE_EXE=$<TARGET_FILE:adventure>
            -DADVENTURE_CWD=${CMAKE_SOURCE_DIR}
            -DADVENTURE_INPUT=${CMAKE_SOURCE_DIR}/tests/score_quit_input.txt
            -DEXPECT_TEXT_1=Initialising
            -DEXPECT_TEXT_2=You\ have\ garnered
            -P ${CMAKE_SOURCE_DIR}/cmake/RunScriptedGameTest.cmake
    )

    add_test(
        NAME smoke.save_resume_roundtrip
        COMMAND ${CMAKE_COMMAND}
            -DADVENTURE_EXE=$<TARGET_FILE:adventure>
            -DADVENTURE_CWD=${CMAKE_SOURCE_DIR}
            -DSAVE_INPUT=${CMAKE_SOURCE_DIR}/tests/save_session_input.txt
            -DRESUME_INPUT=${CMAKE_SOURCE_DIR}/tests/resume_session_input.txt
            -DSAVE_FILE=${CMAKE_SOURCE_DIR}/test-savegame.dat
            -P ${CMAKE_SOURCE_DIR}/cmake/RunSaveResumeTest.cmake
    )

    add_test(
        NAME smoke.inventory_roundtrip
        COMMAND ${CMAKE_COMMAND}
            -DADVENTURE_EXE=$<TARGET_FILE:adventure>
            -DADVENTURE_CWD=${CMAKE_SOURCE_DIR}
            -DADVENTURE_INPUT=${CMAKE_SOURCE_DIR}/tests/inventory_roundtrip_input.txt
            -DEXPECT_TEXT_1=You\ are\ inside\ a\ building
            -DEXPECT_TEXT_2=Brass\ lantern
            -DEXPECT_TEXT_3=You\'re\ not\ carrying\ anything.
            -P ${CMAKE_SOURCE_DIR}/cmake/RunScriptedGameTest.cmake
    )

    add_test(
        NAME smoke.cross_room_inventory_persistence
        COMMAND ${CMAKE_COMMAND}
            -DADVENTURE_EXE=$<TARGET_FILE:adventure>
            -DADVENTURE_CWD=${CMAKE_SOURCE_DIR}
            -DADVENTURE_INPUT=${CMAKE_SOURCE_DIR}/tests/cross_room_inventory_input.txt
            -DEXPECT_TEXT_1=You\ are\ inside\ a\ building
            -DEXPECT_TEXT_2=You\'re\ in\ front\ of\ building.
            -DEXPECT_TEXT_3=Set\ of\ keys
            -P ${CMAKE_SOURCE_DIR}/cmake/RunScriptedGameTest.cmake
    )

    add_test(
        NAME smoke.map1_surface_route
        COMMAND ${CMAKE_COMMAND}
            -DADVENTURE_EXE=$<TARGET_FILE:adventure>
            -DADVENTURE_CWD=${CMAKE_SOURCE_DIR}
            -DADVENTURE_INPUT=${CMAKE_SOURCE_DIR}/tests/map1_surface_route_input.txt
            -DEXPECT_TEXT_1=You\ are\ inside\ a\ building
            -DEXPECT_TEXT_2=You\'re\ in\ front\ of\ building.
            -DEXPECT_TEXT_3=You\ have\ walked\ up\ a\ hill
            -DEXPECT_TEXT_4=You\'re\ in\ front\ of\ building.
            -P ${CMAKE_SOURCE_DIR}/cmake/RunScriptedGameTest.cmake
    )

    add_test(
        NAME smoke.take_all_drop_all
        COMMAND ${CMAKE_COMMAND}
            -DADVENTURE_EXE=$<TARGET_FILE:adventure>
            -DADVENTURE_CWD=${CMAKE_SOURCE_DIR}
            -DADVENTURE_INPUT=${CMAKE_SOURCE_DIR}/tests/take_all_drop_all_input.txt
            -DEXPECT_TEXT_1=You\ are\ inside\ a\ building
            -DEXPECT_TEXT_2=Set\ of\ keys
            -DEXPECT_TEXT_3=Brass\ lantern
            -DEXPECT_TEXT_4=You\'re\ not\ carrying\ anything.
            -P ${CMAKE_SOURCE_DIR}/cmake/RunScriptedGameTest.cmake
    )

    add_test(
        NAME regression.score_ruleset_current
        COMMAND ${CMAKE_COMMAND}
            -DADVENTURE_EXE=$<TARGET_FILE:adventure>
            -DADVENTURE_CWD=${CMAKE_SOURCE_DIR}
            -DADVENTURE_INPUT=${CMAKE_SOURCE_DIR}/tests/map1_surface_route_input.txt
            -DEXPECT_FINAL_SCORE=32
            -DEXPECT_MAX_SCORE=430
            -DEXPECT_TURNS=5
            -P ${CMAKE_SOURCE_DIR}/cmake/RunScoreRegression.cmake
    )
endif()
