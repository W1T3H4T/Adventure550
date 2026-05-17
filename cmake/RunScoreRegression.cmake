if(NOT DEFINED ADVENTURE_EXE)
    message(FATAL_ERROR "ADVENTURE_EXE is required")
endif()
if(NOT DEFINED ADVENTURE_CWD)
    message(FATAL_ERROR "ADVENTURE_CWD is required")
endif()
if(NOT DEFINED ADVENTURE_INPUT)
    message(FATAL_ERROR "ADVENTURE_INPUT is required")
endif()

execute_process(
    COMMAND "${ADVENTURE_EXE}"
    WORKING_DIRECTORY "${ADVENTURE_CWD}"
    INPUT_FILE "${ADVENTURE_INPUT}"
    RESULT_VARIABLE game_result
    OUTPUT_VARIABLE game_stdout
    ERROR_VARIABLE game_stderr
    TIMEOUT 30
)

if(NOT game_result EQUAL 0)
    message(FATAL_ERROR "score regression run failed: exit=${game_result}; stderr=${game_stderr}")
endif()

string(REGEX MATCH "You scored[ \t]+([0-9]+) out of a possible[ \t]+([0-9]+), using[ \t]+([0-9]+) turns\\." score_line "${game_stdout}")
if(score_line STREQUAL "")
    message(FATAL_ERROR "Could not find final score line in output")
endif()

set(final_score "${CMAKE_MATCH_1}")
set(max_score "${CMAKE_MATCH_2}")
set(turn_count "${CMAKE_MATCH_3}")

if(DEFINED EXPECT_FINAL_SCORE)
    if(NOT final_score STREQUAL "${EXPECT_FINAL_SCORE}")
        message(FATAL_ERROR "Final score mismatch: expected ${EXPECT_FINAL_SCORE}, got ${final_score}")
    endif()
endif()

if(DEFINED EXPECT_MAX_SCORE)
    if(NOT max_score STREQUAL "${EXPECT_MAX_SCORE}")
        message(FATAL_ERROR "Max score mismatch: expected ${EXPECT_MAX_SCORE}, got ${max_score}")
    endif()
endif()

if(DEFINED EXPECT_TURNS)
    if(NOT turn_count STREQUAL "${EXPECT_TURNS}")
        message(FATAL_ERROR "Turn count mismatch: expected ${EXPECT_TURNS}, got ${turn_count}")
    endif()
endif()
