if(NOT DEFINED ADVENTURE_EXE)
    message(FATAL_ERROR "ADVENTURE_EXE is required")
endif()
if(NOT DEFINED ADVENTURE_CWD)
    message(FATAL_ERROR "ADVENTURE_CWD is required")
endif()
if(NOT DEFINED SAVE_INPUT)
    message(FATAL_ERROR "SAVE_INPUT is required")
endif()
if(NOT DEFINED RESUME_INPUT)
    message(FATAL_ERROR "RESUME_INPUT is required")
endif()
if(NOT DEFINED SAVE_FILE)
    message(FATAL_ERROR "SAVE_FILE is required")
endif()

file(REMOVE "${SAVE_FILE}")

execute_process(
    COMMAND "${ADVENTURE_EXE}"
    WORKING_DIRECTORY "${ADVENTURE_CWD}"
    INPUT_FILE "${SAVE_INPUT}"
    RESULT_VARIABLE save_result
    OUTPUT_VARIABLE save_stdout
    ERROR_VARIABLE save_stderr
    TIMEOUT 20
)

if(NOT save_result EQUAL 0)
    message(FATAL_ERROR "save run failed: exit=${save_result}; stderr=${save_stderr}")
endif()

if(NOT EXISTS "${SAVE_FILE}")
    message(FATAL_ERROR "save file was not created: ${SAVE_FILE}")
endif()

execute_process(
    COMMAND "${ADVENTURE_EXE}"
    WORKING_DIRECTORY "${ADVENTURE_CWD}"
    INPUT_FILE "${RESUME_INPUT}"
    RESULT_VARIABLE resume_result
    OUTPUT_VARIABLE resume_stdout
    ERROR_VARIABLE resume_stderr
    TIMEOUT 20
)

if(NOT resume_result EQUAL 0)
    message(FATAL_ERROR "resume run failed: exit=${resume_result}; stderr=${resume_stderr}")
endif()

string(FIND "${resume_stdout}" "File name" file_prompt_pos)
if(file_prompt_pos EQUAL -1)
    message(FATAL_ERROR "resume output did not contain file prompt")
endif()

file(REMOVE "${SAVE_FILE}")
