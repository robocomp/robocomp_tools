project(RobocompCLI)
cmake_minimum_required( VERSION 3.10 )
find_package(Python3 COMPONENTS Interpreter REQUIRED)

add_custom_target(RobocompCLI ALL
                    COMMAND pip install ${CMAKE_CURRENT_SOURCE_DIR})
