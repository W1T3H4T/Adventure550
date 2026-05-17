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
    RESULT_VARIABLE adventure_result
    OUTPUT_VARIABLE adventure_stdout
    ERROR_VARIABLE adventure_stderr
    TIMEOUT 20
)

if(NOT adventure_result EQUAL 0)
    string(REPLACE "\n" "\\n" escaped_stdout "${adventure_stdout}")
    string(REPLACE "\n" "\\n" escaped_stderr "${adventure_stderr}")
    message(FATAL_ERROR "smoke.startup failed with exit code ${adventure_result}; stdout=${escaped_stdout}; stderr=${escaped_stderr}")
endif()
