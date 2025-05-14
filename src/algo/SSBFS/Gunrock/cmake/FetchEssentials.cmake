include(FetchContent)
set(FETCHCONTENT_QUIET ON)

message(STATUS "Cloning External Project: Essentials")
get_filename_component(FETCHCONTENT_BASE_DIR "${PROJECT_SOURCE_DIR}/externals" REALPATH)

FetchContent_Declare(
        essentials
        GIT_REPOSITORY https://github.com/gunrock/essentials.git
        GIT_TAG        master
)

FetchContent_MakeAvailable(essentials)
set(ESSENTIALS_INCLUDE_DIR ${FETCHCONTENT_BASE_DIR}/essentials-src/include)