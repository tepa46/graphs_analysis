cmake_minimum_required(VERSION 3.20.1 FATAL_ERROR)

project(gunrock_pagerank LANGUAGES CXX C CUDA)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(MY_EXEC ssbfs)
set(PROJECT_DEPS_DIR externals)
set(ESSENTIALS_BUILD_EXAMPLES OFF)

include(${PROJECT_SOURCE_DIR}/cmake/FetchEssentials.cmake)


add_library(${PROJECT_NAME} SHARED ${CMAKE_CURRENT_SOURCE_DIR}/${MY_EXEC}.cu)
target_include_directories(${PROJECT_NAME} PUBLIC ${ESSENTIALS_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME} PUBLIC essentials)

set_target_properties(${PROJECT_NAME}
        PROPERTIES
        ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

install(TARGETS ${PROJECT_NAME})

add_executable(${MY_EXEC} ${CMAKE_CURRENT_SOURCE_DIR}/${MY_EXEC}.cu)
target_link_libraries(${MY_EXEC} PRIVATE ${PROJECT_NAME})

set_target_properties(${MY_EXEC}
        PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)