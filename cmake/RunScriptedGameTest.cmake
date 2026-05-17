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
    TIMEOUT 20
)

if(NOT game_result EQUAL 0)
    message(FATAL_ERROR "scripted game run failed: exit=${game_result}; stderr=${game_stderr}")
endif()

set(_search_start 0)
foreach(_expected_var IN ITEMS EXPECT_TEXT_1 EXPECT_TEXT_2 EXPECT_TEXT_3 EXPECT_TEXT_4)
    if(DEFINED ${_expected_var})
        set(_expected_text "${${_expected_var}}")
        string(SUBSTRING "${game_stdout}" ${_search_start} -1 _search_space)
        string(FIND "${_search_space}" "${_expected_text}" _relative_pos)
        if(_relative_pos EQUAL -1)
            message(FATAL_ERROR "expected text not found in sequence: ${_expected_text}")
        endif()
        math(EXPR _search_start "${_search_start} + ${_relative_pos} + 1")
    endif()
endforeach()
